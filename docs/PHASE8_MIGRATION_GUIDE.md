# Phase 8 Migration Guide

## Overview

This guide helps you migrate an existing Django Blog API installation to Phase 8 with CKEditor and Supabase Storage.

## Pre-Migration Checklist

- [ ] Backup database
- [ ] Backup media files
- [ ] Review current Post model
- [ ] Check Python version (3.9+)
- [ ] Verify Supabase account access
- [ ] Test in staging environment first

## Migration Steps

### Step 1: Backup Everything

```bash
# Backup database
python manage.py dumpdata blog > backup_blog_$(date +%Y%m%d).json

# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Backup code
git commit -am "Pre-Phase 8 backup"
git tag pre-phase8
```

### Step 2: Update Dependencies

```bash
# Update requirements.txt
pip install django-ckeditor>=6.7,<7.0
pip install bleach>=6.0,<7.0
pip install httpx>=0.25,<1.0

# Or install from requirements.txt
pip install -r requirements.txt
```

### Step 3: Configure Supabase

1. **Create Supabase Project** (if not exists)
   - Go to https://supabase.com
   - Create new project
   - Note the URL and API key

2. **Create Storage Bucket**
   ```sql
   -- In Supabase SQL Editor
   INSERT INTO storage.buckets (id, name, public)
   VALUES ('leather_api_storage', 'leather_api_storage', true);
   ```

3. **Set Bucket Policy**
   ```sql
   -- Allow public read access
   CREATE POLICY "Public Access"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'leather_api_storage');
   
   -- Allow authenticated uploads
   CREATE POLICY "Authenticated Uploads"
   ON storage.objects FOR INSERT
   WITH CHECK (bucket_id = 'leather_api_storage');
   ```

### Step 4: Update Settings

**Add to `settings.py`:**

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'ckeditor',
    'ckeditor_uploader',
]

# Supabase Configuration
SUPABASE_URL = env('SUPABASE_URL', default='https://soccrpfkqjqjaoaturjb.supabase.co')
SUPABASE_API_KEY = env('SUPABASE_API_KEY', default='your-api-key')
SUPABASE_BUCKET = env('SUPABASE_BUCKET', default='leather_api_storage')

# CKEditor Configuration
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', 'Blockquote', 'CodeSnippet'],
            ['Link', 'Unlink', 'Image', 'Table'],
            ['Format', 'RemoveFormat'],
            ['Undo', 'Redo'],
            ['Maximize'],
        ],
        'height': 400,
        'width': 'auto',
        'extraPlugins': ','.join(['codesnippet', 'uploadimage', 'image2']),
        'removePlugins': 'stylesheetparser',
        'codeSnippet_theme': 'monokai_sublime',
        'image2_alignClasses': ['image-left', 'image-center', 'image-right'],
        'image2_captionedClass': 'image-captioned',
    },
}

# HTML Sanitization
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'img',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span', 'figure', 'figcaption',
]
ALLOWED_HTML_ATTRS = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    'table': ['border', 'cellpadding', 'cellspacing'],
}

# CSP Headers (production only)
if not DEBUG:
    SECURE_CONTENT_SECURITY_POLICY = {
        'img-src': ["'self'", 'data:', 'https://soccrpfkqjqjaoaturjb.supabase.co'],
    }
```

**Update `.env`:**

```env
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=your-actual-api-key
SUPABASE_BUCKET=leather_api_storage
```

### Step 5: Copy New Files

Copy these files from Phase 8:

```bash
# Core files
cp blog/views_upload.py /path/to/your/project/blog/
cp blog/utils_sanitize.py /path/to/your/project/blog/

# Tests
cp blog/tests/test_upload.py /path/to/your/project/blog/tests/
cp blog/tests/test_sanitize.py /path/to/your/project/blog/tests/

# Migration
cp blog/migrations/0002_add_ckeditor_field.py /path/to/your/project/blog/migrations/
```

### Step 6: Update Existing Files

**Update `blog/models.py`:**

```python
# Add imports
from ckeditor_uploader.fields import RichTextUploadingField
from blog.utils_sanitize import sanitize_html, calculate_reading_time, count_words

# Update Post model
class Post(TimeStampedModel):
    # ... existing fields ...
    
    # Add new field
    content = RichTextUploadingField(config_name='default', blank=True)
    
    # Modify existing field
    content_html = models.TextField(editable=False)  # Add editable=False
    
    # Update save method
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Add sanitization
        if self.content:
            self.content_html = sanitize_html(self.content)
            self.reading_time = calculate_reading_time(self.content_html)
            self.word_count = count_words(self.content_html)
        
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
```

**Update `blog/admin.py`:**

```python
# In PostAdmin fieldsets, change content_html to content
fieldsets = (
    ('Content', {
        'fields': ('title', 'slug', 'slug_preview', 'summary', 'content', 'content_markdown')
    }),
    # ... rest of fieldsets ...
)
```

**Update `blog/urls_v1.py`:**

```python
# Add import
from .views_upload import upload_image

# Add to urlpatterns
urlpatterns = [
    # ... existing patterns ...
    path('upload-image/', upload_image, name='upload-image-v1'),
]
```

### Step 7: Run Migrations

```bash
# Create migrations (if needed)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Verify
python manage.py showmigrations blog
```

### Step 8: Migrate Existing Content

**Option A: Keep existing content as-is**

Existing posts will continue to work. New posts will use CKEditor.

**Option B: Migrate existing content to CKEditor**

```python
# Create management command: blog/management/commands/migrate_content.py
from django.core.management.base import BaseCommand
from blog.models import Post

