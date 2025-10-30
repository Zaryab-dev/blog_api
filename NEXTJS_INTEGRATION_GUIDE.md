# 🚀 Next.js Integration Guide - Django Blog API

Complete guide for integrating your Next.js blog with the Django Blog API deployed on AWS Elastic Beanstalk.

## 📍 API Base URL

```typescript
const API_BASE_URL = 'http://django-blog-api-prod.eba-uiwnbpqr.us-east-1.elasticbeanstalk.com/api/v1';
```

---

## 📚 Table of Contents

1. [Setup & Configuration](#setup--configuration)
2. [Core API Endpoints](#core-api-endpoints)
3. [Posts API](#posts-api)
4. [Categories & Tags](#categories--tags)
5. [Authors](#authors)
6. [Analytics & Tracking](#analytics--tracking)
7. [SEO Features](#seo-features)
8. [Search](#search)
9. [Homepage Carousel](#homepage-carousel)
10. [TypeScript Types](#typescript-types)
11. [API Client Examples](#api-client-examples)

---

## 🔧 Setup & Configuration

### 1. Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://django-blog-api-prod.eba-uiwnbpqr.us-east-1.elasticbeanstalk.com/api/v1
NEXT_PUBLIC_SITE_URL=https://your-blog.com
REVALIDATE_SECRET=your-secret-key
```

### 2. API Client Setup

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchAPI(endpoint: string, options = {}) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }

  return res.json();
}
```

---

## 📝 Core API Endpoints

### Health Check
```typescript
GET /healthcheck/

// Response
{
  "status": "healthy",
  "service": "django-blog-api"
}
```

### Site Settings
```typescript
GET /settings/

// Response
{
  "site_name": "Zaryab Leather Blog",
  "site_url": "http://...",
  "description": "...",
  "social_links": {...}
}
```

---

## 📰 Posts API

### 1. List All Posts (Paginated)

```typescript
GET /posts/
GET /posts/?page=2
GET /posts/?page_size=10

// Response
{
  "count": 9,
  "next": "http://.../api/v1/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Post Title",
      "slug": "post-title",
      "excerpt": "Short description...",
      "featured_image": "https://...",
      "author": {
        "id": 1,
        "username": "admin",
        "full_name": "Admin User",
        "avatar": "https://..."
      },
      "categories": [...],
      "tags": [...],
      "published_at": "2025-01-20T10:00:00Z",
      "reading_time": 5,
      "views_count": 150,
      "likes_count": 25
    }
  ]
}
```

**Next.js Example:**
```typescript
// app/blog/page.tsx
export default async function BlogPage({ searchParams }: { searchParams: { page?: string } }) {
  const page = searchParams.page || '1';
  const data = await fetchAPI(`/posts/?page=${page}`);
  
  return (
    <div>
      {data.results.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
      <Pagination count={data.count} />
    </div>
  );
}
```

### 2. Get Single Post (Full Details)

```typescript
GET /posts/{slug}/

// Response
{
  "id": 1,
  "title": "Post Title",
  "slug": "post-title",
  "content_html": "<p>Full HTML content...</p>",
  "content_markdown": "# Markdown content...",
  "excerpt": "Short description...",
  "featured_image": "https://...",
  "author": {...},
  "categories": [...],
  "tags": [...],
  "published_at": "2025-01-20T10:00:00Z",
  "last_modified": "2025-01-21T15:30:00Z",
  "reading_time": 5,
  "views_count": 150,
  "likes_count": 25,
  
  // 🆕 NEW: Related Posts
  "related_posts": [
    {
      "id": 2,
      "title": "Related Post",
      "slug": "related-post",
      "excerpt": "...",
      "featured_image": "https://...",
      "published_at": "2025-01-19T10:00:00Z"
    }
  ],
  
  // SEO Data
  "seo": {
    "title": "SEO Title",
    "description": "SEO Description",
    "keywords": ["keyword1", "keyword2"],
    "og_image": "https://..."
  },
  
  // Open Graph
  "open_graph": {
    "title": "OG Title",
    "description": "OG Description",
    "image": "https://...",
    "type": "article"
  },
  
  // Schema.org JSON-LD
  "schema_org": {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "...",
    "author": {...}
  },
  
  // Breadcrumbs
  "breadcrumb": [
    {"name": "Home", "url": "/"},
    {"name": "Blog", "url": "/blog"},
    {"name": "Post Title", "url": "/blog/post-title"}
  ],
  
  "canonical_url": "https://your-blog.com/blog/post-title",
  "allow_index": true,
  "locale": "en"
}
```

**Next.js Example:**
```typescript
// app/blog/[slug]/page.tsx
export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await fetchAPI(`/posts/${params.slug}/`);
  
  return (
    <article>
      <Head>
        <title>{post.seo.title}</title>
        <meta name="description" content={post.seo.description} />
        <script type="application/ld+json">
          {JSON.stringify(post.schema_org)}
        </script>
      </Head>
      
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.content_html }} />
      
      {/* Related Posts */}
      <section>
        <h2>Related Posts</h2>
        {post.related_posts.map((related) => (
          <PostCard key={related.id} post={related} />
        ))}
      </section>
    </article>
  );
}

// Generate static params
export async function generateStaticParams() {
  const data = await fetchAPI('/seo/slugs/');
  return data.slugs.map((slug: string) => ({ slug }));
}
```

### 3. Filter Posts

```typescript
// By Category
GET /posts/?category=leather-jackets

// By Tag
GET /posts/?tag=fashion

// By Author
GET /posts/?author=admin

// By Date
GET /posts/?published_after=2025-01-01
GET /posts/?published_before=2025-12-31

// Search
GET /posts/?search=leather

// Ordering
GET /posts/?ordering=-published_at  // Newest first
GET /posts/?ordering=views_count    // Most viewed
GET /posts/?ordering=-likes_count   // Most liked
```

---

## 🏷️ Categories & Tags

### Categories

```typescript
// List all categories
GET /categories/

// Response
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Leather Jackets",
      "slug": "leather-jackets",
      "description": "...",
      "post_count": 15,
      "image": "https://..."
    }
  ]
}

// Get single category
GET /categories/{slug}/

// Get posts in category
GET /posts/?category=leather-jackets
```

**Next.js Example:**
```typescript
// app/category/[slug]/page.tsx
export default async function CategoryPage({ params }: { params: { slug: string } }) {
  const [category, posts] = await Promise.all([
    fetchAPI(`/categories/${params.slug}/`),
    fetchAPI(`/posts/?category=${params.slug}`)
  ]);
  
  return (
    <div>
      <h1>{category.name}</h1>
      <p>{category.description}</p>
      {posts.results.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

### Tags

```typescript
// List all tags
GET /tags/

// Response
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "name": "Fashion",
      "slug": "fashion",
      "post_count": 8
    }
  ]
}

// Get posts by tag
GET /posts/?tag=fashion
```

---

## 👤 Authors

```typescript
// List all authors
GET /authors/

// Response
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "full_name": "Admin User",
      "bio": "...",
      "avatar": "https://...",
      "social_links": {
        "twitter": "https://twitter.com/...",
        "linkedin": "https://linkedin.com/..."
      },
      "post_count": 25
    }
  ]
}

// Get single author
GET /authors/{username}/

// Get author's posts
GET /posts/?author=admin
```

---

## 📊 Analytics & Tracking

### 1. Track Post View

```typescript
POST /track-view/

// Body
{
  "post_slug": "post-title",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1"  // Optional
}

// Response
{
  "success": true,
  "views_count": 151
}
```

**Next.js Example:**
```typescript
// components/PostView.tsx
'use client';

import { useEffect } from 'react';

export function PostView({ slug }: { slug: string }) {
  useEffect(() => {
    fetch(`${API_URL}/track-view/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        post_slug: slug,
        user_agent: navigator.userAgent
      })
    });
  }, [slug]);
  
  return null;
}
```

### 2. Trending Posts

```typescript
GET /trending/
GET /trending/?period=week  // day, week, month, year

// Response
{
  "period": "week",
  "posts": [
    {
      "id": 1,
      "title": "Trending Post",
      "slug": "trending-post",
      "views_count": 1500,
      "likes_count": 250,
      "featured_image": "https://..."
    }
  ]
}
```

### 3. Analytics Summary

```typescript
GET /analytics/summary/

// Response
{
  "total_posts": 9,
  "total_views": 15000,
  "total_likes": 2500,
  "trending_posts": [...],
  "popular_categories": [...]
}
```

---

## 🔍 Search

```typescript
GET /search/?q=leather
GET /search/?q=jacket&category=leather-jacketsts

// Response
{
  "query": "leather",
  "count": 5,
  "results": [
    {
      "id": 1,
      "title": "Leather Jacket Guide",
      "slug": "leather-jacket-guide",
      "excerpt": "...",
      "featured_image": "https://...",
      "relevance_score": 0.95
    }
  ]
}
```

**Next.js Example:**
```typescript
// app/search/page.tsx
export default async function SearchPage({ searchParams }: { searchParams: { q?: string } }) {
  const query = searchParams.q || '';
  const results = query ? await fetchAPI(`/search/?q=${encodeURIComponent(query)}`) : null;
  
  return (
    <div>
      <SearchInput defaultValue={query} />
      {results && (
        <div>
          <p>{results.count} results for "{query}"</p>
          {results.results.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
```

**Next.js Example:**
```typescript
// app/search/page.tsx
export default async function SearchPage({ searchParams }: { searchParams: { q?: string } }) {
  const query = searchParams.q || '';
  const results = query ? await fetchAPI(`/search/?q=${encodeURIComponent(query)}`) : null;
  
  return (
    <div>
      <SearchInput defaultValue={query} />
      {results && (
        <div>
          <p>{results.count} results for "{query}"</p>
          {results.results.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 💬 Comments API

### 1. List Comments for Post

```typescript
GET /comments/?post={post_id}

// Response
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "author_name": "John Doe",
      "author_email": "john@example.com",
      "content": "Great article!",
      "created_at": "2025-01-20T10:00:00Z",
      "is_approved": true
    }
  ]
}
```

### 2. Create Comment

```typescript
POST /comments/

// Body
{
  "post": 1,
  "author_name": "John Doe",
  "author_email": "john@example.com",
  "content": "Great article!"
}

// Response
{
  "id": 1,
  "message": "Comment submitted for moderation"
}
```

**Next.js Example:**
```typescript
// components/CommentForm.tsx
'use client';

export function CommentForm({ postId }: { postId: number }) {
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    await fetch(`${API_URL}/comments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        post: postId,
        author_name: formData.get('name'),
        author_email: formData.get('email'),
        content: formData.get('comment')
      })
    });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input name="name" placeholder="Your Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <textarea name="comment" placeholder="Your Comment" required />
      <button type="submit">Submit Comment</button>
    </form>
  );
}
```

---

## 📧 Newsletter Subscription

```typescript
POST /subscribe/

// Body
{
  "email": "user@example.com"
}

// Response
{
  "success": true,
  "message": "Successfully subscribed to newsletter"
}
```

**Next.js Example:**
```typescript
// components/Newsletter.tsx
'use client';

export function Newsletter() {
  const handleSubscribe = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    const res = await fetch(`${API_URL}/subscribe/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: formData.get('email') })
    });
    
    const data = await res.json();
    alert(data.message);
  };
  
  return (
    <form onSubmit={handleSubscribe}>
      <input name="email" type="email" placeholder="Enter your email" required />
      <button type="submit">Subscribe</button>
    </form>
  );
}
```

---

## 🎠 Homepage Carousel

```typescript
GET /homepage/carousel/

// Response
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "title": "Featured Post",
      "subtitle": "Subtitle text",
      "image": "https://...",
      "link": "/blog/featured-post",
      "order": 1,
      "is_active": true
    }
  ]
}
```

**Next.js Example:**
```typescript
// components/HeroCarousel.tsx
export async function HeroCarousel() {
  const data = await fetchAPI('/homepage/carousel/');
  
  return (
    <Carousel>
      {data.results.map((slide) => (
        <CarouselSlide key={slide.id}>
          <Image src={slide.image} alt={slide.title} />
          <h2>{slide.title}</h2>
          <p>{slide.subtitle}</p>
          <Link href={slide.link}>Read More</Link>
        </CarouselSlide>
      ))}
    </Carousel>
  );
}
```

---

## 🔗 SEO Features

### 1. Sitemap

```typescript
GET /sitemap.xml

