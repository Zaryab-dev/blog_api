# 🚀 AWS App Runner Deployment - Step-by-Step Guide

Complete walkthrough to deploy your Django Blog API to AWS App Runner.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] AWS Account (with billing enabled)
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS CLI configured (`aws configure`)
- [ ] Docker running (`docker ps`)
- [ ] Your Django app working locally
- [ ] Database ready (using existing Supabase PostgreSQL)

---

## 🎯 STEP 1: Configure AWS CLI

### 1.1 Check if AWS CLI is installed
```bash
aws --version
```

**Expected output**: `aws-cli/2.x.x Python/3.x.x ...`

If not installed, install it:
```bash
# macOS
brew install awscli

# Or download from: https://aws.amazon.com/cli/
```

### 1.2 Configure AWS credentials
```bash
aws configure
```

**You'll be asked for:**
- AWS Access Key ID: `[Your access key]`
- AWS Secret Access Key: `[Your secret key]`
- Default region: `us-east-1` (recommended)
- Default output format: `json`

**Where to get credentials:**
1. Go to AWS Console: https://console.aws.amazon.com/
2. Click your name (top right) → Security credentials
3. Create access key → CLI
4. Copy Access Key ID and Secret Access Key

### 1.3 Verify configuration
```bash
aws sts get-caller-identity
```

**Expected output**: Your AWS account details

---

## 🎯 STEP 2: Create ECR Repository

ECR (Elastic Container Registry) stores your Docker image.

### 2.1 Create repository
```bash
aws ecr create-repository \
    --repository-name django-blog-api \
    --region us-east-1
```

**Expected output**: JSON with repository details

### 2.2 Get repository URI
```bash
ECR_URI=$(aws ecr describe-repositories \
    --repository-names django-blog-api \
    --region us-east-1 \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "Your ECR URI: $ECR_URI"
```

**Save this URI** - you'll need it later!

Example: `123456789012.dkr.ecr.us-east-1.amazonaws.com/django-blog-api`

---

## 🎯 STEP 3: Push Docker Image to ECR

### 3.1 Login to ECR
```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin $ECR_URI
```

**Expected output**: `Login Succeeded`

### 3.2 Tag your Docker image
```bash
docker tag django-blog-api:latest $ECR_URI:latest
```

### 3.3 Push image to ECR
```bash
docker push $ECR_URI:latest
```

**This will take 2-5 minutes** (uploading 576MB)

**Expected output**: 
```
latest: digest: sha256:... size: ...
```

### 3.4 Verify image in ECR
```bash
aws ecr describe-images \
    --repository-name django-blog-api \
    --region us-east-1
```

---

## 🎯 STEP 4: Prepare Environment Variables

Create a file with your production environment variables.

### 4.1 Create production env file
```bash
cat > .env.production << 'EOF'
DEBUG=False
SECRET_KEY=your-production-secret-key-min-50-characters-long
ALLOWED_HOSTS=*
SITE_URL=https://your-app-url.awsapprunner.com

# Database (your existing Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres

# Supabase Storage
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E
SUPABASE_BUCKET=leather_api_storage

# Redis (optional - can be empty for now)
REDIS_URL=

# Security
CSRF_TRUSTED_ORIGINS=https://your-app-url.awsapprunner.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
```

**Important**: Generate a strong SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🎯 STEP 5: Create App Runner Service

### 5.1 Create service configuration file
```bash
cat > apprunner-service.json << EOF
{
  "ServiceName": "django-blog-api",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "$ECR_URI:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "DEBUG": "False",
          "SECRET_KEY": "$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')",
          "ALLOWED_HOSTS": "*",
          "DATABASE_URL": "postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres",
          "SUPABASE_URL": "https://soccrpfkqjqjaoaturjb.supabase.co",
          "SUPABASE_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E",
          "SUPABASE_BUCKET": "leather_api_storage",
          "REDIS_URL": "",
          "SITE_URL": "https://placeholder.awsapprunner.com"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  },
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/api/v1/healthcheck/",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 5
  }
}
EOF
```

### 5.2 Create the App Runner service
```bash
aws apprunner create-service \
    --cli-input-json file://apprunner-service.json \
    --region us-east-1
```

**This will take 5-10 minutes** to provision.

**Expected output**: JSON with service details including `ServiceArn`

### 5.3 Save the Service ARN
```bash
SERVICE_ARN=$(aws apprunner list-services \
    --region us-east-1 \
    --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].ServiceArn' \
    --output text)

echo "Service ARN: $SERVICE_ARN"
```

---

## 🎯 STEP 6: Monitor Deployment

### 6.1 Check service status
```bash
aws apprunner describe-service \
    --service-arn $SERVICE_ARN \
    --region us-east-1 \
    --query 'Service.Status' \
    --output text
```

**Possible statuses:**
- `OPERATION_IN_PROGRESS` - Still deploying
- `RUNNING` - Successfully deployed!
- `CREATE_FAILED` - Something went wrong

### 6.2 Get service URL
```bash
SERVICE_URL=$(aws apprunner describe-service \
    --service-arn $SERVICE_ARN \
    --region us-east-1 \
    --query 'Service.ServiceUrl' \
    --output text)

echo "Your API is live at: https://$SERVICE_URL"
```

### 6.3 View logs (if needed)
```bash
# View recent logs
aws logs tail /aws/apprunner/django-blog-api/service \
    --region us-east-1 \
    --follow
```

---

## 🎯 STEP 7: Update Environment Variables

Now update SITE_URL and CSRF_TRUSTED_ORIGINS with your actual URL.

