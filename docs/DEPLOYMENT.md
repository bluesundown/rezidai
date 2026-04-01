# RealtyAI Deployment Guide

## Production Checklist

Before deploying to production:

- [ ] Change default admin password
- [ ] Set strong JWT secret
- [ ] Obtain real API keys (Qwen, Google Maps)
- [ ] Disable mock services
- [ ] Configure PostgreSQL (not SQLite)
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS for production domain
- [ ] Set up monitoring and logging
- [ ] Configure database backups
- [ ] Set up Stripe for payments
- [ ] Configure OAuth providers
- [ ] Review security settings

## Deployment Options

### Option 1: Docker Compose (VPS)

#### 1. Server Requirements

- Ubuntu 20.04+ or Debian 11+
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ storage
- Docker 20.10+
- Docker Compose 2.0+

#### 2. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 3. Clone and Configure

```bash
git clone https://github.com/yourusername/realtyai.git
cd realtyai

# Configure environment
cp backend/.env.example backend/.env
nano backend/.env
```

#### 4. Update Configuration

Edit `backend/config.yaml`:

```yaml
mock_services:
  enabled: false  # IMPORTANT: Disable in production

cors:
  allowed_origins:
    - "https://yourdomain.com"
```

#### 5. Update Docker Compose

Edit `docker/docker-compose.yml` for production:

```yaml
services:
  backend:
    command: >
      sh -c "python database/seed.py &&
             gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000"
    environment:
      - ENVIRONMENT=production
    # Remove --reload flag
```

#### 6. Set Up Nginx as Reverse Proxy

Create `/etc/nginx/sites-available/realtyai`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static uploads
    location /uploads/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/realtyai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Configure SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### 8. Start Services

```bash
docker-compose up -d

# Enable auto-start
sudo systemctl enable docker
```

#### 9. Set Up Monitoring

Install PM2 for process monitoring:

```bash
npm install -g pm2
pm2 start docker-compose.yml --name realtyai
pm2 startup
pm2 save
```

### Option 2: Cloud Platforms

#### AWS EC2

1. Launch Ubuntu instance (t3.medium or higher)
2. Follow Docker Compose setup above
3. Use AWS RDS for PostgreSQL
4. Use S3 for image storage
5. Use Elastic Load Balancer for SSL termination

#### Google Cloud Platform

1. Create Compute Engine instance
2. Follow Docker Compose setup
3. Use Cloud SQL for PostgreSQL
4. Use Cloud Storage for images
5. Use Cloud Load Balancing

#### Heroku

```bash
# Create files
echo "web: gunicorn backend.main:app" > Procfile
echo "*.pyc\n__pycache__\n.env" > .gitignore

# Deploy
heroku create your-app-name
heroku config:set JWT_SECRET=your-secret
heroku config:set DATABASE_URL=postgres://...
git push heroku main
```

#### Railway.sh

1. Connect GitHub repository
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically on push

### Option 3: Kubernetes

Create `kubernetes/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: realtyai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: realtyai-backend
  template:
    metadata:
      labels:
        app: realtyai-backend
    spec:
      containers:
      - name: backend
        image: your-dockerhub/realtyai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: realtyai-backend
spec:
  selector:
    app: realtyai-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Environment Variables (Production)

```env
# Critical Security Settings
JWT_SECRET=<random-64-characters>
DATABASE_PASSWORD=<strong-random-password>

# Database
DATABASE_HOST=your-db-host
DATABASE_PORT=5432
DATABASE_NAME=realtyai_prod
DATABASE_USER=realtyai

# API Keys
QWEN_API_KEY=your-production-key
GOOGLE_MAPS_API_KEY=your-production-key
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-secret
GOOGLE_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/google/callback

# Application
ENVIRONMENT=production
CONFIG_PATH=/app/config.yaml
```

## Database Setup

### PostgreSQL Production

```bash
# Create database
createdb realtyai_prod

# Create user
createuser -P realtyai

# Set permissions
psql -c "GRANT ALL PRIVILEGES ON DATABASE realtyai_prod TO realtyai;"

# Run migrations
alembic upgrade head

# Seed data
python database/seed.py
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose exec db pg_dump -U realtyai realtyai > /backups/realtyai_$DATE.sql

# Keep last 30 days
find /backups -name "realtyai_*.sql" -mtime +30 -delete
```

Schedule with cron:

```bash
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

## Monitoring & Logging

### Application Logs

```bash
# View logs
docker-compose logs -f backend

# Tail specific logs
docker-compose logs -f --tail=100 backend
```

### Performance Monitoring

Install Prometheus and Grafana:

```yaml
# Add to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
```

### Error Tracking

Integrate with Sentry:

```python
# Add to main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)
```

## Security Hardening

### 1. HTTPS Only

Enable HSTS:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 2. Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend:8000;
}
```

### 3. Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Database Security

- Use strong passwords
- Enable SSL for database connections
- Restrict database access to application server only
- Regular security updates

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Load Balancing

Use Nginx or HAProxy to distribute traffic across multiple backend instances.

### Caching

Add Redis for session and query caching:

```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## Performance Optimization

### 1. Static Files

Use CDN for static assets:
- Cloudflare
- AWS CloudFront
- Google Cloud CDN

### 2. Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_images_listing_id ON images(listing_id);
```

### 3. Image Optimization

- Use WebP format
- Implement lazy loading
- Generate multiple sizes
- Use CDN for delivery

## Rollback Strategy

```bash
# Save current state
docker-compose config > current-compose.yml
docker save realtyai-backend:latest > backend-backup.tar

# Rollback if needed
docker load < backend-backup.tar
docker-compose up -d
```

## Support & Maintenance

### Regular Tasks

- Weekly: Review logs for errors
- Monthly: Update dependencies
- Quarterly: Security audit
- Yearly: Performance review

### Update Process

```bash
# Backup first
docker-compose exec db pg_dump -U realtyai realtyai > backup.sql

# Pull updates
git pull

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify
curl https://yourdomain.com/health
```

## Contact

For deployment assistance, contact: support@realtyai.com
