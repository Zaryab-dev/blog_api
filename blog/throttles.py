from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.conf import settings


class CommentRateThrottle(AnonRateThrottle):
    """Throttle for comment creation"""
    rate = '5/minute'


class AdaptiveAnonThrottle(AnonRateThrottle):
    """Environment-based throttle for anonymous users"""
    
    def get_rate(self):
        if settings.DEBUG:
            return '1000/hour'
        return getattr(settings, 'ANON_THROTTLE_RATE', '100/hour')


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
