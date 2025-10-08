# Django Blog API → Next.js SSG: Phase 1 Documentation

**Project:** Headless Blog CMS for Zaryab Leather  
**Version:** 1.0  
**Status:** Phase 1 Complete - Ready for Implementation

---

## 📋 Overview

This documentation package contains the complete Phase 1 architecture and design specifications for building a production-grade, SEO-first Django Blog API that powers a Next.js static site with Incremental Static Regeneration (ISR).

The system is designed to:
- Deliver exceptional SEO performance
- Support high-traffic blogs with aggressive caching
- Enable seamless content preview and publishing workflows
- Integrate with e-commerce platforms (Shopify/eBay)
- Scale to thousands of posts with minimal infrastructure cost

---

## 📁 Documentation Structure

```
docs/
├── README.md                      # This file - Start here
├── phase-1-architecture.md        # ⭐ Main architecture document
├── phase2-checklist.md            # Prioritized implementation tasks
├── handover.md                    # Setup guide & troubleshooting
├── api_examples.md                # Complete API request/response samples
└── diagrams/
    └── site-tree.txt              # Site architecture diagrams
```

---

## 🚀 Quick Start

### For Backend Developers

1. **Read the architecture document first:**
   - Start with [`phase-1-architecture.md`](./phase-1-architecture.md)
   - Review all 15 sections to understand the complete system

2. **Review the implementation checklist:**
   - Open [`phase2-checklist.md`](./phase2-checklist.md)
   - Follow tasks in priority order (Priority 1 → Priority 10)
   - Estimated timeline: 2–3 weeks for 1 full-time developer

3. **Set up your environment:**
   - Follow setup instructions in [`handover.md`](./handover.md)
   - Configure environment variables (see Section 2)
   - Install dependencies and run migrations

4. **Reference API examples:**
   - Use [`api_examples.md`](./api_examples.md) for exact JSON shapes
   - All endpoints include sample requests and responses

### For Frontend Developers (Next.js)

1. **Understand the API contract:**
   - Read Section 3 of [`phase-1-architecture.md`](./phase-1-architecture.md)
   - Review [`api_examples.md`](./api_examples.md) for complete examples

2. **Implement SSG/ISR:**
   - Use `/api/v1/posts/slugs/` for `getStaticPaths()`
   - Use `/api/v1/posts/{slug}/` for `getStaticProps()`
   - Set `revalidate: 300` (5 minutes) for ISR

3. **Implement revalidation webhook:**
   - Create `/pages/api/revalidate.js` endpoint
   - Validate HMAC signature (see Section 7.3 in architecture doc)
   - Revalidate affected paths on post publish/update

4. **Implement preview mode:**
   - Create `/pages/api/preview.js` endpoint
   - Validate JWT token from query parameter
   - Fetch draft posts from `/api/v1/posts/{slug}/preview/`

5. **Implement SEO meta tags:**
   - Follow rules in Section 4 of architecture doc
   - Use precomputed `schema_org` JSON-LD from API
   - Implement Open Graph and Twitter Card tags

---

## 📖 Key Documents

### 1. Phase 1 Architecture (`phase-1-architecture.md`)

**The definitive technical specification.** Contains:

- **Section 1:** URL patterns, slug rules, canonicalization strategy
- **Section 2:** Complete data model with all SEO fields
- **Section 3:** API contract with 8 endpoints and sample responses
- **Section 4:** SEO meta tag generation rules (title, description, OG, JSON-LD)
- **Section 5:** Image processing pipeline (srcset, WebP, LQIP, CDN)
- **Section 6:** Sitemap/robots/RSS generation strategy
- **Section 7:** Caching strategy (ETag, Redis, ISR hooks)
- **Section 8:** Preview tokens and staging environment
- **Section 9:** Redirects and legacy URL handling
- **Section 10:** Search strategy (Phase 2)
- **Section 11:** Monitoring, logging, and analytics
- **Section 12:** Security and rate limiting
- **Section 13:** CI/CD and deployment hooks
- **Section 14:** Acceptance criteria and QA tests
- **Section 15:** How to use this documentation

