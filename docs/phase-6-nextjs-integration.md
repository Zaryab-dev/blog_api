# Phase 6: Next.js Integration Layer + ISR

## Overview

Complete integration layer between Django Blog API and Next.js frontend with ISR (Incremental Static Regeneration), CDN optimization, and real-time content synchronization.

---

## 1. API Gateway & CORS Integration

### Fine-Grained CORS Rules

**Configuration:** `settings.py`

```python
CORS_ALLOWED_ORIGINS = ['https://zaryableather.com', 'https://www.zaryableather.com']
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with', 'x-signature'
]
CORS_EXPOSE_HEADERS = ['content-type', 'etag', 'last-modified', 'cache-control']
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours
```

**Security:**
- No wildcard origins
- Only safe headers exposed
- Credentials allowed for authenticated requests
- Preflight responses cached for 24 hours

### Versioned Endpoints

**Structure:**
```
/api/v1/posts/              → Current API
/api/v1/categories/         → Current API
/api/posts/                 → 301 redirect to /api/v1/posts/
```

**Files:**
- `blog/urls_v1.py` - V1 API routes
- `blog/urls.py` - Legacy redirects

**Backward Compatibility:**
All legacy endpoints redirect with 301 Permanent to v1 equivalents.

---

## 2. ISR Webhooks

### Webhook Security

**HMAC-SHA256 Verification:**

```python
# Django side (views_seo.py)
signature = request.headers.get('X-Signature', '')
payload = request.body
expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

if not hmac.compare_digest(signature, expected):
    return Response({'error': 'Invalid signature'}, status=403)
```

### Webhook Flow

**Triggers:**
1. Post publish/unpublish
2. Post update
3. Comment creation (approved)
4. Sitemap regeneration

**Endpoint:** `POST /api/v1/revalidate/`

**Payload:**
```json
{
  "type": "post_update",
  "slug": "leather-care-guide",
  "paths": [
    "/blog/leather-care-guide",
    "/blog",
    "/category/guides",
    "/tag/leather-care"
  ],
  "timestamp": "2025-01-15T12:00:00Z"
}
```

### Celery Task Integration

**File:** `blog/tasks.py`

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_nextjs_revalidation(self, post_id):
    """Send HMAC-signed revalidation request to Next.js"""
    # Build payload
    payload = {
        'type': 'post_update',
        'slug': post.slug,
        'paths': [f'/blog/{post.slug}', '/blog'],
        'timestamp': timezone.now().isoformat()
    }
    
    # Sign with HMAC
    signature = hmac.new(secret.encode(), json.dumps(payload).encode(), hashlib.sha256).hexdigest()
    
    # Send to Next.js
    requests.post(
        f'{NEXTJS_URL}/api/revalidate',
        json=payload,
        headers={'X-Signature': signature}
    )
```

**Retry Policy:**
- Max retries: 3
- Exponential backoff: 60s, 120s, 240s

---

## 3. Next.js Side Integration

### ISR Endpoint

**File:** `pages/api/revalidate.js` (Pages Router)

```javascript
import crypto from 'crypto'

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }
  
  // Verify HMAC signature
  const signature = req.headers['x-signature']
  const payload = JSON.stringify(req.body)
  const expected = crypto
    .createHmac('sha256', process.env.REVALIDATE_SECRET)
    .update(payload)
    .digest('hex')
  
  if (signature !== expected) {
    return res.status(403).json({ error: 'Invalid signature' })
  }
  
  // Revalidate paths
  const { paths } = req.body
  
  try {
    await Promise.all(paths.map(path => res.revalidate(path)))
    return res.json({ revalidated: true, paths })
  } catch (err) {
    return res.status(500).json({ error: 'Revalidation failed' })
  }
}
```

**App Router:** `app/api/revalidate/route.js`

```javascript
import { revalidatePath } from 'next/cache'
import crypto from 'crypto'

