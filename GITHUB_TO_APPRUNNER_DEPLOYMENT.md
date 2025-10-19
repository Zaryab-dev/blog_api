# 🚀 GitHub to AWS App Runner Deployment Guide

## ✅ Prerequisites Complete

Your project is now **fully configured** for GitHub to AWS App Runner deployment with all dependencies included.

---

## 📦 What's Included

### Updated Dependencies
- ✅ **Google APIs** - For SEO Indexing API
- ✅ **All core dependencies** - Django, DRF, etc.
- ✅ **Security packages** - Rate limiting, CSRF protection
- ✅ **SEO packages** - All ranking features
- ✅ **Production ready** - Gunicorn, WhiteNoise

### Configuration Files
- ✅ `requirements.txt` - All Python dependencies
- ✅ `apprunner.yaml` - App Runner configuration
- ✅ `Dockerfile` - Container configuration
- ✅ `docker-entrypoint.sh` - Startup script
- ✅ `gunicorn.conf.py` - Server configuration

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub (Already Done ✅)

Your code is already on GitHub:
```
https://github.com/Zaryab-dev/blog_api.git
```

### Step 2: Create App Runner Service from GitHub

#### Option A: AWS Console (Recommended)

1. **Go to AWS App Runner Console**
   ```
   https://console.aws.amazon.com/apprunner/
   ```

2. **Click "Create service"**

3. **Configure Source**
   - **Repository type:** Source code repository
   - **Connect to GitHub:** Click "Add new"
   - **Authorize AWS Connector for GitHub**
   - **Select repository:** `Zaryab-dev/blog_api`
   - **Branch:** `main`
   - **Deployment trigger:** Automatic

4. **Configure Build**
   - **Configuration file:** Use configuration file
   - **Configuration file:** `apprunner.yaml`
   
   OR manually configure:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `/bin/bash docker-entrypoint.sh`
   - **Port:** `8080`

5. **Configure Service**
   - **Service name:** `blog-api`
   - **CPU:** 1 vCPU
   - **Memory:** 2 GB
   - **Port:** `8080`

6. **Add Environment Variables**
   Click "Add environment variable" for each:
   
   ```bash
   # Required
   SECRET_KEY=<generate-new-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=*,.awsapprunner.com,.amazonaws.com
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_API_KEY=your-anon-key
   SUPABASE_BUCKET=your-bucket-name
   
   # Site Configuration
   SITE_URL=https://your-app.awsapprunner.com
   SITE_NAME=Your Blog Name
   CORS_ALLOWED_ORIGINS=https://your-frontend.com
   
   # Optional: SEO APIs
   INDEXNOW_KEY=your-indexnow-key
   GOOGLE_SERVICE_ACCOUNT_FILE=/app/service-account.json
   
   # Optional: Redis
   REDIS_URL=redis://your-elasticache:6379/1
   ```

7. **Configure Health Check**
   - **Protocol:** HTTP
   - **Path:** `/api/v1/healthcheck/`
   - **Interval:** 10 seconds
   - **Timeout:** 5 seconds
   - **Healthy threshold:** 1
   - **Unhealthy threshold:** 3

8. **Review and Create**
   - Review all settings
   - Click "Create & deploy"
   - Wait 5-10 minutes for deployment

#### Option B: AWS CLI

```bash
# Install AWS CLI if not installed
pip install awscli

# Configure AWS credentials
aws configure

# Create App Runner service
aws apprunner create-service \
  --service-name blog-api \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/Zaryab-dev/blog_api",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "/bin/bash docker-entrypoint.sh",
          "Port": "8080",
          "RuntimeEnvironmentVariables": {
            "SECRET_KEY": "your-secret-key",
            "DEBUG": "False",
            "ALLOWED_HOSTS": "*,.awsapprunner.com",
            "DATABASE_URL": "postgresql://...",
            "SUPABASE_URL": "https://...",
            "SUPABASE_API_KEY": "...",
            "SUPABASE_BUCKET": "...",
            "SITE_URL": "https://..."
          }
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --health-check-configuration '{
    "Protocol": "HTTP",
    "Path": "/api/v1/healthcheck/",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 3
  }'
```

---

## 🔐 Environment Variables Reference

### Required Variables

```bash
# Django Core
SECRET_KEY=<generate-with-django>
DEBUG=False
ALLOWED_HOSTS=*,.awsapprunner.com,.amazonaws.com
ENVIRONMENT=production

# Database (Use RDS or Supabase PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Supabase Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-anon-or-service-key
SUPABASE_BUCKET=your-bucket-name

# Site Configuration
SITE_URL=https://your-app.awsapprunner.com
SITE_NAME=Your Blog Name
```

### Optional Variables

```bash
# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.com,https://www.yourdomain.com

# Redis (for caching)
REDIS_URL=redis://your-elasticache:6379/1
CELERY_BROKER_URL=redis://your-elasticache:6379/0
CELERY_RESULT_BACKEND=redis://your-elasticache:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SEO APIs
INDEXNOW_KEY=your-64-char-hex-key
GOOGLE_SERVICE_ACCOUNT_FILE=/app/service-account.json

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
DJANGO_LOG_LEVEL=INFO

# Security
CSRF_TRUSTED_ORIGINS=https://your-app.awsapprunner.com
SECURE_PROXY_SSL_HEADER_ENABLED=True
```

