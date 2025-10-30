#!/bin/bash
# Security validation script for Django Blog API

set -e

API_URL="${API_URL:-http://localhost:8000}"
FAIL_COUNT=0

echo "🔒 Running security checks for: $API_URL"
echo "================================================"

# Test 1: Security Headers
echo "✓ Testing security headers..."
RESPONSE=$(curl -s -I "$API_URL/api/healthcheck/")

check_header() {
    HEADER=$1
    if echo "$RESPONSE" | grep -qi "$HEADER"; then
        echo "  ✓ $HEADER present"
    else
        echo "  ✗ $HEADER missing"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

check_header "Strict-Transport-Security"
check_header "Content-Security-Policy"
check_header "X-Frame-Options"
check_header "X-Content-Type-Options"
check_header "Referrer-Policy"
check_header "Permissions-Policy"

# Test 2: Rate Limiting
echo ""
echo "✓ Testing rate limiting..."
for i in {1..35}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/track-view/" \
        -H "Content-Type: application/json" \
        -d '{"slug":"test"}')
    if [ "$STATUS" = "429" ]; then
        echo "  ✓ Rate limiting active (blocked at request $i)"
        break
    fi
    if [ "$i" = "35" ]; then
        echo "  ⚠ Rate limiting not triggered"
    fi
done

# Test 3: Healthcheck
echo ""
echo "✓ Testing healthcheck..."
HEALTH=$(curl -s "$API_URL/api/healthcheck/")
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo "  ✓ Healthcheck returns healthy"
else
    echo "  ✗ Healthcheck not healthy"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Test 4: API Documentation
echo ""
echo "✓ Testing API docs..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/docs/")
if [ "$DOCS_STATUS" = "200" ]; then
    echo "  ✓ API docs accessible"
else
    echo "  ✗ API docs not accessible (status: $DOCS_STATUS)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Summary
echo ""
echo "================================================"
if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ All security checks passed!"
    exit 0
else
    echo "❌ $FAIL_COUNT security check(s) failed"
    exit 1
fi
