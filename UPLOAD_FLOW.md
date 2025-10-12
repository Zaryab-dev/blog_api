# CKEditor Supabase Upload Flow

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Django Admin                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Blog Post Editor                       │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │           CKEditor 5 Rich Text Editor             │   │  │
│  │  │                                                    │   │  │
│  │  │  [B] [I] [U] [🖼️ Image Upload] [Link] [...]      │   │  │
│  │  │                                                    │   │  │
│  │  │  User clicks image upload button ──────────────┐  │   │  │
│  │  └──────────────────────────────────────────────│──┘   │  │
│  └───────────────────────────────────────────────│──────────┘  │
└────────────────────────────────────────────────│────────────────┘
                                                  │
                                                  │ 1. POST /upload/ckeditor/
                                                  │    multipart/form-data
                                                  │    Field: upload (file)
                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django Backend                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  URL: /upload/ckeditor/                                   │  │
│  │  View: blog/views_ckeditor5_upload.py                     │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  1. Check Authentication (@staff_member_required)  │  │  │
│  │  │     ├─ Not admin? → 403 Forbidden                  │  │  │
│  │  │     └─ Admin? → Continue                           │  │  │
│  │  │                                                      │  │  │
│  │  │  2. Validate File Type                             │  │  │
│  │  │     ├─ Not image? → 400 Bad Request                │  │  │
│  │  │     └─ Valid? → Continue                           │  │  │
│  │  │                                                      │  │  │
│  │  │  3. Validate File Size                             │  │  │
│  │  │     ├─ > 5MB? → 400 Bad Request                    │  │  │
│  │  │     └─ Valid? → Continue                           │  │  │
│  │  │                                                      │  │  │
│  │  │  4. Call supabase_storage.upload_file()            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────│──────────────────┘  │
└────────────────────────────────────────│────────────────────────┘
                                          │
                                          │ 2. Upload file
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Supabase Storage Client                        │
│                   (core/storage.py)                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SupabaseStorage Class                                    │  │
│  │                                                            │  │
│  │  1. Generate unique filename (UUID + extension)          │  │
│  │     Example: 3f8a9b2c-4d5e-6f7g-8h9i-0j1k2l3m4n5o.jpg   │  │
│  │                                                            │  │
│  │  2. Create path: blog/images/{uuid}.jpg                  │  │
│  │                                                            │  │
│  │  3. Upload via Supabase client:                          │  │
│  │     client.storage.from_(bucket).upload(path, content)   │  │
│  │                                                            │  │
│  │  4. Generate public URL:                                 │  │
│  │     client.storage.from_(bucket).get_public_url(path)    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────│────────────────────────┘
                                          │
                                          │ 3. Store file
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase Cloud                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Storage Bucket: leather_api_storage                      │  │
│  │                                                            │  │
│  │  blog/                                                     │  │
│  │  └── images/                                              │  │
│  │      ├── 3f8a9b2c-4d5e-6f7g-8h9i-0j1k2l3m4n5o.jpg        │  │
│  │      ├── 7a1b2c3d-4e5f-6g7h-8i9j-0k1l2m3n4o5p.png        │  │
│  │      └── ...                                              │  │
│  │                                                            │  │
│  │  Public URL Generated:                                    │  │
│  │  https://xyz.supabase.co/storage/v1/object/public/       │  │
│  │  leather_api_storage/blog/images/{uuid}.jpg               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────│────────────────────────┘
                                          │
                                          │ 4. Return public URL
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django Response                             │
│                                                                   │
│  JSON Response:                                                  │
│  {                                                               │
│    "url": "https://xyz.supabase.co/storage/v1/object/public/    │
│            leather_api_storage/blog/images/uuid.jpg"             │
│  }                                                               │
└────────────────────────────────────────│────────────────────────┘
                                          │
                                          │ 5. Insert URL into editor
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CKEditor 5                               │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Content:                                                 │  │
│  │                                                            │  │
│  │  <p>This is my blog post...</p>                           │  │
│  │                                                            │  │
│  │  <img src="https://xyz.supabase.co/storage/v1/object/    │  │
│  │       public/leather_api_storage/blog/images/uuid.jpg"    │  │
│  │       alt="Uploaded image">                               │  │
│  │                                                            │  │
│  │  <p>More content...</p>                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Request/Response Flow

