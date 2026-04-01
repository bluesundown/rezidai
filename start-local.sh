#!/bin/bash
#
# Quick Local Start - RealtyAI
# This script starts the app locally without Docker
#

set -e

echo "=========================================="
echo "🚀 RealtyAI - Local Quick Start"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create venv if not exists
if [ ! -d "backend/venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
cd ..

# Create .env if not exists
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp backend/.env.example backend/.env
    
    echo ""
    echo "⚠️  Setting MOCK_SERVICES_ENABLED=true for local testing..."
    sed -i 's/MOCK_SERVICES_ENABLED=false/MOCK_SERVICES_ENABLED=true/' backend/.env
    
    echo "✅ Created backend/.env with mock mode enabled"
fi

# Set mock mode for local testing
if grep -q "MOCK_SERVICES_ENABLED=false" backend/.env 2>/dev/null; then
    echo ""
    echo "⚙️  Enabling mock services for local testing..."
    sed -i 's/MOCK_SERVICES_ENABLED=false/MOCK_SERVICES_ENABLED=true/' backend/.env
fi

# Set default values if not set
if grep -q "DB_PASSWORD=change_this" backend/.env 2>/dev/null; then
    sed -i 's/DB_PASSWORD=change_this.*/DB_PASSWORD=localdevpassword123/' backend/.env
fi

if grep -q "JWT_SECRET=change_this" backend/.env 2>/dev/null; then
    SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/JWT_SECRET=change_this.*/JWT_SECRET=$SECRET/" backend/.env
fi

echo ""
echo "📊 Database migrations..."
cd backend

# Run migrations with proper error handling
if alembic upgrade head; then
    echo "✅ Migrations completed successfully"
else
    echo "⚠️  Migrations failed or database doesn't exist"
    echo "Creating database tables manually..."
    
    # Create database using SQLAlchemy
    python -c "
from database.connection import Base, engine

try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'❌ Failed to create tables: {e}')
    import sys
    sys.exit(1)
"
    
    if [ $? -ne 0 ]; then
        echo "❌ Database setup failed!"
        exit 1
    fi
fi

echo ""
echo "🌱 Seeding database..."
if python -m database.seed; then
    echo "✅ Database seeded successfully"
else
    echo "❌ Seeding failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "🚀 Starting backend server..."
echo ""

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
