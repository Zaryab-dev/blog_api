"""
Admin configuration for HomeCarousel
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import HomeCarousel


@admin.register(HomeCarousel)
class HomeCarouselAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'position', 'is_active', 'show_on_homepage', 'cta_label', 'created_at']
    list_filter = ['is_active', 'show_on_homepage', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'image_preview']
    list_editable = ['position', 'is_active']
    ordering = ['position', '-created_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Call to Action', {
            'fields': ('cta_label', 'cta_url')
        }),
        ('Display Settings', {
            'fields': ('position', 'is_active', 'show_on_homepage')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image and obj.image.file:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 200px; border: 1px solid #ddd; padding: 5px;" />',
                obj.image.file
            )
        return '-'
    image_preview.short_description = 'Preview'
