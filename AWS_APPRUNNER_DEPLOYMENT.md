# 🚀 AWS App Runner Deployment Guide

## ✅ Issues Fixed

### Root Causes Identified:
1. **❌ Gunicorn binding to port 8000** → ✅ Fixed to use PORT=8080
2. **❌ ALLOWED_HOSTS missing .awsapprunner.com** → ✅ Added wildcard and AWS domains
3. **❌ Complex healthcheck with external dependencies** → ✅ Simplified to database-only check

---

## 📋 Pre-Deployment Checklist

### 1. Environment Variables (App Runner Console)
```bash
# Required
SECRET_KEY=<generate-with-django>
DEBUG=False
ALLOWED_HOSTS=*,.awsapprunner.com,.amazonaws.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional but recommended
SITE_URL=https://your-app.awsapprunner.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com
DJANGO_LOG_LEVEL=INFO
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-key
SUPABASE_BUCKET=your-bucket
```

### 2. Build & Push Docker Image
```bash
# Build for App Runner
docker build -t leather-api:latest .

# Tag for ECR
docker tag leather-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/leather-api:latest

# Login to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# Push to ECR
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/leather-api:latest
```

### 3. App Runner Configuration
- **Port:** 8080
- **Health Check Path:** `/api/v1/healthcheck/`
- **Health Check Interval:** 30 seconds
- **Health Check Timeout:** 10 seconds
- **Health Check Healthy Threshold:** 1
- **Health Check Unhealthy Threshold:** 3

---

## 🔍 Verification Steps

### Step 1: Test Locally
```bash
# Build and run locally
docker build -t leather-api:test .
docker run -p 8080:8080 --env-file .env.apprunner leather-api:test

# Test healthcheck
curl http://localhost:8080/api/v1/healthcheck/
# Expected: {"status":"healthy","service":"django-blog-api"}

# Test API
curl http://localhost:8080/api/v1/posts/
```

### Step 2: Check App Runner Logs
```bash
# List operations
aws apprunner list-operations --service-arn <service-arn>

# Describe service
aws apprunner describe-service --service-arn <service-arn>

# Get logs (CloudWatch)
aws logs tail /aws/apprunner/<service-name>/<service-id>/application --follow
```

### Step 3: Test Deployed Service
```bash
# Get App Runner URL
APP_URL=$(aws apprunner describe-service --service-arn <service-arn> --query 'Service.ServiceUrl' --output text)

# Test healthcheck
curl https://$APP_URL/api/v1/healthcheck/

# Test API
curl https://$APP_URL/api/v1/posts/
```

---

## 🐛 Troubleshooting

### Issue: 502 Bad Gateway
**Causes:**
- Gunicorn not binding to port 8080
- App Runner port configuration mismatch
- Application crash on startup

**Solutions:**
1. Check logs: `aws logs tail /aws/apprunner/<service-name>/<service-id>/application`
2. Verify PORT=8080 in environment variables
3. Test locally with same environment variables

### Issue: Health Check Failing
**Causes:**
- Database connection issues
- ALLOWED_HOSTS misconfigured
- Healthcheck endpoint not responding

**Solutions:**
1. Test healthcheck locally: `curl http://localhost:8080/api/v1/healthcheck/`
2. Verify DATABASE_URL is correct
3. Check ALLOWED_HOSTS includes `.awsapprunner.com`

### Issue: Blank Response
**Causes:**
- ALLOWED_HOSTS blocking requests
- CORS misconfiguration
- Static files not collected

**Solutions:**
1. Add `ALLOWED_HOSTS=*` temporarily for testing
2. Check CORS_ALLOWED_ORIGINS includes your frontend
3. Verify collectstatic runs in entrypoint

### Issue: Database Connection Error
**Causes:**
- DATABASE_URL incorrect
- RDS security group blocking App Runner
- Database credentials wrong

**Solutions:**
1. Test DATABASE_URL locally
2. Add App Runner VPC to RDS security group
3. Verify database credentials in AWS Secrets Manager

---

## 📊 Key Files Changed

### 1. `gunicorn.conf.py`
```python
# Before
bind = "0.0.0.0:8000"

# After
port = os.getenv("PORT", "8080")
bind = f"0.0.0.0:{port}"
```

### 2. `leather_api/settings.py`
```python
# Before
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

# After
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
if not DEBUG:
    ALLOWED_HOSTS.extend(['.awsapprunner.com', '.amazonaws.com'])
```

### 3. `blog/views_healthcheck.py` (NEW)
```python
@never_cache
@require_http_methods(["GET"])
def simple_healthcheck(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)
```

### 4. `Dockerfile`
```dockerfile
# Added
ENV PYTHONIOENCODING=utf-8

# Already correct
EXPOSE 8080
CMD ["/bin/bash", "/app/docker-entrypoint.sh"]
```

### 5. `docker-entrypoint.sh`
```bash
# Already correct - uses PORT env variable
PORT=${PORT:-8080}
exec gunicorn --bind 0.0.0.0:$PORT leather_api.wsgi:application
```

---

## 🎯 Deployment Commands

### Quick Deploy
```bash
# 1. Build
docker build -t leather-api:latest .

# 2. Tag
docker tag leather-api:latest <ecr-repo-url>:latest

# 3. Push
docker push <ecr-repo-url>:latest

# 4. Trigger App Runner deployment (automatic if configured)
# Or manually: AWS Console → App Runner → Deploy
```

### Full Redeploy
```bash
# 1. Stop service
aws apprunner pause-service --service-arn <service-arn>

# 2. Update configuration
aws apprunner update-service \
  --service-arn <service-arn> \
  --source-configuration file://apprunner-config.json

# 3. Resume service
aws apprunner resume-service --service-arn <service-arn>
```

---

## ✅ Success Criteria

Your deployment is successful when:
- ✅ Health check returns `{"status":"healthy"}`
- ✅ API endpoints respond with data
- ✅ No 502 errors
- ✅ Logs show "Starting Gunicorn on 0.0.0.0:8080"
- ✅ Database queries work
- ✅ Static files load correctly

---

## 📞 Support

If issues persist:
1. Check CloudWatch logs
2. Test locally with same environment
3. Verify all environment variables
4. Check RDS/database connectivity
5. Review App Runner service events

**Common Commands:**
```bash
# View logs
aws logs tail /aws/apprunner/<service-name>/<service-id>/application --follow

# Describe service
aws apprunner describe-service --service-arn <service-arn>

# List operations
aws apprunner list-operations --service-arn <service-arn>
```

---

## 🎉 Next Steps

After successful deployment:
1. Configure custom domain
2. Set up CloudFront CDN
3. Enable auto-scaling
4. Configure monitoring alerts
5. Set up CI/CD pipeline

**Your Django API is now ready for production on AWS App Runner! 🚀**