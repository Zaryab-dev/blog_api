# 🎯 Enhanced Fields Integration Guide

Quick guide for integrating the 10 new enhanced fields into your existing Next.js frontend.

## 📊 New Fields Overview

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `keywords` | string[] | SEO keywords | `["leather", "care"]` |
| `excerpt` | string | Short preview | `"Learn how to..."` |
| `reading_time_minutes` | number | Reading time | `5` |
| `frontend_url` | string | Public URL | `"https://zaryableather.com/post"` |
| `canonical_url` | string | SEO canonical | `"https://zaryableather.com/post"` |
| `schema_org` | object | Complete schema | `{@type: "BlogPosting"}` |
| `ebay_product_url` | string | eBay link | `"https://ebay.com/itm/123"` |
| `structured_data_valid` | boolean | Schema valid | `true` |
| `main_image_alt_text` | string | Image alt | `"Leather jacket"` |
| `revalidate_path` | string | ISR path | `"/post-slug"` |

---

## 🔧 Update TypeScript Types

Add to your existing `Post` interface:

```typescript
// types/blog.ts
export interface Post {
  // ... existing fields ...
  
  // NEW: Enhanced fields
  keywords: string[];
  excerpt: string;
  reading_time_minutes: number;
  frontend_url: string;
  canonical_url: string;
  schema_org: SchemaOrg;
  ebay_product_url: string;
  structured_data_valid: boolean;
  main_image_alt_text: string;
  revalidate_path: string;
}
```

---

## 1️⃣ Keywords Integration

### Display Keywords as Tags

```tsx
// components/Keywords.tsx
export function Keywords({ keywords }: { keywords: string[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {keywords.map((keyword) => (
        <span
          key={keyword}
          className="px-3 py-1 bg-gray-100 rounded-full text-sm"
        >
          {keyword}
        </span>
      ))}
    </div>
  );
}

// Usage in post page
<Keywords keywords={post.keywords} />
```

### Use in SEO Meta Tags

```tsx
// app/[slug]/page.tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    keywords: post.keywords.join(', '), // ✅ Use keywords array
    // ... other metadata
  };
}
```

---

## 2️⃣ Excerpt Integration

### Use for Post Previews

```tsx
// components/PostCard.tsx
export function PostCard({ post }) {
  return (
    <article>
      <h2>{post.title}</h2>
      <p className="text-gray-600">{post.excerpt}</p> {/* ✅ Use excerpt */}
      <Link href={`/${post.slug}`}>Read more</Link>
    </article>
  );
}
```

### Use in Meta Description

```tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    description: post.excerpt, // ✅ Use excerpt for meta
    openGraph: {
      description: post.excerpt,
    },
  };
}
```

---

## 3️⃣ Reading Time Integration

### Display Reading Time

```tsx
// components/ReadingTime.tsx
export function ReadingTime({ minutes }: { minutes: number }) {
  return (
    <div className="flex items-center gap-2 text-gray-600">
      <svg className="w-4 h-4">📖</svg>
      <span>{minutes} min read</span>
    </div>
  );
}

// Usage
<ReadingTime minutes={post.reading_time_minutes} />
```

### In Post Header

```tsx
<header>
  <h1>{post.title}</h1>
  <div className="flex gap-4 text-sm text-gray-600">
    <span>{post.author.name}</span>
    <span>{post.reading_time_minutes} min read</span> {/* ✅ */}
    <time>{new Date(post.published_at).toLocaleDateString()}</time>
  </div>
</header>
```

---

## 4️⃣ Frontend URL Integration

### Use for Canonical Links

```tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    alternates: {
      canonical: post.frontend_url, // ✅ Use frontend_url
    },
  };
}
```

### Use in Social Sharing

```tsx
// components/ShareButtons.tsx
export function ShareButtons({ post }) {
  const shareUrl = post.frontend_url; // ✅ Use frontend_url
  
  return (
    <div>
      <a href={`https://twitter.com/intent/tweet?url=${shareUrl}`}>
        Share on Twitter
      </a>
      <a href={`https://facebook.com/sharer/sharer.php?u=${shareUrl}`}>
        Share on Facebook
      </a>
    </div>
  );
}
```

---

## 5️⃣ Canonical URL Integration

### Add to Head

```tsx
// app/[slug]/page.tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    alternates: {
      canonical: post.canonical_url, // ✅ Canonical URL
    },
  };
}
```

---

## 6️⃣ Schema.org Integration

### Add JSON-LD to Page

```tsx
// app/[slug]/page.tsx
export default async function PostPage({ params }) {
  const post = await getPost(params.slug);

  return (
    <>
      {/* ✅ Add schema.org structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(post.schema_org),
        }}
      />
      
      <article>
        {/* Post content */}
      </article>
    </>
  );
}
```

### Validate Schema

```tsx
// Check if schema is valid
{post.structured_data_valid && (
  <script
    type="application/ld+json"
    dangerouslySetInnerHTML={{ __html: JSON.stringify(post.schema_org) }}
  />
)}
```

---

## 7️⃣ eBay Product URL Integration

### Display eBay Link

```tsx
// components/EbayLink.tsx
export function EbayLink({ url }: { url: string }) {
  if (!url) return null;
  
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      🛒 Buy on eBay
    </a>
  );
}

