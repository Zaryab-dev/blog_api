## AWS Deployment Guide - Django Blog API

Complete guide to deploy your Django Blog API on AWS using Docker.

---

## 🎯 Deployment Options

### Option 1: AWS ECS (Elastic Container Service) - Recommended
- Fully managed container orchestration
- Auto-scaling
- Load balancing
- Best for production

### Option 2: AWS EC2 with Docker
- More control
- Lower cost for small apps
- Manual scaling

### Option 3: AWS App Runner
- Simplest deployment
- Auto-scaling
- Higher cost

---

## 📋 Prerequisites

1. **AWS Account** with billing enabled
2. **AWS CLI** installed and configured
3. **Docker** installed locally
4. **PostgreSQL database** (AWS RDS recommended)
5. **Environment variables** ready

---

## 🚀 Option 1: AWS ECS Deployment (Recommended)

### Step 1: Create ECR Repository

```bash
# Login to AWS
aws configure

# Create ECR repository
aws ecr create-repository --repository-name django-blog-api --region us-east-1

# Get repository URI (save this)
aws ecr describe-repositories --repository-names django-blog-api --query 'repositories[0].repositoryUri' --output text
```

### Step 2: Build and Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <YOUR_ECR_URI>

# Build image
docker build -t django-blog-api .

# Tag image
docker tag django-blog-api:latest <YOUR_ECR_URI>:latest

# Push to ECR
docker push <YOUR_ECR_URI>:latest
```

### Step 3: Create RDS PostgreSQL Database

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name blog-db-subnet \
  --db-subnet-group-description "Blog API DB Subnet" \
  --subnet-ids subnet-xxx subnet-yyy

# Create PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier blog-api-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password <STRONG_PASSWORD> \
  --allocated-storage 20 \
  --db-subnet-group-name blog-db-subnet \
  --vpc-security-group-ids sg-xxx \
  --publicly-accessible
```

### Step 4: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name blog-api-cluster

# Create task definition (see task-definition.json below)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster blog-api-cluster \
  --service-name blog-api-service \
  --task-definition blog-api-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Step 5: Create Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name blog-api-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create target group
aws elbv2 create-target-group \
  --name blog-api-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /api/v1/healthcheck/

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn <ALB_ARN> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

---

## 🚀 Option 2: AWS EC2 Deployment

### Step 1: Launch EC2 Instance

```bash
# Launch Ubuntu instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name your-key-pair \
  --security-group-ids sg-xxx \
  --subnet-id subnet-xxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=blog-api}]'
```

### Step 2: SSH and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <YOUR_REPO_URL>
cd aws_blog_api

# Create .env file
nano .env
# Add all environment variables

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py createsuperuser
```

### Step 3: Configure Nginx (Optional)

```bash
# Install Nginx
sudo apt update
sudo apt install nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/blog-api

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/aws_blog_api/staticfiles/;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/blog-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🚀 Option 3: AWS App Runner

### Step 1: Create apprunner.yaml

```yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
      - python manage.py collectstatic --noinput
run:
  command: gunicorn --bind :8000 leather_api.wsgi:application
  network:
    port: 8000
  env:
    - name: DJANGO_SETTINGS_MODULE
      value: leather_api.settings
```

### Step 2: Deploy

```bash
# Create App Runner service
aws apprunner create-service \
  --service-name blog-api \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "<YOUR_REPO_URL>",
      "SourceCodeVersion": {"Type": "BRANCH", "Value": "main"},
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput",
          "StartCommand": "gunicorn --bind :8000 leather_api.wsgi:application",
          "Port": "8000"
        }
      }
    }
  }'
```

---

## 📋 Environment Variables

Create `.env.production` with:

```bash
# Django
DEBUG=False
SECRET_KEY=<GENERATE_STRONG_KEY>
ALLOWED_HOSTS=your-domain.com,*.amazonaws.com
SITE_URL=https://your-domain.com

# Database
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dbname

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-api-key
SUPABASE_BUCKET=your-bucket

# Redis
REDIS_URL=redis://redis-endpoint:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## 🔒 Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY (50+ characters)
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled (SSL certificate)
- [ ] Database password strong
- [ ] Security groups configured
- [ ] Environment variables in AWS Secrets Manager
- [ ] Backup strategy in place

---

## 📊 Post-Deployment

### Run Migrations

```bash
# ECS
aws ecs run-task --cluster blog-api-cluster --task-definition blog-api-task --overrides '{"containerOverrides":[{"name":"web","command":["python","manage.py","migrate"]}]}'

# EC2
docker-compose exec web python manage.py migrate
```

### Create Superuser

```bash
# EC2
docker-compose exec web python manage.py createsuperuser
```

### Test Deployment

```bash
# Health check
curl https://your-domain.com/api/v1/healthcheck/

# API test
curl https://your-domain.com/api/v1/posts/
```

---

## 🔄 CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

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
        run: aws ecr get-login-password | docker login --username AWS --password-stdin ${{ secrets.ECR_URI }}
      
      - name: Build and push
        run: |
          docker build -t blog-api .
          docker tag blog-api:latest ${{ secrets.ECR_URI }}:latest
          docker push ${{ secrets.ECR_URI }}:latest
      
      - name: Update ECS service
        run: aws ecs update-service --cluster blog-api-cluster --service blog-api-service --force-new-deployment
```

---

## 💰 Cost Estimation

### ECS (Recommended)
- **ECS Fargate:** ~$30-50/month (2 tasks)
- **RDS t3.micro:** ~$15/month
- **ALB:** ~$20/month
- **Total:** ~$65-85/month

### EC2
- **t3.small:** ~$15/month
- **RDS t3.micro:** ~$15/month
- **Total:** ~$30/month

### App Runner
- **App Runner:** ~$25-40/month
- **RDS:** ~$15/month
- **Total:** ~$40-55/month

---

## 🎯 Next Steps

1. Choose deployment option
2. Set up AWS resources
3. Configure environment variables
4. Deploy application
5. Run migrations
6. Test thoroughly
7. Set up monitoring
8. Configure backups

---

## 📞 Support

For issues:
1. Check CloudWatch logs
2. Verify environment variables
3. Test database connectivity
4. Review security groups

**Your Django Blog API is ready for AWS deployment!** 🚀
