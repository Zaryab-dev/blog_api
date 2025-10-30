# Next.js Blog Website - Build Instructions for AI Agent

## 🎯 Project Overview

You are building a **production-ready Next.js 14+ blog website** that consumes the Django REST API. The website must be fully SEO-optimized, fast, and ready for deployment.

---

## 📋 Project Requirements

### Core Features

1. **Blog Post Listing Page** (`/blog`)
   - Display all published blog posts
   - Show featured image, title, summary, author, date
   - Pagination support
   - Filter by category/tag
   - Responsive grid layout

2. **Single Blog Post Page** (`/blog/[slug]`)
   - Full post content with HTML rendering
   - Author information
   - Reading time
   - Published date
   - Category and tag badges
   - Related posts section
   - Social share buttons

3. **Category Pages** (`/category/[slug]`)
   - List all posts in a category
   - Category description
   - Post count

4. **Tag Pages** (`/tag/[slug]`)
   - List all posts with a tag
   - Tag description

5. **Search Page** (`/search`)
   - Search functionality with query parameter
   - Display search results
   - "No results" state

6. **Homepage** (`/`)
   - Hero section
   - Featured/trending posts
   - Recent posts
   - Categories showcase

7. **About Page** (`/about`)
   - Company/author information
   - Contact details

---

## 🔧 Technical Stack

### Required Technologies

```json
{
  "framework": "Next.js 14+",
  "language": "TypeScript",
  "styling": "Tailwind CSS",
  "ui": "shadcn/ui (optional but recommended)",
  "fonts": "next/font (Google Fonts)",
  "images": "next/image",
  "icons": "lucide-react or heroicons"
}
```

### Dependencies to Install

```bash
npm install @tailwindcss/typography
npm install lucide-react
npm install date-fns
npm install clsx tailwind-merge
```

---

## 🌐 API Integration

### API Base URL

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
```

### Environment Variables

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SITE_URL=http://localhost:3000
REVALIDATE_SECRET=your-secret-key
```

### Available API Endpoints

```
GET  /posts/                    # List all posts (paginated)
GET  /posts/{slug}/             # Get single post by slug
GET  /categories/               # List all categories
GET  /tags/                     # List all tags
GET  /authors/                  # List all authors
GET  /search/?q={query}         # Search posts
GET  /trending/                 # Get trending posts
```

### API Response Structure

**Post List Response:**
```json
{
  "count": 10,
  "next": "http://api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Post Title",
      "slug": "post-slug",
      "summary": "Post summary text",
      "featured_image": {
        "url": "https://supabase.co/storage/.../image.jpg",
        "alt": "Image description",
        "width": 1200,
        "height": 630
      },
      "author": {
        "name": "Author Name",
        "slug": "author-slug",
        "bio": "Author bio",
        "avatar_url": "https://...",
        "twitter_handle": "username"
      },
      "categories": [
        {
          "name": "Category Name",
          "slug": "category-slug"
        }
      ],
      "tags": [
        {
          "name": "Tag Name",
          "slug": "tag-slug"
        }
      ],
      "published_at": "2025-10-09T19:02:06Z",
      "reading_time": 5,
      "canonical_url": "https://..."
    }
  ]
}
```

**Post Detail Response:**
```json
{
  "id": "uuid",
  "title": "Post Title",
  "slug": "post-slug",
  "summary": "Post summary",
  "content_html": "<p>Full HTML content...</p>",
  "content_markdown": "Markdown content...",
  "featured_image": {...},
  "author": {...},
  "categories": [...],
  "tags": [...],
  "seo": {
    "title": "SEO Title",
    "description": "SEO Description",
    "meta_keywords": ["keyword1", "keyword2"],
    "meta_robots": "index, follow"
  },
  "open_graph": {
    "og_title": "OG Title",
    "og_description": "OG Description",
    "og_image": "https://...",
    "og_image_width": 1200,
    "og_image_height": 630,
    "og_type": "article",
    "og_url": "https://..."
  },
  "twitter_card": {
    "card": "summary_large_image",
    "title": "Twitter Title",
    "description": "Twitter Description",
    "image": "https://...",
    "creator": "@username",
    "site": "@sitename"
  },
  "schema_org": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Post Title",
    "datePublished": "2025-10-09T19:02:06+00:00",
    "dateModified": "2025-10-09T19:08:47+00:00",
    "author": {...},
    "publisher": {...}
  },
  "published_at": "2025-10-09T19:02:06Z",
  "last_modified": "2025-10-09T19:08:47Z",
  "reading_time": 5,
  "word_count": 1234,
  "canonical_url": "https://..."
}
```

