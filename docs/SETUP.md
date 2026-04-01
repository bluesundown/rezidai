# RealtyAI Setup Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/realtyai.git
cd realtyai
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database (Docker)
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=realtyai
DATABASE_USER=realtyai
DATABASE_PASSWORD=password

# JWT Configuration
JWT_SECRET=change_this_to_a_random_secret_key
JWT_EXPIRATION_HOURS=24

# API Keys (Optional - Mock mode enabled by default)
QWEN_API_KEY=your_qwen_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

### 3. Configure Application

Edit `backend/config.yaml` if needed:

```yaml
# Enable/disable mock services
mock_services:
  enabled: true  # Set to false when using real API keys
  ai_responses: true
  maps_responses: true
  stripe_enabled: false
  oauth_validation: true
```

### 4. Start Services

From the project root:

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Start FastAPI backend (port 8000)
- Start Nginx frontend (port 3000)
- Run database migrations
- Seed initial data

### 5. Verify Installation

Check service health:

```bash
docker-compose ps
```

View logs:

```bash
docker-compose logs -f
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 6. Create First Account

Visit http://localhost:3000 and click "Get Started" to create your account.

Or use the default admin account:
- Email: `admin@realtyai.com`
- Password: `admin123`

**Important**: Change the admin password immediately!

## Local Development (Without Docker)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run database migrations (if using PostgreSQL)
# First start PostgreSQL separately or use Docker

# Seed database
python database/seed.py

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Simple HTTP server
python -m http.server 3000

# Or use any HTTP server of your choice
# The frontend is static files, no build process required
```

### Database Setup (Local PostgreSQL)

```bash
# Create database
createdb realtyai

# Create tables
alembic upgrade head

# Seed data
python database/seed.py
```

## Running Tests

```bash
# With Docker
docker-compose exec backend pytest

# Local
cd backend
pytest
```

Run specific test files:

```bash
pytest tests/test_auth.py -v
pytest tests/test_listings.py -v
```

## Getting API Keys

### Qwen AI (Optional)
1. Visit [Qwen API](https://qwen.ai)
2. Sign up and get API key
3. Add to `.env`: `QWEN_API_KEY=your_key`

### Google Maps API (Optional)
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Maps API
3. Get API key
4. Add to `.env`: `GOOGLE_MAPS_API_KEY=your_key`

### Stripe (Optional - For Production)
1. Visit [Stripe Dashboard](https://dashboard.stripe.com/)
2. Get test API keys
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

## Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps db

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Port Already in Use

```bash
# Change ports in docker-compose.yml
# Backend: 8000 -> 8001
# Frontend: 3000 -> 3001
```

### Image Upload Fails

```bash
# Check uploads directory permissions
chmod -R 755 uploads/
```

### API Keys Not Working

1. Ensure `mock_services.enabled: false` in `config.yaml`
2. Restart backend container
3. Check backend logs for API errors

## Updating Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Stopping Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

## Backup

```bash
# Backup database
docker-compose exec db pg_dump -U realtyai realtyai > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U realtyai realtyai
```

## Next Steps

1. Create your first listing
2. Configure API keys for production
3. Set up OAuth providers
4. Configure Stripe for payments
5. Deploy to production server

For production deployment guide, see [DEPLOYMENT.md](DEPLOYMENT.md)
