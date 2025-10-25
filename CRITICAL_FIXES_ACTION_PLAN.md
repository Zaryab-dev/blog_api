# 🚨 Critical Fixes Action Plan
## Immediate Actions Required Before Production

**Priority:** CRITICAL  
**Timeline:** 1-2 Days  
**Status:** ⚠️ BLOCKING PRODUCTION

---

## 🔴 CRITICAL FIX #1: CORS Configuration

**Issue:** Security vulnerability - allows all origins

**Current Code (settings.py line ~108):**
```python
CORS_ALLOW_ALL_ORIGINS = True  # ❌ DANGEROUS
```

**Fix:**
```python
# Remove CORS_ALLOW_ALL_ORIGINS completely
# Keep only:
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
```

**Impact:** High - Exposes API to CSRF attacks  
**Effort:** 5 minutes  
**Testing:** Verify Next.js can still access API

---

## 🔴 CRITICAL FIX #2: Duplicate Logging Configuration

**Issue:** LOGGING defined twice, second overrides first

**Location:** settings.py lines ~280 and ~550

**Fix:**
1. Remove the second LOGGING definition (line ~550)
2. Keep only the comprehensive one with JSON formatting
3. Merge any unique handlers

**Impact:** Medium - Logs not properly structured  
**Effort:** 10 minutes  
**Testing:** Check log output format

---

## 🔴 CRITICAL FIX #3: Database Migration Race Condition

**Issue:** Multiple App Runner instances run migrations simultaneously

**Current Code (docker-entrypoint.sh):**
```bash
# Migrations run in background - RACE CONDITION
(
    sleep 2
    python manage.py migrate --noinput
) &
```

**Fix Option 1 (Recommended):**
```bash
# Run migrations BEFORE starting Gunicorn
python manage.py migrate --noinput || echo "Migration failed"
exec gunicorn ...
```

**Fix Option 2 (Better for App Runner):**
Use App Runner pre-deployment hook in apprunner.yaml:
```yaml
pre-deployment:
  commands:
    - python manage.py migrate --noinput
```

**Impact:** Critical - Data corruption risk  
**Effort:** 15 minutes  
**Testing:** Deploy multiple instances simultaneously

---

## 🔴 CRITICAL FIX #4: Pin Docker Base Image

**Issue:** Unpredictable builds, security vulnerabilities

**Current Code (Dockerfile):**
```dockerfile
FROM python:3.11-slim  # ❌ No version pin
```

**Fix:**
```dockerfile
FROM python:3.11.7-slim  # ✅ Specific version
```

**Impact:** Medium - Build reproducibility  
**Effort:** 2 minutes  
**Testing:** Rebuild Docker image

---

## 🔴 CRITICAL FIX #5: Gunicorn Worker Configuration

**Issue:** Too many workers for App Runner resources

**Current Code (gunicorn.conf.py):**
```python
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
# On 1 vCPU = 3 workers (OK) but formula is wrong for scaling
```

**Fix:**
```python
# For App Runner 1 vCPU / 2GB RAM
workers = int(os.getenv("GUNICORN_WORKERS", "3"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = "gthread"  # Better for I/O bound
```

**Impact:** High - Performance and stability  
**Effort:** 5 minutes  
**Testing:** Load test with 100 concurrent requests

---

## 🟡 HIGH PRIORITY FIX #6: XSS Vulnerability in CKEditor

**Issue:** Script tags allowed in content

**Current Code (settings.py):**
```python
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'img',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span', 'figure', 'figcaption',
]
```

**Fix:**
Ensure 'script', 'iframe', 'object' are NOT in the list (currently OK, but verify)

Add sanitization in serializers:
```python
from blog.utils_sanitize import sanitize_html

class PostSerializer(serializers.ModelSerializer):
    def validate_content_html(self, value):
        return sanitize_html(value)
```

**Impact:** Critical - XSS attacks possible  
**Effort:** 30 minutes  
**Testing:** Try injecting `<script>alert('XSS')</script>`

---

## 🟡 HIGH PRIORITY FIX #7: ALLOWED_HOSTS Wildcard

**Issue:** Accepts requests from any host

**Current Code:**
```python
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
```

**Fix:**
```python
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
if not ALLOWED_HOSTS and not DEBUG:
    raise ValueError("ALLOWED_HOSTS must be set in production")
```

**Impact:** Medium - Host header attacks  
**Effort:** 5 minutes  
**Testing:** Verify deployment with proper hosts

---

## 🟡 HIGH PRIORITY FIX #8: Environment Variable Validation

**Issue:** Missing validation for critical variables

