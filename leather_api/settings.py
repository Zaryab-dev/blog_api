"""
Django settings for leather_api project.
"""

from pathlib import Path
import os
import environ
import logging

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Security
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-in-production')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = ['52.23.171.87', 'zaryableather.vercel.app', 'zaryableather.vercel.app', 'localhost', '127.0.0.1']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third-party
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    'django_ckeditor_5',
    
    # Local
    'core',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'core.middleware.ip_blocking.IPBlockingMiddleware',
    'core.middleware.rate_limit.IPRateLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.request_validation.RequestValidationMiddleware',
    'core.middleware.security_headers.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'leather_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]
# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # local frontend
    "https://your-frontend-domain.com",  # replace with actual domain when deployed
]
CORS_ALLOW_ALL_ORIGINS = True

WSGI_APPLICATION = 'leather_api.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# PostgreSQL connection pooling for better performance
if 'postgresql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000',  # 30 seconds
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'core.validators.PasswordComplexityValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = env('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'blog.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'blog.throttles.AdaptiveAnonThrottle',
        'blog.throttles.AdaptiveUserThrottle',
        'blog.throttles.WriteOperationThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('ANON_THROTTLE_RATE', default='100/hour'),
        'user': env('USER_THROTTLE_RATE', default='1000/hour'),
        'login': env('LOGIN_THROTTLE_RATE', default='5/hour'),
        'register': env('REGISTER_THROTTLE_RATE', default='3/hour'),
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# DRF Spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'Zaryab Leather Blog API',
    'DESCRIPTION': 'Production-ready Django REST API for Next.js blog with SEO, analytics, and caching',
    'VERSION': '1.0.0',
    'CONTACT': {
        'name': 'API Support',
        'email': env('CONTACT_EMAIL', default='api@example.com'),
    },
    'LICENSE': {
        'name': 'MIT',
    },
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'posts', 'description': 'Blog post operations'},
        {'name': 'categories', 'description': 'Category operations'},
        {'name': 'tags', 'description': 'Tag operations'},
        {'name': 'authors', 'description': 'Author operations'},
        {'name': 'analytics', 'description': 'Analytics and tracking'},
        {'name': 'seo', 'description': 'SEO tools (sitemap, RSS, robots)'},
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-signature',
]
CORS_EXPOSE_HEADERS = ['content-type', 'etag', 'last-modified', 'cache-control']
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Cache
REDIS_URL = env('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Celery retry policy
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute
CELERY_TASK_MAX_RETRIES = 3

# Sentry
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=env.float('SENTRY_TRACES_SAMPLE_RATE', default=0.1),
        send_default_pii=False,
        environment=env('ENVIRONMENT', default='production'),
    )

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 30,
            'formatter': 'json',
        },
        'celery': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'celery.log'),
            'maxBytes': 10485760,
            'backupCount': 30,
            'formatter': 'json',
        },
        'security': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 10485760,
            'backupCount': 30,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
        },
        'celery': {
            'handlers': ['console', 'celery'],
            'level': 'INFO',
        },
        'security': {
            'handlers': ['console', 'security'],
            'level': 'WARNING',
        },
        'api.access': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

# Email
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@example.com')
ADMIN_EMAIL = env('ADMIN_EMAIL', default='admin@example.com')

# Site settings
SITE_URL = env('SITE_URL', default='http://localhost:8000')
SITE_NAME = env('SITE_NAME', default='Zaryab Leather Blog')
NEXTJS_URL = env('NEXTJS_URL', default='http://localhost:3000')
TWITTER_SITE = env('TWITTER_SITE', default='@zaryableather')

# SEO Settings
AUTO_PING_SEARCH_ENGINES = env.bool('AUTO_PING_SEARCH_ENGINES', default=True)
SEO_PING_TOKEN = env('SEO_PING_TOKEN', default='')
INDEXNOW_KEY = env('INDEXNOW_KEY', default='')
GOOGLE_SITE_VERIFICATION = env('GOOGLE_SITE_VERIFICATION', default='')