// Returns XML sitemap for search engines
```

### 2. RSS Feed

```typescript
GET /rss.xml

// Returns RSS feed
```

### 3. Robots.txt

```typescript
GET /robots.txt

// Returns robots.txt
```

### 4. Get All Slugs (for Static Generation)

```typescript
GET /seo/slugs/

// Response
{
  "slugs": [
    "post-1",
    "post-2",
    "post-3"
  ]
}
```

### 5. Schema.org Data

```typescript
// Post Schema
GET /seo/schema/post/{slug}/

// Site Schema
GET /seo/schema/site/

// Author Schema
GET /seo/schema/author/{username}/

// Breadcrumbs Schema
GET /seo/schema/breadcrumbs/{slug}/
```

### 6. SEO Preview

```typescript
GET /seo/preview/{slug}/

// Response
{
  "title": "SEO Title",
  "description": "SEO Description",
  "og_image": "https://...",
  "twitter_card": "summary_large_image"
}
```

### 7. SEO Health Check

```typescript
GET /seo/health/

// Response
{
  "status": "healthy",
  "posts_with_seo": 45,
  "posts_without_seo": 5,
  "sitemap_status": "ok"
}
```

### 8. Category RSS Feed

```typescript
GET /feed/category/{slug}/

// Returns RSS feed for specific category
```

---

## 🖼️ Image Upload

```typescript
POST /images/upload/

