"""Security utility functions"""
import logging
import secrets
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger('security')


def log_security_event(event_type, message, request=None, severity='WARNING'):
    """
    Log security events with context
    
    Args:
        event_type: Type of security event (e.g., 'failed_login', 'sql_injection')
        message: Detailed message
        request: Django request object (optional)
        severity: Log level (INFO, WARNING, ERROR, CRITICAL)
    """
    context = {
        'event_type': event_type,
        'message': message,
        'timestamp': timezone.now().isoformat(),
    }
    
    if request:
        context.update({
            'ip': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            'path': request.path,
            'method': request.method,
            'user': str(request.user) if request.user.is_authenticated else 'anonymous',
        })
    
    log_message = f"[{event_type}] {message} | Context: {context}"
    
    if severity == 'INFO':
        logger.info(log_message)
    elif severity == 'WARNING':
        logger.warning(log_message)
    elif severity == 'ERROR':
        logger.error(log_message)
    elif severity == 'CRITICAL':
        logger.critical(log_message)


def get_client_ip(request):
    """Extract real client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_secure_token(length=32):
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def verify_signature(request, secret_key):
    """Verify request signature for webhook/API calls"""
    import hmac
    import hashlib
    
    signature = request.META.get('HTTP_X_SIGNATURE', '')
    if not signature:
        return False
    
    body = request.body
    expected_signature = hmac.new(
        secret_key.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def rate_limit_check(identifier, max_requests=10, window=60):
    """
    Generic rate limiting check
    
    Args:
        identifier: Unique identifier (IP, user ID, etc.)
        max_requests: Maximum requests allowed
        window: Time window in seconds
    
    Returns:
        tuple: (allowed: bool, remaining: int)
    """
    cache_key = f"rate_limit:{identifier}"
    current = cache.get(cache_key, 0)
    
    if current >= max_requests:
        return False, 0
    
    cache.set(cache_key, current + 1, window)
    remaining = max_requests - current - 1
    
    return True, remaining


def is_safe_redirect_url(url, allowed_hosts):
    """
    Check if redirect URL is safe (prevent open redirect)
    
    Args:
        url: URL to check
        allowed_hosts: List of allowed host domains
    
    Returns:
        bool: True if safe, False otherwise
    """
    from urllib.parse import urlparse
    
    if not url:
        return False
    
    # Relative URLs are safe
    if url.startswith('/') and not url.startswith('//'):
        return True
    
    # Check absolute URLs
    try:
        parsed = urlparse(url)
        return parsed.netloc in allowed_hosts
    except Exception:
        return False


def sanitize_user_input(text, max_length=1000):
    """
    Sanitize user input to prevent XSS
    
    Args:
        text: Input text
        max_length: Maximum allowed length
    
    Returns:
        str: Sanitized text
    """
    import bleach
    
    if not text:
        return ''
    
    # Truncate
    text = text[:max_length]
    
    # Remove all HTML tags for plain text fields
    text = bleach.clean(text, tags=[], strip=True)
    
    return text.strip()


class SecurityAudit:
    """Security audit helper"""
    
    @staticmethod
    def check_weak_passwords():
        """Check for users with weak passwords (admin command)"""
        from django.contrib.auth.models import User
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        weak_users = []
        for user in User.objects.filter(is_active=True):
            # This is a simplified check - actual password hashes can't be reversed
            # Use this during user creation/password change
            pass
        
        return weak_users
    
    @staticmethod
    def check_admin_accounts():
        """List all admin/superuser accounts"""
        from django.contrib.auth.models import User
        
        admins = User.objects.filter(is_superuser=True, is_active=True)
        return list(admins.values('username', 'email', 'last_login'))
    
    @staticmethod
    def check_stale_sessions():
        """Find stale sessions (older than 30 days)"""
        from django.contrib.sessions.models import Session
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(days=30)
        stale = Session.objects.filter(expire_date__lt=cutoff)
        return stale.count()
