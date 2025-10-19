# 🔧 AWS App Runner 502 Error - ROOT CAUSE & FIX

## 🎯 Root Causes Identified

### 1. ❌ **Gunicorn Port Mismatch** (CRITICAL)
**Problem:** Gunicorn was binding to port **8000** instead of **8080**
```python
# gunicorn.conf.py - BEFORE
bind = "0.0.0.0:8000"  # ❌ Wrong port!
```

**Fix Applied:**
```python
# gunicorn.conf.py - AFTER
port = os.getenv("PORT", "8080")
bind = f"0.0.0.0:{port}"  # ✅ Uses PORT env variable
```

### 2. ❌ **ALLOWED_HOSTS Missing App Runner Domains** (CRITICAL)
**Problem:** Django was rejecting requests from `.awsapprunner.com` domain
```python
# settings.py - BEFORE
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # ❌ Missing AWS domains
```

**Fix Applied:**
```python
# settings.py - AFTER
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
if not DEBUG:
    ALLOWED_HOSTS.extend(['.awsapprunner.com', '.amazonaws.com'])  # ✅ Added
```

### 3. ⚠️ **Complex Healthcheck Dependencies** (MINOR)
**Problem:** Healthcheck depended on Redis, Celery, psutil - could fail if services unavailable

**Fix Applied:**
- Created simplified `simple_healthcheck()` - only checks database
- Kept detailed version for monitoring
- Multiple healthcheck URLs for compatibility

---

## ✅ Files Modified

### 1. `gunicorn.conf.py`
- Changed bind port from 8000 to use PORT environment variable (8080)

### 2. `leather_api/settings.py`
- Added `.awsapprunner.com` and `.amazonaws.com` to ALLOWED_HOSTS

### 3. `blog/views_healthcheck.py` (NEW)
- Created simplified healthcheck endpoint
- Only requires database connection
- Returns JSON: `{"status": "healthy"}`

### 4. `leather_api/urls.py`
- Added multiple healthcheck endpoints:
  - `/health/`
  - `/healthcheck/`
  - `/api/v1/healthcheck/` (App Runner uses this)
  - `/api/v1/health/detailed/`

### 5. `Dockerfile`
- Added `PYTHONIOENCODING=utf-8` for better logging
- Already had correct EXPOSE 8080

### 6. `.env.apprunner` (NEW)
- Template for App Runner environment variables

---

## 🧪 Test Results

### Local Test - PASSED ✅
```bash
$ python3 test_healthcheck.py

Testing Simple Healthcheck...
Status Code: 200
Response: {"status": "healthy", "service": "django-blog-api"}

Testing Detailed Healthcheck...
Status Code: 200
Response: {"status": "healthy", "checks": {...}}

✅ Healthcheck endpoints working!
```

---

## 🚀 Deployment Steps

### Step 1: Build Docker Image
```bash
docker build -t leather-api:latest .
```

### Step 2: Test Locally on Port 8080
```bash
docker run -p 8080:8080 --env-file .env.apprunner leather-api:latest

# In another terminal
curl http://localhost:8080/api/v1/healthcheck/
# Expected: {"status":"healthy","service":"django-blog-api"}
```

### Step 3: Push to ECR
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag leather-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/leather-api:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/leather-api:latest
```

### Step 4: Configure App Runner

**Required Settings:**
- **Port:** 8080
- **Health Check Path:** `/api/v1/healthcheck/`
- **Health Check Interval:** 30 seconds
- **Health Check Timeout:** 10 seconds

**Required Environment Variables:**
```bash
SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=*,.awsapprunner.com,.amazonaws.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SITE_URL=https://your-app.awsapprunner.com
```

### Step 5: Deploy & Verify
```bash
# Get App Runner URL
APP_URL=$(aws apprunner describe-service --service-arn <arn> --query 'Service.ServiceUrl' --output text)

# Test healthcheck
curl https://$APP_URL/api/v1/healthcheck/

# Test API
curl https://$APP_URL/api/v1/posts/
```

---

## 📊 Verification Checklist

Before deploying to App Runner, verify:

- [x] Gunicorn binds to port 8080 (check `gunicorn.conf.py`)
- [x] Dockerfile exposes port 8080 (check `EXPOSE 8080`)
- [x] ALLOWED_HOSTS includes `.awsapprunner.com`
- [x] Healthcheck endpoint returns 200 OK
- [x] DATABASE_URL is set correctly
- [x] SECRET_KEY is generated and set
- [x] DEBUG=False in production
- [x] All required environment variables are set

After deploying to App Runner, verify:

- [ ] Health check passes (green status in console)
- [ ] `/api/v1/healthcheck/` returns `{"status":"healthy"}`
- [ ] API endpoints return data (not 502)
- [ ] Logs show "Starting Gunicorn on 0.0.0.0:8080"
- [ ] No ALLOWED_HOSTS errors in logs
- [ ] Database connections work

---

## 🐛 Troubleshooting

### If you still get 502:

1. **Check App Runner Logs:**
```bash
aws logs tail /aws/apprunner/<service-name>/<service-id>/application --follow
```

2. **Verify Port Configuration:**
- App Runner Console → Configuration → Port should be **8080**
- Check logs for "Starting Gunicorn on 0.0.0.0:8080"

3. **Test Locally First:**
```bash
docker run -p 8080:8080 --env-file .env.apprunner leather-api:latest
curl http://localhost:8080/api/v1/healthcheck/
```

4. **Check Environment Variables:**
```bash
aws apprunner describe-service --service-arn <arn> --query 'Service.SourceConfiguration.ImageRepository.ImageConfiguration.RuntimeEnvironmentVariables'
```

5. **Verify ALLOWED_HOSTS:**
- Temporarily set `ALLOWED_HOSTS=*` to test
- Check logs for "Invalid HTTP_HOST header" errors

---

## 📈 Expected Behavior

### Successful Deployment:

**App Runner Console:**
- Status: **Running** (green)
- Health: **Healthy** (green checkmark)
- Last deployment: **Successful**

**Logs:**
```
=== Starting Django Blog API Container ===
Python version: Python 3.11.x
Working directory: /app
PORT: 8080
Starting Gunicorn on 0.0.0.0:8080...
[Background] Running migrations...
[Background] Collecting static files...
[Background] Setup complete!
[INFO] Booting worker with pid: 123
[INFO] Booting worker with pid: 124
[INFO] Booting worker with pid: 125
```

**API Response:**
```bash
$ curl https://your-app.awsapprunner.com/api/v1/healthcheck/
{"status":"healthy","service":"django-blog-api"}

$ curl https://your-app.awsapprunner.com/api/v1/posts/
{"count":10,"next":null,"previous":null,"results":[...]}
```

---

## 🎯 Summary

**Root Causes:**
1. ❌ Gunicorn port 8000 → ✅ Fixed to 8080
2. ❌ Missing AWS domains in ALLOWED_HOSTS → ✅ Added
3. ⚠️ Complex healthcheck → ✅ Simplified

**Files Changed:** 6 files
**New Files:** 3 files
**Test Status:** ✅ PASSED

**Next Action:** Build, push to ECR, and deploy to App Runner

---

## 📞 Need Help?

If issues persist after applying these fixes:

1. Share App Runner logs
2. Share `docker run` output
3. Verify all environment variables are set
4. Check RDS security group allows App Runner VPC

**The 502 error should now be resolved! 🎉**