// Body (multipart/form-data)
{
  "image": File
}

// Response
{
  "success": true,
  "url": "https://supabase.co/storage/...",
  "filename": "image.jpg"
}
```

**Next.js Example:**
```typescript
// components/ImageUpload.tsx
'use client';

export function ImageUpload() {
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('image', file);
    
    const res = await fetch(`${API_URL}/images/upload/`, {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    console.log('Uploaded:', data.url);
  };
  
  return <input type="file" accept="image/*" onChange={handleUpload} />;
}
```

---

## 📊 Advanced SEO Endpoints

### 1. Submit to Google Indexing API

```typescript
POST /seo/submit-google/{slug}/

// Response
{
  "success": true,
  "message": "URL submitted to Google"
}
```

### 2. Submit to IndexNow

```typescript
POST /seo/submit-indexnow/{slug}/

// Response
{
  "success": true,
  "search_engines": ["Bing", "Yandex"]
}
```

### 3. Bulk Submit to IndexNow

```typescript
POST /seo/bulk-submit/

// Body
{
  "slugs": ["post-1", "post-2", "post-3"]
}

// Response
{
  "success": true,
  "submitted": 3
}
```

### 4. Get SEO Score

```typescript
GET /seo/score/{slug}/

// Response
{
  "score": 85,
  "title_score": 90,
  "description_score": 80,
  "keywords_score": 85,
  "recommendations": ["Add more keywords", "Optimize images"]
}
```

### 5. Core Web Vitals

```typescript
GET /seo/core-web-vitals/{slug}/

// Response
{
  "lcp": 2.5,
  "fid": 100,
  "cls": 0.1,
  "performance_score": 90
}
```

### 6. E-E-A-T Signals

```typescript
GET /seo/eat-signals/{slug}/

// Response
{
  "expertise_score": 85,
  "authoritativeness_score": 90,
  "trustworthiness_score": 95,
  "author_credentials": true
}
```

### 7. Semantic Keywords

```typescript
GET /seo/semantic/{slug}/

// Response
{
  "primary_keywords": ["leather jacket", "fashion"],
  "related_keywords": ["style", "clothing"],
  "lsi_keywords": ["genuine leather", "jacket care"]
}
```

### 8. Engagement Metrics

```typescript
GET /seo/engagement/{slug}/

// Response
{
  "views": 1500,
  "avg_time_on_page": 180,
  "bounce_rate": 35,
  "social_shares": 45
}
```

### 9. Auto-Optimize SEO

```typescript
POST /seo/auto-optimize/{slug}/

// Response
{
  "success": true,
  "optimizations_applied": [
    "Updated meta description",
    "Added keywords",
    "Optimized title"
  ]
}
```

### 10. SEO Dashboard

```typescript
GET /seo/dashboard/

// Response
{
  "total_posts": 50,
  "avg_seo_score": 85,
  "posts_indexed": 45,
  "pending_optimization": 5,
  "top_performing_posts": [...]
}
```

---

## 🔔 Webhooks & Revalidation

### Next.js Revalidation Webhook

```typescript
POST /revalidate/

// Body
{
  "secret": "your-revalidate-secret",
  "paths": ["/blog/post-1", "/blog"]
}

// Response
{
  "success": true,
  "revalidated": ["/blog/post-1", "/blog"]
}
```

**Next.js API Route:**
```typescript
// app/api/revalidate/route.ts
import { revalidatePath } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  if (body.secret !== process.env.REVALIDATE_SECRET) {
    return Response.json({ message: 'Invalid secret' }, { status: 401 });
  }
  
  for (const path of body.paths) {
    revalidatePath(path);
  }
  
  return Response.json({ revalidated: true });
}
```

---

## 📈 Metrics & Monitoring

### Application Metrics

```typescript
GET /metrics/

