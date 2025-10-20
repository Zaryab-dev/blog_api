#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

export AWS_REGION=us-east-1
export SERVICE_NAME=django-blog-api-v3

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Monitoring App Runner Deployment                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get service ARN
SERVICE_ARN=$(aws apprunner list-services --region $AWS_REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text 2>/dev/null)

if [ -z "$SERVICE_ARN" ]; then
    echo -e "${RED}✗ Service '$SERVICE_NAME' not found!${NC}"
    exit 1
fi

echo "Service: $SERVICE_NAME"
echo "ARN: $SERVICE_ARN"
echo ""
echo "Monitoring deployment status (press Ctrl+C to stop)..."
echo ""

PREV_STATUS=""
while true; do
    # Get service status
    SERVICE_INFO=$(aws apprunner describe-service --service-arn "$SERVICE_ARN" --region $AWS_REGION 2>/dev/null)
    
    STATUS=$(echo "$SERVICE_INFO" | grep -o '"Status": "[^"]*"' | head -1 | cut -d'"' -f4)
    SERVICE_URL=$(echo "$SERVICE_INFO" | grep -o '"ServiceUrl": "[^"]*"' | cut -d'"' -f4)
    
    # Only print if status changed
    if [ "$STATUS" != "$PREV_STATUS" ]; then
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        
        case $STATUS in
            "RUNNING")
                echo -e "${GREEN}[$TIMESTAMP] ✓ Status: RUNNING${NC}"
                echo ""
                echo "╔════════════════════════════════════════════════════════════╗"
                echo "║              🎉 DEPLOYMENT SUCCESSFUL! 🎉                  ║"
                echo "╚════════════════════════════════════════════════════════════╝"
                echo ""
                echo "Service URL: $SERVICE_URL"
                echo ""
                echo "Test health check:"
                echo "  curl $SERVICE_URL/api/v1/healthcheck/"
                echo ""
                
                # Test health check
                echo "Testing health check..."
                sleep 2
                HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/api/v1/healthcheck/" 2>/dev/null || echo "")
                if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
                    echo -e "${GREEN}✓ Health check passed!${NC}"
                    echo "Response: $HEALTH_RESPONSE"
                else
                    echo -e "${YELLOW}⚠ Health check response: $HEALTH_RESPONSE${NC}"
                fi
                exit 0
                ;;
            "CREATE_FAILED"|"UPDATE_FAILED"|"DELETE_FAILED")
                echo -e "${RED}[$TIMESTAMP] ✗ Status: $STATUS${NC}"
                echo ""
                echo "Deployment failed! Check CloudWatch logs:"
                echo "  aws logs tail /aws/apprunner/$SERVICE_NAME --follow --region $AWS_REGION"
                exit 1
                ;;
            "OPERATION_IN_PROGRESS")
                echo -e "${YELLOW}[$TIMESTAMP] ⏳ Status: $STATUS${NC}"
                ;;
            *)
                echo "[$TIMESTAMP] Status: $STATUS"
                ;;
        esac
        
        PREV_STATUS=$STATUS
    fi
    
    sleep 10
done
