# Production Security Hardening Guide

## 🔐 Complete Security Checklist

### 1. Environment Setup

#### Generate Secure SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Generate API Secrets
```bash
openssl rand -hex 32  # For REVALIDATE_SECRET
openssl rand -hex 32  # For ANALYTICS_SECRET
```

#### Configure .env
```bash
cp .env.production.example .env
# Edit .env with your values
```

**Critical Variables:**
- `DEBUG=False` (MUST be False in production)
- `SECRET_KEY` (≥50 chars, cryptographically secure)
- `ALLOWED_HOSTS` (strict whitelist)
- `DATABASE_URL` (with `sslmode=require`)
- `REDIS_URL` (with SSL if available)

---

### 2. SSL/HTTPS Configuration

#### Enable HTTPS Redirect
Already configured in `settings.py`:
```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

#### Behind Reverse Proxy (Nginx/ALB)
Set in `.env`:
```
SECURE_PROXY_SSL_HEADER_ENABLED=True
```

#### HSTS Preload
1. Test locally: `curl -I https://yourdomain.com`
2. Submit to: https://hstspreload.org/

#### SSL Certificate Automation
```bash
# Let's Encrypt with Certbot
sudo certbot --nginx -d api.yourdomain.com
sudo certbot renew --dry-run  # Test renewal
```

Add to crontab:
```
0 0 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

---

### 3. Database Security

#### PostgreSQL Configuration
```sql
-- Create restricted user
CREATE USER django_app WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE your_db TO django_app;
GRANT USAGE ON SCHEMA public TO django_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO django_app;
REVOKE CREATE ON SCHEMA public FROM django_app;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
```

#### Connection String
```
DATABASE_URL=postgresql://django_app:password@host:5432/db?sslmode=require
```

#### Connection Pooling (PgBouncer)
```ini
[databases]
your_db = host=localhost port=5432 dbname=your_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

---

### 4. Redis Security

#### Configure Redis Authentication
```bash
# redis.conf
requirepass your_strong_redis_password
bind 127.0.0.1
protected-mode yes
```

#### Update .env
```
REDIS_URL=redis://:your_strong_redis_password@localhost:6379/1
```

---

### 5. CORS Configuration

#### Strict Whitelist
In `.env`:
```
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Never use:**
- `CORS_ALLOW_ALL_ORIGINS = True`
- Wildcards in production

#### Test CORS
```bash
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://api.yourdomain.com/api/posts/
```

---

### 6. JWT Authentication

#### Token Lifecycle
- **Access Token:** 15 minutes
- **Refresh Token:** 7 days (rotating)
- **Blacklisting:** Enabled on rotation

#### Endpoints
```python
# urls.py
from core.authentication import SecureTokenObtainView, LogoutView

urlpatterns = [
    path('api/auth/login/', SecureTokenObtainView.as_view()),
    path('api/auth/logout/', LogoutView.as_view()),
]
```

#### Usage
```bash
# Login
curl -X POST https://api.yourdomain.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Use token
curl https://api.yourdomain.com/api/posts/ \
  -H "Authorization: Bearer <access_token>"

# Logout (blacklist token)
curl -X POST https://api.yourdomain.com/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -d '{"refresh":"<refresh_token>"}'
```

---

### 7. Rate Limiting

#### Configured Rates
- Anonymous: 100/hour
- Authenticated: 1000/hour
- Login: 5/hour
- Registration: 3/hour
- IP-based: 100 requests/60 seconds

#### Test Rate Limits
```bash
for i in {1..10}; do
  curl https://api.yourdomain.com/api/auth/login/ \
    -X POST -d '{"username":"test","password":"test"}'
done
```

---

### 8. File Upload Security

#### Validators Applied
- Max size: 5MB
- Allowed extensions: jpg, jpeg, png, webp, gif
- MIME type verification
- Malicious content detection
- Filename sanitization

#### Usage
```python
from core.validators import FileValidator

class ImageUploadSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileValidator()])
```

---

### 9. Logging & Monitoring

#### Log Files
- `logs/django.log` - Application logs
- `logs/security.log` - Security events
- `logs/celery.log` - Background tasks

#### View Security Events
```bash
tail -f logs/security.log | grep -E "failed_login|sql_injection|rate_limit"
```

#### Email Alerts
Configured for ERROR level logs to `ADMIN_EMAIL`.

#### Security Event Logging
```python
from core.security_utils import log_security_event

