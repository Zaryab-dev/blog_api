# ⚡ Quick Fix Reference - App Runner 502 Error

## 🔴 Root Causes Found

1. **Gunicorn port 8000** → Should be **8080** ✅ FIXED
2. **ALLOWED_HOSTS missing AWS domains** ✅ FIXED  
3. **Complex healthcheck** ✅ SIMPLIFIED

---

## ✅ What Was Fixed

| File | Change | Status |
|------|--------|--------|
| `gunicorn.conf.py` | Port 8000 → 8080 | ✅ Fixed |
| `settings.py` | Added `.awsapprunner.com` to ALLOWED_HOSTS | ✅ Fixed |
| `views_healthcheck.py` | Created simplified healthcheck | ✅ New |
| `urls.py` | Added healthcheck routes | ✅ Updated |
| `Dockerfile` | Added PYTHONIOENCODING | ✅ Updated |

---

## 🚀 Deploy Now

```bash
# 1. Build
docker build -t leather-api:latest .

# 2. Test locally
docker run -p 8080:8080 --env-file .env.apprunner leather-api:latest
curl http://localhost:8080/api/v1/healthcheck/

# 3. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag leather-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/leather-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/leather-api:latest

# 4. Deploy in App Runner Console or:
aws apprunner start-deployment --service-arn <service-arn>
```

---

## ⚙️ App Runner Settings

**Port:** `8080`  
**Health Check:** `/api/v1/healthcheck/`  
**Interval:** 30s  
**Timeout:** 10s

**Required Env Vars:**
```
SECRET_KEY=<generate>
DEBUG=False
ALLOWED_HOSTS=*,.awsapprunner.com
DATABASE_URL=postgresql://...
```

---

## ✅ Success Check

```bash
curl https://your-app.awsapprunner.com/api/v1/healthcheck/
# Expected: {"status":"healthy","service":"django-blog-api"}
```

---

## 📖 Full Docs

- **Detailed Guide:** `AWS_APPRUNNER_DEPLOYMENT.md`
- **Fix Summary:** `APPRUNNER_FIX_SUMMARY.md`
- **Env Template:** `.env.apprunner`

**Problem solved! Deploy now! 🎉**