# 🚀 Complete AWS App Runner Deployment Guide

## ✅ PRE-DEPLOYMENT CHECKLIST

### Critical Fix Applied ✓
- **Health check import fixed** in `leather_api/urls.py`
- Now uses `blog.views_simple_health.simple_healthcheck` (no DB queries)
- App Runner health checks will pass immediately

### Files Ready ✓
- ✅ `Dockerfile` - Optimized for App Runner
- ✅ `docker-entrypoint.sh` - Starts Gunicorn immediately
- ✅ `gunicorn.conf.py` - Production configuration
- ✅ `requirements.txt` - All dependencies
- ✅ `blog/views_simple_health.py` - Fast health check
- ✅ `leather_api/urls.py` - Correct routing

---

## 📋 DEPLOYMENT PHASES

### PHASE 1: AWS PREREQUISITES

#### 1.1 AWS Account Setup
```bash
# Install AWS CLI (if not installed)
# macOS:
brew install awscli

# Configure AWS credentials
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

#### 1.2 Get Your AWS Account ID
```bash
aws sts get-caller-identity --query Account --output text
```
**Save this number!** You'll need it for the deployment script.

---

### PHASE 2: CONFIGURE DEPLOYMENT SCRIPT

#### 2.1 Edit `DEPLOY_TO_APPRUNNER.sh`
```bash
nano DEPLOY_TO_APPRUNNER.sh
```

Update these lines (around line 15-19):
```bash
AWS_REGION="us-east-1"                    # Your AWS region
AWS_ACCOUNT_ID="123456789012"             # YOUR account ID from step 1.2
ECR_REPO_NAME="blog-api"                  # ECR repository name
APP_RUNNER_SERVICE_NAME="django-blog-api" # App Runner service name
IMAGE_TAG="latest"                        # Image tag
```

Save and exit (Ctrl+X, Y, Enter)

---

### PHASE 3: PREPARE ENVIRONMENT VARIABLES

#### 3.1 Update `.env.apprunner`
```bash
nano .env.apprunner
```

**CRITICAL: Update these values:**
```bash
# Generate a new SECRET_KEY
SECRET_KEY=your-production-secret-key-min-50-chars-random

# Database - Use your Supabase PostgreSQL URL
DATABASE_URL=postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres

# Supabase Storage (already correct from your .env)
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E
SUPABASE_BUCKET=leather_api_storage

# Keep these as-is for now
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=*,.awsapprunner.com,.amazonaws.com
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### PHASE 4: BUILD AND PUSH TO ECR

#### 4.1 Run Deployment Script
```bash
./DEPLOY_TO_APPRUNNER.sh
```

**What this does:**
1. ✅ Checks AWS CLI and Docker
2. ✅ Creates ECR repository (if needed)
3. ✅ Logs into ECR
4. ✅ Builds Docker image
5. ✅ Tags image
6. ✅ Pushes to ECR

**Expected output:**
```
╔════════════════════════════════════════════════════════════╗
║   AWS App Runner Deployment Script                        ║
║   Django Blog API                                          ║
╚════════════════════════════════════════════════════════════╝

▶ Pre-flight Checks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ AWS CLI installed
✓ Docker installed
✓ AWS credentials configured

▶ Step 1: Checking ECR Repository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ ECR repository 'blog-api' exists

▶ Step 2: Logging into ECR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Logged into ECR

▶ Step 3: Building Docker Image
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Building image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/blog-api:latest
[+] Building 45.2s (15/15) FINISHED
✓ Docker image built

▶ Step 4: Tagging Image
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Image tagged

▶ Step 5: Pushing to ECR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
latest: digest: sha256:abc123... size: 2841
✓ Image pushed to ECR

✓ Deployment script completed!
```

---

### PHASE 5: CREATE APP RUNNER SERVICE

#### 5.1 Go to AWS Console
1. Open: https://console.aws.amazon.com/apprunner
2. Click **"Create service"**

#### 5.2 Configure Source
- **Repository type:** Container registry
- **Provider:** Amazon ECR
- **Container image URI:** Click "Browse" and select:
  - Repository: `blog-api`
  - Image tag: `latest`
- **Deployment trigger:** Manual
- Click **"Next"**

#### 5.3 Configure Service
**Service settings:**
- **Service name:** `django-blog-api`
- **Virtual CPU:** 1 vCPU
- **Memory:** 2 GB

**Environment variables:** Click "Add environment variable" for each:
```
SECRET_KEY = <your-generated-secret-key>
DEBUG = False
ENVIRONMENT = production
ALLOWED_HOSTS = *,.awsapprunner.com,.amazonaws.com
DATABASE_URL = postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres
SUPABASE_URL = https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E
SUPABASE_BUCKET = leather_api_storage
DJANGO_LOG_LEVEL = INFO
ANON_THROTTLE_RATE = 100/hour
USER_THROTTLE_RATE = 1000/hour
SECURE_PROXY_SSL_HEADER_ENABLED = True
```

**Port:** `8080`

#### 5.4 Configure Health Check
- **Protocol:** HTTP
- **Path:** `/api/v1/healthcheck/`
- **Interval:** 10 seconds
- **Timeout:** 5 seconds
- **Healthy threshold:** 1
- **Unhealthy threshold:** 5

#### 5.5 Configure Auto Scaling (Optional)
- **Min instances:** 1
- **Max instances:** 3
- **Concurrency:** 100

Click **"Next"** → **"Create & deploy"**

---

### PHASE 6: MONITOR DEPLOYMENT

#### 6.1 Watch Service Status
In App Runner console, you'll see:
```
Status: Creating → Running
```

