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
    ALLOWED_HOSTS=(list, ['backend.zaryableather.com', 'django-blog-api-prod.eba-uiwnbpqr.us-east-1.elasticbeanstalk.com', 'localhost', '127.0.0.1']),
)

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Security - CRITICAL: No defaults for production
SECRET_KEY = env('SECRET_KEY')
if not SECRET_KEY or SECRET_KEY == 'django-insecure-change-in-production':
    raise ValueError(
        "SECRET_KEY environment variable is required and must be set to a secure value. "
        "Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Add App Runner domains if not in DEBUG mode
if not DEBUG:
    apprunner_domains = ['.awsapprunner.com', '.amazonaws.com']
    ALLOWED_HOSTS.extend(apprunner_domains)


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
    'corsheaders.middleware.CorsMiddleware',  # Must be at the top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.compression.CompressionMiddleware',
    'core.middleware.request_id.RequestIDMiddleware',
    'core.middleware.admin_ip_restriction.AdminIPRestrictionMiddleware',
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
# CORS settings - Production secure configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    "https://zaryableather.com",
    "https://www.zaryableather.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
])
CORS_ALLOW_ALL_ORIGINS = False  # Explicitly set to False for security

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

# Password validation - Enhanced Security
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'core.validators.PasswordComplexityValidator'},
    {'NAME': 'core.validators.PasswordStrengthValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

# Use CompressedStaticFilesStorage instead of ManifestStaticFilesStorage
# This avoids manifest errors while still getting compression benefits
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

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

# Additional CORS settings
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

# Ensure CORS works with CSRF
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://zaryableather.com',
    'https://www.zaryableather.com',
    'https://backend.zaryableather.com',
])

# Cache - Optimized Redis with connection pooling
REDIS_URL = env('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                    'socket_keepalive': True,
                    'socket_connect_timeout': 5,
                    'health_check_interval': 30,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'IGNORE_EXCEPTIONS': True,  # Fail gracefully
            },
            'KEY_PREFIX': 'blog',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Celery - Production-grade configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')

# SSL configuration for Upstash Redis (rediss://)
import ssl
if CELERY_BROKER_URL.startswith('rediss://'):
    CELERY_BROKER_USE_SSL = {
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    }
    CELERY_REDIS_BACKEND_USE_SSL = {
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,
        'ssl_certfile': None,
        'ssl_keyfile': None,
    }

# Serialization
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Task execution
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit
CELERY_TASK_ACKS_LATE = True  # Acknowledge after task completion
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # One task at a time for long-running tasks
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart worker after 1000 tasks

# Retry policy
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_AUTORETRY_FOR = (Exception,)
CELERY_TASK_RETRY_BACKOFF = True  # Exponential backoff
CELERY_TASK_RETRY_BACKOFF_MAX = 600  # Max 10 minutes
CELERY_TASK_RETRY_JITTER = True  # Add randomness to prevent thundering herd

# Result backend
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10

# Broker connection
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10

# Rate limiting
CELERY_TASK_DEFAULT_RATE_LIMIT = '100/m'  # 100 tasks per minute

# Monitoring
CELERY_SEND_TASK_SENT_EVENT = True
CELERY_TASK_SEND_SENT_EVENT = True

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

# Supabase Storage (REQUIRED - No defaults for security)
SUPABASE_URL = env('SUPABASE_URL')
SUPABASE_API_KEY = env('SUPABASE_API_KEY')
SUPABASE_BUCKET = env('SUPABASE_BUCKET')
SUPABASE_IMAGE_FOLDER = 'blog-images/'  # Default folder for blog images

# Validate required settings
from django.core.exceptions import ImproperlyConfigured

def validate_required_settings():
    """Validate that critical settings are configured"""
    required = {
        'SUPABASE_URL': SUPABASE_URL,
        'SUPABASE_API_KEY': SUPABASE_API_KEY,
        'SUPABASE_BUCKET': SUPABASE_BUCKET,
    }
    
    missing = [key for key, value in required.items() if not value]
    
    if missing:
        raise ImproperlyConfigured(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Please check your .env file."
        )

validate_required_settings()

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
    
    # Cookie security - only use Secure flag if HTTPS is enabled
    USE_HTTPS = env.bool('USE_HTTPS', default=True)
    
    SESSION_COOKIE_SECURE = USE_HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Changed from Strict for better compatibility
    SESSION_COOKIE_NAME = '__Secure-sessionid' if USE_HTTPS else 'sessionid'
    
    CSRF_COOKIE_SECURE = USE_HTTPS
    CSRF_COOKIE_HTTPONLY = False  # Must be False for CSRF to work
    CSRF_COOKIE_SAMESITE = 'Lax'  # Changed from Strict for better compatibility
    CSRF_COOKIE_NAME = '__Secure-csrftoken' if USE_HTTPS else 'csrftoken'
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
    
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Only enable HSTS if using HTTPS
    if USE_HTTPS:
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
    
    X_FRAME_OPTIONS = 'DENY'

# Session Security
SESSION_COOKIE_AGE = env.int('SESSION_COOKIE_AGE', default=3600)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

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


# Import security settings (disabled for now)
# from .settings_security import *

# Set LOGIN_URL
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

# Logging configuration removed - using comprehensive config above
