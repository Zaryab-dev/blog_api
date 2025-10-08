# Phase 1: SEO Strategy & Project Architecture
## Django Blog API → Next.js SSG/ISR

**Version:** 1.0  
**Date:** 2025  
**Project:** Leather Blog Headless CMS  
**Target:** Production-grade, SEO-first, scale-ready

---

## Table of Contents

1. [High-Level Site Architecture](#1-high-level-site-architecture)
2. [SEO Content Model](#2-seo-content-model)
3. [API Contract for Next.js SSG/ISR](#3-api-contract-for-nextjs-ssgisr)
4. [SEO & Structured Data Rules](#4-seo--structured-data-rules)
5. [Image & Media Strategy](#5-image--media-strategy)
6. [Sitemap / Robots / RSS Plan](#6-sitemap--robots--rss-plan)
7. [Caching, Conditional Requests & ISR Hooks](#7-caching-conditional-requests--isr-hooks)
8. [Preview Tokens & Staging](#8-preview-tokens--staging)
9. [Redirects & Legacy URLs](#9-redirects--legacy-urls)
10. [Search & Discovery](#10-search--discovery)
11. [Monitoring, Logging & Analytics](#11-monitoring-logging--analytics)
12. [Security & Rate Limiting](#12-security--rate-limiting)
13. [CI/CD & Deployment Hooks](#13-cicd--deployment-hooks)
14. [Acceptance Criteria](#14-acceptance-criteria)
15. [How to Use This Document](#15-how-to-use-this-document)

---

## 1. High-Level Site Architecture

### 1.1 Canonical URL Scheme

**Canonical site root:** `https://zaryableather.com/`

**Chosen URL patterns:**

- **Blog index:** `https://zaryableather.com/blog/` (paginated)
- **Post pages:** `https://zaryableather.com/blog/{slug}/`
- **Tag pages:** `https://zaryableather.com/tag/{tag-slug}/` (paginated)
- **Category pages:** `https://zaryableather.com/category/{category-slug}/` (paginated)
- **Author pages:** `https://zaryableather.com/author/{author-slug}/` (paginated)
- **Archive pages:** `https://zaryableather.com/archive/{year}/` (paginated)
- **Product landing:** External absolute URLs to Shopify/eBay (rendered as preview cards in Next.js)

**Pagination strategy:** Query parameter `?page=2`

### 1.2 URL Pattern Justification

**Post URL choice: `/blog/{slug}/` (NOT `/blog/{yyyy}/{mm}/{dd}/{slug}/`)**

**Reasoning:**
- Shorter URLs are easier to share and remember
- Date-based URLs create unnecessary depth and can make content appear dated
- Publish date is still exposed via schema.org `datePublished` and `dateModified` for SEO
- Allows content to remain evergreen (e.g., "Best Leather Jackets 2025" can be updated without URL change)
- Reduces redirect complexity when republishing or updating dates

**Pagination choice: Query parameter `?page=2` (NOT `/page/2/`)**

**Reasoning:**
- Simpler to implement in both Django and Next.js
- Standard practice for REST APIs
- Easier to handle with Next.js dynamic routes and query params
- Canonical tag points to page 1 (without query param) for all paginated pages
- Use `rel="next"` and `rel="prev"` for pagination discovery

### 1.3 Site Tree Diagram

```
zaryableather.com/
│
├── /                          (Homepage)
│
├── /blog/                     (Blog index, paginated ?page=N)
│   └── /{slug}/               (Individual post)
│
├── /category/
│   └── /{category-slug}/      (Category archive, paginated ?page=N)
│
├── /tag/
│   └── /{tag-slug}/           (Tag archive, paginated ?page=N)
│
├── /author/
│   └── /{author-slug}/        (Author archive, paginated ?page=N)
│
├── /archive/
│   └── /{year}/               (Year archive, paginated ?page=N)
│
├── /sitemap.xml               (Sitemap index)
├── /robots.txt                (Robots file)
└── /rss.xml                   (RSS feed)
```

### 1.4 Slug Rules

**Uniqueness:** Slugs must be globally unique across all posts (not scoped by date or category).

**Allowed characters:**
- Lowercase letters: `a-z`
- Numbers: `0-9`
- Hyphens: `-` (not at start or end)
- No spaces, underscores, or special characters

**Length:** 3–100 characters

**Generation rules:**
- Auto-generate from title on creation
- Transliterate non-ASCII characters (e.g., "Café" → "cafe")
- Remove stop words for shorter slugs (optional)
- Ensure uniqueness by appending `-2`, `-3`, etc., if collision occurs

**Validation:** Backend must validate slug format and uniqueness before save.

### 1.5 Canonical Tag Rules

**Post pages:**
- Canonical URL: `https://zaryableather.com/blog/{slug}/`
- If `canonical_url` field is set in Post model, use that value (for cross-posting scenarios)
- Always use trailing slash

**Paginated pages (blog index, category, tag, author, archive):**
- Page 1: Canonical points to base URL without query param (e.g., `/blog/`)
- Page 2+: Canonical points to self (e.g., `/blog/?page=2`)
- Include `rel="next"` on page 1, 2, etc., pointing to next page
- Include `rel="prev"` on page 2, 3, etc., pointing to previous page
- Do NOT include `rel="prev"` on page 1

**Example for `/blog/?page=2`:**
```html
<link rel="canonical" href="https://zaryableather.com/blog/?page=2" />
<link rel="prev" href="https://zaryableather.com/blog/" />
<link rel="next" href="https://zaryableather.com/blog/?page=3" />
```

### 1.6 Redirect Strategy

**Redirect model:** Store legacy URLs and map to new canonical URLs.

**Implementation:**
- Django API exposes `/api/v1/redirects/` endpoint returning all active redirects
- Next.js middleware or CDN (Cloudflare/Vercel) handles 301 redirects
- On post publish/update, if `legacy_urls` array is populated, create Redirect records automatically

**Redirect priority:**
1. Exact path match (highest priority)
2. Pattern match (if implementing regex redirects in Phase 3)
3. 404 fallback

**Status codes:**
- 301 (Permanent) for legacy URLs
- 302 (Temporary) for maintenance or A/B testing

---

## 2. SEO Content Model

### 2.1 Post Model

**Purpose:** Primary content entity for blog articles.

| Field Name | Type | Required | SEO Purpose |
|------------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `title` | String (200) | Yes | Used in `<title>` tag and schema.org `headline` |
| `slug` | String (100) | Yes | URL component, must be unique |
| `summary` | Text (320) | Yes* | Fallback for meta description if `seo_description` empty |
| `content_html` | Text | Yes | Sanitized HTML content to render |
| `content_markdown` | Text | No | Original markdown (optional storage) |
| `author` | Object | Yes | `{id, name, slug, avatar_url}` |
| `categories` | Array | No | `[{id, name, slug}]` |
| `tags` | Array | No | `[{id, name, slug}]` |
| `featured_image` | Object | Yes* | `{url, width, height, alt, srcset[], lqip, webp_url}` |
| `seo_title` | String (70) | No | Override default title template |
| `seo_description` | String (160) | No | Override default meta description |
| `canonical_url` | URL | No | Override computed canonical (for syndication) |
| `published_at` | DateTime (ISO8601+TZ) | Yes* | Publication timestamp (UTC) |
| `last_modified` | DateTime (ISO8601+TZ) | Yes | Auto-updated on save |
| `status` | Enum | Yes | `draft`, `published`, `scheduled`, `archived` |
| `allow_index` | Boolean | Yes | Default `true`; if `false`, emit `noindex, nofollow` |
| `reading_time` | Integer | Yes | Precomputed reading time in minutes |
| `word_count` | Integer | Yes | Precomputed word count |
| `product_references` | Array | No | `[{source, title, url, price, image_url}]` |
| `og_title` | String (70) | No | Override Open Graph title |
| `og_description` | String (200) | No | Override Open Graph description |
| `og_image` | URL | No | Override Open Graph image |
| `schema_org` | JSON | Yes | Precomputed JSON-LD Article schema |
| `legacy_urls` | Array | No | `["/old-path-1/", "/old-path-2/"]` |
| `locale` | String (5) | Yes | Default `en`, for future i18n |

**Required fields marked with * are required only for published posts.**

### 2.2 Category Model

| Field Name | Type | Required | SEO Purpose |
|------------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `name` | String (100) | Yes | Display name |
| `slug` | String (100) | Yes | URL component, unique |
| `description` | Text (500) | No | Used in meta description for category pages |
| `seo_title` | String (70) | No | Override title for category page |
| `seo_description` | String (160) | No | Override meta description |
| `seo_image` | URL | No | Override OG image for category page |
| `count_published_posts` | Integer | Yes | Cached count for display |

### 2.3 Tag Model

| Field Name | Type | Required | SEO Purpose |
|------------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `name` | String (100) | Yes | Display name |
| `slug` | String (100) | Yes | URL component, unique |
| `description` | Text (500) | No | Used in meta description for tag pages |
| `seo_title` | String (70) | No | Override title for tag page |
| `seo_description` | String (160) | No | Override meta description |
| `seo_image` | URL | No | Override OG image for tag page |
| `count_published_posts` | Integer | Yes | Cached count for display |

### 2.4 Author Model

| Field Name | Type | Required | SEO Purpose |
|------------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `name` | String (100) | Yes | Display name |
| `slug` | String (100) | Yes | URL component, unique |
| `bio` | Text (500) | No | Author biography |
| `avatar_url` | URL | No | Author avatar (absolute CDN URL) |
| `twitter_handle` | String (50) | No | Twitter username (without @) |
| `website` | URL | No | Author website |
| `seo_title` | String (70) | No | Override title for author page |
| `seo_description` | String (160) | No | Override meta description |

### 2.5 SiteSettings Model (Singleton)

| Field Name | Type | Required | Purpose |
|------------|------|----------|---------|
| `site_name` | String (100) | Yes | "Zaryab Leather Blog" |
| `site_description` | Text (200) | Yes | Default meta description |
| `site_url` | URL | Yes | `https://zaryableather.com` (no trailing slash) |
| `default_meta_image` | URL | Yes | Fallback OG image |
| `default_title_template` | String (100) | Yes | `{title} — {site_name}` |
| `default_description_template` | String (200) | No | Template for auto-generated descriptions |
| `robots_txt_content` | Text | Yes | Editable robots.txt content |
| `sitemap_index_url` | URL | Yes | `https://zaryableather.com/sitemap.xml` |
| `rss_feed_url` | URL | Yes | `https://zaryableather.com/rss.xml` |
| `google_site_verification` | String (100) | No | Google Search Console verification code |
| `twitter_site` | String (50) | No | Site Twitter handle |
| `facebook_app_id` | String (50) | No | Facebook App ID for OG |

### 2.6 Redirect Model

| Field Name | Type | Required | Purpose |
|------------|------|----------|---------|
| `id` | UUID | Yes | Unique identifier |
| `from_path` | String (500) | Yes | Legacy path (e.g., `/old-post/`) |
| `to_url` | URL | Yes | Target canonical URL (absolute) |
| `status_code` | Integer | Yes | `301` or `302` |
| `active` | Boolean | Yes | Enable/disable redirect |
| `reason` | String (200) | No | Admin note (e.g., "URL restructure 2025") |
| `created_at` | DateTime | Yes | Timestamp |

---

## 3. API Contract for Next.js SSG/ISR

### 3.1 Endpoint: GET /api/v1/posts/slugs/

**Purpose:** Provide compact list of slugs and timestamps for incremental SSG builds.

**Method:** GET

**Query Parameters:**
- `since` (optional, ISO8601 datetime): Return only posts modified since this timestamp
- `page_size` (optional, integer, default 1000): Number of results per page
- `status` (optional, default `published`): Filter by status

**Request Headers:**
- `If-Modified-Since` (optional): Return 304 if no changes since timestamp
- `Accept: application/json`

**Response Headers:**
- `Content-Type: application/json`
- `Cache-Control: public, max-age=3600` (1 hour TTL)
- `ETag: "..."` (hash of result set)
- `Last-Modified: ...` (timestamp of most recent post modification)

**Response Status:**
- `200 OK`: Success
- `304 Not Modified`: No changes since If-Modified-Since
- `400 Bad Request`: Invalid query parameters

**Sample Response:**
```json
{
  "count": 1234,
  "next": "https://api.zaryableather.com/api/v1/posts/slugs/?page_size=1000&since=2025-09-01T00:00:00Z&page=2",
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
    }
  ]
}
```

**Caching Strategy:**
- Redis cache key: `posts:slugs:{since}:{page_size}:{page}`
- TTL: 3600 seconds (1 hour)
- Invalidate on any post publish/update

**Performance Requirements:**
- Must return in <200ms for 1000 slugs
- Database query should use index on `last_modified` and `status`

---

### 3.2 Endpoint: GET /api/v1/posts/{slug}/

**Purpose:** Return full post content and SEO metadata for SSG page generation.

**Method:** GET

**Path Parameters:**
- `slug` (required, string): Post slug

**Query Parameters:**
- `preview_token` (optional, string): Token for accessing draft/scheduled posts

**Request Headers:**
- `If-Modified-Since` (optional): Return 304 if post unchanged
- `If-None-Match` (optional): ETag-based conditional request
- `Authorization: Bearer <token>` (optional): For preview mode
- `Accept: application/json`

**Response Headers:**
- `Content-Type: application/json`
- `Cache-Control: public, max-age=300, s-maxage=3600` (5 min browser, 1 hour CDN)
- `ETag: "..."` (hash of post + last_modified)
- `Last-Modified: ...` (post.last_modified timestamp)

**Response Status:**
- `200 OK`: Success
- `304 Not Modified`: Post unchanged since If-Modified-Since
- `404 Not Found`: Slug does not exist or post not published
- `401 Unauthorized`: Preview token invalid or missing for draft post

**Sample Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Best Leather Jackets for Men in 2025",
  "slug": "best-leather-jackets-2025",
  "summary": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
  "content_html": "<p>Leather jackets have been a timeless fashion staple...</p>",
  "author": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Zaryab Khan",
    "slug": "zaryab-khan",
    "avatar_url": "https://cdn.zaryableather.com/authors/zaryab-khan.webp",
    "bio": "Leather expert and fashion writer.",
    "twitter_handle": "zaryabkhan",
    "website": "https://zaryableather.com"
  },
  "categories": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Biker Jackets",
      "slug": "biker"
    }
  ],
  "tags": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "name": "Bomber",
      "slug": "bomber"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "name": "Men's Fashion",
      "slug": "mens-fashion"
    }
  ],
  "featured_image": {
    "url": "https://cdn.zaryableather.com/images/best-leather-jackets-2025.webp",
    "width": 1600,
    "height": 900,
    "alt": "Black leather biker jacket on mannequin",
    "srcset": [
      {
        "url": "https://cdn.zaryableather.com/images/best-leather-jackets-2025-320w.webp",
        "width": 320
      },
      {
        "url": "https://cdn.zaryableather.com/images/best-leather-jackets-2025-768w.webp",
        "width": 768
      },
      {
        "url": "https://cdn.zaryableather.com/images/best-leather-jackets-2025-1600w.webp",
        "width": 1600
      }
    ],
    "lqip": "data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA=",
    "webp_url": "https://cdn.zaryableather.com/images/best-leather-jackets-2025.webp",
    "og_image_url": "https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp"
  },
  "seo": {
    "title": "Best Leather Jackets for Men in 2025 — Zaryab Leather Blog",
    "description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
    "meta_keywords": ["leather jacket", "men's fashion", "bomber jacket", "biker jacket"],
    "meta_robots": "index, follow"
  },
  "open_graph": {
    "og_title": "Best Leather Jackets for Men in 2025",
    "og_description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
    "og_image": "https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp",
    "og_image_width": 1200,
    "og_image_height": 630,
    "og_type": "article",
    "og_url": "https://zaryableather.com/blog/best-leather-jackets-2025/"
  },
  "twitter_card": {
    "card": "summary_large_image",
    "title": "Best Leather Jackets for Men in 2025",
    "description": "Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.",
    "image": "https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp",
    "creator": "@zaryabkhan"
  },
  "schema_org": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Best Leather Jackets for Men in 2025",
    "image": [
      "https://cdn.zaryableather.com/images/best-leather-jackets-2025.webp",
      "https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp"
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
        "url": "https://cdn.zaryableather.com/logo.png"
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": "https://zaryableather.com/blog/best-leather-jackets-2025/"
    },
    "isAccessibleForFree": true,
    "wordCount": 1850,
    "articleBody": "Leather jackets have been a timeless fashion staple..."
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

**Caching Strategy:**
- Redis cache key: `post:{slug}:{last_modified}`
- TTL: 300 seconds (5 minutes)
- Invalidate immediately on post update

**SSG/ISR Recommendation:**
- Use `getStaticPaths()` to fetch all slugs from `/api/v1/posts/slugs/`
- Use `getStaticProps()` to fetch individual post from `/api/v1/posts/{slug}/`
- Set `revalidate: 300` (5 minutes) for ISR
- On-demand revalidation via webhook when post updates

---

### 3.3 Endpoint: GET /api/v1/posts/

**Purpose:** List posts for blog index, category, tag, author, and archive pages.

**Method:** GET

**Query Parameters:**
- `page` (optional, integer, default 1): Page number
- `page_size` (optional, integer, default 20): Results per page
- `category` (optional, string): Filter by category slug
- `tag` (optional, string): Filter by tag slug
- `author` (optional, string): Filter by author slug
- `year` (optional, integer): Filter by publication year
- `ordering` (optional, string, default `-published_at`): Sort field (prefix `-` for descending)
- `search` (optional, string): Full-text search query

**Request Headers:**
- `Accept: application/json`

**Response Headers:**
- `Content-Type: application/json`
- `Cache-Control: public, max-age=300` (5 minutes)

**Response Status:**
- `200 OK`: Success
- `400 Bad Request`: Invalid query parameters

**Sample Response:**
```json
{
  "count": 245,
  "next": "https://api.zaryableather.com/api/v1/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Best Leather Jackets for Men in 2025",
      "slug": "best-leather-jackets-2025",
      "summary": "Discover the top leather jacket styles for men in 2025...",
      "featured_image": {
        "url": "https://cdn.zaryableather.com/images/best-leather-jackets-2025-768w.webp",
        "width": 768,
        "height": 432,
        "alt": "Black leather biker jacket on mannequin"
      },
      "author": {
        "name": "Zaryab Khan",
        "slug": "zaryab-khan"
      },
      "categories": [{"name": "Biker Jackets", "slug": "biker"}],
      "tags": [{"name": "Bomber", "slug": "bomber"}],
      "published_at": "2025-09-01T12:00:00Z",
      "reading_time": 8,
      "canonical_url": "https://zaryableather.com/blog/best-leather-jackets-2025/"
    }
  ]
}
```

**Caching Strategy:**
- Redis cache key: `posts:list:{page}:{filters_hash}`
- TTL: 300 seconds (5 minutes)

---

### 3.4 Endpoint: GET /api/v1/sitemap.xml

**Purpose:** Serve sitemap index or redirect to S3-hosted sitemap.

**Method:** GET

**Response Headers:**
- `Content-Type: application/xml`
- `Cache-Control: public, max-age=3600` (1 hour)

**Implementation Approach:**
- **Recommended:** Generate sitemap files via Celery background task and upload to S3
- Endpoint returns sitemap index XML pointing to individual sitemap files on S3
- Regenerate sitemap on post publish/update (enqueue Celery task)

**Sample Sitemap Index Response:**
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
</sitemapindex>
```

**Sample Individual Sitemap Entry (posts-1.xml):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://zaryableather.com/blog/best-leather-jackets-2025/</loc>
    <lastmod>2025-09-10T08:34:00Z</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://zaryableather.com/blog/how-to-care-for-leather/</loc>
    <lastmod>2025-08-28T10:00:00Z</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>
```

---

### 3.5 Endpoint: GET /rss.xml

**Purpose:** Serve RSS/Atom feed for blog posts.

**Method:** GET

**Query Parameters:**
- `category` (optional, string): Filter by category slug
- `tag` (optional, string): Filter by tag slug

**Response Headers:**
- `Content-Type: application/rss+xml`
- `Cache-Control: public, max-age=1800` (30 minutes)

**Sample Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Zaryab Leather Blog</title>
    <link>https://zaryableather.com/blog/</link>
    <description>Expert insights on leather fashion and care</description>
    <language>en</language>
    <lastBuildDate>Mon, 10 Sep 2025 08:34:00 GMT</lastBuildDate>
    <atom:link href="https://zaryableather.com/rss.xml" rel="self" type="application/rss+xml" />
    <item>
      <title>Best Leather Jackets for Men in 2025</title>
      <link>https://zaryableather.com/blog/best-leather-jackets-2025/</link>
      <guid isPermaLink="true">https://zaryableather.com/blog/best-leather-jackets-2025/</guid>
      <pubDate>Sun, 01 Sep 2025 12:00:00 GMT</pubDate>
      <description><![CDATA[Discover the top leather jacket styles for men in 2025...]]></description>
      <author>zaryab@zaryableather.com (Zaryab Khan)</author>
      <category>Biker Jackets</category>
    </item>
  </channel>
</rss>
```

**Feed Limit:** Last 50 published posts (configurable in SiteSettings)

---

### 3.6 Endpoint: GET /api/v1/posts/{slug}/preview/

**Purpose:** Access draft/scheduled posts for preview mode.

**Method:** GET

**Path Parameters:**
- `slug` (required, string): Post slug

**Query Parameters:**
- `token` (required, string): Signed preview token

**Request Headers:**
- `Authorization: Bearer <token>` (alternative to query param)
- `Accept: application/json`

**Response Headers:**
- `Content-Type: application/json`
- `Cache-Control: private, no-cache, no-store` (never cache preview)
- `X-Robots-Tag: noindex, nofollow`

**Response Status:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid or expired token
- `404 Not Found`: Slug does not exist

**Response:** Same structure as `/api/v1/posts/{slug}/` but includes draft/scheduled posts.

**Security:**
- Token must be signed JWT or HMAC with 30-minute TTL
- Token payload includes: `{slug, exp, iat}`
- Validate token signature and expiration on every request

---

### 3.7 Endpoint: GET /api/v1/meta/site/

**Purpose:** Return global site settings for Next.js layout and meta tags.

**Method:** GET

**Response Headers:**
- `Content-Type: application/json`
- `Cache-Control: public, max-age=86400` (24 hours)

**Sample Response:**
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

### 3.8 Endpoint: GET /api/v1/redirects/

**Purpose:** Return all active redirects for Next.js middleware or CDN configuration.

**Method:** GET

**Response Headers:**
- `Content-Type: application/json`
- `Cache-Control: public, max-age=3600` (1 hour)

**Sample Response:**
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
    }
  ]
}
```

**Usage:** Next.js middleware fetches this on build and implements redirects.

---

## 4. SEO & Structured Data Rules

### 4.1 Meta Tag Generation Rules

Next.js must implement the following rules when rendering HTML `<head>` from API responses:

#### 4.1.1 Title Tag

**Rule:**
```
IF post.seo_title is present:
  <title>{post.seo_title}</title>
ELSE:
  <title>{post.title} — {site_settings.site_name}</title>
```

**Example:**
```html
<title>Best Leather Jackets for Men in 2025 — Zaryab Leather Blog</title>
```

**Character limit:** 60–70 characters (warn in admin if exceeded)

---

#### 4.1.2 Meta Description

**Rule:**
```
IF post.seo_description is present:
  <meta name="description" content="{post.seo_description}" />
ELSE:
  <meta name="description" content="{post.summary}" />
```

**Example:**
```html
<meta name="description" content="Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets." />
```

**Character limit:** 150–160 characters (warn in admin if exceeded)

---

#### 4.1.3 Canonical URL

**Rule:**
```
IF post.canonical_url is present:
  <link rel="canonical" href="{post.canonical_url}" />
ELSE:
  <link rel="canonical" href="{site_settings.site_url}/blog/{post.slug}/" />
```

**Example:**
```html
<link rel="canonical" href="https://zaryableather.com/blog/best-leather-jackets-2025/" />
```

**Requirements:**
- Always use absolute URLs
- Always include trailing slash
- Use HTTPS

---

#### 4.1.4 Meta Robots

**Rule:**
```
IF post.allow_index is false:
  <meta name="robots" content="noindex, nofollow" />
ELSE:
  (omit tag or use <meta name="robots" content="index, follow" />)
```

**For paginated pages (page > 1):**
```html
<meta name="robots" content="noindex, follow" />
```

**For preview pages:**
```html
<meta name="robots" content="noindex, nofollow" />
```

---

#### 4.1.5 Pagination Links

**For paginated list pages (blog index, category, tag, author):**

**Page 1:**
```html
<link rel="canonical" href="https://zaryableather.com/blog/" />
<link rel="next" href="https://zaryableather.com/blog/?page=2" />
```

**Page 2:**
```html
<link rel="canonical" href="https://zaryableather.com/blog/?page=2" />
<link rel="prev" href="https://zaryableather.com/blog/" />
<link rel="next" href="https://zaryableather.com/blog/?page=3" />
```

**Last page:**
```html
<link rel="canonical" href="https://zaryableather.com/blog/?page=12" />
<link rel="prev" href="https://zaryableather.com/blog/?page=11" />
```

---

### 4.2 Open Graph Tags

**Rule:**
```
og:title = post.open_graph.og_title OR post.seo_title OR post.title
og:description = post.open_graph.og_description OR post.seo_description OR post.summary
og:image = post.open_graph.og_image OR post.featured_image.og_image_url OR site_settings.default_meta_image
og:url = post.canonical_url OR computed canonical
og:type = "article"
og:site_name = site_settings.site_name
```

**Example:**
```html
<meta property="og:title" content="Best Leather Jackets for Men in 2025" />
<meta property="og:description" content="Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets." />
<meta property="og:image" content="https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:url" content="https://zaryableather.com/blog/best-leather-jackets-2025/" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="Zaryab Leather Blog" />
<meta property="article:published_time" content="2025-09-01T12:00:00Z" />
<meta property="article:modified_time" content="2025-09-10T08:34:00Z" />
<meta property="article:author" content="https://zaryableather.com/author/zaryab-khan/" />
<meta property="article:section" content="Biker Jackets" />
<meta property="article:tag" content="Bomber" />
<meta property="article:tag" content="Men's Fashion" />
```

---

### 4.3 Twitter Card Tags

**Rule:**
```
twitter:card = "summary_large_image" (if featured_image present) OR "summary"
twitter:title = same as og:title
twitter:description = same as og:description
twitter:image = same as og:image
twitter:creator = @{author.twitter_handle} (if present)
twitter:site = site_settings.twitter_site
```

**Example:**
```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Best Leather Jackets for Men in 2025" />
<meta name="twitter:description" content="Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets." />
<meta name="twitter:image" content="https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp" />
<meta name="twitter:creator" content="@zaryabkhan" />
<meta name="twitter:site" content="@zaryableather" />
```

---

### 4.4 JSON-LD Structured Data (Schema.org)

**Rule:** Use precomputed `post.schema_org` JSON blob from API response.

**Required fields for Article schema:**
- `@context`: "https://schema.org"
- `@type`: "Article"
- `headline`: post.title (max 110 characters)
- `image`: array of image URLs (featured_image.url, og_image_url)
- `datePublished`: post.published_at (ISO8601)
- `dateModified`: post.last_modified (ISO8601)
- `author`: Person object with name and URL
- `publisher`: Organization object with name and logo
- `mainEntityOfPage`: canonical URL
- `isAccessibleForFree`: true
- `wordCount`: post.word_count
- `articleBody`: plain text excerpt (optional)

**Example:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Best Leather Jackets for Men in 2025",
  "image": [
    "https://cdn.zaryableather.com/images/best-leather-jackets-2025.webp",
    "https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp"
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
    "@id": "https://zaryableather.com/blog/best-leather-jackets-2025/"
  },
  "isAccessibleForFree": true,
  "wordCount": 1850
}
</script>
```

**Additional schemas for list pages:**
- **Blog index:** Use `CollectionPage` or `Blog` schema
- **Category/Tag pages:** Use `CollectionPage` with `about` property
- **Author pages:** Include `Person` schema with `sameAs` links to social profiles

---

### 4.5 Hreflang for Internationalization

**Current Phase:** Single locale (`en`)

**Future implementation (Phase 3):**
```html
<link rel="alternate" hreflang="en" href="https://zaryableather.com/blog/best-leather-jackets-2025/" />
<link rel="alternate" hreflang="es" href="https://zaryableather.com/es/blog/mejores-chaquetas-cuero-2025/" />
<link rel="alternate" hreflang="x-default" href="https://zaryableather.com/blog/best-leather-jackets-2025/" />
```

**API contract for Phase 3:**
- Add `locale_variants` array to post response
- Each variant includes: `{locale, slug, canonical_url}`

---

### 4.6 Complete Example: Fully Populated `<head>`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  
  <!-- Primary Meta Tags -->
  <title>Best Leather Jackets for Men in 2025 — Zaryab Leather Blog</title>
  <meta name="description" content="Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets." />
  <link rel="canonical" href="https://zaryableather.com/blog/best-leather-jackets-2025/" />
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://zaryableather.com/blog/best-leather-jackets-2025/" />
  <meta property="og:title" content="Best Leather Jackets for Men in 2025" />
  <meta property="og:description" content="Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets." />
  <meta property="og:image" content="https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:site_name" content="Zaryab Leather Blog" />
  <meta property="article:published_time" content="2025-09-01T12:00:00Z" />
  <meta property="article:modified_time" content="2025-09-10T08:34:00Z" />
  <meta property="article:author" content="https://zaryableather.com/author/zaryab-khan/" />
  <meta property="article:section" content="Biker Jackets" />
  <meta property="article:tag" content="Bomber" />
  
  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:url" content="https://zaryableather.com/blog/best-leather-jackets-2025/" />
  <meta name="twitter:title" content="Best Leather Jackets for Men in 2025" />
  <meta name="twitter:description" content="Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets." />
  <meta name="twitter:image" content="https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp" />
  <meta name="twitter:creator" content="@zaryabkhan" />
  <meta name="twitter:site" content="@zaryableather" />
  
  <!-- JSON-LD Structured Data -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Best Leather Jackets for Men in 2025",
    "image": [
      "https://cdn.zaryableather.com/images/best-leather-jackets-2025.webp",
      "https://cdn.zaryableather.com/images/best-leather-jackets-2025-og.webp"
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
      "@id": "https://zaryableather.com/blog/best-leather-jackets-2025/"
    },
    "isAccessibleForFree": true,
    "wordCount": 1850
  }
  </script>
</head>
<body>
  <!-- Page content -->
</body>
</html>
```

---

## 5. Image & Media Strategy

### 5.1 Backend Responsibilities

#### 5.1.1 Image Upload & Processing Pipeline

**On image upload (via Django admin or API):**

1. **Validate:**
   - Accept: JPEG, PNG, WebP, GIF
   - Max file size: 10 MB
   - Min dimensions: 320×180
   - Max dimensions: 4096×4096

2. **Generate multiple sizes:**
   - 320w (mobile portrait)
   - 480w (mobile landscape)
   - 768w (tablet)
   - 1024w (desktop)
   - 1600w (large desktop)
   - 2048w (retina/high-DPI)

3. **Generate WebP alternatives:**
   - For each size, create WebP version
   - Quality: 85% for WebP, 90% for JPEG
   - Preserve aspect ratio

4. **Generate OG image:**
   - Size: 1200×630 (Facebook/Twitter optimal)
   - Crop to center if aspect ratio doesn't match
   - Format: WebP + JPEG fallback

5. **Generate LQIP (Low-Quality Image Placeholder):**
   - Tiny version: 20×20 pixels
   - Base64-encoded WebP or JPEG
   - Embedded in API response for instant placeholder

6. **Extract metadata:**
   - Original dimensions (width, height)
   - File size
   - MIME type
   - EXIF data (optional: camera, location - strip for privacy)

7. **Upload to S3:**
   - Bucket: `zaryableather-media`
   - Path structure: `/images/{year}/{month}/{uuid}-{size}.{ext}`
   - Example: `/images/2025/09/550e8400-e29b-41d4-a716-446655440000-1600w.webp`
   - Set public-read ACL
   - Set Cache-Control: `public, max-age=31536000, immutable`

8. **Serve via CDN:**
   - CloudFront or Cloudflare CDN
   - CDN URL: `https://cdn.zaryableather.com/`
   - Enable Brotli/Gzip compression
   - Enable HTTP/2

#### 5.1.2 API Response Format

**Image object structure:**
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
  "jpeg_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.jpg",
  "og_image_url": "https://cdn.zaryableather.com/images/2025/09/550e8400-og.webp"
}
```

---

### 5.2 Frontend Responsibilities (Next.js)

#### 5.2.1 Image Rendering with Next.js Image Component

**Use Next.js `<Image>` component for automatic optimization:**

```jsx
import Image from 'next/image';

<Image
  src={post.featured_image.url}
  alt={post.featured_image.alt}
  width={post.featured_image.width}
  height={post.featured_image.height}
  placeholder="blur"
  blurDataURL={post.featured_image.lqip}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  priority={isAboveFold}
/>
```

**For custom implementation (if not using Next.js Image):**

```html
<img
  src="https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp"
  srcset="
    https://cdn.zaryableather.com/images/2025/09/550e8400-320w.webp 320w,
    https://cdn.zaryableather.com/images/2025/09/550e8400-768w.webp 768w,
    https://cdn.zaryableather.com/images/2025/09/550e8400-1600w.webp 1600w
  "
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  alt="Black leather biker jacket on mannequin"
  loading="lazy"
  width="1600"
  height="900"
/>
```

#### 5.2.2 Loading Strategy

**Above-the-fold images (hero, featured):**
- Use `priority` prop or `loading="eager"`
- Preload with `<link rel="preload" as="image" href="..." />`

**Below-the-fold images:**
- Use `loading="lazy"` for native lazy loading
- Intersection Observer for older browsers

**LQIP placeholder:**
- Display base64 LQIP immediately
- Fade in full image when loaded

---

### 5.3 Image Cache Invalidation

**When image is re-uploaded or regenerated:**

1. Generate new UUID for image filename
2. Update Post.featured_image with new URLs
3. Invalidate CDN cache for old URLs (CloudFront invalidation API)
4. Trigger Next.js revalidation webhook for affected posts

**Cache headers for images:**
```
Cache-Control: public, max-age=31536000, immutable
```

**Rationale:** Images are immutable (UUID in filename), so aggressive caching is safe.

---

### 5.4 Alt Text Requirements

**Mandatory for all images:**
- Alt text must be descriptive and concise (max 125 characters)
- Include relevant keywords naturally
- Describe what's in the image, not "image of..."
- For decorative images, use empty alt (`alt=""`)

**Admin validation:**
- Warn if alt text is missing or too short (<10 characters)
- Suggest alt text using image filename or post title

---

### 5.5 Performance Targets

- **Largest Contentful Paint (LCP):** <2.5s
- **Cumulative Layout Shift (CLS):** <0.1
- **First Input Delay (FID):** <100ms

**Image optimization contributes to:**
- LCP: Fast-loading hero images with LQIP
- CLS: Explicit width/height prevents layout shift

---

## 6. Sitemap / Robots / RSS Plan

### 6.1 Sitemap Strategy

#### 6.1.1 Approach: Background Generation + S3 Hosting

**Recommended implementation:**

1. **Generate sitemap files via Celery background task**
2. **Upload to S3 bucket** (`zaryableather-sitemaps`)
3. **Serve sitemap index** at `/sitemap.xml` (Django endpoint or CDN redirect)
4. **Incremental regeneration** on post publish/update

**Sitemap structure:**
```
/sitemap.xml                    → Sitemap index (points to individual sitemaps)
/sitemaps/posts-1.xml           → Posts 1-1000
/sitemaps/posts-2.xml           → Posts 1001-2000
/sitemaps/categories.xml        → All category pages
/sitemaps/tags.xml              → All tag pages
/sitemaps/authors.xml           → All author pages
/sitemaps/static.xml            → Homepage, about, contact, etc.
```

#### 6.1.2 Sitemap Entry Fields

**For post pages:**
```xml
<url>
  <loc>https://zaryableather.com/blog/best-leather-jackets-2025/</loc>
  <lastmod>2025-09-10T08:34:00Z</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.9</priority>
</url>
```

**Priority calculation:**
- Featured/pinned posts: `0.9`
- Recent posts (<30 days): `0.8`
- Regular posts: `0.6`
- Category/tag pages: `0.4`
- Author pages: `0.3`
- Static pages: `0.5`

**Changefreq hints:**
- Posts: `monthly` (or `weekly` for frequently updated)
- Category/tag pages: `weekly`
- Homepage: `daily`

#### 6.1.3 Incremental Sitemap Regeneration

**Trigger:** When a post is published, updated, or deleted

**Process:**
1. Enqueue Celery task: `regenerate_sitemap.delay()`
2. Task determines which sitemap files need updating:
   - If post count changes, regenerate affected `posts-N.xml` files
   - If categories/tags change, regenerate `categories.xml` / `tags.xml`
3. Upload updated files to S3
4. Update sitemap index with new `<lastmod>` timestamps
5. Ping search engines (optional):
   - `http://www.google.com/ping?sitemap=https://zaryableather.com/sitemap.xml`
   - `http://www.bing.com/ping?sitemap=https://zaryableather.com/sitemap.xml`

**Performance:**
- Sitemap generation should complete in <30 seconds for 10,000 posts
- Use database pagination to avoid memory issues
- Cache sitemap files on CDN with 1-hour TTL

#### 6.1.4 Sitemap Index Example

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

### 6.2 Robots.txt Strategy

#### 6.2.1 Editable via SiteSettings

**Storage:** `SiteSettings.robots_txt_content` (text field)

**Endpoint:** `GET /robots.txt` (Django view or static file)

**Default content:**
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

#### 6.2.2 Environment-Specific Robots

**Production:**
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Sitemap: https://zaryableather.com/sitemap.xml
```

**Staging/Dev:**
```
User-agent: *
Disallow: /
```

**Implementation:** Check environment variable `ENVIRONMENT` and serve appropriate robots.txt.

---

### 6.3 RSS Feed Strategy

#### 6.3.1 Feed Endpoint: GET /rss.xml

**Feed format:** RSS 2.0 with Atom namespace

**Feed items:** Last 50 published posts (configurable in SiteSettings)

**Query parameters:**
- `category={slug}`: Filter by category
- `tag={slug}`: Filter by tag

**Example URLs:**
- `https://zaryableather.com/rss.xml` (all posts)
- `https://zaryableather.com/rss.xml?category=biker` (category-specific)
- `https://zaryableather.com/rss.xml?tag=bomber` (tag-specific)

#### 6.3.2 RSS Feed Structure

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
      <link>https://zaryableather.com/blog/best-leather-jackets-2025/</link>
      <guid isPermaLink="true">https://zaryableather.com/blog/best-leather-jackets-2025/</guid>
      <pubDate>Sun, 01 Sep 2025 12:00:00 GMT</pubDate>
      <description><![CDATA[Discover the top leather jacket styles for men in 2025, from classic bombers to modern biker jackets.]]></description>
      <content:encoded><![CDATA[<p>Leather jackets have been a timeless fashion staple...</p>]]></content:encoded>
      <author>zaryab@zaryableather.com (Zaryab Khan)</author>
      <category>Biker Jackets</category>
      <category>Men's Fashion</category>
      <enclosure url="https://cdn.zaryableather.com/images/best-leather-jackets-2025.webp" type="image/webp" length="245760" />
    </item>
    
  </channel>
</rss>
```

#### 6.3.3 Feed Content Options

**Configurable in SiteSettings:**
- `rss_feed_full_content` (boolean): If true, include full `content_html` in `<content:encoded>`; if false, include only `summary` in `<description>`

**Recommendation:** Use full content for better subscriber experience.

#### 6.3.4 Feed Caching

**Cache headers:**
```
Cache-Control: public, max-age=1800
```

**Redis cache:**
- Key: `rss:feed:{category}:{tag}`
- TTL: 1800 seconds (30 minutes)
- Invalidate on post publish/update

---

### 6.4 Integration with Next.js ISR

#### 6.4.1 Revalidation Webhook Contract

**When a post is published/updated/deleted:**

1. Backend sends POST request to Next.js revalidation webhook
2. Next.js triggers on-demand ISR for affected pages

**Webhook URL:**
```
POST https://zaryableather.com/api/revalidate
```

**Request headers:**
```
Content-Type: application/json
X-Revalidate-Secret: <HMAC_SECRET>
X-Signature: <HMAC_SHA256_SIGNATURE>
```

**Request payload:**
```json
{
  "slugs": ["best-leather-jackets-2025", "how-to-care-for-leather"],
  "paths": [
    "/blog/best-leather-jackets-2025",
    "/blog/how-to-care-for-leather",
    "/blog",
    "/category/biker",
    "/tag/bomber"
  ],
  "timestamp": "2025-09-10T08:34:00Z",
  "event": "post.published"
}
```

**HMAC signature calculation:**
```python
import hmac
import hashlib

secret = os.environ['REVALIDATE_SECRET']
payload = json.dumps(request_body, sort_keys=True)
signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
```

**Next.js webhook handler validates signature and calls:**
```javascript
await res.revalidate('/blog/best-leather-jackets-2025');
await res.revalidate('/blog');
```

#### 6.4.2 Sitemap Notification

**After sitemap regeneration:**

1. Send webhook to Next.js with `event: "sitemap.updated"`
2. Next.js can optionally trigger full rebuild or notify search engines

---

## 7. Caching, Conditional Requests & ISR Hooks

### 7.1 ETag & Last-Modified Headers

#### 7.1.1 Post Detail Endpoint

**Response headers:**
```
ETag: "a1b2c3d4e5f6"
Last-Modified: Wed, 10 Sep 2025 08:34:00 GMT
Cache-Control: public, max-age=300, s-maxage=3600
```

**ETag generation:**
```python
import hashlib

etag_source = f"{post.id}:{post.last_modified.isoformat()}"
etag = hashlib.md5(etag_source.encode()).hexdigest()
```

**Conditional request handling:**

**Request with If-None-Match:**
```
GET /api/v1/posts/best-leather-jackets-2025/
If-None-Match: "a1b2c3d4e5f6"
```

**Response if ETag matches:**
```
HTTP/1.1 304 Not Modified
ETag: "a1b2c3d4e5f6"
Last-Modified: Wed, 10 Sep 2025 08:34:00 GMT
```

**Request with If-Modified-Since:**
```
GET /api/v1/posts/best-leather-jackets-2025/
If-Modified-Since: Wed, 10 Sep 2025 08:34:00 GMT
```

**Response if not modified:**
```
HTTP/1.1 304 Not Modified
```

---

### 7.2 Redis Caching Strategy

#### 7.2.1 Cache Layers

**Layer 1: CDN (CloudFront/Cloudflare)**
- TTL: 1 hour (3600s)
- Caches full HTTP responses
- Respects Cache-Control headers

**Layer 2: Redis (Application cache)**
- TTL: 5–60 minutes (varies by endpoint)
- Caches serialized objects and query results

**Layer 3: Database query cache**
- Django ORM query caching (optional)

#### 7.2.2 Cache Keys & TTLs

| Endpoint | Cache Key | TTL | Invalidation Trigger |
|----------|-----------|-----|----------------------|
| `/api/v1/posts/slugs/` | `posts:slugs:{since}:{page}` | 3600s | Any post publish/update |
| `/api/v1/posts/{slug}/` | `post:{slug}:{last_modified}` | 300s | Post update |
| `/api/v1/posts/` | `posts:list:{page}:{filters_hash}` | 300s | Any post publish/update |
| `/api/v1/meta/site/` | `site:settings` | 86400s | SiteSettings update |
| `/rss.xml` | `rss:feed:{category}:{tag}` | 1800s | Post publish/update |

#### 7.2.3 Cache Invalidation

**On post publish/update:**
```python
# Invalidate specific post cache
cache.delete(f"post:{post.slug}:*")

# Invalidate list caches
cache.delete_pattern("posts:list:*")
cache.delete_pattern("posts:slugs:*")

# Invalidate RSS feed
cache.delete_pattern("rss:feed:*")

# Trigger CDN invalidation (CloudFront)
cloudfront.create_invalidation(
    DistributionId='E1234567890ABC',
    InvalidationBatch={
        'Paths': {
            'Quantity': 2,
            'Items': [
                f'/api/v1/posts/{post.slug}/',
                '/api/v1/posts/slugs/'
            ]
        },
        'CallerReference': str(time.time())
    }
)
```

---

### 7.3 ISR (Incremental Static Regeneration) Integration

#### 7.3.1 Recommended ISR Configuration

**Next.js getStaticProps:**
```javascript
export async function getStaticProps({ params }) {
  const post = await fetchPost(params.slug);
  
  return {
    props: { post },
    revalidate: 300, // 5 minutes
  };
}
```

**Tradeoffs:**

| Revalidate Value | Pros | Cons |
|------------------|------|------|
| 60s | Fresh content, low latency | Higher API load, more builds |
| 300s (5 min) | **Balanced** | Slight staleness |
| 3600s (1 hour) | Low API load, cost-effective | Content can be stale |

**Recommendation:** Start with 300s (5 minutes) and adjust based on traffic and content update frequency.

#### 7.3.2 On-Demand Revalidation

**Preferred approach:** Use on-demand revalidation instead of time-based ISR.

**Next.js API route: /api/revalidate**
```javascript
export default async function handler(req, res) {
  // Validate HMAC signature
  const signature = req.headers['x-signature'];
  const isValid = validateSignature(req.body, signature);
  
  if (!isValid) {
    return res.status(401).json({ message: 'Invalid signature' });
  }
  
  // Revalidate paths
  const { paths } = req.body;
  
  for (const path of paths) {
    await res.revalidate(path);
  }
  
  return res.json({ revalidated: true, paths });
}
```

**Django trigger:**
```python
import hmac
import hashlib
import requests

def trigger_nextjs_revalidation(post):
    payload = {
        'slugs': [post.slug],
        'paths': [
            f'/blog/{post.slug}',
            '/blog',
            *[f'/category/{cat.slug}' for cat in post.categories.all()],
            *[f'/tag/{tag.slug}' for tag in post.tags.all()],
        ],
        'timestamp': timezone.now().isoformat(),
        'event': 'post.published'
    }
    
    secret = settings.REVALIDATE_SECRET
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    
    response = requests.post(
        f'{settings.NEXTJS_URL}/api/revalidate',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'X-Signature': signature
        },
        timeout=10
    )
    
    return response.status_code == 200
```

---

### 7.4 Cache-Control Headers Summary

| Resource Type | Cache-Control | Rationale |
|---------------|---------------|-----------|
| Post detail | `public, max-age=300, s-maxage=3600` | 5 min browser, 1 hour CDN |
| Post list | `public, max-age=300` | 5 min cache |
| Slugs endpoint | `public, max-age=3600` | 1 hour cache (incremental builds) |
| Site settings | `public, max-age=86400` | 24 hour cache (rarely changes) |
| Images | `public, max-age=31536000, immutable` | 1 year (immutable URLs) |
| RSS feed | `public, max-age=1800` | 30 min cache |
| Preview pages | `private, no-cache, no-store` | Never cache |

---

## 8. Preview Tokens & Staging

### 8.1 Preview Token Mechanism

#### 8.1.1 Token Generation

**Use JWT (JSON Web Token) for preview tokens:**

**Token payload:**
```json
{
  "slug": "best-leather-jackets-2025",
  "iat": 1693824000,
  "exp": 1693825800
}
```

**Token TTL:** 30 minutes (1800 seconds)

**Django implementation:**
```python
import jwt
from datetime import datetime, timedelta

def generate_preview_token(post_slug):
    payload = {
        'slug': post_slug,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.PREVIEW_SECRET, algorithm='HS256')
    return token

def validate_preview_token(token):
    try:
        payload = jwt.decode(token, settings.PREVIEW_SECRET, algorithms=['HS256'])
        return payload['slug']
    except jwt.ExpiredSignatureError:
        raise ValidationError('Preview token expired')
    except jwt.InvalidTokenError:
        raise ValidationError('Invalid preview token')
```

#### 8.1.2 Preview Endpoint

**Endpoint:** `GET /api/v1/posts/{slug}/preview/`

**Authentication:**
- Query param: `?token=<JWT>`
- OR Header: `Authorization: Bearer <JWT>`

**Response:**
- Same structure as `/api/v1/posts/{slug}/`
- Includes draft/scheduled posts
- Returns 401 if token invalid/expired

**Response headers:**
```
Cache-Control: private, no-cache, no-store
X-Robots-Tag: noindex, nofollow
```

#### 8.1.3 Preview Flow

1. **Editor clicks "Preview" in Django admin**
2. **Backend generates preview token** for post slug
3. **Backend returns preview URL:** `https://zaryableather.com/blog/best-leather-jackets-2025/?preview=true&token=<JWT>`
4. **Next.js detects `?preview=true` query param**
5. **Next.js fetches post from preview endpoint** with token
6. **Next.js renders page with noindex meta tag**

**Next.js preview mode:**
```javascript
export async function getServerSideProps({ params, query, preview }) {
  if (query.preview && query.token) {
    const post = await fetchPostPreview(params.slug, query.token);
    return { props: { post, preview: true } };
  }
  
  // Normal SSG flow
  const post = await fetchPost(params.slug);
  return { props: { post, preview: false } };
}
```

---

### 8.2 Staging Environment

**Staging URL:** `https://staging.zaryableather.com/`

**Staging robots.txt:**
```
User-agent: *
Disallow: /
```

**Staging meta tags:**
```html
<meta name="robots" content="noindex, nofollow" />
```

**Environment variables:**
- `ENVIRONMENT=staging`
- `SITE_URL=https://staging.zaryableather.com`
- `ALLOW_INDEXING=false`

**Staging API:** `https://api-staging.zaryableather.com/`

---

## 9. Redirects & Legacy URLs

### 9.1 Redirect Model & Storage

**Redirect records stored in database:**

| Field | Type | Purpose |
|-------|------|---------|
| `from_path` | String (500) | Legacy path (e.g., `/old-post/`) |
| `to_url` | URL | Target canonical URL (absolute) |
| `status_code` | Integer | `301` (permanent) or `302` (temporary) |
| `active` | Boolean | Enable/disable redirect |
| `reason` | String (200) | Admin note |
| `created_at` | DateTime | Timestamp |

### 9.2 Redirect API Endpoint

**Endpoint:** `GET /api/v1/redirects/`

**Purpose:** Provide all active redirects for Next.js middleware or CDN configuration.

**Response:**
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
    }
  ]
}
```

**Cache headers:**
```
Cache-Control: public, max-age=3600
```

### 9.3 Automatic Redirect Creation

**When a post is published/updated:**

1. Check if `post.legacy_urls` array is populated
2. For each legacy URL, create a Redirect record:
   - `from_path`: legacy URL
   - `to_url`: post canonical URL
   - `status_code`: 301
   - `active`: true
   - `reason`: "Auto-generated from post legacy_urls"

**Example:**
```python
def create_redirects_for_post(post):
    for legacy_url in post.legacy_urls:
        Redirect.objects.get_or_create(
            from_path=legacy_url,
            defaults={
                'to_url': post.canonical_url,
                'status_code': 301,
                'active': True,
                'reason': f'Legacy URL for post: {post.title}'
            }
        )
```

### 9.4 Next.js Middleware Implementation

**Fetch redirects on build:**
```javascript
// middleware.js
import { NextResponse } from 'next/server';

const redirects = await fetch('https://api.zaryableather.com/api/v1/redirects/')
  .then(res => res.json());

export function middleware(request) {
  const path = request.nextUrl.pathname;
  
  const redirect = redirects.redirects.find(r => r.from_path === path);
  
  if (redirect) {
    return NextResponse.redirect(redirect.to_url, redirect.status_code);
  }
  
  return NextResponse.next();
}
```

**Alternative: CDN-level redirects (Cloudflare/Vercel):**
- Export redirects as JSON
- Configure CDN to handle redirects at edge
- Faster than application-level redirects

### 9.5 Redirect Priority & Conflict Resolution

**Priority order:**
1. Exact path match
2. Pattern match (if implementing regex in Phase 3)
3. 404 fallback

**Conflict resolution:**
- If multiple redirects match, use most recently created
- Warn in admin if duplicate `from_path` exists

---

## 10. Search & Discovery

### 10.1 Search Strategy (Phase 2)

**Approach:** PostgreSQL full-text search with trigram fuzzy matching

**Indexed fields:**
- `Post.title` (weight A)
- `Post.summary` (weight B)
- `Post.content_html` (weight C, strip HTML tags)
- `Post.tags` (weight B)
- `Post.categories` (weight B)

**Search endpoint:** `GET /api/v1/posts/?search=leather+jacket`

**Implementation notes:**
- Use `django.contrib.postgres.search` (SearchVector, SearchQuery, SearchRank)
- Create GIN index on search vector
- Support fuzzy matching with trigram similarity

**Phase 1 requirement:** Define which fields to index (listed above).

### 10.2 Search API Contract (Phase 2)

**Query parameters:**
- `search` (string): Search query
- `page` (integer): Page number
- `page_size` (integer): Results per page

**Response:**
```json
{
  "count": 42,
  "results": [
    {
      "id": "...",
      "title": "Best Leather Jackets for Men in 2025",
      "slug": "best-leather-jackets-2025",
      "summary": "...",
      "search_rank": 0.95,
      "canonical_url": "https://zaryableather.com/blog/best-leather-jackets-2025/"
    }
  ]
}
```

### 10.3 SEO for Search Results

**Search results page meta:**
- Title: `Search results for "{query}" — Zaryab Leather Blog`
- Meta robots: `noindex, follow` (don't index search results)
- Canonical: Point to search page itself

---

## 11. Monitoring, Logging & Analytics

### 11.1 Error Tracking

**Tool:** Sentry

**Integration:**
- Capture all exceptions in Django views and Celery tasks
- Include request context (URL, user agent, IP)
- Set environment tags (production, staging, dev)

**Critical alerts:**
- 500 errors on public endpoints
- Failed sitemap generation
- Failed revalidation webhook calls

### 11.2 Request Logging

**Log format (JSON):**
```json
{
  "timestamp": "2025-09-10T08:34:00Z",
  "method": "GET",
  "path": "/api/v1/posts/best-leather-jackets-2025/",
  "status": 200,
  "response_time_ms": 45,
  "user_agent": "Mozilla/5.0...",
  "ip": "203.0.113.42",
  "cache_hit": true
}
```

**Logged events:**
- All API requests
- Cache hits/misses
- Slow queries (>100ms)
- Failed authentication attempts

### 11.3 Performance Metrics

**Tool:** Prometheus + Grafana (or AWS CloudWatch)

**Metrics to track:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Cache hit rate
- Database query time
- Celery task queue length

**Dashboards:**
- API performance overview
- Cache performance
- Sitemap generation status
- Recent posts published

### 11.4 SEO Analytics

**Google Search Console integration:**
- Track organic clicks, impressions, CTR
- Monitor top landing pages
- Identify crawl errors and indexing issues

**Metrics to track:**
- Organic traffic (sessions, users)
- Top landing pages
- Top search queries
- Average position in search results
- Core Web Vitals (LCP, FID, CLS)

**Admin dashboard widgets:**
- Recent posts published
- Top 10 posts by organic traffic (last 30 days)
- Sitemap generation status
- Cache hit rate

### 11.5 Uptime Monitoring

**Tool:** UptimeRobot or Pingdom

**Endpoints to monitor:**
- `https://zaryableather.com/` (homepage)
- `https://api.zaryableather.com/api/v1/posts/slugs/` (API health)
- `https://zaryableather.com/sitemap.xml` (sitemap)

**Alert thresholds:**
- Downtime >2 minutes
- Response time >2 seconds
- 5xx error rate >1%

---

## 12. Security & Rate Limiting

### 12.1 Rate Limiting

**Tool:** Django Ratelimit or Redis-based rate limiting

**Rate limits by endpoint:**

| Endpoint | Rate Limit | Scope |
|----------|------------|-------|
| `/api/v1/posts/slugs/` | 100/hour | IP address |
| `/api/v1/posts/{slug}/` | 300/hour | IP address |
| `/api/v1/posts/` | 300/hour | IP address |
| `/api/v1/posts/{slug}/preview/` | 50/hour | Token |
| `/api/revalidate` (Next.js webhook) | 1000/hour | Secret key |

**Whitelist build IPs:**
- Vercel/Netlify build IPs should have higher limits or no limits
- Use `X-Forwarded-For` header to identify real client IP behind CDN

**Rate limit response:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 3600
Content-Type: application/json

{
  "error": "Rate limit exceeded",
  "retry_after": 3600
}
```

### 12.2 Authentication & Authorization

**Public endpoints (no auth required):**
- `/api/v1/posts/slugs/`
- `/api/v1/posts/{slug}/`
- `/api/v1/posts/`
- `/sitemap.xml`
- `/rss.xml`
- `/robots.txt`

**Protected endpoints:**
- `/api/v1/posts/{slug}/preview/` (JWT token required)
- `/api/revalidate` (HMAC signature required)
- `/admin/` (Django admin authentication)

**Preview token validation:**
- Verify JWT signature
- Check expiration
- Validate slug matches token payload

**Revalidation webhook validation:**
- Verify HMAC signature in `X-Signature` header
- Use constant-time comparison to prevent timing attacks

### 12.3 HTTPS & Security Headers

**Enforce HTTPS:**
- Redirect all HTTP requests to HTTPS
- Use HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

**Security headers:**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; img-src 'self' https://cdn.zaryableather.com; script-src 'self' 'unsafe-inline'
```

### 12.4 CORS Configuration

**Allow Next.js frontend to access API:**

```python
CORS_ALLOWED_ORIGINS = [
    'https://zaryableather.com',
    'https://staging.zaryableather.com',
    'http://localhost:3000',  # Local dev
]

CORS_ALLOW_METHODS = ['GET', 'OPTIONS']
CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'If-Modified-Since', 'If-None-Match']
```

### 12.5 Input Validation & Sanitization

**Slug validation:**
- Regex: `^[a-z0-9-]{3,100}$`
- No SQL injection risk (use ORM)

**HTML content sanitization:**
- Use `bleach` library to sanitize `content_html`
- Allow safe tags: `<p>, <a>, <strong>, <em>, <ul>, <ol>, <li>, <h2>, <h3>, <img>`
- Strip dangerous attributes: `onclick`, `onerror`, etc.

---

## 13. CI/CD & Deployment Hooks

### 13.1 Deployment Workflow

**On post publish/update:**

1. **Save post to database**
2. **Invalidate caches** (Redis, CDN)
3. **Enqueue Celery tasks:**
   - Regenerate sitemap
   - Trigger Next.js revalidation webhook
4. **Send revalidation webhook to Next.js**
5. **Log event** (post published, timestamp, author)

**Celery task: `regenerate_sitemap.delay()`**
```python
@shared_task
def regenerate_sitemap():
    # Generate sitemap XML files
    # Upload to S3
    # Update sitemap index
    # Ping search engines (optional)
    pass
```

**Celery task: `trigger_nextjs_revalidation.delay(post_id)`**
```python
@shared_task
def trigger_nextjs_revalidation(post_id):
    post = Post.objects.get(id=post_id)
    
    payload = {
        'slugs': [post.slug],
        'paths': [
            f'/blog/{post.slug}',
            '/blog',
            *[f'/category/{cat.slug}' for cat in post.categories.all()],
        ],
        'timestamp': timezone.now().isoformat(),
        'event': 'post.published'
    }
    
    # Send webhook with HMAC signature
    send_revalidation_webhook(payload)
```

### 13.2 Revalidation Webhook Contract

**Endpoint:** `POST https://zaryableather.com/api/revalidate`

**Request headers:**
```
Content-Type: application/json
X-Signature: <HMAC_SHA256_SIGNATURE>
```

**Request payload:**
```json
{
  "slugs": ["best-leather-jackets-2025"],
  "paths": [
    "/blog/best-leather-jackets-2025",
    "/blog",
    "/category/biker"
  ],
  "timestamp": "2025-09-10T08:34:00Z",
  "event": "post.published"
}
```

**HMAC signature calculation:**
```python
import hmac
import hashlib
import json

secret = settings.REVALIDATE_SECRET  # Shared secret with Next.js
payload_str = json.dumps(payload, sort_keys=True)
signature = hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
```

**Next.js validation:**
```javascript
import crypto from 'crypto';

function validateSignature(payload, signature) {
  const secret = process.env.REVALIDATE_SECRET;
  const payloadStr = JSON.stringify(payload, Object.keys(payload).sort());
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payloadStr)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}
```

**Response:**
```json
{
  "revalidated": true,
  "paths": [
    "/blog/best-leather-jackets-2025",
    "/blog",
    "/category/biker"
  ]
}
```

### 13.3 CI/CD Pipeline

**Tools:** GitHub Actions, GitLab CI, or CircleCI

**Pipeline stages:**

1. **Lint & Format**
   - Run `flake8`, `black`, `isort`
   - Run `eslint`, `prettier` (for Next.js)

2. **Test**
   - Run Django unit tests
   - Run integration tests (API endpoints)
   - Run Next.js tests

3. **Build**
   - Build Docker image for Django API
   - Build Next.js static site

4. **Deploy**
   - Deploy Django API to AWS ECS/Fargate or Heroku
   - Deploy Next.js to Vercel or Netlify
   - Run database migrations
   - Invalidate CDN cache

5. **Post-Deploy**
   - Run smoke tests (health check endpoints)
   - Send Slack notification

**Environment variables required:**
- `DATABASE_URL`
- `REDIS_URL`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (for S3)
- `PREVIEW_SECRET` (JWT signing key)
- `REVALIDATE_SECRET` (HMAC shared secret)
- `SENTRY_DSN`
- `NEXTJS_URL` (for webhook)

---

## 14. Acceptance Criteria

### 14.1 Phase 1 Deliverables Checklist

- [x] **Architecture document** (this file) with URL patterns, slug rules, canonicalization rules, and site tree diagram
- [x] **SEO content model** with all models, fields, types, and required/optional flags
- [x] **API contract** with endpoints, query params, headers, cache headers, and sample JSON responses for:
  - `/api/v1/posts/slugs/`
  - `/api/v1/posts/{slug}/`
  - `/api/v1/posts/`
  - `/sitemap.xml`
  - `/rss.xml`
  - `/api/v1/posts/{slug}/preview/`
  - `/api/v1/meta/site/`
  - `/api/v1/redirects/`
- [x] **Image & media strategy** with sizes, formats, srcset, LQIP, and CDN expectations
- [x] **Sitemap & robots strategy** with example sitemap entry and revalidation webhook contract
- [x] **Caching & invalidation strategy** with ETag/Last-Modified rules, Redis cache TTLs, and recommended ISR revalidate default
- [x] **Preview token spec** with JWT example and security approach
- [x] **Redirect/legacy URL plan** with `/api/v1/redirects/` contract
- [x] **Prioritized Phase 2 checklist** (see Section 15)
- [x] **Timeline and estimate** for Phase 2 (see Section 16)
- [x] **Handover notes** (see Section 17)

### 14.2 QA Acceptance Tests

**Test 1: Slug list endpoint returns valid data**
```bash
curl -H "Accept: application/json" https://api.zaryableather.com/api/v1/posts/slugs/
# Expected: 200 OK, JSON with count and results array
```

**Test 2: Post detail endpoint returns full SEO metadata**
```bash
curl -H "Accept: application/json" https://api.zaryableather.com/api/v1/posts/best-leather-jackets-2025/
# Expected: 200 OK, JSON with seo, open_graph, schema_org fields
```

**Test 3: Conditional request returns 304**
```bash
curl -H "If-None-Match: \"a1b2c3d4e5f6\"" https://api.zaryableather.com/api/v1/posts/best-leather-jackets-2025/
# Expected: 304 Not Modified
```

**Test 4: Preview endpoint requires valid token**
```bash
curl https://api.zaryableather.com/api/v1/posts/draft-post/preview/
# Expected: 401 Unauthorized

curl -H "Authorization: Bearer <VALID_JWT>" https://api.zaryableather.com/api/v1/posts/draft-post/preview/
# Expected: 200 OK, JSON with draft post
```

**Test 5: Sitemap index is valid XML**
```bash
curl https://zaryableather.com/sitemap.xml
# Expected: 200 OK, valid XML with <sitemapindex>
```

**Test 6: RSS feed is valid**
```bash
curl https://zaryableather.com/rss.xml
# Expected: 200 OK, valid RSS 2.0 XML
```

**Test 7: Redirects endpoint returns active redirects**
```bash
curl https://api.zaryableather.com/api/v1/redirects/
# Expected: 200 OK, JSON with redirects array
```

**Test 8: Revalidation webhook validates HMAC signature**
```bash
curl -X POST https://zaryableather.com/api/revalidate \
  -H "Content-Type: application/json" \
  -H "X-Signature: invalid" \
  -d '{"slugs": ["test"]}'
# Expected: 401 Unauthorized
```

---

## 15. How to Use This Document

### 15.1 Document Structure

This Phase 1 architecture document is organized into the following sections:

1. **High-Level Site Architecture** — URL patterns, slug rules, canonicalization
2. **SEO Content Model** — Database models and fields
3. **API Contract** — Endpoints, request/response formats
4. **SEO & Structured Data Rules** — Meta tags, Open Graph, JSON-LD
5. **Image & Media Strategy** — Image processing, srcset, CDN
6. **Sitemap / Robots / RSS Plan** — Sitemap generation, robots.txt, RSS feed
7. **Caching & ISR Hooks** — ETag, Redis, ISR integration
8. **Preview Tokens & Staging** — Preview mode, JWT tokens
9. **Redirects & Legacy URLs** — Redirect model, API endpoint
10. **Search & Discovery** — Search strategy (Phase 2)
11. **Monitoring & Analytics** — Logging, metrics, SEO analytics
12. **Security & Rate Limiting** — Authentication, rate limits, HTTPS
13. **CI/CD & Deployment Hooks** — Deployment workflow, revalidation webhook
14. **Acceptance Criteria** — Deliverables checklist, QA tests
15. **How to Use This Document** — (this section)

### 15.2 Where to Place This Document

**Recommended location:**
```
/docs/phase-1-architecture.md
/docs/api_examples.md
/docs/phase2-checklist.md
/docs/handover.md
/docs/diagrams/site-tree.txt
```

### 15.3 Who to Notify

**When sitemap/revalidate webhook is available:**
- Notify Next.js frontend developer
- Provide `REVALIDATE_SECRET` environment variable
- Provide webhook URL format: `POST https://zaryableather.com/api/revalidate`

**When API endpoints are ready:**
- Notify Next.js developer
- Provide API base URL: `https://api.zaryableather.com/`
- Provide sample API responses (see `docs/api_examples.md`)

### 15.4 Environment Variables & Secrets

**Required for Phase 2:**

**Django backend:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=zaryableather-media
AWS_CLOUDFRONT_DOMAIN=cdn.zaryableather.com
PREVIEW_SECRET=<random-256-bit-key>
REVALIDATE_SECRET=<random-256-bit-key>
SENTRY_DSN=https://...@sentry.io/...
NEXTJS_URL=https://zaryableather.com
ENVIRONMENT=production
SITE_URL=https://zaryableather.com
```

**Next.js frontend:**
```bash
NEXT_PUBLIC_API_URL=https://api.zaryableather.com
REVALIDATE_SECRET=<same-as-backend>
PREVIEW_SECRET=<same-as-backend>
```

**Generate secrets:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

