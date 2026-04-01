# Docker Deployment Guide - RealtyAI

## 📋 Overview

This directory contains Docker configuration for deploying RealtyAI in development and production environments.

## 🚀 Quick Start

### Development Environment

1. **Copy and configure environment variables:**
```bash
cp .env.example .env
nano .env  # Edit and fill in your values
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Check logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

### Production Environment

1. **Copy and configure environment variables:**
```bash
cp .env.example .env
nano .env  # Edit and fill in ALL required values
```

2. **Generate secure secrets:**
```bash
# Database password
export DB_PASSWORD=$(openssl rand -base64 32)

# JWT secret
export JWT_SECRET=$(openssl rand -hex 32)

# Add to .env file
```

3. **Get SSL certificates (Let's Encrypt):**
```bash
# Option 1: Manual
certbot certonly --standalone -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/ssl/

# Option 2: Use cloud provider (AWS ACM, Cloudflare, etc.)
# Copy certificates to docker/ssl/
```

4. **Start production services:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

5. **Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

## 📁 File Structure

```
docker/
├── .env.example              # Template for environment variables
├── .env                      # Actual environment variables (DO NOT COMMIT)
├── .dockerignore            # Files to exclude from build
├── .gitignore               # Git ignore for docker directory
├── docker-compose.yml       # Development configuration
├── docker-compose.prod.yml  # Production configuration
├── Dockerfile.backend       # Multi-stage backend build
├── Dockerfile.frontend      # Multi-stage frontend build
├── nginx.conf               # Nginx configuration with HTTPS
└── ssl/                     # SSL certificates directory
    ├── fullchain.pem
    └── privkey.pem
```

## 🔐 Security Features

### Implemented
- ✅ **Multi-stage builds** - Smaller, secure images
- ✅ **Non-root user** - Backend runs as `appuser`
- ✅ **Environment variables** - No hardcoded secrets
- ✅ **HTTPS/SSL** - TLS 1.2/1.3 with modern ciphers
- ✅ **Security headers** - CSP, HSTS, X-Frame-Options, etc.
- ✅ **Resource limits** - CPU and memory constraints
- ✅ **Health checks** - Automatic restart on failure
- ✅ **Internal network** - Database not exposed
- ✅ **Logging** - Structured JSON logs with rotation
- ✅ **Dockerignore** - Prevents sensitive files in images

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_PASSWORD` | ✅ | PostgreSQL password (min 32 chars) |
| `JWT_SECRET` | ✅ | JWT signing secret (min 32 chars) |
| `QWEN_API_KEY` | ✅ | Qwen AI API key |
| `GOOGLE_MAPS_API_KEY` | ✅ | Google Maps API key |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | ✅ | Stripe webhook secret |
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ | Google OAuth client secret |
| `CORS_ALLOWED_ORIGINS` | ✅ | Comma-separated allowed origins |
| `ENVIRONMENT` | ❌ | Environment (development/production) |
| `LOG_LEVEL` | ❌ | Logging level (DEBUG/INFO/WARNING) |

## 🛠️ Commands Reference

### Build
```bash
# Build all images
docker-compose build

# Build with production flags
docker-compose -f docker-compose.prod.yml build --no-cache

# Build only backend
docker-compose build backend
```

### Run
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d --build

# With logs
docker-compose up

# Specific service
docker-compose up backend
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# JSON format
docker-compose logs --no-color backend
```

### Database
```bash
# Access PostgreSQL
docker-compose exec db psql -U realtyai -d realtyai

# Backup database
docker-compose exec db pg_dump -U realtyai realtyai > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U realtyai realtyai

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Backend
```bash
# Access backend shell
docker-compose exec backend bash

# Run Python
docker-compose exec backend python

# Run tests
docker-compose exec backend pytest

# Run migrations
docker-compose exec backend alembic upgrade head

# Check health
curl http://localhost:8000/health
```

### Maintenance
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart

# Update images
docker-compose pull
docker-compose up -d --build

# Clean up
docker-compose down --rmi all --volumes --remove-orphans
```

## 🔍 Troubleshooting

### Database Connection Issues
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify connection
docker-compose exec backend python -c "from database.connection import engine; print('OK')"
```

### Backend Not Starting
```bash
# Check backend logs
docker-compose logs backend

# Check environment variables
docker-compose exec backend env | grep DATABASE

# Check if port is in use
lsof -i :8000
```

### Frontend Not Loading
```bash
# Check nginx logs
docker-compose logs frontend

# Check if backend is reachable
docker-compose exec frontend wget -O- http://backend:8000/health

# Verify nginx config
docker-compose exec frontend nginx -t
```

### SSL/HTTPS Issues
```bash
# Check certificate files
ls -la docker/ssl/

# Verify certificate
openssl x509 -in docker/ssl/fullchain.pem -text -noout

# Check nginx SSL configuration
docker-compose exec frontend nginx -T | grep ssl
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check container health
docker-compose ps

# View slow queries (PostgreSQL)
docker-compose exec db psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 📊 Monitoring

### Health Checks
```bash
# Check all container health
docker inspect --format='{{.State.Health.Status}}' realtyai-backend
docker inspect --format='{{.State.Health.Status}}' realtyai-db
docker inspect --format='{{.State.Health.Status}}' realtyai-frontend
```

### Logs Aggregation
For production, consider:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki** (Grafana logs)
- **CloudWatch** (AWS)
- **Datadog** (SaaS)

### Metrics
- **Prometheus + Grafana** for custom metrics
- **cAdvisor** for container metrics
- **Node Exporter** for host metrics

## 🚀 Production Checklist

- [ ] All environment variables set in `.env`
- [ ] Strong passwords generated (DB, JWT)
- [ ] SSL certificates installed and configured
- [ ] CORS origins updated for production domain
- [ ] `MOCK_SERVICES_ENABLED=false`
- [ ] `ENVIRONMENT=production`
- [ ] `LOG_LEVEL=INFO` or `WARNING`
- [ ] Database backups configured
- [ ] Monitoring and alerts set up
- [ ] Firewall rules configured
- [ ] Domain DNS pointing to server
- [ ] Let's Encrypt auto-renewal configured (if using)
- [ ] Load balancer configured (if scaling)
- [ ] CI/CD pipeline set up

## 🔧 Advanced Configuration

### Custom Resource Limits
Edit `docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 1G
```

### Persistent Volumes
```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/data/postgres
```

### External Network
```yaml
networks:
  realtyai-network:
    external: true
```

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Nginx SSL Guide](https://ssl-config.mozilla.org/)
- [PostgreSQL Tuning](https://www.postgresql.org/docs/current/tuning.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section above
3. Check Docker documentation
4. Open an issue on GitHub

---

**Last Updated:** 2024-01-01  
**Version:** 1.0.0
