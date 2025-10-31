# 📸 Image Upload Guide

## ✅ Status: WORKING

All image upload functionality is working correctly with Supabase Storage.

## 🔧 Configuration

### Environment Variables (.env)
```bash
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_BUCKET=leather_api_storage
```

✅ All configured and validated

## 📡 API Endpoints

### 1. REST API Upload (Authenticated)
```bash
POST /api/v1/images/upload/
Authorization: Bearer <token>
Content-Type: multipart/form-data

# Form data:
- image: <file> (required)
- alt_text: <string> (optional)
- folder: <string> (optional, default: blog-images/)
```

**Response:**
```json
{
  "id": "uuid",
  "url": "https://supabase.co/storage/...",
  "alt_text": "Image description",
  "width": 1920,
  "height": 1080,
  "format": "png"
}
```

### 2. CKEditor 5 Upload (Staff Only)
```bash
POST /ckeditor5/image_upload/
POST /upload/ckeditor/

# Form data:
- upload: <file>
```

**Response:**
```json
{
  "url": "https://supabase.co/storage/..."
}
```

## 🧪 Testing

Run the test script:
```bash
source venv/bin/activate
python3 test_image_upload.py
```

**Test Results:**
- ✅ Configuration: PASSED
- ✅ Storage Client: PASSED
- ✅ Image Upload: PASSED
- ✅ API Endpoints: PASSED

## 📋 Validation Rules

### File Types
- ✅ JPEG/JPG
- ✅ PNG
- ✅ GIF
- ✅ WebP

### File Size Limits
- REST API: 10MB max
- CKEditor: 5MB max

## 🔐 Authentication

### REST API (`/api/v1/images/upload/`)
- Requires: JWT Bearer token
- Permission: IsAuthenticated

### CKEditor (`/ckeditor5/image_upload/`)
- Requires: Staff/Admin login
- Permission: @staff_member_required

## 💾 Storage Details

### Supabase Storage
- **Bucket:** leather_api_storage
- **Default Folder:** blog-images/
- **URL Format:** `https://{project}.supabase.co/storage/v1/object/public/{bucket}/{path}`

### File Naming
- Slugified alt_text + timestamp
- Example: `my-image-1761936560.png`

## 🎯 Usage Examples

### cURL Example
```bash
# Get JWT token first
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  | jq -r '.access')

# Upload image
curl -X POST http://localhost:8000/api/v1/images/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "alt_text=My awesome image"
```

### Python Example
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', json={
    'username': 'admin',
    'password': 'your-password'
})
token = response.json()['access']

# Upload image
files = {'image': open('image.jpg', 'rb')}
data = {'alt_text': 'My image'}
headers = {'Authorization': f'Bearer {token}'}

response = requests.post(
    'http://localhost:8000/api/v1/images/upload/',
    files=files,
    data=data,
    headers=headers
)

print(response.json())
```

### JavaScript/Fetch Example
```javascript
// Get token from login
const token = localStorage.getItem('access_token');

// Upload image
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('alt_text', 'My image');

const response = await fetch('http://localhost:8000/api/v1/images/upload/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const data = await response.json();
console.log(data.url);
```

## 🐛 Troubleshooting

### Error: "No image file provided"
- Ensure form field name is `image` (not `file` or `upload`)
- Check Content-Type is `multipart/form-data`

### Error: "Invalid file type"
- Only JPEG, PNG, GIF, WebP allowed
- Check file extension and MIME type

### Error: "File too large"
- REST API: Max 10MB
- CKEditor: Max 5MB

### Error: "Authentication credentials were not provided"
- Include JWT token in Authorization header
- Format: `Authorization: Bearer <token>`

### Error: "Upload failed"
- Check Supabase credentials in .env
- Verify bucket exists and is public
- Check network connectivity

## 📊 Image Asset Model

Uploaded images are tracked in the database:

```python
class ImageAsset(models.Model):
    id = UUIDField(primary_key=True)
    file = URLField()  # Supabase URL
    alt_text = CharField(max_length=255)
    width = IntegerField()
    height = IntegerField()
    format = CharField(max_length=10)
    created_at = DateTimeField(auto_now_add=True)
```

## 🚀 Production Deployment

### Environment Variables
Ensure these are set in production:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-production-key
SUPABASE_BUCKET=your-bucket-name
```

### CORS Configuration
Add your frontend domain to Supabase Storage CORS settings:
```
https://zaryableather.com
https://www.zaryableather.com
```

### Security Checklist
- ✅ JWT authentication enabled
- ✅ File type validation
- ✅ File size limits
- ✅ Staff-only access for CKEditor
- ✅ Secure Supabase credentials

---

**Last Updated:** October 31, 2025  
**Status:** ✅ Fully Operational  
**Test Results:** All tests passing
