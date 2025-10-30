# 📊 SEO Analytics Backend Guide

## Overview

Lightweight analytics system for tracking API hits, crawlers, and SEO performance.

---

## 🎯 Features

- **Crawler Detection**: Identify search engine bots
- **API Tracking**: Monitor endpoint usage
- **Performance Metrics**: Response time logging
- **Referrer Tracking**: Source attribution
- **Schema Monitoring**: Track schema requests

---

## 📊 Analytics Models

### SEOAnalyticsLog

**Fields:**
- `event_type`: api_hit, crawler_visit, schema_request, validation
- `url`: Full request URL
- `object_type`: post, author, category
- `object_id`: Slug or ID
- `user_agent`: Browser/bot identifier
- `ip_address`: Client IP
- `referrer`: HTTP referrer
- `is_crawler`: Boolean flag
- `crawler_name`: Googlebot, Bingbot, etc.
- `response_time_ms`: Performance metric
- `created_at`: Timestamp

---

## 🕷️ Crawler Detection

### Supported Crawlers
- **Googlebot** - Google Search
- **Bingbot** - Bing Search
- **Yahoo Slurp** - Yahoo Search
- **DuckDuckBot** - DuckDuckGo
- **Baidu Spider** - Baidu Search
- **Yandex Bot** - Yandex Search
- **Facebook Bot** - Facebook sharing
- **Twitter Bot** - Twitter cards
- **LinkedIn Bot** - LinkedIn sharing

### Detection Logic
```python
user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

if 'googlebot' in user_agent:
    is_crawler = True
    crawler_name = 'Googlebot'
```

---

## 📈 Analytics Queries

### Recent Crawler Visits
```python
from blog.models_seo import SEOAnalyticsLog

crawlers = SEOAnalyticsLog.objects.filter(
    is_crawler=True
).order_by('-created_at')[:50]

for log in crawlers:
    print(f"{log.crawler_name}: {log.url}")
```

### Googlebot Activity
```python
googlebot_visits = SEOAnalyticsLog.objects.filter(
    crawler_name='Googlebot',
    created_at__gte=timezone.now() - timedelta(days=7)
).count()

print(f"Googlebot visits (7 days): {googlebot_visits}")
```

### Most Popular Posts
```python
from django.db.models import Count

popular = SEOAnalyticsLog.objects.filter(
    object_type='post'
).values('object_id').annotate(
    hits=Count('id')
).order_by('-hits')[:10]
```

### Average Response Time
```python
from django.db.models import Avg

avg_time = SEOAnalyticsLog.objects.filter(
    event_type='schema_request'
).aggregate(Avg('response_time_ms'))

print(f"Avg response: {avg_time['response_time_ms__avg']:.2f}ms")
```

### Referrer Analysis
```python
referrers = SEOAnalyticsLog.objects.exclude(
    referrer=''
).values('referrer').annotate(
    count=Count('id')
).order_by('-count')[:10]
```

---

## 🎨 Admin Dashboard

### View Analytics
1. Go to Django Admin
2. Navigate to **SEO Analytics Log**
3. Filter by:
   - Event type
   - Crawler status
   - Date range
   - Object type

### Export Data
```python
# Export to CSV
import csv
from django.http import HttpResponse

def export_analytics(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Event', 'URL', 'Crawler', 'Response Time'])
    
    logs = SEOAnalyticsLog.objects.all()[:1000]
    for log in logs:
        writer.writerow([
            log.created_at,
            log.event_type,
            log.url,
            log.crawler_name,
            log.response_time_ms
        ])
    
    return response
```

---

## 📊 Performance Monitoring

### Response Time Tracking
```python
# Slow requests (>100ms)
slow_requests = SEOAnalyticsLog.objects.filter(
    response_time_ms__gt=100
).order_by('-response_time_ms')[:20]

for log in slow_requests:
    print(f"{log.url}: {log.response_time_ms}ms")
```

### Endpoint Performance
```python
from django.db.models import Avg, Max, Min

stats = SEOAnalyticsLog.objects.filter(
    event_type='schema_request'
).aggregate(
    avg=Avg('response_time_ms'),
    max=Max('response_time_ms'),
    min=Min('response_time_ms')
)

print(f"Avg: {stats['avg']:.2f}ms")
print(f"Max: {stats['max']}ms")
print(f"Min: {stats['min']}ms")
```

---

## 🔍 Crawler Insights

