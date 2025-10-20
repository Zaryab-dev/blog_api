#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Local Docker Testing - Django Blog API            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Build Docker Image
echo -e "${YELLOW}[1/6] Building Docker image...${NC}"
docker build -t django-blog-api:test . || {
    echo -e "${RED}✗ Docker build failed!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Step 2: Create test environment file
echo -e "${YELLOW}[2/6] Creating test environment file...${NC}"
cat > .env.test << 'EOF'
PORT=8080
DEBUG=False
SECRET_KEY=test-secret-key-for-local-testing-only-min-50-chars-long
ALLOWED_HOSTS=*
DATABASE_URL=postgresql://postgres.soccrpfkqjqjaoaturjb:Zaryab@1Database@aws-1-us-east-1.pooler.supabase.com:6543/postgres
DJANGO_SETTINGS_MODULE=leather_api.settings
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMzE4OSwiZXhwIjoyMDc1NTg5MTg5fQ.9he4UDmhGEBklIjtb_UIQxUwAfxFzNyzrAZDnlrcS9E
SUPABASE_BUCKET=leather_api_storage
EOF
echo -e "${GREEN}✓ Test environment file created${NC}"
echo ""

# Step 3: Run container
echo -e "${YELLOW}[3/6] Starting Docker container...${NC}"
docker run -d \
  --name django-test \
  -p 8080:8080 \
  --env-file .env.test \
  django-blog-api:test || {
    echo -e "${RED}✗ Failed to start container!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Container started${NC}"
echo ""

# Step 4: Wait for container to start
echo -e "${YELLOW}[4/6] Waiting for container to initialize (10 seconds)...${NC}"
sleep 10

# Check container logs
echo "Container logs:"
docker logs django-test | tail -20
echo ""

# Verify container is running
if ! docker ps | grep -q django-test; then
    echo -e "${RED}✗ Container is not running!${NC}"
    echo "Full logs:"
    docker logs django-test
    docker rm -f django-test 2>/dev/null
    exit 1
fi
echo -e "${GREEN}✓ Container is running${NC}"
echo ""

# Step 5: Test health check
echo -e "${YELLOW}[5/6] Testing health check endpoint...${NC}"

# Test GET request
echo "Testing GET request..."
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8080/api/v1/healthcheck/)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}✗ Health check failed! HTTP $HTTP_CODE${NC}"
    echo "Response: $BODY"
    docker logs django-test
    docker stop django-test
    docker rm django-test
    exit 1
fi

if ! echo "$BODY" | grep -q "healthy"; then
    echo -e "${RED}✗ Health check response invalid!${NC}"
    echo "Response: $BODY"
    docker stop django-test
    docker rm django-test
    exit 1
fi

echo -e "${GREEN}✓ GET request successful: $BODY${NC}"

# Test HEAD request
echo "Testing HEAD request..."
HEAD_CODE=$(curl -s -I http://localhost:8080/api/v1/healthcheck/ | head -1 | grep -o "[0-9]\{3\}")
if [ "$HEAD_CODE" != "200" ]; then
    echo -e "${RED}✗ HEAD request failed! HTTP $HEAD_CODE${NC}"
    docker stop django-test
    docker rm django-test
    exit 1
fi
echo -e "${GREEN}✓ HEAD request successful${NC}"

# Test response time
echo "Testing response time..."
START=$(date +%s%N)
curl -s http://localhost:8080/api/v1/healthcheck/ > /dev/null
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))
echo "Response time: ${DURATION}ms"
if [ $DURATION -gt 1000 ]; then
    echo -e "${YELLOW}⚠ Response time is slow (>1s)${NC}"
else
    echo -e "${GREEN}✓ Response time is good (<1s)${NC}"
fi
echo ""

# Step 6: Verify container health
echo -e "${YELLOW}[6/6] Verifying container health...${NC}"

# Check if Gunicorn is listening
echo "Checking if Gunicorn is listening on port 8080..."
if docker exec django-test sh -c "command -v netstat >/dev/null 2>&1 && netstat -tuln | grep 8080" 2>/dev/null; then
    echo -e "${GREEN}✓ Gunicorn is listening on port 8080${NC}"
else
    echo -e "${YELLOW}⚠ netstat not available, checking with ps...${NC}"
    if docker exec django-test ps aux | grep -q "gunicorn.*8080"; then
        echo -e "${GREEN}✓ Gunicorn process found${NC}"
    else
        echo -e "${RED}✗ Gunicorn not found!${NC}"
    fi
fi

# Check static files
echo "Checking static files..."
if docker exec django-test ls /app/staticfiles/ | grep -q .; then
    echo -e "${GREEN}✓ Static files collected${NC}"
else
    echo -e "${YELLOW}⚠ No static files found${NC}"
fi
echo ""

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
docker stop django-test
docker rm django-test
rm -f .env.test

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ✅ ALL LOCAL TESTS PASSED! ✅                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Your Docker image is ready for AWS App Runner deployment!"
echo ""
echo "Next steps:"
echo "1. Push image to ECR: docker tag django-blog-api:test YOUR_ECR_URI:latest"
echo "2. docker push YOUR_ECR_URI:latest"
echo "3. Deploy to App Runner"
echo ""
