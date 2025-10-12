"""Advanced SEO Indexing Utilities"""
import requests
import hashlib
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def submit_indexnow(urls):
    """Submit URLs to IndexNow API (Google, Bing, Yandex)"""
    indexnow_key = getattr(settings, 'INDEXNOW_KEY', '')
    site_url = getattr(settings, 'SITE_URL', '')
    
    if not indexnow_key or not site_url:
        logger.warning("IndexNow not configured")
        return False
    
    if isinstance(urls, str):
        urls = [urls]
    
    payload = {
        "host": site_url.replace('https://', '').replace('http://', ''),
        "key": indexnow_key,
        "keyLocation": f"{site_url}/{indexnow_key}.txt",
        "urlList": urls
    }
    
    try:
        response = requests.post(
            'https://api.indexnow.org/indexnow',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code in [200, 202]:
            logger.info(f"IndexNow submitted {len(urls)} URLs successfully")
            return True
        else:
            logger.error(f"IndexNow failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"IndexNow error: {str(e)}")
        return False


def verify_google_search_console():
    """Generate Google Search Console verification meta tag"""
    gsc_code = getattr(settings, 'GOOGLE_SITE_VERIFICATION', '')
    if gsc_code:
        return f'<meta name="google-site-verification" content="{gsc_code}" />'
    return ''


def ping_google_indexing_api(url):
    """Ping Google Indexing API (requires OAuth)"""
    # Requires google-auth and google-api-python-client
    # Simplified version - full implementation needs OAuth setup
    try:
        ping_url = f"https://www.google.com/ping?sitemap={url}"
        response = requests.get(ping_url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Google ping failed: {str(e)}")
        return False


def generate_indexnow_key():
    """Generate IndexNow key file content"""
    key = getattr(settings, 'INDEXNOW_KEY', '')
    return key if key else hashlib.md5(settings.SECRET_KEY.encode()).hexdigest()


def check_url_indexed(url):
    """Check if URL is indexed in Google (basic check)"""
    try:
        search_url = f"https://www.google.com/search?q=site:{url}"
        response = requests.get(search_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; SEOBot/1.0)'
        })
        return 'did not match any documents' not in response.text
    except:
        return None


def generate_robots_meta(post):
    """Generate robots meta tag for post"""
    if not post.allow_index or post.status != 'published':
        return 'noindex, nofollow'
    return 'index, follow, max-snippet:-1, max-image-preview:large'