// Usage in post page
{post.ebay_product_url && (
  <EbayLink url={post.ebay_product_url} />
)}
```

### Show in Post Card

```tsx
// components/PostCard.tsx
export function PostCard({ post }) {
  return (
    <article>
      <h2>{post.title}</h2>
      <p>{post.excerpt}</p>
      
      {/* ✅ Show eBay badge if product link exists */}
      {post.ebay_product_url && (
        <span className="inline-flex items-center gap-1 text-sm text-blue-600">
          🛒 Available on eBay
        </span>
      )}
    </article>
  );
}
```

---

## 8️⃣ Structured Data Valid Integration

### Show Validation Badge (Admin/Debug)

```tsx
// Only show in development
{process.env.NODE_ENV === 'development' && (
  <div className="fixed bottom-4 right-4 bg-white p-2 rounded shadow">
    Schema Valid: {post.structured_data_valid ? '✅' : '❌'}
  </div>
)}
```

### Conditional Schema Rendering

```tsx
{post.structured_data_valid && (
  <script
    type="application/ld+json"
    dangerouslySetInnerHTML={{ __html: JSON.stringify(post.schema_org) }}
  />
)}
```

---

## 9️⃣ Main Image Alt Text Integration

### Use for Featured Image

```tsx
// app/[slug]/page.tsx
{post.featured_image && (
  <Image
    src={post.featured_image.url}
    alt={post.main_image_alt_text} {/* ✅ Use main_image_alt_text */}
    width={post.featured_image.width}
    height={post.featured_image.height}
    priority
  />
)}
```

### Use in OpenGraph

```tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    openGraph: {
      images: [
        {
          url: post.open_graph.og_image,
          alt: post.main_image_alt_text, // ✅ Use for OG image alt
        },
      ],
    },
  };
}
```

---

## 🔟 Revalidate Path Integration

### ISR Revalidation API

```tsx
// app/api/revalidate/route.ts
import { revalidatePath } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get('secret');
  
  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ message: 'Invalid token' }, { status: 401 });
  }

  const body = await request.json();
  const { revalidate_path } = body; // ✅ Use revalidate_path from API

  if (!revalidate_path) {
    return NextResponse.json({ message: 'Missing path' }, { status: 400 });
  }

  revalidatePath(revalidate_path);

  return NextResponse.json({
    revalidated: true,
    path: revalidate_path,
    now: Date.now(),
  });
}
```

### Django Integration

Add to Django `.env`:
```bash
NEXTJS_URL=https://zaryableather.com
REVALIDATE_SECRET=your-secret-key
```

---

## 🎨 Complete Example

### Full Post Page with All Fields

```tsx
// app/[slug]/page.tsx
import { getPost } from '@/lib/posts';
import { Metadata } from 'next';
import Image from 'next/image';
import { Keywords } from '@/components/Keywords';
import { ReadingTime } from '@/components/ReadingTime';
import { EbayLink } from '@/components/EbayLink';

export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    title: post.seo.title,
    description: post.excerpt, // ✅ excerpt
    keywords: post.keywords.join(', '), // ✅ keywords
    alternates: {
      canonical: post.canonical_url, // ✅ canonical_url
    },
    openGraph: {
      images: [
        {
          url: post.open_graph.og_image,
          alt: post.main_image_alt_text, // ✅ main_image_alt_text
        },
      ],
    },
  };
}

export default async function PostPage({ params }) {
  const post = await getPost(params.slug);

  return (
    <>
      {/* ✅ schema_org */}
      {post.structured_data_valid && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(post.schema_org) }}
        />
      )}

      <article>
        <header>
          <h1>{post.title}</h1>
          
          <div className="flex gap-4">
            <span>{post.author.name}</span>
            <ReadingTime minutes={post.reading_time_minutes} /> {/* ✅ */}
          </div>
        </header>

        {post.featured_image && (
          <Image
            src={post.featured_image.url}
            alt={post.main_image_alt_text} {/* ✅ */}
            width={post.featured_image.width}
            height={post.featured_image.height}
          />
        )}

        <div dangerouslySetInnerHTML={{ __html: post.content_html }} />

        {/* ✅ ebay_product_url */}
        {post.ebay_product_url && (
          <EbayLink url={post.ebay_product_url} />
        )}

        {/* ✅ keywords */}
        <Keywords keywords={post.keywords} />
      </article>
    </>
  );
}
```

---

## ✅ Integration Checklist

- [ ] Update TypeScript types with new fields
- [ ] Use `keywords` for SEO meta tags
- [ ] Display `excerpt` in post cards
- [ ] Show `reading_time_minutes` in post header
- [ ] Use `frontend_url` for sharing
- [ ] Add `canonical_url` to metadata
- [ ] Render `schema_org` JSON-LD
- [ ] Display `ebay_product_url` if present
- [ ] Use `main_image_alt_text` for images
- [ ] Set up ISR with `revalidate_path`
- [ ] Test all fields in production

---

## 🚀 Quick Test

```bash
# Fetch a post and check new fields
curl https://backend.zaryableather.com/api/v1/posts/your-slug/ | jq '{
  keywords,
  excerpt,
  reading_time_minutes,
  frontend_url,
  canonical_url,
  ebay_product_url,
  structured_data_valid,
  main_image_alt_text,
  revalidate_path
}'
```

---

**All enhanced fields ready for integration!** 🎉
