# 🚀 Django Blog API - SEO Backend

Enterprise-grade SEO implementation for Django REST Framework Blog API with Next.js integration.

---

## ⚡ Quick Start (5 Minutes)

### 1. Run Migrations

```bash
python manage.py migrate
```

### 2. Configure Environment

Add to `.env`:

```bash
SITE_URL=https://yourdomain.com
SITE_NAME=Your Blog Name
TWITTER_SITE=@yourhandle
AUTO_PING_SEARCH_ENGINES=True
SEO_PING_TOKEN=your-secret-token
```

### 3. Configure Site Settings

Go to Django Admin → Site Settings and set:
- Site name and description
- Default Open Graph image
- Twitter handle
- Google verification code

### 4. Test SEO Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/seo/health/

# Sitemap
curl http://localhost:8000/sitemap.xml

# RSS Feed
curl http://localhost:8000/rss/

# Schema for a post
curl http://localhost:8000/api/v1/seo/schema/your-post-slug/
```

---

## 🎯 Features

### ✅ SEO Metadata
- Custom SEO titles, descriptions, keywords
- Automatic fallbacks to post title/summary
- Canonical URL support
- Meta robots configuration

### ✅ Open Graph Protocol
- Full OG protocol support
- Article-specific tags
- Custom OG images with dimensions
- Locale support

### ✅ Twitter Cards
- Summary and large image cards
- Creator attribution
- Image alt text

### ✅ Schema.org Structured Data
- BlogPosting schema
- BreadcrumbList navigation
- Author and Publisher info
- Reading time and word count

### ✅ Sitemaps
- Dynamic XML sitemaps
- Configurable priority/changefreq
- Smart priority based on engagement
- Multiple sitemap types (posts, categories, tags, authors)

### ✅ RSS/Atom Feeds
- Full Atom 1.0 feed
- RSS 2.0 feed
- Category-specific feeds
- Featured image enclosures

### ✅ Search Engine Integration
- Auto-ping Google on publish
- Auto-ping Bing on publish
- Manual ping API endpoint
- Async non-blocking pings

---

## 📡 API Endpoints

| Endpoint | Description | Cache |
|----------|-------------|-------|
| `/api/v1/seo/schema/<slug>/` | JSON-LD structured data | 24h |
| `/api/v1/seo/preview/<slug>/` | Complete SEO preview | 12h |
| `/api/v1/seo/slugs/` | All post slugs | 24h |
| `/api/v1/seo/ping/` | Manual search engine ping | - |
| `/api/v1/seo/site/` | Site-wide metadata | 24h |
| `/api/v1/seo/health/` | SEO health check | - |
| `/sitemap.xml` | XML sitemap | 12h |
| `/rss/` | Atom feed | 1h |
| `/rss.xml` | RSS 2.0 feed | 1h |
| `/robots.txt` | Robots directives | 12h |

---

## 🔌 Next.js Integration

### Fetch SEO Data

```typescript
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await fetch(`${API_URL}/api/v1/posts/${params.slug}/`)
    .then(r => r.json());
  
  return {
    title: post.seo.title,
    description: post.seo.description,
    openGraph: {
      title: post.open_graph.og_title,
      description: post.open_graph.og_description,
      images: [post.open_graph.og_image],
      type: 'article',
    },
    twitter: {
      card: post.twitter_card.card,
      title: post.twitter_card.title,
      images: [post.twitter_card.image],
    },
  };
}
```

### Add JSON-LD Schema

```typescript
export default async function BlogPost({ params }: Props) {
  const schema = await fetch(`${API_URL}/api/v1/seo/schema/${params.slug}/`)
    .then(r => r.json());
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      {/* Content */}
    </>
  );
}
```

### Generate Static Paths

```typescript
export async function generateStaticParams() {
  const { slugs } = await fetch(`${API_URL}/api/v1/seo/slugs/`)
    .then(r => r.json());
  
  return slugs.map((item: any) => ({ slug: item.slug }));
}
```

---

## 📊 Model Fields

### Post Model - SEO Fields

```python
# SEO
seo_title = CharField(max_length=70)
seo_description = CharField(max_length=160)
seo_keywords = CharField(max_length=255)
canonical_url = URLField()

# Open Graph
og_title = CharField(max_length=70)
og_description = CharField(max_length=200)
og_image = URLField()
og_type = CharField(default='article')

# Twitter
twitter_card = CharField(default='summary_large_image')