log_security_event(
    'suspicious_activity',
    'Multiple failed login attempts',
    request,
    severity='WARNING'
)
```

---

### 10. Secret Rotation

#### Zero-Downtime SECRET_KEY Rotation
```bash
# 1. Generate new key
python manage.py rotate_secret_key

# 2. Update .env (keeps OLD_SECRET_KEY)
python manage.py rotate_secret_key --update-env

# 3. Deploy with both keys
# Django will accept sessions signed with either key

# 4. After 24-48 hours, remove OLD_SECRET_KEY from .env
```

#### JWT Secret Rotation
JWT uses SECRET_KEY. Follow same process above.

---

### 11. Security Audit

#### Run Audit
```bash
python manage.py security_audit --check all
```

#### Checks Performed
- Admin account review
- Stale session detection
- Security settings validation
- Password policy compliance

---

### 12. Attack Prevention

#### Enabled Protections
✅ SQL Injection - ORM + query validation  
✅ XSS - Bleach sanitization  
✅ CSRF - Token validation  
✅ Clickjacking - X-Frame-Options: DENY  
✅ Directory Traversal - Filename sanitization  
✅ Rate Limiting - Redis-based throttling  
✅ IP Blocking - Malicious IP/UA detection  

#### Test Attack Prevention
```bash
# SQL Injection attempt (should be blocked)
curl "https://api.yourdomain.com/api/posts/?search=1' OR '1'='1"

# Path traversal (should be blocked)
curl "https://api.yourdomain.com/../../etc/passwd"
```

---

### 13. Deployment Checklist

#### Pre-Deployment
- [ ] `DEBUG=False` in .env
- [ ] Strong SECRET_KEY (≥50 chars)
- [ ] ALLOWED_HOSTS configured
- [ ] Database SSL enabled
- [ ] Redis password set
- [ ] CORS whitelist configured
- [ ] SSL certificate installed
- [ ] Static files collected
- [ ] Migrations applied

#### Post-Deployment
- [ ] Run `python manage.py security_audit`
- [ ] Test HTTPS redirect
- [ ] Verify CORS policy
- [ ] Test rate limiting
- [ ] Check log files
- [ ] Monitor error tracking (Sentry)
- [ ] Test JWT authentication
- [ ] Verify file upload restrictions

---

### 14. Monitoring & Alerts

#### Sentry Integration
Already configured. Set in `.env`:
```
SENTRY_DSN=https://key@sentry.io/project
SENTRY_TRACES_SAMPLE_RATE=0.1
```

#### Health Check Endpoint
```python
# Add to urls.py
path('health/', lambda r: JsonResponse({'status': 'ok'}))
```

#### Uptime Monitoring
Use services like:
- UptimeRobot
- Pingdom
- AWS CloudWatch

---

### 15. Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    # Security headers (redundant with Django middleware, but good practice)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Hide server version
    server_tokens off;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

### 16. Testing Security

#### Automated Security Tests
```bash
# Install security testing tools
pip install bandit safety

# Run security checks
bandit -r . -ll
safety check

# Run Django system checks
python manage.py check --deploy
```

#### Manual Penetration Testing
Consider hiring professionals or using:
- OWASP ZAP
- Burp Suite
- Nmap
- SQLMap (to verify protection)

---

### 17. Incident Response

#### If Breach Detected
1. **Isolate:** Take affected systems offline
2. **Investigate:** Check logs for entry point
3. **Rotate:** Change all secrets immediately
4. **Patch:** Fix vulnerability
5. **Notify:** Inform affected users
6. **Document:** Write post-mortem

#### Emergency Contacts
Document in `.env` or secure location:
- Security team email
- On-call phone numbers
- Incident response plan link

---

### 18. Compliance

#### GDPR Considerations
- User data encryption at rest
- Right to deletion (implement user data export/delete)
- Privacy policy
- Cookie consent

#### PCI DSS (if handling payments)
- Never store credit card data
- Use payment gateway (Stripe, PayPal)
- Maintain audit logs

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.production.example .env
# Edit .env with your values

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Run security audit
python manage.py security_audit

# 7. Start with Gunicorn
gunicorn leather_api.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 📞 Support

For security issues, contact: security@yourdomain.com

**Never disclose security vulnerabilities publicly.**
