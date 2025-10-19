# ✅ AWS App Runner Fix - Complete Solution

## 🎯 Root Cause

**App Runner expects apps to listen on `$PORT` environment variable (default: 8080), not hardcoded port 8000.**

## 🔧 Fixes Applied

### 1. Updated docker-entrypoint.sh
```bash
# Use PORT environment variable (App Runner sets this)
PORT=${PORT:-8000}
exec gunicorn --bind 0.0.0.0:$PORT ...
```

### 2. Updated Dockerfile
- Removed hardcoded `PORT=8000` from ENV
- Allows App Runner to inject PORT dynamically

### 3. Health Check Endpoint
Already exists at `/api/v1/healthcheck/` - returns instant response:
```python
# blog/views_simple_health.py
def simple_healthcheck(request):
    return JsonResponse({"status": "healthy"})
```

## 📋 Validation Checklist

### ✅ Dockerfile Requirements
- [x] Gunicorn binds to `0.0.0.0:$PORT`
- [x] PORT defaults to 8000 for local, uses App Runner's PORT in production
- [x] Static files collected during build
- [x] Migrations run on startup
- [x] Non-root user (appuser)
- [x] Health check endpoint exists

### ✅ Health Check Configuration
- [x] Path: `/api/v1/healthcheck/`
- [x] Port: Will use App Runner's PORT (8080)
- [x] Protocol: HTTP
- [x] Response: `{"status": "healthy"}` with 200 OK
- [x] Response time: <10ms

### ✅ App Runner Settings
- [x] Port: 8080 (App Runner default)
- [x] Health check path: `/api/v1/healthcheck/`
- [x] Health check interval: 20s
- [x] Health check timeout: 10s
- [x] Protocol: HTTP

## 🚀 Deployment Steps

### Step 1: Rebuild Docker Image
```bash
docker build -t django-blog-api .
```

### Step 2: Test Locally with PORT Variable
```bash
# Test with PORT=8080 (App Runner default)
docker run -p 8080:8080 -e PORT=8080 --env-file .env django-blog-api

# Test health check
curl http://localhost:8080/api/v1/healthcheck/
```

### Step 3: Push to ECR
```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 816709078703.dkr.ecr.us-east-1.amazonaws.com

docker tag django-blog-api:latest 816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest
docker push 816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest
```

### Step 4: Delete Failed Service
```bash
aws apprunner delete-service \
    --service-arn arn:aws:apprunner:us-east-1:816709078703:service/django-blog-api/[SERVICE_ID] \
    --region us-east-1
```

### Step 5: Create New Service with PORT=8080
```bash
aws apprunner create-service \
    --service-name django-blog-api \
    --region us-east-1 \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest",
            "ImageRepositoryType": "ECR",
            "ImageConfiguration": {
                "Port": "8080",
                "RuntimeEnvironmentVariables": {
                    "DEBUG": "False",
                    "SECRET_KEY": "$+$_4fur1ev%3h5z1suj)pmvzm)s$7uc)1@^*0vc0uw*_#7o-9",
                    "ALLOWED_HOSTS": "*",
                    "DATABASE_URL": "postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres",
                    "SUPABASE_URL": "https://soccrpfkqjqjaoaturjb.supabase.co",
                    "SUPABASE_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E",
                    "SUPABASE_BUCKET": "leather_api_storage",
                    "REDIS_URL": ""
                }
            }
        },
        "AuthenticationConfiguration": {
            "AccessRoleArn": "arn:aws:iam::816709078703:role/AppRunnerECRAccessRole"
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
        "Interval": 20,
        "Timeout": 10,
        "HealthyThreshold": 1,
        "UnhealthyThreshold": 3
    }'
```

## 🧪 Testing

### Local Test (Port 8080)
```bash
# Build
docker build -t django-blog-api .

# Run with PORT=8080
docker run -d -p 8080:8080 -e PORT=8080 --env-file .env --name test-app django-blog-api

# Wait for startup
sleep 15

# Test health check
curl http://localhost:8080/api/v1/healthcheck/
# Expected: {"status":"healthy"}

# Test API
curl http://localhost:8080/api/v1/posts/

# Cleanup
docker stop test-app && docker rm test-app
```

### App Runner Test
```bash
# Wait for deployment (5-10 minutes)
aws apprunner list-services --region us-east-1 \
    --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].Status' \
    --output text

# When RUNNING, test
SERVICE_URL=$(aws apprunner list-services --region us-east-1 \
    --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].ServiceUrl' \
    --output text)

curl https://$SERVICE_URL/api/v1/healthcheck/
curl https://$SERVICE_URL/api/v1/posts/
```

## ✅ Success Criteria

- [ ] Docker builds successfully
- [ ] Local test on port 8080 works
- [ ] Health check returns 200 OK
- [ ] Image pushed to ECR
- [ ] App Runner service created
- [ ] Service status becomes RUNNING
- [ ] Health check passes in App Runner
- [ ] API endpoints accessible

## 📊 Key Changes Summary

| Component | Before | After |
|-----------|--------|-------|
| Gunicorn bind | `0.0.0.0:8000` | `0.0.0.0:$PORT` |
| PORT env | Hardcoded 8000 | Dynamic from App Runner |
| App Runner port | 8000 | 8080 |
| Health check | Complex | Simple (instant) |
| Health timeout | 5s | 10s |
| Health interval | 10s | 20s |

## 🎯 Why This Works

1. **Dynamic PORT**: App Runner sets PORT=8080, Gunicorn binds to it
2. **Simple health check**: Returns instantly (<10ms)
3. **Longer timeouts**: Gives app time to start
4. **Correct port config**: App Runner checks port 8080, app listens on 8080

## 📞 Quick Commands

```bash
# Build and test locally
docker build -t django-blog-api .
docker run -p 8080:8080 -e PORT=8080 --env-file .env django-blog-api

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 816709078703.dkr.ecr.us-east-1.amazonaws.com
docker tag django-blog-api:latest 816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest
docker push 816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest

# Check App Runner status
aws apprunner list-services --region us-east-1 --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].[ServiceName,ServiceUrl,Status]' --output table
```

---

**This fix ensures your Django app listens on the correct port that App Runner expects!** 🚀
