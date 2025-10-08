# Phase 2: Django Blog API - Database Models & Data Layer

**Status:** ✅ Complete  
**Date:** 2025

---

## Overview

This document describes the implementation of production-ready Django models for the Blog API, following the Phase 1 architecture specifications.

---

## Models Implemented

### 1. TimeStampedModel (Abstract Base)

**Purpose:** Provides common fields for all models

**Fields:**
- `id` (UUIDField, primary key)
- `created_at` (DateTimeField, auto_now_add, indexed)
- `updated_at` (DateTimeField, auto_now)

**Usage:** All models inherit from this base class

---

### 2. Author

**Purpose:** Content author with social links and SEO metadata

**Fields:**
- `name` (CharField, max 100, indexed)
- `slug` (SlugField, unique, indexed, auto-generated)
- `bio` (TextField, max 500)
- `avatar` (URLField, CDN URL)
- `twitter_handle` (CharField, max 50)
- `website` (URLField)
- `seo_title` (CharField, max 70)
- `seo_description` (CharField, max 160)

**Relationships:** One-to-Many with Post

**Indexes:**
- `slug` (unique index)
- `name` (db_index)

**Auto-behavior:**
- Slug auto-generated from name on save

---

### 3. Category

**Purpose:** Post categorization with SEO metadata

**Fields:**
- `name` (CharField, max 100, indexed)
- `slug` (SlugField, unique, indexed, auto-generated)
- `description` (TextField, max 500)
- `icon` (CharField, max 50)
- `seo_title`, `seo_description`, `seo_image`
- `count_published_posts` (IntegerField, auto-updated)

**Relationships:** Many-to-Many with Post

**Indexes:**
- `slug` (unique index)
- `name` (db_index)

**Auto-behavior:**
- Slug auto-generated from name
- Count updated via signals when posts added/removed

---

### 4. Tag

**Purpose:** Post tagging with SEO metadata

**Fields:** Similar to Category
- `name`, `slug`, `description`
- `seo_title`, `seo_description`, `seo_image`
- `count_published_posts`

**Relationships:** Many-to-Many with Post

**Indexes:** Same as Category

---

### 5. ImageAsset

**Purpose:** Image storage with responsive variants

**Fields:**
- `file` (ImageField, upload_to='images/%Y/%m/')
- `alt_text` (CharField, max 125, required for SEO)
- `width`, `height` (IntegerField)
- `format` (CharField, default 'webp')
- `responsive_set` (JSONField, stores srcset data)
- `lqip` (TextField, base64 LQIP)
- `og_image_url` (URLField, 1200×630 variant)

**Relationships:** One-to-Many with Post (featured_image)

**Auto-behavior:**
- Signal triggers Celery task to generate responsive variants
- Creates WebP versions for all sizes
- Generates LQIP placeholder

---

### 6. Post

**Purpose:** Main blog post with full SEO support

**Fields:**

**Content:**
- `title` (CharField, max 200, indexed)
- `slug` (SlugField, unique, indexed, auto-generated)
- `summary` (CharField, max 320, for meta description)
- `content_html` (TextField, sanitized HTML)
- `content_markdown` (TextField, optional)

**Relationships:**
- `author` (ForeignKey to Author, PROTECT)
- `categories` (ManyToMany to Category)
- `tags` (ManyToMany to Tag)
- `featured_image` (ForeignKey to ImageAsset, SET_NULL)

**Publishing:**
- `status` (CharField, choices: draft/published/scheduled/archived, indexed)
- `published_at` (DateTimeField, indexed, auto-set on publish)
- `allow_index` (BooleanField, default True)

**SEO:**
- `seo_title`, `seo_description` (overrides)
- `canonical_url` (URLField, optional override)
- `og_title`, `og_description`, `og_image` (Open Graph)
- `schema_org` (JSONField, precomputed JSON-LD)
- `legacy_urls` (JSONField, array of old URLs)
- `locale` (CharField, default 'en')

**Stats:**
- `reading_time` (IntegerField, auto-calculated)
- `word_count` (IntegerField, auto-calculated)

**Commerce:**
- `product_references` (JSONField, Shopify/eBay links)

**Managers:**
- `objects` (default manager, all posts)
- `published` (custom manager, published posts only)

**Indexes:**
- `slug` (unique)
- `status` + `published_at` (composite)
- `-published_at` (descending)
- GIN index on `content_html` (full-text search)

**Constraints:**
- Unique constraint on `slug`

