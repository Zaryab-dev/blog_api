#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

export AWS_REGION=us-east-1
export SERVICE_NAME=django-blog-api-v3

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Verify App Runner Deployment                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get service URL
SERVICE_URL=$(aws apprunner describe-service \
  --service-arn $(aws apprunner list-services --region $AWS_REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text) \
  --region $AWS_REGION \
  --query 'Service.ServiceUrl' \
  --output text 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}✗ Service not found or not accessible${NC}"
    exit 1
fi

echo "Service URL: https://$SERVICE_URL"
echo ""

FAILED=0

# Test 1: Health check GET
echo -e "${YELLOW}[1/5] Testing health check (GET)...${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "https://$SERVICE_URL/api/v1/healthcheck/" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" = "200" ]; then
    if echo "$BODY" | grep -q "healthy"; then
        echo -e "${GREEN}✓ GET request successful${NC}"
        echo "  Response: $BODY"
    else
        echo -e "${RED}✗ Invalid response body${NC}"
        echo "  Response: $BODY"
        FAILED=1
    fi
else
    echo -e "${RED}✗ GET request failed (HTTP $HTTP_CODE)${NC}"
    echo "  Response: $BODY"
    FAILED=1
fi
echo ""

# Test 2: Health check HEAD
echo -e "${YELLOW}[2/5] Testing health check (HEAD)...${NC}"
HEAD_CODE=$(curl -s -I "https://$SERVICE_URL/api/v1/healthcheck/" 2>/dev/null | head -1 | grep -o "[0-9]\{3\}")
if [ "$HEAD_CODE" = "200" ]; then
    echo -e "${GREEN}✓ HEAD request successful${NC}"
else
    echo -e "${RED}✗ HEAD request failed (HTTP $HEAD_CODE)${NC}"
    FAILED=1
fi
echo ""

# Test 3: Response time
echo -e "${YELLOW}[3/5] Testing response time...${NC}"
START=$(date +%s%N)
curl -s "https://$SERVICE_URL/api/v1/healthcheck/" > /dev/null
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))
echo "  Response time: ${DURATION}ms"
if [ $DURATION -lt 1000 ]; then
    echo -e "${GREEN}✓ Response time is good (<1s)${NC}"
else
    echo -e "${YELLOW}⚠ Response time is slow (>1s)${NC}"
fi
echo ""

# Test 4: API endpoints
echo -e "${YELLOW}[4/5] Testing API endpoints...${NC}"

# Test posts endpoint
POSTS_CODE=$(curl -s -w "%{http_code}" "https://$SERVICE_URL/api/v1/posts/" -o /dev/null 2>/dev/null)
if [ "$POSTS_CODE" = "200" ]; then
    echo -e "${GREEN}✓ /api/v1/posts/ accessible (HTTP $POSTS_CODE)${NC}"
else
    echo -e "${YELLOW}⚠ /api/v1/posts/ returned HTTP $POSTS_CODE${NC}"
fi

# Test categories endpoint
CATS_CODE=$(curl -s -w "%{http_code}" "https://$SERVICE_URL/api/v1/categories/" -o /dev/null 2>/dev/null)
if [ "$CATS_CODE" = "200" ]; then
    echo -e "${GREEN}✓ /api/v1/categories/ accessible (HTTP $CATS_CODE)${NC}"
else
    echo -e "${YELLOW}⚠ /api/v1/categories/ returned HTTP $CATS_CODE${NC}"
fi

# Test tags endpoint
TAGS_CODE=$(curl -s -w "%{http_code}" "https://$SERVICE_URL/api/v1/tags/" -o /dev/null 2>/dev/null)
if [ "$TAGS_CODE" = "200" ]; then
    echo -e "${GREEN}✓ /api/v1/tags/ accessible (HTTP $TAGS_CODE)${NC}"
else
    echo -e "${YELLOW}⚠ /api/v1/tags/ returned HTTP $TAGS_CODE${NC}"
fi
echo ""

# Test 5: Check for common errors
echo -e "${YELLOW}[5/5] Checking for common errors...${NC}"
ERROR_RESPONSE=$(curl -s "https://$SERVICE_URL/api/v1/posts/" 2>/dev/null)

if echo "$ERROR_RESPONSE" | grep -qi "bad request"; then
    echo -e "${RED}✗ Bad Request error detected (ALLOWED_HOSTS issue?)${NC}"
    FAILED=1
elif echo "$ERROR_RESPONSE" | grep -qi "internal server error"; then
    echo -e "${RED}✗ Internal Server Error detected${NC}"
    FAILED=1
elif echo "$ERROR_RESPONSE" | grep -qi "service unavailable"; then
    echo -e "${RED}✗ Service Unavailable${NC}"
    FAILED=1
else
    echo -e "${GREEN}✓ No common errors detected${NC}"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
if [ $FAILED -eq 0 ]; then
    echo "║              ✅ ALL VERIFICATIONS PASSED! ✅                ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Your Django Blog API is successfully deployed!"
    echo ""
    echo "Service URL: https://$SERVICE_URL"
    echo "Health Check: https://$SERVICE_URL/api/v1/healthcheck/"
    echo "API Docs: https://$SERVICE_URL/api/v1/docs/"
    echo ""
    exit 0
else
    echo "║              ⚠️  SOME TESTS FAILED ⚠️                       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Check CloudWatch logs:"
    echo "  aws logs tail /aws/apprunner/$SERVICE_NAME --follow --region $AWS_REGION"
    echo ""
    exit 1
fi
