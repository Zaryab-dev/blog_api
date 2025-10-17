# Docker Quick Start Guide

Fast guide to build, test, and deploy your Django Blog API with Docker.

---

## 🚀 Quick Commands

### Local Development

```bash
# Build image
docker build -t django-blog-api .

# Run with environment file
docker run -p 8000:8000 --env-file .env django-blog-api

# Or run with docker-compose
docker-compose up
```

### Test Locally

```bash
# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/v1/posts/
curl http://localhost:8000/api/v1/healthcheck/

# Stop services
docker-compose down
```

---

## 📦 What's Included

### Dockerfile Features

✅ **Multi-stage build** - Smaller final image (~200MB)
✅ **Python 3.11 slim** - Latest stable Python
✅ **Non-root user** - Security best practice
✅ **Health checks** - Automatic monitoring
✅ **Static files** - Collected during build
✅ **Optimized layers** - Better caching
✅ **Production-ready** - Gunicorn with 3 workers

### Files Created

- **Dockerfile** - Production-ready container
- **docker-compose.yml** - Local testing environment
- **.dockerignore** - Excludes unnecessary files
- **apprunner.yaml** - AWS App Runner config

---

## 🔧 Configuration Changes Made

### 1. Dockerfile Optimizations

**Added:**
- `collectstatic` runs during build
- WhiteNoise for static file serving
- Health check endpoint
- Proper worker configuration (3 workers, 2 threads)

**Command:**
```bash
gunicorn --bind 0.0.0.0:8000 \
         --workers 3 \
         --threads 2 \
         --timeout 60 \
         --access-logfile - \
         --error-logfile - \
         --log-level info \
         leather_api.wsgi:application
```

### 2. Settings.py Updates

**Added WhiteNoise middleware:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added
    'corsheaders.middleware.CorsMiddleware',
    # ... rest
]
```

**Added static files configuration:**
```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Requirements.txt

Already includes:
- ✅ gunicorn>=21.2,<22.0
- ✅ whitenoise>=6.6,<7.0
- ✅ psycopg2-binary>=2.9,<3.0

---

## 🧪 Testing Checklist

### Before Deployment

```bash
# 1. Build succeeds
docker build -t django-blog-api .

# 2. Container starts
docker run -d -p 8000:8000 --env-file .env --name test-api django-blog-api

# 3. Health check passes
curl http://localhost:8000/api/v1/healthcheck/
# Expected: {"status": "healthy"}

# 4. API responds
curl http://localhost:8000/api/v1/posts/
# Expected: JSON response with posts

# 5. Static files load
curl -I http://localhost:8000/static/admin/css/base.css
# Expected: 200 OK

# 6. Admin accessible
curl -I http://localhost:8000/admin/
# Expected: 200 or 302

# 7. Landing page works
curl http://localhost:8000/
# Expected: HTML landing page

# Cleanup
docker stop test-api && docker rm test-api
```

---

## 🌐 Environment Variables

### Required for Production

```bash
# Django Core
DEBUG=False
SECRET_KEY=your-secret-key-min-50-chars
ALLOWED_HOSTS=yourdomain.com,*.amazonaws.com
SITE_URL=https://yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Supabase Storage
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_API_KEY=your-api-key
SUPABASE_BUCKET=your-bucket

# Redis (optional but recommended)
REDIS_URL=redis://host:6379/0

# Security
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

### Create .env File

```bash
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=django-insecure-change-this-to-50-plus-random-characters
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:pass@localhost:5432/blog
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_API_KEY=your-key
SUPABASE_BUCKET=your-bucket
REDIS_URL=redis://localhost:6379/0
EOF
```

---

## 📊 Image Size Optimization

### Current Image Size

```bash
docker images django-blog-api
# Expected: ~200-250MB
```

### Size Breakdown

- Base image (python:3.11-slim): ~120MB
- Dependencies: ~80MB
- Application code: ~10MB
- Static files: ~5MB

### Further Optimization (Optional)

```dockerfile
# Use alpine for even smaller size (~150MB)
FROM python:3.11-alpine

# But requires additional build dependencies
RUN apk add --no-cache postgresql-dev gcc musl-dev
```

---

## 🚢 Deployment Options

### 1. AWS App Runner (Easiest)

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
docker tag django-blog-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# Deploy
aws apprunner create-service --cli-input-json file://apprunner-config.json
```

**See:** `AWS_APP_RUNNER_DEPLOYMENT.md`

### 2. AWS ECS Fargate

```bash
# Push to ECR (same as above)
# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service --cluster blog-cluster --service-name blog-api --task-definition blog-api
```

**See:** `AWS_DEPLOYMENT_GUIDE.md`

### 3. AWS EC2

```bash
# SSH to EC2
ssh -i key.pem ubuntu@ec2-ip

# Pull and run
docker pull $ECR_URI:latest
docker run -d -p 8000:8000 --env-file .env $ECR_URI:latest
```

---

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs <container-id>

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port already in use
```

### Static Files Not Loading

```bash
# Verify collectstatic ran
docker run django-blog-api ls -la /app/staticfiles/

# Should see admin/, css/, js/ directories
```

### Database Connection Failed

```bash
# Test database connection
docker run --rm django-blog-api python manage.py check --database default

# Check DATABASE_URL format
# postgresql://user:password@host:5432/database
```

### Permission Denied

```bash
# Check file ownership
docker run django-blog-api ls -la /app/

# Should be owned by appuser (uid 1000)
```

---

## 📈 Performance Tuning

### Worker Configuration

```bash
# Formula: (2 x CPU cores) + 1
# 1 vCPU = 3 workers (current)
# 2 vCPU = 5 workers
# 4 vCPU = 9 workers

# Update in Dockerfile CMD:
--workers 5  # for 2 vCPU
```

### Memory Optimization

```bash
# Monitor memory usage
docker stats

# Adjust worker threads if needed
--threads 4  # increase for I/O bound tasks
```

---

## 🔐 Security Checklist

- [x] Non-root user (appuser)
- [x] No secrets in Dockerfile
- [x] .dockerignore configured
- [x] Health checks enabled
- [x] Minimal base image (slim)
- [x] Security headers middleware
- [x] HTTPS enforced (in production)
- [x] Debug mode disabled

---

## 📚 Next Steps

1. **Test locally**: `docker-compose up`
2. **Push to ECR**: Follow AWS_APP_RUNNER_DEPLOYMENT.md
3. **Deploy to App Runner**: ~10 minutes
4. **Configure domain**: Add custom domain
5. **Set up monitoring**: CloudWatch logs
6. **Enable auto-scaling**: Based on traffic

---

## ✨ Summary

Your Docker setup is **production-ready** with:
- ✅ Optimized multi-stage build
- ✅ WhiteNoise for static files
- ✅ Health checks configured
- ✅ Non-root user for security
- ✅ Gunicorn with proper workers
- ✅ AWS App Runner compatible
- ✅ ~200MB image size

**Build time:** ~2-3 minutes
**Image size:** ~200-250MB
**Ready to deploy!** 🚀
