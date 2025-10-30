# CKEditor 5 Supabase Upload Integration

## Overview

CKEditor 5 is now configured to upload all images directly to **Supabase Storage** instead of local storage. This ensures cloud-based, scalable file management suitable for production deployments.

## Implementation Details

### 1. Custom Upload Endpoint

**URL:** `/upload/ckeditor/`

**Location:** `blog/views_ckeditor5_upload.py`

**Features:**
- ✅ Accepts POST requests with `upload` file field
- ✅ Validates file type (JPEG, PNG, GIF, WebP only)
- ✅ Validates file size (max 5MB)
- ✅ Requires admin/staff authentication
- ✅ Uploads to Supabase Storage bucket
- ✅ Returns public URL in CKEditor-compatible JSON format

**Response Format:**
```json
{
  "url": "https://xyz.supabase.co/storage/v1/object/public/leather_api_storage/blog/images/uuid.jpg"
}
```

**Error Format:**
```json
{
  "error": {
    "message": "Error description"
  }
}
```

### 2. Supabase Storage Client

**Location:** `core/storage.py`

**Class:** `SupabaseStorage`

**Methods:**
- `upload_file(file, folder)` - Upload file to Supabase
- `get_public_url(path)` - Get public URL for file
- `delete_file(path)` - Delete file from Supabase

**Features:**
- Uses official `supabase-py` client
- Generates unique filenames with UUID
- Handles errors gracefully with logging
- Returns public URLs automatically

### 3. Configuration

**Settings (settings.py):**
```python
SUPABASE_URL = env('SUPABASE_URL', default='https://soccrpfkqjqjaoaturjb.supabase.co')
SUPABASE_API_KEY = env('SUPABASE_API_KEY', default='...')
SUPABASE_BUCKET = env('SUPABASE_BUCKET', default='leather_api_storage')
```

**CKEditor Config:**
```python
CKEDITOR_5_CONFIGS = {
    'extends': {
        'simpleUpload': {
            'uploadUrl': '/upload/ckeditor/',
            'withCredentials': True,
        }
    }
}
```

### 4. Security

- ✅ **Authentication Required:** Only admin/staff users can upload
- ✅ **File Type Validation:** Only images allowed
- ✅ **File Size Limit:** Maximum 5MB per file
- ✅ **CSRF Protection:** Disabled for CKEditor compatibility (admin-only endpoint)
- ✅ **Unique Filenames:** UUID-based to prevent overwrites
- ✅ **Error Logging:** All failures logged for debugging

### 5. Supabase Bucket Setup

**Bucket Name:** `leather_api_storage`

**Required Settings:**
1. Create bucket in Supabase Dashboard
2. Set bucket to **Public** (or configure public access policy)
3. Enable file uploads via API

**Bucket Policy (if needed):**
```sql
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'leather_api_storage' );

CREATE POLICY "Authenticated Upload"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'leather_api_storage' );
```

## Installation

### 1. Install Dependencies

```bash
pip install supabase>=2.0,<3.0
```

Or update from requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add to `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-anon-or-service-key
SUPABASE_BUCKET=leather_api_storage
```

### 3. Create Supabase Bucket

1. Go to Supabase Dashboard → Storage
2. Create new bucket: `leather_api_storage`
3. Set to **Public** or configure access policies
4. Test upload via API

### 4. Test Upload

1. Login to Django admin: `/admin/`
2. Create/edit a blog post
3. Use CKEditor image upload button
4. Verify image appears in Supabase Storage
5. Verify image displays in editor

## Usage

### In Django Admin

1. Navigate to any Post in admin
2. Click the image upload icon in CKEditor toolbar
3. Select an image file (JPEG, PNG, GIF, WebP)
4. Image uploads to Supabase automatically
5. Public URL is inserted into editor

### Programmatic Upload

```python
from core.storage import supabase_storage

# Upload file
url = supabase_storage.upload_file(file, folder='blog/images/')

# Get public URL
public_url = supabase_storage.get_public_url('blog/images/file.jpg')

# Delete file
supabase_storage.delete_file('blog/images/file.jpg')
```

## File Organization

Uploaded files are organized as:
```
leather_api_storage/
└── blog/
    └── images/
        ├── uuid-1.jpg
        ├── uuid-2.png
        └── uuid-3.webp
```

## Troubleshooting

### Upload Fails with 401 Unauthorized

**Solution:** Check `SUPABASE_API_KEY` in `.env` - use service role key for admin operations

### Upload Fails with 404 Not Found

**Solution:** Verify bucket name matches `SUPABASE_BUCKET` setting

### Images Don't Display

**Solution:** Ensure bucket is set to Public or has proper access policies

### File Size Error

**Solution:** Increase `MAX_FILE_SIZE` in `views_ckeditor5_upload.py` (default 5MB)

### CSRF Token Error

**Solution:** Endpoint uses `@csrf_exempt` - ensure `withCredentials: True` in CKEditor config

## Production Deployment

### Heroku/Render/Vercel

1. Set environment variables in platform dashboard
2. Ensure `supabase` package in requirements.txt
3. No local file storage needed - all files in Supabase
4. Works with ephemeral filesystems

### Performance

- Files served directly from Supabase CDN
- No Django server load for file serving
- Automatic image optimization available via Supabase

### Monitoring

Check logs for upload activity:
```bash
tail -f logs/django.log | grep "CKEditor"
```

## API Reference

### POST /upload/ckeditor/

**Authentication:** Admin/Staff required

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Field: `upload` (file)

**Response (Success):**
```json
{
  "url": "https://xyz.supabase.co/storage/v1/object/public/bucket/path/file.jpg"
}
```

**Response (Error):**
```json
{
  "error": {
    "message": "Error description"
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid file type/size or no file provided
- `403` - Not authenticated as admin/staff
- `405` - Method not allowed (not POST)
- `500` - Upload failed (Supabase error)

## Migration from Local Storage

If you have existing local uploads:

1. Export existing files from `media/` directory
2. Upload to Supabase using script:
```python
from core.storage import supabase_storage
import os

for root, dirs, files in os.walk('media/'):
    for file in files:
        path = os.path.join(root, file)
        with open(path, 'rb') as f:
            url = supabase_storage.upload_file(f, folder='blog/images/')
            print(f"Migrated: {path} -> {url}")
```
3. Update Post content_html to use new URLs

## Support

For issues or questions:
- Check Django logs: `logs/django.log`
- Check Supabase Dashboard → Storage → Logs
- Verify bucket permissions and API keys
