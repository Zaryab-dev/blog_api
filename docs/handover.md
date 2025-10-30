# Phase 2 Handover Notes

**Project:** Django Blog API → Next.js SSG  
**Date:** 2025  
**For:** Backend & Frontend Developers

---

## 1. Quick Start

### 1.1 Repository Structure

```
leather_api/
├── docs/
│   ├── phase-1-architecture.md    # Main architecture document
│   ├── phase2-checklist.md        # Implementation checklist
│   ├── handover.md                # This file
│   ├── api_examples.md            # Sample API responses
│   └── diagrams/
│       └── site-tree.txt          # Site structure diagram
├── leather_api/                   # Django project
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── blog/                          # Blog app (to be created)
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── ...
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── manage.py
```

### 1.2 Local Development Setup

**Prerequisites:**
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for Next.js frontend)

**Backend setup:**
```bash
# Clone repository
git clone <repo-url>
cd leather_api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your local settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# In another terminal, run Celery worker
celery -A leather_api worker -l info

# In another terminal, run Redis
redis-server
```

**Frontend setup (Next.js):**
```bash
# In a separate directory
git clone <nextjs-repo-url>
cd nextjs-blog

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local
# Edit .env.local with API URL and secrets

# Run development server
npm run dev
```

---

## 2. Environment Variables

### 2.1 Backend (Django)

**Required environment variables:**

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/leather_blog

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3 (for image storage)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=zaryableather-media
AWS_CLOUDFRONT_DOMAIN=cdn.zaryableather.com
AWS_REGION=us-east-1

# Secrets
SECRET_KEY=<django-secret-key>
PREVIEW_SECRET=<random-256-bit-hex>
REVALIDATE_SECRET=<random-256-bit-hex>

# Next.js Integration
NEXTJS_URL=https://zaryableather.com

# Environment
ENVIRONMENT=development  # or staging, production
DEBUG=True  # False in production
ALLOWED_HOSTS=localhost,127.0.0.1,api.zaryableather.com

# Site Configuration
SITE_URL=https://zaryableather.com

# Sentry (optional)
SENTRY_DSN=https://...@sentry.io/...

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://zaryableather.com
```

**Generate secrets:**
```bash
# Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# PREVIEW_SECRET and REVALIDATE_SECRET
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2.2 Frontend (Next.js)

**Required environment variables:**

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.zaryableather.com

# Secrets (must match backend)
REVALIDATE_SECRET=<same-as-backend>
PREVIEW_SECRET=<same-as-backend>

# Site Configuration
NEXT_PUBLIC_SITE_URL=https://zaryableather.com
```

---

## 3. API Integration Guide

### 3.1 API Base URL

**Development:** `http://localhost:8000`  
**Staging:** `https://api-staging.zaryableather.com`  
**Production:** `https://api.zaryableather.com`

### 3.2 Key Endpoints for Next.js

**Fetch all post slugs (for getStaticPaths):**
```javascript
const response = await fetch('https://api.zaryableather.com/api/v1/posts/slugs/');
const data = await response.json();
const slugs = data.results.map(post => post.slug);
```

**Fetch single post (for getStaticProps):**
```javascript
const response = await fetch(`https://api.zaryableather.com/api/v1/posts/${slug}/`);
const post = await response.json();
```

**Fetch site settings (for layout):**
```javascript
const response = await fetch('https://api.zaryableather.com/api/v1/meta/site/');
const siteSettings = await response.json();
```

**Fetch redirects (for middleware):**
```javascript
const response = await fetch('https://api.zaryableather.com/api/v1/redirects/');
const { redirects } = await response.json();
```

### 3.3 Revalidation Webhook

**Next.js API route:** `/pages/api/revalidate.js`

```javascript
import crypto from 'crypto';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Validate HMAC signature
  const signature = req.headers['x-signature'];
  const secret = process.env.REVALIDATE_SECRET;
  const payload = JSON.stringify(req.body, Object.keys(req.body).sort());
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature))) {
    return res.status(401).json({ message: 'Invalid signature' });
  }

  // Revalidate paths
  const { paths } = req.body;
  
  try {
    for (const path of paths) {
      await res.revalidate(path);
    }
    
    return res.json({ revalidated: true, paths });
  } catch (err) {
    return res.status(500).json({ message: 'Error revalidating', error: err.message });
  }
}
```

**Webhook URL to provide to backend:**
```
POST https://zaryableather.com/api/revalidate
```

### 3.4 Preview Mode

**Next.js preview API route:** `/pages/api/preview.js`

```javascript
export default async function handler(req, res) {
  const { slug, token } = req.query;

  if (!slug || !token) {
    return res.status(401).json({ message: 'Missing slug or token' });
  }

  // Fetch preview post from API
  const response = await fetch(
    `https://api.zaryableather.com/api/v1/posts/${slug}/preview/?token=${token}`
  );

  if (!response.ok) {
    return res.status(401).json({ message: 'Invalid preview token' });
  }

  // Enable preview mode
  res.setPreviewData({});

  // Redirect to post page
  res.redirect(`/blog/${slug}`);
}
```

**Preview URL format (from Django admin):**
```
https://zaryableather.com/api/preview?slug=best-leather-jackets-2025&token=<JWT>
```

---

## 4. Common Tasks

### 4.1 Create a New Post

1. Log in to Django admin: `https://api.zaryableather.com/admin/`
2. Navigate to "Posts" → "Add Post"
3. Fill in required fields:
   - Title
   - Slug (auto-generated from title)
   - Summary
   - Content (HTML or Markdown)
   - Author
   - Featured image
   - Categories and tags
