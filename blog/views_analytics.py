from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Q, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import timedelta
import hmac
import hashlib
from django.conf import settings

from .models import Post
from .models_analytics import PostView, SearchQueryLog, ReferrerLog
from .serializers import PostListSerializer
from .pagination import StandardPagination


@api_view(['POST'])
def track_view(request):
    """
    Track post view (lightweight, async-ready)
    
    POST /api/track-view/
    Body: {
        "slug": "post-slug",
        "referrer": "https://example.com" (optional)
    }
    """
    # Verify HMAC signature
    signature = request.headers.get('X-Signature', '')
    secret = getattr(settings, 'ANALYTICS_SECRET', '')
    
    if secret:
        payload = request.body.decode('utf-8')
        expected_sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_403_FORBIDDEN)
    
    slug = request.data.get('slug')
    if not slug:
        return Response({'error': 'slug required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check Redis counter first (lightweight)
    cache_key = f"view:{slug}"
    cache.incr(cache_key, 1)
    cache.expire(cache_key, 3600)  # 1 hour TTL
    
    # Get post
    try:
        post = Post.published.get(slug=slug)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Hash identifiers for privacy
    ip = request.META.get('REMOTE_ADDR', '')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip_hash = PostView.hash_identifier(ip)
    ua_hash = PostView.hash_identifier(user_agent)
    
    # Check if already viewed (deduplication within 1 hour)
    dedup_key = f"viewed:{ip_hash}:{ua_hash}:{slug}"
    if cache.get(dedup_key):
        return Response({'status': 'already_counted'}, status=status.HTTP_200_OK)
    
    # Record view
    PostView.objects.create(
        post=post,
        ip_hash=ip_hash,
        user_agent_hash=ua_hash,
        referrer=request.data.get('referrer', '')
    )
    
    # Set deduplication flag
    cache.set(dedup_key, 1, 3600)
    
    # Track referrer if present
    referrer = request.data.get('referrer', '')
    if referrer and referrer.startswith('http'):
        from urllib.parse import urlparse
        domain = urlparse(referrer).netloc
        if domain:
            ReferrerLog.objects.update_or_create(
                post=post,
                referrer_url=referrer,
                defaults={'referrer_domain': domain, 'visit_count': F('visit_count') + 1}
            )
    
    return Response({'status': 'tracked'}, status=status.HTTP_201_CREATED)


class TrendingPostsView(generics.ListAPIView):
    """
    Get trending posts based on trending_score
    
    GET /api/v1/trending/?limit=5
    """
    serializer_class = PostListSerializer
    pagination_class = None  # No pagination for trending
    
    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 5))
        
        # Get top trending posts by score
        return (
            Post.published
            .filter(trending_score__gt=0)
            .select_related('author', 'featured_image')
            .prefetch_related('categories', 'tags')
            .order_by('-trending_score')[:limit]
        )
    
    @method_decorator(cache_page(1800))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=1800'
        return response


class PopularSearchesView(generics.ListAPIView):
    """
    Get top 20 search queries for SEO dashboard
    
    GET /api/popular-searches/?days=30
    """
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        
        # Check cache
        cache_key = f"popular_searches:{days}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        # Aggregate search queries
        since = timezone.now() - timedelta(days=days)
        popular = (
            SearchQueryLog.objects
            .filter(created_at__gte=since)
            .values('query')
            .annotate(
                search_count=Count('id'),
                click_count=Count('clicked_post', filter=Q(clicked_post__isnull=False))
            )
            .order_by('-search_count')[:20]
        )
        
        results = [
            {
                'query': item['query'],
                'searches': item['search_count'],
                'clicks': item['click_count'],
                'ctr': round(item['click_count'] / item['search_count'] * 100, 1) if item['search_count'] > 0 else 0
            }
            for item in popular
        ]
        
        # Cache for 1 hour
        cache.set(cache_key, results, 3600)
        
        return Response(results)
