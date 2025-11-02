# ⚡ Next.js Quick Start - Django API Integration

## 🚀 Setup (5 minutes)

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
REVALIDATE_SECRET=your-secret-key
```

### 3. Create Types
```typescript
// types/blog.ts
export interface Post {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content_html: string;
  featured_image: {
    url: string;
    alt: string;
    width: number;
    height: number;
  };
  author: { name: string };
  keywords: string[];
  reading_time_minutes: number;
  canonical_url: string;
  frontend_url: string;
  schema_org: any;
  ebay_product_url: string;
}
```

### 4. API Client
```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getPost(slug: string) {
  const res = await fetch(`${API_URL}/api/v1/posts/${slug}/`);
  return res.json();
}

export async function getPosts() {
  const res = await fetch(`${API_URL}/api/v1/posts/`);
  return res.json();
}
```

### 5. Blog Post Page
```typescript
// app/[slug]/page.tsx
import { getPost } from '@/lib/api';
import { Metadata } from 'next';

export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    title: post.seo.title,
    description: post.seo.description,
    keywords: post.keywords.join(', '),
    openGraph: {
      title: post.open_graph.og_title,
      description: post.open_graph.og_description,
      images: [post.open_graph.og_image],
    },
  };
}

export default async function PostPage({ params }) {
  const post = await getPost(params.slug);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(post.schema_org) }}
      />
      
      <article>
        <h1>{post.title}</h1>
        <p>{post.reading_time_minutes} min read</p>
        <div dangerouslySetInnerHTML={{ __html: post.content_html }} />
        
        {post.ebay_product_url && (
          <a href={post.ebay_product_url}>Buy on eBay</a>
        )}
      </article>
    </>
  );
}
```

## 📊 Available Fields

```typescript
// All fields from API
post.title                    // "Leather Care Guide"
post.slug                     // "leather-care-guide"
post.excerpt                  // Short preview
post.content_html             // Full HTML content
post.keywords                 // ["leather", "care"]
post.reading_time_minutes     // 5
post.word_count               // 1250
post.canonical_url            // Full URL
post.frontend_url             // Frontend URL
post.schema_org               // Complete schema
post.ebay_product_url         // eBay link
post.views_count              // View count
post.trending_score           // Trending score
```

## 🔄 ISR Revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidatePath } from 'next/cache';

export async function POST(request) {
  const { revalidate_path } = await request.json();
  revalidatePath(revalidate_path);
  return Response.json({ revalidated: true });
}
```

## ✅ Done!

Your Next.js app is now connected to Django API with:
- ✅ Full SEO support
- ✅ Schema.org structured data
- ✅ ISR revalidation
- ✅ All enhanced fields

See `NEXTJS_INTEGRATION_GUIDE.md` for complete documentation.
