# Supabase Image Upload Setup Guide

## ✅ Implementation Complete

Your Django Blog API now supports **direct image uploads to Supabase Storage** with only URLs stored in the database.

---

## 🎯 What's Implemented

### 1. **API Endpoint**
- **POST** `/api/v1/images/upload/`
- Accepts `multipart/form-data` with image file
- Returns Supabase public URL + metadata
- Authentication required

### 2. **Django Admin Integration**
- Custom upload form for ImageAsset
- Upload images directly from admin panel
- Automatic Supabase upload on save
- Image preview with Supabase URLs

### 3. **Storage Backend**
- All images stored in Supabase Storage
- Bucket: `leather_api_storage`
- Folder: `blog-images/`
- SEO-friendly filenames (slugified + timestamp)

### 4. **Database Schema**
- `ImageAsset.file` = URLField (Supabase URL)
- No local file storage
- Metadata: width, height, format, alt_text

---

## 📁 Files Created/Modified

### New Files
```
blog/views_image_upload.py       # API upload endpoint
blog/admin_forms.py              # Admin upload form
blog/admin_widgets.py            # Custom admin widget
test_image_upload.py             # Test script
API_IMAGE_UPLOAD.md              # API documentation
SUPABASE_SETUP.md                # This file
```

### Modified Files
```
blog/admin.py                    # Updated ImageAssetAdmin
blog/urls_v1.py                  # Added image upload route
leather_api/settings.py          # Added SUPABASE_IMAGE_FOLDER
```

---

## 🚀 Quick Start

### 1. Verify Supabase Configuration
```bash
# Check .env file
cat .env | grep SUPABASE
```

Should show:
```
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_BUCKET=leather_api_storage
```

