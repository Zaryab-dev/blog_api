# ✅ Localhost Testing - Ready!

## Backend CORS Now Allows Localhost

I've updated the backend to allow requests from your local development environment.

**Allowed Origins:**
- ✅ `http://localhost:3000`
- ✅ `http://127.0.0.1:3000`
- ✅ `https://zaryableather.com`
- ✅ `https://www.zaryableather.com`

---

## Quick Setup for Local Testing

### 1. Create `.env.local` in Your Frontend Project

```bash
# In your Next.js project root
NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### 2. Start Development Server

```bash
npm run dev
```

### 3. Test in Browser

Open http://localhost:3000 and check browser console:

```javascript
// Test API connection
fetch('https://backend.zaryableather.com/api/v1/posts/')
  .then(res => res.json())
  .then(data => console.log('✅ Posts loaded:', data))
  .catch(err => console.error('❌ Error:', err));
```

---

## Complete Frontend Setup

### `lib/api.js`

```javascript
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend.zaryableather.com';

export const API_ENDPOINTS = {
  posts: `${API_URL}/api/v1/posts/`,
  categories: `${API_URL}/api/v1/categories/`,
  tags: `${API_URL}/api/v1/tags/`,
  settings: `${API_URL}/api/v1/settings/`,
  carousel: `${API_URL}/api/v1/homepage/carousel/`,
};

export async function fetchAPI(endpoint) {
  const response = await fetch(endpoint);
  if (!response.ok) throw new Error(`API Error: ${response.status}`);
  return response.json();
}
```

### Example Component

```javascript
// components/PostsList.jsx
import { useEffect, useState } from 'react';
import { API_ENDPOINTS, fetchAPI } from '@/lib/api';

export default function PostsList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAPI(API_ENDPOINTS.posts)
      .then(data => setPosts(data.results || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {posts.map(post => (
        <div key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.summary}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Verify CORS is Working

### Test 1: Browser Console

```javascript
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
// Should show: https://backend.zaryableather.com

fetch('https://backend.zaryableather.com/api/v1/posts/')
  .then(r => r.json())
  .then(d => console.log('Success! Posts:', d.results.length))
  .catch(e => console.error('Failed:', e));
```

### Test 2: Network Tab

1. Open DevTools → Network tab
2. Reload page
3. Find API requests
4. Check Response Headers:
   - Should see: `access-control-allow-origin: http://localhost:3000` ✅

### Test 3: Command Line

```bash
curl -H "Origin: http://localhost:3000" \
     https://backend.zaryableather.com/api/v1/posts/ | head -50
```

---

## Common Issues & Fixes

### Issue: "CORS error" in console

**Check:**
```javascript
console.log(window.location.origin);
// Must be: http://localhost:3000
```

**Fix:** Make sure you're accessing via `http://localhost:3000` (not `127.0.0.1`)

### Issue: "Failed to fetch"

**Check:**
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL);
// Must show: https://backend.zaryableather.com
```

**Fix:** 
1. Create `.env.local` with correct URL
2. Restart dev server: `npm run dev`

### Issue: Data is undefined

**Check API response:**
```javascript
fetch('https://backend.zaryableather.com/api/v1/posts/')
  .then(r => r.json())
  .then(d => console.log('Full response:', d));
```

**Fix:** API returns paginated data:
```javascript
// ✅ Correct
const posts = data.results;

// ❌ Wrong
const posts = data;
```

---

## Environment Variables Reference

### Development (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### Production (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
NEXT_PUBLIC_SITE_URL=https://zaryableather.com
```

---

## API Endpoints Available

### Posts
```javascript
GET /api/v1/posts/                    // List all posts
GET /api/v1/posts/{slug}/             // Get single post
GET /api/v1/posts/?categories__slug=leather-care  // Filter by category
GET /api/v1/posts/?search=query       // Search posts
```

### Categories
```javascript
GET /api/v1/categories/               // All categories
GET /api/v1/categories/?slugs=cat1,cat2  // Specific categories
GET /api/v1/categories/{slug}/        // Single category
```

### Other
```javascript
GET /api/v1/tags/                     // All tags
GET /api/v1/authors/                  // All authors
GET /api/v1/settings/                 // Site settings
GET /api/v1/homepage/carousel/        // Homepage carousel
GET /api/v1/trending/                 // Trending posts
```

---

## Testing Checklist

- [ ] `.env.local` created with `NEXT_PUBLIC_API_URL`
- [ ] Dev server restarted after creating `.env.local`
- [ ] Accessing via `http://localhost:3000`
- [ ] Browser console shows correct API URL
- [ ] Network tab shows requests to `backend.zaryableather.com`
- [ ] Response headers include `access-control-allow-origin`
- [ ] Data is loading in components

---

## Quick Debug Commands

```javascript
// 1. Check environment
console.log('API:', process.env.NEXT_PUBLIC_API_URL);
console.log('Origin:', window.location.origin);

// 2. Test API
fetch('https://backend.zaryableather.com/api/v1/posts/')
  .then(r => r.json())
  .then(d => console.log('Posts:', d.results.length));

// 3. Test categories
fetch('https://backend.zaryableather.com/api/v1/categories/')
  .then(r => r.json())
  .then(d => console.log('Categories:', d));

// 4. Test settings
fetch('https://backend.zaryableather.com/api/v1/settings/')
  .then(r => r.json())
  .then(d => console.log('Settings:', d));
```

---

## ✅ You're All Set!

**Backend:** `https://backend.zaryableather.com` ✅  
**Frontend (local):** `http://localhost:3000` ✅  
**CORS:** Configured and working ✅

Start coding! 🚀