# CDN settings
CDN_PROVIDER = env('CDN_PROVIDER', default='')  # 'cloudflare' or 'bunnycdn'
CLOUDFLARE_ZONE_ID = env('CLOUDFLARE_ZONE_ID', default='')
CLOUDFLARE_API_TOKEN = env('CLOUDFLARE_API_TOKEN', default='')
BUNNYCDN_API_KEY = env('BUNNYCDN_API_KEY', default='')
BUNNYCDN_PULL_ZONE_ID = env('BUNNYCDN_PULL_ZONE_ID', default='')

# Secrets
REVALIDATE_SECRET = env('REVALIDATE_SECRET', default='')
ANALYTICS_SECRET = env('ANALYTICS_SECRET', default='')

# Add requests to requirements if not already present
try:
    import requests
except ImportError:
    pass

# Supabase Storage
SUPABASE_URL = env('SUPABASE_URL', default='https://soccrpfkqjqjaoaturjb.supabase.co')
SUPABASE_API_KEY = env('SUPABASE_API_KEY', default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvY2NycGZrcWpxamFvYXR1cmpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAwMTMxODksImV4cCI6MjA3NTU4OTE4OX0.u7HCVr6Na0wSuapw_fb3tCu38B23AIhnQgjP8f1F5e0')
SUPABASE_BUCKET = env('SUPABASE_BUCKET', default='leather_api_storage')
SUPABASE_IMAGE_FOLDER = 'blog-images/'  # Default folder for blog images

# CKEditor 5 Configuration
customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'uploadImage', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        },
        'simpleUpload': {
            'uploadUrl': '/upload/ckeditor/',
            'withCredentials': True,
            'headers': {
                'X-CSRF-TOKEN': 'CSRF-Token',
            }
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

# CKEditor 5 Upload - Use custom Supabase upload
CKEDITOR_5_UPLOAD_FILE_VIEW_NAME = 'ck5_upload'

# HTML Sanitization (Bleach)
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'img',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span', 'figure', 'figcaption',
]
ALLOWED_HTML_ATTRS = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    'table': ['border', 'cellpadding', 'cellspacing'],
}

# Throttle rates
ANON_THROTTLE_RATE = env('ANON_THROTTLE_RATE', default='100/hour')
USER_THROTTLE_RATE = env('USER_THROTTLE_RATE', default='1000/hour')

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

INSTALLED_APPS += ['rest_framework_simplejwt.token_blacklist']

# Security settings
SECURE_PROXY_SSL_HEADER_ENABLED = env.bool('SECURE_PROXY_SSL_HEADER_ENABLED', default=False)

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    if SECURE_PROXY_SSL_HEADER_ENABLED:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_NAME = '__Secure-sessionid'
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_NAME = '__Secure-csrftoken'
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'

# Account Security
MAX_LOGIN_ATTEMPTS = env.int('MAX_LOGIN_ATTEMPTS', default=5)
ACCOUNT_LOCKOUT_DURATION = env.int('ACCOUNT_LOCKOUT_DURATION', default=900)
PASSWORD_MIN_LENGTH = env.int('PASSWORD_MIN_LENGTH', default=12)

# File Upload Security
MAX_UPLOAD_SIZE = env.int('MAX_UPLOAD_SIZE', default=5242880)
ALLOWED_IMAGE_EXTENSIONS = env.list('ALLOWED_IMAGE_EXTENSIONS', default=['jpg', 'jpeg', 'png', 'webp', 'gif'])

# IP Blocking
BLOCKED_IPS = env('BLOCKED_IPS', default='')
BLOCKED_USER_AGENTS = env('BLOCKED_USER_AGENTS', default='sqlmap,nmap,nikto,masscan')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',   # show only WARNING and ERROR
    },
    'loggers': {
        'django.utils.autoreload': {
            'handlers': ['console'],
            'level': 'WARNING',   # suppress autoreload debug logs
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',  # keeps startup and request logs visible
            'propagate': False,
        },
    },
}