---

## 🎨 SEO Requirements (CRITICAL)

### 1. Metadata Generation

Every page MUST have complete metadata using Next.js 14 Metadata API:

```typescript
import { Metadata } from 'next';

export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug);
  
  return {
    title: post.seo.title,
    description: post.seo.description,
    keywords: post.seo.meta_keywords,
    robots: post.seo.meta_robots,
    
    // Open Graph
    openGraph: {
      title: post.open_graph.og_title,
      description: post.open_graph.og_description,
      images: [
        {
          url: post.open_graph.og_image,
          width: post.open_graph.og_image_width,
          height: post.open_graph.og_image_height,
          alt: post.title,
        }
      ],
      type: 'article',
      publishedTime: post.published_at,
      modifiedTime: post.last_modified,
      authors: [post.author.name],
      url: post.open_graph.og_url,
    },
    
    // Twitter Card
    twitter: {
      card: 'summary_large_image',
      title: post.twitter_card.title,
      description: post.twitter_card.description,
      images: [post.twitter_card.image],
      creator: post.twitter_card.creator,
      site: post.twitter_card.site,
    },
    
    // Canonical URL
    alternates: {
      canonical: post.canonical_url,
    },
  };
}
```

### 2. Schema.org Structured Data

Add JSON-LD script to every blog post page:

```typescript
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify(post.schema_org)
  }}
/>
```

### 3. Sitemap Generation

Create `app/sitemap.ts`:

```typescript
import { MetadataRoute } from 'next';

export default async function sitemap(): MetadataRoute.Sitemap {
  const posts = await getAllPosts();
  
  const postUrls = posts.map((post) => ({
    url: `https://yourdomain.com/blog/${post.slug}`,
    lastModified: new Date(post.last_modified),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));
  
  return [
    {
      url: 'https://yourdomain.com',
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    {
      url: 'https://yourdomain.com/blog',
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    ...postUrls,
  ];
}
```

### 4. Robots.txt

Create `app/robots.ts`:

```typescript
import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/admin/'],
    },
    sitemap: 'https://yourdomain.com/sitemap.xml',
  };
}
```

### 5. Image Optimization

Use Next.js Image component for all images:

```typescript
import Image from 'next/image';

<Image
  src={post.featured_image.url}
  alt={post.featured_image.alt}
  width={post.featured_image.width}
  height={post.featured_image.height}
  priority={isAboveFold}
  className="rounded-lg"
/>
```

---

## 📁 Project Structure

```
app/
├── layout.tsx                 # Root layout with metadata
├── page.tsx                   # Homepage
├── blog/
│   ├── page.tsx              # Blog listing page
│   └── [slug]/
│       └── page.tsx          # Single blog post page
├── category/
│   └── [slug]/
│       └── page.tsx          # Category page
├── tag/
│   └── [slug]/
│       └── page.tsx          # Tag page
├── search/
│   └── page.tsx              # Search page
├── about/
│   └── page.tsx              # About page
├── sitemap.ts                # Dynamic sitemap
└── robots.ts                 # Robots.txt

components/
├── blog/
│   ├── PostCard.tsx          # Blog post card component
│   ├── PostContent.tsx       # Blog post content renderer
│   ├── PostMeta.tsx          # Post metadata (author, date, etc.)
│   ├── RelatedPosts.tsx      # Related posts section
│   └── ShareButtons.tsx      # Social share buttons
├── layout/
│   ├── Header.tsx            # Site header
│   ├── Footer.tsx            # Site footer
│   └── Navigation.tsx        # Navigation menu
└── ui/
    ├── Badge.tsx             # Badge component for tags/categories
    ├── Button.tsx            # Button component
    └── Card.tsx              # Card component

lib/
├── api.ts                    # API client functions
├── utils.ts                  # Utility functions
└── constants.ts              # Constants (API URL, etc.)

types/
└── blog.ts                   # TypeScript types for API responses
```

---

## 🎨 Design Requirements

### Color Scheme

Use a professional, readable color scheme:

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        // Add more colors as needed
      },
    },
  },
};
```

