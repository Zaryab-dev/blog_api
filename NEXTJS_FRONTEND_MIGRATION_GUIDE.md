# 🚀 Next.js Frontend Migration Guide - New Domain URLs

Complete guide to update your existing Next.js frontend with the new backend and frontend URLs.

---

## 📋 Overview

**Old URLs:**
- Backend: `http://localhost:8000` or old domain
- Frontend: `http://localhost:3000` or old domain

**New URLs:**
- Backend: `https://backend.zaryableather.com`
- Frontend: `https://zaryableather.com` and `https://www.zaryableather.com`

---

## 🔧 Step 1: Update Environment Variables

### `.env.local` (Development)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://django-blog-api-prod.eba-uiwnbpqr.us-east-1.elasticbeanstalk.com
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Once DNS is configured, use:
# NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
# NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### `.env.production` (Production)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
NEXT_PUBLIC_SITE_URL=https://zaryableather.com

# SEO
NEXT_PUBLIC_SITE_NAME=Zaryab Leather Blog
NEXT_PUBLIC_TWITTER_SITE=@zaryableather

# Optional: Analytics Secret (if using)
ANALYTICS_SECRET=your-analytics-secret-token
REVALIDATE_SECRET=your-revalidate-secret-token
```

### Vercel Environment Variables

If deploying to Vercel, add these in **Settings → Environment Variables**:

```
NEXT_PUBLIC_API_URL = https://backend.zaryableather.com
NEXT_PUBLIC_SITE_URL = https://zaryableather.com
NEXT_PUBLIC_SITE_NAME = Zaryab Leather Blog
NEXT_PUBLIC_TWITTER_SITE = @zaryableather
```

---

## 📁 Step 2: Update API Configuration Files

### `lib/api.js` or `utils/api.js`

```javascript
// API base URL
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

// API endpoints
export const API_ENDPOINTS = {
  posts: `${API_URL}/api/v1/posts/`,
  categories: `${API_URL}/api/v1/categories/`,
  tags: `${API_URL}/api/v1/tags/`,
  authors: `${API_URL}/api/v1/authors/`,
  search: `${API_URL}/api/v1/search/`,
  trending: `${API_URL}/api/v1/trending/`,
  carousel: `${API_URL}/api/v1/homepage/carousel/`,
  settings: `${API_URL}/api/v1/settings/`,
  subscribe: `${API_URL}/api/v1/subscribe/`,
};

// Fetch helper with error handling
export async function fetchAPI(endpoint, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = await fetch(endpoint, { ...defaultOptions, ...options });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}
```

---

## 📄 Step 3: Update Data Fetching Functions

### Fetch All Posts

```javascript
// lib/posts.js
import { API_ENDPOINTS, fetchAPI } from './api';

export async function getAllPosts(page = 1, limit = 20) {
  const data = await fetchAPI(
    `${API_ENDPOINTS.posts}?page=${page}&limit=${limit}`
  );
  return data;
}

export async function getPostBySlug(slug) {
  const data = await fetchAPI(`${API_ENDPOINTS.posts}${slug}/`);
  return data;
}

export async function getPostsByCategory(categorySlug, page = 1) {
  const data = await fetchAPI(
    `${API_ENDPOINTS.posts}?categories__slug=${categorySlug}&page=${page}`
  );
  return data;
}

export async function searchPosts(query) {
  const data = await fetchAPI(
    `${API_ENDPOINTS.search}?q=${encodeURIComponent(query)}`
  );
  return data;
}
```

### Fetch Categories (with filtering)

```javascript
// lib/categories.js
import { API_ENDPOINTS, fetchAPI } from './api';

export async function getAllCategories() {
  const data = await fetchAPI(API_ENDPOINTS.categories);
  return data;
}

// Fetch only specific categories for navigation
export async function getSelectedCategories(slugs = []) {
  if (slugs.length === 0) {
    return getAllCategories();
  }
  
  const slugsParam = slugs.join(',');
  const data = await fetchAPI(
    `${API_ENDPOINTS.categories}?slugs=${slugsParam}`
  );
  return data;
}

