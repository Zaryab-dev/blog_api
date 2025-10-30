# Blog API - REST Endpoints

**Phase 3:** API Views & Endpoints  
**Status:** ✅ Complete

---

## Quick Start

### 1. Configure Settings

```python
# leather_api/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'blog',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'blog.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'comments': '5/min',
    }
}

CORS_ALLOWED_ORIGINS = [
    'https://zaryableather.com',
    'http://localhost:3000',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. Update Main URLs

```python
# leather_api/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('blog.urls')),
]
```

### 3. Run Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/api/posts/

---

## API Endpoints

### Posts
- `GET /api/posts/` - List posts (paginated, filterable)
- `GET /api/posts/{slug}/` - Get single post

### Taxonomy
- `GET /api/categories/` - List categories
- `GET /api/tags/` - List tags
- `GET /api/authors/` - List authors

### Interaction
- `GET /api/comments/?post_slug={slug}` - List comments
- `POST /api/comments/` - Create comment
- `GET /api/search/?q={query}` - Search posts
- `POST /api/subscribe/` - Subscribe to newsletter

---

## Examples

### List Posts with Filtering

```bash
curl "http://localhost:8000/api/posts/?categories__slug=biker&page=1&page_size=10"
```

### Get Single Post

```bash
curl "http://localhost:8000/api/posts/best-leather-jackets-2025/"
```

### Search Posts

```bash
curl "http://localhost:8000/api/search/?q=leather+jacket"
```

### Create Comment

```bash
curl -X POST "http://localhost:8000/api/comments/" \
  -H "Content-Type: application/json" \
  -d '{
    "post": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john@example.com",
    "content": "Great article!"
  }'
```

---

## Features

### Performance
- ✅ Redis caching (5 min - 1 hour)
- ✅ ETag support (304 Not Modified)
- ✅ Query optimization (select_related, prefetch_related)
- ✅ Database indexes

### SEO
- ✅ Full SEO metadata (seo, open_graph, twitter_card, schema_org)
- ✅ Absolute URLs
- ✅ Canonical URLs
- ✅ Cache-Control headers

### Security
- ✅ Rate limiting (5 comments/min)
- ✅ CORS configuration
- ✅ Input validation
- ✅ Email validation

---

## Testing

```bash
# Run all tests
pytest blog/tests/test_views.py

# Run with coverage
pytest --cov=blog.views blog/tests/test_views.py

# Run specific test
pytest blog/tests/test_views.py::PostViewSetTest
```

---

## Documentation

- **[phase-3-views.md](../docs/phase-3-views.md)** - Complete API documentation
- **[PHASE3_API_COMPLETE.md](../PHASE3_API_COMPLETE.md)** - Phase 3 summary

---

**Status: ✅ Phase 3 Complete**

Ready for Celery tasks (Phase 4).
