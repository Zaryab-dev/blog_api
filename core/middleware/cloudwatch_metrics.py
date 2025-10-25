"""CloudWatch metrics middleware"""
import time
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CloudWatchMetricsMiddleware:
    """Collect and send metrics to CloudWatch"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = (time.time() - start_time) * 1000
        
        # Store metrics in cache for aggregation
        metrics_key = f"metrics:{int(time.time() // 60)}"
        metrics = cache.get(metrics_key, {
            'request_count': 0,
            'total_duration': 0,
            'status_codes': {},
            'endpoints': {}
        })
        
        metrics['request_count'] += 1
        metrics['total_duration'] += duration
        metrics['status_codes'][response.status_code] = metrics['status_codes'].get(response.status_code, 0) + 1
        
        endpoint = f"{request.method} {request.path}"
        metrics['endpoints'][endpoint] = metrics['endpoints'].get(endpoint, 0) + 1
        
        cache.set(metrics_key, metrics, 120)
        
        # Add metrics to response headers
        response['X-Response-Time'] = f"{duration:.2f}ms"
        
        return response