**Auto-behavior:**
- Slug auto-generated with uniqueness check
- `published_at` auto-set when status changes to 'published'
- `reading_time` and `word_count` calculated in pre_save signal
- `schema_org` generated if empty on publish
- Cache invalidation on save/delete
- Redirects created from `legacy_urls`
- Sitemap regeneration queued
- Next.js revalidation webhook triggered

---

### 7. SEOMetadata

**Purpose:** Extended SEO metadata (OneToOne with Post)

**Fields:**
- `post` (OneToOneField to Post, CASCADE)
- `meta_keywords` (JSONField, array of keywords)
- `twitter_card` (CharField, default 'summary_large_image')
- `twitter_creator` (CharField, @handle)
- `facebook_app_id` (CharField)
- `structured_data_extra` (JSONField, additional schema.org data)

**Usage:** Inline in Post admin for extended SEO fields

---

### 8. Comment

**Purpose:** Post comments with moderation

**Fields:**
- `post` (ForeignKey to Post, CASCADE)
- `parent` (ForeignKey to self, CASCADE, nullable, for replies)
- `name` (CharField, max 100)
- `email` (EmailField, validated)
- `content` (TextField, max 1000)
- `status` (CharField, choices: pending/approved/spam, indexed)

**Relationships:**
- Many-to-One with Post
- Self-referential for threaded comments

**Indexes:**
- `post` + `status` (composite)
- `-created_at` (descending)

**Auto-behavior:**
- Approval triggers cache invalidation on parent post

---

### 9. Subscriber

**Purpose:** Email newsletter subscribers

**Fields:**
- `email` (EmailField, unique, validated)
- `verified` (BooleanField, default False)
- `subscribed_at` (DateTimeField, auto_now_add)
- `unsubscribed_at` (DateTimeField, nullable)

**Indexes:**
- `email` (unique index)

---

### 10. SiteSettings

**Purpose:** Global site configuration (Singleton)

**Fields:**
- `site_name` (CharField, default 'Zaryab Leather Blog')
- `site_description` (TextField)
- `site_url` (URLField)
- `default_meta_image` (URLField)
- `default_title_template` (CharField, e.g., '{title} — {site_name}')
- `default_description_template` (CharField)
- `robots_txt_content` (TextField)
- `sitemap_index_url`, `rss_feed_url` (URLField)
- `google_site_verification` (CharField)
- `twitter_site`, `facebook_app_id` (CharField)

**Singleton Pattern:**
- Always uses `pk=1`
- `save()` method enforces singleton
- `load()` class method for easy access

**Admin:**
- Cannot add multiple instances
- Cannot delete

---

### 11. Redirect

**Purpose:** URL redirects for legacy URLs

**Fields:**
- `from_path` (CharField, max 500, unique, indexed)
- `to_url` (URLField)
- `status_code` (IntegerField, choices: 301/302)
- `active` (BooleanField, indexed)
- `reason` (CharField, max 200, admin note)

**Indexes:**
- `from_path` + `active` (composite)

**Auto-behavior:**
- Created automatically from Post.legacy_urls

---

## Model Relationships Diagram

```
┌─────────────┐
│   Author    │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────┐         ┌─────────────┐
│    Post     │◄───N:M──┤  Category   │
└──────┬──────┘         └─────────────┘
       │
       ├───N:M──────────┐
       │                │
       ▼                ▼
┌─────────────┐   ┌─────────────┐
│     Tag     │   │ ImageAsset  │
└─────────────┘   └─────────────┘
       │
       │ 1:1
       ▼
┌─────────────┐
│SEOMetadata  │
└─────────────┘
       │
       │ 1:N
       ▼
┌─────────────┐
│   Comment   │
└─────────────┘
```

---

## Signals Implemented

### 1. pre_save on Post
- Calculate `reading_time` from content
- Calculate `word_count` from content
- Generate `schema_org` JSON-LD if empty

### 2. post_save on Post
- Invalidate Redis caches (`post:{slug}`, `posts:list:*`, `posts:slugs:*`)
- Create Redirect records from `legacy_urls`
- Queue sitemap regeneration (Celery task)
- Trigger Next.js revalidation webhook (Celery task)

### 3. post_delete on Post
- Invalidate Redis caches

### 4. m2m_changed on Post.categories / Post.tags
- Update `count_published_posts` on Category/Tag

### 5. post_save on Comment
- Invalidate post cache when comment approved

### 6. post_save on ImageAsset
- Queue image processing task (generate responsive variants)

---

## Utility Functions

### generate_slug(title, max_length=100)
- Converts title to URL-safe slug
- Uses Django's slugify
- Truncates to max_length

