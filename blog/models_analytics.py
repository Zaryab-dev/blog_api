import hashlib
from django.db import models
from django.utils import timezone
from .models import TimeStampedModel, Post


class PostView(models.Model):
    """Track anonymous post views for analytics"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views', db_index=True)
    ip_hash = models.CharField(max_length=64, db_index=True)
    user_agent_hash = models.CharField(max_length=64, db_index=True)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    referrer = models.URLField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['post', '-viewed_at']),
            models.Index(fields=['ip_hash', 'user_agent_hash', 'post']),
        ]
    
    def __str__(self):
        return f"View on {self.post.slug} at {self.viewed_at}"
    
    @staticmethod
    def hash_identifier(value):
        """Hash IP or User-Agent for privacy"""
        return hashlib.sha256(value.encode()).hexdigest()


class SearchQueryLog(TimeStampedModel):
    """Track search queries for keyword analysis"""
    query = models.CharField(max_length=200, db_index=True)
    results_count = models.IntegerField(default=0)
    clicked_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='search_clicks')
    ip_hash = models.CharField(max_length=64, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Search: {self.query} ({self.results_count} results)"


class ReferrerLog(TimeStampedModel):
    """Track HTTP referrers for backlink analysis"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='referrers', db_index=True)
    referrer_url = models.URLField(max_length=500, db_index=True)
    referrer_domain = models.CharField(max_length=200, db_index=True)
    visit_count = models.IntegerField(default=1)
    last_visit = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_count', '-last_visit']
        indexes = [
            models.Index(fields=['post', '-visit_count']),
            models.Index(fields=['referrer_domain', '-visit_count']),
        ]
        unique_together = [['post', 'referrer_url']]
    
    def __str__(self):
        return f"{self.referrer_domain} → {self.post.slug} ({self.visit_count})"


class DailyMetrics(models.Model):
    """Aggregated daily analytics metrics"""
    date = models.DateField(unique=True, db_index=True)
    total_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    total_searches = models.IntegerField(default=0)
    top_posts = models.JSONField(default=list)  # [{slug, views, title}]
    top_searches = models.JSONField(default=list)  # [{query, count}]
    top_referrers = models.JSONField(default=list)  # [{domain, count}]
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Daily Metrics'
    
    def __str__(self):
        return f"Metrics for {self.date}"
