# Image Upload API Documentation

## Overview
All images are uploaded directly to **Supabase Storage** and only the public URL is stored in the database. No files are stored in the local `/media/` folder.

---

## 🚀 API Endpoint

### Upload Image
**POST** `/api/v1/images/upload/`

Upload an image from device to Supabase Storage.

#### Authentication
- **Required**: Yes (Bearer Token or Session Auth)

#### Request
- **Content-Type**: `multipart/form-data`
- **Body Parameters**:
  - `image` (file, required): Image file (JPEG, PNG, GIF, WebP)
  - `alt_text` (string, optional): Alt text for SEO (used for filename)
  - `folder` (string, optional): Custom folder path (default: `blog-images/`)

#### Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog-images/my-image-1234567890.jpg",
  "alt_text": "My Image",
  "width": 1920,
  "height": 1080,
  "format": "jpeg"
}
```

#### Error Responses
- **400 Bad Request**: No image file, invalid file type, or file too large
- **401 Unauthorized**: Authentication required
- **500 Internal Server Error**: Upload failed

---

## 📝 Usage Examples

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/images/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "alt_text=Beautiful leather product"
```

### Python (requests)
```python
import requests

url = "http://localhost:8000/api/v1/images/upload/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"image": open("image.jpg", "rb")}
data = {"alt_text": "Beautiful leather product"}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### JavaScript (fetch)
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('alt_text', 'Beautiful leather product');

fetch('http://localhost:8000/api/v1/images/upload/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### React Example
```jsx
const handleImageUpload = async (file) => {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('alt_text', 'Product image');

  try {
    const response = await fetch('/api/v1/images/upload/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const data = await response.json();
    console.log('Uploaded:', data.url);
    // Use data.url for featured_image or other fields
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

---

## 🎯 Django Admin Usage

### Upload Image in Admin Panel

1. Navigate to **Blog → Image Assets → Add Image Asset**
2. Click **"Choose File"** under "Upload Image"
3. Select image from your device
4. Enter **Alt Text** (used for SEO-friendly filename)
5. Click **"Save"**
6. Image automatically uploads to Supabase
7. Public URL is stored in database

### Featured Image Upload

1. Navigate to **Blog → Posts → Add Post** (or edit existing)
2. Under "Featured Image", select existing ImageAsset or create new one
3. If creating new:
   - Click **"+"** next to Featured Image dropdown
   - Upload image as described above
   - Save and return to post

---

## 🔧 Model Structure

### ImageAsset Model
```python
class ImageAsset(TimeStampedModel):
    file = models.URLField(max_length=500)  # Supabase public URL
    alt_text = models.CharField(max_length=125)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    format = models.CharField(max_length=10, default='webp')
    responsive_set = models.JSONField(default=dict, blank=True)
    lqip = models.TextField(blank=True)
    og_image_url = models.URLField(max_length=500, blank=True)
```

### Post Model (Featured Image)
```python
class Post(TimeStampedModel):
    # ... other fields
    featured_image = models.ForeignKey(
        ImageAsset, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='posts'
    )
```

---

## 🗂️ File Storage Structure

### Supabase Storage
- **Bucket**: `leather_api_storage`
- **Folder**: `blog-images/`
- **Filename Format**: `{slugified-alt-text}-{timestamp}.{extension}`
- **Example**: `beautiful-leather-product-1696789012.jpg`

### Public URL Format
```
https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog-images/{filename}
```

---

## ✅ Validation Rules

### File Type
- **Allowed**: JPEG, JPG, PNG, GIF, WebP
- **Rejected**: All other formats

### File Size
- **Maximum**: 10 MB
- **Recommended**: < 2 MB for optimal performance

### Filename
- Automatically slugified from `alt_text` or original filename
- Timestamp added to ensure uniqueness
- Special characters removed

---

## 🔐 Security

### Authentication
- All upload endpoints require authentication
- Use Django session auth or Bearer token

### CSRF Protection
- CSRF token required for session-based auth
- Exempt for API token auth

### Content Security Policy
```python
# settings.py
SECURE_CONTENT_SECURITY_POLICY = {
    'img-src': ["'self'", 'data:', 'https://soccrpfkqjqjaoaturjb.supabase.co'],
}
```

---

## 🧪 Testing

### Test Upload Endpoint
```bash
# Login to admin first
python manage.py createsuperuser

# Get auth token or use session

# Test upload
curl -X POST http://localhost:8000/api/v1/images/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@test.jpg" \
  -F "alt_text=Test Image"
```

### Expected Response
```json
{
  "id": "uuid-here",
  "url": "https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog-images/test-image-1234567890.jpg",
  "alt_text": "Test Image",
  "width": 800,
  "height": 600,
  "format": "jpeg"
}
```

---

## 🐛 Troubleshooting

### Upload Fails
1. Check Supabase credentials in `.env`
2. Verify bucket exists and is public
3. Check file size and type
4. Review logs: `tail -f logs/django.log`

### Image Not Displaying
1. Verify Supabase URL is accessible
2. Check bucket permissions (should be public)
3. Verify CSP settings allow Supabase domain

### Admin Upload Issues
1. Clear browser cache
2. Check Django admin static files
3. Verify form is using `ImageAssetAdminForm`

---

## 📊 Monitoring

### Check Uploaded Images
```python
from blog.models import ImageAsset

# List all images
images = ImageAsset.objects.all()
for img in images:
    print(f"{img.alt_text}: {img.file}")

# Check recent uploads
recent = ImageAsset.objects.order_by('-created_at')[:10]
```

### Supabase Storage Dashboard
- Login to Supabase Dashboard
- Navigate to Storage → `leather_api_storage`
- View `blog-images/` folder
- Monitor storage usage

---

## 🚀 Next Steps

1. **Implement image optimization**: Add WebP conversion, responsive variants
2. **Add LQIP generation**: Low-quality image placeholders
3. **Implement CDN**: Use Cloudflare or BunnyCDN for faster delivery
4. **Add image deletion**: Clean up Supabase when ImageAsset is deleted
5. **Batch upload**: Support multiple images at once

---

## 📚 Related Files

- `/blog/views_image_upload.py` - Main upload endpoint
- `/blog/admin_forms.py` - Admin upload form
- `/core/storage.py` - Supabase storage utility
- `/blog/models.py` - ImageAsset model
- `/blog/admin.py` - Admin configuration
