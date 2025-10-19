"""
Advanced Security Implementation for Production
Enterprise-grade security measures
"""

import hashlib
import hmac
import secrets
import re
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('security')


class AdvancedRateLimiter:
    """Advanced rate limiting with adaptive throttling"""
    
    @staticmethod
    def check_rate_limit(identifier, limit=100, window=3600):
        """
        Check if request exceeds rate limit
        Returns: (allowed: bool, remaining: int, reset_time: int)
        """
        cache_key = f"rate_limit:{identifier}"
        current = cache.get(cache_key, 0)
        
        if current >= limit:
            ttl = cache.ttl(cache_key)
            return False, 0, ttl
        
        cache.set(cache_key, current + 1, window)
        return True, limit - current - 1, window
    
    @staticmethod
    def adaptive_throttle(identifier, suspicious_score=0):
        """Adaptive throttling based on behavior"""
        base_limit = 100
        
        # Reduce limit for suspicious behavior
        if suspicious_score > 50:
            base_limit = 20
        elif suspicious_score > 30:
            base_limit = 50
        
        return AdvancedRateLimiter.check_rate_limit(identifier, base_limit)


class SQLInjectionProtector:
    """Advanced SQL injection protection"""
    
    SUSPICIOUS_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b)",
        r"(\bINSERT\b.*\bINTO\b.*\bVALUES\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(;.*\bEXEC\b)",
        r"(\bxp_cmdshell\b)"
    ]
    
    @classmethod
    def detect_sql_injection(cls, input_string):
        """Detect potential SQL injection attempts"""
        if not input_string:
            return False
        
        input_upper = input_string.upper()
        
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, input_upper, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected: {input_string[:100]}")
                return True
        
        return False
    
    @classmethod
    def sanitize_input(cls, input_string):
        """Sanitize input to prevent SQL injection"""
        if cls.detect_sql_injection(input_string):
            raise ValueError("Potentially malicious input detected")
        return input_string


class XSSProtector:
    """Advanced XSS protection"""
    
    DANGEROUS_TAGS = ['script', 'iframe', 'object', 'embed', 'applet']
    DANGEROUS_ATTRS = ['onerror', 'onload', 'onclick', 'onmouseover']
    
    @classmethod
    def detect_xss(cls, html_content):
        """Detect potential XSS attacks"""
        if not html_content:
            return False
        
        content_lower = html_content.lower()
        
        # Check for dangerous tags
        for tag in cls.DANGEROUS_TAGS:
            if f'<{tag}' in content_lower:
                logger.warning(f"XSS attempt detected: {tag} tag")
                return True
        
        # Check for dangerous attributes
        for attr in cls.DANGEROUS_ATTRS:
            if attr in content_lower:
                logger.warning(f"XSS attempt detected: {attr} attribute")
                return True
        
        # Check for javascript: protocol
        if 'javascript:' in content_lower:
            logger.warning("XSS attempt detected: javascript: protocol")
            return True
        
        return False


class CSRFProtector:
    """Enhanced CSRF protection"""
    
    @staticmethod
    def generate_token():
        """Generate cryptographically secure CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(token, session_token):
        """Validate CSRF token with constant-time comparison"""
        if not token or not session_token:
            return False
        return hmac.compare_digest(token, session_token)


class ContentSecurityPolicy:
    """Content Security Policy generator"""
    
    @staticmethod
    def generate_csp_header(strict=True):
        """Generate CSP header for maximum security"""
        if strict:
            policy = {
                'default-src': ["'self'"],
                'script-src': ["'self'", "'unsafe-inline'", "https://www.googletagmanager.com", "https://www.google-analytics.com"],
                'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
                'img-src': ["'self'", "https:", "data:", "blob:"],
                'font-src': ["'self'", "https://fonts.gstatic.com"],
                'connect-src': ["'self'", "https://www.google-analytics.com"],
                'frame-ancestors': ["'none'"],
                'base-uri': ["'self'"],
                'form-action': ["'self'"],
                'upgrade-insecure-requests': []
            }
        else:
            policy = {
                'default-src': ["'self'"],
                'script-src': ["'self'", "'unsafe-inline'"],
                'style-src': ["'self'", "'unsafe-inline'"],
                'img-src': ["'self'", "https:", "data:"],
                'frame-ancestors': ["'self'"]
            }
        
        csp_string = '; '.join([
            f"{key} {' '.join(values)}" if values else key
            for key, values in policy.items()
        ])
        
        return csp_string


class SecurityHeadersGenerator:
    """Generate comprehensive security headers"""
    
    @staticmethod
    def get_security_headers():
        """Get all security headers for maximum protection"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=()',
            'Content-Security-Policy': ContentSecurityPolicy.generate_csp_header(),
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Cross-Origin-Embedder-Policy': 'require-corp',
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Resource-Policy': 'same-origin'
        }


