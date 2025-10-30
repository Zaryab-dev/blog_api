"""
Homepage Carousel API views
"""
from rest_framework import generics
from .models import HomeCarousel
from .serializers import HomeCarouselSerializer


class HomeCarouselListView(generics.ListAPIView):
    """
    List active homepage carousel slides
    
    GET /api/v1/homepage/carousel/
    
    Returns all active carousel items ordered by position
    """
    serializer_class = HomeCarouselSerializer
    queryset = HomeCarousel.objects.filter(is_active=True, show_on_homepage=True).select_related('image')
    pagination_class = None  # No pagination for carousel
