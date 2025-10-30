# Secret Rotation Guide

## Overview

This guide covers rotating sensitive secrets in production without downtime.

## Secrets Inventory

| Secret | Purpose | Rotation Frequency | Impact |
|--------|---------|-------------------|--------|
| SECRET_KEY | Django session/CSRF | Annually | Sessions invalidated |
| REVALIDATE_SECRET | Next.js ISR webhook | Quarterly | ISR temporarily broken |
| ANALYTICS_SECRET | View tracking HMAC | Quarterly | Tracking temporarily broken |
| EMAIL_HOST_PASSWORD | SMTP authentication | As needed | Email sending fails |
| SENTRY_DSN | Error monitoring | Rarely | Monitoring stops |
| DATABASE_URL | Database connection | Rarely | Complete outage |

---

## Rotation Procedures

### 1. Django SECRET_KEY

**Impact:** All active sessions will be invalidated. Users will need to re-login.

**Steps:**

```bash
# 1. Generate new key
NEW_KEY=$(openssl rand -hex 32)

# 2. Update environment variable
export SECRET_KEY=$NEW_KEY

# 3. Restart Django workers (zero-downtime)
systemctl reload gunicorn

# 4. Clear session cache
python manage.py clearsessions
```

**Rollback:** Revert to old SECRET_KEY and restart.

---

### 2. REVALIDATE_SECRET (Next.js ISR)

**Impact:** ISR revalidation will fail until Next.js is updated.

**Steps:**

```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Update Django .env
export REVALIDATE_SECRET=$NEW_SECRET

# 3. Update Next.js .env
# In Next.js repo:
export REVALIDATE_SECRET=$NEW_SECRET

# 4. Deploy both services simultaneously
# Django:
systemctl reload gunicorn

# Next.js:
pm2 reload nextjs-app

# 5. Test webhook
curl -X POST https://api.example.com/api/revalidate/ \
  -H "Content-Type: application/json" \
  -H "X-Signature: $(echo -n '{"slugs":["test"]}' | openssl dgst -sha256 -hmac "$NEW_SECRET" | cut -d' ' -f2)" \
  -d '{"slugs":["test"]}'
```

**Rollback:** Revert both services to old secret.

---

### 3. ANALYTICS_SECRET (View Tracking)

**Impact:** View tracking will fail until Next.js is updated.

**Steps:**

```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Update Django .env
export ANALYTICS_SECRET=$NEW_SECRET

# 3. Update Next.js .env
export ANALYTICS_SECRET=$NEW_SECRET

# 4. Deploy both services
systemctl reload gunicorn
pm2 reload nextjs-app

# 5. Test tracking
curl -X POST https://api.example.com/api/track-view/ \
  -H "Content-Type: application/json" \
  -H "X-Signature: $(echo -n '{"slug":"test"}' | openssl dgst -sha256 -hmac "$NEW_SECRET" | cut -d' ' -f2)" \
  -d '{"slug":"test"}'
```

**Rollback:** Revert both services to old secret.

---

### 4. EMAIL_HOST_PASSWORD

**Impact:** Email sending will fail (comments, subscriptions).

**Steps:**

```bash
# 1. Generate new password in email provider dashboard

# 2. Update .env
export EMAIL_HOST_PASSWORD=new-password

# 3. Restart Django
systemctl reload gunicorn

# 4. Test email
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'noreply@example.com', ['admin@example.com'])
```

**Rollback:** Revert to old password.

---

### 5. Database Password

**Impact:** Complete database connection failure. HIGH RISK.

**Steps:**

```bash
# 1. Create new database user with same permissions
psql -U postgres
CREATE USER leather_api_new WITH PASSWORD 'new-password';
GRANT ALL PRIVILEGES ON DATABASE leather_api TO leather_api_new;

# 2. Test connection
psql -U leather_api_new -d leather_api -c "SELECT 1"

# 3. Update .env
export DATABASE_URL=postgresql://leather_api_new:new-password@localhost:5432/leather_api

# 4. Restart Django (zero-downtime)
systemctl reload gunicorn

# 5. Verify health
curl https://api.example.com/api/healthcheck/

# 6. Drop old user (after 24 hours)
psql -U postgres
DROP USER leather_api;
```

