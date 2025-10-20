# ⚡ AWS App Runner - Quick Start (5 Minutes)

## 🎯 Prerequisites
- AWS CLI installed and configured
- Docker installed
- AWS Account ID

## 🚀 Deploy in 3 Steps

### Step 1: Configure (1 minute)
```bash
# Get your AWS Account ID
aws sts get-caller-identity --query Account --output text

# Edit deployment script
nano DEPLOY_TO_APPRUNNER.sh
# Update line 15: AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
# Save: Ctrl+X, Y, Enter

# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy this key for Step 3
```

### Step 2: Build & Push (3 minutes)
```bash
# Run deployment script
./DEPLOY_TO_APPRUNNER.sh

# Wait for:
# ✓ ECR repository created
# ✓ Docker image built
# ✓ Image pushed to ECR
```

### Step 3: Create Service (1 minute)
1. Open: https://console.aws.amazon.com/apprunner
2. Click **"Create service"**
3. Select:
   - Repository: `blog-api`
   - Image tag: `latest`
4. Configure:
   - Service name: `django-blog-api`
   - Port: `8080`
   - Health check: `/api/v1/healthcheck/`
5. Add environment variables:
   ```
   SECRET_KEY=<your-generated-key>
   DEBUG=False
   DATABASE_URL=postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres
   SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
   SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E
   SUPABASE_BUCKET=leather_api_storage
   ALLOWED_HOSTS=*,.awsapprunner.com
   SECURE_PROXY_SSL_HEADER_ENABLED=True
   ```
6. Click **"Create & deploy"**

## ✅ Verify (30 seconds)
```bash
# Wait for status: RUNNING (5-6 minutes)
# Then test:
curl https://YOUR-SERVICE-URL.awsapprunner.com/api/v1/healthcheck/

# Expected: {"status": "healthy", "service": "django-blog-api"}
```

## 🎉 Done!
Your API is live at: `https://YOUR-SERVICE-URL.awsapprunner.com`

---

## 📋 Environment Variables (Copy-Paste Ready)

```bash
SECRET_KEY=<GENERATE_NEW_KEY>
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=*,.awsapprunner.com,.amazonaws.com
DATABASE_URL=postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E
SUPABASE_BUCKET=leather_api_storage
DJANGO_LOG_LEVEL=INFO
ANON_THROTTLE_RATE=100/hour
USER_THROTTLE_RATE=1000/hour
SECURE_PROXY_SSL_HEADER_ENABLED=True
```

---

## 🔧 Troubleshooting

**Health check failing?**
- Check CloudWatch logs
- Verify DATABASE_URL is correct
- Ensure port is 8080

**Database connection error?**
- Test connection: `psql $DATABASE_URL`
- Check Supabase pooler is enabled

**Need detailed guide?**
- See: `COMPLETE_DEPLOYMENT_GUIDE.md`

---

## 🔄 Update Deployment

```bash
# Make code changes, then:
./DEPLOY_TO_APPRUNNER.sh

# In App Runner console, click "Deploy"
```

---

**Cost:** ~$10-30/month | **Deploy time:** 5 minutes | **Uptime:** 99.9%
