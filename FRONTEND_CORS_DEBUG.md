# 🔍 Frontend CORS Debugging Guide

## ✅ Backend CORS is Working!

I've verified that CORS headers are correctly configured on `backend.zaryableather.com`:

```bash
$ curl -I -H "Origin: https://zaryableather.com" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  https://backend.zaryableather.com/api/v1/posts/

access-control-allow-origin: https://zaryableather.com ✅
access-control-allow-credentials: true ✅
access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS ✅
```

## 🐛 Frontend Issues to Check

Since backend CORS is working, the issue is in your **frontend configuration**. Follow these steps:

---

## Step 1: Verify Frontend Environment Variables

### Check in Browser Console

Open your frontend in browser, then in DevTools Console, run:

```javascript
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('Site URL:', process.env.NEXT_PUBLIC_SITE_URL);
```

**Expected Output:**
```
API URL: https://backend.zaryableather.com
Site URL: https://zaryableather.com
```

**❌ If you see `undefined` or wrong URL:**
- Your environment variables are not set correctly
- See fix below

---

## Step 2: Fix Environment Variables

### For Vercel Deployment

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**

2. Add/Update these variables:

```
Name: NEXT_PUBLIC_API_URL
Value: https://backend.zaryableather.com
Environment: Production

Name: NEXT_PUBLIC_SITE_URL
Value: https://zaryableather.com
Environment: Production
```

3. **Redeploy** your frontend:
```bash
vercel --prod
```

### For Local Development

Create/Update `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://backend.zaryableather.com
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

Then restart your dev server:
```bash
npm run dev
```

---

## Step 3: Check Your API Configuration File

### Verify `lib/api.js` or `utils/api.js`

Make sure it's using the environment variable:

```javascript
// ✅ CORRECT
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend.zaryableather.com';

// ❌ WRONG - Hardcoded old URL
export const API_URL = 'http://localhost:8000';
export const API_URL = 'http://old-domain.com';
```

---

## Step 4: Check Network Requests in DevTools

1. Open **DevTools** → **Network** tab
2. Reload your page
3. Look for API requests
4. Click on a failed request
5. Check the **Request URL**

**What to look for:**

### ✅ Correct Request URL:
```
https://backend.zaryableather.com/api/v1/posts/
```

### ❌ Wrong Request URLs:
```
http://localhost:8000/api/v1/posts/          ← Old local URL
http://old-domain.com/api/v1/posts/          ← Old domain
undefined/api/v1/posts/                      ← Missing env var
```

---

## Step 5: Test API Call Directly in Browser

Open browser console on your frontend site and run:

```javascript
// Test 1: Check if API is reachable
fetch('https://backend.zaryableather.com/api/v1/posts/')
  .then(res => {
    console.log('Status:', res.status);
    console.log('Headers:', [...res.headers.entries()]);
    return res.json();
  })
  .then(data => console.log('Data:', data))
  .catch(err => console.error('Error:', err));

// Test 2: Check environment variable
console.log('API URL from env:', process.env.NEXT_PUBLIC_API_URL);
```

**Expected Result:**
- Status: 200
- Headers should include `access-control-allow-origin: https://zaryableather.com`
- Data: Array of posts

**If you get CORS error:**
- Check if the Origin header matches your frontend domain exactly
- Make sure you're accessing frontend via `https://zaryableather.com` (not `http://`)

---

## Step 6: Common Frontend Mistakes

### ❌ Mistake 1: Using HTTP instead of HTTPS

```javascript
// WRONG
const API_URL = 'http://backend.zaryableather.com';

// CORRECT
const API_URL = 'https://backend.zaryableather.com';
```

### ❌ Mistake 2: Trailing Slash Inconsistency

```javascript
// Be consistent
const API_URL = 'https://backend.zaryableather.com';  // No trailing slash
const endpoint = `${API_URL}/api/v1/posts/`;          // Add slash in endpoint
```

### ❌ Mistake 3: Not Using Environment Variable

```javascript
// WRONG - Hardcoded
const API_URL = 'https://backend.zaryableather.com';

// CORRECT - From environment
const API_URL = process.env.NEXT_PUBLIC_API_URL;
```

### ❌ Mistake 4: Wrong Environment Variable Name

```javascript
// WRONG - Missing NEXT_PUBLIC_ prefix
process.env.API_URL  ❌

// CORRECT - With NEXT_PUBLIC_ prefix
process.env.NEXT_PUBLIC_API_URL  ✅
```

---

## Step 7: Verify Frontend Domain

Make sure you're accessing your frontend via the correct domain:

### ✅ Correct:
```
https://zaryableather.com
https://www.zaryableather.com
```

### ❌ Wrong:
```
http://zaryableather.com          ← HTTP instead of HTTPS
https://vercel-preview-url.app    ← Preview URL not in CORS whitelist
http://localhost:3000             ← Local (only works if backend allows it)
```

---

## Step 8: Quick Fix - Temporary CORS Allow All (Testing Only)

**⚠️ ONLY FOR TESTING - NOT FOR PRODUCTION**

If you need to quickly test if CORS is the issue, temporarily allow all origins:

```bash
# SSH into backend
eb ssh

# Edit environment variable (temporary)
eb setenv CORS_ALLOW_ALL_ORIGINS=True

# Deploy
eb deploy
```

**If this works**, it confirms the issue is with origin matching. Then:
1. Set `CORS_ALLOW_ALL_ORIGINS=False` again
2. Fix your frontend to use the correct domain

---

## Step 9: Check Browser Console for Exact Error

Look for the exact CORS error message:

### Error Type 1: Origin Not Allowed
```
Access to fetch at 'https://backend.zaryableather.com/api/v1/posts/' 
from origin 'https://wrong-domain.com' has been blocked by CORS policy
```

**Fix:** Your frontend is running on a domain not in the CORS whitelist.

### Error Type 2: Missing CORS Headers
```
No 'Access-Control-Allow-Origin' header is present
```

**Fix:** Backend CORS not configured (but we verified it IS configured).

### Error Type 3: Preflight Request Failed
```
Response to preflight request doesn't pass access control check
```

**Fix:** OPTIONS request failing. Check if backend handles OPTIONS method.

---

## Step 10: Complete Frontend API Setup

Here's the complete, correct setup:

### `lib/api.js`

```javascript
// API Configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend.zaryableather.com';
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://zaryableather.com';

// API Endpoints
export const API_ENDPOINTS = {
  posts: `${API_URL}/api/v1/posts/`,
  categories: `${API_URL}/api/v1/categories/`,
  tags: `${API_URL}/api/v1/tags/`,
  settings: `${API_URL}/api/v1/settings/`,
  carousel: `${API_URL}/api/v1/homepage/carousel/`,
};

// Fetch helper
export async function fetchAPI(endpoint, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  try {
    const response = await fetch(endpoint, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}
```

### Usage in Component

```javascript
import { API_ENDPOINTS, fetchAPI } from '@/lib/api';

export default function PostsList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadPosts() {
      try {
        const data = await fetchAPI(API_ENDPOINTS.posts);
        setPosts(data.results || []);
      } catch (err) {
        setError(err.message);
        console.error('Failed to load posts:', err);
      } finally {
        setLoading(false);
      }
    }
    loadPosts();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {posts.map(post => (
        <div key={post.id}>{post.title}</div>
      ))}
    </div>
  );
}
```

---

## ✅ Final Checklist

- [ ] Environment variables set in Vercel/hosting platform
- [ ] `NEXT_PUBLIC_API_URL=https://backend.zaryableather.com`
- [ ] Frontend redeployed after setting env vars
- [ ] API configuration file uses `process.env.NEXT_PUBLIC_API_URL`
- [ ] No hardcoded URLs in code
- [ ] Accessing frontend via `https://zaryableather.com`
- [ ] Browser cache cleared
- [ ] Tested API call in browser console
- [ ] Network tab shows correct request URL
- [ ] Response headers include `access-control-allow-origin`

---

## 🆘 Still Not Working?

### Share These Details:

1. **What URL is your frontend using?**
   ```javascript
   console.log(process.env.NEXT_PUBLIC_API_URL);
   ```

2. **What's the exact error in console?**
   - Copy the full error message

3. **What's in Network tab?**
   - Request URL
   - Response headers
   - Status code

4. **Where is frontend deployed?**
   - Vercel? Netlify? Other?

5. **What domain are you accessing?**
   - `https://zaryableather.com`?
   - Or preview URL?

---

## 📞 Quick Test Commands

### Test Backend CORS (Should Work ✅)
```bash
curl -H "Origin: https://zaryableather.com" \
     https://backend.zaryableather.com/api/v1/posts/ | head -20
```

### Test from Browser Console (Run on your frontend)
```javascript
fetch('https://backend.zaryableather.com/api/v1/posts/')
  .then(r => r.json())
  .then(d => console.log('Success:', d))
  .catch(e => console.error('Error:', e));
```

---

**Backend CORS is working perfectly ✅**

**The issue is 100% in your frontend configuration.**

Follow the steps above to fix it!