**Fix (add to settings.py):**
```python
def validate_production_settings():
    """Validate critical settings in production"""
    if not DEBUG:
        required = {
            'DATABASE_URL': os.getenv('DATABASE_URL'),
            'SECRET_KEY': SECRET_KEY,
            'ALLOWED_HOSTS': ALLOWED_HOSTS,
            'SUPABASE_URL': SUPABASE_URL,
            'SUPABASE_API_KEY': SUPABASE_API_KEY,
            'SUPABASE_BUCKET': SUPABASE_BUCKET,
        }
        
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ImproperlyConfigured(
                f"Missing required production settings: {', '.join(missing)}"
            )

validate_production_settings()
```

**Impact:** High - Fail fast on misconfiguration  
**Effort:** 10 minutes  
**Testing:** Deploy without DATABASE_URL

---

## 🟡 HIGH PRIORITY FIX #9: Session Timeout

**Issue:** Sessions never expire

**Fix (add to settings.py):**
```python
# Session security
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
```

**Impact:** Medium - Security risk  
**Effort:** 2 minutes  
**Testing:** Verify session expires after 1 hour

---

## 🟡 HIGH PRIORITY FIX #10: Add Request ID Tracing

**Issue:** Cannot trace requests across services

**Fix (create core/middleware/request_id.py):**
```python
import uuid
from django.utils.deprecation import MiddlewareMixin

class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        
    def process_response(self, request, response):
        if hasattr(request, 'id'):
            response['X-Request-ID'] = request.id
        return response
```

Add to MIDDLEWARE in settings.py:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.request_id.RequestIDMiddleware',  # Add here
    ...
]
```

**Impact:** Medium - Debugging difficulty  
**Effort:** 15 minutes  
**Testing:** Check response headers for X-Request-ID

---

## 📋 IMPLEMENTATION CHECKLIST

### Day 1 Morning (2 hours)
- [ ] Fix #1: CORS configuration
- [ ] Fix #2: Remove duplicate logging
- [ ] Fix #4: Pin Docker base image
- [ ] Fix #5: Configure Gunicorn workers
- [ ] Fix #7: Remove ALLOWED_HOSTS wildcard
- [ ] Fix #9: Add session timeout

### Day 1 Afternoon (2 hours)
- [ ] Fix #3: Database migration strategy
- [ ] Fix #6: Verify XSS protection
- [ ] Fix #8: Add environment validation
- [ ] Fix #10: Add request ID tracing

### Day 2 (4 hours)
- [ ] Test all fixes locally
- [ ] Run security scan
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Load test
- [ ] Deploy to production

---

## 🧪 TESTING CHECKLIST

### Security Tests
- [ ] CORS only allows configured origins
- [ ] XSS injection blocked
- [ ] SQL injection blocked
- [ ] CSRF protection working
- [ ] Rate limiting active

### Functionality Tests
- [ ] API endpoints respond correctly
- [ ] Authentication works
- [ ] File uploads work
- [ ] Database queries optimized
- [ ] Caching works

### Performance Tests
- [ ] Response time < 200ms
- [ ] Handle 100 concurrent users
- [ ] No memory leaks
- [ ] Database connections stable
- [ ] Cache hit rate > 70%

### Deployment Tests
- [ ] Docker build succeeds
- [ ] Health check passes
- [ ] Migrations run successfully
- [ ] Static files served
- [ ] Logs properly formatted

---

## 🚀 DEPLOYMENT PROCEDURE

### Pre-Deployment
1. Backup database
2. Tag release in Git
3. Build Docker image
4. Run security scan
5. Test in staging

### Deployment
1. Deploy to App Runner
2. Monitor health checks
3. Verify migrations
4. Check logs
5. Run smoke tests

### Post-Deployment
1. Monitor error rates
2. Check performance metrics
3. Verify API responses
4. Test critical flows
5. Update documentation

---

## 📞 ROLLBACK PLAN

If deployment fails:

1. **Immediate:** Revert to previous App Runner deployment
2. **Database:** Restore from backup if migrations failed
3. **Verify:** Run health checks
4. **Investigate:** Check logs for root cause
5. **Fix:** Address issues before retry

---

## 📊 SUCCESS CRITERIA

Deployment is successful when:

- ✅ All health checks pass
- ✅ API response time < 200ms
- ✅ Error rate < 0.1%
- ✅ No security vulnerabilities
- ✅ All critical endpoints working
- ✅ Database connections stable
- ✅ Logs properly formatted
- ✅ Monitoring dashboards green

---

## 🎯 NEXT STEPS AFTER CRITICAL FIXES

1. Complete CI/CD pipeline
2. Add comprehensive monitoring
3. Implement load testing
4. Add staging environment
5. Configure auto-scaling
6. Set up alerting
7. Document runbooks
8. Train team

---

**Created:** January 2025  
**Owner:** DevOps Team  
**Status:** Ready for Implementation  
**Estimated Time:** 1-2 Days

---

*Execute these fixes before production deployment. No exceptions.*
