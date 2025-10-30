# Phase 2: Implementation Checklist

**Project:** Django Blog API → Next.js SSG  
**Estimated Duration:** 2–3 weeks (1 full-time developer)

---

## Priority 1: Foundation (Days 1–3)

### Task 1.1: Project Setup & Dependencies
- [ ] Initialize Django project with PostgreSQL database
- [ ] Install dependencies: Django, DRF, Celery, Redis, Pillow, boto3, django-cors-headers
- [ ] Configure settings for dev/staging/production environments
- [ ] Set up environment variables (`.env` file)
- [ ] Configure CORS for Next.js frontend
- [ ] Set up Sentry for error tracking

**Acceptance:**
- Django server runs successfully
- Database connection works
- Environment variables load correctly

---

### Task 1.2: Data Models & Migrations
- [ ] Create `Post` model with all SEO fields (see Section 2.1)
- [ ] Create `Category` model (see Section 2.2)
- [ ] Create `Tag` model (see Section 2.3)
- [ ] Create `Author` model (see Section 2.4)
- [ ] Create `SiteSettings` singleton model (see Section 2.5)
- [ ] Create `Redirect` model (see Section 2.6)
- [ ] Add database indexes:
  - `Post.slug` (unique)
  - `Post.status` + `Post.published_at` (composite)
  - `Post.last_modified`
  - `Category.slug`, `Tag.slug`, `Author.slug` (unique)
- [ ] Run migrations
- [ ] Create initial SiteSettings record via data migration

**Acceptance:**
- All models created with correct fields and types
- Migrations run without errors
- Database indexes created

**Estimated time:** 1 day

---

### Task 1.3: Django Admin Basics
- [ ] Register all models in Django admin
- [ ] Customize `PostAdmin`:
  - List display: title, status, published_at, author
  - List filters: status, categories, tags, published_at
  - Search fields: title, slug, summary
  - Prepopulated fields: slug from title
  - Inline editing for categories and tags
- [ ] Add "Preview" button in PostAdmin (generates preview URL with JWT token)
- [ ] Add "Generate Slug" action
- [ ] Customize `SiteSettingsAdmin` (singleton pattern)
- [ ] Add basic image upload field for `featured_image`

**Acceptance:**
- All models visible in admin
- Can create/edit posts with slug auto-generation
- Preview button generates valid preview URL

**Estimated time:** 1 day

---

## Priority 2: Core API Endpoints (Days 4–7)

### Task 2.1: API Serializers
- [ ] Create `PostListSerializer` (minimal fields for list views)
- [ ] Create `PostDetailSerializer` (full fields including SEO metadata)
- [ ] Create `PostSlugSerializer` (slug, published_at, last_modified, canonical_url)
- [ ] Create `CategorySerializer`, `TagSerializer`, `AuthorSerializer`
- [ ] Create `SiteSettingsSerializer`
- [ ] Create `RedirectSerializer`
- [ ] Add computed fields:
  - `canonical_url` (computed from slug if not set)
  - `seo.title` (fallback logic)
  - `seo.description` (fallback logic)
  - `open_graph` (fallback logic)
  - `twitter_card` (fallback logic)

**Acceptance:**
- Serializers return correct JSON structure
- Fallback logic works for SEO fields

**Estimated time:** 1 day

---

### Task 2.2: Endpoint: GET /api/v1/posts/slugs/
- [ ] Create view with pagination
- [ ] Add query param: `since` (filter by last_modified)
- [ ] Add query param: `page_size` (default 1000)
- [ ] Add query param: `status` (default `published`)
- [ ] Return only: slug, published_at, last_modified, canonical_url
- [ ] Add ETag and Last-Modified headers
- [ ] Support If-Modified-Since conditional requests (return 304)
- [ ] Add Redis caching (TTL: 3600s)
- [ ] Add cache headers: `Cache-Control: public, max-age=3600`

**Acceptance:**
- Endpoint returns correct JSON structure
- Pagination works
- `since` filter works
- Conditional requests return 304
- Redis cache works

**Estimated time:** 0.5 day

---

### Task 2.3: Endpoint: GET /api/v1/posts/{slug}/
- [ ] Create detail view
- [ ] Return full post with all SEO metadata
- [ ] Precompute `schema_org` JSON-LD on save
- [ ] Add ETag and Last-Modified headers
- [ ] Support If-None-Match and If-Modified-Since (return 304)
- [ ] Add Redis caching (TTL: 300s, key includes last_modified)
- [ ] Add cache headers: `Cache-Control: public, max-age=300, s-maxage=3600`
- [ ] Return 404 if post not found or not published

