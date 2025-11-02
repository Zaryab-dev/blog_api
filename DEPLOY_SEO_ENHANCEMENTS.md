# 🚀 SEO Enhancements Deployment Checklist

## Pre-Deployment

- [ ] Review all changes in `SEO_ENHANCEMENTS_COMPLETE.md`
- [ ] Backup database before migration
- [ ] Ensure `.env` has `NEXTJS_URL` configured
- [ ] Test migration in development environment

## Deployment Steps

### 1. Apply Database Migration
```bash
python manage.py migrate blog
```

**Expected Output:**
```
Running migrations:
  Applying blog.0015_add_seo_enhancements... OK
```

### 2. Populate Leather Keywords
```bash
python manage.py populate_leather_keywords
```

**Expected Output:**
```
Updated "Post Title 1" with 8 keywords
Updated "Post Title 2" with 10 keywords
...
Successfully updated X posts with leather keywords
```

### 3. Update Frontend URLs
```bash
python manage.py update_frontend_urls
```

**Expected Output:**
```
Updated "Post Title 1"
Updated "Post Title 2"
...
Successfully updated X posts with frontend URLs
```

### 4. Collect Static Files (if needed)
```bash
python manage.py collectstatic --noinput
```

### 5. Restart Application
```bash
# For Gunicorn
sudo systemctl restart gunicorn

# For Docker
docker-compose restart

# For AWS App Runner
# Trigger new deployment from console or CLI
```

## Post-Deployment Validation

### 1. Check Django Admin
- [ ] Go to `/admin/blog/post/`
- [ ] Verify new fields appear in list view
- [ ] Open a post and check all new fields are editable
- [ ] Verify keywords are populated
- [ ] Check frontend URLs are correct

### 2. Test API Endpoints

#### List Endpoint
```bash
curl https://backend.zaryableather.com/api/v1/posts/ | jq '.[0]'
```

**Verify fields present:**
- [ ] `keywords`
- [ ] `excerpt`
- [ ] `reading_time_minutes`
- [ ] `frontend_url`
- [ ] `canonical_url`

#### Detail Endpoint
```bash
curl https://backend.zaryableather.com/api/v1/posts/{slug}/ | jq
```

**Verify fields present:**
- [ ] `keywords`
- [ ] `excerpt`
- [ ] `reading_time_minutes`
- [ ] `frontend_url`
- [ ] `canonical_url`
- [ ] `seo_score`
- [ ] `structured_data_valid`
- [ ] `main_image_alt_text`
- [ ] `revalidate_path`

#### Schema.org Validation
```bash
curl https://backend.zaryableather.com/api/v1/posts/{slug}/ | jq '.schema_org'
```

**Verify:**
- [ ] `url` uses frontend domain
- [ ] `mainEntityOfPage` uses frontend domain
- [ ] `publisher.logo.url` uses frontend domain
- [ ] `keywords` field populated

### 3. Run Test Script
```bash
python test_seo_enhancements.py
```

**Expected Output:**
```
✅ ALL TESTS PASSED!
```

### 4. Check Logs
```bash
# Check for any errors
tail -f logs/django.log

# Check for migration success
grep "0015_add_seo_enhancements" logs/django.log
```

## Rollback Plan (If Needed)

### 1. Rollback Migration
```bash
python manage.py migrate blog 0014_remove_comment_comment_post_idx_and_more
```

### 2. Restore Database Backup
```bash
# PostgreSQL
pg_restore -d your_database backup_file.dump

# Or use your backup tool
```

### 3. Restart Application
```bash
sudo systemctl restart gunicorn
# or
docker-compose restart
```

## Environment Variables

Ensure these are set in `.env`:

```bash
# Frontend URL (required for canonical URLs)
NEXTJS_URL=https://zaryableather.com

# Backend URL (for API)
SITE_URL=https://backend.zaryableather.com

# Site name
SITE_NAME=Zaryab Leather Blog
```

## Next.js Integration

After deployment, update your Next.js frontend:

### 1. Update TypeScript Types
```typescript
interface Post {
  // ... existing fields
  keywords: string[];
  excerpt: string;
  reading_time_minutes: number;
  frontend_url: string;
  seo_score: number;
  structured_data_valid: boolean;
  main_image_alt_text: string;
  revalidate_path: string;
}
```

### 2. Use New Fields
```tsx
// In your blog post component
export default function BlogPost({ post }: { post: Post }) {
  return (
    <>
      {/* Schema.org with frontend URLs */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(post.schema_org) }}
      />
      
      {/* Meta tags */}
      <meta name="keywords" content={post.keywords.join(', ')} />
      
      {/* Reading time */}
      <p>{post.reading_time_minutes} min read</p>
      
      {/* Excerpt */}
      <p>{post.excerpt}</p>
    </>
  );
}
```

### 3. Implement ISR Revalidation
```typescript
// app/api/revalidate/route.ts
export async function POST(request: Request) {
  const { revalidate_path } = await request.json();
  
  try {
    await revalidate(revalidate_path);
    return Response.json({ revalidated: true });
  } catch (err) {
    return Response.json({ revalidated: false }, { status: 500 });
  }
}
```

## Monitoring

### Key Metrics to Watch

1. **API Response Time**
   - Monitor `/api/v1/posts/` endpoint
   - Should remain under 200ms

2. **Database Performance**
   - Check query performance for new fields
   - Monitor index usage

3. **Error Rates**
   - Watch for serialization errors
   - Check for null/empty field issues

4. **SEO Metrics**
   - Google Search Console indexing status
   - Schema.org validation (Google Rich Results Test)
   - Core Web Vitals

## Success Criteria

- [x] Migration applied successfully
- [x] All posts have keywords populated
- [x] Frontend URLs correct in all posts
- [x] API returns all new fields
- [x] Django Admin shows new fields
- [x] No errors in logs
- [x] Test script passes
- [x] Schema.org uses frontend URLs
- [x] ISR revalidation paths set

## Support

If issues occur:

1. Check logs: `logs/django.log`
2. Run test script: `python test_seo_enhancements.py`
3. Verify migration: `python manage.py showmigrations blog`
4. Check database: `python manage.py dbshell`

## Documentation

- Full details: `SEO_ENHANCEMENTS_COMPLETE.md`
- Model changes: `blog/models.py`
- API changes: `blog/serializers.py`
- Admin changes: `blog/admin.py`
- Migration: `blog/migrations/0015_add_seo_enhancements.py`

---

**Deployment Date:** _____________
**Deployed By:** _____________
**Status:** ⬜ Pending / ⬜ In Progress / ⬜ Complete