class Command(BaseCommand):
    help = 'Migrate existing post content to CKEditor format'
    
    def handle(self, *args, **options):
        posts = Post.objects.filter(content='')
        count = 0
        
        for post in posts:
            if post.content_html:
                post.content = post.content_html
                post.save()
                count += 1
                self.stdout.write(f'Migrated: {post.title}')
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} posts'))
```

Run migration:
```bash
python manage.py migrate_content
```

### Step 9: Test Everything

```bash
# Run tests
python manage.py test blog.tests.test_upload
python manage.py test blog.tests.test_sanitize

# Test upload manually
python manage.py runserver
# Go to admin, create post, upload image
```

### Step 10: Deploy

```bash
# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart celery

# Check logs
tail -f logs/django.log
```

## Post-Migration Tasks

### 1. Verify Uploads

1. Login to Django Admin
2. Create/edit a post
3. Upload an image
4. Verify image appears in content
5. Check Supabase Storage dashboard

### 2. Test API

```bash
# Get post with rich content
curl http://localhost:8000/api/v1/posts/test-post/

# Verify response includes:
# - content_html (sanitized)
# - reading_time (calculated)
# - word_count (calculated)
```

### 3. Update Next.js

**Update `next.config.js`:**
```js
module.exports = {
  images: {
    domains: ['soccrpfkqjqjaoaturjb.supabase.co'],
  },
}
```

**Update post rendering:**
```tsx
<div
  className="prose max-w-none"
  dangerouslySetInnerHTML={{ __html: post.content_html }}
/>
```

### 4. Monitor

- Check upload success rate
- Monitor Supabase storage usage
- Review error logs
- Test from different browsers

## Troubleshooting

### Issue: Migration fails

**Error:** `django.db.utils.OperationalError: no such column: blog_post.content`

**Solution:**
```bash
# Ensure migrations are applied
python manage.py migrate blog --fake-initial
python manage.py migrate blog
```

### Issue: Uploads fail

**Error:** `Upload failed: 401 Unauthorized`

**Solution:**
1. Check Supabase API key is correct
2. Verify bucket exists
3. Check bucket policies allow uploads
4. Ensure user is authenticated

### Issue: Images not displaying

**Error:** Images show broken in admin

**Solution:**
1. Check Supabase bucket is public
2. Verify URL format is correct
3. Check CSP headers allow Supabase domain
4. Test URL directly in browser

### Issue: HTML not sanitized

**Error:** Script tags appear in content

**Solution:**
1. Verify bleach is installed: `pip list | grep bleach`
2. Check ALLOWED_HTML_TAGS in settings
3. Ensure Post.save() is called
4. Test sanitization manually:
   ```python
   from blog.utils_sanitize import sanitize_html
   print(sanitize_html('<script>alert("xss")</script>'))
   ```

### Issue: Reading time not calculated

**Error:** reading_time is 0

**Solution:**
1. Ensure content field has data
2. Check save() method is updated
3. Manually trigger:
   ```python
   post = Post.objects.get(slug='test')
   post.save()
   print(post.reading_time)
   ```

## Rollback Procedure

If migration fails:

### 1. Restore Database

```bash
# Restore from backup
python manage.py loaddata backup_blog_20250101.json
```

### 2. Revert Code

```bash
# Revert to pre-migration state
git checkout pre-phase8
```

### 3. Revert Migration

```bash
# Rollback migration
python manage.py migrate blog 0001_initial
```

### 4. Remove Dependencies

```bash
# Uninstall new packages
pip uninstall django-ckeditor bleach httpx
```

### 5. Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
```

## Validation Checklist

After migration, verify:

- [ ] All existing posts still display correctly
- [ ] New posts can be created with CKEditor
- [ ] Images can be uploaded
- [ ] Images display in admin
- [ ] Images display in API response
- [ ] HTML is sanitized (no XSS)
- [ ] Reading time is calculated
- [ ] Word count is calculated
- [ ] API tests pass
- [ ] Upload tests pass
- [ ] Sanitization tests pass
- [ ] Next.js renders content correctly
- [ ] SEO meta tags work
- [ ] No errors in logs

## Performance Considerations

### Before Migration

- Measure baseline API response times
- Note current database size
- Check media storage usage

### After Migration

- Compare API response times (should be similar)
- Monitor Supabase storage usage
- Check for any performance regressions

### Optimization

If performance issues:

1. **Enable caching:**
   ```python
   from django.core.cache import cache
   
   cache_key = f'post:{slug}'
   post = cache.get(cache_key)
   if not post:
       post = Post.objects.get(slug=slug)
       cache.set(cache_key, post, timeout=600)
   ```

2. **Use CDN for images:**
   - Configure CloudFront or BunnyCDN
   - Point to Supabase URLs

3. **Optimize queries:**
   ```python
   posts = Post.objects.select_related('author', 'featured_image')
   ```

## Support

If you encounter issues:

1. Check documentation: `docs/phase-8-ckeditor-supabase.md`
2. Review tests: `blog/tests/test_upload.py`
3. Check logs: `logs/django.log`
4. Test Supabase connection
5. Verify settings configuration

## Conclusion

Migration complete! Your Django Blog API now supports:

✅ Rich text editing with CKEditor
✅ Cloud storage with Supabase
✅ HTML sanitization for security
✅ Auto-calculated reading time
✅ Auto-calculated word count
✅ Next.js-ready API responses

Next steps:
1. Create content with rich media
2. Monitor performance
3. Optimize as needed
4. Enjoy the new features!
