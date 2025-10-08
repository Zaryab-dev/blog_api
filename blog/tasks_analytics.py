from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Q
from django.core.cache import cache
from datetime import timedelta
import json


@shared_task
def aggregate_daily_metrics():
    """
    Aggregate daily analytics metrics and prune old logs
    
    Runs daily at 1 AM via Celery Beat
    """
    from .models_analytics import PostView, SearchQueryLog, ReferrerLog, DailyMetrics
    from .models import Post
    
    yesterday = (timezone.now() - timedelta(days=1)).date()
    
    # Aggregate views
    views = PostView.objects.filter(viewed_at__date=yesterday)
    total_views = views.count()
    unique_visitors = views.values('ip_hash', 'user_agent_hash').distinct().count()
    
    # Top posts
    top_posts = (
        views.values('post__slug', 'post__title')
        .annotate(view_count=Count('id'))
        .order_by('-view_count')[:10]
    )
    top_posts_data = [
        {'slug': p['post__slug'], 'title': p['post__title'], 'views': p['view_count']}
        for p in top_posts
    ]
    
    # Aggregate searches
    searches = SearchQueryLog.objects.filter(created_at__date=yesterday)
    total_searches = searches.count()
    
    top_searches = (
        searches.values('query')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    top_searches_data = [
        {'query': s['query'], 'count': s['count']}
        for s in top_searches
    ]
    
    # Top referrers
    referrers = ReferrerLog.objects.filter(last_visit__date=yesterday)
    top_referrers = (
        referrers.values('referrer_domain')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    top_referrers_data = [
        {'domain': r['referrer_domain'], 'count': r['count']}
        for r in top_referrers
    ]
    
    # Save metrics
    DailyMetrics.objects.update_or_create(
        date=yesterday,
        defaults={
            'total_views': total_views,
            'unique_visitors': unique_visitors,
            'total_searches': total_searches,
            'top_posts': top_posts_data,
            'top_searches': top_searches_data,
            'top_referrers': top_referrers_data,
        }
    )
    
    # Prune old logs (keep 90 days)
    cutoff = timezone.now() - timedelta(days=90)
    deleted_views = PostView.objects.filter(viewed_at__lt=cutoff).delete()
    deleted_searches = SearchQueryLog.objects.filter(created_at__lt=cutoff).delete()
    
    # Invalidate caches
    cache.delete_pattern('trending:*')
    cache.delete_pattern('popular_searches:*')
    
    return {
        'date': str(yesterday),
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'total_searches': total_searches,
        'deleted_views': deleted_views[0],
        'deleted_searches': deleted_searches[0],
    }


@shared_task
def export_trending_keywords():
    """
    Export trending keywords as JSON for Next.js ISR
    
    Generates /api/trending-keywords.json for static generation
    """
    from .models_analytics import SearchQueryLog
    from django.conf import settings
    import os
    
    # Get top 50 keywords from last 30 days
    since = timezone.now() - timedelta(days=30)
    keywords = (
        SearchQueryLog.objects
        .filter(created_at__gte=since)
        .values('query')
        .annotate(
            search_count=Count('id'),
            click_count=Count('clicked_post', filter=Q(clicked_post__isnull=False))
        )
        .order_by('-search_count')[:50]
    )
    
    data = {
        'generated_at': timezone.now().isoformat(),
        'period_days': 30,
        'keywords': [
            {
                'query': k['query'],
                'searches': k['search_count'],
                'clicks': k['click_count'],
                'ctr': round(k['click_count'] / k['search_count'] * 100, 1) if k['search_count'] > 0 else 0
            }
            for k in keywords
        ]
    }
    
    # Save to static directory
    static_dir = getattr(settings, 'STATIC_ROOT', '/tmp')
    output_path = os.path.join(static_dir, 'trending-keywords.json')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Cache for API endpoint
    cache.set('trending_keywords_export', data, 3600)
    
    return f"Exported {len(data['keywords'])} keywords to {output_path}"
