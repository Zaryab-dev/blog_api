# 🚀 Next.js Integration Guide - Django Blog API

Complete guide for integrating the enhanced Django Blog API with Next.js frontend.

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [TypeScript Types](#typescript-types)
3. [API Client Setup](#api-client-setup)
4. [Fetching Posts](#fetching-posts)
5. [SEO Implementation](#seo-implementation)
6. [ISR Revalidation](#isr-revalidation)
7. [Components](#components)

---

## 🔌 API Overview

### Base URL
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend.zaryableather.com';
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/posts/` | GET | List all posts |
| `/api/v1/posts/{slug}/` | GET | Get post detail |
| `/api/v1/categories/` | GET | List categories |
| `/api/v1/tags/` | GET | List tags |
| `/api/v1/carousel/` | GET | Homepage carousel |

---

## 📝 TypeScript Types

Create `types/blog.ts`:

```typescript
export interface Author {
  id: string;
  name: string;
  slug: string;
  bio: string;
  avatar_url: string;
  twitter_handle: string;
  website: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  count_published_posts: number;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  description: string;
  count_published_posts: number;
}

export interface FeaturedImage {
  url: string;
  width: number;
  height: number;
  alt: string;
  srcset: Record<string, string>;
  lqip: string;
  webp_url: string;
  og_image_url: string;
}

export interface SEO {
  title: string;
  description: string;
  keywords: string;
  canonical_url: string;
  meta_robots: string;
  og_image: string;
  published_time: string;
  modified_time: string;
  author_name: string;
  locale: string;
}

export interface OpenGraph {
  og_type: string;
  og_title: string;
  og_description: string;
  og_url: string;
  og_site_name: string;
  og_locale: string;
  og_image: string;
  og_image_width: number;
  og_image_height: number;
  article_published_time: string;
  article_modified_time: string;
  article_author: string;
  article_section: string;
  article_tag: string[];
}

export interface TwitterCard {
  card: string;
  site: string;
  creator: string;
  title: string;
  description: string;
  image: string;
  image_alt: string;
}

export interface SchemaOrg {
  '@context': string;
  '@type': string;
  headline: string;
  description: string;
  url: string;
  datePublished: string;
  dateModified: string;
  author: {
    '@type': string;
    name: string;
    url: string;
  };
  publisher: {
    '@type': string;
    name: string;
    logo: {
      '@type': string;
      url: string;
    };
  };
  image?: {
    '@type': string;
    url: string;
    width: number;
    height: number;
  };
  keywords: string;
  wordCount: number;
  timeRequired: string;
  inLanguage: string;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  summary: string;
  excerpt: string;
  content_html: string;
  content_markdown: string;
  author: Author;
  categories: Category[];
  tags: Tag[];
  featured_image: FeaturedImage | null;
  
  // SEO Fields
  seo: SEO;
  open_graph: OpenGraph;
  twitter_card: TwitterCard;
  schema_org: SchemaOrg;
  breadcrumb: any;
  
  // URLs
  canonical_url: string;
  frontend_url: string;
  revalidate_path: string;
  
  // Metadata
  published_at: string;
  last_modified: string;
  status: string;
  allow_index: boolean;
  
  // Performance
  reading_time: number;
  reading_time_minutes: number;
  word_count: number;
  
  // Keywords
  keywords: string[];
  seo_score: number;
  structured_data_valid: boolean;
  main_image_alt_text: string;
  
  // Engagement
  views_count: number;
  likes_count: number;
  trending_score: number;
  
  // Other
  product_references: any[];
  ebay_product_url: string;
  locale: string;
  related_posts: Post[];
}

export interface PostListItem {
  id: string;
  title: string;
  slug: string;
  summary: string;
  excerpt: string;
  featured_image: FeaturedImage | null;
  author: Author;
  categories: Category[];
  tags: Tag[];
  published_at: string;
  reading_time: number;
  reading_time_minutes: number;
  canonical_url: string;
  frontend_url: string;
  views_count: number;
  likes_count: number;
  trending_score: number;
  keywords: string[];
  ebay_product_url: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

## 🔧 API Client Setup

Create `lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend.zaryableather.com';

export async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
```

---

## 📚 Fetching Posts

Create `lib/posts.ts`:

```typescript
import { fetchAPI } from './api';
import { Post, PostListItem, PaginatedResponse } from '@/types/blog';

// Get all posts (paginated)
export async function getPosts(page = 1, pageSize = 20) {
  return fetchAPI<PaginatedResponse<PostListItem>>(
    `/api/v1/posts/?page=${page}&page_size=${pageSize}`
  );
}

// Get single post by slug
export async function getPost(slug: string) {
  return fetchAPI<Post>(`/api/v1/posts/${slug}/`);
}

// Get posts by category
export async function getPostsByCategory(categorySlug: string, page = 1) {
  return fetchAPI<PaginatedResponse<PostListItem>>(
    `/api/v1/posts/?category=${categorySlug}&page=${page}`
  );
}

// Get posts by tag
export async function getPostsByTag(tagSlug: string, page = 1) {
  return fetchAPI<PaginatedResponse<PostListItem>>(
    `/api/v1/posts/?tag=${tagSlug}&page=${page}`
  );
}

// Search posts
export async function searchPosts(query: string, page = 1) {
  return fetchAPI<PaginatedResponse<PostListItem>>(
    `/api/v1/posts/?search=${encodeURIComponent(query)}&page=${page}`
  );
}

// Get trending posts
export async function getTrendingPosts(limit = 5) {
  return fetchAPI<PostListItem[]>(
    `/api/v1/posts/?ordering=-trending_score&page_size=${limit}`
  );
}
```

---

## 🎯 SEO Implementation

### Page Component with SEO

Create `app/[slug]/page.tsx`:

```typescript
import { Metadata } from 'next';
import { getPost } from '@/lib/posts';
import { notFound } from 'next/navigation';

interface Props {
  params: { slug: string };
}

// Generate metadata for SEO
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  if (!post) return {};

  return {
    title: post.seo.title,
    description: post.seo.description,
    keywords: post.keywords.join(', '),
    authors: [{ name: post.author.name }],
    openGraph: {
      title: post.open_graph.og_title,
      description: post.open_graph.og_description,
      url: post.open_graph.og_url,
      siteName: post.open_graph.og_site_name,
      images: [
        {
          url: post.open_graph.og_image,
          width: post.open_graph.og_image_width,
          height: post.open_graph.og_image_height,
          alt: post.main_image_alt_text,
        },
      ],
      locale: post.open_graph.og_locale,
      type: 'article',
      publishedTime: post.open_graph.article_published_time,
      modifiedTime: post.open_graph.article_modified_time,
      authors: [post.open_graph.article_author],
      tags: post.open_graph.article_tag,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.twitter_card.title,
      description: post.twitter_card.description,
      site: post.twitter_card.site,
      creator: post.twitter_card.creator,
      images: [post.twitter_card.image],
    },
    alternates: {
      canonical: post.canonical_url,
    },
    robots: {
      index: post.allow_index,
      follow: post.allow_index,
    },
  };
}

export default async function PostPage({ params }: Props) {
  const post = await getPost(params.slug);
  
  if (!post) notFound();

  return (
    <>
      {/* Schema.org JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(post.schema_org),
        }}
      />
      
      {/* Breadcrumb Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(post.breadcrumb),
        }}
      />

      <article>
        <header>
          <h1>{post.title}</h1>
          <div className="meta">
            <span>{post.author.name}</span>
            <time dateTime={post.published_at}>
              {new Date(post.published_at).toLocaleDateString()}
            </time>
            <span>{post.reading_time_minutes} min read</span>
          </div>
        </header>

        {post.featured_image && (
          <img
            src={post.featured_image.url}
            alt={post.main_image_alt_text}
            width={post.featured_image.width}
            height={post.featured_image.height}
          />
        )}

        <div dangerouslySetInnerHTML={{ __html: post.content_html }} />

        {post.ebay_product_url && (
          <a href={post.ebay_product_url} target="_blank" rel="noopener">
            🛒 Buy on eBay
          </a>
        )}

        <div className="keywords">
          {post.keywords.map((keyword) => (
            <span key={keyword}>{keyword}</span>
          ))}
        </div>
      </article>
    </>
  );
}
```

---

## 🔄 ISR Revalidation

### Revalidation API Route

Create `app/api/revalidate/route.ts`:

```typescript
import { revalidatePath } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get('secret');
  
  // Verify secret token
  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ message: 'Invalid token' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { revalidate_path } = body;

    if (!revalidate_path) {
      return NextResponse.json(
        { message: 'Missing revalidate_path' },
        { status: 400 }
      );
    }

    // Revalidate the path
    revalidatePath(revalidate_path);

    return NextResponse.json({
      revalidated: true,
      path: revalidate_path,
      now: Date.now(),
    });
  } catch (err) {
    return NextResponse.json(
      { message: 'Error revalidating', error: String(err) },
      { status: 500 }
    );
  }
}
```

### Django Signal to Trigger Revalidation

In Django `blog/signals.py`, add:

```python
def trigger_nextjs_revalidation(post):
    """Trigger Next.js ISR revalidation"""
    import requests
    from django.conf import settings
    
    nextjs_url = getattr(settings, 'NEXTJS_URL', '')
    revalidate_secret = getattr(settings, 'REVALIDATE_SECRET', '')
    
    if not nextjs_url or not revalidate_secret:
        return
    
    try:
        response = requests.post(
            f"{nextjs_url}/api/revalidate?secret={revalidate_secret}",
            json={'revalidate_path': post.revalidate_path},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to revalidate: {e}")
        return False
```

---

## 🎨 Components

### Post Card Component

Create `components/PostCard.tsx`:

```typescript
import Link from 'next/link';
import Image from 'next/image';
import { PostListItem } from '@/types/blog';

export function PostCard({ post }: { post: PostListItem }) {
  return (
    <article className="post-card">
      {post.featured_image && (
        <Link href={`/${post.slug}`}>
          <Image
            src={post.featured_image.url}
            alt={post.featured_image.alt}
            width={post.featured_image.width}
            height={post.featured_image.height}
            className="post-image"
          />
        </Link>
      )}
      
      <div className="post-content">
        <div className="post-meta">
          {post.categories.map((cat) => (
            <Link key={cat.id} href={`/category/${cat.slug}`}>
              {cat.name}
            </Link>
          ))}
        </div>
        
        <h2>
          <Link href={`/${post.slug}`}>{post.title}</Link>
        </h2>
        
        <p>{post.excerpt}</p>
        
        <div className="post-footer">
          <span>{post.author.name}</span>
          <span>{post.reading_time_minutes} min read</span>
          <span>{post.views_count} views</span>
        </div>
        
        {post.ebay_product_url && (
          <span className="ebay-badge">🛒 eBay</span>
        )}
      </div>
    </article>
  );
}
```

### Reading Time Component

```typescript
export function ReadingTime({ minutes }: { minutes: number }) {
  return (
    <div className="reading-time">
      <svg>📖</svg>
      <span>{minutes} min read</span>
    </div>
  );
}
```

### Keywords Component

```typescript
export function Keywords({ keywords }: { keywords: string[] }) {
  return (
    <div className="keywords">
      {keywords.map((keyword) => (
        <span key={keyword} className="keyword-tag">
          {keyword}
        </span>
      ))}
    </div>
  );
}
```

---

## 🚀 Complete Example

### Blog List Page

```typescript
// app/page.tsx
import { getPosts } from '@/lib/posts';
import { PostCard } from '@/components/PostCard';

export default async function HomePage() {
  const { results: posts } = await getPosts();

  return (
    <main>
      <h1>Latest Posts</h1>
      <div className="post-grid">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </main>
  );
}
```

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
REVALIDATE_SECRET=your-secret-key-here
```

---

## ✅ Checklist

- [ ] Install dependencies: `npm install`
- [ ] Create TypeScript types
- [ ] Set up API client
- [ ] Implement post fetching
- [ ] Add SEO metadata
- [ ] Set up ISR revalidation
- [ ] Create components
- [ ] Test API integration
- [ ] Deploy to production

---

**Complete integration ready!** 🎉
