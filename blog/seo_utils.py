"""
SEO Utilities for Django Blog API
Provides structured data generation, Open Graph, Twitter Cards, and schema.org support
"""

from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional
import requests
import logging

logger = logging.getLogger(__name__)


def get_site_url() -> str:
    """Get the site URL from settings"""
    return getattr(settings, 'SITE_URL', 'https://zaryableather.com')


def get_site_name() -> str:
    """Get the site name from settings"""
    return getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog')


def generate_schema_article(post) -> Dict[str, Any]:
    """
    Generate schema.org Article JSON-LD for a blog post
    
    Args:
        post: Post model instance
        
    Returns:
        dict: Schema.org Article structured data
    """
    site_url = get_site_url()
    site_name = get_site_name()
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.seo_title or post.title,
        "description": post.seo_description or post.summary,
        "articleBody": post.summary,
        "url": post.canonical_url or f"{site_url}/blog/{post.slug}/",
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
            "@id": post.canonical_url or f"{site_url}/blog/{post.slug}/"
        },
        "isAccessibleForFree": True,
        "wordCount": post.word_count,
        "timeRequired": f"PT{post.reading_time}M",
        "inLanguage": post.locale or "en"
    }
    
    # Add image if available
    if post.featured_image:
        schema["image"] = {
            "@type": "ImageObject",
            "url": post.featured_image.file,
            "width": post.featured_image.width,
            "height": post.featured_image.height
        }
    elif post.og_image:
        schema["image"] = post.og_image
    
    # Add keywords
    if post.seo_keywords:
        schema["keywords"] = post.seo_keywords
    elif post.tags.exists():
        schema["keywords"] = ", ".join([tag.name for tag in post.tags.all()])
    
    # Add article section (category)
    if post.categories.exists():
        schema["articleSection"] = [cat.name for cat in post.categories.all()]
    
    return schema


def generate_schema_breadcrumb(post) -> Dict[str, Any]:
    """
    Generate schema.org BreadcrumbList for a blog post
    
    Args:
        post: Post model instance
        
    Returns:
        dict: Schema.org BreadcrumbList structured data
    """
    site_url = get_site_url()
    
    items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": site_url
        },
        {
            "@type": "ListItem",
            "position": 2,
            "name": "Blog",
            "item": f"{site_url}/blog/"
        }
    ]
    
    # Add category if exists
    if post.categories.exists():
        category = post.categories.first()
        items.append({
            "@type": "ListItem",
            "position": 3,
            "name": category.name,
            "item": f"{site_url}/category/{category.slug}/"
        })
        items.append({
            "@type": "ListItem",
            "position": 4,
            "name": post.title,
            "item": f"{site_url}/blog/{post.slug}/"
        })
    else:
        items.append({
            "@type": "ListItem",
            "position": 3,
            "name": post.title,
            "item": f"{site_url}/blog/{post.slug}/"
        })
    
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }


def generate_open_graph_data(post) -> Dict[str, str]:
    """
    Generate Open Graph metadata for a blog post
    
    Args:
        post: Post model instance
        
    Returns:
        dict: Open Graph metadata
    """
    site_url = get_site_url()
    site_name = get_site_name()
    
    og_data = {
        "og:type": post.og_type or "article",
        "og:title": post.og_title or post.seo_title or post.title,
        "og:description": post.og_description or post.seo_description or post.summary,
        "og:url": post.canonical_url or f"{site_url}/blog/{post.slug}/",
        "og:site_name": site_name,
        "og:locale": post.locale or "en_US"
    }
    
    # Add image
    if post.og_image:
        og_data["og:image"] = post.og_image
        og_data["og:image:width"] = "1200"
        og_data["og:image:height"] = "630"
    elif post.featured_image:
        og_data["og:image"] = post.featured_image.og_image_url or post.featured_image.file
        og_data["og:image:width"] = str(post.featured_image.width)
        og_data["og:image:height"] = str(post.featured_image.height)
    
    # Article-specific tags
    if post.og_type == "article":
        og_data["article:published_time"] = post.published_at.isoformat() if post.published_at else ""
        og_data["article:modified_time"] = post.updated_at.isoformat()
        og_data["article:author"] = f"{site_url}/author/{post.author.slug}/"
        
        if post.categories.exists():
            og_data["article:section"] = post.categories.first().name
        
        if post.tags.exists():
            og_data["article:tag"] = [tag.name for tag in post.tags.all()]
    
    return og_data


def generate_twitter_card_data(post) -> Dict[str, str]:
    """
    Generate Twitter Card metadata for a blog post
    
    Args:
        post: Post model instance
        
    Returns:
        dict: Twitter Card metadata
    """
    site_url = get_site_url()
    
    twitter_data = {
        "twitter:card": post.twitter_card or "summary_large_image",
        "twitter:title": post.og_title or post.seo_title or post.title,
        "twitter:description": post.og_description or post.seo_description or post.summary,
        "twitter:site": getattr(settings, 'TWITTER_SITE', '@zaryableather')
    }
    
    # Add creator if author has Twitter handle
    if post.author.twitter_handle:
        twitter_data["twitter:creator"] = f"@{post.author.twitter_handle.lstrip('@')}"
    
    # Add image
    if post.og_image:
        twitter_data["twitter:image"] = post.og_image
    elif post.featured_image:
        twitter_data["twitter:image"] = post.featured_image.file
    
    return twitter_data


def ping_google_sitemap(sitemap_url: Optional[str] = None) -> bool:
    """
    Ping Google to notify about sitemap updates
    
    Args:
        sitemap_url: Full URL to sitemap (optional, uses default if not provided)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not sitemap_url:
        site_url = get_site_url()
        sitemap_url = f"{site_url}/sitemap.xml"
    
    try:
        ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"
        response = requests.get(ping_url, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Successfully pinged Google for sitemap: {sitemap_url}")
            return True
        else:
            logger.warning(f"Google ping returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to ping Google: {str(e)}")
        return False


def ping_bing_sitemap(sitemap_url: Optional[str] = None) -> bool:
    """
    Ping Bing to notify about sitemap updates
    
    Args:
        sitemap_url: Full URL to sitemap (optional, uses default if not provided)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not sitemap_url:
        site_url = get_site_url()
        sitemap_url = f"{site_url}/sitemap.xml"
    
    try:
        ping_url = f"https://www.bing.com/ping?sitemap={sitemap_url}"
        response = requests.get(ping_url, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Successfully pinged Bing for sitemap: {sitemap_url}")
            return True
        else:
            logger.warning(f"Bing ping returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to ping Bing: {str(e)}")
        return False


def notify_search_engines(sitemap_url: Optional[str] = None) -> Dict[str, bool]:
    """
    Notify both Google and Bing about sitemap updates
    
    Args:
        sitemap_url: Full URL to sitemap (optional, uses default if not provided)
        
    Returns:
        dict: Results for each search engine
    """
    return {
        "google": ping_google_sitemap(sitemap_url),
        "bing": ping_bing_sitemap(sitemap_url)
    }


def generate_meta_robots(post) -> str:
    """
    Generate meta robots directive for a post
    
    Args:
        post: Post model instance
        
    Returns:
        str: Meta robots directive
    """
    if not post.allow_index:
        return "noindex, nofollow"
    
    if post.status != 'published':
        return "noindex, nofollow"
    
    return "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"


def get_canonical_url(post) -> str:
    """
    Get the canonical URL for a post
    
    Args:
        post: Post model instance
        
    Returns:
        str: Canonical URL
    """
    if post.canonical_url:
        return post.canonical_url
    
    site_url = get_site_url()
    return f"{site_url}/blog/{post.slug}/"
