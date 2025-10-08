# API Examples & Sample Responses

**Project:** Django Blog API → Next.js SSG  
**Version:** 1.0

This document contains complete sample API request/response examples for all endpoints.

---

## 1. GET /api/v1/posts/slugs/

**Purpose:** Fetch list of post slugs for incremental SSG builds

### Request

```http
GET /api/v1/posts/slugs/?since=2025-09-01T00:00:00Z&page_size=100 HTTP/1.1
Host: api.zaryableather.com
Accept: application/json
If-Modified-Since: Wed, 10 Sep 2025 08:00:00 GMT
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=3600
ETag: "a1b2c3d4e5f6"
Last-Modified: Wed, 10 Sep 2025 08:34:00 GMT
```

```json
{
  "count": 245,
  "next": "https://api.zaryableather.com/api/v1/posts/slugs/?since=2025-09-01T00:00:00Z&page_size=100&page=2",
  "previous": null,
  "results": [
    {
      "slug": "best-leather-jacket-2025",
      "published_at": "2025-09-01T12:00:00Z",
      "last_modified": "2025-09-10T08:34:00Z",
      "canonical_url": "https://zaryableather.com/blog/best-leather-jacket-2025/",
      "status": "published"
    },
    {
      "slug": "how-to-care-for-leather",
      "published_at": "2025-08-28T10:00:00Z",
      "last_modified": "2025-08-28T10:00:00Z",
      "canonical_url": "https://zaryableather.com/blog/how-to-care-for-leather/",
      "status": "published"
    },
    {
      "slug": "vintage-leather-jackets-guide",
      "published_at": "2025-08-25T14:30:00Z",
      "last_modified": "2025-09-05T16:20:00Z",
      "canonical_url": "https://zaryableather.com/blog/vintage-leather-jackets-guide/",
      "status": "published"
    }
  ]
}
```

### Response (304 Not Modified)

```http
HTTP/1.1 304 Not Modified
ETag: "a1b2c3d4e5f6"
Last-Modified: Wed, 10 Sep 2025 08:34:00 GMT
```

---

## 2. GET /api/v1/posts/{slug}/

**Purpose:** Fetch full post content and SEO metadata

### Request

