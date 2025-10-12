# 🔐 Security Quick Reference

## Essential Commands

### Security Audit
```bash
python manage.py security_audit --check all
```

### Secret Key Rotation
```bash
python manage.py rotate_secret_key --update-env
```

### Run Security Tests
```bash
./scripts/test_security.sh
```

### Check Django Security
```bash
python manage.py check --deploy
```

---

## Security Features Implemented

### ✅ Environment & Secrets
- Cryptographically secure SECRET_KEY (≥50 chars)
- django-environ for safe .env loading
- Zero-downtime secret rotation strategy
- Separate dev/staging/prod configurations

### ✅ SSL/HTTPS
- SECURE_SSL_REDIRECT = True
- SECURE_PROXY_SSL_HEADER for reverse proxy
- HSTS with 1-year max-age + preload
- Automatic SSL renewal guide

### ✅ Cookie & Session Security
- SESSION_COOKIE_SECURE = True
- SESSION_COOKIE_HTTPONLY = True
- SESSION_COOKIE_SAMESITE = 'Strict'
- CSRF_COOKIE_SECURE = True
- Secure cookie prefixes (__Secure-)

### ✅ CORS Configuration
- Strict whitelist (no wildcards)
- CORS_ALLOW_CREDENTIALS = True
- Preflight request handling
- CSRF_TRUSTED_ORIGINS configured

### ✅ JWT Authentication
- Short-lived access tokens (15 min)
- Rotating refresh tokens (7 days)
- Token blacklisting on logout
- Login attempt tracking (5 attempts → 15 min lockout)
- Security event logging

### ✅ Rate Limiting
- Anonymous: 100/hour
- Authenticated: 1000/hour
- Login: 5/hour
- Registration: 3/hour
- IP-based: 100 requests/60 seconds (Redis)

### ✅ Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: geolocation=(), microphone=(), camera=()
- Content-Security-Policy with frame-ancestors 'none'
- Server fingerprint removal

### ✅ IP Blocking & Firewall
- Malicious IP detection
- User agent blacklist (sqlmap, nmap, nikto, etc.)
- Temporary IP banning (1 hour)
- Redis-based block storage

### ✅ Request Validation
- Max body size: 10MB
- Content-Type validation
- SQL injection pattern detection
- Path traversal prevention
- XSS pattern detection

### ✅ Attack Prevention
- SQL Injection → ORM + query validation
- XSS → Bleach sanitization
- CSRF → Token validation
- Clickjacking → X-Frame-Options
- Directory Traversal → Filename sanitization

### ✅ Logging & Monitoring
- Separate security.log and django.log
- RotatingFileHandler (10MB, 30 backups)
- Email alerts for errors
- Security event utility function
- Sentry integration

### ✅ Database Security
- PostgreSQL SSL required (sslmode=require)
- Connection pooling
- Minimal privilege user
- Atomic transactions

### ✅ File Upload Security
- Extension whitelist (jpg, jpeg, png, webp, gif)
- Max size: 5MB
- MIME type verification (python-magic)
- Malicious content detection
- Filename sanitization

### ✅ Password & Account Security
- Min length: 12 characters
- Complexity requirements (uppercase, lowercase, digit, special)
- Account lockout: 5 failed attempts → 15 min
- Password validators

### ✅ API Endpoint Protection
- IsAdminOrReadOnly permission
- IsOwnerOrReadOnly permission
- Unauthorized access logging
- JWT authentication required

---

## File Structure

