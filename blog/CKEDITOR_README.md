# CKEditor Integration with Supabase Storage

## Overview

This module provides rich text editing capabilities with cloud storage for the Django Blog API.

## Components

### 1. Upload Handler (`views_upload.py`)

Handles image uploads from CKEditor to Supabase Storage.

**Endpoint:** `POST /api/v1/upload-image/`

**Features:**
- Authentication required
- File type validation (JPEG, PNG, GIF, WebP)
- Size limit (5MB)
- Returns CKEditor-compatible JSON

**Example:**
```python
from blog.views_upload import upload_image

# Called automatically by CKEditor when user uploads image
```

### 2. HTML Sanitizer (`utils_sanitize.py`)

Provides HTML sanitization and content processing utilities.

**Functions:**

```python
from blog.utils_sanitize import (
    sanitize_html,
    strip_html_tags,
    calculate_reading_time,
    extract_excerpt,
    count_words
)

# Sanitize HTML content
clean_html = sanitize_html('<p>Hello <script>alert("xss")</script></p>')
# Output: '<p>Hello </p>'

# Extract plain text
text = strip_html_tags('<p>Hello <strong>world</strong></p>')
# Output: 'Hello world'

# Calculate reading time
minutes = calculate_reading_time(html_content)
# Output: 5 (for ~1000 words)

# Extract excerpt
excerpt = extract_excerpt(html_content, max_length=320)
# Output: 'First 320 characters...'

# Count words
count = count_words(html_content)
# Output: 1000
```

### 3. Post Model Updates

The Post model now includes:

```python
class Post(TimeStampedModel):
    content = RichTextUploadingField(config_name='default', blank=True)
    content_html = models.TextField(editable=False)  # Auto-sanitized
    reading_time = models.IntegerField(default=0)  # Auto-calculated
    word_count = models.IntegerField(default=0)  # Auto-calculated
```

**Auto-processing on save:**
- HTML sanitization
- Reading time calculation
- Word count calculation

## Configuration

### Settings

```python
# CKEditor
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
        'extraPlugins': ','.join(['codesnippet', 'uploadimage', 'image2']),
    },
}

# Supabase
SUPABASE_URL = 'https://soccrpfkqjqjaoaturjb.supabase.co'
SUPABASE_API_KEY = 'your-api-key'
SUPABASE_BUCKET = 'leather_api_storage'

# HTML Sanitization
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'img',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]
```

### URLs

```python
from blog.views_upload import upload_image

urlpatterns = [
    path('upload-image/', upload_image, name='upload-image'),
]
```

## Usage

### Django Admin

1. Go to Post admin
2. Use CKEditor to create content
3. Click image button to upload
4. Image is uploaded to Supabase
5. Image URL is embedded in content
6. On save, HTML is sanitized

### Programmatic

```python
from blog.models import Post
from blog.utils_sanitize import sanitize_html

# Create post with rich content
post = Post.objects.create(
    title='My Post',
    content='<p>Rich <strong>HTML</strong> content</p>',
    author=author,
    status='published'
)

# Content is automatically sanitized
print(post.content_html)  # Sanitized HTML
print(post.reading_time)  # Auto-calculated
print(post.word_count)    # Auto-calculated
```

## Security

### XSS Prevention

All HTML is sanitized using `bleach`:
- Dangerous tags removed (script, iframe, etc.)
- Dangerous attributes removed (onclick, onerror, etc.)
- External links get `rel="noopener noreferrer"`

### Upload Security

- Authentication required
- File type validation
- File size limits
- Unique filenames (UUID)

## Testing

### Run Tests

```bash
# Upload tests
python manage.py test blog.tests.test_upload

# Sanitization tests
python manage.py test blog.tests.test_sanitize
```

### Test Coverage

```bash
pytest --cov=blog.views_upload --cov=blog.utils_sanitize
```

## API Response

### Post Detail

```json
{
  "id": "uuid",
  "title": "Blog Post",
  "content_html": "<p>Sanitized <strong>HTML</strong> with <img src='https://supabase.co/...' /></p>",
  "reading_time": 5,
  "word_count": 1000,
  "author": {...},
  "seo": {...}
}
```

## Next.js Integration

### Render Content

```tsx
import { Post } from '@/types/blog';

export default function BlogPost({ post }: { post: Post }) {
  return (
    <article className="prose prose-lg max-w-none">
      <h1>{post.title}</h1>
      
      <div className="text-gray-600">
        {post.reading_time} min read
      </div>
      
      <div
        dangerouslySetInnerHTML={{ __html: post.content_html }}
      />
    </article>
  );
}
```

### Configure Images

```js
// next.config.js
module.exports = {
  images: {
    domains: ['soccrpfkqjqjaoaturjb.supabase.co'],
  },
}
```

## Troubleshooting

### Upload Fails

**Check:**
1. User is authenticated
2. Supabase credentials are correct
3. Bucket exists and is public
4. File type is allowed
5. File size is under 5MB

**Debug:**
```bash
# Check logs
tail -f logs/django.log

# Test Supabase connection
curl -X POST \
  https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/leather_api_storage/test.txt \
  -H "Authorization: Bearer {API_KEY}" \
  -d "test"
```

### HTML Not Sanitized

**Check:**
1. `bleach` is installed
2. `ALLOWED_HTML_TAGS` is configured
3. Post.save() is called (triggers sanitization)

**Debug:**
```python
from blog.utils_sanitize import sanitize_html

html = '<p>Test <script>alert("xss")</script></p>'
clean = sanitize_html(html)
print(clean)  # Should not contain <script>
```

### Images Not Displaying

**Check:**
1. Supabase bucket is public
2. CSP headers allow Supabase domain
3. Next.js config includes Supabase domain

**Debug:**
```bash
# Test image URL
curl -I https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog/images/test.jpg
```

## Performance

### Caching

Content is sanitized once on save and stored in `content_html`:

```python
# No need to sanitize on every request
post = Post.objects.get(slug='my-post')
return post.content_html  # Already sanitized
```

### Reading Time

Calculated once on save:

```python
# No need to calculate on every request
post = Post.objects.get(slug='my-post')
return post.reading_time  # Already calculated
```

## Best Practices

### Content Creation

1. Use semantic HTML (h2, h3 for structure)
2. Optimize images before upload
3. Add descriptive alt text
4. Use lists for enumeration
5. Add internal links

### Code Quality

1. Always sanitize user input
2. Test for XSS vulnerabilities
3. Handle upload errors gracefully
4. Log important events
5. Monitor performance

## Monitoring

### Metrics

```python
# Track upload success rate
uploads_total = cache.get('uploads_total', 0)
uploads_failed = cache.get('uploads_failed', 0)
success_rate = (uploads_total - uploads_failed) / uploads_total

# Track average upload time
import time
start = time.time()
supabase_storage.upload_file(file)
duration = time.time() - start
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Image uploaded: {url}")
logger.error(f"Upload failed: {str(e)}")
```

## Future Enhancements

1. **Image Optimization**
   - Auto-resize on upload
   - Generate thumbnails
   - WebP conversion

2. **Video Support**
   - Upload videos to Supabase
   - Embed YouTube/Vimeo

3. **File Management**
   - Browse uploaded files
   - Delete unused files
   - Organize by folder

## Support

For issues or questions:
1. Check `docs/phase-8-ckeditor-supabase.md`
2. Review test files for examples
3. Check Supabase dashboard
4. Review Django logs

## License

MIT License - See LICENSE file for details
