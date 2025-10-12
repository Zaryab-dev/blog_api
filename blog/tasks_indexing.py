"""Celery tasks for SEO indexing"""
from celery import shared_task
from django.conf import settings
from .models_seo import IndexingQueue, SEOHealthLog
from .seo_indexing import submit_indexnow
from .seo_utils import notify_search_engines
import logging

logger = logging.getLogger(__name__)


@shared_task
def submit_url_to_indexnow(url):
    """Submit single URL to IndexNow"""
    try:
        success = submit_indexnow([url])
        SEOHealthLog.objects.create(
            action='indexnow',
            status='success' if success else 'failed',
            url=url
        )
        return success
    except Exception as e:
        logger.error(f"IndexNow task failed: {str(e)}")
        return False


@shared_task
def process_indexing_queue():
    """Process pending URLs in queue"""
    from django.utils import timezone
    
    pending = IndexingQueue.objects.filter(
        processed_at__isnull=True
    ).order_by('-priority', 'created_at')[:50]
    
    if not pending:
        return 0
    
    urls = [item.url for item in pending]
    
    if submit_indexnow(urls):
        for item in pending:
            item.submitted_indexnow = True
            item.processed_at = timezone.now()
            item.save()
        return len(urls)
    
    return 0


@shared_task
def ping_search_engines_task():
    """Ping Google and Bing"""
    results = notify_search_engines()
    
    for engine, success in results.items():
        SEOHealthLog.objects.create(
            action=f'{engine}_ping',
            status='success' if success else 'failed'
        )
    
    return results


@shared_task
def queue_new_post_for_indexing(post_id):
    """Queue new post for indexing"""
    from .models import Post
    
    try:
        post = Post.objects.get(id=post_id)
        site_url = getattr(settings, 'SITE_URL', '')
        url = f"{site_url}/blog/{post.slug}/"
        
        IndexingQueue.objects.get_or_create(
            url=url,
            defaults={'priority': 10}
        )
        
        # Immediate IndexNow submission
        submit_url_to_indexnow.delay(url)
        
        return True
    except Exception as e:
        logger.error(f"Queue post failed: {str(e)}")
        return False
