# Analytics Integration Guide

Quick reference for integrating Django Blog API analytics with Next.js.

## Setup

### 1. Environment Configuration

```bash
# .env
ANALYTICS_SECRET=your-64-char-secret-key
NEXTJS_URL=https://your-nextjs-app.com
REDIS_URL=redis://127.0.0.1:6379/1
```

### 2. Generate Secrets

```bash
# Generate analytics secret
openssl rand -hex 32

# Generate revalidation secret
openssl rand -hex 32
```

---

## Next.js Implementation

### Track Page Views

```typescript
// lib/analytics.ts
import crypto from 'crypto'

export async function trackPageView(slug: string, referrer?: string) {
  const payload = JSON.stringify({ slug, referrer })
  
  // Sign on server-side
  const signature = crypto
    .createHmac('sha256', process.env.ANALYTICS_SECRET!)
    .update(payload)
    .digest('hex')
  
  await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/track-view/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Signature': signature
    },
    body: payload
  })
}

// pages/blog/[slug].tsx
import { useEffect } from 'react'
import { trackPageView } from '@/lib/analytics'

export default function BlogPost({ post }) {
  useEffect(() => {
    trackPageView(post.slug, document.referrer)
  }, [post.slug])
  
  return <article>{/* ... */}</article>
}
```

### Display Trending Posts

```typescript
// pages/trending.tsx
import { GetStaticProps } from 'next'

interface TrendingProps {
  posts: Post[]
}

export const getStaticProps: GetStaticProps<TrendingProps> = async () => {
  const res = await fetch(
    `${process.env.API_URL}/api/trending/?days=7&limit=10`
  )
  const data = await res.json()
  
  return {
    props: { posts: data.results },
    revalidate: 900 // 15 minutes
  }
}

export default function TrendingPage({ posts }: TrendingProps) {
  return (
    <div>
      <h1>Trending Posts</h1>
      {posts.map(post => (
        <article key={post.slug}>
          <h2>{post.title}</h2>
          <p>{post.summary}</p>
        </article>
      ))}
    </div>
  )
}
```

### SEO Dashboard

```typescript
// pages/admin/seo.tsx
import { GetServerSideProps } from 'next'

interface SEODashboardProps {
  trending: Post[]
  searches: SearchQuery[]
}

export const getServerSideProps: GetServerSideProps<SEODashboardProps> = async () => {
  const [trendingRes, searchesRes] = await Promise.all([
    fetch(`${process.env.API_URL}/api/trending/?days=30&limit=20`),
    fetch(`${process.env.API_URL}/api/popular-searches/?days=30`)
  ])
  
  return {
    props: {
      trending: (await trendingRes.json()).results,
      searches: await searchesRes.json()
    }
  }
}

export default function SEODashboard({ trending, searches }: SEODashboardProps) {
  return (
    <div>
      <section>
        <h2>Trending Posts (30 days)</h2>
        <ul>
          {trending.map(post => (
            <li key={post.slug}>{post.title}</li>
          ))}
        </ul>
      </section>
      
      <section>
        <h2>Popular Searches</h2>
        <table>
          <thead>
            <tr>
              <th>Query</th>
              <th>Searches</th>
              <th>Clicks</th>
              <th>CTR</th>
            </tr>
          </thead>
          <tbody>
            {searches.map(s => (
              <tr key={s.query}>
                <td>{s.query}</td>
                <td>{s.searches}</td>
                <td>{s.clicks}</td>
                <td>{s.ctr}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}
```

---

## API Signing (Server-Side)

```typescript
// pages/api/sign.ts
import { NextApiRequest, NextApiResponse } from 'next'
import crypto from 'crypto'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }
  
  const payload = JSON.stringify(req.body)
  const signature = crypto
    .createHmac('sha256', process.env.ANALYTICS_SECRET!)
    .update(payload)
    .digest('hex')
  
  res.status(200).json({ signature })
}
```

---

## React Hook

```typescript
// hooks/useAnalytics.ts
import { useEffect } from 'react'

export function usePageView(slug: string) {
  useEffect(() => {
    const track = async () => {
      const payload = { slug, referrer: document.referrer }
      
      // Get signature from API route
      const sigRes = await fetch('/api/sign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const { signature } = await sigRes.json()
      
      // Track view
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/track-view/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Signature': signature
        },
        body: JSON.stringify(payload)
      })
    }
    
    track()
  }, [slug])
}

// Usage
export default function BlogPost({ post }) {
  usePageView(post.slug)
  return <article>{/* ... */}</article>
}
```

---

## Testing

```typescript
// __tests__/analytics.test.ts
import { trackPageView } from '@/lib/analytics'

describe('Analytics', () => {
  it('tracks page view with signature', async () => {
    const mockFetch = jest.fn().mockResolvedValue({ ok: true })
    global.fetch = mockFetch
    
    await trackPageView('test-post', 'https://google.com')
    
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/track-view/'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'X-Signature': expect.any(String)
        })
      })
    )
  })
})
```

---

## Deployment

### Vercel Configuration

```json
// vercel.json
{
  "env": {
    "ANALYTICS_SECRET": "@analytics-secret",
    "NEXT_PUBLIC_API_URL": "https://api.example.com",
    "API_URL": "https://api.example.com"
  }
}
```

### Environment Variables

```bash
# Add to Vercel dashboard
ANALYTICS_SECRET=your-secret-key
NEXT_PUBLIC_API_URL=https://api.example.com
API_URL=https://api.example.com
```

---

## Performance Tips

1. **Debounce tracking calls**
   ```typescript
   const debouncedTrack = debounce(trackPageView, 1000)
   ```

2. **Use SWR for trending data**
   ```typescript
   import useSWR from 'swr'
   
   const { data } = useSWR('/api/trending', fetcher, {
     refreshInterval: 900000 // 15 minutes
   })
   ```

3. **Prefetch trending posts**
   ```typescript
   <Link href="/trending" prefetch>
     Trending Posts
   </Link>
   ```

---

## Monitoring

```typescript
// lib/monitoring.ts
export async function checkAnalyticsHealth() {
  const res = await fetch(`${process.env.API_URL}/api/healthcheck/`)
  const data = await res.json()
  
  if (data.status !== 'healthy') {
    console.error('Analytics unhealthy:', data)
  }
  
  return data
}
```

---

## Common Issues

### Issue: CORS errors
**Solution:** Add Next.js domain to Django CORS_ALLOWED_ORIGINS

### Issue: Invalid signature
**Solution:** Ensure ANALYTICS_SECRET matches on both sides

### Issue: Views not tracking
**Solution:** Check Redis connection and HMAC signature

### Issue: Trending posts empty
**Solution:** Verify PostView records exist and date range

---

## Quick Reference

| Endpoint | Method | Purpose | Cache |
|----------|--------|---------|-------|
| /api/track-view/ | POST | Track page view | N/A |
| /api/trending/ | GET | Get trending posts | 15 min |
| /api/popular-searches/ | GET | Get search queries | 1 hour |

| Task | Schedule | Purpose |
|------|----------|---------|
| aggregate_daily_metrics | 1 AM | Aggregate + prune logs |
| export_trending_keywords | 3 AM | Export JSON for ISR |

---

## Support

For issues or questions:
1. Check Django logs: `tail -f logs/django.log`
2. Check Celery logs: `tail -f logs/celery.log`
3. Verify Redis: `redis-cli ping`
4. Test endpoint: `curl -X POST https://api.example.com/api/track-view/`
