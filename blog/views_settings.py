from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .models import SiteSettings
from .serializers import SiteSettingsSerializer


@api_view(['GET'])
def site_settings(request):
    """Get site settings (store URL and social links)"""
    cache_key = 'site_settings'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    settings = SiteSettings.load()
    serializer = SiteSettingsSerializer(settings)
    
    cache.set(cache_key, serializer.data, 3600)  # Cache for 1 hour
    
    return Response(serializer.data)