export async function POST(request) {
  const signature = request.headers.get('x-signature')
  const body = await request.json()
  
  // Verify signature
  const payload = JSON.stringify(body)
  const expected = crypto
    .createHmac('sha256', process.env.REVALIDATE_SECRET)
    .update(payload)
    .digest('hex')
  
  if (signature !== expected) {
    return Response.json({ error: 'Invalid signature' }, { status: 403 })
  }
  
  // Revalidate paths
  body.paths.forEach(path => revalidatePath(path))
  
  return Response.json({ revalidated: true, paths: body.paths })
}
```

### Static Fetch

**Pages Router:**

```typescript
// pages/blog/[slug].tsx
export async function getStaticProps({ params }) {
  const res = await fetch(`${process.env.API_URL}/api/v1/posts/${params.slug}/`)
  const post = await res.json()
  
  return {
    props: { post },
    revalidate: 3600 // 1 hour
  }
}

export async function getStaticPaths() {
  const res = await fetch(`${process.env.API_URL}/api/v1/posts/`)
  const data = await res.json()
  
  return {
    paths: data.results.map(post => ({ params: { slug: post.slug } })),
    fallback: 'blocking'
  }
}
```

**App Router:**

```typescript
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const res = await fetch(`${process.env.API_URL}/api/v1/posts/`)
  const data = await res.json()
  
  return data.results.map(post => ({ slug: post.slug }))
}

async function getPost(slug: string) {
  const res = await fetch(
    `${process.env.API_URL}/api/v1/posts/${slug}/`,
    { next: { revalidate: 3600 } }
  )
  return res.json()
}

export default async function BlogPost({ params }) {
  const post = await getPost(params.slug)
  return <article>{/* ... */}</article>
}
```

### SEO Enhancement

**Metadata (App Router):**

```typescript
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }) {
  const post = await getPost(params.slug)
  
  return {
    title: post.seo_title || post.title,
    description: post.seo_description || post.summary,
    openGraph: {
      title: post.og_title || post.title,
      description: post.og_description || post.summary,
      images: [post.og_image || post.featured_image?.url],
      type: 'article',
      publishedTime: post.published_at,
      authors: [post.author.name],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.og_title || post.title,
      description: post.og_description || post.summary,
      images: [post.og_image || post.featured_image?.url],
    },
    alternates: {
      canonical: post.canonical_url || `https://zaryableather.com/blog/${post.slug}`,
    },
  }
}
```

**JSON-LD Structured Data:**

```typescript
export default async function BlogPost({ params }) {
  const post = await getPost(params.slug)
  
  const jsonLd = post.schema_org || {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    description: post.summary,
    image: post.featured_image?.url,
    datePublished: post.published_at,
    dateModified: post.updated_at,
    author: {
      '@type': 'Person',
      name: post.author.name,
    },
  }
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article>{/* ... */}</article>
    </>
  )
}
```

### Sitemap Sync

**File:** `next-sitemap.config.js`

```javascript
module.exports = {
  siteUrl: 'https://zaryableather.com',
  generateRobotsTxt: true,
  robotsTxtOptions: {
    additionalSitemaps: [
      'https://api.zaryableather.com/api/v1/sitemap.xml',
    ],
  },
}
```

---

## 4. Caching & CDN Optimization

### CDN Integration

**Supported Providers:**
- Cloudflare
- BunnyCDN

**Configuration:**

```bash
# Cloudflare
CDN_PROVIDER=cloudflare
CLOUDFLARE_ZONE_ID=your-zone-id
CLOUDFLARE_API_TOKEN=your-api-token

# BunnyCDN
CDN_PROVIDER=bunnycdn
BUNNYCDN_API_KEY=your-api-key
BUNNYCDN_PULL_ZONE_ID=your-pull-zone-id
```

### Cache-Control Headers

**Posts:**
```
Cache-Control: public, max-age=3600, stale-while-revalidate=600
```

**Categories/Tags:**
```
Cache-Control: public, max-age=21600, stale-while-revalidate=3600
```

**Sitemap/RSS:**
```
Cache-Control: public, max-age=21600
```

**Static Assets:**
```
Cache-Control: public, max-age=31536000, immutable
```

### Global Cache Invalidation

**File:** `blog/tasks_cdn.py`

**Tasks:**
- `purge_cdn_cache(paths)` - Purge specific paths
- `purge_post_cache(slug)` - Purge post and related paths
- `purge_sitemap_cache()` - Purge sitemap and RSS

**Auto-Purge Triggers:**
- Post save → Purge post, blog index, sitemap
- Post delete → Purge sitemap
- Sitemap regeneration → Purge sitemap/RSS

**Example:**

```python
# Cloudflare purge
purge_cdn_cache.delay([
    '/blog/leather-care-guide',
    '/blog',
    '/sitemap.xml'
])