4. Set status to "Published" and set publish date
5. Click "Save"
6. Backend automatically:
   - Invalidates caches
   - Regenerates sitemap
   - Sends revalidation webhook to Next.js

### 4.2 Preview a Draft Post

1. Create or edit a post in Django admin
2. Set status to "Draft"
3. Click "Preview" button
4. Opens preview URL in new tab with JWT token
5. Next.js renders draft post with noindex meta tag

### 4.3 Regenerate Sitemap Manually

**Via Django admin:**
1. Navigate to "Site Settings"
2. Click "Regenerate Sitemap" button

**Via command line:**
```bash
python manage.py regenerate_sitemap
```

**Via Celery task:**
```python
from blog.tasks import regenerate_sitemap
regenerate_sitemap.delay()
```

### 4.4 Create a Redirect

1. Log in to Django admin
2. Navigate to "Redirects" → "Add Redirect"
3. Fill in:
   - From path: `/old-url/`
   - To URL: `https://zaryableather.com/new-url/`
   - Status code: `301`
   - Active: checked
4. Click "Save"
5. Next.js middleware will handle redirect on next build

### 4.5 Update Site Settings

1. Log in to Django admin
2. Navigate to "Site Settings"
3. Edit fields (site name, description, default meta image, etc.)
4. Click "Save"
5. Cache automatically invalidated

---

## 5. Troubleshooting

### 5.1 API Returns 500 Error

**Check Sentry for error details:**
- Log in to Sentry dashboard
- Find recent error
- Check stack trace and request context

**Check Django logs:**
```bash
# If using Docker
docker logs <container-id>

# If using systemd
journalctl -u leather-api

# If using Heroku
heroku logs --tail -a leather-api
```

### 5.2 Images Not Loading

**Check S3 bucket permissions:**
- Ensure bucket has public-read ACL
- Ensure CORS configuration allows requests from Next.js domain

**Check CloudFront distribution:**
- Ensure distribution is enabled
- Ensure origin points to correct S3 bucket
- Check cache invalidation status

**Check image URLs in API response:**
- Should be absolute URLs: `https://cdn.zaryableather.com/...`
- Should include CDN domain, not S3 domain

### 5.3 Sitemap Not Updating

**Check Celery worker is running:**
```bash
celery -A leather_api inspect active
```

**Check Celery logs:**
```bash
celery -A leather_api events
```

**Manually trigger sitemap regeneration:**
```bash
python manage.py regenerate_sitemap
```

**Check S3 bucket for sitemap files:**
```bash
aws s3 ls s3://zaryableather-sitemaps/
```

### 5.4 Revalidation Webhook Failing

**Check Next.js logs:**
- Verify webhook endpoint is accessible
- Verify HMAC signature is correct

**Check Django logs for webhook errors:**
```bash
# Search for "revalidation" in logs
grep -i "revalidation" /var/log/leather-api.log
```

**Test webhook manually:**
```bash
# Generate HMAC signature
python -c "
import hmac
import hashlib
import json

secret = 'YOUR_REVALIDATE_SECRET'
payload = {'slugs': ['test'], 'paths': ['/blog/test'], 'timestamp': '2025-09-10T08:34:00Z', 'event': 'post.published'}
payload_str = json.dumps(payload, sort_keys=True)
signature = hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
print(f'Signature: {signature}')
print(f'Payload: {payload_str}')
"

# Send webhook
curl -X POST https://zaryableather.com/api/revalidate \
  -H "Content-Type: application/json" \
  -H "X-Signature: <signature>" \
  -d '<payload>'
```

### 5.5 Preview Token Expired

**Preview tokens expire after 30 minutes.**

**Solution:**
- Click "Preview" button again in Django admin to generate new token