**Read this first.** Everything else references this document.

---

### 2. Phase 2 Checklist (`phase2-checklist.md`)

**Your implementation roadmap.** Contains:

- 10 priority groups with 40+ specific tasks
- Estimated time for each task
- Acceptance criteria for each task
- Dependencies and critical path
- Total estimated timeline: 2–3 weeks

**Use this as your sprint plan.** Check off tasks as you complete them.

---

### 3. Handover Notes (`handover.md`)

**Your operational guide.** Contains:

- Local development setup instructions
- Environment variables and secrets
- API integration guide for Next.js
- Common tasks (create post, regenerate sitemap, create redirect)
- Troubleshooting guide (API errors, images not loading, webhook failures)
- Deployment process (staging and production)
- Monitoring and alerts setup
- Contact information and resources

**Reference this when setting up or troubleshooting.**

---

### 4. API Examples (`api_examples.md`)

**Your API reference.** Contains:

- Complete request/response examples for all 10 endpoints
- HTTP headers (Cache-Control, ETag, Last-Modified)
- Query parameters and filters
- Error responses (401, 404, 429)
- Webhook payload examples with HMAC signatures

**Use this when implementing API clients or testing.**

---

### 5. Site Architecture Diagrams (`diagrams/site-tree.txt`)

**Visual reference.** Contains:

- URL structure tree
- API architecture diagram
- Data flow diagram (Django → Celery → Next.js)
- Caching architecture (CDN → Redis → Database)
- Image processing pipeline
- SEO data flow
- Deployment architecture

**Use this to understand system interactions.**

---

## 🎯 Key Decisions & Rationale

### URL Pattern: `/blog/{slug}/` (NOT `/blog/{yyyy}/{mm}/{dd}/{slug}/`)

**Why:** Shorter URLs are more shareable and don't make content appear dated. Publish date is still exposed via schema.org metadata for SEO.

### Pagination: Query parameter `?page=2` (NOT `/page/2/`)

**Why:** Simpler to implement, standard REST practice, easier to handle in Next.js dynamic routes.

### ISR Revalidate: 300 seconds (5 minutes)

**Why:** Balances content freshness with API load and build costs. Use on-demand revalidation via webhook for immediate updates.

### Image Sizes: 320w, 480w, 768w, 1024w, 1600w, 2048w

**Why:** Covers all common device sizes from mobile to retina displays. WebP format for modern browsers with JPEG fallback.

### Cache TTLs:
- **Post detail:** 5 min browser, 1 hour CDN
- **Slug list:** 1 hour (for incremental builds)
- **Images:** 1 year (immutable URLs with UUID)

**Why:** Aggressive caching reduces API load while maintaining reasonable freshness. Immutable image URLs enable long-term caching.

### Preview Token: JWT with 30-minute expiration

**Why:** Secure, stateless, and sufficient time for content review without leaving preview links exposed indefinitely.

### Sitemap: Background generation + S3 hosting

**Why:** Avoids blocking requests, scales to thousands of posts, and leverages CDN for fast delivery.

---

## ✅ Acceptance Criteria

Phase 1 is complete when:

- [x] Architecture document exists and is comprehensive
- [x] All 8 API endpoints are specified with sample JSON
- [x] SEO meta tag rules are explicit and unambiguous
- [x] Image processing pipeline is fully specified
- [x] Sitemap/robots/RSS strategy is defined
- [x] Caching strategy includes ETag, Redis, and ISR
- [x] Preview token mechanism is specified with JWT example
- [x] Redirect strategy is defined with API contract
- [x] Phase 2 checklist is prioritized with time estimates
- [x] Handover documentation includes setup and troubleshooting
- [x] API examples include all endpoints with complete requests/responses
- [x] Diagrams illustrate system architecture and data flow

**Status: ✅ All criteria met. Ready for Phase 2 implementation.**

---