### Daily Crawler Activity
```python
from django.db.models.functions import TruncDate
from django.db.models import Count

daily_crawlers = SEOAnalyticsLog.objects.filter(
    is_crawler=True
).annotate(
    date=TruncDate('created_at')
).values('date', 'crawler_name').annotate(
    count=Count('id')
).order_by('-date')
```

### Crawler Coverage
```python
# Posts crawled by Googlebot
crawled_posts = SEOAnalyticsLog.objects.filter(
    crawler_name='Googlebot',
    object_type='post'
).values('object_id').distinct().count()

total_posts = Post.published.count()
coverage = (crawled_posts / total_posts) * 100

print(f"Googlebot coverage: {coverage:.1f}%")
```

---

## 🎯 Use Cases

### 1. Monitor Indexing
Track when Googlebot visits new posts:
```python
recent_posts = Post.published.filter(
    published_at__gte=timezone.now() - timedelta(days=7)
)

for post in recent_posts:
    crawled = SEOAnalyticsLog.objects.filter(
        crawler_name='Googlebot',
        object_id=post.slug
    ).exists()
    
    status = "✓ Crawled" if crawled else "⏳ Pending"
    print(f"{post.title}: {status}")
```

### 2. Identify Popular Content
```python
# Most requested schemas
popular_schemas = SEOAnalyticsLog.objects.filter(
    event_type='schema_request',
    created_at__gte=timezone.now() - timedelta(days=30)
).values('object_id').annotate(
    requests=Count('id')
).order_by('-requests')[:10]
```

### 3. Track Social Sharing
```python
social_bots = SEOAnalyticsLog.objects.filter(
    crawler_name__in=['Facebook', 'Twitter', 'LinkedIn']
).values('crawler_name').annotate(
    count=Count('id')
)
```

### 4. Performance Optimization
```python
# Find slow endpoints
slow_endpoints = SEOAnalyticsLog.objects.values('url').annotate(
    avg_time=Avg('response_time_ms')
).filter(avg_time__gt=100).order_by('-avg_time')
```

---

## 🔧 Configuration

### Enable Middleware
```python
# settings.py
MIDDLEWARE = [
    ...
    'blog.middleware.seo_analytics.SEOAnalyticsMiddleware',
]
```

### Disable for Development
```python
# settings.py
if DEBUG:
    MIDDLEWARE = [m for m in MIDDLEWARE if 'seo_analytics' not in m]
```

---

## 📊 Reporting

### Weekly Report
```python
from datetime import timedelta
from django.utils import timezone

week_ago = timezone.now() - timedelta(days=7)

report = {
    'total_hits': SEOAnalyticsLog.objects.filter(
        created_at__gte=week_ago
    ).count(),
    'crawler_visits': SEOAnalyticsLog.objects.filter(
        created_at__gte=week_ago,
        is_crawler=True
    ).count(),
    'schema_requests': SEOAnalyticsLog.objects.filter(
        created_at__gte=week_ago,
        event_type='schema_request'
    ).count(),
    'avg_response_time': SEOAnalyticsLog.objects.filter(
        created_at__gte=week_ago
    ).aggregate(Avg('response_time_ms'))['response_time_ms__avg']
}

print(f"Weekly Report:")
print(f"Total Hits: {report['total_hits']}")
print(f"Crawler Visits: {report['crawler_visits']}")
print(f"Schema Requests: {report['schema_requests']}")
print(f"Avg Response: {report['avg_response_time']:.2f}ms")
```

---

## 🎯 Best Practices

1. **Monitor daily** for crawler activity
2. **Track response times** for performance
3. **Analyze referrers** for traffic sources
4. **Review popular content** for optimization
5. **Export data** for external analysis
6. **Clean old logs** periodically
7. **Alert on anomalies** (sudden drops/spikes)

---

## 🧹 Maintenance

### Clean Old Logs
```python
# Keep last 90 days
from datetime import timedelta
from django.utils import timezone

cutoff = timezone.now() - timedelta(days=90)
SEOAnalyticsLog.objects.filter(created_at__lt=cutoff).delete()
```

### Archive Data
```python
# Export before deletion
old_logs = SEOAnalyticsLog.objects.filter(
    created_at__lt=cutoff
)

# Save to file or external DB
# Then delete
old_logs.delete()
```

---

**Status:** ✅ Production Ready

**Version:** 1.0.0

**Last Updated:** 2025-01-10
