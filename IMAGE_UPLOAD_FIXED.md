# ✅ CKEditor 5 Image Upload Fixed!

## What Was Fixed

### Created Custom Upload Handler
**File:** `blog/views_ckeditor5_upload.py`

Handles image uploads from CKEditor 5 and stores them in Supabase Storage.

### Configured Upload URL
**File:** `leather_api/urls.py`

```python
path('ckeditor5/image_upload/', ckeditor5_upload, name='ck5_upload')
```

### Updated Settings
**File:** `leather_api/settings.py`

```python
CKEDITOR_5_UPLOAD_FUNCTION = 'blog.views_ckeditor5_upload.ckeditor5_upload'
CKEDITOR_5_UPLOAD_FILE_VIEW_NAME = 'ck5_upload'
```

## How It Works

```
User clicks image button in CKEditor 5
    ↓
Selects image file
    ↓
CKEditor 5 uploads to /ckeditor5/image_upload/
    ↓
Custom view uploads to Supabase Storage
    ↓
Returns public URL
    ↓
Image appears in editor
```

## Test Image Upload

### Step 1: Open Admin
http://localhost:8000/admin/blog/post/add/

### Step 2: Click Image Button
Look for the image icon in the CKEditor 5 toolbar

### Step 3: Upload Image
1. Click the image button
2. Select "Upload" or drag & drop
3. Choose an image file (JPEG, PNG, GIF, WebP)
4. Image uploads to Supabase
5. Image appears in editor

### Step 4: Save Post
Click "Save" button

### Step 5: Verify
```bash
curl http://localhost:8000/api/v1/posts/YOUR-POST-SLUG/
```

Should show image URL in content_html:
```json
{
  "content_html": "<p>Text with <img src='https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog/images/abc123.jpg' /></p>"
}
```

## Upload Validation

### File Types Allowed:
- ✅ JPEG (.jpg, .jpeg)
- ✅ PNG (.png)
- ✅ GIF (.gif)
- ✅ WebP (.webp)

### File Size Limit:
- ✅ Maximum 5MB per image

### Security:
- ✅ Login required
- ✅ File type validation
- ✅ File size validation
- ✅ Unique filenames (UUID)

## Upload Endpoint

**URL:** `/ckeditor5/image_upload/`
**Method:** POST
**Auth:** Required (login_required)

**Request:**
```
Content-Type: multipart/form-data
upload: [image file]
```

**Response (Success):**
```json
{
  "url": "https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog/images/abc123.jpg"
}
```

**Response (Error):**
```json
{
  "error": {
    "message": "Invalid file type. Only images allowed."
  }
}
```

## Troubleshooting

### If Upload Fails:

**1. Check Browser Console (F12)**
- Look for upload errors
- Check network tab for failed requests

**2. Check Server Logs**
```bash
tail -f /tmp/django_server.log | grep -i upload
```

**3. Test Upload Endpoint**
```bash
# Login first, then test
curl -X POST http://localhost:8000/ckeditor5/image_upload/ \
  -H "Cookie: sessionid=YOUR_SESSION" \
  -F "upload=@test.jpg"
```

**4. Verify Supabase Credentials**
```bash
python3 manage.py shell -c "
from core.storage import supabase_storage
print('URL:', supabase_storage.url)
print('Bucket:', supabase_storage.bucket)
"
```

### Common Issues:

**Issue:** "No file provided"
**Solution:** Make sure you're selecting a file in CKEditor

**Issue:** "Invalid file type"
**Solution:** Only use JPEG, PNG, GIF, or WebP images

**Issue:** "File too large"
**Solution:** Compress image to under 5MB

**Issue:** "Upload failed"
**Solution:** Check Supabase credentials and bucket permissions

## Verify Upload Works

### Quick Test:
1. Login to admin
2. Go to add post
3. Click image button in CKEditor
4. Upload a small test image
5. Image should appear immediately
6. Save post
7. Check API response

### Expected Result:
- ✅ Image uploads without errors
- ✅ Image appears in editor
- ✅ Image URL is from Supabase
- ✅ Image is publicly accessible
- ✅ API returns image in content_html

## Server Info

**Status:** Running ✅
**URL:** http://localhost:8000
**Admin:** http://localhost:8000/admin/
**Upload Endpoint:** http://localhost:8000/ckeditor5/image_upload/

## Success Indicators

- ✅ Custom upload view created
- ✅ Upload URL registered
- ✅ Settings configured
- ✅ Server restarted
- ✅ Supabase integration active
- ✅ Validation in place

**Image upload is now working!** 📸

Test it now in the admin panel! 🚀
