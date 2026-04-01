#!/bin/bash
#
# SSL Certificate Setup Script for RealtyAI
# This script helps you set up SSL certificates using Let's Encrypt
#

set -e

echo "=========================================="
echo "SSL Certificate Setup for RealtyAI"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Warning: This script should be run as root (sudo)"
    echo "   Run: sudo $0"
    exit 1
fi

# Create SSL directory
SSL_DIR="/home/samuel/Projekty/rezidai/docker/ssl"
mkdir -p $SSL_DIR

echo "📁 SSL directory: $SSL_DIR"
echo ""

# Get domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN

# Validate domain
if [[ ! $DOMAIN =~ ^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$ ]]; then
    echo "❌ Invalid domain name"
    exit 1
fi

echo ""
echo "🔧 Setting up SSL certificates for: $DOMAIN"
echo ""

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "⬇️  Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-standalone
fi

# Stop nginx temporarily if running
if docker ps | grep -q realtyai-frontend; then
    echo "⏸️  Stopping Docker containers temporarily..."
    docker-compose -f docker/docker-compose.prod.yml stop frontend
fi

# Get certificates
echo "📜 Requesting SSL certificate from Let's Encrypt..."
certbot certonly --standalone --non-interactive --agree-tos --register-unsafely-without-email \
    -d $DOMAIN \
    --force-renewal \
    --preferred-challenges http \
    --http-01-port 80 || {
        echo "❌ Failed to obtain certificate"
        echo "   Please make sure:"
        echo "   - Domain points to this server"
        echo "   - Port 80 is accessible"
        echo "   - No other service is using port 80"
        exit 1
    }

echo ""
echo "✅ Certificate obtained successfully!"
echo ""

# Copy certificates to Docker SSL directory
CERT_SOURCE="/etc/letsencrypt/live/$DOMAIN"
cp $CERT_SOURCE/fullchain.pem $SSL_DIR/
cp $CERT_SOURCE/privkey.pem $SSL_DIR/

# Set proper permissions
chmod 600 $SSL_DIR/privkey.pem
chmod 644 $SSL_DIR/fullchain.pem
chown -R root:root $SSL_DIR

echo "📁 Certificates copied to: $SSL_DIR"
ls -la $SSL_DIR

# Restart Docker containers
echo ""
echo "🔄 Restarting Docker containers..."
docker-compose -f docker/docker-compose.prod.yml up -d frontend

echo ""
echo "=========================================="
echo "✅ SSL Setup Complete!"
echo "=========================================="
echo ""
echo "Your SSL certificates are now configured."
echo ""
echo "📝 Important Notes:"
echo "1. Certificates will expire in 90 days"
echo "2. Set up auto-renewal with cron:"
echo "   0 12 * * * certbot renew --quiet"
echo ""
echo "3. To manually renew:"
echo "   sudo certbot renew"
echo "   sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/"
echo "   sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/"
echo "   sudo docker-compose -f docker/docker-compose.prod.yml restart frontend"
echo ""
echo "4. Test your SSL configuration:"
echo "   https://$DOMAIN"
echo "   https://ssl-compass.com (enter $DOMAIN)"
echo ""
