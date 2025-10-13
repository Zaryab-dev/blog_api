# 🚀 Django Backend API Deployment Guide

## 🏗️ Overview

This document covers deploying a **Django REST API backend** to **Render**. The backend serves data to a **Next.js frontend** deployed on Vercel.

**Architecture:**
- **Render** hosts the Django API and static files
- **PostgreSQL** managed database on Render
- **HTTPS** public API accessible by frontend
- **Gunicorn** as WSGI server

---

## ⚙️ Prerequisites

### Required Tools & Accounts
- Git + GitHub repository
- [Render account](https://render.com) (free tier available)
- Python 3.10+
- PostgreSQL (Render provides managed instance)

### Render Free Tier Includes
- Free PostgreSQL database
- Free Web Service hosting
- **No credit card required** for free tier
- Automatic SSL certificates

### Alternative Platforms
- **Railway.app** - Easy UI, auto-deploy
- **Fly.io** - Geo-distributed with Docker
- **Deta Space** - Simple API hosting

---

## 🧰 Project Preparation

### 1. Project Structure
```
leather_api/
├── manage.py
├── requirements.txt
├── leather_api/
│   ├── settings.py
│   ├── wsgi.py
│   └── asgi.py
└── blog/
```

### 2. Install Required Packages
Add to `requirements.txt`:
```
gunicorn
psycopg2-binary
dj-database-url
whitenoise
python-dotenv
django-cors-headers
```

Install locally:
```bash
pip install -r requirements.txt
```

### 3. Update `settings.py`

```python
import os
import dj_database_url
from pathlib import Path

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-dev-secret-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000'
).split(',')

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    'corsheaders.middleware.CorsMiddleware',
    # ... rest of middleware
]

# Apps
INSTALLED_APPS = [
    # ...
    'corsheaders',
    'rest_framework',
    # ...
]
```

### 4. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 🚀 Deployment on Render

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Web Service on Render
1. Go to [https://render.com](https://render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Select **Python 3** runtime

### Step 3: Configure Build Settings
**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn leather_api.wsgi
```

### Step 4: Add Environment Variables
In Render dashboard → **Environment** tab:

```
DJANGO_SECRET_KEY=your-strong-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.onrender.com,.vercel.app,yourdomain.com
DATABASE_URL=postgresql://user:pass@host/db
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
```

### Step 5: Create PostgreSQL Database
1. In Render dashboard → **New** → **PostgreSQL**
2. Create database (free tier available)
3. Copy **Internal Database URL**
4. Add as `DATABASE_URL` in environment variables

### Step 6: Run Migrations
In Render **Shell** tab:
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional
```

### Step 7: Verify Deployment
Visit your API URL:
```
https://your-backend.onrender.com/api/
```

---

## 🌍 CORS & Frontend Connection

### Configure CORS in `settings.py`
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",
    "https://yourdomain.com",
    "http://localhost:3000",  # For local development
]

CORS_ALLOW_CREDENTIALS = True
```

### Update Frontend API URL
In your Next.js `.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 📦 Static and Media Files

### Static Files (Whitenoise)
Already configured in settings:
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Media Files (User Uploads)
For production, use cloud storage:

**Option 1: Supabase Storage**
```python
# settings.py
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
```

**Option 2: AWS S3**
```python
# Install: pip install django-storages boto3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'your-bucket'
```

**Option 3: Cloudinary**
```python
# Install: pip install cloudinary
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
```

---

## 🔒 Security Configuration

### Production Settings
```python
# settings.py
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ['.onrender.com', 'yourdomain.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Generate Strong Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 🌐 Custom Domain Setup

### Add Custom Domain
1. In Render dashboard → **Settings** → **Custom Domain**
2. Add your domain: `api.yourdomain.com`
3. Update DNS records:
   - **Type:** CNAME
   - **Name:** api
   - **Value:** your-app.onrender.com

### Update Settings
```python
ALLOWED_HOSTS = ['api.yourdomain.com', '.onrender.com']
```

Render provides **free SSL certificates** automatically.

---

## ⚙️ Maintenance & Logs

### View Logs
- Go to Render dashboard → **Logs** tab
- Real-time log streaming available

### Restart Service
- Dashboard → **Manual Deploy** → **Deploy latest commit**
- Or: **Settings** → **Restart Service**

### Connect to PostgreSQL
Use the **External Database URL** from Render:
```bash
psql postgresql://user:pass@host/db
```

### Scale Up
Free tier limitations:
- Service sleeps after 15 minutes of inactivity
- 750 hours/month free compute
- Upgrade to **Starter ($7/month)** for:
  - No sleep
  - More resources
  - Better performance

---

## 🧩 Alternative Deployments

### Railway.app
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Pros:** Easy UI, auto-deploy, generous free tier  
**Cons:** Requires credit card for free tier

### Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

**Pros:** Geo-distributed, Docker-based  
**Cons:** More complex setup

### Deta Space
```bash
# Install Deta CLI
curl -fsSL https://get.deta.dev/cli.sh | sh

# Deploy
deta login
deta new
```

**Pros:** Simple, free tier  
**Cons:** Limited features

---

## 📈 Final Notes

### Free Tier Limits
- **Render Web Service:** Sleeps after 15 min inactivity, 750 hrs/month
- **PostgreSQL:** 1GB storage, 97 connection limit
- **Recommendation:** Upgrade for production apps with consistent traffic

### Best Practices
- Use environment variables for all secrets
- Enable automatic deploys from GitHub
- Set up health checks: `/api/health/`
- Monitor logs regularly
- Use Redis for caching (Render offers free Redis)

### Render + Vercel Stack
Perfect combination for full-stack projects:
- **Frontend:** Next.js on Vercel
- **Backend:** Django on Render
- **Database:** PostgreSQL on Render
- **Storage:** Supabase/S3/Cloudinary

### Support
- [Render Docs](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Render Community](https://community.render.com)

---

## 🎯 Quick Deploy Checklist

- [ ] Push code to GitHub
- [ ] Create Render Web Service
- [ ] Add environment variables
- [ ] Create PostgreSQL database
- [ ] Run migrations
- [ ] Test API endpoints
- [ ] Configure CORS
- [ ] Update frontend API URL
- [ ] Set up custom domain (optional)
- [ ] Enable automatic deploys

**Your Django API is now live! 🎉**
