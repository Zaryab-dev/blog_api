from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from .models import Post
from .models_analytics import PostView, SearchQueryLog, ReferrerLog, DailyMetrics


class AnalyticsSummaryView(APIView):
    """
    Analytics summary endpoint for Next.js dashboard
    
    GET /api/v1/analytics/summary/?days=30
    
    Returns:
    - Top 10 trending posts
    - Top 10 referrers
    - Top 10 search queries with CTR
    - Daily metrics summary
    """
    
    def get(self, request):
        days = int(request.query_params.get('days', 30))
        
        # Check cache
        cache_key = f'analytics_summary:{days}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        since = timezone.now() - timedelta(days=days)
        
        # Trending posts
        trending = (
            PostView.objects
            .filter(viewed_at__gte=since)
            .values('post__slug', 'post__title')
            .annotate(views=Count('id'))
            .order_by('-views')[:10]
        )
        
        # Top referrers
        referrers = (
            ReferrerLog.objects
            .filter(last_visit__gte=since)
            .values('referrer_domain')
            .annotate(visits=Count('id'))
            .order_by('-visits')[:10]
        )
        
        # Top searches with CTR
        searches = (
            SearchQueryLog.objects
            .filter(created_at__gte=since)
            .values('query')
            .annotate(
                searches=Count('id'),
                clicks=Count('clicked_post', filter=Q(clicked_post__isnull=False))
            )
            .order_by('-searches')[:10]
        )
        
        # Daily metrics
        total_views = PostView.objects.filter(viewed_at__gte=since).count()
        unique_visitors = PostView.objects.filter(viewed_at__gte=since).values('ip_hash', 'user_agent_hash').distinct().count()
        total_searches = SearchQueryLog.objects.filter(created_at__gte=since).count()
        
        # Recent daily metrics
        recent_metrics = DailyMetrics.objects.filter(date__gte=since.date()).order_by('-date')[:7]
        
        summary = {
            'period_days': days,
            'generated_at': timezone.now().isoformat(),
            'overview': {
                'total_views': total_views,
                'unique_visitors': unique_visitors,
                'total_searches': total_searches,
                'avg_daily_views': round(total_views / days) if days > 0 else 0,
            },
            'trending_posts': [
                {
                    'slug': t['post__slug'],
                    'title': t['post__title'],
                    'views': t['views']
                }
                for t in trending
            ],
            'top_referrers': [
                {
                    'domain': r['referrer_domain'],
                    'visits': r['visits']
                }
                for r in referrers
            ],
            'top_searches': [
                {
                    'query': s['query'],
                    'searches': s['searches'],
                    'clicks': s['clicks'],
                    'ctr': round(s['clicks'] / s['searches'] * 100, 1) if s['searches'] > 0 else 0
                }
                for s in searches
            ],
            'daily_metrics': [
                {
                    'date': str(m.date),
                    'views': m.total_views,
                    'visitors': m.unique_visitors,
                    'searches': m.total_searches
                }
                for m in recent_metrics
            ]
        }
        
        # Cache for 1 hour
        cache.set(cache_key, summary, 3600)
        
        return Response(summary)