---

## 🧪 Testing Deployment

### 1. Check Service Status

```bash
# Get service URL
aws apprunner list-services --region us-east-1

# Or in AWS Console
# App Runner → Services → Your service
```

### 2. Test Health Check

```bash
# Replace with your App Runner URL
APP_URL="https://your-app.awsapprunner.com"

# Test health check
curl $APP_URL/api/v1/healthcheck/

# Expected response:
# {"status":"healthy","service":"django-blog-api"}
```

### 3. Test API Endpoints

```bash
# Test posts endpoint
curl $APP_URL/api/v1/posts/

# Test admin (in browser)
open $APP_URL/admin/

# Test API docs
open $APP_URL/api/v1/docs/
```

---

## 🔄 Automatic Deployments

### How It Works

1. **Push to GitHub** - Commit and push changes to `main` branch
2. **Auto-Deploy** - App Runner detects changes and deploys automatically
3. **Zero Downtime** - Rolling deployment with health checks
4. **Rollback** - Automatic rollback if deployment fails

### Trigger Deployment

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# App Runner will automatically:
# 1. Pull latest code
# 2. Build application
# 3. Run migrations
# 4. Deploy new version
# 5. Health check
# 6. Switch traffic
```

---

## 📊 Monitoring

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/apprunner/blog-api/<service-id>/application --follow

# Or in AWS Console
# CloudWatch → Log groups → /aws/apprunner/blog-api/
```

### Metrics to Monitor

- **Request count** - Total API requests
- **Response time** - Average latency
- **Error rate** - 4xx and 5xx errors
- **CPU usage** - Server load
- **Memory usage** - RAM consumption
- **Health check** - Service availability

---

## 🐛 Troubleshooting

### Deployment Failed

1. **Check build logs** in App Runner console
2. **Verify requirements.txt** has all dependencies
3. **Check environment variables** are set correctly
4. **Test locally** with same environment

### Health Check Failing

1. **Verify port 8080** is configured
2. **Check DATABASE_URL** is correct
3. **Test healthcheck endpoint** locally
4. **Review application logs**

### Application Errors

1. **Check CloudWatch logs** for errors
2. **Verify environment variables**
3. **Test database connection**
4. **Check ALLOWED_HOSTS** includes App Runner domain

---

## 🎯 Post-Deployment Checklist

- [ ] Service deployed successfully
- [ ] Health check passing
- [ ] API endpoints responding
- [ ] Admin panel accessible
- [ ] Database connected
- [ ] Static files loading
- [ ] Environment variables set
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Monitoring enabled
- [ ] Logs accessible
- [ ] Auto-deploy working

---

## 🚀 Next Steps

### 1. Configure Custom Domain

```bash
# In App Runner Console
# Service → Custom domains → Add domain
# Follow DNS configuration instructions
```

### 2. Set Up Database

```bash
# Option A: Amazon RDS PostgreSQL
# Option B: Supabase PostgreSQL (recommended)
# Update DATABASE_URL environment variable
```

### 3. Configure SEO APIs

```bash
# Google Indexing API
# 1. Create service account
# 2. Upload JSON key to S3 or use secrets manager
# 3. Set GOOGLE_SERVICE_ACCOUNT_FILE

# IndexNow
# 1. Generate key: python -c "import secrets; print(secrets.token_hex(32))"
# 2. Set INDEXNOW_KEY environment variable
```

### 4. Enable Monitoring

```bash
# Set up CloudWatch alarms
# Configure Sentry for error tracking
# Enable AWS X-Ray for tracing
```

---

## 📈 Scaling

### Auto-Scaling Configuration

App Runner automatically scales based on:
- **Concurrent requests** - Default: 100 per instance
- **CPU usage** - Scales up at 70%
- **Memory usage** - Scales up at 80%

### Manual Scaling

```bash
# Update instance configuration
aws apprunner update-service \
  --service-arn <service-arn> \
  --instance-configuration '{
    "Cpu": "2 vCPU",
    "Memory": "4 GB"
  }'
```

---

## 💰 Cost Optimization

### Estimated Costs

- **Compute:** $0.064/vCPU-hour + $0.007/GB-hour
- **1 vCPU, 2 GB:** ~$51/month (always on)
- **Auto-scaling:** Pay only for what you use
- **Free tier:** 2,000 build minutes/month

### Tips to Reduce Costs

1. **Use auto-scaling** - Scale down during low traffic
2. **Optimize images** - Reduce build time
3. **Cache effectively** - Reduce compute needs
4. **Monitor usage** - Track and optimize

---

## ✅ Deployment Complete!

Your Django Blog API is now:
- ✅ **Deployed on AWS App Runner**
- ✅ **Auto-deploying from GitHub**
- ✅ **Production ready**
- ✅ **Fully monitored**
- ✅ **Auto-scaling**

**Service URL:** `https://your-app.awsapprunner.com`

**Start building your blog! 🎉**