"""
Simplified healthcheck for App Runner
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.db import connection
import time


@never_cache
@require_http_methods(["GET"])
def simple_healthcheck(request):
    """
    Minimal healthcheck for App Runner - only checks database
    Returns 200 OK if database is accessible
    """
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'django-blog-api'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)


@never_cache
@require_http_methods(["GET"])
def detailed_healthcheck(request):
    """
    Detailed healthcheck with all service checks
    """
    from django.utils import timezone
    from django.core.cache import cache
    
    health_status = 'healthy'
    checks = {}
    
    # Database check
    try:
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        latency = (time.time() - start) * 1000
        checks['database'] = {
            'status': 'ok',
            'latency_ms': round(latency, 2)
        }
    except Exception as e:
        checks['database'] = {'status': 'error', 'message': str(e)}
        health_status = 'unhealthy'
    
    # Redis check (non-critical)
    try:
        start = time.time()
        cache.set('healthcheck', 'ok', 10)
        result = cache.get('healthcheck')
        latency = (time.time() - start) * 1000
        
        if result == 'ok':
            checks['redis'] = {
                'status': 'ok',
                'latency_ms': round(latency, 2)
            }
        else:
            checks['redis'] = {'status': 'warning', 'message': 'cache not working'}
    except Exception as e:
        checks['redis'] = {'status': 'warning', 'message': str(e)}
    
    response_status = 200 if health_status == 'healthy' else 503
    
    return JsonResponse({
        'status': health_status,
        'checks': checks,
        'timestamp': timezone.now().isoformat()
    }, status=response_status)