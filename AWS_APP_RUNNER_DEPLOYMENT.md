# AWS App Runner Deployment Guide

Complete guide to deploy your Django Blog API on AWS App Runner.

---

## 🎯 What is AWS App Runner?

AWS App Runner is a fully managed service that makes it easy to deploy containerized web applications and APIs at scale. It automatically handles:
- Load balancing
- Auto-scaling
- Health checks
- HTTPS certificates
- Continuous deployment

---

## 📋 Prerequisites

1. **AWS Account** with billing enabled
2. **AWS CLI** installed and configured
3. **Docker** installed locally
4. **GitHub/GitLab repository** (optional, for auto-deploy)
5. **PostgreSQL database** (AWS RDS recommended)
6. **Environment variables** ready

---

## 🚀 Deployment Methods

### Method 1: Deploy from ECR (Recommended)

#### Step 1: Create ECR Repository

```bash
# Create repository
aws ecr create-repository \
    --repository-name django-blog-api \
    --region us-east-1

# Get repository URI
ECR_URI=$(aws ecr describe-repositories \
    --repository-names django-blog-api \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "ECR URI: $ECR_URI"
```

#### Step 2: Build and Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin $ECR_URI

# Build image
docker build -t django-blog-api .

# Tag image
docker tag django-blog-api:latest $ECR_URI:latest

