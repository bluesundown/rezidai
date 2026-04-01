# Render Deployment Configuration
# This file is used by Render for automatic deployment

# Backend: FastAPI application
# Frontend: Static files served via Netlify/Vercel
# Database: PostgreSQL on Render

## Quick Start
# 1. Push to GitHub
# 2. Go to render.com
# 3. Click "New" -> "Import from GitHub"
# 4. Select your repository
# 5. Render will auto-detect this file and deploy

## Environment Variables (set in Render dashboard)
# - QWEN_API_KEY: Your Qwen AI API key
# - GOOGLE_MAPS_API_KEY: Your Google Maps API key
# - STRIPE_SECRET_KEY: Your Stripe secret key
# - STRIPE_WEBHOOK_SECRET: Your Stripe webhook secret
# - GOOGLE_OAUTH_CLIENT_ID: Your Google OAuth client ID
# - GOOGLE_OAUTH_CLIENT_SECRET: Your Google OAuth client secret
# - CORS_ALLOWED_ORIGINS: Your frontend URL

## Free Tier Limits
# - Web Services: 750 hours/month
# - Database: 1 GB storage, 90 days free
# - Bandwidth: 100 GB/month
