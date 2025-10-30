# 🔐 Admin Login & CKEditor Test

## Admin Credentials

**URL:** http://localhost:8000/admin/

**Username:** `admin`
**Password:** `admin123`

## Test CKEditor

### Step 1: Login
1. Go to: http://localhost:8000/admin/
2. Enter credentials above
3. Click "Log in"

### Step 2: Create Post
1. Click "Posts" → "Add Post"
2. Or go directly to: http://localhost:8000/admin/blog/post/add/

### Step 3: Fill Form
- **Title:** Test CKEditor Post
- **Slug:** test-ckeditor-post (auto-fills)
- **Summary:** Testing rich text editor
- **Content:** ← THIS IS THE CKEDITOR FIELD
  - Should show rich text editor with toolbar
  - Type some text
  - Try formatting (bold, italic, etc.)
  - Try image upload button
- **Author:** Select "Zaryab Khan"
- **Status:** Published

### Step 4: Save
Click "Save" button

### Step 5: Verify API
```bash
curl http://localhost:8000/api/v1/posts/test-ckeditor-post/
```

## CKEditor Field Details

**Field Name:** Content (Rich Text Editor)
**Widget:** CKEditorUploadingWidget
**Features:**
- Rich text formatting
- Image upload to Supabase
- Code snippets
- Tables
- Links
- Lists

## What You Should See

### In Admin Form:
```
┌─────────────────────────────────────┐
│ Content (Rich Text Editor)          │
├─────────────────────────────────────┤
│ [B] [I] [U] [≡] [🔗] [📷] [⚙️]      │ ← Toolbar
├─────────────────────────────────────┤
│                                     │
│  Type your content here...          │ ← Editable area
│                                     │
│                                     │
└─────────────────────────────────────┘
```

### Toolbar Buttons:
- **B** = Bold
- **I** = Italic  
- **U** = Underline
- **≡** = Lists
- **🔗** = Link
- **📷** = Image upload
- **⚙️** = More options

## Troubleshooting

### If CKEditor Not Showing:

1. **Hard Refresh Browser**
   - Mac: Cmd + Shift + R
   - Windows: Ctrl + Shift + R

2. **Check Browser Console**
   - Press F12
   - Look for JavaScript errors
   - Should see CKEditor loading

3. **Verify Static Files**
   ```bash
   ls staticfiles/ckeditor/ckeditor/ckeditor.js
   ```
   Should exist

4. **Check Server Logs**
   ```bash
   tail -50 /tmp/django_server.log
   ```

### If Field is Empty/Disabled:

1. Make sure you're logged in as admin
2. Check that form is using PostAdminForm
3. Verify widget is CKEditorUploadingWidget:
   ```bash
   python3 manage.py shell -c "from blog.admin import PostAdminForm; print(type(PostAdminForm().fields['content'].widget).__name__)"
   ```
   Should output: `CKEditorUploadingWidget`

## Test Upload

1. Click image button (📷) in toolbar
2. Go to "Upload" tab
3. Choose an image file
4. Click "Send it to the Server"
5. Image should upload to Supabase
6. Image appears in editor

## Expected Behavior

✅ CKEditor loads with toolbar
✅ Can type and edit text
✅ Formatting buttons work
✅ Image upload works
✅ Content saves to database
✅ HTML is sanitized on save
✅ API returns clean HTML

## Server Status

**Running:** http://localhost:8000 ✅
**Admin:** http://localhost:8000/admin/ ✅
**Login:** admin / admin123 ✅

## Quick Commands

```bash
# Check server is running
curl -s http://localhost:8000/api/v1/healthcheck/ | python3 -m json.tool

# Login to admin (in browser)
open http://localhost:8000/admin/

# View posts API
curl http://localhost:8000/api/v1/posts/

# Check CKEditor widget
python3 manage.py shell -c "from blog.admin import PostAdminForm; print(PostAdminForm().fields['content'].widget)"
```

**Now test it in your browser!** 🚀