**Timeline:**
- 0-2 min: Creating infrastructure
- 2-4 min: Pulling image from ECR
- 4-5 min: Starting container
- 5-6 min: Health checks passing
- **6 min: RUNNING ✅**

#### 6.2 Get Service URL
Once status is **RUNNING**, copy the service URL:
```
https://abc123xyz.us-east-1.awsapprunner.com
```

---

### PHASE 7: VERIFY DEPLOYMENT

#### 7.1 Test Health Check
```bash
# Replace with your actual App Runner URL
curl https://abc123xyz.us-east-1.awsapprunner.com/api/v1/healthcheck/
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "django-blog-api"
}
```

#### 7.2 Test API Endpoints
```bash
# List posts
curl https://abc123xyz.us-east-1.awsapprunner.com/api/v1/posts/

# API documentation
open https://abc123xyz.us-east-1.awsapprunner.com/api/v1/docs/
```

#### 7.3 Check Logs
In App Runner console:
1. Click on your service
2. Go to **"Logs"** tab
3. Click **"View in CloudWatch"**

Look for:
```
Starting Gunicorn on 0.0.0.0:8080...
[Background] Running migrations...
[Background] Collecting static files...
[Background] Setup complete!
```

---

## 🎯 POST-DEPLOYMENT TASKS

### Update Frontend URLs
Update your Next.js `.env`:
```bash
NEXT_PUBLIC_API_URL=https://abc123xyz.us-east-1.awsapprunner.com
```

### Update CORS Settings
Add your frontend domain to App Runner environment variables:
```
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://abc123xyz.us-east-1.awsapprunner.com,https://your-frontend.vercel.app
```

### Run Database Migrations (if needed)
```bash
# Connect to App Runner service and run migrations
# This is done automatically in docker-entrypoint.sh
```

---

## 🔧 TROUBLESHOOTING

### Issue: Health Check Failing
**Symptoms:** Service stuck in "Creating" or "Unhealthy"

**Solution:**
1. Check CloudWatch logs for errors
2. Verify health check path: `/api/v1/healthcheck/`
3. Ensure port is `8080`
4. Check DATABASE_URL is correct

### Issue: Database Connection Error
**Symptoms:** 500 errors, "could not connect to server"

**Solution:**
1. Verify DATABASE_URL format:
   ```
   postgresql://user:password@host:port/database
   ```
2. Check Supabase connection pooler is enabled
3. Ensure App Runner has internet access (default VPC)

### Issue: Static Files Not Loading
**Symptoms:** Admin panel has no CSS

**Solution:**
1. Check logs for "Collecting static files..."
2. Verify `STATIC_ROOT=staticfiles` in environment variables
3. WhiteNoise is configured in settings.py ✅

### Issue: Image Upload Failing
**Symptoms:** CKEditor upload errors

**Solution:**
1. Verify SUPABASE_URL, SUPABASE_API_KEY, SUPABASE_BUCKET
2. Check Supabase bucket permissions (public read)
3. Test upload endpoint: `/upload/ckeditor/`

---

## 📊 MONITORING

### CloudWatch Metrics
- **Request count:** Monitor traffic
- **Response time:** Track performance
- **Error rate:** Watch for issues
- **CPU/Memory:** Check resource usage

### Set Up Alarms
1. Go to CloudWatch → Alarms
2. Create alarm for:
   - High error rate (> 5%)
   - High response time (> 2s)
   - Low health check success rate (< 90%)

---

## 🔄 UPDATING THE SERVICE

### Deploy New Version
```bash
# 1. Make code changes
# 2. Run deployment script again
./DEPLOY_TO_APPRUNNER.sh

# 3. In App Runner console, click "Deploy"
# Service will automatically pull new image
```

### Rollback
1. Go to App Runner console
2. Click "Deployments" tab
3. Find previous successful deployment
4. Click "Redeploy"

---

## 💰 COST ESTIMATION

**App Runner Pricing (us-east-1):**
- **Provisioned:** $0.007/hour (1 vCPU, 2 GB) = ~$5/month
- **Compute:** $0.064/vCPU-hour + $0.007/GB-hour
- **Build:** Free (using ECR)

**Estimated monthly cost:** $10-30 depending on traffic

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] AWS CLI configured
- [ ] Docker installed
- [ ] AWS Account ID obtained
- [ ] Deployment script configured
- [ ] SECRET_KEY generated
- [ ] Environment variables prepared
- [ ] ECR repository created
- [ ] Docker image built and pushed
- [ ] App Runner service created
- [ ] Environment variables added
- [ ] Health check configured
- [ ] Service status: RUNNING
- [ ] Health check endpoint tested
- [ ] API endpoints tested
- [ ] Frontend URLs updated
- [ ] CORS configured
- [ ] CloudWatch logs checked
- [ ] Monitoring set up

---

## 🎉 SUCCESS CRITERIA

Your deployment is successful when:
1. ✅ App Runner status: **RUNNING**
2. ✅ Health check: Returns `{"status": "healthy"}`
3. ✅ API docs: Accessible at `/api/v1/docs/`
4. ✅ Posts endpoint: Returns data
5. ✅ Admin panel: Loads with CSS
6. ✅ Image upload: Works in CKEditor
7. ✅ No errors in CloudWatch logs

---

## 📞 SUPPORT

If you encounter issues:
1. Check CloudWatch logs first
2. Review this guide's troubleshooting section
3. Verify all environment variables
4. Test health check endpoint manually
5. Check Supabase database connectivity

---

**🚀 You're ready to deploy! Run `./DEPLOY_TO_APPRUNNER.sh` to begin.**
