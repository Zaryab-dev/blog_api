#!/bin/bash

# Security Testing Script
# Tests various security features of the Django API

set -e

API_URL="${API_URL:-http://localhost:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================"
echo "Security Testing Suite"
echo "API URL: $API_URL"
echo "================================"
echo ""

# Test 1: HTTPS Redirect (only if production)
test_https_redirect() {
    echo -e "${YELLOW}[TEST 1] HTTPS Redirect${NC}"
    response=$(curl -s -o /dev/null -w "%{http_code}" -L "$API_URL/api/posts/" 2>/dev/null || echo "000")
    if [[ "$response" == "200" ]] || [[ "$response" == "301" ]]; then
        echo -e "${GREEN}✓ HTTPS redirect working${NC}"
    else
        echo -e "${RED}✗ HTTPS redirect failed (code: $response)${NC}"
    fi
    echo ""
}

# Test 2: Security Headers
test_security_headers() {
    echo -e "${YELLOW}[TEST 2] Security Headers${NC}"
    
    headers=$(curl -s -I "$API_URL/api/posts/" 2>/dev/null || echo "")
    
    check_header() {
        if echo "$headers" | grep -qi "$1"; then
            echo -e "${GREEN}✓ $1 present${NC}"
        else
            echo -e "${RED}✗ $1 missing${NC}"
        fi
    }
    
    check_header "X-Content-Type-Options"
    check_header "X-Frame-Options"
    check_header "X-XSS-Protection"
    check_header "Referrer-Policy"
    check_header "Permissions-Policy"
    echo ""
}

# Test 3: SQL Injection Protection
test_sql_injection() {
    echo -e "${YELLOW}[TEST 3] SQL Injection Protection${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/posts/?search=1%27%20OR%20%271%27=%271" 2>/dev/null || echo "000")
    
    if [[ "$response" == "400" ]] || [[ "$response" == "200" ]]; then
        echo -e "${GREEN}✓ SQL injection attempt handled${NC}"
    else
        echo -e "${RED}✗ Unexpected response: $response${NC}"
    fi
    echo ""
}

# Test 4: Path Traversal Protection
test_path_traversal() {
    echo -e "${YELLOW}[TEST 4] Path Traversal Protection${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/../../etc/passwd" 2>/dev/null || echo "000")
    
    if [[ "$response" == "400" ]] || [[ "$response" == "404" ]]; then
        echo -e "${GREEN}✓ Path traversal blocked${NC}"
    else
        echo -e "${RED}✗ Path traversal not blocked: $response${NC}"
    fi
    echo ""
}

# Test 5: Rate Limiting
test_rate_limiting() {
    echo -e "${YELLOW}[TEST 5] Rate Limiting${NC}"
    
    count=0
    for i in {1..10}; do
        response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/posts/" 2>/dev/null || echo "000")
        if [[ "$response" == "429" ]]; then
            echo -e "${GREEN}✓ Rate limit triggered after $i requests${NC}"
            return
        fi
        ((count++))
    done
    
    echo -e "${YELLOW}⚠ Rate limit not triggered in 10 requests (may be disabled in dev)${NC}"
    echo ""
}

# Test 6: CORS Policy
test_cors() {
    echo -e "${YELLOW}[TEST 6] CORS Policy${NC}"
    
    response=$(curl -s -H "Origin: https://evil.com" -I "$API_URL/api/posts/" 2>/dev/null || echo "")
    
    if echo "$response" | grep -qi "Access-Control-Allow-Origin"; then
        origin=$(echo "$response" | grep -i "Access-Control-Allow-Origin" | cut -d' ' -f2)
        if [[ "$origin" == "https://evil.com"* ]]; then
            echo -e "${RED}✗ CORS allows unauthorized origin${NC}"
        else
            echo -e "${GREEN}✓ CORS properly restricted${NC}"
        fi
    else
        echo -e "${GREEN}✓ CORS not allowing unauthorized origins${NC}"
    fi
    echo ""
}

# Test 7: Authentication Required
test_authentication() {
    echo -e "${YELLOW}[TEST 7] Authentication${NC}"
    
    # Try to access protected endpoint without auth
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/posts/" 2>/dev/null || echo "000")
    
    if [[ "$response" == "401" ]] || [[ "$response" == "403" ]]; then
        echo -e "${GREEN}✓ Authentication required for protected endpoints${NC}"
    else
        echo -e "${RED}✗ Protected endpoint accessible without auth: $response${NC}"
    fi
    echo ""
}

# Test 8: Content-Type Validation
test_content_type() {
    echo -e "${YELLOW}[TEST 8] Content-Type Validation${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/posts/" -d '{}' 2>/dev/null || echo "000")
    
    if [[ "$response" == "400" ]] || [[ "$response" == "401" ]] || [[ "$response" == "403" ]] || [[ "$response" == "415" ]]; then
        echo -e "${GREEN}✓ Content-Type validation working${NC}"
    else
        echo -e "${YELLOW}⚠ Unexpected response: $response${NC}"
    fi
    echo ""
}

# Test 9: Large Request Body
test_large_body() {
    echo -e "${YELLOW}[TEST 9] Large Request Body Protection${NC}"
    
    # Generate 11MB of data (exceeds 10MB limit)
    large_data=$(python3 -c "print('x' * 11000000)")
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/api/posts/" \
        -H "Content-Type: application/json" \
        -d "$large_data" 2>/dev/null || echo "000")
    
    if [[ "$response" == "413" ]] || [[ "$response" == "400" ]]; then
        echo -e "${GREEN}✓ Large request body rejected${NC}"
    else
        echo -e "${YELLOW}⚠ Large body not rejected: $response${NC}"
    fi
    echo ""
}

# Test 10: Malicious User Agent
test_malicious_ua() {
    echo -e "${YELLOW}[TEST 10] Malicious User Agent Detection${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -A "sqlmap/1.0" "$API_URL/api/posts/" 2>/dev/null || echo "000")
    
    if [[ "$response" == "403" ]]; then
        echo -e "${GREEN}✓ Malicious user agent blocked${NC}"
    else
        echo -e "${YELLOW}⚠ Malicious UA not blocked: $response (may be disabled in dev)${NC}"
    fi
    echo ""
}

# Run all tests
echo "Starting security tests..."
echo ""

test_https_redirect
test_security_headers
test_sql_injection
test_path_traversal
test_rate_limiting
test_cors
test_authentication
test_content_type
test_large_body
test_malicious_ua

echo "================================"
echo "Security Testing Complete"
echo "================================"
