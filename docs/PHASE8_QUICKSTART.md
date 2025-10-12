# Phase 8 Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Django project running
- Supabase account (free tier works)
- Python 3.9+

### Step 1: Install Dependencies (1 min)

```bash
pip install django-ckeditor bleach httpx
```

### Step 2: Configure Settings (2 min)

**Add to `INSTALLED_APPS`:**
```python
INSTALLED_APPS = [
    # ...
    'ckeditor',
    'ckeditor_uploader',
]
```

**Add Supabase credentials:**
```python
SUPABASE_URL = 'https://soccrpfkqjqjaoaturjb.supabase.co'
SUPABASE_API_KEY = 'your-api-key'
SUPABASE_BUCKET = 'leather_api_storage'
```

**Add CKEditor config:**
```python
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', 'Blockquote'],
            ['Link', 'Image', 'Table'],
            ['Undo', 'Redo'],
        ],
        'height': 400,
    },
}
```

### Step 3: Run Migrations (1 min)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Test It! (1 min)

1. Start server: `python manage.py runserver`
2. Go to admin: `http://localhost:8000/admin/`
3. Create/edit a blog post
4. Upload an image in the editor
5. Save and check the API response

## 📝 Usage Examples

### Django Admin

The CKEditor will automatically appear in the Post admin form. Just start typing and use the toolbar to format content and upload images.

### API Response

```json
{
  "title": "My Blog Post",
  "content_html": "<p>Rich <strong>HTML</strong> content with <img src='https://supabase.co/...' /></p>",
  "reading_time": 5,
  "word_count": 1000
}
```

### Next.js Rendering

```tsx
<div
  className="prose max-w-none"
  dangerouslySetInnerHTML={{ __html: post.content_html }}
/>
```

## 🔒 Security

All HTML is automatically sanitized before saving. No XSS attacks possible!

## 📚 Full Documentation

See `docs/phase-8-ckeditor-supabase.md` for complete details.

## 🐛 Troubleshooting

**Images not uploading?**
- Check Supabase credentials
- Verify bucket exists and is public
- Check user is authenticated

**HTML not rendering?**
- Use `dangerouslySetInnerHTML` in React
- Check CSP headers allow Supabase domain

**Need help?**
- Check logs: `logs/django.log`
- Review tests: `blog/tests/test_upload.py`
- Read docs: `docs/phase-8-ckeditor-supabase.md`

## ✅ Done!

You now have a fully functional rich text editor with cloud storage! 🎉
