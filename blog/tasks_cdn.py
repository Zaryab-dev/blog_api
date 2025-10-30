from celery import shared_task
from django.conf import settings
import requests
import logging

logger = logging.getLogger('celery')


@shared_task(bind=True, max_retries=3)
def purge_cdn_cache(self, paths=None):
    """
    Purge CDN cache for specified paths
    
    Supports Cloudflare and BunnyCDN
    
    Args:
        paths: List of paths to purge (e.g. ['/blog/post-slug', '/sitemap.xml'])
    """
    cdn_provider = getattr(settings, 'CDN_PROVIDER', None)
    
    if not cdn_provider:
        return "CDN_PROVIDER not configured"
    
    if paths is None:
        paths = []
    
    try:
        if cdn_provider == 'cloudflare':
            return _purge_cloudflare(paths)
        elif cdn_provider == 'bunnycdn':
            return _purge_bunnycdn(paths)
        else:
            return f"Unsupported CDN provider: {cdn_provider}"
    
    except Exception as e:
        logger.error(f"CDN purge failed: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


def _purge_cloudflare(paths):
    """Purge Cloudflare cache"""
    zone_id = getattr(settings, 'CLOUDFLARE_ZONE_ID', '')
    api_token = getattr(settings, 'CLOUDFLARE_API_TOKEN', '')
    
    if not zone_id or not api_token:
        return "Cloudflare credentials not configured"
    
    # Build full URLs
    site_url = getattr(settings, 'SITE_URL', '')
    files = [f"{site_url}{path}" for path in paths] if paths else []
    
    # Purge everything if no paths specified
    if not files:
        payload = {"purge_everything": True}
    else:
        payload = {"files": files}
    
    response = requests.post(
        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        },
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        return f"Cloudflare cache purged: {len(files)} files"
    else:
        return f"Cloudflare purge failed: {response.status_code}"


def _purge_bunnycdn(paths):
    """Purge BunnyCDN cache"""
    api_key = getattr(settings, 'BUNNYCDN_API_KEY', '')
    pull_zone_id = getattr(settings, 'BUNNYCDN_PULL_ZONE_ID', '')
    
    if not api_key or not pull_zone_id:
        return "BunnyCDN credentials not configured"
    
    # Purge entire pull zone if no paths specified
    if not paths:
        response = requests.post(
            f'https://api.bunny.net/pullzone/{pull_zone_id}/purgeCache',
            headers={'AccessKey': api_key},
            timeout=10
        )
    else:
        # Purge specific URLs
        site_url = getattr(settings, 'SITE_URL', '')
        for path in paths:
            url = f"{site_url}{path}"
            response = requests.post(
                f'https://api.bunny.net/purge',
                params={'url': url},
                headers={'AccessKey': api_key},
                timeout=10
            )
    
    if response.status_code in [200, 204]:
        return f"BunnyCDN cache purged: {len(paths)} paths"
    else:
        return f"BunnyCDN purge failed: {response.status_code}"


@shared_task
def purge_post_cache(post_slug):
    """Purge CDN cache for a specific post"""
    paths = [
        f'/blog/{post_slug}',
        '/blog',
        '/sitemap.xml',
        '/api/v1/posts/',
        f'/api/v1/posts/{post_slug}/',
    ]
    return purge_cdn_cache.delay(paths)


@shared_task
def purge_sitemap_cache():
    """Purge CDN cache for sitemap and RSS"""
    paths = [
        '/sitemap.xml',
        '/rss.xml',
        '/api/v1/sitemap.xml',
        '/api/v1/rss.xml',
    ]
    return purge_cdn_cache.delay(paths)
