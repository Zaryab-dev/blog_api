import re
import hashlib
from django.utils.text import slugify as django_slugify
from django.conf import settings


def generate_slug(title, max_length=100):
    """Generate URL-safe slug from title"""
    slug = django_slugify(title)
    return slug[:max_length]


def estimate_reading_time(content_html):
    """Estimate reading time in minutes (250 words/min)"""
    text = re.sub(r'<[^>]+>', '', content_html)
    words = len(text.split())
    minutes = max(1, round(words / 250))
    return minutes


def count_words(content_html):
    """Count words in HTML content"""
    text = re.sub(r'<[^>]+>', '', content_html)
    return len(text.split())


def get_canonical_url(post):
    """Generate canonical URL for post"""
    if post.canonical_url:
        return post.canonical_url
    site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
    return f"{site_url}/blog/{post.slug}/"


def generate_structured_data(post):
    """Generate schema.org Article JSON-LD"""
    site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
    site_name = getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog')
    
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.title,
        "datePublished": post.published_at.isoformat() if post.published_at else None,
        "dateModified": post.updated_at.isoformat(),
        "author": {
            "@type": "Person",
            "name": post.author.name,
            "url": f"{site_url}/author/{post.author.slug}/"
        },
        "publisher": {
            "@type": "Organization",
            "name": site_name,
            "logo": {
                "@type": "ImageObject",
                "url": f"{site_url}/static/logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": get_canonical_url(post)
        },
        "isAccessibleForFree": True,
        "wordCount": post.word_count
    }
    
    if post.featured_image:
        data["image"] = [post.featured_image.file.url]
    
    return data


def generate_etag(post):
    """Generate ETag for post"""
    etag_source = f"{post.id}:{post.updated_at.isoformat()}"
    return hashlib.md5(etag_source.encode()).hexdigest()