# Push to ECR
docker push $ECR_URI:latest
```

#### Step 3: Create App Runner Service

```bash
# Create service from ECR
aws apprunner create-service \
    --service-name django-blog-api \
    --source-configuration '{
        "ImageRepository": {
            "ImageIdentifier": "'$ECR_URI':latest",
            "ImageRepositoryType": "ECR",
            "ImageConfiguration": {
                "Port": "8000",
                "RuntimeEnvironmentVariables": {
                    "DEBUG": "False",
                    "ALLOWED_HOSTS": "*",
                    "DATABASE_URL": "postgresql://user:pass@host:5432/db"
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

---

### Method 2: Deploy from GitHub (Auto-Deploy)

#### Step 1: Create apprunner.yaml

Already created in your project root. Content:

```yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install --no-cache-dir -r requirements.txt
      - python manage.py collectstatic --noinput
run:
  runtime-version: python3.11
  command: gunicorn --bind 0.0.0.0:8000 --workers 3 --threads 2 leather_api.wsgi:application
  network:
    port: 8000
  env:
    - name: PYTHONUNBUFFERED
      value: "1"
```

#### Step 2: Connect GitHub and Deploy

```bash
# Create GitHub connection (one-time setup)
aws apprunner create-connection \
    --connection-name github-connection \
    --provider-type GITHUB

# Get connection ARN
CONNECTION_ARN=$(aws apprunner list-connections \
    --query 'ConnectionSummaryList[0].ConnectionArn' \
    --output text)

# Create service from GitHub
aws apprunner create-service \
    --service-name django-blog-api \
    --source-configuration '{
        "CodeRepository": {
            "RepositoryUrl": "https://github.com/yourusername/aws_blog_api",
            "SourceCodeVersion": {
                "Type": "BRANCH",
                "Value": "main"
            },
            "CodeConfiguration": {
                "ConfigurationSource": "REPOSITORY"
            }
        },
        "AutoDeploymentsEnabled": true,
        "AuthenticationConfiguration": {
            "ConnectionArn": "'$CONNECTION_ARN'"
        }
    }' \
    --instance-configuration '{
        "Cpu": "1 vCPU",
        "Memory": "2 GB"
    }'
```

---

## 🔐 Environment Variables Setup

### Using AWS Secrets Manager (Recommended)

```bash
# Create secret
aws secretsmanager create-secret \
    --name django-blog-api-secrets \
    --secret-string '{
        "SECRET_KEY": "your-secret-key-here",
        "DATABASE_URL": "postgresql://user:pass@host:5432/db",
        "SUPABASE_URL": "https://xxx.supabase.co",
        "SUPABASE_API_KEY": "your-key",
        "SUPABASE_BUCKET": "your-bucket",
        "REDIS_URL": "redis://host:6379/0"
    }'

# Get secret ARN
SECRET_ARN=$(aws secretsmanager describe-secret \
    --secret-id django-blog-api-secrets \
    --query 'ARN' \
    --output text)
```

### Update App Runner Service with Secrets

```bash
aws apprunner update-service \
    --service-arn <YOUR_SERVICE_ARN> \
    --source-configuration '{
        "ImageRepository": {
            "ImageConfiguration": {
                "RuntimeEnvironmentSecrets": {
                    "SECRET_KEY": "'$SECRET_ARN':SECRET_KEY::",
                    "DATABASE_URL": "'$SECRET_ARN':DATABASE_URL::",
                    "SUPABASE_URL": "'$SECRET_ARN':SUPABASE_URL::",
                    "SUPABASE_API_KEY": "'$SECRET_ARN':SUPABASE_API_KEY::",
                    "SUPABASE_BUCKET": "'$SECRET_ARN':SUPABASE_BUCKET::"
                }
            }
        }
    }'
```

---

## 🗄️ Database Setup (AWS RDS)

### Create PostgreSQL Database

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name blog-db-subnet \
    --db-subnet-group-description "Blog API DB" \
    --subnet-ids subnet-xxx subnet-yyy

# Create PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier blog-api-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username admin \
    --master-user-password <STRONG_PASSWORD> \
    --allocated-storage 20 \
    --db-subnet-group-name blog-db-subnet \
    --vpc-security-group-ids sg-xxx \
    --publicly-accessible

# Get endpoint
aws rds describe-db-instances \
    --db-instance-identifier blog-api-db \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text
```

### Run Migrations

```bash
# SSH into a temporary EC2 or use local connection
export DATABASE_URL="postgresql://admin:password@endpoint:5432/postgres"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## 🔧 Local Testing

### Test Docker Image Locally

```bash
# Build image
docker build -t django-blog-api .

# Run with environment variables
docker run -p 8000:8000 \
    -e DEBUG=False \
    -e SECRET_KEY=test-key \
    -e DATABASE_URL=postgresql://user:pass@host:5432/db \
    -e SUPABASE_URL=https://xxx.supabase.co \
    -e SUPABASE_API_KEY=your-key \
    -e SUPABASE_BUCKET=your-bucket \
    -e ALLOWED_HOSTS=localhost,127.0.0.1 \
    django-blog-api

# Test endpoints
curl http://localhost:8000/api/v1/healthcheck/
curl http://localhost:8000/api/v1/posts/
```

### Test with Docker Compose

```bash
# Start all services
docker-compose up

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Test
curl http://localhost:8000/
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Get service ARN
SERVICE_ARN=$(aws apprunner list-services \
    --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].ServiceArn' \
    --output text)

# View logs (requires CloudWatch)
aws logs tail /aws/apprunner/django-blog-api --follow
```

### Health Check

```bash
# Get service URL
SERVICE_URL=$(aws apprunner describe-service \
    --service-arn $SERVICE_ARN \
    --query 'Service.ServiceUrl' \
    --output text)

# Test health
curl https://$SERVICE_URL/api/v1/healthcheck/
```

---

## 💰 Cost Estimation

### App Runner Pricing (us-east-1)

**Compute:**
- 1 vCPU, 2 GB RAM: ~$0.064/hour = ~$46/month
- Auto-scaling: Pay only for active instances

**Additional Costs:**
- RDS t3.micro: ~$15/month
- Data transfer: ~$0.09/GB
- ECR storage: ~$0.10/GB/month

**Total Estimated Cost:** ~$60-80/month

---

## 🔄 CI/CD with GitHub Actions

Create `.github/workflows/deploy-apprunner.yml`:

```yaml
name: Deploy to App Runner

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin ${{ secrets.ECR_URI }}
      
      - name: Build and push
        run: |
          docker build -t django-blog-api .
          docker tag django-blog-api:latest ${{ secrets.ECR_URI }}:latest
          docker push ${{ secrets.ECR_URI }}:latest
      
      - name: Deploy to App Runner
        run: |
          aws apprunner start-deployment --service-arn ${{ secrets.APP_RUNNER_SERVICE_ARN }}
```

---

## ✅ Post-Deployment Checklist

- [ ] Service is running and healthy
- [ ] Database migrations completed
- [ ] Superuser created
- [ ] Environment variables configured
- [ ] HTTPS working (automatic with App Runner)
- [ ] Custom domain configured (optional)
- [ ] Health check endpoint responding
- [ ] API endpoints accessible
- [ ] Static files loading correctly
- [ ] Logs visible in CloudWatch
- [ ] Auto-scaling configured
- [ ] Backup strategy in place

---

## 🌐 Custom Domain Setup

```bash
# Create custom domain association
aws apprunner associate-custom-domain \
    --service-arn $SERVICE_ARN \
    --domain-name api.yourdomain.com

# Get DNS records to configure
aws apprunner describe-custom-domains \
    --service-arn $SERVICE_ARN
```

Add the provided DNS records to your domain registrar.

---

## 🔒 Security Best Practices

1. **Use Secrets Manager** for sensitive data
2. **Enable VPC connector** for private RDS access
3. **Configure WAF** for DDoS protection
4. **Set up CloudWatch alarms** for monitoring
5. **Enable auto-scaling** based on traffic
6. **Use HTTPS only** (automatic with App Runner)
7. **Rotate secrets regularly**
8. **Enable CloudTrail** for audit logs

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check service status
aws apprunner describe-service --service-arn $SERVICE_ARN

# View logs
aws logs tail /aws/apprunner/django-blog-api --follow

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port mismatch (must be 8000)
# - Health check failing
```

### Database Connection Issues

```bash
# Test connection from local
psql $DATABASE_URL

# Check security groups
# - App Runner needs outbound access to RDS
# - RDS security group must allow inbound from App Runner
```

### Static Files Not Loading

```bash
# Verify collectstatic ran
docker run django-blog-api ls -la /app/staticfiles/

# Check WhiteNoise configuration in settings.py
# Ensure STATICFILES_STORAGE is set correctly
```

---

## 📚 Additional Resources

- [App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [App Runner Pricing](https://aws.amazon.com/apprunner/pricing/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

## ✨ Summary

Your Django Blog API is now deployed on AWS App Runner with:
- ✅ Automatic HTTPS
- ✅ Auto-scaling
- ✅ Health monitoring
- ✅ Continuous deployment
- ✅ Production-ready configuration
- ✅ Optimized Docker image
- ✅ Static files served via WhiteNoise

**Deployment time:** ~10-15 minutes
**Monthly cost:** ~$60-80
**Maintenance:** Minimal (fully managed)