// Response
{
  "requests_total": 10000,
  "requests_per_second": 10,
  "avg_response_time": 150,
  "error_rate": 0.5
}
```

### Full Health Check

```typescript
GET /healthcheck/full/

// Response
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "storage": "connected",
  "version": "1.0.0"
}
```

---

## 🔎 Popular Searches

```typescript
GET /popular-searches/

// Response
{
  "searches": [
    {
      "query": "leather jacket",
      "count": 150
    },
    {
      "query": "fashion tips",
      "count": 120
    }
  ]
}
```

---

## 📘 TypeScript Types

```typescript
// types/api.ts

export interface Post {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  content_html: string;
  content_markdown: string;
  featured_image: string;
  author: Author;
  categories: Category[];
  tags: Tag[];
  published_at: string;
  last_modified: string;
  reading_time: number;
  views_count: number;
  likes_count: number;
  related_posts: RelatedPost[];
  seo: SEO;
  open_graph: OpenGraph;
  schema_org: any;
  breadcrumb: Breadcrumb[];
  canonical_url: string;
  allow_index: boolean;
  locale: string;
}

export interface RelatedPost {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  featured_image: string;
  published_at: string;
}

export interface Author {
  id: number;
  username: string;
  full_name: string;
  bio: string;
  avatar: string;
  social_links: Record<string, string>;
  post_count: number;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  post_count: number;
  image: string;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
  post_count: number;
}