**Acceptance:**
- Endpoint returns correct JSON structure with all SEO fields
- Conditional requests return 304
- Redis cache works
- 404 for unpublished posts

**Estimated time:** 1 day

---

### Task 2.4: Endpoint: GET /api/v1/posts/
- [ ] Create list view with pagination
- [ ] Add query params: `page`, `page_size`, `category`, `tag`, `author`, `year`, `ordering`, `search`
- [ ] Return paginated results with PostListSerializer
- [ ] Add Redis caching (TTL: 300s)
- [ ] Add cache headers: `Cache-Control: public, max-age=300`

**Acceptance:**
- Endpoint returns paginated list
- Filters work (category, tag, author, year)
- Ordering works
- Search works (basic, Phase 3 will improve)

**Estimated time:** 1 day

---

### Task 2.5: Endpoint: GET /api/v1/posts/{slug}/preview/
- [ ] Create preview view (same as detail but includes draft/scheduled posts)
- [ ] Validate JWT token from query param or Authorization header
- [ ] Return 401 if token invalid/expired
- [ ] Add response headers: `Cache-Control: private, no-cache, no-store`
- [ ] Add response header: `X-Robots-Tag: noindex, nofollow`

**Acceptance:**
- Preview endpoint returns draft posts with valid token
- Returns 401 with invalid token
- Never caches preview responses

**Estimated time:** 0.5 day

---

### Task 2.6: Endpoint: GET /api/v1/meta/site/
- [ ] Create view returning SiteSettings
- [ ] Add Redis caching (TTL: 86400s)
- [ ] Add cache headers: `Cache-Control: public, max-age=86400`

**Acceptance:**
- Endpoint returns site settings
- Cache works

**Estimated time:** 0.5 day

---

### Task 2.7: Endpoint: GET /api/v1/redirects/
- [ ] Create view returning all active redirects
- [ ] Add Redis caching (TTL: 3600s)
- [ ] Add cache headers: `Cache-Control: public, max-age=3600`

**Acceptance:**
- Endpoint returns all active redirects
- Cache works

**Estimated time:** 0.5 day

---

## Priority 3: Image Processing (Days 8–9)

### Task 3.1: Image Upload & Processing Pipeline
- [ ] Create `ImageProcessor` utility class
- [ ] On image upload:
  - Validate file type and size
  - Generate UUID filename
  - Create multiple sizes: 320w, 480w, 768w, 1024w, 1600w, 2048w
  - Generate WebP alternatives for each size
  - Generate OG image (1200×630)
  - Generate LQIP (20×20 base64)
  - Extract metadata (width, height, MIME type)
- [ ] Upload all variants to S3 with public-read ACL
- [ ] Set Cache-Control header: `public, max-age=31536000, immutable`
- [ ] Store image metadata in database (ImageField or JSONField)
- [ ] Return image object with url, srcset, lqip, og_image_url

**Acceptance:**
- Image upload generates all sizes and formats
- Images uploaded to S3 successfully
- Image object returned in API response with srcset

**Estimated time:** 1.5 days

---

### Task 3.2: CDN Configuration
- [ ] Set up CloudFront distribution pointing to S3 bucket
- [ ] Configure custom domain: `cdn.zaryableather.com`
- [ ] Enable Brotli/Gzip compression
- [ ] Enable HTTP/2
- [ ] Set cache TTL: 1 year

**Acceptance:**
- Images served via CDN
- Compression enabled
- Cache headers correct

**Estimated time:** 0.5 day

---

## Priority 4: Sitemap & RSS (Days 10–11)

### Task 4.1: Sitemap Generation
- [ ] Create Celery task: `regenerate_sitemap()`
- [ ] Generate sitemap index XML
- [ ] Generate individual sitemap files:
  - `posts-1.xml` (posts 1-1000)
  - `posts-2.xml` (posts 1001-2000)
  - `categories.xml`
  - `tags.xml`
  - `authors.xml`
  - `static.xml`
- [ ] Upload sitemap files to S3
- [ ] Create endpoint: `GET /sitemap.xml` (returns sitemap index or redirects to S3)
- [ ] Add priority calculation logic
- [ ] Trigger sitemap regeneration on post publish/update

**Acceptance:**
- Sitemap files generated correctly
- Sitemap index valid XML
- Sitemap uploaded to S3
- Endpoint returns sitemap index

**Estimated time:** 1 day

---