### Typography

- Use `@tailwindcss/typography` for blog content
- Headings: Bold, clear hierarchy
- Body text: 16-18px, line-height 1.6-1.8
- Code blocks: Monospace font with syntax highlighting

### Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Test on mobile, tablet, and desktop

### Layout

- Max content width: 1280px
- Blog post content: Max 720px for readability
- Generous whitespace
- Clear visual hierarchy

---

## ⚡ Performance Requirements

### 1. Static Site Generation (SSG)

Use `generateStaticParams` for all blog posts:

```typescript
export async function generateStaticParams() {
  const { results: posts } = await getPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}
```

### 2. Image Optimization

- Use `next/image` for all images
- Set proper width/height
- Use `priority` for above-the-fold images
- Lazy load below-the-fold images

### 3. Caching

```typescript
// Revalidate every hour
export const revalidate = 3600;

// Or use fetch with cache
fetch(url, {
  next: { revalidate: 3600 }
});
```

### 4. Code Splitting

- Use dynamic imports for heavy components
- Lazy load non-critical features

---

## 🔍 Search Functionality

### Search Page Implementation

```typescript
// app/search/page.tsx
export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q: string };
}) {
  const query = searchParams.q || '';
  const results = query ? await searchPosts(query) : [];
  
  return (
    <div>
      <h1>Search Results for "{query}"</h1>
      {results.length === 0 ? (
        <p>No results found</p>
      ) : (
        <div className="grid gap-6">
          {results.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### Search Input Component

```typescript
'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

export function SearchInput() {
  const [query, setQuery] = useState('');
  const router = useRouter();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query)}`);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search posts..."
        className="..."
      />
      <button type="submit">Search</button>
    </form>
  );
}
```

---

## 📱 Social Features

### Share Buttons

Implement share buttons for:
- Twitter/X
- Facebook
- LinkedIn
- Copy link