export async function getCategoryBySlug(slug) {
  const data = await fetchAPI(`${API_ENDPOINTS.categories}${slug}/`);
  return data;
}
```

### Fetch Homepage Carousel

```javascript
// lib/carousel.js
import { API_ENDPOINTS, fetchAPI } from './api';

export async function getHomeCarousel() {
  const data = await fetchAPI(API_ENDPOINTS.carousel);
  return data;
}
```

---

## 🎨 Step 4: Update Components

### Navigation Component

```jsx
// components/Navigation.jsx
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getSelectedCategories } from '@/lib/categories';

export default function Navigation() {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    async function loadCategories() {
      // Specify which categories to show in navigation
      const selectedSlugs = ['leather-care', 'fashion-tips', 'product-reviews'];
      const data = await getSelectedCategories(selectedSlugs);
      setCategories(data);
    }
    loadCategories();
  }, []);

  return (
    <nav className="navigation">
      <Link href="/">Home</Link>
      <Link href="/blog">Blog</Link>
      {categories.map((cat) => (
        <Link key={cat.slug} href={`/category/${cat.slug}`}>
          {cat.name}
        </Link>
      ))}
      <Link href="/about">About</Link>
    </nav>
  );
}
```

### Blog Post Card

```jsx
// components/PostCard.jsx
import Link from 'next/link';
import Image from 'next/image';

export default function PostCard({ post }) {
  return (
    <article className="post-card">
      {post.featured_image && (
        <Link href={`/blog/${post.slug}`}>
          <Image
            src={post.featured_image.url}
            alt={post.featured_image.alt}
            width={post.featured_image.width}
            height={post.featured_image.height}
            placeholder="blur"
            blurDataURL={post.featured_image.lqip}
          />
        </Link>
      )}
      
      <div className="post-content">
        <div className="post-meta">
          {post.categories.map((cat) => (
            <Link key={cat.slug} href={`/category/${cat.slug}`}>
              {cat.name}
            </Link>
          ))}
          <span>{post.reading_time} min read</span>
        </div>
        
        <h2>
          <Link href={`/blog/${post.slug}`}>{post.title}</Link>
        </h2>
        
        <p>{post.summary}</p>
        
        <div className="post-footer">
          <span>By {post.author.name}</span>
          <time>{new Date(post.published_at).toLocaleDateString()}</time>
        </div>
      </div>
    </article>
  );
}
```

---

## 📄 Step 5: Update Pages

### Homepage (`pages/index.js` or `app/page.js`)

```jsx
// pages/index.js (Pages Router)
import { getAllPosts } from '@/lib/posts';
import { getHomeCarousel } from '@/lib/carousel';
import PostCard from '@/components/PostCard';
import Carousel from '@/components/Carousel';

