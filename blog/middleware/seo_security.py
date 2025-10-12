"""SEO Security Middleware"""
from django.http import HttpResponseForbidden, HttpResponse
from django.core.cache import cache
import logging

logger = logging.getLogger('security')


class SEOSecurityMiddleware:
    """Protect SEO endpoints from abuse and fake crawlers"""
    
    FAKE_BOTS = ['semrush', 'ahrefs', 'majestic', 'mj12bot', 'dotbot', 'blexbot']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(bot in user_agent for bot in self.FAKE_BOTS):
            logger.warning(f"Blocked fake bot: {user_agent}")
            return HttpResponseForbidden("Access Denied")
        
        if request.path.startswith('/api/v1/seo/'):
            ip = self.get_client_ip(request)
            cache_key = f"seo_rate_{ip}"
            count = cache.get(cache_key, 0)
            
            if count > 60:
                return HttpResponse("Rate limit exceeded", status=429)
            
            cache.set(cache_key, count + 1, 60)
        
        response = self.get_response(request)
        
        if '/sitemap' in request.path or '/rss' in request.path:
            response['X-Robots-Tag'] = 'noindex'
            response['Cache-Control'] = 'public, max-age=3600'
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
