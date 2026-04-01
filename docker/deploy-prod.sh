#!/bin/bash
#
# Production Deployment Script for RealtyAI
# This script deploys RealtyAI to production
#

set -e

echo "=========================================="
echo "🚀 RealtyAI Production Deployment"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Warning: This script should be run as root (sudo)"
    echo "   Run: sudo $0"
    exit 1
fi

# Check if .env exists
if [ ! -f docker/.env ]; then
    echo "❌ Error: docker/.env file not found"
    echo "   Copy docker/.env.example to docker/.env and fill in all required values"
    exit 1
fi

# Backup existing data
echo "📦 Creating backup..."
BACKUP_DIR="docker/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if docker ps | grep -q realtyai-db; then
    echo "   - Backing up database..."
    docker-compose -f docker/docker-compose.prod.yml exec -T db pg_dump -U realtyai realtyai > "$BACKUP_DIR/database.sql" 2>/dev/null || true
fi

if [ -d uploads ]; then
    echo "   - Backing up uploads..."
    cp -r uploads "$BACKUP_DIR/" 2>/dev/null || true
fi

echo "✅ Backup created: $BACKUP_DIR"
echo ""

# Check SSL certificates
echo "🔒 Checking SSL certificates..."
if [ ! -f docker/ssl/fullchain.pem ] || [ ! -f docker/ssl/privkey.pem ]; then
    echo "❌ SSL certificates not found"
    echo "   Run: sudo ./docker/setup-ssl.sh"
    echo "   Or copy your certificates to:"
    echo "   - docker/ssl/fullchain.pem"
    echo "   - docker/ssl/privkey.pem"
    exit 1
fi
echo "✅ SSL certificates found"
echo ""

# Check environment variables
echo "🔍 Checking environment variables..."
critical_vars=("DB_PASSWORD" "JWT_SECRET" "QWEN_API_KEY" "GOOGLE_MAPS_API_KEY" "STRIPE_SECRET_KEY" "STRIPE_WEBHOOK_SECRET" "GOOGLE_OAUTH_CLIENT_ID" "GOOGLE_OAUTH_CLIENT_SECRET" "CORS_ALLOWED_ORIGINS")
missing=false

while IFS= read -r line; do
    var_name=$(echo "$line" | cut -d'=' -f1)
    var_value=$(echo "$line" | cut -d'=' -f2-)
    
    for req in "${critical_vars[@]}"; do
        if [ "$req" == "$var_name" ]; then
            if [ "$var_value" == "change_this*" ] || [ "$var_value" == "your_*" ] || [ -z "$var_value" ]; then
                echo "❌ Error: $var_name not configured"
                missing=true
            fi
        fi
    done
done < docker/.env

if [ "$missing" = true ]; then
    echo ""
    echo "❌ Critical environment variables are not configured"
    echo "   Edit docker/.env and try again"
    exit 1
fi

# Check if MOCK_SERVICES is disabled
if grep -q "MOCK_SERVICES_ENABLED=true" docker/.env; then
    echo "❌ Error: MOCK_SERVICES_ENABLED must be false in production"
    exit 1
fi

echo "✅ All environment variables configured"
echo ""

# Stop existing services
echo "⏸️  Stopping existing services..."
docker-compose -f docker/docker-compose.prod.yml down || true
echo ""

# Build new images
echo "🔨 Building Docker images..."
docker-compose -f docker/docker-compose.prod.yml build --no-cache
echo ""

# Start services
echo "🐳 Starting production services..."
docker-compose -f docker/docker-compose.prod.yml up -d
echo ""

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check health
echo "🏥 Checking service health..."
healthy=true

check_health() {
    local service=$1
    local url=$2
    local name=$3
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo "   ✅ $name is healthy"
    else
        echo "   ❌ $name is not responding"
        healthy=false
    fi
}

check_health backend "http://localhost:8000/health" "Backend API"
check_health frontend "http://localhost/" "Frontend"

echo ""

if [ "$healthy" = false ]; then
    echo "⚠️  Some services are not healthy"
    echo "   Check logs: docker-compose -f docker/docker-compose.prod.yml logs -f"
    exit 1
fi

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker/docker-compose.prod.yml exec -T backend alembic upgrade head || true
echo ""

# Show status
echo "=========================================="
echo "📊 Service Status"
echo "=========================================="
docker-compose -f docker/docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "✅ Production Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Access points:"
echo "   - Frontend: https://yourdomain.com"
echo "   - Backend API: https://yourdomain.com/api"
echo "   - API Docs: https://yourdomain.com/docs"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose -f docker/docker-compose.prod.yml logs -f"
echo "   - Stop: docker-compose -f docker/docker-compose.prod.yml down"
echo "   - Restart: docker-compose -f docker/docker-compose.prod.yml restart"
echo "   - Status: docker-compose -f docker/docker-compose.prod.yml ps"
echo ""
echo "🔍 View real-time logs:"
echo "   docker-compose -f docker/docker-compose.prod.yml logs -f"
echo ""
echo "💾 Backup location: $BACKUP_DIR"
echo ""