```http
GET /api/v1/posts/best-leather-jacket-2025/ HTTP/1.1
Host: api.zaryableather.com
Accept: application/json
If-None-Match: "post-550e8400-2025-09-10T08:34:00Z"
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=300, s-maxage=3600
ETag: "post-550e8400-2025-09-10T08:34:00Z"
Last-Modified: Wed, 10 Sep 2025 08:34:00 GMT
```

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Best Leather Jackets for Men in 2025",
  "slug": "best-leather-jacket-2025",
  "summary": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets. Expert recommendations and buying guide.",
  "content_html": "<p>Leather jackets have been a timeless fashion staple for decades, and 2025 brings exciting new styles while honoring classic designs.</p><h2>Top Styles for 2025</h2><p>The bomber jacket continues to dominate...</p><h3>1. Classic Bomber Jacket</h3><p>The bomber remains the most versatile option...</p>",
  "content_markdown": null,
  "author": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Zaryab Khan",
    "slug": "zaryab-khan",
    "avatar_url": "https://cdn.zaryableather.com/authors/zaryab-khan-200w.webp",
    "bio": "Leather expert and fashion writer with 10 years of experience in the industry.",
    "twitter_handle": "zaryabkhan",
    "website": "https://zaryableather.com"
  },
  "categories": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Biker Jackets",
      "slug": "biker"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "name": "Men's Fashion",
      "slug": "mens-fashion"
    }
  ],
  "tags": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "name": "Bomber",
      "slug": "bomber"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440005",
      "name": "Style Guide",
      "slug": "style-guide"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440006",
      "name": "2025 Trends",
      "slug": "2025-trends"
    }
  ],
  "featured_image": {
    "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
    "width": 1600,
    "height": 900,
    "alt": "Black leather biker jacket displayed on mannequin with vintage motorcycle in background",
    "srcset": [
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-320w.webp",
        "width": 320,
        "format": "webp"
      },
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-480w.webp",
        "width": 480,
        "format": "webp"
      },
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-768w.webp",
        "width": 768,
        "format": "webp"
      },
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1024w.webp",
        "width": 1024,
        "format": "webp"
      },
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
        "width": 1600,
        "format": "webp"
      },
      {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-2048w.webp",
        "width": 2048,
        "format": "webp"
      }
    ],
    "lqip": "data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA=",
    "webp_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
    "jpeg_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.jpg",
    "og_image_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp"
  },
  "seo": {
    "title": "Best Leather Jackets for Men in 2025 — Zaryab Leather Blog",
    "description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets. Expert recommendations and buying guide.",
    "meta_keywords": [
      "leather jacket",
      "men's fashion",
      "bomber jacket",
      "biker jacket",
      "2025 trends"
    ],
    "meta_robots": "index, follow"
  },
  "open_graph": {
    "og_title": "Best Leather Jackets for Men in 2025",
    "og_description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
    "og_image": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp",
    "og_image_width": 1200,
    "og_image_height": 630,
    "og_type": "article",
    "og_url": "https://zaryableather.com/blog/best-leather-jacket-2025/"
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
      "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp",
      "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp"
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
        "url": "https://cdn.zaryableather.com/logo.png",
        "width": 600,
        "height": 60
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": "https://zaryableather.com/blog/best-leather-jacket-2025/"
    },
    "isAccessibleForFree": true,
    "wordCount": 1850,
    "articleBody": "Leather jackets have been a timeless fashion staple for decades..."
  },
  "published_at": "2025-09-01T12:00:00Z",
  "last_modified": "2025-09-10T08:34:00Z",
  "status": "published",
  "allow_index": true,
  "reading_time": 8,
  "word_count": 1850,
  "canonical_url": "https://zaryableather.com/blog/best-leather-jacket-2025/",
  "product_references": [
    {
      "source": "shopify",
      "title": "Classic Bomber Leather Jacket",
      "url": "https://shop.zaryableather.com/products/classic-bomber",
      "price": "299.99",
      "currency": "USD",
      "image_url": "https://cdn.shopify.com/s/files/1/0123/4567/products/bomber.jpg"
    },
    {
      "source": "ebay",
      "title": "Vintage Biker Jacket",
      "url": "https://www.ebay.com/itm/123456789",
      "price": "450.00",
      "currency": "USD",
      "image_url": "https://i.ebayimg.com/images/g/abc/s-l1600.jpg"
    }
  ],
  "locale": "en"
}
```

---

## 3. GET /api/v1/posts/

**Purpose:** List posts for blog index, category, tag, author pages

### Request

```http
GET /api/v1/posts/?page=1&page_size=20&category=biker&ordering=-published_at HTTP/1.1
Host: api.zaryableather.com
Accept: application/json
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=300
```

```json
{
  "count": 42,
  "next": "https://api.zaryableather.com/api/v1/posts/?page=2&page_size=20&category=biker",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Best Leather Jackets for Men in 2025",
      "slug": "best-leather-jacket-2025",
      "summary": "Discover the top leather jacket styles for men in 2025...",
      "featured_image": {
        "url": "https://cdn.zaryableather.com/images/2025/09/550e8400-768w.webp",
        "width": 768,
        "height": 432,
        "alt": "Black leather biker jacket on mannequin"
      },
      "author": {
        "name": "Zaryab Khan",
        "slug": "zaryab-khan",
        "avatar_url": "https://cdn.zaryableather.com/authors/zaryab-khan-200w.webp"
      },
      "categories": [
        {
          "name": "Biker Jackets",
          "slug": "biker"
        }
      ],
      "tags": [
        {
          "name": "Bomber",
          "slug": "bomber"
        },
        {
          "name": "Style Guide",
          "slug": "style-guide"
        }
      ],
      "published_at": "2025-09-01T12:00:00Z",
      "reading_time": 8,
      "canonical_url": "https://zaryableather.com/blog/best-leather-jacket-2025/"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440007",
      "title": "How to Break In a New Leather Jacket",
      "slug": "break-in-leather-jacket",
      "summary": "Learn the best techniques to break in your new leather jacket...",
      "featured_image": {
        "url": "https://cdn.zaryableather.com/images/2025/08/660e8400-768w.webp",
        "width": 768,
        "height": 432,
        "alt": "Person wearing new brown leather jacket"
      },
      "author": {
        "name": "Zaryab Khan",
        "slug": "zaryab-khan",
        "avatar_url": "https://cdn.zaryableather.com/authors/zaryab-khan-200w.webp"
      },
      "categories": [
        {
          "name": "Biker Jackets",
          "slug": "biker"
        }
      ],
      "tags": [
        {
          "name": "Care Guide",
          "slug": "care-guide"
        }
      ],
      "published_at": "2025-08-28T10:00:00Z",
      "reading_time": 5,
      "canonical_url": "https://zaryableather.com/blog/break-in-leather-jacket/"
    }
  ]
}
```

---

## 4. GET /api/v1/posts/{slug}/preview/

**Purpose:** Access draft/scheduled posts for preview mode

### Request

```http
GET /api/v1/posts/upcoming-leather-trends-2026/preview/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... HTTP/1.1
Host: api.zaryableather.com
Accept: application/json
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: private, no-cache, no-store
X-Robots-Tag: noindex, nofollow
```

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440008",
  "title": "Upcoming Leather Trends for 2026",
  "slug": "upcoming-leather-trends-2026",
  "summary": "Get a sneak peek at the leather fashion trends coming in 2026...",
  "content_html": "<p>As we look ahead to 2026...</p>",
  "status": "draft",
  "allow_index": false,
  "...": "... (same structure as regular post detail)"
}
```

