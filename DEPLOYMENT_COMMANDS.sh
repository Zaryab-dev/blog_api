#!/bin/bash
# Quick deployment commands for Django Blog API

# ============================================
# LOCAL TESTING
# ============================================

# Test with Docker Compose
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
curl http://localhost:8000/
docker-compose down

# Test single container
docker build -t django-blog-api .
docker run -p 8000:8000 --env-file .env django-blog-api

# ============================================
# AWS APP RUNNER - ECR METHOD (RECOMMENDED)
# ============================================

# 1. Create ECR repository
aws ecr create-repository --repository-name django-blog-api --region us-east-1

# 2. Get ECR URI
ECR_URI=$(aws ecr describe-repositories --repository-names django-blog-api --query 'repositories[0].repositoryUri' --output text --region us-east-1)
echo "ECR URI: $ECR_URI"

# 3. Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URI

# 4. Build and push
docker build -t django-blog-api .
docker tag django-blog-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# 5. Create App Runner service
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
                    "SECRET_KEY": "your-secret-key",
                    "ALLOWED_HOSTS": "*",
                    "DATABASE_URL": "postgresql://user:pass@host:5432/db",
                    "SUPABASE_URL": "https://xxx.supabase.co",
                    "SUPABASE_API_KEY": "your-key",
                    "SUPABASE_BUCKET": "your-bucket"
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

# 6. Get service URL
SERVICE_ARN=$(aws apprunner list-services --region us-east-1 --query 'ServiceSummaryList[?ServiceName==`django-blog-api`].ServiceArn' --output text)
SERVICE_URL=$(aws apprunner describe-service --service-arn $SERVICE_ARN --region us-east-1 --query 'Service.ServiceUrl' --output text)
echo "Service URL: https://$SERVICE_URL"

# ============================================
# AWS APP RUNNER - GITHUB METHOD
# ============================================

# 1. Create GitHub connection
aws apprunner create-connection \
    --connection-name github-connection \
    --provider-type GITHUB \
    --region us-east-1

# 2. Get connection ARN (after completing OAuth flow)
CONNECTION_ARN=$(aws apprunner list-connections --region us-east-1 --query 'ConnectionSummaryList[0].ConnectionArn' --output text)

# 3. Create service from GitHub
aws apprunner create-service \
    --service-name django-blog-api \
    --region us-east-1 \
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

# ============================================
# DATABASE SETUP (AWS RDS)
# ============================================

# Create PostgreSQL database
aws rds create-db-instance \
    --db-instance-identifier blog-api-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username admin \
    --master-user-password YourStrongPassword123! \
    --allocated-storage 20 \
    --publicly-accessible \
    --region us-east-1

# Get database endpoint
DB_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier blog-api-db --query 'DBInstances[0].Endpoint.Address' --output text --region us-east-1)
echo "Database endpoint: $DB_ENDPOINT"

# ============================================
# SECRETS MANAGER (RECOMMENDED)
# ============================================

# Create secret
aws secretsmanager create-secret \
    --name django-blog-api-secrets \
    --region us-east-1 \
    --secret-string '{
        "SECRET_KEY": "your-secret-key-here",
        "DATABASE_URL": "postgresql://admin:password@'$DB_ENDPOINT':5432/postgres",
        "SUPABASE_URL": "https://xxx.supabase.co",
        "SUPABASE_API_KEY": "your-key",
        "SUPABASE_BUCKET": "your-bucket"
    }'

# ============================================
# MONITORING & LOGS
# ============================================

# View logs
aws logs tail /aws/apprunner/django-blog-api --follow --region us-east-1

# Check service status
aws apprunner describe-service --service-arn $SERVICE_ARN --region us-east-1

# Test health
curl https://$SERVICE_URL/api/v1/healthcheck/

# ============================================
# UPDATES & REDEPLOYMENT
# ============================================

# Update image and redeploy
docker build -t django-blog-api .
docker tag django-blog-api:latest $ECR_URI:latest
docker push $ECR_URI:latest
aws apprunner start-deployment --service-arn $SERVICE_ARN --region us-east-1

# ============================================
# CLEANUP
# ============================================

# Delete App Runner service
aws apprunner delete-service --service-arn $SERVICE_ARN --region us-east-1

# Delete RDS instance
aws rds delete-db-instance --db-instance-identifier blog-api-db --skip-final-snapshot --region us-east-1

# Delete ECR repository
aws ecr delete-repository --repository-name django-blog-api --force --region us-east-1

# Delete secret
aws secretsmanager delete-secret --secret-id django-blog-api-secrets --force-delete-without-recovery --region us-east-1