export default function Home({ posts, carousel }) {
  return (
    <main>
      <Carousel items={carousel} />
      
      <section className="latest-posts">
        <h2>Latest Posts</h2>
        <div className="posts-grid">
          {posts.results.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      </section>
    </main>
  );
}

export async function getStaticProps() {
  const posts = await getAllPosts(1, 12);
  const carousel = await getHomeCarousel();

  return {
    props: { posts, carousel },
    revalidate: 60, // Revalidate every 60 seconds
  };
}
```

### Blog Post Page (`pages/blog/[slug].js`)

```jsx
// pages/blog/[slug].js
import { getPostBySlug, getAllPosts } from '@/lib/posts';
import Image from 'next/image';
import Head from 'next/head';

export default function BlogPost({ post }) {
  return (
    <>
      <Head>
        <title>{post.seo.title}</title>
        <meta name="description" content={post.seo.description} />
        <meta name="keywords" content={post.seo.keywords} />
        <link rel="canonical" href={post.seo.canonical_url} />
        
        {/* Open Graph */}
        <meta property="og:type" content={post.open_graph.og_type} />
        <meta property="og:title" content={post.open_graph.og_title} />
        <meta property="og:description" content={post.open_graph.og_description} />
        <meta property="og:image" content={post.open_graph.og_image} />
        <meta property="og:url" content={post.open_graph.og_url} />
        
        {/* Twitter Card */}
        <meta name="twitter:card" content={post.twitter_card.card} />
        <meta name="twitter:title" content={post.twitter_card.title} />
        <meta name="twitter:description" content={post.twitter_card.description} />
        <meta name="twitter:image" content={post.twitter_card.image} />
        
        {/* Schema.org */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(post.schema_org) }}
        />
      </Head>

      <article className="blog-post">
        {post.featured_image && (
          <Image
            src={post.featured_image.url}
            alt={post.featured_image.alt}
            width={post.featured_image.width}
            height={post.featured_image.height}
            priority
          />
        )}
        
        <header>
          <h1>{post.title}</h1>
          <div className="post-meta">
            <span>By {post.author.name}</span>
            <time>{new Date(post.published_at).toLocaleDateString()}</time>
            <span>{post.reading_time} min read</span>
          </div>
        </header>
        
        <div 
          className="post-content"
          dangerouslySetInnerHTML={{ __html: post.content_html }}
        />
        
        {post.related_posts.length > 0 && (
          <section className="related-posts">
            <h2>Related Posts</h2>
            <div className="posts-grid">
              {post.related_posts.map((relatedPost) => (
                <PostCard key={relatedPost.id} post={relatedPost} />
              ))}
            </div>
          </section>
        )}
      </article>
    </>
  );
}

export async function getStaticPaths() {
  const posts = await getAllPosts(1, 100);
  
  const paths = posts.results.map((post) => ({
    params: { slug: post.slug },
  }));

  return { paths, fallback: 'blocking' };
}

export async function getStaticProps({ params }) {
  const post = await getPostBySlug(params.slug);

  if (!post) {
    return { notFound: true };
  }

  return {
    props: { post },
    revalidate: 60,
  };
}
```

### Category Page (`pages/category/[slug].js`)

```jsx
// pages/category/[slug].js
import { getPostsByCategory } from '@/lib/posts';
import { getCategoryBySlug } from '@/lib/categories';
import PostCard from '@/components/PostCard';

export default function CategoryPage({ category, posts }) {
  return (
    <main>
      <header>
        <h1>{category.name}</h1>
        <p>{category.description}</p>
      </header>
      
      <div className="posts-grid">
        {posts.results.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </main>
  );
}

export async function getStaticPaths() {
  // Generate paths for main categories only
  const paths = [
    { params: { slug: 'leather-care' } },
    { params: { slug: 'fashion-tips' } },
    { params: { slug: 'product-reviews' } },
  ];

  return { paths, fallback: 'blocking' };
}

export async function getStaticProps({ params }) {
  const category = await getCategoryBySlug(params.slug);
  const posts = await getPostsByCategory(params.slug);

  return {
    props: { category, posts },
    revalidate: 60,
  };
}
```

---

## 🔍 Step 6: Update SEO Configuration

### `next-seo.config.js`

```javascript
export default {
  defaultTitle: 'Zaryab Leather Blog',
  titleTemplate: '%s | Zaryab Leather Blog',
  description: 'Premium leather fashion, care tips, and style guides',
  canonical: 'https://zaryableather.com',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://zaryableather.com',
    site_name: 'Zaryab Leather Blog',
    images: [
      {
        url: 'https://zaryableather.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Zaryab Leather Blog',
      },
    ],
  },
  twitter: {
    handle: '@zaryableather',
    site: '@zaryableather',
    cardType: 'summary_large_image',
  },
};
```

---

## 🚀 Step 7: Deploy to Vercel

### 1. Update Vercel Project Settings

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Login to Vercel
vercel login

# Link to your project
vercel link

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://backend.zaryableather.com

vercel env add NEXT_PUBLIC_SITE_URL production
# Enter: https://zaryableather.com
```

### 2. Deploy

```bash
# Deploy to production
vercel --prod
```

### 3. Configure Custom Domain in Vercel

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Domains**
2. Add domains:
   - `zaryableather.com`
   - `www.zaryableather.com`
