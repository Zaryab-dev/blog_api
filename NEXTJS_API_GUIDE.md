# Next.js API Integration Guide

## 🚀 Django Blog API Endpoints

Base URL: `http://localhost:8000/api/v1`

---

## 📋 Complete API Endpoints

### **Posts**
```
GET    /api/v1/posts/                    # List all published posts (paginated)
GET    /api/v1/posts/{slug}/              # Get single post by slug
GET    /api/v1/posts/{id}/                # Get single post by ID
POST   /api/v1/posts/                     # Create post (auth required)
PUT    /api/v1/posts/{id}/                # Update post (auth required)
DELETE /api/v1/posts/{id}/                # Delete post (auth required)
```

### **Categories**
```
GET    /api/v1/categories/                # List all categories
GET    /api/v1/categories/{slug}/         # Get category by slug
GET    /api/v1/categories/{slug}/posts/   # Get posts in category
```

### **Tags**
```
GET    /api/v1/tags/                      # List all tags
GET    /api/v1/tags/{slug}/               # Get tag by slug
GET    /api/v1/tags/{slug}/posts/         # Get posts with tag
```

### **Authors**
```
GET    /api/v1/authors/                   # List all authors
GET    /api/v1/authors/{slug}/            # Get author by slug
GET    /api/v1/authors/{slug}/posts/      # Get posts by author
```

### **Search**
```
GET    /api/v1/search/?q={query}          # Search posts
```

### **Trending & Analytics**
```
GET    /api/v1/trending/                  # Get trending posts
POST   /api/v1/track-view/                # Track post view
GET    /api/v1/popular-searches/          # Get popular searches
```

### **Comments**
```
GET    /api/v1/comments/                  # List comments
POST   /api/v1/comments/                  # Create comment
GET    /api/v1/posts/{slug}/comments/     # Get post comments
```

### **Newsletter**
```
POST   /api/v1/subscribe/                 # Subscribe to newsletter
```

### **SEO & Feeds**
```
GET    /api/v1/sitemap.xml                # XML sitemap
GET    /api/v1/rss.xml                    # RSS feed
GET    /api/v1/robots.txt                 # Robots.txt
```

### **Images**
```
POST   /api/v1/images/upload/             # Upload image (auth required)
```

### **Health & Docs**
```
GET    /api/v1/healthcheck/               # API health check
GET    /api/v1/schema/                    # OpenAPI schema
GET    /api/v1/docs/                      # Swagger UI
GET    /api/v1/redoc/                     # ReDoc UI
```

---

## 🎯 Next.js Integration Prompt

```markdown
# Next.js Blog Frontend - API Integration

## Project Requirements

Build a Next.js 14+ blog frontend that consumes the Django REST API.

## API Configuration

**Base URL:** `http://localhost:8000/api/v1`

### Environment Variables (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

## API Endpoints to Integrate

### 1. Posts
- **List Posts:** `GET /posts/` (with pagination)
- **Get Post:** `GET /posts/{slug}/`
- **Search Posts:** `GET /search/?q={query}`
- **Trending Posts:** `GET /trending/`

### 2. Categories
- **List Categories:** `GET /categories/`
- **Get Category:** `GET /categories/{slug}/`
- **Category Posts:** `GET /categories/{slug}/posts/`

### 3. Tags
- **List Tags:** `GET /tags/`
- **Get Tag:** `GET /tags/{slug}/`
- **Tag Posts:** `GET /tags/{slug}/posts/`

### 4. Authors
- **List Authors:** `GET /authors/`
- **Get Author:** `GET /authors/{slug}/`
- **Author Posts:** `GET /authors/{slug}/posts/`

### 5. Comments
- **Get Comments:** `GET /posts/{slug}/comments/`
- **Post Comment:** `POST /comments/`

### 6. Newsletter
- **Subscribe:** `POST /subscribe/`

### 7. Analytics
- **Track View:** `POST /track-view/`

## Required Pages

1. **Home** (`/`) - List recent posts
2. **Blog List** (`/blog`) - All posts with filters
3. **Post Detail** (`/blog/[slug]`) - Single post
4. **Category** (`/category/[slug]`) - Posts by category
5. **Tag** (`/tag/[slug]`) - Posts by tag
6. **Author** (`/author/[slug]`) - Posts by author
7. **Search** (`/search`) - Search results

## API Response Examples