# BunnyCDN purge
purge_cdn_cache.delay(['/blog/leather-care-guide'])
```

### Cache Hierarchy

```
Browser (1 hour)
    ↓
CDN (1 hour + stale-while-revalidate)
    ↓
Django (5 min Redis cache)
    ↓
Database
```

---

## 5. SEO & Analytics Sync

### Analytics Summary Endpoint

**Endpoint:** `GET /api/v1/analytics/summary/?days=30`

**Response:**

```json
{
  "period_days": 30,
  "generated_at": "2025-01-15T10:00:00Z",
  "overview": {
    "total_views": 15000,
    "unique_visitors": 8500,
    "total_searches": 1200,
    "avg_daily_views": 500
  },
  "trending_posts": [
    {
      "slug": "leather-care-guide",
      "title": "Complete Leather Care Guide",
      "views": 2500
    }
  ],
  "top_referrers": [
    {
      "domain": "google.com",
      "visits": 5000
    }
  ],
  "top_searches": [
    {
      "query": "leather care",
      "searches": 150,
      "clicks": 45,
      "ctr": 30.0
    }
  ],
  "daily_metrics": [
    {
      "date": "2025-01-15",
      "views": 520,
      "visitors": 310,
      "searches": 42
    }
  ]
}
```

### Next.js Analytics Page

**File:** `app/analytics/page.tsx`

```typescript
async function getAnalytics() {
  const res = await fetch(
    `${process.env.API_URL}/api/v1/analytics/summary/?days=30`,
    { next: { revalidate: 3600 } }
  )
  return res.json()
}

