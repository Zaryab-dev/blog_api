# API Examples: Model Serialization Output

**Phase 2:** Database Models & Serializers  
**Date:** 2025

This document shows the exact JSON output from the implemented serializers.

---

## 1. AuthorSerializer

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Zaryab Khan",
  "slug": "zaryab-khan",
  "bio": "Leather expert and fashion writer with 10 years of experience.",
  "avatar_url": "https://cdn.zaryableather.com/authors/zaryab-khan-200w.webp",
  "twitter_handle": "zaryabkhan",
  "website": "https://zaryableather.com"
}
```

---

## 2. CategorySerializer

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "name": "Biker Jackets",
  "slug": "biker",
  "description": "Classic and modern biker jacket styles",
  "count_published_posts": 42
}
```

---

## 3. TagSerializer

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "name": "Bomber",
  "slug": "bomber",
  "description": "Bomber jacket style and trends",
  "count_published_posts": 15
}
```

---

## 4. ImageAssetSerializer

```json
{
  "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
  "width": 1600,
  "height": 900,
  "alt": "Black leather biker jacket on mannequin",
  "srcset": [
    {
      "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-320w.webp",
      "width": 320,
      "format": "webp"
    },
    {
      "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-768w.webp",
      "width": 768,
      "format": "webp"
    },
    {
      "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
      "width": 1600,
      "format": "webp"
    }
  ],
  "lqip": "data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA=",
  "webp_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
  "og_image_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp"
}
```

---

## 5. SEOSerializer (Computed)

```json
{
  "title": "Best Leather Jackets for Men in 2025 — Zaryab Leather Blog",
  "description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
  "meta_keywords": ["leather jacket", "men's fashion", "bomber", "biker"],
  "meta_robots": "index, follow"
}
```

**Fallback Logic:**
- `title`: Uses `seo_title` if set, else `{title} — {site_name}`
- `description`: Uses `seo_description` if set, else `summary`
- `meta_keywords`: Extracted from post tags
- `meta_robots`: "noindex, nofollow" if `allow_index=False`, else "index, follow"

---

## 6. OpenGraphSerializer (Computed)

```json
{
  "og_title": "Best Leather Jackets for Men in 2025",
  "og_description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
  "og_image": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp",
  "og_image_width": 1200,
  "og_image_height": 630,
  "og_type": "article",
  "og_url": "https://zaryableather.com/blog/best-leather-jackets-2025/"
}
```

**Fallback Logic:**
- `og_title`: Uses `og_title` → `seo_title` → `title`
- `og_description`: Uses `og_description` → `seo_description` → `summary`
- `og_image`: Uses `og_image` → `featured_image.og_image_url` → `featured_image.file.url`
- `og_url`: Uses `canonical_url` if set, else computed canonical

---

## 7. TwitterCardSerializer (Computed)

```json
{
  "card": "summary_large_image",
  "title": "Best Leather Jackets for Men in 2025",
  "description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
  "image": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp",
  "creator": "@zaryabkhan",
  "site": "@zaryableather"
}
```

**Fallback Logic:**
- `card`: "summary_large_image" if featured_image present, else "summary"
- `title`: Same as Open Graph
- `description`: Same as Open Graph
- `image`: Same as Open Graph
- `creator`: `@{author.twitter_handle}` if set

---

## 8. PostSlugSerializer (Minimal)

**Used for:** `/api/v1/posts/slugs/` endpoint

```json
{
  "slug": "best-leather-jackets-2025",
  "published_at": "2025-09-01T12:00:00Z",
  "last_modified": "2025-09-10T08:34:00Z",
  "canonical_url": "https://zaryableather.com/blog/best-leather-jackets-2025/",
  "status": "published"
}
```

---

## 9. PostListSerializer

**Used for:** `/api/v1/posts/` list endpoint

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Best Leather Jackets for Men in 2025",
  "slug": "best-leather-jackets-2025",
  "summary": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
  "featured_image": {
    "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-768w.webp",
    "width": 768,
    "height": 432,
    "alt": "Black leather biker jacket on mannequin",
    "srcset": [...],
    "lqip": "data:image/webp;base64,...",
    "webp_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-768w.webp",
    "og_image_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp"
  },
  "author": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Zaryab Khan",
    "slug": "zaryab-khan",
    "bio": "Leather expert and fashion writer.",
    "avatar_url": "https://cdn.zaryableather.com/authors/zaryab-khan-200w.webp",
    "twitter_handle": "zaryabkhan",
    "website": "https://zaryableather.com"
  },
  "categories": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Biker Jackets",
      "slug": "biker",
      "description": "Classic and modern biker jacket styles",
      "count_published_posts": 42
    }
  ],
  "tags": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "name": "Bomber",
      "slug": "bomber",
      "description": "Bomber jacket style",
      "count_published_posts": 15
    }
  ],
  "published_at": "2025-09-01T12:00:00Z",
  "reading_time": 8,
  "canonical_url": "https://zaryableather.com/blog/best-leather-jackets-2025/"
}
```

---

## 10. PostDetailSerializer (Full)

