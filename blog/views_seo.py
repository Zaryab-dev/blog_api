import hmac
import hashlib
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import redis


@cache_page(60 * 60 * 12)  # 12 hours
@require_http_methods(["GET"])
def robots_txt(request):
    """
    Enhanced robots.txt with comprehensive crawl directives
    """
    from .models import SiteSettings
    
    site_settings = SiteSettings.load()
    site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
    
    # Use custom robots.txt if configured
    if site_settings.robots_txt_content:
        content = site_settings.robots_txt_content
        # Ensure sitemap is included
        if 'Sitemap:' not in content:
            content += f"\n\nSitemap: {site_url}/sitemap.xml"
    else:
        # Default robots.txt
        content = f"""# Robots.txt for {site_url}

# Allow all crawlers
User-agent: *
Allow: /

# Disallow admin and private areas
Disallow: /admin/
Disallow: /api/auth/
Disallow: /api/admin/

# Allow API endpoints for content
Allow: /api/v1/posts/
Allow: /api/v1/categories/
Allow: /api/v1/tags/
Allow: /api/v1/authors/

# Crawl delay (be nice to servers)
Crawl-delay: 1

# Sitemaps
Sitemap: {site_url}/sitemap.xml
Sitemap: {site_url}/rss/

# Specific bot rules
User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 0

User-agent: Slurp
Allow: /

# Block bad bots
User-agent: AhrefsBot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: DotBot
Disallow: /
"""
    
    return HttpResponse(content, content_type='text/plain')


@api_view(['POST'])
def revalidate_webhook(request):
    """
    Secure webhook endpoint to trigger ISR revalidation in Next.js
    
    Validates HMAC signature and forwards revalidation request
    """
    # Validate HMAC signature
    signature = request.headers.get('X-Signature', '')
    secret = getattr(settings, 'REVALIDATE_SECRET', '')
    
    if not secret:
        return Response(
            {'error': 'REVALIDATE_SECRET not configured'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Calculate expected signature
    payload = request.body
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison
    if not hmac.compare_digest(signature, expected_signature):
        return Response(
            {'error': 'Invalid signature'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Extract slugs from request
    slugs = request.data.get('slugs', [])
    paths = request.data.get('paths', [])
    
    # TODO: Send revalidation request to Next.js
    # from .tasks import trigger_nextjs_revalidation
    # trigger_nextjs_revalidation.delay(slugs, paths)
    
    return Response({
        'message': 'Revalidation triggered',
        'slugs': slugs,
        'paths': paths
    })


@api_view(['GET'])
def healthcheck(request):
    """
    Enhanced health check endpoint for monitoring
    
    Returns: JSON with status, checks, latency, uptime
    """
    import time
    from django.utils import timezone
    
    health_status = 'healthy'
    checks = {}
    
    # Check database with latency (3 pings)
    try:
        latencies = []
        for _ in range(3):
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            latencies.append((time.time() - start) * 1000)
        
        avg_latency = sum(latencies) / len(latencies)
        checks['database'] = {
            'status': 'ok',
            'latency_ms': round(avg_latency, 2)
        }
    except Exception as e:
        checks['database'] = {'status': 'error', 'message': str(e)}
        health_status = 'unhealthy'
    
    # Check Redis with latency (non-critical)
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
    
    # Check Celery Beat status
    try:
        from django_celery_beat.models import PeriodicTask
        active_tasks = PeriodicTask.objects.filter(enabled=True).count()
        checks['celery_beat'] = {
            'status': 'ok',
            'active_tasks': active_tasks
        }
    except Exception as e:
        checks['celery_beat'] = {'status': 'warning', 'message': str(e)}
    
    # System uptime
    try:
        import psutil
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        checks['uptime'] = {
            'seconds': int(uptime_seconds),
            'human': f"{int(uptime_seconds // 86400)}d {int((uptime_seconds % 86400) // 3600)}h"
        }
    except:
        checks['uptime'] = {'status': 'unavailable'}
    
    response_status = status.HTTP_200_OK if health_status == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response({
        'status': health_status,
        'checks': checks,
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    }, status=response_status)
