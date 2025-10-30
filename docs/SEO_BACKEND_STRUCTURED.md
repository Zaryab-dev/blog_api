# 📊 Structured Schema & Analytics Backend

## Overview

Complete structured data and analytics system for Django Blog API with Next.js integration.

---

## 🎯 Features

### 1. Schema Metadata System
- Auto-generated JSON-LD schemas
- Database storage with caching
- Admin panel control
- Custom schema overrides

### 2. Schema API Endpoints
- BlogPosting schema per post
- Person schema per author
- Website + Organization schema
- BreadcrumbList navigation

### 3. Analytics Tracking
- API hit logging
- Crawler detection
- Schema request monitoring
- Performance metrics

---

## 📡 API Endpoints

### Schema Endpoints

| Endpoint | Description | Cache |
|----------|-------------|-------|
| `GET /api/v1/seo/schema/post/<slug>/` | BlogPosting schema | 24h |
| `GET /api/v1/seo/schema/site/` | Website + Organization | 24h |
| `GET /api/v1/seo/schema/author/<username>/` | Person schema | 24h |
| `GET /api/v1/seo/schema/breadcrumbs/<slug>/` | BreadcrumbList | 12h |

---

## 🚀 Quick Start

### 1. Run Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 2. Enable Analytics Middleware
```python
# settings.py
MIDDLEWARE = [
    ...
    'blog.middleware.seo_analytics.SEOAnalyticsMiddleware',
]
```

### 3. Verify Schemas
```bash
python3 manage.py verify_seo_schema
```

### 4. Auto-fix Missing Schemas
```bash
python3 manage.py verify_seo_schema --fix
```

---

## 📊 Models

### SEOMetadata
Stores structured schema data:
- `object_type`: post, author, category, site
- `schema_type`: BlogPosting, Person, Organization, etc.
- `json_data`: JSON-LD schema
- `is_active`: Enable/disable
- `last_synced`: Auto-updated timestamp

### SEOAnalyticsLog
Tracks API and crawler activity:
- `event_type`: api_hit, crawler_visit, schema_request
- `is_crawler`: Boolean flag
- `crawler_name`: Googlebot, Bingbot, etc.
- `response_time_ms`: Performance metric

---

## 🧠 Schema Generator

### Auto-Generation
Schemas are automatically generated and cached:

```python
from blog.seo_schema_generator import generate_blog_posting_schema

post = Post.objects.get(slug='my-post')
schema = generate_blog_posting_schema(post)
```

### Caching
- Redis/Memory cache: 1-24 hours
- Database storage for persistence
- Auto-sync on post save

### Supported Schemas
- **BlogPosting**: Full article schema
- **Person**: Author profiles
- **Organization**: Site identity
- **WebSite**: Site-wide with search action
- **BreadcrumbList**: Navigation paths

---

## 🔍 Analytics Features

### Crawler Detection
Automatically detects:
- Googlebot
- Bingbot
- Yahoo Slurp
- DuckDuckBot
- Baidu Spider
- Yandex Bot
- Facebook Bot
- Twitter Bot
- LinkedIn Bot

### Tracked Metrics
- API endpoint hits
- Schema requests
- Crawler visits
- Response times
- Referrers
- IP addresses

---

## 🎨 Admin Interface

### SEO Metadata Admin
- View all schemas
- Edit JSON data
- Enable/disable schemas
- Filter by type
- Search by object ID

### Analytics Dashboard
- View crawler visits
- Monitor API hits
- Track schema requests
- Performance metrics
- Date filtering

---

## 🧪 Testing

### Test Schema Endpoints
```bash
# Post schema
curl http://localhost:8000/api/v1/seo/schema/post/my-post-slug/

# Site schema
curl http://localhost:8000/api/v1/seo/schema/site/

# Author schema
curl http://localhost:8000/api/v1/seo/schema/author/john-doe/

# Breadcrumbs
curl http://localhost:8000/api/v1/seo/schema/breadcrumbs/my-post-slug/
```

