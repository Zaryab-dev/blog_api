#!/bin/bash
# Verification script for critical fixes

echo "🔍 Verifying Critical Fixes Applied"
echo "===================================="
echo ""

PASS=0
FAIL=0

# Fix #1: CORS Configuration
echo "✓ Checking CORS configuration..."
if grep -q "CORS_ALLOW_ALL_ORIGINS = True" leather_api/settings.py; then
    echo "  ❌ FAIL: CORS_ALLOW_ALL_ORIGINS still present"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: CORS_ALLOW_ALL_ORIGINS removed"
    PASS=$((PASS + 1))
fi

# Fix #2: Duplicate Logging
echo "✓ Checking for duplicate logging configuration..."
LOGGING_COUNT=$(grep -c "^LOGGING = {" leather_api/settings.py)
if [ "$LOGGING_COUNT" -gt 1 ]; then
    echo "  ❌ FAIL: Multiple LOGGING definitions found ($LOGGING_COUNT)"
    FAIL=$((FAIL + 1))
else
    echo "  ✅ PASS: Single LOGGING configuration"
    PASS=$((PASS + 1))
fi

# Fix #3: Migration Race Condition
echo "✓ Checking migration strategy..."
if grep -q "python manage.py migrate --noinput || echo" docker-entrypoint.sh; then
    echo "  ✅ PASS: Migrations run before Gunicorn"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: Migration race condition still exists"
    FAIL=$((FAIL + 1))
fi

# Fix #4: Docker Base Image
echo "✓ Checking Docker base image pinning..."
if grep -q "FROM python:3.11.7-slim" Dockerfile; then
    echo "  ✅ PASS: Docker base image pinned to 3.11.7"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: Docker base image not pinned"
    FAIL=$((FAIL + 1))
fi

# Fix #5: Gunicorn Configuration
echo "✓ Checking Gunicorn worker configuration..."
if grep -q 'worker_class = "gthread"' gunicorn.conf.py && grep -q 'threads = int' gunicorn.conf.py; then
    echo "  ✅ PASS: Gunicorn configured with threads"
    PASS=$((PASS + 1))
else
    echo "  ❌ FAIL: Gunicorn not properly configured"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "===================================="
echo "Results: $PASS passed, $FAIL failed"
echo "===================================="

if [ $FAIL -eq 0 ]; then
    echo "✅ All critical fixes verified!"
    echo ""
    echo "Next steps:"
    echo "1. Test locally: docker build -t blog-api . && docker run -p 8080:8080 --env-file .env blog-api"
    echo "2. Run tests: python manage.py test"
    echo "3. Deploy to staging"
    echo "4. Deploy to production"
    exit 0
else
    echo "❌ Some fixes failed verification"
    echo "Please review the failed checks above"
    exit 1
fi
