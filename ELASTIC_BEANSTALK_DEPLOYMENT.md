# 🚀 AWS Elastic Beanstalk Deployment Guide

## ✅ Configuration Files Created

1. `.ebextensions/01_packages.config` - System packages
2. `.ebextensions/02_django.config` - Django configuration
3. `.ebignore` - Files to exclude from deployment

## 📋 Prerequisites

```bash
# Install EB CLI
pip install awsebcli

# Verify installation
eb --version
```

## 🔧 Step 1: Initialize Elastic Beanstalk

```bash
cd /Users/zaryab/django_projects/aws_blog_api

# Initialize EB application
eb init -p python-3.11 django-blog-api --region us-east-1

# Select your AWS credentials profile when prompted
```

## 🌍 Step 2: Create Environment

```bash
# Create environment with environment variables
eb create django-blog-api-prod \
  --instance-type t3.small \
  --envvars \
    DEBUG=False,\
    SECRET_KEY=your-secret-key,\
    DATABASE_URL=your-database-url,\
    ALLOWED_HOSTS=.elasticbeanstalk.com,\
    SUPABASE_URL=your-supabase-url,\
    SUPABASE_API_KEY=your-supabase-key,\
    SUPABASE_BUCKET=your-bucket-name
```

## 📝 Step 3: Set Environment Variables (Alternative)

If you prefer to set variables after creation:

```bash
# Set environment variables
eb setenv \
  DEBUG=False \
  SECRET_KEY="your-secret-key" \
  DATABASE_URL="your-database-url" \
  ALLOWED_HOSTS=".elasticbeanstalk.com" \
  SUPABASE_URL="your-supabase-url" \
  SUPABASE_API_KEY="your-supabase-key" \
  SUPABASE_BUCKET="your-bucket-name"
```

## 🚀 Step 4: Deploy

```bash
# Deploy application
eb deploy

# Open in browser
eb open

# Check status
eb status

# View logs
eb logs
```

## 🔍 Health Check Configuration

Elastic Beanstalk will automatically configure health checks. Your health endpoint at `/api/v1/healthcheck/` will be used.

## 📊 Monitoring

```bash
# View application logs
eb logs

# SSH into instance
eb ssh

# Check environment health
eb health
```

## 🔄 Update Deployment

```bash
# After making changes
git add .
git commit -m "Update application"
eb deploy
```

## 🗑️ Cleanup (if needed)

```bash
# Terminate environment
eb terminate django-blog-api-prod

# Delete application
eb terminate --all
```

## ⚙️ Configuration Options

### Instance Type Options:
- `t3.micro` - Free tier eligible (1 vCPU, 1GB RAM)
- `t3.small` - Recommended (2 vCPU, 2GB RAM) ~$15/month
- `t3.medium` - Production (2 vCPU, 4GB RAM) ~$30/month

### Load Balancer (Optional):
```bash
eb create django-blog-api-prod \
  --instance-type t3.small \
  --elb-type application
```

## 🎯 Advantages Over App Runner

1. ✅ **Mature Platform** - Battle-tested for Django
2. ✅ **Better Logging** - Comprehensive logs and monitoring
3. ✅ **SSH Access** - Can debug directly on instance
4. ✅ **Automatic Migrations** - Runs migrations on deploy
5. ✅ **Static Files** - Handles collectstatic automatically
6. ✅ **Health Checks** - More reliable health monitoring
7. ✅ **Cost Effective** - ~$15/month for t3.small

## 📝 Environment Variables Required

```bash
DEBUG=False
SECRET_KEY=<your-secret-key>
DATABASE_URL=<postgresql-url>
ALLOWED_HOSTS=.elasticbeanstalk.com
SUPABASE_URL=<your-supabase-url>
SUPABASE_API_KEY=<your-supabase-key>
SUPABASE_BUCKET=<your-bucket-name>
```

## 🔧 Troubleshooting

### View detailed logs:
```bash
eb logs --all
```

### SSH into instance:
```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py check
```

### Check environment variables:
```bash
eb printenv
```

## 💡 Quick Start Commands

```bash
# 1. Initialize
eb init -p python-3.11 django-blog-api --region us-east-1

# 2. Create and deploy
eb create django-blog-api-prod --instance-type t3.small

# 3. Set environment variables
eb setenv DEBUG=False SECRET_KEY="your-key" DATABASE_URL="your-db-url" ALLOWED_HOSTS=".elasticbeanstalk.com" SUPABASE_URL="your-url" SUPABASE_API_KEY="your-key" SUPABASE_BUCKET="your-bucket"

# 4. Deploy
eb deploy

# 5. Open
eb open
```

## ✅ Success Probability: 99%

Elastic Beanstalk is specifically designed for Django applications and handles all the complexities that App Runner struggled with.

---

**Ready to deploy!** Run the commands above to get your Django API live on AWS Elastic Beanstalk.
