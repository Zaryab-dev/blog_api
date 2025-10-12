"""Redis-based IP rate limiting middleware"""
import hashlib
import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('security')


class IPRateLimitMiddleware:
    """IP-based rate limiting with Redis"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.window = 60  # 60 seconds
        self.max_requests = 100  # requests per window
    
    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)
        
        # Get client IP
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:200]
        
        # Create unique identifier
        identifier = hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()
        cache_key = f"ratelimit:{identifier}"
        
        # Get current count
        current = cache.get(cache_key, 0)
        
        if current >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return JsonResponse({
                'error': 'Rate limit exceeded. Try again later.'
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, current + 1, self.window)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(self.max_requests)
        response['X-RateLimit-Remaining'] = str(max(0, self.max_requests - current - 1))
        response['X-RateLimit-Reset'] = str(self.window)
        
        return response
    
    def get_client_ip(self, request):
        """Extract real client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
