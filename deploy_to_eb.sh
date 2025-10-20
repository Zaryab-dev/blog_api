#!/bin/bash
set -e

echo "🚀 AWS Elastic Beanstalk Deployment Script"
echo "=========================================="

# Load environment variables
if [ -f .env ]; then
    source .env
    echo "✅ Loaded .env file"
else
    echo "❌ .env file not found"
    exit 1
fi

# Check if EB is initialized
if [ ! -d .elasticbeanstalk ]; then
    echo "📦 Initializing Elastic Beanstalk..."
    eb init -p python-3.11 django-blog-api --region us-east-1
fi

# Check if environment exists
ENV_EXISTS=$(eb list 2>/dev/null | grep -c "django-blog-api-prod" || echo "0")

if [ "$ENV_EXISTS" -eq "0" ]; then
    echo "🌍 Creating new environment..."
    eb create django-blog-api-prod \
        --instance-type t3.small \
        --envvars \
            DEBUG=False,\
            SECRET_KEY="${SECRET_KEY}",\
            DATABASE_URL="${DATABASE_URL}",\
            ALLOWED_HOSTS=".elasticbeanstalk.com",\
            SUPABASE_URL="${SUPABASE_URL}",\
            SUPABASE_API_KEY="${SUPABASE_API_KEY}",\
            SUPABASE_BUCKET="${SUPABASE_BUCKET}"
else
    echo "🔄 Deploying to existing environment..."
    eb deploy
fi

echo ""
echo "✅ Deployment complete!"
echo "🌐 Opening application..."
eb open