### 1. Upload Request

```http
POST /upload/ckeditor/ HTTP/1.1
Host: localhost:8000
Cookie: sessionid=abc123...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="upload"; filename="photo.jpg"
Content-Type: image/jpeg

[binary image data]
------WebKitFormBoundary--
```

### 2. Success Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "url": "https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog/images/3f8a9b2c-4d5e-6f7g-8h9i-0j1k2l3m4n5o.jpg"
}
```

### 3. Error Response (Invalid File Type)

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "message": "Invalid file type. Allowed: image/jpeg, image/png, image/gif, image/webp, image/jpg"
  }
}
```

### 4. Error Response (Not Authenticated)

```http
HTTP/1.1 403 Forbidden
Content-Type: text/html

[Django login redirect]
```

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Django Authentication                         │
│  ├─ @staff_member_required decorator                    │
│  └─ Only admin/staff users can access                   │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: File Type Validation                          │
│  ├─ Whitelist: JPEG, PNG, GIF, WebP                     │
│  └─ Reject all other file types                         │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: File Size Validation                          │
│  ├─ Maximum: 5MB                                         │
│  └─ Reject larger files                                  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Unique Filename Generation                    │
│  ├─ UUID-based filenames                                 │
│  └─ Prevents overwrites and conflicts                    │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 5: Supabase Authentication                       │
│  ├─ Service role key required                            │
│  └─ Bucket-level permissions                             │
└─────────────────────────────────────────────────────────┘
```

## File Storage Structure

```
Supabase Storage
└── leather_api_storage (bucket)
    └── blog/
        └── images/
            ├── 3f8a9b2c-4d5e-6f7g-8h9i-0j1k2l3m4n5o.jpg
            ├── 7a1b2c3d-4e5f-6g7h-8i9j-0k1l2m3n4o5p.png
            ├── 9b2c3d4e-5f6g-7h8i-9j0k-1l2m3n4o5p6q.webp
            └── ...

Public URLs:
https://soccrpfkqjqjaoaturjb.supabase.co/storage/v1/object/public/leather_api_storage/blog/images/{uuid}.{ext}
```

## Code Flow

```python
# 1. User uploads image in CKEditor
# CKEditor sends POST to /upload/ckeditor/

# 2. Django view receives request
@csrf_exempt
@staff_member_required
def ckeditor5_upload(request):
    file = request.FILES.get('upload')
    
    # 3. Validate file
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse({'error': {...}}, status=400)
    
    if file.size > MAX_FILE_SIZE:
        return JsonResponse({'error': {...}}, status=400)
    
    # 4. Upload to Supabase
    url = supabase_storage.upload_file(file, folder='blog/images/')
    
    # 5. Return URL to CKEditor
    return JsonResponse({'url': url})

# 6. CKEditor inserts image with URL
# <img src="https://...supabase.co/.../uuid.jpg">
```

## Configuration Chain

```
.env file
    ↓
settings.py
    ↓ SUPABASE_URL, SUPABASE_API_KEY, SUPABASE_BUCKET
core/storage.py (SupabaseStorage)
    ↓ supabase_storage singleton
blog/views_ckeditor5_upload.py
    ↓ ckeditor5_upload view
leather_api/urls.py
    ↓ /upload/ckeditor/ endpoint
CKEditor Config (settings.py)
    ↓ simpleUpload.uploadUrl
CKEditor in Django Admin
```

## Summary

1. **User Action:** Clicks image upload in CKEditor
2. **Request:** POST to `/upload/ckeditor/` with file
3. **Validation:** Auth, file type, file size
4. **Upload:** File sent to Supabase Storage
5. **Storage:** File saved with UUID filename
6. **Response:** Public URL returned to CKEditor
7. **Display:** Image inserted into editor with URL
8. **Save:** Post saved with Supabase image URLs in content

**Result:** All images stored in Supabase cloud, served via CDN, no local storage needed.
