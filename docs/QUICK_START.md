# Quick Start Guide

## Installation

```bash
# Clone repository
git clone https://github.com/your-org/leather_api.git
cd leather_api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Generate secrets
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
openssl rand -hex 32  # For HMAC secrets

# Run migrations
python manage.py migrate
python manage.py migrate django_celery_beat

# Create superuser
python manage.py createsuperuser

# Create logs directory
mkdir -p logs

# Collect static files
python manage.py collectstatic --noinput
```

## Development

```bash
# Start Django
python manage.py runserver

# Start Celery Worker
celery -A leather_api worker -l info

# Start Celery Beat
celery -A leather_api beat -l info

# Run tests
python manage.py test

# Run security checks
./scripts/security-checks.sh
```

## API Endpoints

### Core Endpoints
- `GET /api/posts/` - List posts
- `GET /api/posts/{slug}/` - Get post
- `GET /api/categories/` - List categories
- `GET /api/tags/` - List tags
- `GET /api/authors/` - List authors
- `GET /api/search/?q=query` - Search posts

### Analytics
- `POST /api/track-view/` - Track page view
- `GET /api/trending/` - Trending posts
- `GET /api/popular-searches/` - Popular searches

### SEO
- `GET /api/sitemap.xml` - Sitemap
- `GET /api/rss.xml` - RSS feed
- `GET /api/robots.txt` - Robots.txt

### Monitoring
- `GET /api/healthcheck/` - Health status
- `GET /api/schema/` - OpenAPI schema
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc

## Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://127.0.0.1:6379/1

# Optional
DEBUG=False
ALLOWED_HOSTS=api.example.com
SENTRY_DSN=https://your-dsn@sentry.io/project
CORS_ALLOWED_ORIGINS=https://example.com
```

## Common Tasks

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Generate OpenAPI schema
python manage.py spectacular --file schema.json

# Clear cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Test email
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

## Troubleshooting

### Database connection error
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
python manage.py dbshell
```

### Redis connection error
```bash
# Check Redis running
redis-cli ping

# Check REDIS_URL
echo $REDIS_URL
```

### Celery not running
```bash
# Check Celery workers
celery -A leather_api inspect ping

# Check scheduled tasks
celery -A leather_api inspect scheduled
```

### Security headers missing
```bash
# Check middleware order in settings.py
# SecurityHeadersMiddleware should be last
```

## Documentation

- **Architecture:** `docs/phase-1-architecture.md`
- **Analytics:** `docs/phase-5-analytics.md`
- **Security:** `docs/phase-5-security-monitoring.md`
- **Secret Rotation:** `docs/SECRET_ROTATION.md`
- **API Docs:** `http://localhost:8000/api/docs/`

## Support

- **Issues:** https://github.com/your-org/leather_api/issues
- **Email:** api@example.com
- **Docs:** https://api.example.com/api/docs/
