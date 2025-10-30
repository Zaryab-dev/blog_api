"""SEO Analytics Middleware"""
from django.utils import timezone
from blog.models_seo import SEOAnalyticsLog
import re
import time
import logging

logger = logging.getLogger(__name__)


class SEOAnalyticsMiddleware:
    """Track API hits, crawlers, and schema requests"""
    
    CRAWLERS = {
        'googlebot': 'Googlebot',
        'bingbot': 'Bingbot',
        'slurp': 'Yahoo',
        'duckduckbot': 'DuckDuckGo',
        'baiduspider': 'Baidu',
        'yandexbot': 'Yandex',
        'facebookexternalhit': 'Facebook',
        'twitterbot': 'Twitter',
        'linkedinbot': 'LinkedIn',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Detect crawler
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_crawler = False
        crawler_name = ''
        
        for bot_pattern, bot_name in self.CRAWLERS.items():
            if bot_pattern in user_agent:
                is_crawler = True
                crawler_name = bot_name
                break
        
        response = self.get_response(request)
        
        # Log schema and API requests
        if '/api/v1/' in request.path or '/seo/schema/' in request.path:
            response_time = int((time.time() - start_time) * 1000)
            
            # Extract object info from path
            object_type = ''
            object_id = ''
            
            if '/posts/' in request.path:
                object_type = 'post'
                match = re.search(r'/posts/([^/]+)/', request.path)
                if match:
                    object_id = match.group(1)
            elif '/author/' in request.path:
                object_type = 'author'
                match = re.search(r'/author/([^/]+)/', request.path)
                if match:
                    object_id = match.group(1)
            elif '/schema/' in request.path:
                event_type = 'schema_request'
            else:
                event_type = 'api_hit'
            
            # Determine event type
            if '/schema/' in request.path:
                event_type = 'schema_request'
            elif is_crawler:
                event_type = 'crawler_visit'
            else:
                event_type = 'api_hit'
            
            # Log asynchronously
            try:
                SEOAnalyticsLog.objects.create(
                    event_type=event_type,
                    url=request.build_absolute_uri(),
                    object_type=object_type,
                    object_id=object_id,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    ip_address=self.get_client_ip(request),
                    referrer=request.META.get('HTTP_REFERER', '')[:500],
                    is_crawler=is_crawler,
                    crawler_name=crawler_name,
                    response_time_ms=response_time
                )
            except Exception as e:
                logger.error(f"Analytics log failed: {str(e)}")
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