export interface SEO {
  title: string;
  description: string;
  keywords: string[];
  og_image: string;
}

export interface OpenGraph {
  title: string;
  description: string;
  image: string;
  type: string;
}

export interface Breadcrumb {
  name: string;
  url: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

## 🛠️ API Client Examples

### Complete API Client

```typescript
// lib/api-client.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL;

class BlogAPI {
  private async fetch(endpoint: string, options = {}) {
    const res = await fetch(`${API_URL}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  }

  // Posts
  async getPosts(page = 1, filters = {}) {
    const params = new URLSearchParams({ page: page.toString(), ...filters });
    return this.fetch(`/posts/?${params}`);
  }

  async getPost(slug: string) {
    return this.fetch(`/posts/${slug}/`);
  }

  async getRelatedPosts(slug: string) {
    const post = await this.getPost(slug);
    return post.related_posts;
  }

  // Categories
  async getCategories() {
    return this.fetch('/categories/');
  }

  async getCategory(slug: string) {
    return this.fetch(`/categories/${slug}/`);
  }

  // Tags
  async getTags() {
    return this.fetch('/tags/');
  }

  // Authors
  async getAuthors() {
    return this.fetch('/authors/');
  }

  async getAuthor(username: string) {
    return this.fetch(`/authors/${username}/`);
  }

  // Search
  async search(query: string, filters = {}) {
    const params = new URLSearchParams({ q: query, ...filters });
    return this.fetch(`/search/?${params}`);
  }

  // Analytics
  async trackView(slug: string) {
    return this.fetch('/track-view/', {
      method: 'POST',
      body: JSON.stringify({
        post_slug: slug,
        user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : ''
      })
    });
  }

  async getTrending(period = 'week') {
    return this.fetch(`/trending/?period=${period}`);
  }

  // Homepage
  async getCarousel() {
    return this.fetch('/homepage/carousel/');
  }

  // SEO
  async getAllSlugs() {
    return this.fetch('/seo/slugs/');
  }

  async getSiteSettings() {
    return this.fetch('/settings/');
  }
}