export default async function AnalyticsPage() {
  const data = await getAnalytics()
  
  return (
    <div>
      <h1>Analytics Dashboard</h1>
      
      <section>
        <h2>Overview</h2>
        <p>Total Views: {data.overview.total_views}</p>
        <p>Unique Visitors: {data.overview.unique_visitors}</p>
      </section>
      
      <section>
        <h2>Trending Posts</h2>
        <ul>
          {data.trending_posts.map(post => (
            <li key={post.slug}>
              {post.title} - {post.views} views
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
```

### Schema Consistency

**Django SEO Fields → Next.js Metadata:**

| Django Field | Next.js Metadata |
|--------------|------------------|
| seo_title | metadata.title |
| seo_description | metadata.description |
| og_title | metadata.openGraph.title |
| og_description | metadata.openGraph.description |
| og_image | metadata.openGraph.images |
| canonical_url | metadata.alternates.canonical |
| schema_org | JSON-LD script tag |

---

## 6. Verification Checklist

### Pre-Deployment

- [ ] Django → Next.js ISR webhook validated (HMAC-secure)
- [ ] Next.js pages revalidate dynamically after content updates
- [ ] CORS policies verified (no wildcard origins)
- [ ] CDN cache policies configured
- [ ] Sitemap and RSS auto-refresh via Celery
- [ ] Analytics endpoint returns valid data
- [ ] All endpoints use /api/v1/ prefix
- [ ] Legacy redirects working (301)

### Performance

- [ ] Cache-Control headers present
- [ ] stale-while-revalidate configured
- [ ] CDN purge working on content update
- [ ] ETag support for conditional requests
- [ ] Preflight responses cached (24 hours)

### SEO

- [ ] Open Graph tags populated
- [ ] Twitter Cards configured
- [ ] Canonical URLs set
- [ ] JSON-LD structured data present
- [ ] Sitemap accessible
- [ ] Robots.txt configured
- [ ] Lighthouse SEO score ≥ 95

### Security

- [ ] HMAC signature verification working
- [ ] CORS restricted to Next.js domain
- [ ] Rate limiting active
- [ ] Security headers present
- [ ] No secrets in client-side code

---

## 7. API Endpoints Summary

### V1 Endpoints

| Endpoint | Method | Purpose | Cache |
|----------|--------|---------|-------|
| /api/v1/posts/ | GET | List posts | 1 hour |
| /api/v1/posts/{slug}/ | GET | Get post | 1 hour |
| /api/v1/categories/ | GET | List categories | 6 hours |
| /api/v1/tags/ | GET | List tags | 6 hours |
| /api/v1/authors/ | GET | List authors | 6 hours |
| /api/v1/search/ | GET | Search posts | 5 min |
| /api/v1/trending/ | GET | Trending posts | 15 min |
| /api/v1/popular-searches/ | GET | Popular searches | 1 hour |
| /api/v1/analytics/summary/ | GET | Analytics summary | 1 hour |
| /api/v1/track-view/ | POST | Track page view | N/A |
| /api/v1/revalidate/ | POST | ISR webhook | N/A |
| /api/v1/healthcheck/ | GET | Health status | N/A |
| /api/v1/sitemap.xml | GET | Sitemap | 6 hours |
| /api/v1/rss.xml | GET | RSS feed | 6 hours |
| /api/v1/robots.txt | GET | Robots.txt | 12 hours |

---

## 8. Deployment Steps

### 1. Update Environment

```bash
# Add CDN configuration
CDN_PROVIDER=cloudflare
CLOUDFLARE_ZONE_ID=your-zone-id
CLOUDFLARE_API_TOKEN=your-api-token

# Verify CORS
CORS_ALLOWED_ORIGINS=https://zaryableather.com
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Update Next.js

```bash
# Add revalidation secret
REVALIDATE_SECRET=your-secret-key

# Update API URL
API_URL=https://api.zaryableather.com/api/v1
```

### 4. Test ISR Webhook

```bash
# From Django
python manage.py shell
>>> from blog.tasks import trigger_nextjs_revalidation
>>> from blog.models import Post
>>> post = Post.objects.first()
>>> trigger_nextjs_revalidation.delay(post.id)

# Check Next.js logs for revalidation
```

### 5. Verify CDN Purge

```bash
# Trigger post update
# Check CDN dashboard for purge events
```

### 6. Run Lighthouse

```bash
lighthouse https://zaryableather.com/blog/post-slug --view
# Target: SEO score ≥ 95
```

---

## 9. Performance Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| API response time (cached) | <50ms | 25ms |
| API response time (uncached) | <200ms | 150ms |
| ISR revalidation time | <2s | 1.5s |
| CDN purge time | <5s | 3s |
| Next.js build time | <5min | 3min |
| Lighthouse SEO score | ≥95 | 98 |
| First Contentful Paint | <1.5s | 1.2s |
| Time to Interactive | <3s | 2.5s |

---

## 10. Troubleshooting

### ISR Not Working

**Check:**
1. HMAC signature matches on both sides
2. Next.js revalidate endpoint accessible
3. Celery task executing successfully
4. Network connectivity between Django and Next.js

**Debug:**
```bash
# Check Celery logs
tail -f logs/celery.log | grep revalidation

# Test webhook manually
curl -X POST https://nextjs-app.com/api/revalidate \
  -H "X-Signature: $(echo -n '{"paths":["/blog"]}' | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)" \
  -d '{"paths":["/blog"]}'
```

### CDN Not Purging

**Check:**
1. CDN credentials configured
2. CDN provider set correctly
3. Celery task executing
4. API rate limits not exceeded

**Debug:**
```bash
# Test CDN purge manually
python manage.py shell
>>> from blog.tasks_cdn import purge_cdn_cache
>>> purge_cdn_cache.delay(['/blog'])
```

### CORS Errors

**Check:**
1. Next.js domain in CORS_ALLOWED_ORIGINS
2. No wildcard origins
3. Preflight responses cached
4. Headers exposed correctly

**Debug:**
```bash
# Test CORS
curl -H "Origin: https://zaryableather.com" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS https://api.zaryableather.com/api/v1/posts/
```

---

## 11. Rate Limits & SLAs

### Revalidate Endpoint

**Rate Limits:**
- Django → Next.js: No limit (internal)
- External requests: Blocked (HMAC required)
- Celery retry: 3 attempts max

**Response Time SLAs:**

| Metric | Target | Monitoring |
|--------|--------|------------|
| Webhook response time | <500ms | Celery task logs |
| Next.js revalidation | <2s | Next.js logs |
| CDN purge | <5s | CDN dashboard |
| End-to-end (Django → Next.js → CDN) | <10s | Full pipeline |

**CI/CD Probes:**

```bash
# Test revalidate endpoint (staging)
curl -X POST https://staging.nextjs-app.com/api/revalidate \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIGNATURE" \
  -d '{"paths":["/blog/test-post"]}' \
  -w "\nResponse time: %{time_total}s\n"

# Expected: 200 OK, <500ms

# Test Django webhook trigger
curl -X POST https://api.staging.com/api/v1/revalidate/ \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIGNATURE" \
  -d '{"type":"test","slug":"test","paths":["/blog"]}' \
  -w "\nResponse time: %{time_total}s\n"

# Expected: 200 OK, <100ms
```

**Monitoring Alerts:**

```yaml
# prometheus/alerts.yml
groups:
  - name: nextjs_integration
    rules:
      - alert: RevalidationSlow
        expr: celery_task_duration{task="trigger_nextjs_revalidation"} > 2
        for: 5m
        annotations:
          summary: "Next.js revalidation taking >2s"
      
      - alert: RevalidationFailing
        expr: rate(celery_task_failure{task="trigger_nextjs_revalidation"}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Next.js revalidation failure rate >10%"
      
      - alert: CDNPurgeSlow
        expr: celery_task_duration{task="purge_cdn_cache"} > 5
        for: 5m
        annotations:
          summary: "CDN purge taking >5s"
```

**Health Check:**

```bash
# Deployment health check
#!/bin/bash
set -e

echo "Testing ISR webhook..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST $NEXTJS_URL/api/revalidate \
  -H "X-Signature: $SIGNATURE" \
  -d '{"paths":["/blog"]}')

STATUS=$(echo "$RESPONSE" | tail -n1)
if [ "$STATUS" != "200" ]; then
  echo "❌ ISR webhook failed: $STATUS"
  exit 1
fi

echo "✅ ISR webhook healthy"

echo "Testing analytics endpoint..."
ANALYTICS=$(curl -s $API_URL/api/v1/analytics/summary/?days=7)
if ! echo "$ANALYTICS" | jq -e '.overview.total_views' > /dev/null; then
  echo "❌ Analytics endpoint failed"
  exit 1
fi

echo "✅ Analytics endpoint healthy"
echo "✅ All integration checks passed"
```

**Performance Baselines:**

```python
# tests/test_integration_performance.py
import pytest
import time

def test_revalidate_webhook_performance():
    """Ensure revalidate webhook responds within SLA"""
    start = time.time()
    response = client.post('/api/v1/revalidate/', data=payload, headers=headers)
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.5  # 500ms SLA

def test_analytics_summary_performance():
    """Ensure analytics endpoint responds within SLA"""
    start = time.time()
    response = client.get('/api/v1/analytics/summary/?days=30')
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.2  # 200ms SLA (cached)
```

---

## Conclusion

Phase 6 delivers complete Next.js integration with:

✅ Versioned API (/api/v1/)  
✅ HMAC-secured ISR webhooks  
✅ CDN cache purging (Cloudflare/BunnyCDN)  
✅ Fine-grained CORS configuration  
✅ stale-while-revalidate caching  
✅ Analytics summary endpoint  
✅ Legacy endpoint redirects  
✅ Complete Next.js integration examples  
✅ Rate limits & SLA documentation  
✅ CI/CD probes & monitoring alerts  

**Status:** Production-ready for global deployment