### GET /posts/
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Post Title",
      "slug": "post-title",
      "summary": "Post summary...",
      "content_html": "<p>HTML content...</p>",
      "author": {
        "name": "Author Name",
        "slug": "author-name",
        "avatar": "https://supabase.co/.../avatar.jpg"
      },
      "categories": [
        {"name": "Category", "slug": "category"}
      ],
      "tags": [
        {"name": "Tag", "slug": "tag"}
      ],
      "featured_image": {
        "file": "https://supabase.co/.../image.jpg",
        "alt_text": "Image description",
        "width": 1920,
        "height": 1080
      },
      "published_at": "2024-01-15T10:30:00Z",
      "reading_time": 5,
      "word_count": 1200,
      "seo_title": "SEO Title",
      "seo_description": "SEO description"
    }
  ]
}
```

### GET /posts/{slug}/
```json
{
  "id": "uuid",
  "title": "Post Title",
  "slug": "post-title",
  "summary": "Post summary...",
  "content_html": "<p>Full HTML content...</p>",
  "author": {
    "id": "uuid",
    "name": "Author Name",
    "slug": "author-name",
    "bio": "Author bio...",
    "avatar": "https://supabase.co/.../avatar.jpg",
    "twitter_handle": "@author"
  },
  "categories": [
    {
      "id": "uuid",
      "name": "Category",
      "slug": "category",
      "description": "Category description"
    }
  ],
  "tags": [
    {
      "id": "uuid",
      "name": "Tag",
      "slug": "tag"
    }
  ],
  "featured_image": {
    "id": "uuid",
    "file": "https://supabase.co/.../image.jpg",
    "alt_text": "Image description",
    "width": 1920,
    "height": 1080,
    "format": "jpeg"
  },
  "published_at": "2024-01-15T10:30:00Z",
  "reading_time": 5,
  "word_count": 1200,
  "seo_title": "SEO Title",
  "seo_description": "SEO description",
  "og_title": "OG Title",
  "og_description": "OG description",
  "og_image": "https://supabase.co/.../og-image.jpg",
  "canonical_url": "https://example.com/blog/post-title",
  "schema_org": {}
}
```

### GET /categories/
```json
{
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "name": "Category Name",
      "slug": "category-name",
      "description": "Category description",
      "icon": "icon-name",
      "count_published_posts": 25,
      "seo_title": "SEO Title",
      "seo_description": "SEO description",
      "seo_image": "https://supabase.co/.../image.jpg"
    }
  ]
}
```

### POST /comments/
```json
// Request
{
  "post": "post-slug-or-id",
  "name": "Commenter Name",
  "email": "email@example.com",
  "content": "Comment text..."
}

// Response
{
  "id": "uuid",
  "name": "Commenter Name",
  "content": "Comment text...",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "pending"
}
```

### POST /subscribe/
```json
// Request
{
  "email": "user@example.com"
}

// Response
{
  "message": "Subscription successful",
  "email": "user@example.com"
}
```

### POST /track-view/
```json
// Request
{
  "post_slug": "post-title",
  "user_agent": "Mozilla/5.0...",
  "referrer": "https://google.com"
}

// Response
{
  "success": true
}
```

## Implementation Requirements

### 1. API Client Setup
Create `lib/api.ts`:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchPosts(page = 1) {
  const res = await fetch(`${API_URL}/posts/?page=${page}`);
  return res.json();
}

export async function fetchPost(slug: string) {
  const res = await fetch(`${API_URL}/posts/${slug}/`);
  return res.json();
}

export async function fetchCategories() {
  const res = await fetch(`${API_URL}/categories/`);
  return res.json();
}

// Add more functions...
```

### 2. TypeScript Types
Create `types/blog.ts`:
```typescript
export interface Post {
  id: string;
  title: string;
  slug: string;
  summary: string;
  content_html: string;
  author: Author;
  categories: Category[];
  tags: Tag[];
  featured_image: Image | null;
  published_at: string;
  reading_time: number;
  word_count: number;
  seo_title: string;
  seo_description: string;
}

export interface Author {
  id: string;
  name: string;
  slug: string;
  bio: string;
  avatar: string;
  twitter_handle: string;
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
}

export interface Image {
  id: string;
  file: string;
  alt_text: string;
  width: number;
  height: number;
  format: string;
}
```

### 3. Features to Implement
- ✅ Server-side rendering (SSR) for SEO
- ✅ Static generation (SSG) for posts
- ✅ Incremental Static Regeneration (ISR)
- ✅ Image optimization (Next.js Image)
- ✅ SEO metadata (next-seo)
- ✅ Pagination
- ✅ Search functionality
- ✅ Category/Tag filtering
- ✅ Comments section
- ✅ Newsletter subscription
- ✅ Analytics tracking
- ✅ Responsive design
- ✅ Dark mode support

### 4. SEO Implementation
Use post metadata for:
- Page title: `post.seo_title || post.title`
- Meta description: `post.seo_description || post.summary`
- OG image: `post.og_image || post.featured_image.file`
- Canonical URL: `post.canonical_url`
- Schema.org: `post.schema_org`

### 5. Performance Optimization
- Use Next.js Image for all images
- Implement lazy loading
- Cache API responses
- Use ISR for posts (revalidate: 60)
- Prefetch links on hover

### 6. Error Handling
- 404 page for missing posts
- Error boundaries
- Loading states
- Retry logic for failed requests

## Tech Stack Recommendations
- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS
- **State:** React Query / SWR
- **Forms:** React Hook Form
- **SEO:** next-seo
- **Analytics:** Vercel Analytics
- **Deployment:** Vercel

## Getting Started
1. Create Next.js app: `npx create-next-app@latest`
2. Install dependencies: `npm install @tanstack/react-query axios`
3. Configure environment variables
4. Create API client
5. Build pages and components
6. Test with Django API running on localhost:8000

## CORS Configuration
Django API already configured with CORS. Add your Next.js URL to `.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```
```

---

## 📝 Quick API Test Commands

```bash
# List posts
curl http://localhost:8000/api/v1/posts/

# Get single post
curl http://localhost:8000/api/v1/posts/post-slug/

# List categories
curl http://localhost:8000/api/v1/categories/

# Search
curl http://localhost:8000/api/v1/search/?q=leather

# Trending posts
curl http://localhost:8000/api/v1/trending/

# Subscribe
curl -X POST http://localhost:8000/api/v1/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Track view
curl -X POST http://localhost:8000/api/v1/track-view/ \
  -H "Content-Type: application/json" \
  -d '{"post_slug":"post-slug"}'
```

---

## 🔗 API Documentation

- **Swagger UI:** http://localhost:8000/api/v1/docs/
- **ReDoc:** http://localhost:8000/api/v1/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/v1/schema/

---

## ✅ Ready to Use

Your Django API is fully configured and ready for Next.js integration!
