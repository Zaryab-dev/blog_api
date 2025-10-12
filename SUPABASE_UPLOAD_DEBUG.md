# 🔍 Supabase Upload Debugging

## Current Setup

**Upload View:** `/ckeditor5/image_upload/`
**Handler:** `blog.views_ckeditor5_upload.ckeditor5_upload`
**Storage:** Supabase Storage (not local media folder)

## Debug Steps

### 1. Check Supabase Credentials

```bash
python3 manage.py shell -c "
from django.conf import settings
print('Supabase URL:', settings.SUPABASE_URL)
print('Supabase Bucket:', settings.SUPABASE_BUCKET)
print('API Key set:', bool(settings.SUPABASE_API_KEY))
"
```

### 2. Test Upload Manually

**In admin, try uploading an image and check logs:**

```bash
tail -f /tmp/django_server.log | grep -i "upload\|supabase"
```

You should see:
```
Upload request: method=POST, files=['upload']
Uploading to Supabase: test.jpg, size=12345, type=image/jpeg
✅ CKEditor 5 image uploaded successfully: https://soccrpfkqjqjaoaturjb.supabase.co/...
```

### 3. Check What's Happening

**If you see logs going to media folder instead:**
- CKEditor 5 is using default upload, not our custom one
- Need to verify simpleUpload configuration

**If you see our logs but upload fails:**
- Check Supabase credentials
- Check bucket permissions
- Check network connectivity

### 4. Verify Upload URL

```bash
curl http://localhost:8000/ckeditor5/image_upload/
```

Should return: `{"error": {"message": "No file provided"}}`

## Current Configuration

**Settings:**
```python
CKEDITOR_5_UPLOAD_FILE_VIEW_NAME = 'ck5_upload'

'simpleUpload': {
    'uploadUrl': '/ckeditor5/image_upload/',
}
```

**URLs:**
```python
path('ckeditor5/image_upload/', ckeditor5_upload, name='ck5_upload')
```

## What to Check

1. **Upload an image in admin**
2. **Watch the logs:** `tail -f /tmp/django_server.log`
3. **Tell me what you see:**
   - Does it show "Upload request" log?
   - Does it show "Uploading to Supabase" log?
   - Any errors?
   - Where is the image being saved?

## Supabase Info Needed

If upload fails, I need:
- ✅ Supabase URL (already have)
- ✅ API Key (already have)
- ✅ Bucket name (already have)
- ❓ Is bucket public?
- ❓ Are upload permissions set?

**Please try uploading an image and share what you see in the logs!**
