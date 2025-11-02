from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post, Comment, Category, Tag, ImageAsset, Redirect
from .utils import estimate_reading_time, count_words, generate_structured_data


@receiver(pre_save, sender=Post)
def post_pre_save(sender, instance, **kwargs):
    """Auto-populate fields before saving"""
    # Note: Most auto-population is now in Post.save() method
    # This signal is kept for backward compatibility
    pass


@receiver(post_save, sender=Post)
def post_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Invalidate caches
    cache.delete(f"post:{instance.slug}")
    # Only delete patterns if cache backend supports it (Redis)
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("posts:list:*")
        cache.delete_pattern("posts:slugs:*")
        cache.delete_pattern("sitemap:*")
    cache.delete("rss:feed")
    
    # Create redirects from legacy URLs
    if instance.legacy_urls:
        for legacy_url in instance.legacy_urls:
            Redirect.objects.get_or_create(
                from_path=legacy_url,
                defaults={
                    'to_url': f"https://zaryableather.com/blog/{instance.slug}/",
                    'status_code': 301,
                    'active': True,
                    'reason': f'Legacy URL for post: {instance.title}'
                }
            )
    
    # Queue sitemap regeneration and CDN purge (Celery tasks)
    if instance.status == 'published':
        try:
            from .tasks import regenerate_sitemap, trigger_nextjs_revalidation
            from .tasks_cdn import purge_post_cache
            regenerate_sitemap.delay()
            trigger_nextjs_revalidation.delay(instance.id)
            purge_post_cache.delay(instance.slug)
        except Exception:
            # Skip Celery tasks in development without Redis
            pass
        
        # Ping search engines when post is newly published
        if created or not instance.pk:
            from django.conf import settings
            if getattr(settings, 'AUTO_PING_SEARCH_ENGINES', True):
                try:
                    from .seo_utils import notify_search_engines
                    import threading
                    
                    def ping_async():
                        try:
                            results = notify_search_engines()
                            logger.info(f"Pinged search engines for post: {instance.slug}. Results: {results}")
                        except Exception as e:
                            logger.error(f"Failed to ping search engines: {str(e)}")
                    
                    thread = threading.Thread(target=ping_async)
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    logger.error(f"Error setting up search engine ping: {str(e)}")


@receiver(post_delete, sender=Post)
def post_post_delete(sender, instance, **kwargs):
    """Handle post deletion"""
    # Invalidate caches
    cache.delete(f"post:{instance.slug}")
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("posts:list:*")
        cache.delete_pattern("posts:slugs:*")
        cache.delete_pattern("sitemap:*")
    cache.delete("rss:feed")
    
    # Queue sitemap regeneration and CDN purge
    try:
        from .tasks import regenerate_sitemap
        from .tasks_cdn import purge_sitemap_cache
        regenerate_sitemap.delay()
        purge_sitemap_cache.delay()
    except Exception:
        pass


@receiver(m2m_changed, sender=Post.categories.through)
@receiver(m2m_changed, sender=Post.tags.through)
def post_m2m_changed(sender, instance, action, **kwargs):
    """Update category/tag counts and auto-generate keywords when posts are added/removed"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Update category counts
        for category in Category.objects.all():
            category.count_published_posts = category.posts.filter(status='published').count()
            category.save(update_fields=['count_published_posts'])
        
        # Update tag counts
        for tag in Tag.objects.all():
            tag.count_published_posts = tag.posts.filter(status='published').count()
            tag.save(update_fields=['count_published_posts'])
    
    # Auto-generate keywords after categories/tags are added
    if action == 'post_add':
        if not instance.keywords or len(instance.keywords) == 0:
            keywords = set(['leather'])
            
            # Add from categories
            for cat in instance.categories.all():
                keywords.add(cat.name.lower())
                keywords.add(f'leather {cat.name.lower()}')
            
            # Add from tags
            for tag in instance.tags.all():
                keywords.add(tag.name.lower())
            
            instance.keywords = list(keywords)[:10]
            instance.save(update_fields=['keywords'])


@receiver(post_save, sender=Comment)
def comment_post_save(sender, instance, created, **kwargs):
    """Invalidate post cache and send notification when comment is created"""
    if instance.status == 'approved':
        cache.delete(f"post:{instance.post.slug}")
    
    # Send notification email for new comments
    if created:
        from .tasks import send_comment_notification
        send_comment_notification.delay(instance.id)


@receiver(post_save, sender=ImageAsset)
def image_post_save(sender, instance, created, **kwargs):
    """Queue image processing task"""
    if created:
        # In production, trigger Celery task to generate responsive variants
        # from .tasks import generate_image_variants
        # generate_image_variants.delay(instance.id)
        pass
