"""Schema.org JSON-LD Generator"""
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def get_site_url():
    return getattr(settings, 'SITE_URL', 'https://zaryableather.com')


def generate_blog_posting_schema(post):
    """Generate BlogPosting schema for a post"""
    cache_key = f"schema_post_{post.slug}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    site_url = get_site_url()
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": f"{site_url}/blog/{post.slug}/#article",
        "headline": post.seo_title or post.title,
        "description": post.seo_description or post.summary,
        "url": f"{site_url}/blog/{post.slug}/",
        "datePublished": post.published_at.isoformat() if post.published_at else None,
        "dateModified": post.updated_at.isoformat(),
        "author": {
            "@type": "Person",
            "@id": f"{site_url}/author/{post.author.slug}/#person",
            "name": post.author.name,
            "url": f"{site_url}/author/{post.author.slug}/"
        },
        "publisher": {
            "@type": "Organization",
            "name": getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog'),
            "logo": {
                "@type": "ImageObject",
                "url": f"{site_url}/static/logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{site_url}/blog/{post.slug}/"
        },
        "wordCount": post.word_count,
        "timeRequired": f"PT{post.reading_time}M",
        "inLanguage": post.locale or "en"
    }
    
    if post.featured_image:
        schema["image"] = {
            "@type": "ImageObject",
            "url": post.featured_image.file,
            "width": post.featured_image.width,
            "height": post.featured_image.height
        }
    
    if post.seo_keywords:
        schema["keywords"] = post.seo_keywords
    elif post.tags.exists():
        schema["keywords"] = ", ".join([tag.name for tag in post.tags.all()])
    
    if post.categories.exists():
        schema["articleSection"] = [cat.name for cat in post.categories.all()]
    
    cache.set(cache_key, schema, 3600)
    return schema


def generate_person_schema(author):
    """Generate Person schema for an author"""
    cache_key = f"schema_author_{author.slug}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    site_url = get_site_url()
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": f"{site_url}/author/{author.slug}/#person",
        "name": author.name,
        "url": f"{site_url}/author/{author.slug}/",
        "description": author.bio
    }
    
    if author.avatar:
        schema["image"] = author.avatar
    
    if author.website:
        schema["sameAs"] = [author.website]
        if author.twitter_handle:
            schema["sameAs"].append(f"https://twitter.com/{author.twitter_handle.lstrip('@')}")
    
    cache.set(cache_key, schema, 3600)
    return schema


def generate_organization_schema():
    """Generate Organization schema for the site"""
    cache_key = "schema_organization"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    site_url = get_site_url()
    site_name = getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog')
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{site_url}/#organization",
        "name": site_name,
        "url": site_url,
        "logo": {
            "@type": "ImageObject",
            "url": f"{site_url}/static/logo.png"
        },
        "sameAs": []
    }
    
    twitter = getattr(settings, 'TWITTER_SITE', '')
    if twitter:
        schema["sameAs"].append(f"https://twitter.com/{twitter.lstrip('@')}")
    
    cache.set(cache_key, schema, 86400)
    return schema


def generate_website_schema():
    """Generate WebSite schema with search action"""
    cache_key = "schema_website"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    site_url = get_site_url()
    site_name = getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog')
    
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{site_url}/#website",
        "name": site_name,
        "url": site_url,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{site_url}/search?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        }
    }
    
    cache.set(cache_key, schema, 86400)
    return schema


def generate_breadcrumb_schema(post):
    """Generate BreadcrumbList schema for a post"""
    cache_key = f"schema_breadcrumb_{post.slug}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
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
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }
    
    cache.set(cache_key, schema, 3600)
    return schema


def sync_schema_to_db(obj, schema_type, schema_data):
    """Save schema to SchemaMetadata model"""
    from .models_seo import SchemaMetadata
    
    object_type_map = {
        'Post': 'post',
        'Author': 'author',
        'Category': 'category'
    }
    
    object_type = object_type_map.get(obj.__class__.__name__, 'post')
    object_id = str(obj.slug if hasattr(obj, 'slug') else obj.id)
    
    SchemaMetadata.objects.update_or_create(
        object_type=object_type,
        object_id=object_id,
        schema_type=schema_type,
        defaults={
            'json_data': schema_data,
            'is_active': True
        }
    )
