#!/bin/bash
#
# Docker Development Start - RealtyAI
# This script starts the app using Docker for local development
#

set -e

echo "=========================================="
echo "🐳 RealtyAI - Docker Development Start"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop or Docker Engine"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Check .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Set development defaults
    sed -i 's/MOCK_SERVICES_ENABLED=false/MOCK_SERVICES_ENABLED=true/' .env
    sed -i 's/ENVIRONMENT=development/ENVIRONMENT=development/' .env
    sed -i 's/LOG_LEVEL=INFO/LOG_LEVEL=DEBUG/' .env
    
    # Generate JWT secret if not set
    if grep -q "JWT_SECRET=change_this" .env; then
        SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s/JWT_SECRET=change_this.*/JWT_SECRET=$SECRET/" .env
    fi
    
    echo "✅ Created .env with development settings"
fi

echo ""
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.dev.yml build --no-cache

echo ""
echo "🐳 Starting services..."
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📊 Checking service status..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "=========================================="
echo "✅ Development Environment Ready!"
echo "=========================================="
echo ""
echo "🌐 Access points:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "   - Stop: docker-compose -f docker-compose.dev.yml down"
echo "   - Restart: docker-compose -f docker-compose.dev.yml restart"
echo "   - Rebuild: docker-compose -f docker-compose.dev.yml up -d --build"
echo ""
echo "🔍 View real-time logs:"
echo "   docker-compose -f docker-compose.dev.yml logs -f"
echo ""