export const api = new BlogAPI();
```

### Usage in Next.js App Router

```typescript
// app/blog/page.tsx
import { api } from '@/lib/api-client';

export default async function BlogPage() {
  const posts = await api.getPosts();
  
  return (
    <div>
      {posts.results.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}

// app/blog/[slug]/page.tsx
export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await api.getPost(params.slug);
  
  return (
    <article>
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.content_html }} />
      
      {/* Related Posts Section */}
      {post.related_posts.length > 0 && (
        <section className="related-posts">
          <h2>Related Posts</h2>
          <div className="grid">
            {post.related_posts.map((related) => (
              <Link key={related.id} href={`/blog/${related.slug}`}>
                <img src={related.featured_image} alt={related.title} />
                <h3>{related.title}</h3>
                <p>{related.excerpt}</p>
              </Link>
            ))}
          </div>
        </section>
      )}
    </article>
  );
}

// Generate static params
export async function generateStaticParams() {
  const data = await api.getAllSlugs();
  return data.slugs.map((slug: string) => ({ slug }));
}
```

---

## 🎯 Quick Reference

### Most Used Endpoints

```typescript
// Homepage
GET /homepage/carousel/          // Hero carousel
GET /trending/?period=week       // Trending posts
GET /posts/?page_size=6          // Latest posts

// Blog List
GET /posts/?page=1               // All posts
GET /categories/                 // All categories
GET /tags/                       // All tags

// Single Post
GET /posts/{slug}/               // Full post with related_posts
POST /track-view/                // Track view
GET /comments/?post={id}         // Post comments

// Search
GET /search/?q=query             // Search posts
GET /popular-searches/           // Popular search terms

// SEO
GET /sitemap.xml                 // Sitemap
GET /rss.xml                     // RSS feed
GET /seo/slugs/                  // All slugs for static generation
GET /seo/score/{slug}/           // SEO score
POST /seo/submit-indexnow/{slug}/ // Submit to search engines

// User Interaction
POST /comments/                  // Submit comment
POST /subscribe/                 // Newsletter subscription
POST /images/upload/             // Upload image

// Monitoring
GET /healthcheck/                // Basic health check
GET /metrics/                    // Application metrics
```

---

## 🚀 Deployment Checklist

### Environment Setup
- [ ] Update `NEXT_PUBLIC_API_URL` in `.env.local`
- [ ] Set `REVALIDATE_SECRET` for webhooks
- [ ] Configure CORS on Django API

### Core Features
- [ ] Test all API endpoints
- [ ] Implement error handling
- [ ] Add loading states
- [ ] Set up ISR (Incremental Static Regeneration)
- [ ] Test pagination

### Content Features
- [ ] Test related posts feature
- [ ] Implement comments system
- [ ] Add newsletter subscription
- [ ] Test image upload
- [ ] Implement search functionality

### SEO & Analytics
- [ ] Implement analytics tracking
- [ ] Add SEO meta tags
- [ ] Test sitemap generation
- [ ] Configure RSS feeds
- [ ] Set up revalidation webhooks
- [ ] Test IndexNow submission

### Performance
- [ ] Implement caching strategy
- [ ] Optimize images
- [ ] Test Core Web Vitals
- [ ] Monitor API response times

### Testing
- [ ] Test on mobile devices
- [ ] Test all user interactions
- [ ] Verify SEO metadata
- [ ] Check accessibility

---

## 📞 Support

- **API Docs**: http://django-blog-api-prod.eba-uiwnbpqr.us-east-1.elasticbeanstalk.com/api/v1/docs/
- **GitHub**: https://github.com/Zaryab-dev/blog_api
- **API Base**: http://django-blog-api-prod.eba-uiwnbpqr.us-east-1.elasticbeanstalk.com/api/v1

---

**🎉 Your Next.js blog is now ready to integrate with the Django API!**