**Check token expiration:**
```python
import jwt

token = "YOUR_TOKEN"
secret = "YOUR_PREVIEW_SECRET"

try:
    payload = jwt.decode(token, secret, algorithms=['HS256'])
    print(f"Token valid. Slug: {payload['slug']}, Expires: {payload['exp']}")
except jwt.ExpiredSignatureError:
    print("Token expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

---

## 6. Deployment

### 6.1 Staging Deployment

**Trigger:** Push to `develop` branch

**Process:**
1. GitHub Actions runs CI pipeline (lint, test)
2. Build Docker image
3. Push to container registry
4. Deploy to staging environment (AWS ECS or Heroku)
5. Run database migrations
6. Restart Celery workers
7. Invalidate CDN cache

**Staging URL:** `https://api-staging.zaryableather.com`

### 6.2 Production Deployment

**Trigger:** Push to `main` branch (with manual approval)

**Process:**
1. GitHub Actions runs CI pipeline (lint, test)
2. Build Docker image
3. Push to container registry
4. **Manual approval required**
5. Deploy to production environment
6. Run database migrations (with backup)
7. Restart Celery workers
8. Invalidate CDN cache
9. Send Slack notification

**Production URL:** `https://api.zaryableather.com`

### 6.3 Rollback

**If deployment fails:**

```bash
# Rollback to previous version (AWS ECS)
aws ecs update-service --cluster leather-api --service leather-api --task-definition leather-api:PREVIOUS_VERSION

# Rollback database migrations
python manage.py migrate blog PREVIOUS_MIGRATION

# Rollback Heroku
heroku rollback -a leather-api
```

---

## 7. Monitoring & Alerts

### 7.1 Uptime Monitoring

**Tool:** UptimeRobot

**Monitored endpoints:**
- `https://zaryableather.com/` (homepage)
- `https://api.zaryableather.com/api/v1/posts/slugs/` (API health)
- `https://zaryableather.com/sitemap.xml` (sitemap)

**Alert channels:**
- Email
- Slack

### 7.2 Error Tracking

**Tool:** Sentry

**Dashboard:** `https://sentry.io/organizations/zaryableather/`

**Alert rules:**
- 500 errors on public endpoints (immediate)
- Failed Celery tasks (after 3 failures)
- Slow queries >1s (daily digest)

### 7.3 Performance Monitoring

**Tool:** Prometheus + Grafana (or AWS CloudWatch)

**Key metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Cache hit rate
- Database query time
- Celery task queue length

**Dashboards:**
- API performance overview
- Cache performance
- Database performance
- Celery task status

---

## 8. Contact & Support

### 8.1 Team Contacts

**Backend Developer:** [Your Name] - [email]  
**Frontend Developer:** [Name] - [email]  
**DevOps:** [Name] - [email]  
**Project Manager:** [Name] - [email]

### 8.2 Resources

**Documentation:**
- Phase 1 Architecture: `/docs/phase-1-architecture.md`
- Phase 2 Checklist: `/docs/phase2-checklist.md`
- API Examples: `/docs/api_examples.md`

**External Resources:**
- Django REST Framework: https://www.django-rest-framework.org/
- Next.js ISR: https://nextjs.org/docs/basic-features/data-fetching/incremental-static-regeneration
- Schema.org Article: https://schema.org/Article
- Google Search Console: https://search.google.com/search-console

### 8.3 On-Call Runbook

**Critical issues:**
1. API down (5xx errors)
2. Database connection lost
3. Redis connection lost
4. S3/CloudFront unavailable
5. Celery workers stopped

**Response steps:**
1. Check Sentry for error details
2. Check uptime monitoring alerts
3. Check server logs
4. Restart affected services
5. Notify team in Slack
6. Create incident report

---

## 9. Next Steps

### 9.1 Phase 2 Implementation

**Start with:** Priority 1 tasks (Foundation)
- Set up project and dependencies
- Create data models
- Set up Django admin

**Follow:** Phase 2 checklist (`/docs/phase2-checklist.md`)

### 9.2 Next.js Integration

**Once API endpoints are ready:**
1. Provide API base URL to frontend developer
2. Provide `REVALIDATE_SECRET` and `PREVIEW_SECRET`
3. Test integration with staging API
4. Verify revalidation webhook works
5. Verify preview mode works
6. Test full SSG build

### 9.3 Phase 3 Enhancements (Future)

**Potential improvements:**
- Advanced search (Elasticsearch)
- Multi-language support (i18n)
- Comment system
- Related posts recommendations
- A/B testing for headlines
- Advanced analytics dashboard
- Automated SEO audits

---

**End of Handover Document**

For questions or issues, refer to the main architecture document (`phase-1-architecture.md`) or contact the team.
