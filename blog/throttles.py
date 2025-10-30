"""Enhanced throttling with security features"""
import logging
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, SimpleRateThrottle
from django.conf import settings
from core.security_utils import log_security_event

logger = logging.getLogger('security')


class CommentRateThrottle(AnonRateThrottle):
    """Throttle for comment creation"""
    rate = '5/minute'


class AdaptiveAnonThrottle(AnonRateThrottle):
    """Environment-based throttle for anonymous users"""
    
    def get_rate(self):
        if settings.DEBUG:
            return '1000/hour'
        return getattr(settings, 'ANON_THROTTLE_RATE', '100/hour')
    
    def throttle_failure(self):
        log_security_event(
            'rate_limit_exceeded',
            f'Anonymous user exceeded rate limit',
            severity='WARNING'
        )


class AdaptiveUserThrottle(UserRateThrottle):
    """Environment-based throttle for authenticated users"""
    
    def get_rate(self):
        if settings.DEBUG:
            return '10000/hour'
        return getattr(settings, 'USER_THROTTLE_RATE', '1000/hour')


class WriteOperationThrottle(AnonRateThrottle):
    """Throttle for all non-GET operations"""
    rate = '30/minute'
    
    def allow_request(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return super().allow_request(request, view)


class LoginRateThrottle(SimpleRateThrottle):
    """Strict throttle for login attempts"""
    scope = 'login'
    
    def get_cache_key(self, request, view):
        # Throttle by IP for login attempts
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }
    
    def get_rate(self):
        return getattr(settings, 'LOGIN_THROTTLE_RATE', '5/hour')


class RegisterRateThrottle(SimpleRateThrottle):
    """Strict throttle for registration"""
    scope = 'register'
    
    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }
    
    def get_rate(self):
        return getattr(settings, 'REGISTER_THROTTLE_RATE', '3/hour')