# Sitemap
sitemap_priority = DecimalField(default=0.8)
sitemap_changefreq = CharField(default='monthly')

# Structured Data
schema_org = JSONField(default=dict)
```

All fields are optional with smart fallbacks.

---

## 🧪 Testing

### Test SEO Health

```bash
curl http://localhost:8000/api/v1/seo/health/ | jq
```

Expected output:
```json
{
  "status": "healthy",
  "checks": {
    "sitemap_configured": true,
    "robots_txt_configured": true,
    "rss_feed_configured": true
  },
  "seo_coverage": {
    "total_published_posts": 150,
    "seo_title_coverage": "96.7%"
  }
}
```

### Validate Schema.org

```bash
# Get schema for a post
curl http://localhost:8000/api/v1/seo/schema/your-post-slug/ | jq

# Validate with Google Rich Results Test
# Visit: https://search.google.com/test/rich-results
```

### Test Search Engine Ping

```bash
curl -X POST http://localhost:8000/api/v1/seo/ping/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 🚀 Deployment

### 1. Environment Setup

```bash
# Production .env
SITE_URL=https://yourdomain.com
SITE_NAME=Your Blog
TWITTER_SITE=@yourhandle
AUTO_PING_SEARCH_ENGINES=True
SEO_PING_TOKEN=$(openssl rand -hex 32)
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Configure Site Settings

Django Admin → Site Settings:
- Set site name, description
- Upload default OG image (1200x630)
- Add Twitter handle
- Add Google verification code

### 4. Submit Sitemap

**Google Search Console:**
- Add property: `https://yourdomain.com`
- Submit sitemap: `https://yourdomain.com/sitemap.xml`

**Bing Webmaster:**
- Add site
- Submit sitemap: `https://yourdomain.com/sitemap.xml`

### 5. Verify

```bash
# Check health
curl https://yourdomain.com/api/v1/seo/health/

# Test sitemap
curl https://yourdomain.com/sitemap.xml

# Test RSS
curl https://yourdomain.com/rss/
```

---

## 📈 Performance

### Caching Strategy

- SEO endpoints: 12-24 hour cache
- Sitemap: 12 hour cache
- RSS feeds: 1 hour cache
- ETag support for conditional requests
- Cache-Control with stale-while-revalidate

### Expected Response Times

- Cached endpoints: < 100ms
- Sitemap (1000 posts): < 500ms
- RSS feed: < 200ms
- Search engine ping: Async (non-blocking)

---

## 🔧 Troubleshooting

### Sitemap Not Updating

```bash
# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Access sitemap
curl https://yourdomain.com/sitemap.xml
```

### Search Engine Ping Failing

```bash
# Check logs
tail -f logs/django.log | grep "search engines"

# Test manually
curl -X POST /api/v1/seo/ping/ -H "Authorization: Bearer TOKEN"
```

### Schema Validation Errors

```bash
# Test endpoint
curl /api/v1/seo/schema/post-slug/ | jq

# Validate with Google
# https://search.google.com/test/rich-results
```

---

## 📚 Documentation

- **[Full Implementation Guide](docs/SEO_BACKEND_IMPLEMENTATION.md)** - Complete documentation
- **[Launch Checklist](docs/SEO_CHECKLIST_BACKEND.md)** - Pre-launch checklist
- **[API Examples](docs/api_examples.md)** - API usage examples

---

## ✅ Checklist

Before going live:

- [ ] Migrations applied
- [ ] Environment variables set
- [ ] Site settings configured
- [ ] SEO health check passes
- [ ] Sitemap accessible
- [ ] RSS feed working
- [ ] Schema.org validates
- [ ] OG images displaying
- [ ] Search Console configured
- [ ] Automatic ping working

---

## 🎯 Success Metrics

### Technical SEO
- ✅ 95%+ SEO title coverage
- ✅ 95%+ SEO description coverage
- ✅ 100% valid schema.org markup
- ✅ All pages indexed within 48h

### Performance
- ✅ API response < 100ms (cached)
- ✅ Lighthouse SEO score 95+
- ✅ Core Web Vitals passing

---

## 🆘 Support

- **Issues:** Check [Troubleshooting](#troubleshooting) section
- **Documentation:** See [docs/](docs/) folder
- **Health Check:** `/api/v1/seo/health/`

---

## 📝 License

MIT License - See LICENSE file

---

**Status:** ✅ Production Ready

**Last Updated:** 2025-01-10

**Version:** 1.0.0