**Used for:** `/api/v1/posts/{slug}/` detail endpoint

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Best Leather Jackets for Men in 2025",
  "slug": "best-leather-jackets-2025",
  "summary": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
  "content_html": "<p>Leather jackets have been a timeless fashion staple...</p>",
  "content_markdown": null,
  "author": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Zaryab Khan",
    "slug": "zaryab-khan",
    "bio": "Leather expert and fashion writer with 10 years of experience.",
    "avatar_url": "https://cdn.zaryableather.com/authors/zaryab-khan-200w.webp",
    "twitter_handle": "zaryabkhan",
    "website": "https://zaryableather.com"
  },
  "categories": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Biker Jackets",
      "slug": "biker",
      "description": "Classic and modern biker jacket styles",
      "count_published_posts": 42
    }
  ],
  "tags": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "name": "Bomber",
      "slug": "bomber",
      "description": "Bomber jacket style and trends",
      "count_published_posts": 15
    }
  ],
  "featured_image": {
    "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
    "width": 1600,
    "height": 900,
    "alt": "Black leather biker jacket on mannequin",
    "srcset": [
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-320w.webp",
        "width": 320,
        "format": "webp"
      },
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-768w.webp",
        "width": 768,
        "format": "webp"
      },
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
        "width": 1600,
        "format": "webp"
      }
    ],
    "lqip": "data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA=",
    "webp_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
    "og_image_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp"
  },
  "seo": {
    "title": "Best Leather Jackets for Men in 2025 — Zaryab Leather Blog",
    "description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
    "meta_keywords": ["leather jacket", "men's fashion", "bomber", "biker"],
    "meta_robots": "index, follow"
  },
  "open_graph": {
    "og_title": "Best Leather Jackets for Men in 2025",
    "og_description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
    "og_image": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp",
    "og_image_width": 1200,
    "og_image_height": 630,
    "og_type": "article",
    "og_url": "https://zaryableather.com/blog/best-leather-jackets-2025/"
  },
  "twitter_card": {
    "card": "summary_large_image",
    "title": "Best Leather Jackets for Men in 2025",
    "description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
    "image": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp",
    "creator": "@zaryabkhan",
    "site": "@zaryableather"
  },
  "schema_org": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Best Leather Jackets for Men in 2025",
    "image": [
      "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp"
    ],
    "datePublished": "2025-09-01T12:00:00Z",
    "dateModified": "2025-09-10T08:34:00Z",
    "author": {
      "@type": "Person",
      "name": "Zaryab Khan",
      "url": "https://zaryableather.com/author/zaryab-khan/"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Zaryab Leather Blog",
      "logo": {
        "@type": "ImageObject",
        "url": "https://zaryableather.com/static/logo.png"
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": "https://zaryableather.com/blog/best-leather-jackets-2025/"
    },
    "isAccessibleForFree": true,
    "wordCount": 1850
  },
  "published_at": "2025-09-01T12:00:00Z",
  "last_modified": "2025-09-10T08:34:00Z",
  "status": "published",
  "allow_index": true,
  "reading_time": 8,
  "word_count": 1850,
  "canonical_url": "https://zaryableather.com/blog/best-leather-jackets-2025/",
  "product_references": [
    {
      "source": "shopify",
      "title": "Classic Bomber Leather Jacket",
      "url": "https://shop.zaryableather.com/products/classic-bomber",
      "price": "299.99",
      "currency": "USD",
      "image_url": "https://cdn.shopify.com/s/files/1/0123/4567/products/bomber.jpg"
    }
  ],
  "locale": "en"
}
```

---

## 11. CommentSerializer

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440010",
  "post": "550e8400-e29b-41d4-a716-446655440000",
  "parent": null,
  "name": "John Doe",
  "email": "john@example.com",
  "content": "Great article! Very informative.",
  "status": "approved",
  "created_at": "2025-09-11T10:30:00Z"
}
```

---

## 12. SubscriberSerializer

```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440011",
  "email": "subscriber@example.com",
  "verified": true,
  "subscribed_at": "2025-09-01T08:00:00Z"
}
```

---

## 13. SiteSettingsSerializer

```json
{
  "site_name": "Zaryab Leather Blog",
  "site_description": "Expert insights on leather fashion, care, and style",
  "site_url": "https://zaryableather.com",
  "default_meta_image": "https://cdn.zaryableather.com/default-og.webp",
  "default_title_template": "{title} — Zaryab Leather Blog",
  "robots_txt_url": "https://zaryableather.com/robots.txt",
  "sitemap_index_url": "https://zaryableather.com/sitemap.xml",
  "rss_feed_url": "https://zaryableather.com/rss.xml",
  "twitter_site": "@zaryableather",
  "facebook_app_id": "1234567890"
}
```

---

## 14. RedirectSerializer

```json
{
  "from_path": "/old-leather-guide/",
  "to_url": "https://zaryableather.com/blog/leather-care-guide/",
  "status_code": 301
}
```

---

## Serializer Usage in Views

### Example: Post Detail View

```python
from rest_framework import generics
from blog.models import Post
from blog.serializers import PostDetailSerializer

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags')
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
```

### Example: Post List View

```python
from rest_framework import generics
from blog.models import Post
from blog.serializers import PostListSerializer

class PostListView(generics.ListAPIView):
    queryset = Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags')
    serializer_class = PostListSerializer
    pagination_class = PageNumberPagination
```

---

## Computed Fields Logic

### SEO Title
1. If `post.seo_title` is set → use it
2. Else → `{post.title} — {site_settings.site_name}`

### SEO Description
1. If `post.seo_description` is set → use it
2. Else → use `post.summary`

### Open Graph Image
1. If `post.og_image` is set → use it
2. Else if `post.featured_image.og_image_url` exists → use it
3. Else if `post.featured_image.file.url` exists → use it
4. Else → use `site_settings.default_meta_image`

### Canonical URL
1. If `post.canonical_url` is set → use it
2. Else → `{SITE_URL}/blog/{post.slug}/`

### Meta Robots
1. If `post.allow_index` is False → "noindex, nofollow"
2. Else → "index, follow"

---

**End of API Examples**

These JSON structures match the Phase 1 API contract specifications and are ready for Next.js integration.
