from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@never_cache
@require_http_methods(["GET", "HEAD"])
def simple_healthcheck(request):
    """Ultra-simple health check for App Runner - responds immediately without any I/O"""
    return JsonResponse({"status": "healthy", "service": "django-blog-api"}, status=200)
