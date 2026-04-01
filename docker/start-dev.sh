#!/bin/bash
#
# Quick Start Script for RealtyAI Development
# This script sets up and starts the development environment
#

set -e

echo "=========================================="
echo "🚀 RealtyAI Development Quick Start"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# Check if .env exists
if [ ! -f docker/.env ]; then
    echo "📝 Creating .env file from template..."
    cp docker/.env.example docker/.env
    echo "✅ Created docker/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit docker/.env and fill in your values!"
    echo "   Required variables:"
    echo "   - DB_PASSWORD (generate: openssl rand -base64 32)"
    echo "   - JWT_SECRET (generate: openssl rand -hex 32)"
    echo "   - QWEN_API_KEY"
    echo "   - GOOGLE_MAPS_API_KEY"
    echo "   - STRIPE_SECRET_KEY"
    echo "   - STRIPE_WEBHOOK_SECRET"
    echo "   - GOOGLE_OAUTH_CLIENT_ID"
    echo "   - GOOGLE_OAUTH_CLIENT_SECRET"
    echo ""
    read -p "Press Enter after you've edited .env..."
fi

# Check if required variables are set
echo "🔍 Checking environment variables..."
required_vars=("DB_PASSWORD" "JWT_SECRET" "QWEN_API_KEY" "GOOGLE_MAPS_API_KEY")
missing=false

while IFS= read -r line; do
    var_name=$(echo "$line" | cut -d'=' -f1)
    var_value=$(echo "$line" | cut -d'=' -f2-)
    
    for req in "${required_vars[@]}"; do
        if [ "$req" == "$var_name" ]; then
            if [ "$var_value" == "change_this*" ] || [ -z "$var_value" ]; then
                echo "⚠️  Warning: $var_name not configured"
                missing=true
            fi
        fi
    done
done < docker/.env

if [ "$missing" = true ]; then
    echo ""
    echo "❌ Some required variables are not configured"
    echo "   Edit docker/.env and try again"
    exit 1
fi

echo "✅ Environment variables configured"
echo ""

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build --no-cache

echo ""
echo "🐳 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Development Environment Ready!"
echo "=========================================="
echo ""
echo "🌐 Access points:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Database: localhost:5432"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop: docker-compose down"
echo "   - Restart: docker-compose restart"
echo "   - Database: docker-compose exec db psql -U realtyai -d realtyai"
echo ""
echo "🔍 View real-time logs:"
echo "   docker-compose logs -f"
echo ""
