#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

export AWS_REGION=us-east-1
export SERVICE_NAME=django-blog-api-v3

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Troubleshoot App Runner Deployment                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get service ARN
SERVICE_ARN=$(aws apprunner list-services --region $AWS_REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text 2>/dev/null)

if [ -z "$SERVICE_ARN" ]; then
    echo -e "${RED}✗ Service '$SERVICE_NAME' not found!${NC}"
    echo ""
    echo "Available services:"
    aws apprunner list-services --region $AWS_REGION --query "ServiceSummaryList[*].[ServiceName,Status]" --output table
    exit 1
fi

echo "Service: $SERVICE_NAME"
echo "ARN: $SERVICE_ARN"
echo ""

# Check 1: Service Status
echo -e "${YELLOW}[1/6] Checking service status...${NC}"
STATUS=$(aws apprunner describe-service --service-arn "$SERVICE_ARN" --region $AWS_REGION --query 'Service.Status' --output text)
echo "Status: $STATUS"

case $STATUS in
    "RUNNING")
        echo -e "${GREEN}✓ Service is running${NC}"
        ;;
    "OPERATION_IN_PROGRESS")
        echo -e "${YELLOW}⚠ Service is deploying (wait 5-10 minutes)${NC}"
        ;;
    "CREATE_FAILED"|"UPDATE_FAILED")
        echo -e "${RED}✗ Service deployment failed!${NC}"
        ;;
    *)
        echo -e "${YELLOW}⚠ Unexpected status: $STATUS${NC}"
        ;;
esac
echo ""

# Check 2: Recent Operations
echo -e "${YELLOW}[2/6] Checking recent operations...${NC}"
aws apprunner list-operations \
  --service-arn "$SERVICE_ARN" \
  --region $AWS_REGION \
  --max-results 3 \
  --query 'OperationSummaryList[*].[Type,Status,StartedAt]' \
  --output table
echo ""

# Check 3: Health Check Configuration
echo -e "${YELLOW}[3/6] Checking health check configuration...${NC}"
HEALTH_PATH=$(aws apprunner describe-service --service-arn "$SERVICE_ARN" --region $AWS_REGION --query 'Service.HealthCheckConfiguration.Path' --output text)
echo "Health check path: $HEALTH_PATH"
if [ "$HEALTH_PATH" = "/api/v1/healthcheck/" ]; then
    echo -e "${GREEN}✓ Health check path is correct${NC}"
else
    echo -e "${RED}✗ Health check path is wrong! Should be: /api/v1/healthcheck/${NC}"
fi
echo ""

# Check 4: Environment Variables
echo -e "${YELLOW}[4/6] Checking environment variables...${NC}"
ENV_VARS=$(aws apprunner describe-service --service-arn "$SERVICE_ARN" --region $AWS_REGION --query 'Service.SourceConfiguration.ImageRepository.ImageConfiguration.RuntimeEnvironmentVariables' --output json)

for VAR in "SECRET_KEY" "DATABASE_URL" "ALLOWED_HOSTS" "DEBUG"; do
    if echo "$ENV_VARS" | grep -q "\"$VAR\""; then
        echo -e "${GREEN}✓ $VAR is set${NC}"
    else
        echo -e "${RED}✗ $VAR is missing!${NC}"
    fi
done
echo ""

# Check 5: ECR Image
echo -e "${YELLOW}[5/6] Checking ECR image...${NC}"
IMAGE_ID=$(aws apprunner describe-service --service-arn "$SERVICE_ARN" --region $AWS_REGION --query 'Service.SourceConfiguration.ImageRepository.ImageIdentifier' --output text)
echo "Image: $IMAGE_ID"

IMAGE_TAG=$(echo "$IMAGE_ID" | grep -o ":[^:]*$" | cut -d: -f2)
if aws ecr describe-images --repository-name django-blog-api --image-ids imageTag="$IMAGE_TAG" --region $AWS_REGION >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Image exists in ECR${NC}"
else
    echo -e "${RED}✗ Image not found in ECR!${NC}"
fi
echo ""

# Check 6: CloudWatch Logs
echo -e "${YELLOW}[6/6] Recent CloudWatch logs...${NC}"
echo "Last 20 log entries:"
aws logs tail /aws/apprunner/$SERVICE_NAME --region $AWS_REGION --since 10m 2>/dev/null | tail -20 || echo "No logs available yet"
echo ""

# Recommendations
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    RECOMMENDATIONS                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ "$STATUS" = "CREATE_FAILED" ] || [ "$STATUS" = "UPDATE_FAILED" ]; then
    echo "Service deployment failed. Common fixes:"
    echo "  1. Check health check path is /api/v1/healthcheck/"
    echo "  2. Verify all environment variables are set"
    echo "  3. Ensure image exists in ECR"
    echo "  4. Check CloudWatch logs for errors"
    echo ""
    echo "To delete and recreate:"
    echo "  aws apprunner delete-service --service-arn $SERVICE_ARN --region $AWS_REGION"
    echo "  ./deploy_to_apprunner.sh"
elif [ "$STATUS" = "OPERATION_IN_PROGRESS" ]; then
    echo "Service is still deploying. Wait 5-10 minutes."
    echo "Monitor with:"
    echo "  ./monitor_deployment.sh"
elif [ "$STATUS" = "RUNNING" ]; then
    echo "Service is running! Verify with:"
    echo "  ./verify_deployment.sh"
fi
echo ""
