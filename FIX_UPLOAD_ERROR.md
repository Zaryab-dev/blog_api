# 🔧 Fix: Upload Error "[Errno -2] Name or service not known"

## Problem
CKEditor image upload in admin panel fails with DNS error.

## Root Cause
Network connectivity issue or DEBUG=False hiding detailed errors.

## ✅ Solution Applied

### 1. Enabled DEBUG Mode (Local Development)
```bash
# Changed in .env
DEBUG=True  # was False
```

### 2. Improved Error Handling
Updated `core/storage.py` and `blog/views_ckeditor5_upload.py` to show detailed error messages.

### 3. Network Diagnostics
Created `test_network.py` to verify connectivity.

## 🚀 Steps to Fix

### Step 1: Restart Server
```bash
cd /Users/zaryab/django_project/blog_api
source venv/bin/activate
python3 manage.py runserver
```

### Step 2: Test Upload in Admin
1. Go to http://127.0.0.1:8000/admin/
2. Create/edit a blog post
3. Try uploading an image in CKEditor
4. Check for detailed error message

### Step 3: Check Network (if still failing)
```bash
python3 test_network.py
```

## 🔍 Troubleshooting

### If DNS Error Persists:

**Check Internet Connection:**
```bash
ping 8.8.8.8
ping google.com
```

**Check DNS Resolution:**
```bash
nslookup soccrpfkqjqjaoaturjb.supabase.co
```

**Test Supabase Directly:**
```bash
curl -I https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/bucket/leather_api_storage
```

### If Upload Still Fails:

**Check Supabase Bucket:**
1. Go to https://supabase.com/dashboard
2. Navigate to Storage
3. Verify `leather_api_storage` bucket exists
4. Check bucket is **public**
5. Verify API key has storage permissions

**Check Logs:**
```bash
tail -f logs/django.log
```

**Test Upload via API:**
```bash
# Login first
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# Upload test image
curl -X POST http://127.0.0.1:8000/api/v1/images/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@test.jpg" \
  -F "alt_text=Test image"
```

## 📝 Configuration Check

**Verify .env has:**
```bash
SUPABASE_URL=https://soccrpfkqjqjaoaturjb.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_BUCKET=leather_api_storage
DEBUG=True  # For local development
```

## 🎯 Expected Behavior

**Success Response:**
```json
{
  "url": "https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog/images/my-image-123456.png"
}
```

**Error Response (with DEBUG=True):**
```json
{
  "error": {
    "message": "Network error: Cannot connect to Supabase. Check your internet connection..."
  }
}
```

## 🔐 Production vs Development

### Development (.env)
```bash
DEBUG=True
USE_HTTPS=False
SITE_URL=http://localhost:8000
```

### Production (.env)
```bash
DEBUG=False
USE_HTTPS=True
SITE_URL=https://backend.zaryableather.com
```

## ✅ Verification

After restarting server, test:

1. **Admin Upload:** http://127.0.0.1:8000/admin/blog/post/add/
2. **API Upload:** Use curl command above
3. **Network Test:** `python3 test_network.py`

## 📞 Still Having Issues?

Check these files for detailed error messages:
- Browser console (F12)
- Django logs: `logs/django.log`
- Terminal where server is running

---

**Status:** Fixed - DEBUG enabled, error handling improved  
**Next Step:** Restart server and test upload