3. Update DNS in Route 53:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   
   Type: A
   Name: @
   Value: 76.76.21.21 (Vercel IP)
   ```

---

## ✅ Step 8: Testing Checklist

### Local Testing

```bash
# 1. Update .env.local
# 2. Install dependencies
npm install

# 3. Run development server
npm run dev

# 4. Test pages
# - http://localhost:3000
# - http://localhost:3000/blog
# - http://localhost:3000/blog/[any-post-slug]
# - http://localhost:3000/category/leather-care
```

### Production Testing

```bash
# Test API connectivity
curl https://backend.zaryableather.com/api/v1/healthcheck/

# Test CORS
curl -H "Origin: https://zaryableather.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://backend.zaryableather.com/api/v1/posts/

# Test frontend
curl https://zaryableather.com
```

---

## 🔧 Step 9: Common Issues & Solutions

### Issue: CORS Errors

**Solution**: Verify backend CORS settings
```bash
# Check backend environment variables
eb printenv | grep CORS

# Should show:
# CORS_ALLOWED_ORIGINS = https://zaryableather.com,https://www.zaryableather.com
```

### Issue: 404 on API Calls

**Solution**: Check API URL in environment variables
```javascript
// Verify in browser console
console.log(process.env.NEXT_PUBLIC_API_URL);
// Should output: https://backend.zaryableather.com
```

### Issue: Images Not Loading

**Solution**: Add backend domain to Next.js image config

```javascript
// next.config.js
module.exports = {
  images: {
    domains: [
      'backend.zaryableather.com',
      'soccrpfkqjqjaoaturjb.supabase.co', // Supabase storage
    ],
  },
};
```

### Issue: Slow API Responses

**Solution**: Implement caching with SWR

```bash
npm install swr
```

```javascript
// lib/hooks/usePosts.js
import useSWR from 'swr';
import { fetchAPI, API_ENDPOINTS } from '@/lib/api';

export function usePosts(page = 1) {
  const { data, error } = useSWR(
    `${API_ENDPOINTS.posts}?page=${page}`,
    fetchAPI,
    { revalidateOnFocus: false }
  );

  return {
    posts: data,
    isLoading: !error && !data,
    isError: error,
  };
}
```

---

## 📊 Step 10: Performance Optimization

### Enable ISR (Incremental Static Regeneration)

```javascript
// All pages with getStaticProps
export async function getStaticProps() {
  // ... fetch data
  
  return {
    props: { data },
    revalidate: 60, // Revalidate every 60 seconds
  };
}
```

### Add Loading States

```jsx
// components/PostsList.jsx
import { usePosts } from '@/lib/hooks/usePosts';

export default function PostsList() {
  const { posts, isLoading, isError } = usePosts();

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Failed to load posts</div>;

  return (
    <div className="posts-grid">
      {posts.results.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

---

## 🎯 Final Checklist

- [ ] Environment variables updated (`.env.local`, `.env.production`)
- [ ] API configuration file updated (`lib/api.js`)
- [ ] Data fetching functions updated
- [ ] Components updated with new API calls
- [ ] Pages updated (homepage, blog, category)
- [ ] SEO configuration updated
- [ ] `next.config.js` updated with image domains
- [ ] Deployed to Vercel
- [ ] Custom domains configured
- [ ] DNS records updated in Route 53
- [ ] CORS tested and working
- [ ] All pages loading correctly
- [ ] Images displaying properly
- [ ] SEO meta tags working

---

## 📞 Support & Resources

- **Backend API Docs**: https://backend.zaryableather.com/api/v1/docs/
- **Backend Health**: https://backend.zaryableather.com/api/v1/healthcheck/
- **Category Filtering Guide**: See `CATEGORY_FILTERING.md`
- **Deployment Guide**: See `DEPLOYMENT_UPDATED.md`

---

**✅ Migration Complete!**

Your Next.js frontend is now configured to work with the new backend URL `https://backend.zaryableather.com` and deployed at `https://zaryableather.com`.
