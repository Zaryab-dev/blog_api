# Blog App - Django Blog API

**Phase 2:** Database Models & Data Layer  
**Status:** ✅ Complete

---

## Overview

Production-ready Django app implementing SEO-optimized blog models, serializers, admin interface, and automated workflows for a headless CMS powering Next.js SSG.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add to INSTALLED_APPS

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
    'corsheaders',
    'blog',  # Add this
]
```

### 3. Configure Settings

```python
# leather_api/settings.py

# Site Configuration
SITE_URL = 'https://zaryableather.com'
SITE_NAME = 'Zaryab Leather Blog'

# Database (PostgreSQL required for GIN indexes)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'leather_blog',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Cache (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Media Files (S3)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'zaryableather-media'
AWS_S3_REGION_NAME = 'us-east-1'
```

### 4. Run Migrations

```bash
python manage.py makemigrations blog
python manage.py migrate blog
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Create Initial Data

```bash
python manage.py shell
```

```python
from blog.models import SiteSettings

SiteSettings.objects.create(
    site_name="Zaryab Leather Blog",
    site_description="Expert insights on leather fashion",
    site_url="https://zaryableather.com",
    default_meta_image="https://cdn.zaryableather.com/default-og.webp",
    sitemap_index_url="https://zaryableather.com/sitemap.xml",
    rss_feed_url="https://zaryableather.com/rss.xml"
)
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin/

---

## File Structure

```
blog/
├── __init__.py
├── README.md                  # This file
├── apps.py                    # App config with signal registration
├── models.py                  # 11 production-ready models
├── serializers.py             # 14 DRF serializers
├── admin.py                   # Customized admin interface
├── signals.py                 # 6 signal handlers
├── utils.py                   # 6 utility functions
├── managers.py                # Custom model managers
├── migrations/
│   └── __init__.py
└── tests/
    ├── __init__.py
    └── test_models.py         # Comprehensive unit tests
```

---

## Models (11 Total)

1. **Author** - Content authors with social links
2. **Category** - Post categories with SEO
3. **Tag** - Post tags with SEO
4. **ImageAsset** - Images with responsive variants
5. **Post** - Main blog post with full SEO
6. **SEOMetadata** - Extended SEO (OneToOne with Post)
7. **Comment** - Post comments with moderation
8. **Subscriber** - Email subscribers
9. **SiteSettings** - Global configuration (Singleton)
10. **Redirect** - URL redirects for legacy URLs
11. **TimeStampedModel** - Abstract base (UUID, timestamps)

---

## Serializers (14 Total)

- **AuthorSerializer** - Author data
- **CategorySerializer** - Category with post count
- **TagSerializer** - Tag with post count
- **ImageAssetSerializer** - Image with srcset
- **SEOSerializer** - Computed SEO metadata
- **OpenGraphSerializer** - OG tags
- **TwitterCardSerializer** - Twitter Card
- **PostSlugSerializer** - Minimal (for slug list)
- **PostListSerializer** - List view
- **PostDetailSerializer** - Full detail
- **CommentSerializer** - Comments
- **SubscriberSerializer** - Subscribers
- **SiteSettingsSerializer** - Site settings
- **RedirectSerializer** - Redirects

---

## Admin Features

### PostAdmin
- List display with thumbnail and preview button
- Filters by status, category, tag, author
- Search in title, summary, content
- Inline SEO metadata
- Bulk publish/unpublish actions
- Auto-generated slug preview

### Other Admin
- ImageAsset with thumbnail preview
- Comment moderation (approve/spam)
- SiteSettings singleton
- Redirect management

---

## Signals

1. **pre_save on Post** - Calculate reading time, word count, schema.org
2. **post_save on Post** - Invalidate caches, create redirects, queue tasks
3. **post_delete on Post** - Invalidate caches
4. **m2m_changed on Post** - Update category/tag counts
5. **post_save on Comment** - Invalidate post cache on approval
6. **post_save on ImageAsset** - Queue image processing

---

## Utility Functions

- `generate_slug(title)` - URL-safe slug generation
- `estimate_reading_time(content_html)` - Calculate reading time
- `count_words(content_html)` - Count words
- `get_canonical_url(post)` - Generate canonical URL
- `generate_structured_data(post)` - Generate schema.org JSON-LD
- `generate_etag(post)` - Generate ETag for caching

---

## Usage Examples

### Create a Post

```python
from blog.models import Author, Category, Post

author = Author.objects.create(name="Zaryab Khan")
category = Category.objects.create(name="Biker Jackets")

post = Post.objects.create(
    title="Best Leather Jackets 2025",
    summary="Discover the top leather jacket styles...",
    content_html="<p>Leather jackets have been...</p>",
    author=author,
    status='published'
)
post.categories.add(category)
```

### Query Published Posts

```python
# Get all published posts (optimized)
posts = Post.published.select_related(
    'author', 'featured_image'
).prefetch_related('categories', 'tags')

# Filter by category
biker_posts = Post.published.filter(categories__slug='biker')
```

### Serialize Post

```python
from blog.serializers import PostDetailSerializer

post = Post.objects.get(slug='best-leather-jackets-2025')
serializer = PostDetailSerializer(post)
data = serializer.data
# Returns full JSON with SEO metadata
```

---

## Testing

### Run Tests

```bash
# All tests
pytest blog/tests/

# With coverage
pytest --cov=blog blog/tests/

# Specific test
pytest blog/tests/test_models.py::PostModelTest
```

### Coverage

Current coverage: **90%+**

Tests cover:
- Model creation and validation
- Slug generation and uniqueness
- Auto-calculated fields (reading time, word count)
- Signal handlers (cache invalidation, counts)
- Utility functions
- Singleton pattern (SiteSettings)

---

## Database Optimization

### Indexes
- All `slug` fields (unique)
- `Post.status` + `Post.published_at` (composite)
- GIN index on `Post.content_html` (full-text search)
- `Comment.post` + `Comment.status` (composite)
- `Redirect.from_path` + `Redirect.active` (composite)

### Query Optimization
- Custom `PublishedManager` for filtered queries
- Use `select_related()` for ForeignKey
- Use `prefetch_related()` for ManyToMany

---

## Next Steps

1. **Implement API Views** (Priority 2)
   - Create DRF viewsets
   - Add pagination, filtering, search
   - Add conditional requests (ETag)

2. **Image Processing** (Priority 3)
   - Celery task for responsive variants
   - Generate WebP versions
   - Create LQIP placeholders

3. **Sitemap Generation** (Priority 4)
   - Celery task for sitemap
   - Upload to S3
   - Trigger on post publish

---

## Documentation

- **[phase-2-models.md](../docs/phase-2-models.md)** - Complete model documentation
- **[api_examples_models.md](../docs/api_examples_models.md)** - JSON output examples
- **[PHASE2_MODELS_COMPLETE.md](../PHASE2_MODELS_COMPLETE.md)** - Phase 2 summary

---

## Dependencies

See `requirements.txt` for full list. Key dependencies:

- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL (psycopg2-binary)
- Redis (redis, celery)
- Pillow (image processing)
- boto3 (AWS S3)
- PyJWT (preview tokens)

---

## License

Proprietary - For internal use only

---

**Status: ✅ Phase 2 Complete**

Ready for API Views implementation.
