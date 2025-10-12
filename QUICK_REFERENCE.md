# 🚀 Image Upload Quick Reference

## API Endpoint

### Upload Image
```bash
POST /api/v1/images/upload/

# cURL
curl -X POST http://localhost:8000/api/v1/images/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@image.jpg" \
  -F "alt_text=My Image"

# Response
{
  "id": "uuid",
  "url": "https://supabase.co/storage/.../image.jpg",
  "alt_text": "My Image",
  "width": 1920,
  "height": 1080,
  "format": "jpeg"
}
```

---

## Admin Panel

### Upload Image
1. Go to http://localhost:8000/admin/blog/imageasset/add/
2. Click "Choose File"
3. Select image
4. Enter alt text
5. Click "Save"

### Add Featured Image to Post
1. Go to http://localhost:8000/admin/blog/post/
2. Click "Add Post" or edit existing
3. Click "+" next to "Featured Image"
4. Upload image (see above)
5. Select created image
6. Save post

---

## Python Code

### Upload via API
```python
import requests

url = "http://localhost:8000/api/v1/images/upload/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"image": open("image.jpg", "rb")}
data = {"alt_text": "Product image"}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json()['url'])
```

### Direct Storage Upload
```python
from core.storage import supabase_storage

url = supabase_storage.upload_file(
    file,
    folder='blog-images/',
    filename='my-image'
)
```

### Create ImageAsset
```python
from blog.models import ImageAsset

image = ImageAsset.objects.create(
    file='https://supabase.co/storage/.../image.jpg',
    alt_text='Product image',
    width=1920,
    height=1080,
    format='jpeg'
)
```

---

## JavaScript/React

### Upload from Frontend
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('alt_text', 'Product image');

const response = await fetch('/api/v1/images/upload/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

const data = await response.json();
console.log('Uploaded:', data.url);
```

---

## Configuration

### Environment Variables
```bash
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=your-api-key
SUPABASE_BUCKET=leather_api_storage
```

### Settings
```python
SUPABASE_URL = env('SUPABASE_URL')
SUPABASE_API_KEY = env('SUPABASE_API_KEY')
SUPABASE_BUCKET = env('SUPABASE_BUCKET')
SUPABASE_IMAGE_FOLDER = 'blog-images/'
```

---

## Validation

### File Type
- ✅ JPEG, JPG, PNG, GIF, WebP
- ❌ All other formats

### File Size
- ✅ Max 10MB
- ❌ Larger files rejected

### Authentication
- ✅ Required for all uploads
- ❌ Anonymous uploads not allowed

---

## Storage Structure

```
Supabase Storage
└── leather_api_storage (bucket)
    └── blog-images/
        ├── product-image-1760181234.jpg
        ├── featured-photo-1760181456.webp
        └── test-upload-1760181506.jpg
```

---

## Testing

### Run Test Script
```bash
python3 test_image_upload.py
```

### Expected Output
```
✅ Upload successful!
✅ ImageAsset created!
✅ All tests passed!
```

---

## Troubleshooting

### Upload Fails
```bash
# Check credentials
python3 manage.py shell
>>> from django.conf import settings
>>> print(settings.SUPABASE_URL)
>>> print(settings.SUPABASE_BUCKET)
```

### Image Not Displaying
1. Check bucket is public in Supabase Dashboard
2. Verify URL is accessible in browser
3. Check CSP settings

### Admin Upload Not Working
1. Clear browser cache
2. Check form is using `ImageAssetAdminForm`
3. Verify Supabase credentials

---

## Key Files

```
blog/views_image_upload.py       # API endpoint
blog/admin_forms.py              # Admin form
core/storage.py                  # Storage utility
blog/models.py                   # ImageAsset model
blog/admin.py                    # Admin config
```

---

## Documentation

- **API_IMAGE_UPLOAD.md** - Complete API docs
- **SUPABASE_SETUP.md** - Setup guide
- **IMPLEMENTATION_SUMMARY.md** - Overview

---

## Admin Credentials

```
Username: admin
Password: admin123
URL: http://localhost:8000/admin/
```

---

## Status

✅ **Implementation Complete**  
✅ **All Tests Passing**  
✅ **API Working**  
✅ **Admin Working**  
✅ **No Local Storage**
