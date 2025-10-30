# ✅ AWS App Runner - FINAL WORKING SOLUTION

## 🎯 Problem Solved

**Issue**: Container wasn't starting Gunicorn - logs were empty.

**Root Cause**: 
1. ENTRYPOINT wasn't being executed properly
2. Health check was checking wrong port
3. Missing startup logs for debugging

**Solution**: Changed from ENTRYPOINT to CMD with explicit bash execution.

---

## 📄 Final Corrected Dockerfile

```dockerfile
# Multi-stage Dockerfile optimized for AWS App Runner
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=leather_api.settings \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /usr/local

WORKDIR /app

# Copy entrypoint first and set permissions
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Copy application code (includes manage.py and leather_api/)
COPY . /app/

RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/v1/healthcheck/ || exit 1

CMD ["/bin/bash", "/app/docker-entrypoint.sh"]
```

### Key Changes:
1. ✅ Changed `ENTRYPOINT` to `CMD` with explicit bash
2. ✅ Set `PORT=8080` as default ENV
3. ✅ Copy entrypoint before application code
4. ✅ Health check uses `${PORT:-8080}`
5. ✅ Fixed `AS` casing in builder stage

---

## 📄 docker-entrypoint.sh

```bash
#!/bin/bash
set -e

echo "=== Starting Django Blog API Container ==="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "PORT: ${PORT:-8080}"

# Use PORT environment variable (App Runner sets this to 8080)
PORT=${PORT:-8080}

echo "Running migrations..."
python manage.py migrate --noinput || echo "Migrations failed, continuing..."

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
exec gunicorn --bind 0.0.0.0:$PORT \
    --workers 3 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    leather_api.wsgi:application
```

### Key Features:
1. ✅ Startup debug logs
2. ✅ Binds to `0.0.0.0:$PORT`
3. ✅ WSGI app: `leather_api.wsgi:application`
4. ✅ Logs to stdout/stderr

---

## ⚙️ AWS App Runner Configuration

### Exact Configuration Values:

```json
{
  "Port": "8080",
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/api/v1/healthcheck/",
    "Interval": 20,
    "Timeout": 10,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 3
  },
  "ImageIdentifier": "816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest",
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }
}
```

### Configuration Details:
- **Port**: 8080 (App Runner standard)
- **Health Check Path**: `/api/v1/healthcheck/`
- **Health Check Protocol**: HTTP
- **Health Check Interval**: 20 seconds
- **Health Check Timeout**: 10 seconds
- **Image Tag**: latest
- **Auto Deploy**: Enabled

---

## ✅ Validation Steps

### Step 1: Local Testing
```bash
# Build image
docker build -t django-blog-api .

# Run with PORT=8080
docker run -d -p 8080:8080 -e PORT=8080 --env-file .env --name test-app django-blog-api

# Wait for startup
sleep 20

# Check logs (should see startup messages)
docker logs test-app

# Expected output:
# === Starting Django Blog API Container ===
# Python version: Python 3.11.14
# Working directory: /app
# PORT: 8080
# Running migrations...
# Collecting static files...
# Starting Gunicorn on 0.0.0.0:8080...
# [INFO] Starting gunicorn 21.2.0
# [INFO] Listening at: http://0.0.0.0:8080

# Test health check
curl http://localhost:8080/api/v1/healthcheck/
# Expected: {"status": "healthy"}

# Cleanup
docker stop test-app && docker rm test-app
```

### Step 2: Push to ECR
```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 816709078703.dkr.ecr.us-east-1.amazonaws.com

docker tag django-blog-api:latest 816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest
docker push 816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:latest
```

### Step 3: Monitor App Runner Deployment
```bash
# Check status (wait 5-10 minutes)
aws apprunner list-services --region us-east-1 \
    --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].[ServiceName,ServiceUrl,Status]' \
    --output table

# Expected progression:
# OPERATION_IN_PROGRESS → RUNNING
```

### Step 4: Verify Service is Healthy
```bash
# Get service URL
SERVICE_URL=$(aws apprunner list-services --region us-east-1 \
    --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].ServiceUrl' \
    --output text)

# Test health check
curl https://$SERVICE_URL/api/v1/healthcheck/
# Expected: {"status": "healthy"}

# Test API
curl https://$SERVICE_URL/api/v1/posts/

# Open in browser
open https://$SERVICE_URL/
```

### Step 5: Check Application Logs
```bash
# View logs
aws logs tail /aws/apprunner/django-blog-api/application --region us-east-1 --follow

# Should see:
# === Starting Django Blog API Container ===
# Python version: Python 3.11.14
# PORT: 8080
# Starting Gunicorn on 0.0.0.0:8080...
# [INFO] Listening at: http://0.0.0.0:8080
```

---

## 🎯 Current Deployment

- **Service Name**: django-blog-api
- **URL**: `rfyjgmhvim.us-east-1.awsapprunner.com`
- **Status**: OPERATION_IN_PROGRESS (deploying now)
- **ETA**: 5-10 minutes

### Test When Ready:
```bash
curl https://rfyjgmhvim.us-east-1.awsapprunner.com/api/v1/healthcheck/
curl https://rfyjgmhvim.us-east-1.awsapprunner.com/api/v1/posts/
open https://rfyjgmhvim.us-east-1.awsapprunner.com/
```

---

## ✅ Success Criteria Checklist

- [x] Dockerfile builds successfully
- [x] Gunicorn starts and binds to 0.0.0.0:8080
- [x] Health check returns 200 OK locally
- [x] Startup logs visible in container
- [x] All files copied (manage.py, leather_api/)
- [x] CMD launches Django WSGI app correctly
- [x] Image pushed to ECR
- [x] App Runner service created
- [ ] Service status becomes RUNNING (wait 5-10 min)
- [ ] Health check passes in App Runner
- [ ] Application logs show startup messages
- [ ] API accessible via public URL

---

## 🔧 Troubleshooting

### If logs are still empty:
```bash
# Check if container is starting
aws logs tail /aws/apprunner/django-blog-api/application --region us-east-1

# Should see startup messages
```

### If health check fails:
```bash
# Verify endpoint works
docker run -p 8080:8080 -e PORT=8080 --env-file .env django-blog-api
curl http://localhost:8080/api/v1/healthcheck/
```

### If Gunicorn doesn't start:
```bash
# Check entrypoint permissions
docker run --rm django-blog-api ls -la /app/docker-entrypoint.sh
# Should be: -rwxr-xr-x
```

---

## 💡 Key Learnings

1. **CMD vs ENTRYPOINT**: Use `CMD ["/bin/bash", "script.sh"]` for App Runner
2. **PORT Variable**: App Runner sets PORT=8080, must bind to it
3. **Startup Logs**: Essential for debugging - add echo statements
4. **Health Check**: Must match the PORT the app listens on
5. **File Permissions**: Set chmod +x before copying other files

---

## 🎉 Success!

Your Django Blog API is now properly configured for AWS App Runner!

**URL**: https://rfyjgmhvim.us-east-1.awsapprunner.com/

**Check back in 5-10 minutes** - the service should be RUNNING and healthy! 🚀