### 2. Verify Bucket Exists
- Login to [Supabase Dashboard](https://supabase.com/dashboard)
- Navigate to **Storage**
- Ensure `leather_api_storage` bucket exists
- Set bucket to **Public** (for public URLs)

### 3. Test Upload
```bash
# Run test script
python test_image_upload.py
```

Expected output:
```
✅ Upload successful!
📸 URL: https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/...
✅ ImageAsset created!
```

### 4. Test API Endpoint
```bash
# Login to get session cookie
curl -X POST http://localhost:8000/admin/login/ \
  -d "username=admin&password=admin123"

# Upload image
curl -X POST http://localhost:8000/api/v1/images/upload/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -F "image=@test.jpg" \
  -F "alt_text=Test Image"
```

### 5. Test Admin Panel
1. Navigate to http://localhost:8000/admin/
2. Login with `admin` / `admin123`
3. Go to **Blog → Image Assets → Add Image Asset**
4. Upload an image
5. Verify it appears in Supabase Storage

---

## 🔧 Configuration

### Settings (leather_api/settings.py)
```python
# Supabase Storage
SUPABASE_URL = 'https://soccrpfkqjqjaoaturjb.supabase.co'
SUPABASE_API_KEY = 'your-api-key'
SUPABASE_BUCKET = 'leather_api_storage'
SUPABASE_IMAGE_FOLDER = 'blog-images/'
```

### Storage Utility (core/storage.py)
```python
from core.storage import supabase_storage

# Upload file
url = supabase_storage.upload_file(
    file,
    folder='blog-images/',
    filename='my-image'
)

# Get public URL
url = supabase_storage.get_public_url('blog-images/image.jpg')

# Delete file
supabase_storage.delete_file('blog-images/image.jpg')
```

---

## 📊 Usage Examples

### API Upload (Python)
```python
import requests

url = "http://localhost:8000/api/v1/images/upload/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"image": open("image.jpg", "rb")}
data = {"alt_text": "Product image"}

response = requests.post(url, headers=headers, files=files, data=data)
data = response.json()

print(f"Uploaded: {data['url']}")
# Use data['url'] for featured_image or other fields
```

### Admin Upload
1. Create/Edit Post
2. Click "+" next to Featured Image
3. Upload image file
4. Enter alt text
5. Save
6. Image automatically uploads to Supabase

### Direct Model Usage
```python
from blog.models import ImageAsset

# Create with Supabase URL
image = ImageAsset.objects.create(
    file='https://supabase.co/storage/.../image.jpg',
    alt_text='Product image',
    width=1920,
    height=1080,
    format='jpeg'
)

# Use in Post
post.featured_image = image
post.save()
```

---

## 🔍 Verification Checklist

- [ ] Supabase credentials configured in `.env`
- [ ] Bucket `leather_api_storage` exists and is public
- [ ] Test script runs successfully
- [ ] API endpoint returns Supabase URL
- [ ] Admin upload works
- [ ] Images display in admin panel
- [ ] Featured images work in posts
- [ ] No files in local `/media/` folder

---

## 🐛 Troubleshooting

### Upload Fails with "Invalid credentials"
```bash
# Check Supabase credentials
python manage.py shell
>>> from django.conf import settings
>>> print(settings.SUPABASE_URL)
>>> print(settings.SUPABASE_API_KEY)
```

### Images Don't Display
1. Check bucket is **public** in Supabase Dashboard
2. Verify URL format: `https://[project].supabase.co/storage/v1/object/public/[bucket]/[path]`
3. Check CSP settings allow Supabase domain

### Admin Upload Not Working
1. Clear browser cache
2. Check `ImageAssetAdminForm` is imported in `admin.py`
3. Verify `form = ImageAssetAdminForm` in `ImageAssetAdmin`

### API Returns 401 Unauthorized
1. Ensure user is authenticated
2. Use session cookie or Bearer token
3. Check CSRF token for session auth

---

## 📈 Performance Tips

### 1. Image Optimization
- Compress images before upload (< 2MB recommended)
- Use WebP format for better compression
- Consider lazy loading on frontend

### 2. CDN Integration
- Use Cloudflare or BunnyCDN in front of Supabase
- Cache images at edge locations
- Reduce latency for global users

### 3. Responsive Images
- Generate multiple sizes (thumbnail, medium, large)
- Store in `responsive_set` JSON field
- Serve appropriate size based on device

---

## 🔐 Security

### Authentication
- All upload endpoints require authentication
- Use Django session or Bearer token
- Rate limiting applied (see `throttles.py`)

### File Validation
- File type: JPEG, PNG, GIF, WebP only
- File size: Max 10MB
- Filename: Auto-sanitized (slugified)

### Bucket Permissions
- Bucket should be **public** for read access
- Write access only via API key (server-side)
- No direct client uploads (security)

---

## 🚀 Next Steps

### Recommended Enhancements
1. **Image Optimization**: Add WebP conversion, compression
2. **Responsive Variants**: Generate multiple sizes
3. **LQIP**: Low-quality image placeholders
4. **CDN**: Cloudflare/BunnyCDN integration
5. **Cleanup**: Delete from Supabase when ImageAsset deleted
6. **Batch Upload**: Support multiple images at once
7. **Image Cropping**: Admin interface for cropping
8. **Alt Text AI**: Auto-generate alt text with AI

---

## 📚 Documentation

- **API Docs**: See `API_IMAGE_UPLOAD.md`
- **Supabase Docs**: https://supabase.com/docs/guides/storage
- **Django Admin**: http://localhost:8000/admin/
- **API Schema**: http://localhost:8000/api/v1/schema/

---

## ✅ Summary

Your blog API now has:
- ✅ Direct Supabase uploads (no local storage)
- ✅ API endpoint for image uploads
- ✅ Admin panel integration
- ✅ SEO-friendly filenames
- ✅ Automatic metadata extraction
- ✅ Public URL storage in database
- ✅ Featured image support
- ✅ Authentication & validation

**No files are stored locally** - everything goes to Supabase! 🎉