### Task 4.2: RSS Feed
- [ ] Create endpoint: `GET /rss.xml`
- [ ] Generate RSS 2.0 XML with last 50 posts
- [ ] Support query params: `category`, `tag`
- [ ] Add Redis caching (TTL: 1800s)
- [ ] Add cache headers: `Cache-Control: public, max-age=1800`

**Acceptance:**
- RSS feed valid XML
- Feed includes last 50 posts
- Filters work (category, tag)
- Cache works

**Estimated time:** 0.5 day

---

### Task 4.3: Robots.txt
- [ ] Create endpoint: `GET /robots.txt`
- [ ] Return `SiteSettings.robots_txt_content`
- [ ] Add environment check (staging returns `Disallow: /`)
- [ ] Add cache headers: `Cache-Control: public, max-age=86400`

**Acceptance:**
- Robots.txt endpoint works
- Content editable in admin
- Staging returns noindex robots.txt

**Estimated time:** 0.5 day

---

## Priority 5: Caching & Revalidation (Days 12–13)

### Task 5.1: Redis Caching Implementation
- [ ] Set up Redis connection
- [ ] Implement cache decorators for all endpoints
- [ ] Implement cache invalidation on post save/delete
- [ ] Implement cache invalidation on SiteSettings update
- [ ] Add cache key versioning

**Acceptance:**
- All endpoints use Redis cache
- Cache invalidation works on post update
- Cache hit rate >80%

**Estimated time:** 1 day

---

### Task 5.2: ETag & Last-Modified Headers
- [ ] Add ETag generation for post detail endpoint
- [ ] Add Last-Modified header for post detail endpoint
- [ ] Implement conditional request handling (If-None-Match, If-Modified-Since)
- [ ] Return 304 Not Modified when appropriate

**Acceptance:**
- ETag and Last-Modified headers present
- Conditional requests return 304

**Estimated time:** 0.5 day

---

### Task 5.3: Next.js Revalidation Webhook
- [ ] Create Celery task: `trigger_nextjs_revalidation(post_id)`
- [ ] Generate HMAC signature for webhook payload
- [ ] Send POST request to Next.js `/api/revalidate` endpoint
- [ ] Include affected paths (post, blog index, category, tag pages)
- [ ] Trigger webhook on post publish/update/delete
- [ ] Log webhook success/failure

**Acceptance:**
- Webhook sends correct payload with HMAC signature
- Next.js receives and validates webhook
- Affected pages revalidated

**Estimated time:** 0.5 day

---

## Priority 6: Preview & Redirects (Day 14)

### Task 6.1: Preview Token Generation
- [ ] Create utility function: `generate_preview_token(slug)`
- [ ] Use JWT with 30-minute expiration
- [ ] Add "Preview" button in Django admin
- [ ] Generate preview URL: `https://zaryableather.com/blog/{slug}/?preview=true&token={JWT}`

**Acceptance:**
- Preview button generates valid preview URL
- Token expires after 30 minutes

**Estimated time:** 0.5 day

---

### Task 6.2: Automatic Redirect Creation
- [ ] On post save, check `legacy_urls` field
- [ ] Create Redirect records for each legacy URL
- [ ] Set `status_code=301`, `active=True`

**Acceptance:**
- Redirects created automatically on post save
- Redirects visible in admin

**Estimated time:** 0.5 day

---

## Priority 7: Search & Indexes (Day 15)

### Task 7.1: Database Indexes
- [ ] Create GIN index on Post for full-text search
- [ ] Create trigram index for fuzzy search
- [ ] Test query performance

**Acceptance:**
- Indexes created
- Search queries <100ms

**Estimated time:** 0.5 day

---

### Task 7.2: Basic Search Implementation
- [ ] Implement search in `/api/v1/posts/?search=query`
- [ ] Use PostgreSQL full-text search
- [ ] Return results ranked by relevance

**Acceptance:**
- Search returns relevant results
- Search works on title, summary, content

**Estimated time:** 0.5 day

---

## Priority 8: Testing & Documentation (Days 16–18)

### Task 8.1: Unit Tests
- [ ] Write tests for all serializers
- [ ] Write tests for all API endpoints
- [ ] Write tests for image processing
- [ ] Write tests for sitemap generation
- [ ] Write tests for preview token validation
- [ ] Write tests for cache invalidation
- [ ] Achieve >80% code coverage

**Acceptance:**
- All tests pass
- Code coverage >80%

**Estimated time:** 2 days

---

### Task 8.2: Integration Tests
- [ ] Test full post publish workflow (create → save → cache invalidate → webhook)
- [ ] Test conditional requests (ETag, If-Modified-Since)
- [ ] Test preview mode end-to-end
- [ ] Test redirect creation
- [ ] Test sitemap generation

