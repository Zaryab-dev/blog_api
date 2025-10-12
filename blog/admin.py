from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import (
    Author, Category, Tag, Post, ImageAsset, Comment, 
    Subscriber, SiteSettings, Redirect, SEOMetadata, SitemapGenerationLog
)
from .admin_forms import ImageAssetAdminForm


class PostAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
    
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='extends')
        }


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'twitter_handle', 'created_at']
    search_fields = ['name', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'bio', 'avatar', 'website')
        }),
        ('Social', {
            'fields': ('twitter_handle',)
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'count_published_posts', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'count_published_posts']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'count_published_posts', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'count_published_posts']


@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    form = ImageAssetAdminForm
    list_display = ['thumbnail_preview', 'alt_text', 'width', 'height', 'format', 'created_at']
    search_fields = ['alt_text', 'file']
    readonly_fields = ['id', 'created_at', 'updated_at', 'thumbnail_preview', 'file_url_display']
    fieldsets = (
        ('Upload', {
            'fields': ('upload_file',),
            'description': 'Upload a new image to Supabase Storage'
        }),
        ('Image Info', {
            'fields': ('file', 'file_url_display', 'alt_text', 'width', 'height', 'format')
        }),
        ('Preview', {
            'fields': ('thumbnail_preview',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; border: 1px solid #ddd; padding: 5px;" />', obj.file)
        return '-'
    thumbnail_preview.short_description = 'Preview'
    
    def file_url_display(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file, obj.file)
        return '-'
    file_url_display.short_description = 'Supabase URL'


class SEOMetadataInline(admin.StackedInline):
    model = SEOMetadata
    extra = 0
    fields = ['meta_keywords', 'twitter_card', 'twitter_creator', 'facebook_app_id']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ['title', 'author', 'status', 'published_at', 'views_count', 'likes_count', 'trending_score', 'thumbnail']
    list_filter = ['status', 'categories', 'tags', 'author', 'created_at']
    search_fields = ['title', 'summary', 'content_html']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'reading_time', 'word_count', 'slug_preview', 'preview_button', 'content_html', 'views_count', 'likes_count', 'comments_count', 'trending_score']
    filter_horizontal = ['categories', 'tags']
    date_hierarchy = 'published_at'
    inlines = [SEOMetadataInline]
    ordering = ['-trending_score', '-published_at']
    
    actions = ['publish_posts', 'unpublish_posts']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'slug_preview', 'summary', 'content', 'content_markdown')
        }),
        ('Relationships', {
            'fields': ('author', 'categories', 'tags', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('status', 'published_at', 'allow_index')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'canonical_url', 'og_title', 'og_description', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Advanced', {
            'fields': ('schema_org', 'legacy_urls', 'product_references', 'locale'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('reading_time', 'word_count', 'content_html'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'trending_score'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def slug_preview(self, obj):
        if obj.slug:
            return format_html('<code>/blog/{}/</code>', obj.slug)
        return '-'
    slug_preview.short_description = 'URL Preview'
    
    def thumbnail(self, obj):
        if obj.featured_image and obj.featured_image.file:
            return format_html('<img src="{}" width="50" />', obj.featured_image.file)
        return '-'
    thumbnail.short_description = 'Image'
    
    def preview_button(self, obj):
        if obj.pk:
            preview_url = f"https://zaryableather.com/blog/{obj.slug}/?preview=true"
            return format_html('<a href="{}" target="_blank" class="button">Preview</a>', preview_url)
        return '-'
    preview_button.short_description = 'Preview'
    
    def publish_posts(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{count} posts published.')
    publish_posts.short_description = 'Publish selected posts'
    
    def unpublish_posts(self, request, queryset):
        count = queryset.update(status='draft')
        self.message_user(request, f'{count} posts unpublished.')
    unpublish_posts.short_description = 'Unpublish selected posts'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    actions = ['approve_comments', 'mark_as_spam']
    
    def approve_comments(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'{count} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def mark_as_spam(self, request, queryset):
        count = queryset.update(status='spam')
        self.message_user(request, f'{count} comments marked as spam.')
    mark_as_spam.short_description = 'Mark as spam'


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'verified', 'subscribed_at']
    list_filter = ['verified', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'subscribed_at']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('site_name', 'site_description', 'site_url')
        }),
        ('SEO Defaults', {
            'fields': ('default_meta_image', 'default_title_template', 'default_description_template')
        }),
        ('URLs', {
            'fields': ('sitemap_index_url', 'rss_feed_url')
        }),
        ('Social', {
            'fields': ('twitter_site', 'facebook_app_id', 'google_site_verification')
        }),
        ('Robots', {
            'fields': ('robots_txt_content',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ['from_path', 'to_url', 'status_code', 'active', 'created_at']
    list_filter = ['status_code', 'active', 'created_at']
    search_fields = ['from_path', 'to_url', 'reason']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(SitemapGenerationLog)
class SitemapGenerationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'total_posts', 'total_files', 'started_at', 'completed_at', 'duration']
    list_filter = ['status', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'duration', 's3_urls_display']
    search_fields = ['error_message']
    
    fieldsets = (
        ('Status', {
            'fields': ('status', 'started_at', 'completed_at', 'duration')
        }),
        ('Stats', {
            'fields': ('total_posts', 'total_files')
        }),
        ('S3 URLs', {
            'fields': ('s3_urls_display',),
            'classes': ('collapse',)
        }),
        ('Error', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration(self, obj):
        if obj.started_at and obj.completed_at:
            delta = obj.completed_at - obj.started_at
            return f"{delta.total_seconds():.2f}s"
        return '-'
    duration.short_description = 'Duration'
    
    def s3_urls_display(self, obj):
        if obj.s3_urls:
            urls = '<br>'.join([f'<a href="{url}" target="_blank">{url}</a>' for url in obj.s3_urls])
            return format_html(urls)
        return '-'
    s3_urls_display.short_description = 'S3 URLs'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