**Rollback:** Revert DATABASE_URL and restart.

---

## Zero-Downtime Rotation Strategy

### Dual-Secret Support (Recommended)

For critical secrets, support both old and new simultaneously:

```python
# settings.py
REVALIDATE_SECRETS = [
    env('REVALIDATE_SECRET'),
    env('REVALIDATE_SECRET_OLD', default=''),
]

# views_seo.py
def verify_signature(payload, signature):
    for secret in settings.REVALIDATE_SECRETS:
        if not secret:
            continue
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected):
            return True
    return False
```

**Rotation Steps:**

1. Add new secret as `REVALIDATE_SECRET`
2. Move old secret to `REVALIDATE_SECRET_OLD`
3. Deploy Django (accepts both)
4. Update Next.js with new secret
5. Deploy Next.js
6. Remove `REVALIDATE_SECRET_OLD` after 24 hours

---

## Automated Rotation (Future)

### AWS Secrets Manager Integration

```python
# settings.py
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

if not DEBUG:
    secrets = get_secret('leather-api/production')
    SECRET_KEY = secrets['SECRET_KEY']
    REVALIDATE_SECRET = secrets['REVALIDATE_SECRET']
```

### Rotation Lambda

```python
# lambda_function.py
def rotate_secret(event, context):
    secret_name = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']
    
    if step == 'createSecret':
        new_secret = generate_random_secret()
        secrets_manager.put_secret_value(
            SecretId=secret_name,
            SecretString=new_secret,
            VersionStages=['AWSPENDING']
        )
    
    elif step == 'setSecret':
        # Update application configuration
        update_application_config(secret_name, new_secret)
    
    elif step == 'testSecret':
        # Verify new secret works
        test_application_health()
    
    elif step == 'finishSecret':
        # Promote AWSPENDING to AWSCURRENT
        secrets_manager.update_secret_version_stage(
            SecretId=secret_name,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token
        )
```

---

## Emergency Procedures

### Compromised Secret

**Immediate Actions:**

1. **Rotate immediately** (follow procedures above)
2. **Audit logs** for unauthorized access
3. **Notify team** via incident channel
4. **Document incident** in security log

### Audit Log Query

```bash
# Check for suspicious HMAC failures
grep "Invalid signature" logs/security.log | tail -100

# Check for unusual API access
grep "403\|401" logs/django.log | tail -100

# Check Sentry for errors
# Visit: https://sentry.io/organizations/your-org/issues/
```

---

## Verification Checklist

After rotation, verify:

- [ ] Django healthcheck returns 200
- [ ] Next.js can revalidate pages
- [ ] View tracking works
- [ ] Email sending works
- [ ] Celery tasks execute
- [ ] No errors in Sentry
- [ ] No 401/403 errors in logs

---

## Rotation Schedule

| Secret | Last Rotated | Next Rotation | Owner |
|--------|--------------|---------------|-------|
| SECRET_KEY | 2024-01-01 | 2025-01-01 | DevOps |
| REVALIDATE_SECRET | 2024-01-01 | 2024-04-01 | DevOps |
| ANALYTICS_SECRET | 2024-01-01 | 2024-04-01 | DevOps |
| EMAIL_HOST_PASSWORD | 2024-01-01 | As needed | DevOps |
| DATABASE_URL | 2023-01-01 | As needed | DBA |

---

## Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for all secrets
3. **Rotate quarterly** for HMAC secrets
4. **Test in staging** before production
5. **Document all rotations** in this file
6. **Monitor for failures** after rotation
7. **Keep old secrets** for 24 hours (dual-secret)
8. **Use strong secrets** (64+ characters, random)

---

## Secret Generation

```bash
# Generate 64-character hex secret
openssl rand -hex 32

# Generate 32-character base64 secret
openssl rand -base64 32

# Generate Django SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## Support

For questions or incidents:
- **Slack:** #devops-alerts
- **Email:** devops@example.com
- **On-call:** PagerDuty rotation