**Acceptance:**
- All integration tests pass

**Estimated time:** 0.5 day

---

### Task 8.3: API Documentation
- [ ] Generate OpenAPI/Swagger documentation
- [ ] Document all endpoints with examples
- [ ] Add authentication requirements
- [ ] Add rate limit information

**Acceptance:**
- API documentation accessible at `/api/docs/`
- All endpoints documented

**Estimated time:** 0.5 day

---

## Priority 9: Deployment & Monitoring (Days 19–21)

### Task 9.1: Docker & CI/CD
- [ ] Create Dockerfile for Django app
- [ ] Create docker-compose.yml for local dev
- [ ] Set up GitHub Actions or GitLab CI pipeline:
  - Lint (flake8, black)
  - Test (pytest)
  - Build Docker image
  - Deploy to staging
  - Deploy to production (manual approval)
- [ ] Configure environment variables in CI/CD

**Acceptance:**
- Docker image builds successfully
- CI/CD pipeline runs on every commit
- Deployment to staging works

**Estimated time:** 1 day

---

### Task 9.2: Production Deployment
- [ ] Deploy Django app to AWS ECS/Fargate or Heroku
- [ ] Set up PostgreSQL database (RDS or managed)
- [ ] Set up Redis (ElastiCache or managed)
- [ ] Set up Celery workers
- [ ] Configure S3 bucket and CloudFront
- [ ] Set up domain and SSL certificate
- [ ] Run database migrations
- [ ] Create superuser account

**Acceptance:**
- Django app running in production
- All services connected (database, Redis, S3)
- API accessible via HTTPS

**Estimated time:** 1 day

---

### Task 9.3: Monitoring & Logging
- [ ] Configure Sentry for error tracking
- [ ] Set up request logging (JSON format)
- [ ] Set up Prometheus metrics (optional)
- [ ] Configure uptime monitoring (UptimeRobot)
- [ ] Set up alerts for critical errors

**Acceptance:**
- Sentry captures errors
- Logs visible in CloudWatch or logging service
- Uptime monitoring active

**Estimated time:** 0.5 day

---

### Task 9.4: Performance Optimization
- [ ] Enable database connection pooling
- [ ] Optimize slow queries (use Django Debug Toolbar)
- [ ] Enable Redis connection pooling
- [ ] Configure Celery concurrency
- [ ] Load test API endpoints (use Locust or k6)
- [ ] Optimize image processing (use Celery for async processing)

**Acceptance:**
- API response time <200ms (p95)
- Image processing doesn't block requests
- Load test passes (1000 req/min)

**Estimated time:** 0.5 day

---

## Priority 10: Handover & Documentation (Day 21)

### Task 10.1: Handover Documentation
- [ ] Document deployment process
- [ ] Document environment variables
- [ ] Document common tasks (create post, regenerate sitemap)
- [ ] Document troubleshooting steps
- [ ] Create runbook for on-call

**Acceptance:**
- Handover documentation complete
- Next.js developer can integrate API

**Estimated time:** 0.5 day

---

### Task 10.2: Next.js Integration Support
- [ ] Provide API base URL and sample responses
- [ ] Provide REVALIDATE_SECRET and PREVIEW_SECRET
- [ ] Test Next.js integration with staging API
- [ ] Verify revalidation webhook works
- [ ] Verify preview mode works

**Acceptance:**
- Next.js successfully fetches data from API
- Revalidation webhook works
- Preview mode works

**Estimated time:** 0.5 day

---

## Summary

**Total estimated time:** 2–3 weeks (1 full-time developer)

**Critical path:**
1. Foundation (models, admin) → 3 days
2. Core API endpoints → 4 days
3. Image processing → 2 days
4. Sitemap & RSS → 2 days
5. Caching & revalidation → 2 days
6. Preview & redirects → 1 day
7. Search & indexes → 1 day
8. Testing & documentation → 3 days
9. Deployment & monitoring → 2 days
10. Handover → 1 day

**Assumptions:**
- Developer has experience with Django, DRF, PostgreSQL, Redis, Celery
- CI/CD infrastructure exists (GitHub Actions or similar)
- AWS account set up with S3, CloudFront, RDS, ElastiCache
- Next.js developer available for integration testing

**Risks:**
- Image processing may take longer if complex transformations needed
- Deployment may take longer if infrastructure setup required
- Testing may reveal issues requiring refactoring

**Mitigation:**
- Start with basic image processing (single size + WebP) and iterate
- Use managed services (Heroku, Vercel) to reduce infrastructure complexity
- Write tests early and run continuously