```
leather_api/
├── core/
│   ├── middleware/
│   │   ├── security_headers.py      # Enhanced security headers
│   │   ├── rate_limit.py            # Redis IP rate limiting
│   │   ├── ip_blocking.py           # Malicious IP/UA blocking
│   │   └── request_validation.py    # Attack detection
│   ├── management/commands/
│   │   ├── security_audit.py        # Security audit tool
│   │   └── rotate_secret_key.py     # Secret rotation
│   ├── validators.py                # Password & file validators
│   ├── authentication.py            # Secure JWT auth
│   └── security_utils.py            # Security utilities
├── blog/
│   ├── permissions.py               # Enhanced permissions
│   └── throttles.py                 # Rate throttling
├── docs/
│   └── PRODUCTION_SECURITY_GUIDE.md # Complete guide
├── scripts/
│   └── test_security.sh             # Security tests
├── .env.production.example          # Production env template
└── leather_api/
    ├── settings.py                  # Main settings
    └── settings_production.py       # Production overrides
```

---

## Middleware Order (Critical)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'core.middleware.ip_blocking.IPBlockingMiddleware',        # Block first
    'core.middleware.rate_limit.IPRateLimitMiddleware',        # Then rate limit
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.request_validation.RequestValidationMiddleware',  # Validate requests
    'core.middleware.security_headers.SecurityHeadersMiddleware',      # Add headers last
]
```

---

## Environment Variables

### Required
```bash
SECRET_KEY=                    # ≥50 chars
DEBUG=False
ALLOWED_HOSTS=
DATABASE_URL=                  # with sslmode=require
REDIS_URL=
```

### Security
```bash
CORS_ALLOWED_ORIGINS=
CSRF_TRUSTED_ORIGINS=
SECURE_PROXY_SSL_HEADER_ENABLED=True  # If behind proxy
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=900
PASSWORD_MIN_LENGTH=12
```

### Rate Limiting
```bash
ANON_THROTTLE_RATE=100/hour
USER_THROTTLE_RATE=1000/hour
LOGIN_THROTTLE_RATE=5/hour
REGISTER_THROTTLE_RATE=3/hour
```

### File Upload
```bash
MAX_UPLOAD_SIZE=5242880
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,webp,gif
```

### IP Blocking
```bash
BLOCKED_IPS=1.2.3.4,5.6.7.8
BLOCKED_USER_AGENTS=sqlmap,nmap,nikto
```

---

## Testing Security

### Run All Tests
```bash
./scripts/test_security.sh
```

### Individual Tests
```bash
# SQL Injection
curl "http://localhost:8000/api/posts/?search=1' OR '1'='1"

# Path Traversal
curl "http://localhost:8000/../../etc/passwd"

# Rate Limiting
for i in {1..10}; do curl http://localhost:8000/api/posts/; done

# Malicious User Agent
curl -A "sqlmap/1.0" http://localhost:8000/api/posts/
```

---

## Deployment Checklist

### Pre-Deploy
- [ ] Set DEBUG=False
- [ ] Generate strong SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable database SSL
- [ ] Set Redis password
- [ ] Configure CORS whitelist
- [ ] Install SSL certificate
- [ ] Run migrations
- [ ] Collect static files

### Post-Deploy
- [ ] Run security_audit
- [ ] Test HTTPS redirect
- [ ] Verify CORS policy
- [ ] Test rate limiting
- [ ] Check security logs
- [ ] Test JWT authentication
- [ ] Verify file upload limits
- [ ] Monitor Sentry

---

## Common Issues

### Issue: Rate limiting not working
**Solution:** Ensure Redis is running and REDIS_URL is correct

### Issue: CORS errors
**Solution:** Add frontend domain to CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS

### Issue: JWT tokens not working
**Solution:** Check SECRET_KEY hasn't changed, run migrations for token_blacklist

### Issue: File uploads rejected
**Solution:** Check MAX_UPLOAD_SIZE and ALLOWED_IMAGE_EXTENSIONS

### Issue: Account locked
**Solution:** Clear Redis cache or wait for ACCOUNT_LOCKOUT_DURATION

---

## Security Contacts

- **Security Issues:** security@yourdomain.com
- **Documentation:** docs/PRODUCTION_SECURITY_GUIDE.md
- **Support:** admin@yourdomain.com

---

## Additional Resources

- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [HSTS Preload](https://hstspreload.org/)
