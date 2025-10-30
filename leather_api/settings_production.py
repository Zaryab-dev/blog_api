"""
Production Security Settings
Import this after base settings.py
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SSL/HTTPS ENFORCEMENT
# ============================================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # For reverse proxy
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ============================================
# COOKIE & SESSION SECURITY
# ============================================
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_NAME = '__Secure-sessionid'  # Secure prefix
SESSION_COOKIE_AGE = 86400  # 24 hours

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_NAME = '__Secure-csrftoken'
CSRF_USE_SESSIONS = False  # Keep token in cookie for API

# ============================================
# SECURITY HEADERS
# ============================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")  # CKEditor requires inline styles
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)

# ============================================
# DATABASE SECURITY
# ============================================
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
        'ATOMIC_REQUESTS': True,  # Wrap each request in transaction
    }
}

# ============================================
# LOGGING WITH SECURITY EVENTS
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
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
        'security': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 10485760,
            'backupCount': 30,
            'formatter': 'json',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
        },
        'django.security': {
            'handlers': ['console', 'security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'security': {
            'handlers': ['console', 'security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'api.access': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}

# ============================================
# PASSWORD SECURITY
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'core.validators.PasswordComplexityValidator'},
]

# ============================================
# FILE UPLOAD SECURITY
# ============================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# ============================================
# ADMIN SECURITY
# ============================================
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')  # Customize admin URL

# ============================================
# DISABLE DEBUG FEATURES
# ============================================
DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = False
ALLOWED_HOSTS = []  # Must be set via environment