class BruteForceProtector:
    """Protect against brute force attacks"""
    
    @staticmethod
    def check_login_attempts(identifier, max_attempts=5, lockout_duration=900):
        """
        Check and track login attempts
        Returns: (allowed: bool, attempts_remaining: int, lockout_seconds: int)
        """
        cache_key = f"login_attempts:{identifier}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            ttl = cache.ttl(cache_key)
            logger.warning(f"Account locked due to brute force: {identifier}")
            return False, 0, ttl
        
        return True, max_attempts - attempts, 0
    
    @staticmethod
    def record_failed_attempt(identifier, lockout_duration=900):
        """Record a failed login attempt"""
        cache_key = f"login_attempts:{identifier}"
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, lockout_duration)
    
    @staticmethod
    def reset_attempts(identifier):
        """Reset login attempts after successful login"""
        cache_key = f"login_attempts:{identifier}"
        cache.delete(cache_key)


class IPReputationChecker:
    """Check IP reputation and block malicious IPs"""
    
    BLOCKED_IPS_CACHE_KEY = "blocked_ips_set"
    
    @staticmethod
    def is_ip_blocked(ip_address):
        """Check if IP is in blocklist"""
        blocked_ips = cache.get(IPReputationChecker.BLOCKED_IPS_CACHE_KEY, set())
        return ip_address in blocked_ips
    
    @staticmethod
    def block_ip(ip_address, duration=86400):
        """Add IP to blocklist"""
        blocked_ips = cache.get(IPReputationChecker.BLOCKED_IPS_CACHE_KEY, set())
        blocked_ips.add(ip_address)
        cache.set(IPReputationChecker.BLOCKED_IPS_CACHE_KEY, blocked_ips, duration)
        logger.warning(f"IP blocked: {ip_address}")
    
    @staticmethod
    def calculate_threat_score(request):
        """Calculate threat score based on request characteristics"""
        score = 0
        
        # Check user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        if any(agent in user_agent for agent in suspicious_agents):
            score += 20
        
        # Check for missing headers
        if not request.META.get('HTTP_ACCEPT'):
            score += 15
        if not request.META.get('HTTP_ACCEPT_LANGUAGE'):
            score += 10
        
        # Check request method
        if request.method in ['PUT', 'DELETE', 'PATCH']:
            score += 5
        
        # Check for suspicious query parameters
        query_string = request.META.get('QUERY_STRING', '')
        if SQLInjectionProtector.detect_sql_injection(query_string):
            score += 50
        
        return score


class DataEncryptionHelper:
    """Helper for encrypting sensitive data"""
    
    @staticmethod
    def hash_password(password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        try:
            salt, pwd_hash = hashed.split('$')
            return DataEncryptionHelper.hash_password(password, salt) == hashed
        except:
            return False
    
    @staticmethod
    def generate_api_key():
        """Generate secure API key"""
        return secrets.token_urlsafe(32)


class AuditLogger:
    """Security audit logging"""
    
    @staticmethod
    def log_security_event(event_type, details, severity='INFO'):
        """Log security events for audit trail"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'severity': severity
        }
        
        if severity == 'CRITICAL':
            logger.critical(f"Security Event: {log_entry}")
        elif severity == 'WARNING':
            logger.warning(f"Security Event: {log_entry}")
        else:
            logger.info(f"Security Event: {log_entry}")
        
        # Store in cache for recent events
        cache_key = "security_events"
        events = cache.get(cache_key, [])
        events.append(log_entry)
        cache.set(cache_key, events[-100:], 3600)  # Keep last 100 events
    
    @staticmethod
    def get_recent_security_events(limit=50):
        """Get recent security events"""
        events = cache.get("security_events", [])
        return events[-limit:]


def apply_security_middleware(request):
    """Apply all security checks to incoming request"""
    ip_address = request.META.get('REMOTE_ADDR')
    
    # Check if IP is blocked
    if IPReputationChecker.is_ip_blocked(ip_address):
        AuditLogger.log_security_event('BLOCKED_IP_ACCESS', {'ip': ip_address}, 'WARNING')
        return False, "IP blocked"
    
    # Calculate threat score
    threat_score = IPReputationChecker.calculate_threat_score(request)
    if threat_score > 70:
        IPReputationChecker.block_ip(ip_address)
        AuditLogger.log_security_event('HIGH_THREAT_DETECTED', {'ip': ip_address, 'score': threat_score}, 'CRITICAL')
        return False, "Suspicious activity detected"
    
    # Check rate limit
    allowed, remaining, reset = AdvancedRateLimiter.adaptive_throttle(ip_address, threat_score)
    if not allowed:
        AuditLogger.log_security_event('RATE_LIMIT_EXCEEDED', {'ip': ip_address}, 'WARNING')
        return False, "Rate limit exceeded"
    
    return True, "OK"
