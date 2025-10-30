# ✅ Featured Images Now Use Supabase Storage

## Changes Implemented

### 1. Updated Storage Backend
**File:** `core/storage.py`
- ✅ Using official Supabase Python client
- ✅ SEO-friendly filenames (slugified title + timestamp)
- ✅ Returns public Supabase URLs

### 2. Modified ImageAsset Model
**File:** `blog/models.py`
```python
class ImageAsset:
    file = models.URLField(max_length=500)  # Supabase URL (not ImageField)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
```

### 3. Created Upload Serializers
**File:** `blog/serializers_upload.py`
- `ImageAssetUploadSerializer` - Handles image uploads
- `PostCreateUpdateSerializer` - Handles post with featured_image

### 4. Migration Applied
```bash
✅ Migration 0004 applied
✅ ImageAsset.file changed from ImageField to URLField
```

## How It Works

### Upload Flow:
```
1. User uploads image via API/Admin
   ↓
2. Serializer receives image file
   ↓
3. Upload to Supabase Storage (blog-images/ folder)
   ↓
4. Generate SEO-friendly filename (post-title-timestamp.jpg)
   ↓
5. Get public URL from Supabase
   ↓
6. Save URL in ImageAsset.file field
   ↓
7. API returns Supabase URL
```

### Example API Usage:

**Create Post with Featured Image:**
```bash
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer TOKEN" \
  -F "title=My Blog Post" \
  -F "summary=Post summary" \
  -F "content=Post content" \
  -F "author=AUTHOR_ID" \
  -F "featured_image_file=@image.jpg"
```

**Response:**
```json
{
  "id": "uuid",
  "title": "My Blog Post",
  "featured_image_url": "https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog-images/my-blog-post-1234567890.jpg"
}
```

## Admin Panel

Featured images uploaded via admin will also go to Supabase automatically.

## No More /media/ Folder

- ✅ All images stored in Supabase
- ✅ Database stores only URLs
- ✅ No local file handling
- ✅ CDN-ready public URLs

## Testing

### Test Upload:
```bash
python3 manage.py shell
```

```python
from blog.models import ImageAsset
from django.core.files.uploadedfile import SimpleUploadedFile
from core.storage import supabase_storage

# Test direct upload
with open('test.jpg', 'rb') as f:
    from django.core.files.uploadedfile import InMemoryUploadedFile
    file = InMemoryUploadedFile(f, None, 'test.jpg', 'image/jpeg', f.seek(0, 2), None)
    f.seek(0)
    url = supabase_storage.upload_file(file, folder='blog-images/', filename='test-image')
    print(f"✅ Uploaded: {url}")
```

### Verify:
```bash
curl http://localhost:8000/api/v1/posts/
```

All `featured_image` URLs should point to Supabase.

## Configuration

**Settings already configured:**
```python
SUPABASE_URL = 'https://soccrpfkqjqjaoaturjb.supabase.co'
SUPABASE_API_KEY = 'your-key'
SUPABASE_BUCKET = 'leather_api_storage'
```

## Server Status

**Running:** http://localhost:8000
**API:** http://localhost:8000/api/v1/posts/

## Summary

✅ ImageAsset.file changed to URLField
✅ Supabase Python client integrated
✅ SEO-friendly filenames
✅ Upload serializers created
✅ Migration applied
✅ No /media/ folder usage
✅ Public Supabase URLs in database
✅ CKEditor also uses Supabase

**All images now stored in Supabase Storage!** 📸☁️
