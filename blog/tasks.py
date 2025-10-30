from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
import requests
import hmac
import hashlib
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def regenerate_sitemap(self):
    """
    Regenerate sitemap and invalidate cache
    
    Triggered on post save/delete
    Retry policy: 3 attempts with 60s delay
    """
    from .models import SitemapGenerationLog
    
    log = SitemapGenerationLog.create_pending()
    log.status = 'processing'
    log.started_at = timezone.now()
    log.save()
    
    try:
        # Invalidate sitemap cache
        cache.delete_pattern('sitemap:*')
        
        # Count posts
        from .models import Post
        log.total_posts = Post.published.count()
        
        # Mark as completed
        log.status = 'completed'
        log.completed_at = timezone.now()
        log.save()
        
        return f"Sitemap regenerated: {log.total_posts} posts"
    
    except (IOError, OSError) as e:
        logger.error(f"File system error in sitemap generation: {e}")
        log.status = 'failed'
        log.error_message = str(e)
        log.completed_at = timezone.now()
        log.save()
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    
    except Exception as e:
        logger.exception(f"Unexpected error in sitemap generation: {e}")
        log.status = 'failed'
        log.error_message = str(e)
        log.completed_at = timezone.now()
        log.save()
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_nextjs_revalidation(self, post_id):
    """
    Trigger Next.js ISR revalidation webhook
    
    Sends HMAC-signed request to Next.js revalidation endpoint
    Retry policy: 3 attempts with exponential backoff
    """
    from .models import Post
    
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return f"Post {post_id} not found"
    
    # Build payload
    payload = {
        'slugs': [post.slug],
        'paths': [
            f'/blog/{post.slug}',
            '/blog',
            *[f'/category/{cat.slug}' for cat in post.categories.all()],
            *[f'/tag/{tag.slug}' for tag in post.tags.all()],
        ],
        'timestamp': timezone.now().isoformat(),
        'event': 'post.updated'
    }
    
    # Sign payload
    secret = getattr(settings, 'REVALIDATE_SECRET', '')
    if not secret:
        return "REVALIDATE_SECRET not configured"
    
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    
    # Send webhook
    nextjs_url = getattr(settings, 'NEXTJS_URL', '')
    if not nextjs_url:
        return "NEXTJS_URL not configured"
    
    try:
        response = requests.post(
            f'{nextjs_url}/api/revalidate',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Signature': signature
            },
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Revalidation triggered for post {post.slug}: {response.status_code}")
        return f"Revalidation triggered: {response.status_code}"
    
    except requests.RequestException as e:
        logger.error(f"HTTP error during revalidation: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    
    except Exception as e:
        logger.exception(f"Unexpected error during revalidation: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_comment_notification(comment_id):
    """
    Send email notification to admin when new comment is posted
    """
    from .models import Comment
    from django.core.mail import send_mail
    
    try:
        comment = Comment.objects.select_related('post').get(id=comment_id)
    except Comment.DoesNotExist:
        return f"Comment {comment_id} not found"
    
    subject = f"New comment on: {comment.post.title}"
    message = f"""
New comment from {comment.name} ({comment.email}):

{comment.content}

Post: {comment.post.title}
Moderate: {settings.SITE_URL}/admin/blog/comment/{comment.id}/change/
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info(f"Notification sent for comment {comment_id}")
        return f"Notification sent for comment {comment_id}"
    except Exception as e:
        logger.exception(f"Failed to send notification for comment {comment_id}: {e}")
        return f"Failed to send notification: {str(e)}"


@shared_task
def send_verification_email(subscriber_id):
    """
    Send verification email to new subscriber
    """
    from .models import Subscriber
    from django.core.mail import send_mail
    import uuid
    
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
    except Subscriber.DoesNotExist:
        return f"Subscriber {subscriber_id} not found"
    
    # Generate verification token (in production, use JWT or signed token)
    verification_token = str(uuid.uuid4())
    cache.set(f'verify:{verification_token}', subscriber.email, 60 * 60 * 24)  # 24 hours
    
    verification_url = f"{settings.SITE_URL}/verify/{verification_token}/"
    
    subject = "Verify your email subscription"
    message = f"""
Thank you for subscribing to Zaryab Leather Blog!

Please verify your email by clicking the link below:

{verification_url}

This link will expire in 24 hours.
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email],
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {subscriber.email}")
        return f"Verification email sent to {subscriber.email}"
    except Exception as e:
        logger.exception(f"Failed to send verification email to {subscriber.email}: {e}")
        return f"Failed to send verification email: {str(e)}"


@shared_task
def refresh_rss_feed():
    """
    Refresh RSS feed cache
    
    Scheduled task to run daily
    """
    try:
        cache.delete('rss:feed')
        logger.info("RSS feed cache refreshed")
        return "RSS feed cache refreshed"
    except Exception as e:
        logger.exception(f"Failed to refresh RSS feed cache: {e}")
        return f"Failed to refresh RSS feed cache: {str(e)}"
