# 🚀 Deploy to AWS App Runner - START HERE

## Step 1: Install AWS CLI

AWS CLI is not installed. Install it first:

```bash
# Install AWS CLI
brew install awscli

# Verify installation
aws --version
```

Expected output: `aws-cli/2.x.x`

---

## Step 2: Configure AWS Credentials

```bash
aws configure
```

You'll need:
- **AWS Access Key ID**: Get from AWS Console → Security Credentials
- **AWS Secret Access Key**: From same place
- **Default region**: `us-east-1`
- **Output format**: `json`

**How to get credentials:**
1. Go to: https://console.aws.amazon.com/
2. Click your name (top right) → Security credentials
3. Scroll to "Access keys" → Create access key
4. Choose "Command Line Interface (CLI)"
5. Copy both keys

---

## Step 3: Create ECR Repository

```bash
# Create repository for your Docker images
aws ecr create-repository \
    --repository-name django-blog-api \
    --region us-east-1

# Get the repository URI
ECR_URI=$(aws ecr describe-repositories \
    --repository-names django-blog-api \
    --region us-east-1 \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "ECR URI: $ECR_URI"
```

Save the ECR URI - you'll need it!

---

## Step 4: Push Docker Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin $ECR_URI

# Tag your image
docker tag django-blog-api:latest $ECR_URI:latest

# Push to ECR (takes 2-5 minutes)
docker push $ECR_URI:latest
```

---

## Step 5: Create App Runner Service

```bash
# Generate a strong secret key
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Create the service
aws apprunner create-service \
    --service-name django-blog-api \
    --region us-east-1 \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'$ECR_URI':latest",
            "ImageRepositoryType": "ECR",
            "ImageConfiguration": {
                "Port": "8000",
                "RuntimeEnvironmentVariables": {
                    "DEBUG": "False",
                    "SECRET_KEY": "'$SECRET_KEY'",
                    "ALLOWED_HOSTS": "*",
                    "DATABASE_URL": "postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres",
                    "SUPABASE_URL": "https://soccrpfkqjqjaoaturjb.supabase.co",
                    "SUPABASE_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E",
                    "SUPABASE_BUCKET": "leather_api_storage",
                    "REDIS_URL": ""
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
        "UnhealthyThreshold": 5
    }'
```

This takes 5-10 minutes to deploy.

---

## Step 6: Get Your Service URL

```bash
# Get service ARN
SERVICE_ARN=$(aws apprunner list-services \
    --region us-east-1 \
    --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].ServiceArn' \
    --output text)

# Get service URL
SERVICE_URL=$(aws apprunner describe-service \
    --service-arn $SERVICE_ARN \
    --region us-east-1 \
    --query 'Service.ServiceUrl' \
    --output text)

echo "🎉 Your API is live at: https://$SERVICE_URL"
```

---

## Step 7: Test Your Deployment

```bash
# Test health check
curl https://$SERVICE_URL/api/v1/healthcheck/

# Test API
curl https://$SERVICE_URL/api/v1/posts/

# Open in browser
open https://$SERVICE_URL/
```

---

## Step 8: Run Migrations

```bash
# Run migrations from local
export DATABASE_URL="postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser
```

---

## ✅ Done!

Your Django Blog API is now live on AWS App Runner!

**Access your API:**
- Landing Page: https://$SERVICE_URL/
- API Docs: https://$SERVICE_URL/api/v1/docs/
- Admin: https://$SERVICE_URL/admin/

**Monthly Cost**: ~$60-80

---

## 🔄 To Update Later

```bash
# Rebuild and push
docker build -t django-blog-api .
docker tag django-blog-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# App Runner auto-deploys!
```

---

## 📚 Full Documentation

See `AWS_APP_RUNNER_STEP_BY_STEP.md` for complete details.

---

## 🆘 Need Help?

**Check status:**
```bash
aws apprunner describe-service --service-arn $SERVICE_ARN --region us-east-1
```

**View logs:**
```bash
aws logs tail /aws/apprunner/django-blog-api/service --region us-east-1 --follow
```

**Delete service:**
```bash
aws apprunner delete-service --service-arn $SERVICE_ARN --region us-east-1
```
