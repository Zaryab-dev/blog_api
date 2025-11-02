# Enhanced Admin Security Settings
import environ
import os

# Initialize environ for this file
env = environ.Env(
    ADMIN_IP_RESTRICTION_ENABLED=(bool, False),
    SECURITY_EMAIL_ALERTS=(bool, True),
)

# Django Axes - Login Attempt Protection
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1  # 1 hour lockout
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'admin/lockout.html'
AXES_ENABLE_ADMIN = True
AXES_VERBOSE = True
AXES_ONLY_ADMIN_SITE = True  # Only protect admin
AXES_LOCK_OUT_AT_FAILURE = True
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Two-Factor Authentication (Disabled for now)
TWO_FACTOR_PATCH_ADMIN = False
TWO_FACTOR_CALL_GATEWAY = None
TWO_FACTOR_SMS_GATEWAY = None
LOGIN_REDIRECT_URL = '/admin/'

# Admin IP Restriction
ALLOWED_ADMIN_IPS = env.list('ALLOWED_ADMIN_IPS', default=[])
ADMIN_IP_RESTRICTION_ENABLED = env.bool('ADMIN_IP_RESTRICTION_ENABLED', default=False)

# Session Security - Admin Only
ADMIN_SESSION_COOKIE_AGE = 900  # 15 minutes
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Email Alerts for Security Events
SECURITY_EMAIL_ALERTS = env.bool('SECURITY_EMAIL_ALERTS', default=True)
SECURITY_ALERT_EMAIL = env('SECURITY_ALERT_EMAIL', default=env('ADMIN_EMAIL', default='admin@example.com'))