## 🔧 Technology Stack

### Backend
- **Framework:** Django 4.2+ with Django REST Framework
- **Database:** PostgreSQL 14+ (with full-text search)
- **Cache:** Redis 7+
- **Task Queue:** Celery with Redis broker
- **Image Processing:** Pillow (PIL)
- **Storage:** AWS S3 + CloudFront CDN
- **Authentication:** JWT (for preview tokens)
- **Error Tracking:** Sentry

### Frontend (Next.js)
- **Framework:** Next.js 13+ (App Router or Pages Router)
- **Rendering:** SSG with ISR (Incremental Static Regeneration)
- **Image Optimization:** Next.js Image component
- **Deployment:** Vercel or Netlify

### Infrastructure
- **Hosting:** AWS ECS/Fargate or Heroku (Django), Vercel (Next.js)
- **CDN:** CloudFront or Cloudflare
- **Monitoring:** Sentry, CloudWatch, UptimeRobot
- **CI/CD:** GitHub Actions or GitLab CI

---

## 📊 Performance Targets

- **API Response Time:** <200ms (p95)
- **Image Load Time:** <1s (with LQIP placeholder)
- **Largest Contentful Paint (LCP):** <2.5s
- **Cumulative Layout Shift (CLS):** <0.1
- **First Input Delay (FID):** <100ms
- **Cache Hit Rate:** >80%
- **Sitemap Generation:** <30s for 10,000 posts

---

## 🔐 Security Considerations

- **HTTPS:** Enforced with HSTS header
- **Rate Limiting:** 100-300 requests/hour per IP for public endpoints
- **Preview Tokens:** JWT with 30-minute expiration
- **Webhook Signatures:** HMAC-SHA256 validation
- **Input Validation:** Slug regex, HTML sanitization
- **CORS:** Restricted to Next.js domain
- **Secrets:** Environment variables, never committed to repo

---

## 📈 Scalability

**Designed to handle:**
- 10,000+ published posts
- 1,000+ requests/minute
- 100+ concurrent users in admin
- 50+ posts published per day

**Scaling strategies:**
- Aggressive caching (CDN + Redis)
- Database read replicas (if needed)
- Celery worker horizontal scaling
- S3 + CloudFront for static assets
- Next.js edge caching (Vercel/Cloudflare)

---

## 🚦 Next Steps

### Immediate (Week 1)
1. Review all documentation
2. Set up development environment
3. Start Priority 1 tasks (Foundation)
4. Create data models and migrations

### Short-term (Weeks 2-3)
1. Implement core API endpoints
2. Build image processing pipeline
3. Implement sitemap generation
4. Set up caching and revalidation

### Medium-term (Week 4)
1. Write tests (unit + integration)
2. Deploy to staging
3. Integrate with Next.js frontend
4. Test end-to-end workflows

### Long-term (Phase 3)
1. Advanced search (Elasticsearch)
2. Multi-language support (i18n)
3. Performance optimization
4. Advanced analytics dashboard

---

## 📞 Support & Resources

### Documentation
- Django REST Framework: https://www.django-rest-framework.org/
- Next.js ISR: https://nextjs.org/docs/basic-features/data-fetching/incremental-static-regeneration
- Schema.org Article: https://schema.org/Article
- Open Graph Protocol: https://ogp.me/

### Tools
- Google Search Console: https://search.google.com/search-console
- Google Rich Results Test: https://search.google.com/test/rich-results
- AWS Pricing Calculator: https://calculator.aws

### Community
- Django Discord: https://discord.gg/django
- Next.js Discord: https://discord.gg/nextjs

---

## 📝 Version History

- **v1.0** (2025) - Initial Phase 1 architecture and specifications

---

## 📄 License

This documentation is proprietary and confidential. For internal use only.

---

**Ready to build? Start with [`phase-1-architecture.md`](./phase-1-architecture.md) and [`phase2-checklist.md`](./phase2-checklist.md).**

For questions or clarifications, refer to the main architecture document or contact the project team.
