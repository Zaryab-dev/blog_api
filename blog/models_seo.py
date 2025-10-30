"""SEO Monitoring and Indexing Models"""
from django.db import models
from django.utils import timezone


class SchemaMetadata(models.Model):
    """Structured schema metadata for posts, authors, categories"""
    OBJECT_TYPES = [
        ('post', 'Post'),
        ('author', 'Author'),
        ('category', 'Category'),
        ('site', 'Site'),
    ]
    
    SCHEMA_TYPES = [
        ('BlogPosting', 'Blog Posting'),
        ('Person', 'Person'),
        ('Organization', 'Organization'),
        ('WebSite', 'Web Site'),
        ('BreadcrumbList', 'Breadcrumb List'),
    ]
    
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES, db_index=True)
    schema_type = models.CharField(max_length=30, choices=SCHEMA_TYPES, db_index=True)
    object_id = models.CharField(max_length=100, db_index=True)
    json_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True, db_index=True)
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_synced']
        indexes = [
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['is_active', '-last_synced']),
        ]
        unique_together = [['object_type', 'object_id', 'schema_type']]
    
    def __str__(self):
        return f"{self.schema_type} for {self.object_type}:{self.object_id}"


class SEOHealthLog(models.Model):
    """Track SEO system health and indexing status"""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    ACTION_CHOICES = [
        ('google_ping', 'Google Ping'),
        ('bing_ping', 'Bing Ping'),
        ('indexnow', 'IndexNow'),
        ('sitemap_gen', 'Sitemap Generation'),
        ('gsc_verify', 'GSC Verification'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, db_index=True)
    url = models.URLField(max_length=500, blank=True)
    response_code = models.IntegerField(null=True, blank=True)
    response_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['action', 'status', '-created_at'])]
    
    def __str__(self):
        return f"{self.action} - {self.status} - {self.created_at}"


class IndexingQueue(models.Model):
    """Queue for URLs to be submitted to search engines"""
    url = models.URLField(max_length=500, unique=True)
    priority = models.IntegerField(default=5, db_index=True)
    submitted_google = models.BooleanField(default=False)
    submitted_bing = models.BooleanField(default=False)
    submitted_indexnow = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
        indexes = [models.Index(fields=['-priority', 'created_at'])]
    
    def __str__(self):
        return f"{self.url} (Priority: {self.priority})"


class SEOAnalyticsLog(models.Model):
    """Track API hits, crawlers, and schema validation"""
    EVENT_TYPES = [
        ('api_hit', 'API Hit'),
        ('crawler_visit', 'Crawler Visit'),
        ('schema_request', 'Schema Request'),
        ('validation', 'Validation'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    url = models.URLField(max_length=500)
    object_type = models.CharField(max_length=20, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    referrer = models.URLField(max_length=500, blank=True)
    is_crawler = models.BooleanField(default=False, db_index=True)
    crawler_name = models.CharField(max_length=50, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['is_crawler', '-created_at']),
            models.Index(fields=['object_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.url} - {self.created_at}"