### Response (401 Unauthorized)

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "error": "Invalid or expired preview token"
}
```

---

## 5. GET /api/v1/meta/site/

**Purpose:** Fetch global site settings

### Request

```http
GET /api/v1/meta/site/ HTTP/1.1
Host: api.zaryableather.com
Accept: application/json
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=86400
```

```json
{
  "site_name": "Zaryab Leather Blog",
  "site_description": "Expert insights on leather fashion, care, and style. Discover the latest trends, buying guides, and maintenance tips.",
  "site_url": "https://zaryableather.com",
  "default_meta_image": "https://cdn.zaryableather.com/default-og.webp",
  "default_title_template": "{title} — Zaryab Leather Blog",
  "default_description_template": "{summary} | Zaryab Leather Blog",
  "robots_txt_url": "https://zaryableather.com/robots.txt",
  "sitemap_index_url": "https://zaryableather.com/sitemap.xml",
  "rss_feed_url": "https://zaryableather.com/rss.xml",
  "twitter_site": "@zaryableather",
  "facebook_app_id": "1234567890",
  "google_site_verification": "abc123xyz789"
}
```

---

## 6. GET /api/v1/redirects/

**Purpose:** Fetch all active redirects for Next.js middleware

### Request

```http
GET /api/v1/redirects/ HTTP/1.1
Host: api.zaryableather.com
Accept: application/json
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: public, max-age=3600
```

```json
{
  "redirects": [
    {
      "from_path": "/old-leather-guide/",
      "to_url": "https://zaryableather.com/blog/leather-care-guide/",
      "status_code": 301
    },
    {
      "from_path": "/blog/2024/01/15/old-post/",
      "to_url": "https://zaryableather.com/blog/old-post/",
      "status_code": 301
    },
    {
      "from_path": "/articles/bomber-jackets/",
      "to_url": "https://zaryableather.com/category/bomber/",
      "status_code": 301
    }
  ]
}
```

---

## 7. GET /sitemap.xml

**Purpose:** Serve sitemap index

### Request

```http
GET /sitemap.xml HTTP/1.1
Host: zaryableather.com
Accept: application/xml
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/xml
Cache-Control: public, max-age=3600
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://cdn.zaryableather.com/sitemaps/posts-1.xml</loc>
    <lastmod>2025-09-10T08:34:00Z</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://cdn.zaryableather.com/sitemaps/posts-2.xml</loc>
    <lastmod>2025-09-08T14:20:00Z</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://cdn.zaryableather.com/sitemaps/categories.xml</loc>
    <lastmod>2025-09-01T10:00:00Z</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://cdn.zaryableather.com/sitemaps/tags.xml</loc>
    <lastmod>2025-08-25T16:45:00Z</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://cdn.zaryableather.com/sitemaps/authors.xml</loc>
    <lastmod>2025-08-20T12:00:00Z</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://cdn.zaryableather.com/sitemaps/static.xml</loc>
    <lastmod>2025-08-15T09:00:00Z</lastmod>
  </sitemap>
