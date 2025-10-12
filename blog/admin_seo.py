from django.contrib import admin
from .models_seo import SchemaMetadata, SEOHealthLog, IndexingQueue, SEOAnalyticsLog


@admin.register(SchemaMetadata)
class SchemaMetadataAdmin(admin.ModelAdmin):
    list_display = ['schema_type', 'object_type', 'object_id', 'is_active', 'last_synced']
    list_filter = ['schema_type', 'object_type', 'is_active']
    search_fields = ['object_id']
    readonly_fields = ['last_synced', 'created_at']


@admin.register(SEOHealthLog)
class SEOHealthLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'status', 'url', 'response_code', 'created_at']
    list_filter = ['action', 'status', 'created_at']
    search_fields = ['url', 'response_message']
    readonly_fields = ['created_at']


@admin.register(IndexingQueue)
class IndexingQueueAdmin(admin.ModelAdmin):
    list_display = ['url', 'priority', 'submitted_google', 'submitted_bing', 'submitted_indexnow', 'created_at']
    list_filter = ['submitted_google', 'submitted_bing', 'submitted_indexnow']
    search_fields = ['url']
    readonly_fields = ['created_at', 'processed_at']


@admin.register(SEOAnalyticsLog)
class SEOAnalyticsLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'url', 'is_crawler', 'crawler_name', 'created_at']
    list_filter = ['event_type', 'is_crawler', 'created_at']
    search_fields = ['url', 'crawler_name', 'ip_address']
    readonly_fields = ['created_at']
