#!/bin/bash
# Smoke tests for post-deployment validation

set -e

API_URL="${API_URL:-https://api.zaryableather.com}"
FAIL_COUNT=0

echo "🧪 Running smoke tests against: $API_URL"
echo "================================================"

# Test 1: Health check
echo "✓ Testing health check..."
HEALTH=$(curl -s -w "\n%{http_code}" "$API_URL/api/v1/healthcheck/")
STATUS=$(echo "$HEALTH" | tail -n1)
BODY=$(echo "$HEALTH" | head -n-1)

if [ "$STATUS" != "200" ]; then
    echo "  ✗ Health check failed: $STATUS"
    FAIL_COUNT=$((FAIL_COUNT + 1))
elif ! echo "$BODY" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo "  ✗ Health check not healthy"
    FAIL_COUNT=$((FAIL_COUNT + 1))
else
    echo "  ✓ Health check passed"
fi

# Test 2: API endpoints
echo ""
echo "✓ Testing API endpoints..."
POSTS=$(curl -s -w "\n%{http_code}" "$API_URL/api/v1/posts/")
STATUS=$(echo "$POSTS" | tail -n1)

if [ "$STATUS" != "200" ]; then
    echo "  ✗ Posts endpoint failed: $STATUS"
    FAIL_COUNT=$((FAIL_COUNT + 1))
else
    echo "  ✓ Posts endpoint passed"
fi

# Test 3: Schema endpoint
echo ""
echo "✓ Testing schema endpoint..."
SCHEMA=$(curl -s -w "\n%{http_code}" "$API_URL/api/v1/schema/")
STATUS=$(echo "$SCHEMA" | tail -n1)

if [ "$STATUS" != "200" ]; then
    echo "  ✗ Schema endpoint failed: $STATUS"
    FAIL_COUNT=$((FAIL_COUNT + 1))
else
    echo "  ✓ Schema endpoint passed"
fi

# Test 4: Database connectivity
echo ""
echo "✓ Testing database connectivity..."
if echo "$BODY" | jq -e '.checks.database.status == "ok"' > /dev/null 2>&1; then
    echo "  ✓ Database connected"
else
    echo "  ✗ Database connection failed"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Test 5: Redis connectivity
echo ""
echo "✓ Testing Redis connectivity..."
if echo "$BODY" | jq -e '.checks.redis.status == "ok"' > /dev/null 2>&1; then
    echo "  ✓ Redis connected"
else
    echo "  ✗ Redis connection failed"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Summary
echo ""
echo "================================================"
if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ All smoke tests passed!"
    exit 0
else
    echo "❌ $FAIL_COUNT smoke test(s) failed"
    exit 1
fi
