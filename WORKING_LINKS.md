# 🚀 Django Blog API - Working Links

## Server Status
✅ **Server Running on:** http://localhost:8000

## 📍 API Endpoints (v1)

### Core API
- **API Root:** http://localhost:8000/api/v1/
- **Posts:** http://localhost:8000/api/v1/posts/
- **Categories:** http://localhost:8000/api/v1/categories/
- **Tags:** http://localhost:8000/api/v1/tags/
- **Authors:** http://localhost:8000/api/v1/authors/
- **Comments:** http://localhost:8000/api/v1/comments/

### Search & Subscribe
- **Search:** http://localhost:8000/api/v1/search/
- **Subscribe:** http://localhost:8000/api/v1/subscribe/

### Analytics
- **Track View:** http://localhost:8000/api/v1/track-view/
- **Trending Posts:** http://localhost:8000/api/v1/trending/
- **Popular Searches:** http://localhost:8000/api/v1/popular-searches/
- **Analytics Summary:** http://localhost:8000/api/v1/analytics/summary/

### SEO
- **Sitemap:** http://localhost:8000/api/v1/sitemap.xml
- **RSS Feed:** http://localhost:8000/api/v1/rss.xml
- **Robots.txt:** http://localhost:8000/api/v1/robots.txt

### Phase 8 - CKEditor Upload
- **Upload Image:** http://localhost:8000/api/v1/upload-image/ (POST, Auth Required)

### Webhooks & Monitoring
- **Revalidate:** http://localhost:8000/api/v1/revalidate/
- **Health Check:** http://localhost:8000/api/v1/healthcheck/

### Documentation
- **OpenAPI Schema:** http://localhost:8000/api/v1/schema/
- **Swagger UI:** http://localhost:8000/api/v1/docs/
- **ReDoc:** http://localhost:8000/api/v1/redoc/

## 🔐 Admin Panel
- **Django Admin:** http://localhost:8000/admin/

## 📊 Test the API

### Get All Posts
```bash
curl http://localhost:8000/api/v1/posts/
```

### Get Single Post
```bash
curl http://localhost:8000/api/v1/posts/{slug}/
```

### Search Posts
```bash
curl "http://localhost:8000/api/v1/search/?q=leather"
```

### Health Check
```bash
curl http://localhost:8000/api/v1/healthcheck/
```

## 🎯 Phase 8 Features

### Upload Image (Requires Authentication)
```bash
curl -X POST http://localhost:8000/api/v1/upload-image/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "upload=@image.jpg"
```

## 📝 Next Steps

1. **Create Admin User:**
```bash
python3 manage.py createsuperuser
```

2. **Access Admin Panel:**
   - Go to: http://localhost:8000/admin/
   - Login with your credentials
   - Create posts with CKEditor

3. **Test API:**
   - Browse: http://localhost:8000/api/v1/docs/
   - Try endpoints in Swagger UI

## 🛑 Stop Server
```bash
kill $(cat /tmp/django_server.pid)
```
