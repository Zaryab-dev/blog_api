from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models_analytics import PostView, SearchQueryLog, ReferrerLog, DailyMetrics


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'viewed_at', 'referrer_domain']
    list_filter = ['viewed_at']
    search_fields = ['post__title', 'post__slug']
    date_hierarchy = 'viewed_at'
    readonly_fields = ['post', 'ip_hash', 'user_agent_hash', 'viewed_at', 'referrer']
    
    def referrer_domain(self, obj):
        if obj.referrer:
            from urllib.parse import urlparse
            return urlparse(obj.referrer).netloc
        return '-'
    referrer_domain.short_description = 'Referrer Domain'
    
    def has_add_permission(self, request):
        return False


@admin.register(SearchQueryLog)
class SearchQueryLogAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'clicked_post', 'created_at']
    list_filter = ['created_at', 'results_count']
    search_fields = ['query', 'clicked_post__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['query', 'results_count', 'clicked_post', 'ip_hash', 'created_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(ReferrerLog)
class ReferrerLogAdmin(admin.ModelAdmin):
    list_display = ['referrer_domain', 'post', 'visit_count', 'last_visit']
    list_filter = ['referrer_domain', 'last_visit']
    search_fields = ['referrer_url', 'referrer_domain', 'post__title']
    readonly_fields = ['post', 'referrer_url', 'referrer_domain', 'visit_count', 'last_visit', 'created_at']
    ordering = ['-visit_count']
    
    def has_add_permission(self, request):
        return False


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_views', 'unique_visitors', 'total_searches', 'top_post_preview']
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = [
        'date', 'total_views', 'unique_visitors', 'total_searches',
        'top_posts_display', 'top_searches_display', 'top_referrers_display', 'created_at'
    ]
    
    def top_post_preview(self, obj):
        if obj.top_posts:
            top = obj.top_posts[0]
            return f"{top['title']} ({top['views']} views)"
        return '-'
    top_post_preview.short_description = 'Top Post'
    
    def top_posts_display(self, obj):
        if not obj.top_posts:
            return '-'
        html = '<ol>'
        for post in obj.top_posts[:5]:
            html += f"<li><strong>{post['title']}</strong> - {post['views']} views</li>"
        html += '</ol>'
        return format_html(html)
    top_posts_display.short_description = 'Top Posts'
    
    def top_searches_display(self, obj):
        if not obj.top_searches:
            return '-'
        html = '<ol>'
        for search in obj.top_searches[:5]:
            html += f"<li><strong>{search['query']}</strong> - {search['count']} searches</li>"
        html += '</ol>'
        return format_html(html)
    top_searches_display.short_description = 'Top Searches'
    
    def top_referrers_display(self, obj):
        if not obj.top_referrers:
            return '-'
        html = '<ol>'
        for ref in obj.top_referrers[:5]:
            html += f"<li><strong>{ref['domain']}</strong> - {ref['count']} visits</li>"
        html += '</ol>'
        return format_html(html)
    top_referrers_display.short_description = 'Top Referrers'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Custom admin dashboard view (optional - requires custom template)
class AnalyticsDashboard:
    """
    Custom analytics dashboard for admin
    
    To enable, add to admin.py:
    from .admin_analytics import AnalyticsDashboard
    admin.site.register_view('analytics/', view=AnalyticsDashboard.as_view())
    """
    
    @staticmethod
    def get_stats():
        """Get analytics stats for dashboard"""
        from django.db.models import Sum
        
        # Last 7 days
        since = timezone.now() - timedelta(days=7)
        
        total_views = PostView.objects.filter(viewed_at__gte=since).count()
        unique_visitors = PostView.objects.filter(viewed_at__gte=since).values('ip_hash', 'user_agent_hash').distinct().count()
        total_searches = SearchQueryLog.objects.filter(created_at__gte=since).count()
        
        # Trending posts
        trending = (
            PostView.objects
            .filter(viewed_at__gte=since)
            .values('post__title', 'post__slug')
            .annotate(views=Count('id'))
            .order_by('-views')[:10]
        )
        
        # Popular searches
        popular_searches = (
            SearchQueryLog.objects
            .filter(created_at__gte=since)
            .values('query')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        return {
            'total_views': total_views,
            'unique_visitors': unique_visitors,
            'total_searches': total_searches,
            'trending_posts': list(trending),
            'popular_searches': list(popular_searches),
        }