### Validate with Google
```bash
# Get schema
curl http://localhost:8000/api/v1/seo/schema/post/my-post/ | jq

# Test at: https://search.google.com/test/rich-results
```

### Verify All Schemas
```bash
python3 manage.py verify_seo_schema
```

---

## 🔌 Next.js Integration

### Fetch Schema for Post
```typescript
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }: Props) {
  const schema = await fetch(
    `${API_URL}/api/v1/seo/schema/post/${params.slug}/`
  ).then(r => r.json());
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      {/* Post content */}
    </>
  );
}
```

### Fetch Site Schema
```typescript
// app/layout.tsx
const siteSchema = await fetch(
  `${API_URL}/api/v1/seo/schema/site/`
).then(r => r.json());

<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(siteSchema) }}
/>
```

### Fetch Breadcrumbs
```typescript
const breadcrumbs = await fetch(
  `${API_URL}/api/v1/seo/schema/breadcrumbs/${params.slug}/`
).then(r => r.json());
```

---

## 📈 Analytics Queries

### View Crawler Activity
```python
from blog.models_seo import SEOAnalyticsLog

# Recent crawler visits
crawlers = SEOAnalyticsLog.objects.filter(
    is_crawler=True
).order_by('-created_at')[:50]

# Googlebot visits
googlebot = SEOAnalyticsLog.objects.filter(
    crawler_name='Googlebot'
).count()
```

### Performance Metrics
```python
# Average response time
from django.db.models import Avg

avg_time = SEOAnalyticsLog.objects.filter(
    event_type='schema_request'
).aggregate(Avg('response_time_ms'))
```

### Popular Posts
```python
# Most requested schemas
from django.db.models import Count

popular = SEOAnalyticsLog.objects.filter(
    object_type='post'
).values('object_id').annotate(
    count=Count('id')
).order_by('-count')[:10]
```

---

## 🔧 Configuration

### Cache Settings
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Schema Cache Duration
- BlogPosting: 1 hour
- Person: 1 hour
- Organization: 24 hours
- WebSite: 24 hours

---

## ✅ Validation

### Management Command
```bash
# Check all schemas
python3 manage.py verify_seo_schema

# Auto-fix issues
python3 manage.py verify_seo_schema --fix
```

### Output Example
```
Checking 150 published posts...

✓ Fixed: post-slug-1
✓ Fixed: post-slug-2
⚠ Fixed invalid: post-slug-3

==================================================
Total Posts: 150
Valid Schemas: 147
Missing Schemas: 3
==================================================
✓ All schemas valid!
```

---

## 🎯 Best Practices

1. **Enable caching** for production
2. **Run verify command** weekly
3. **Monitor analytics** for crawler activity
4. **Review schemas** in admin panel
5. **Test with Google** Rich Results
6. **Keep schemas updated** on content changes
7. **Use --fix flag** to auto-repair
8. **Monitor response times** for performance

---

## 📊 Success Metrics

### Schema Coverage
- **Target:** 100% of published posts
- **Monitor:** `verify_seo_schema` command
- **Fix:** Auto-fix with `--fix` flag

### Validation Rate
- **Target:** 100% valid schemas
- **Test:** Google Rich Results Test
- **Monitor:** Admin panel

### Crawler Activity
- **Target:** Daily Googlebot visits
- **Monitor:** SEOAnalyticsLog
- **Optimize:** Improve response times

### Performance
- **Target:** < 50ms schema generation
- **Monitor:** response_time_ms field
- **Optimize:** Redis caching

---

## 🔧 Troubleshooting

### Missing Schemas
```bash
python3 manage.py verify_seo_schema --fix
```

### Invalid JSON
Check admin panel → SEO Metadata → Edit json_data

### Cache Issues
```bash
python3 manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Analytics Not Logging
Check middleware enabled in settings.py

---

**Status:** ✅ Production Ready

**Version:** 1.0.0

**Last Updated:** 2025-01-10
