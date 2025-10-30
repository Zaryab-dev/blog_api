# 🚀 Django Blog API - Production Ready

A production-ready Django REST API for a blog platform with advanced SEO, analytics, and AWS App Runner deployment support.

## ✨ Features

- 🔐 **JWT Authentication** - Secure token-based auth
- 📝 **Rich Text Editor** - CKEditor 5 with Supabase storage
- 🎯 **SEO Optimized** - Auto-generated meta tags, Open Graph, Twitter Cards, Schema.org
- 📊 **Analytics** - Built-in view tracking and trending posts
- 🖼️ **Image Management** - Supabase storage integration
- 🔍 **Advanced Search** - Full-text search with PostgreSQL
- 🎨 **Homepage Carousel** - Dynamic hero sections
- 📱 **API Documentation** - Swagger/ReDoc auto-generated docs
- 🔒 **Security** - Rate limiting, IP blocking, CORS, CSRF protection
- 🐳 **Docker Ready** - Multi-stage Dockerfile optimized for AWS App Runner
- ☁️ **AWS Deployment** - Ready for App Runner, ECS, or EC2

## 🏗️ Architecture

- **Backend:** Django 4.2+ with Django REST Framework
- **Database:** PostgreSQL (Supabase compatible)
- **Cache:** Redis (optional)
- **Storage:** Supabase Storage
- **Task Queue:** Celery (optional)
- **Server:** Gunicorn
- **Container:** Docker

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- PostgreSQL or Supabase account
- Supabase Storage bucket

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/Zaryab-dev/blog_api.git
cd blog_api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

Visit: `http://localhost:8000/admin/`

### Docker Development

```bash
# Build image
docker build -t blog-api .

# Run container
docker run -p 8080:8080 --env-file .env blog-api
```

## 📋 Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Django Core
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Supabase Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-anon-key
SUPABASE_BUCKET=your-bucket-name

# Optional: Redis
REDIS_URL=redis://localhost:6379/1

# Optional: Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## 🐳 AWS App Runner Deployment

### Prerequisites

1. AWS Account with CLI configured
2. ECR repository created
3. App Runner IAM role with ECR access

### Deployment Steps

1. **Build and push Docker image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t blog-api .

# Tag and push
docker tag blog-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/blog-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/blog-api:latest
```

2. **Create App Runner service**
   - Go to AWS Console → App Runner
   - Create service from ECR
   - Configure:
     - Port: **8080**
     - Health check: **/api/v1/healthcheck/**
     - Add environment variables
   - Deploy

See `AWS_APPRUNNER_DEPLOYMENT.md` for detailed instructions.

## 📚 API Documentation

Once running, visit:
- **Swagger UI:** `http://localhost:8000/api/v1/docs/`
- **ReDoc:** `http://localhost:8000/api/v1/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/v1/schema/`

### Key Endpoints

```
GET  /api/v1/posts/              # List posts
GET  /api/v1/posts/{slug}/       # Get post detail
GET  /api/v1/categories/         # List categories
GET  /api/v1/tags/               # List tags
GET  /api/v1/authors/            # List authors
POST /api/v1/posts/              # Create post (auth required)
GET  /api/v1/healthcheck/        # Health check
GET  /sitemap.xml                # Sitemap
GET  /rss.xml                    # RSS feed
```

## 🔧 Management Commands

```bash
# Populate SEO metadata for all posts
python manage.py populate_seo

# Create test data
python manage.py loaddata fixtures/sample_data.json

# Collect static files
python manage.py collectstatic --noinput
```

## 🎯 SEO Automation

The API includes automatic SEO metadata generation:

```python
# Automatically generates:
- SEO title and description
- Open Graph tags
- Twitter Card metadata
- Schema.org JSON-LD
- Canonical URLs
```

See `SEO_AUTOMATION_GUIDE.md` for details.

## 🔒 Security Features

- ✅ JWT authentication
- ✅ Rate limiting (per IP and user)
- ✅ IP blocking
- ✅ CORS configuration
- ✅ CSRF protection
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Secure headers
- ✅ Password validation

## 📊 Project Structure

```
blog_api/
├── blog/                   # Main blog app
│   ├── models.py          # Post, Category, Tag, etc.
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── urls_v1.py         # API routes
│   └── seo_automation.py  # SEO automation
├── core/                   # Core utilities
│   ├── authentication.py  # JWT auth
│   ├── middleware/        # Security middleware
│   └── validators.py      # Custom validators
├── leather_api/           # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URLs
│   └── wsgi.py            # WSGI config
├── Dockerfile             # Docker configuration
├── docker-entrypoint.sh   # Container startup
├── gunicorn.conf.py       # Gunicorn config
├── requirements.txt       # Python dependencies
└── manage.py              # Django CLI
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# With coverage
pytest --cov=blog --cov-report=html

# Test healthcheck
curl http://localhost:8000/api/v1/healthcheck/
```

## 📖 Documentation

- `AWS_APPRUNNER_DEPLOYMENT.md` - AWS deployment guide
- `SEO_AUTOMATION_GUIDE.md` - SEO features documentation
- `APPRUNNER_FIX_SUMMARY.md` - Troubleshooting guide
- `DEPLOYMENT_STATUS.md` - Current deployment status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**Zaryab**
- GitHub: [@Zaryab-dev](https://github.com/Zaryab-dev)

## 🙏 Acknowledgments

- Django REST Framework
- CKEditor 5
- Supabase
- AWS App Runner

---

**⭐ Star this repo if you find it helpful!**