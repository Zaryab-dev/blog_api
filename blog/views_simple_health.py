from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache

@never_cache
@require_http_methods(["GET"])
def simple_healthcheck(request):
    """Ultra-simple health check for App Runner"""
    return JsonResponse({"status": "healthy"})