### 7.1 Update service with correct URL
```bash
aws apprunner update-service \
    --service-arn $SERVICE_ARN \
    --region us-east-1 \
    --source-configuration '{
        "ImageRepository": {
            "ImageConfiguration": {
                "RuntimeEnvironmentVariables": {
                    "SITE_URL": "https://'$SERVICE_URL'",
                    "CSRF_TRUSTED_ORIGINS": "https://'$SERVICE_URL'",
                    "ALLOWED_HOSTS": "'$SERVICE_URL',*"
                }
            }
        }
    }'
```

**This will trigger a new deployment** (~3-5 minutes)

---

## 🎯 STEP 8: Test Your Deployment

### 8.1 Test health check
```bash
curl https://$SERVICE_URL/api/v1/healthcheck/
```

**Expected**: `{"status":"healthy",...}`

### 8.2 Test landing page
```bash
curl https://$SERVICE_URL/
```

**Expected**: HTML content

### 8.3 Test API endpoints
```bash
# Get posts
curl https://$SERVICE_URL/api/v1/posts/

# Get categories
curl https://$SERVICE_URL/api/v1/categories/

# Get tags
curl https://$SERVICE_URL/api/v1/tags/
```

### 8.4 Open in browser
```bash
open https://$SERVICE_URL/
```

---

## 🎯 STEP 9: Run Database Migrations (Important!)

Your database needs to be migrated for the deployed app.

### 9.1 Create a one-time task to run migrations

Since App Runner doesn't have a built-in way to run one-time commands, you have two options:

**Option A: Run migrations from local (Recommended)**
```bash
# Set DATABASE_URL to your production database
export DATABASE_URL="postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

# Run migrations
python3 manage.py migrate

# Create superuser (optional)
python3 manage.py createsuperuser
```

**Option B: Temporarily add to entrypoint**

Edit `docker-entrypoint.sh` to add migrations:
```bash
#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    leather_api.wsgi:application
```

Then rebuild and redeploy:
```bash
docker build -t django-blog-api .
docker tag django-blog-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# App Runner will auto-deploy (if AutoDeploymentsEnabled)
```

---

## 🎯 STEP 10: Verify Everything Works

### 10.1 Complete test checklist
```bash
# Save your URL
echo "export API_URL=https://$SERVICE_URL" >> ~/.bashrc
source ~/.bashrc

# Test all endpoints
curl $API_URL/api/v1/healthcheck/
curl $API_URL/api/v1/posts/
curl $API_URL/api/v1/categories/
curl $API_URL/api/v1/tags/
curl $API_URL/api/v1/authors/
curl $API_URL/admin/
```

### 10.2 Check admin panel
```bash
open https://$SERVICE_URL/admin/
```

Login with your superuser credentials.

---

## 🎯 OPTIONAL: Custom Domain Setup

### 11.1 Associate custom domain
```bash
aws apprunner associate-custom-domain \
    --service-arn $SERVICE_ARN \
    --domain-name api.yourdomain.com \
    --region us-east-1
```

### 11.2 Get DNS records
```bash
aws apprunner describe-custom-domains \
    --service-arn $SERVICE_ARN \
    --region us-east-1
```

Add the provided DNS records to your domain registrar.

---

## 📊 Cost Monitoring

### Check current costs
```bash
# View App Runner costs
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --filter file://cost-filter.json
```

**Expected monthly cost**: ~$60-80
- App Runner: ~$46/month (1 vCPU, 2GB)
- Data transfer: ~$1-5/month
- ECR storage: ~$0.10/month

---

## 🔄 Future Updates

### To update your app:

```bash
# 1. Make code changes locally
# 2. Rebuild Docker image
docker build -t django-blog-api .

# 3. Push to ECR
docker tag django-blog-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# 4. App Runner auto-deploys (if enabled)
# Or manually trigger:
aws apprunner start-deployment \
    --service-arn $SERVICE_ARN \
    --region us-east-1
```

---

## 🆘 Troubleshooting

### Service won't start
```bash
# Check service status
aws apprunner describe-service --service-arn $SERVICE_ARN

# View logs
aws logs tail /aws/apprunner/django-blog-api/service --follow
```

### Health check failing
```bash
# Test locally first
docker run -p 8000:8000 --env-file .env django-blog-api
curl http://localhost:8000/api/v1/healthcheck/
```

### Database connection issues
```bash
# Verify DATABASE_URL is correct
# Check if database allows connections from AWS
```

---

## ✅ Deployment Checklist

- [ ] AWS CLI configured
- [ ] ECR repository created
- [ ] Docker image pushed to ECR
- [ ] App Runner service created
- [ ] Service is RUNNING
- [ ] Health check passing
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Superuser created
- [ ] All endpoints tested
- [ ] Admin panel accessible
- [ ] Custom domain configured (optional)

---

## 🎉 Success!

Your Django Blog API is now live on AWS App Runner!

**Your API URL**: https://$SERVICE_URL
**Admin Panel**: https://$SERVICE_URL/admin/
**API Docs**: https://$SERVICE_URL/api/v1/docs/

**Next steps:**
1. Set up monitoring and alerts
2. Configure custom domain
3. Set up CI/CD pipeline
4. Enable auto-scaling
5. Set up backups

---

## 📞 Quick Reference

```bash
# Service ARN
echo $SERVICE_ARN

# Service URL
echo $SERVICE_URL

# View logs
aws logs tail /aws/apprunner/django-blog-api/service --follow

# Check status
aws apprunner describe-service --service-arn $SERVICE_ARN

# Update service
aws apprunner update-service --service-arn $SERVICE_ARN ...

# Delete service (careful!)
aws apprunner delete-service --service-arn $SERVICE_ARN
```

**Congratulations! You're live on AWS!** 🚀
