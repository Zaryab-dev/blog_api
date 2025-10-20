#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=816709078703
export SERVICE_NAME=django-blog-api-v3
export ECR_IMAGE=816709078703.dkr.ecr.us-east-1.amazonaws.com/django-blog-api:v3

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Deploy to AWS App Runner - Django Blog API        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo "Create .env file with required variables"
    exit 1
fi

# Load environment variables
source .env

# Validate required variables
if [ -z "$SECRET_KEY" ] || [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}✗ Missing required environment variables!${NC}"
    echo "Required: SECRET_KEY, DATABASE_URL"
    exit 1
fi

echo "Configuration:"
echo "  Service Name: $SERVICE_NAME"
echo "  ECR Image:    $ECR_IMAGE"
echo "  Region:       $AWS_REGION"
echo ""

# Step 1: Check IAM role
echo -e "${YELLOW}[1/3] Checking IAM role for ECR access...${NC}"
if aws iam get-role --role-name AppRunnerECRAccessRole --region $AWS_REGION >/dev/null 2>&1; then
    echo -e "${GREEN}✓ IAM role exists${NC}"
else
    echo "Creating IAM role..."
    
    cat > /tmp/trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    aws iam create-role \
      --role-name AppRunnerECRAccessRole \
      --assume-role-policy-document file:///tmp/trust-policy.json \
      --region $AWS_REGION
    
    aws iam attach-role-policy \
      --role-name AppRunnerECRAccessRole \
      --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess \
      --region $AWS_REGION
    
    echo -e "${GREEN}✓ IAM role created${NC}"
    echo "Waiting 10 seconds for IAM role to propagate..."
    sleep 10
fi
echo ""

# Step 2: Check if service already exists
echo -e "${YELLOW}[2/3] Checking if service exists...${NC}"
SERVICE_ARN=$(aws apprunner list-services --region $AWS_REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text 2>/dev/null || echo "")

if [ -n "$SERVICE_ARN" ]; then
    echo -e "${YELLOW}⚠ Service '$SERVICE_NAME' already exists${NC}"
    echo "Service ARN: $SERVICE_ARN"
    echo ""
    read -p "Do you want to update the existing service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Updating service..."
        aws apprunner update-service \
          --service-arn "$SERVICE_ARN" \
          --source-configuration "{
            \"ImageRepository\": {
              \"ImageIdentifier\": \"$ECR_IMAGE\",
              \"ImageConfiguration\": {
                \"Port\": \"8080\",
                \"RuntimeEnvironmentVariables\": {
                  \"PORT\": \"8080\",
                  \"DEBUG\": \"False\",
                  \"DJANGO_SETTINGS_MODULE\": \"leather_api.settings\",
                  \"ALLOWED_HOSTS\": \"*\",
                  \"SECRET_KEY\": \"$SECRET_KEY\",
                  \"DATABASE_URL\": \"$DATABASE_URL\",
                  \"SUPABASE_URL\": \"$SUPABASE_URL\",
                  \"SUPABASE_API_KEY\": \"$SUPABASE_API_KEY\",
                  \"SUPABASE_BUCKET\": \"$SUPABASE_BUCKET\"
                }
              },
              \"ImageRepositoryType\": \"ECR\"
            }
          }" \
          --region $AWS_REGION
        echo -e "${GREEN}✓ Service update initiated${NC}"
    else
        echo "Deployment cancelled"
        exit 0
    fi
else
    # Step 3: Create new service
    echo -e "${YELLOW}[3/3] Creating App Runner service...${NC}"
    
    aws apprunner create-service \
      --service-name "$SERVICE_NAME" \
      --source-configuration "{
        \"ImageRepository\": {
          \"ImageIdentifier\": \"$ECR_IMAGE\",
          \"ImageConfiguration\": {
            \"Port\": \"8080\",
            \"RuntimeEnvironmentVariables\": {
              \"PORT\": \"8080\",
              \"DEBUG\": \"False\",
              \"DJANGO_SETTINGS_MODULE\": \"leather_api.settings\",
              \"ALLOWED_HOSTS\": \"*\",
              \"SECRET_KEY\": \"$SECRET_KEY\",
              \"DATABASE_URL\": \"$DATABASE_URL\",
              \"SUPABASE_URL\": \"$SUPABASE_URL\",
              \"SUPABASE_API_KEY\": \"$SUPABASE_API_KEY\",
              \"SUPABASE_BUCKET\": \"$SUPABASE_BUCKET\"
            }
          },
          \"ImageRepositoryType\": \"ECR\"
        },
        \"AuthenticationConfiguration\": {
          \"AccessRoleArn\": \"arn:aws:iam::$AWS_ACCOUNT_ID:role/AppRunnerECRAccessRole\"
        }
      }" \
      --instance-configuration "{
        \"Cpu\": \"1 vCPU\",
        \"Memory\": \"2 GB\"
      }" \
      --health-check-configuration "{
        \"Protocol\": \"HTTP\",
        \"Path\": \"/api/v1/healthcheck/\",
        \"Interval\": 10,
        \"Timeout\": 5,
        \"HealthyThreshold\": 1,
        \"UnhealthyThreshold\": 5
      }" \
      --region $AWS_REGION > /tmp/apprunner-output.json
    
    SERVICE_ARN=$(cat /tmp/apprunner-output.json | grep -o '"ServiceArn": "[^"]*"' | cut -d'"' -f4)
    SERVICE_URL=$(cat /tmp/apprunner-output.json | grep -o '"ServiceUrl": "[^"]*"' | cut -d'"' -f4)
    
    echo -e "${GREEN}✓ Service created${NC}"
    echo ""
    echo "Service ARN: $SERVICE_ARN"
    echo "Service URL: $SERVICE_URL"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ✅ DEPLOYMENT INITIATED SUCCESSFULLY! ✅            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Monitor deployment:"
echo "  ./monitor_deployment.sh"
echo ""
echo "Or manually:"
echo "  aws apprunner list-services --region $AWS_REGION"
echo ""
