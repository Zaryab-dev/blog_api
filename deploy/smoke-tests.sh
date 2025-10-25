#!/bin/bash
# Smoke tests for production deployment

set -e

BASE_URL="${1:-http://localhost:8080}"
echo "🧪 Running smoke tests against: $BASE_URL"
echo "================================================"

PASS=0
FAIL=0

# Test 1: Health check
echo "✓ Testing health check..."
if curl -sf "$BASE_URL/api/v1/healthcheck/" > /dev/null; then
    echo "  ✅ PASS: Health check"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: Health check"
    FAIL=$((FAIL + 1))
fi

# Test 2: API root
echo "✓ Testing API root..."
if curl -sf "$BASE_URL/api/v1/posts/" > /dev/null; then
    echo "  ✅ PASS: API root accessible"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: API root"
    FAIL=$((FAIL + 1))
fi

# Test 3: Request ID header
echo "✓ Testing request ID..."
if curl -sI "$BASE_URL/api/v1/posts/" | grep -q "X-Request-ID"; then
    echo "  ✅ PASS: Request ID present"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: Request ID missing"
    FAIL=$((FAIL + 1))
fi

# Test 4: Response time
echo "✓ Testing response time..."
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' "$BASE_URL/api/v1/healthcheck/")
if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
    echo "  ✅ PASS: Response time ${RESPONSE_TIME}s"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: Response time ${RESPONSE_TIME}s (>1s)"
    FAIL=$((FAIL + 1))
fi

# Test 5: Security headers
echo "✓ Testing security headers..."
if curl -sI "$BASE_URL/api/v1/posts/" | grep -q "X-Content-Type-Options"; then
    echo "  ✅ PASS: Security headers present"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: Security headers missing"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "================================================"
echo "Results: $PASS passed, $FAIL failed"
echo "================================================"

if [ $FAIL -eq 0 ]; then
    echo "✅ All smoke tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