</sitemapindex>
```

---

## 8. GET /rss.xml

**Purpose:** Serve RSS feed

### Request

```http
GET /rss.xml HTTP/1.1
Host: zaryableather.com
Accept: application/rss+xml
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/rss+xml
Cache-Control: public, max-age=1800
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Zaryab Leather Blog</title>
    <link>https://zaryableather.com/blog/</link>
    <description>Expert insights on leather fashion, care, and style</description>
    <language>en</language>
    <lastBuildDate>Mon, 10 Sep 2025 08:34:00 GMT</lastBuildDate>
    <atom:link href="https://zaryableather.com/rss.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>https://cdn.zaryableather.com/logo.png</url>
      <title>Zaryab Leather Blog</title>
      <link>https://zaryableather.com/</link>
    </image>
    
    <item>
      <title>Best Leather Jackets for Men in 2025</title>
      <link>https://zaryableather.com/blog/best-leather-jacket-2025/</link>
      <guid isPermaLink="true">https://zaryableather.com/blog/best-leather-jacket-2025/</guid>
      <pubDate>Sun, 01 Sep 2025 12:00:00 GMT</pubDate>
      <description><![CDATA[Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.]]></description>
      <content:encoded><![CDATA[<p>Leather jackets have been a timeless fashion staple for decades...</p>]]></content:encoded>
      <author>zaryab@zaryableather.com (Zaryab Khan)</author>
      <category>Biker Jackets</category>
      <category>Men's Fashion</category>
      <enclosure url="https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp" type="image/webp" length="245760" />
    </item>
    
    <item>
      <title>How to Break In a New Leather Jacket</title>
      <link>https://zaryableather.com/blog/break-in-leather-jacket/</link>
      <guid isPermaLink="true">https://zaryableather.com/blog/break-in-leather-jacket/</guid>
      <pubDate>Wed, 28 Aug 2025 10:00:00 GMT</pubDate>
      <description><![CDATA[Learn the best techniques to break in your new leather jacket for maximum comfort.]]></description>
      <content:encoded><![CDATA[<p>Breaking in a new leather jacket requires patience...</p>]]></content:encoded>
      <author>zaryab@zaryableather.com (Zaryab Khan)</author>
      <category>Biker Jackets</category>
      <enclosure url="https://cdn.zaryableather.com/images/2025/08/660e8400-1600w.webp" type="image/webp" length="198432" />
    </item>
    
  </channel>
</rss>
```

---

## 9. POST /api/revalidate (Next.js Webhook)

**Purpose:** Trigger Next.js ISR revalidation

### Request

```http
POST /api/revalidate HTTP/1.1
Host: zaryableather.com
Content-Type: application/json
X-Signature: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

```json
{
  "slugs": ["best-leather-jacket-2025", "how-to-care-for-leather"],
  "paths": [
    "/blog/best-leather-jacket-2025",
    "/blog/how-to-care-for-leather",
    "/blog",
    "/category/biker",
    "/tag/bomber"
  ],
  "timestamp": "2025-09-10T08:34:00Z",
  "event": "post.published"
}
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "revalidated": true,
  "paths": [
    "/blog/best-leather-jacket-2025",
    "/blog/how-to-care-for-leather",
    "/blog",
    "/category/biker",
    "/tag/bomber"
  ]
}
```

### Response (401 Unauthorized)

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "error": "Invalid signature"
}
```

---

## 10. GET /robots.txt

**Purpose:** Serve robots.txt

### Request

```http
GET /robots.txt HTTP/1.1
Host: zaryableather.com
```

### Response (200 OK)

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Cache-Control: public, max-age=86400
```

```
User-agent: *
Allow: /

# Disallow admin and API endpoints
Disallow: /admin/
Disallow: /api/

# Disallow preview and draft pages
Disallow: /preview/
Disallow: /?preview_token=

# Sitemap
Sitemap: https://zaryableather.com/sitemap.xml
```

---

**End of API Examples**

For complete API contract details, see `/docs/phase-1-architecture.md`.