```typescript
export function ShareButtons({ post }: { post: Post }) {
  const url = post.canonical_url;
  const title = post.title;
  
  return (
    <div className="flex gap-2">
      <a
        href={`https://twitter.com/intent/tweet?url=${url}&text=${title}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        Share on Twitter
      </a>
      {/* Add more share buttons */}
    </div>
  );
}
```

---

## 🎯 Content Rendering

### HTML Content Rendering

Use `@tailwindcss/typography` for styled content:

```typescript
export function PostContent({ html }: { html: string }) {
  return (
    <div
      className="prose prose-lg max-w-none prose-headings:font-bold prose-a:text-blue-600 hover:prose-a:text-blue-800"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
```

### Code Syntax Highlighting

If content includes code blocks, consider adding syntax highlighting:

```bash
npm install react-syntax-highlighter
```

---

## 📊 Analytics Integration

### Page View Tracking

```typescript
'use client';

import { useEffect } from 'react';

export function PageViewTracker({ slug }: { slug: string }) {
  useEffect(() => {
    fetch(`${API_BASE_URL}/track-view/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slug }),
    });
  }, [slug]);
  
  return null;
}
```

---

## 🚀 Deployment Checklist

### Before Deployment

- [ ] All pages render correctly
- [ ] SEO metadata on all pages
- [ ] Images optimized with next/image
- [ ] Responsive design tested
- [ ] Search functionality working
- [ ] Social share buttons working
- [ ] 404 page created
- [ ] Loading states implemented
- [ ] Error boundaries added
- [ ] Environment variables configured

### Production Environment Variables

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
REVALIDATE_SECRET=production-secret-key
```

### Deployment Platforms

Recommended platforms:
- **Vercel** (easiest, built for Next.js)
- **Netlify**
- **AWS Amplify**
- **Railway**

---

## 🎨 UI Components to Build

### 1. PostCard Component

Display post preview in grid/list:
- Featured image
- Title
- Summary (truncated)
- Author avatar and name
- Published date
- Reading time
- Category badges
- Hover effects

### 2. PostMeta Component

Display post metadata:
- Author info with avatar
- Published date (formatted)
- Reading time
- Category and tag badges

### 3. RelatedPosts Component

Show 3-4 related posts:
- Same category
- Similar tags
- Exclude current post

### 4. Pagination Component

Navigate between pages:
- Previous/Next buttons
- Page numbers
- Disabled states

### 5. CategoryBadge Component

Display category/tag badges:
- Colored background
- Clickable link
- Hover effects

---

## 🔐 Error Handling

### Error Boundaries

Create error boundaries for graceful failures:

```typescript
// app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### 404 Page

```typescript
// app/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h1>404 - Page Not Found</h1>
      <a href="/">Go back home</a>
    </div>
  );
}
```

---

## 📝 TypeScript Types

Create complete type definitions in `types/blog.ts`:

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
  alt: string;
  width: number;
  height: number;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  summary: string;
  featured_image: FeaturedImage | null;
  author: Author;
  categories: Category[];
  tags: Tag[];
  published_at: string;
  reading_time: number;
  canonical_url: string;
}

export interface SEO {
  title: string;
  description: string;
  meta_keywords: string[];
  meta_robots: string;
}

export interface OpenGraph {
  og_title: string;
  og_description: string;
  og_image: string | null;
  og_image_width: number;
  og_image_height: number;
  og_type: string;
  og_url: string;
}

export interface TwitterCard {
  card: string;
  title: string;
  description: string;
  image: string | null;
  creator: string;
  site: string;
}

export interface PostDetail extends Post {
  content_html: string;
  content_markdown: string;
  seo: SEO;
  open_graph: OpenGraph;
  twitter_card: TwitterCard;
  schema_org: any;
  last_modified: string;
  status: string;
  allow_index: boolean;
  word_count: number;
  product_references: any[];
  locale: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

## 🎯 Key Success Criteria

### Must Have

✅ All pages render with proper SEO metadata  
✅ Blog posts display correctly with formatted content  
✅ Images load properly from Supabase  
✅ Search functionality works  
✅ Responsive design on all devices  
✅ Fast page load times (< 3s)  
✅ Proper error handling  
✅ Clean, professional design  

### Nice to Have

- Dark mode toggle
- Reading progress indicator
- Table of contents for long posts
- Comment section (if API supports)
- Newsletter subscription form
- Related posts recommendations
- Breadcrumb navigation

---

## 📚 Additional Resources

### Reference Files

1. **NEXTJS_INTEGRATION_GUIDE.md** - Complete API integration examples
2. **PHASE8_API_TEST_REPORT.md** - API endpoint documentation
3. **API Documentation** - http://localhost:8000/api/v1/docs/

### Helpful Links

- Next.js Documentation: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- TypeScript: https://www.typescriptlang.org/docs
- shadcn/ui: https://ui.shadcn.com

---

## 🚀 Getting Started

### Step 1: Create Next.js Project

```bash
npx create-next-app@latest blog-frontend
cd blog-frontend
```

Choose:
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ App Router
- ✅ Import alias (@/*)

### Step 2: Install Dependencies

```bash
npm install @tailwindcss/typography lucide-react date-fns clsx tailwind-merge
```

### Step 3: Configure Environment

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### Step 4: Create Type Definitions

Create `types/blog.ts` with all TypeScript interfaces

### Step 5: Create API Client

Create `lib/api.ts` with fetch functions

### Step 6: Build Pages

Start with:
1. Homepage
2. Blog listing page
3. Single blog post page
4. Category/tag pages
5. Search page

### Step 7: Add SEO

Implement metadata generation for all pages

### Step 8: Test & Deploy

Test thoroughly, then deploy to Vercel

---

## ✅ Final Checklist

Before considering the project complete:

- [ ] All pages created and working
- [ ] SEO metadata on every page
- [ ] Open Graph tags implemented
- [ ] Twitter Cards implemented
- [ ] Schema.org structured data added
- [ ] Sitemap generated
- [ ] Robots.txt configured
- [ ] Images optimized with next/image
- [ ] Responsive design tested
- [ ] Search functionality working
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] 404 page created
- [ ] Social share buttons working
- [ ] Performance optimized (Lighthouse score > 90)
- [ ] TypeScript types complete
- [ ] Code clean and documented
- [ ] Environment variables configured
- [ ] Ready for deployment

---

## 🎉 Expected Result

A fully functional, SEO-optimized Next.js blog website that:

✅ Loads fast (< 3s)  
✅ Ranks well in search engines  
✅ Looks professional and modern  
✅ Works perfectly on all devices  
✅ Integrates seamlessly with Django API  
✅ Ready for production deployment  

**Good luck building! 🚀**