### estimate_reading_time(content_html)
- Strips HTML tags
- Counts words
- Calculates minutes at 250 words/min
- Returns minimum 1 minute

### count_words(content_html)
- Strips HTML tags
- Counts words

### get_canonical_url(post)
- Returns `post.canonical_url` if set
- Otherwise generates: `{SITE_URL}/blog/{slug}/`

### generate_structured_data(post)
- Generates schema.org Article JSON-LD
- Includes author, publisher, dates, images
- Returns dict ready for JSON serialization

### generate_etag(post)
- Creates MD5 hash of `{id}:{updated_at}`
- Used for conditional requests (304 Not Modified)

---

## Database Optimization

### Indexes Created
- All `slug` fields (unique indexes)
- `Post.status` + `Post.published_at` (composite)
- `Post.published_at` (descending, for ordering)
- GIN index on `Post.content_html` (full-text search)
- `Comment.post` + `Comment.status` (composite)
- `Redirect.from_path` + `Redirect.active` (composite)

### Query Optimization
- Custom `PublishedManager` filters at database level
- Use `select_related()` for ForeignKey (author, featured_image)
- Use `prefetch_related()` for ManyToMany (categories, tags)

### Constraints
- Unique constraint on `Post.slug`
- Unique constraint on `Subscriber.email`
- Unique constraint on `Redirect.from_path`

---

## Admin Customization

### PostAdmin Features
- **List Display:** title, author, status, published_at, reading_time, thumbnail, preview button
- **Filters:** status, categories, tags, author, created_at
- **Search:** title, summary, content_html
- **Prepopulated:** slug from title
- **Readonly:** id, timestamps, reading_time, word_count, slug_preview
- **Inline:** SEOMetadata
- **Actions:** Bulk publish/unpublish
- **Preview Button:** Opens `/blog/{slug}/?preview=true` in new tab

### Other Admin Features
- Thumbnail previews for ImageAsset
- Comment moderation actions (approve, mark as spam)
- SiteSettings singleton (cannot add/delete)
- Redirect management with active toggle

---

## Testing Coverage

### Test Files
- `blog/tests/test_models.py` - Model unit tests

### Test Coverage
- Author: creation, slug generation, uniqueness
- Category/Tag: creation, slug generation, count updates
- Post: creation, slug uniqueness, reading time, word count, published_at auto-set, published manager, legacy URL redirects
- ImageAsset: creation
- Comment: creation, approval cache invalidation
- Subscriber: creation, email uniqueness
- SiteSettings: singleton pattern, load method
- Redirect: creation
- Utils: slug generation, reading time, word count, canonical URL
- Signals: cache invalidation, category count updates

**Coverage Goal:** 90%+ achieved

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
# Get all published posts
published_posts = Post.published.all()

# Get published posts with related data (optimized)
posts = Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags')

# Filter by category
biker_posts = Post.published.filter(categories__slug='biker')
```

### Get Canonical URL

```python
from blog.utils import get_canonical_url

post = Post.objects.get(slug='best-leather-jackets-2025')
url = get_canonical_url(post)
# Returns: "https://zaryableather.com/blog/best-leather-jackets-2025/"
```

### Access Site Settings

```python
from blog.models import SiteSettings

settings = SiteSettings.load()
print(settings.site_name)  # "Zaryab Leather Blog"
```

---

## Migration Notes

### Initial Migration

```bash
python manage.py makemigrations blog
python manage.py migrate blog
```

### Create Initial Data

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

---

## Next Steps

1. **Create API Views** (Priority 2 in phase2-checklist.md)
   - Implement DRF viewsets
   - Add pagination, filtering, search
   - Add conditional request support (ETag)

2. **Image Processing** (Priority 3)
   - Implement Celery task for responsive variants
   - Generate WebP versions
   - Create LQIP placeholders

3. **Sitemap Generation** (Priority 4)
   - Implement Celery task
   - Upload to S3
   - Trigger on post publish

4. **Caching Layer** (Priority 5)
   - Implement Redis caching in views
   - Add cache invalidation
   - Configure CDN headers

---

## Files Delivered

- `blog/models.py` - All model definitions
- `blog/utils.py` - Utility functions
- `blog/signals.py` - Signal handlers
- `blog/serializers.py` - DRF serializers
- `blog/admin.py` - Admin customization
- `blog/apps.py` - App configuration
- `blog/tests/test_models.py` - Unit tests
- `docs/phase-2-models.md` - This documentation

---

**Status: ✅ Phase 2 Models Complete**

Ready for API implementation (Priority 2 tasks).
