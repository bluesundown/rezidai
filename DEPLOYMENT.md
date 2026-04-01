# 🚀 Deployment Guide - RealtyAI

## 📋 Platform Comparison

| Platform | Backend | Frontend | Database | Cost | Recommendation |
|----------|---------|----------|----------|------|----------------|
| **Render** | ✅ Perfect | ✅ Good | ✅ Free | Free tier | 🏆 **Best Choice** |
| **Vercel** | ⚠️ Serverless | ✅ Best | ❌ External | Free tier | ⚠️ Frontend only |
| **Railway** | ✅ Good | ✅ Good | ✅ Free | $5 credits/mo | 🥈 Alternative |
| **Fly.io** | ✅ Good | ✅ Good | ✅ Good | Free tier | 🥈 Alternative |

---

## 🏆 Option 1: Render (RECOMMENDED)

### **Why Render?**
- ✅ **Free PostgreSQL database** (90 days free, then $7/mo)
- ✅ **Free web services** (750 hours/month)
- ✅ **Automatic HTTPS**
- ✅ **Zero configuration** - auto-detects FastAPI
- ✅ **Simple deployment** - just push to GitHub

### **Step-by-Step Deployment**

#### **1. Prepare Your Code**

```bash
# Install Git if you don't have it
sudo apt install git  # Ubuntu/Debian
brew install git      # macOS

# Initialize git repository
cd /home/samuel/Projekty/rezidai
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository
# Go to github.com -> New Repository -> Create
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/realtyai.git
git push -u origin main
```

#### **2. Create Render Account**

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your GitHub

#### **3. Deploy Backend + Database**

1. Click **"New"** → **"Import from GitHub"**
2. Select your repository
3. Render will auto-detect `render.yaml`
4. Configure:
   - **Name**: `realtyai-backend`
   - **Region**: Choose closest to your users
   - **Instance Type**: Free
   - **Branch**: main

5. **Add Environment Variables** (in Render dashboard):
   ```
   QWEN_API_KEY=your_qwen_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   STRIPE_SECRET_KEY=sk_test_your_stripe_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
   CORS_ALLOWED_ORIGINS=https://your-frontend-url.onrender.com
   ```

6. Click **"Create Advanced Web + Database Service"**

7. Wait for deployment (~3-5 minutes)

8. **Copy your backend URL** (e.g., `https://realtyai-backend.onrender.com`)

#### **4. Deploy Frontend**

**Option A: Render Static Site**

1. Click **"New"** → **"Static Site"**
2. Select your repository
3. Configure:
   - **Name**: `realtyai-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty - no build needed)
   - **Publish Directory**: `frontend`

4. Add Environment Variable:
   ```
   VITE_API_URL=https://realtyai-backend.onrender.com/api
   ```

5. Click **"Create Static Site"**

**Option B: Netlify (Alternative)**

1. Go to [netlify.com](https://netlify.com)
2. "Add new site" → "Import an existing project"
3. Select GitHub → your repository
4. Configure:
   - **Base directory**: `frontend`
   - **Build command**: (leave empty)
   - **Publish directory**: `frontend`
5. Add redirect rules in `netlify.toml`:
   ```toml
   [[redirects]]
   from = "/api/*"
   to = "https://realtyai-backend.onrender.com/api/:splat"
   status = 200
   ```

#### **5. Update CORS**

1. Go back to Render → Backend service
2. Settings → Environment
3. Update `CORS_ALLOWED_ORIGINS` with your frontend URL:
   ```
   https://your-frontend-name.onrender.com,https://your-site.netlify.app
   ```

#### **6. Run Database Migrations**

1. Go to Render → Backend service
2. Click **"Shell"** tab
3. Run:
   ```bash
   alembic upgrade head
   python -m database.seed
   ```

4. Copy the admin password from the output!

#### **7. Configure Google OAuth**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth Client ID
3. **Authorized redirect URIs**:
   ```
   https://your-backend.onrender.com/api/oauth/google/callback
   ```
4. Update Render environment variables with new Client ID/Secret

---

## 🌐 Option 2: Vercel (Frontend Only)

### **Why Vercel?**
- ✅ **Best frontend performance**
- ✅ **Automatic deployments**
- ✅ **Instant previews**
- ❌ **Backend needs separate hosting**

### **Steps**

1. Go to [vercel.com](https://vercel.com)
2. "Add New Project"
3. Import from GitHub
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: `frontend`

5. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com/api
   ```

6. Deploy!

---

## 🚂 Option 3: Railway

### **Steps**

1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect:
   - Backend (FastAPI)
   - Database (PostgreSQL)

5. Add variables in Railway dashboard

6. Deploy!

---

## 🔧 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `QWEN_API_KEY` | ✅ | Qwen AI API key | `sk-...` |
| `GOOGLE_MAPS_API_KEY` | ✅ | Google Maps API | `AIza...` |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | ✅ | Stripe webhook | `whsec_...` |
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ | Google OAuth ID | `123...apps.googleusercontent.com` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ | Google OAuth secret | `GOCSPX-...` |
| `JWT_SECRET` | ✅ | JWT signing secret | Auto-generated |
| `CORS_ALLOWED_ORIGINS` | ✅ | Frontend URL | `https://frontend.onrender.com` |
| `DATABASE_URL` | ✅ | PostgreSQL URL | Auto-configured |

---

## 📊 Costs

### **Render Free Tier**
- Backend: **Free** (750 hours/month)
- Frontend: **Free** (unlimited)
- Database: **Free** for 90 days, then **$7/mo**
- **Total: $0-7/month**

### **Vercel Free Tier**
- Frontend: **Free** (unlimited)
- Backend: Not applicable
- **Total: $0/month** (backend elsewhere)

### **Railway Free Tier**
- **$5 credits/month** (enough for small app)
- **Total: ~$5/month**

---

## ✅ Post-Deployment Checklist

- [ ] Backend is running: `https://backend.onrender.com/health`
- [ ] Frontend is running: `https://frontend.onrender.com`
- [ ] API docs accessible: `https://backend.onrender.com/docs`
- [ ] Database migrations completed
- [ ] Admin user created (saved password)
- [ ] Google OAuth configured
- [ ] CORS properly set up
- [ ] Environment variables all set
- [ ] Test user registration
- [ ] Test listing creation
- [ ] Test AI description generation

---

## 🐛 Troubleshooting

### **Backend won't start**
```bash
# Check logs in Render dashboard
# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port not set to $PORT
```

### **CORS errors**
```bash
# Update CORS_ALLOWED_ORIGINS in Render
# Include both http://localhost:3000 and your production URL
```

### **Database connection failed**
```bash
# Check DATABASE_URL is set
# Run migrations: alembic upgrade head
# Check database service is running
```

### **OAuth not working**
```bash
# Update Google Console with production redirect URI
# https://your-backend.onrender.com/api/oauth/google/callback
```

---

## 🎯 Quick Commands

```bash
# Local development
cd backend
uvicorn main:app --reload

# Check database
docker-compose exec db psql -U realtyai -d realtyai

# Run migrations
alembic upgrade head

# View logs (Render)
# Use Render dashboard → Logs tab
```

---

## 📞 Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **FastAPI Deployment**: [fastapi.tiangolo.com/deployment](https://fastapi.tiangolo.com/deployment)
- **GitHub Issues**: Create issue if you need help

---

**Ready to deploy?** Start with **Option 1: Render** - it's the easiest! 🚀
