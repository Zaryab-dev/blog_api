"""
Auto-populate SEO metadata from post content
"""
import re
from django.conf import settings
from django.utils.html import strip_tags


def truncate_at_word(text, max_length, suffix='...'):
    """Truncate text at word boundary"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return f"{truncated}{suffix}"


def clean_text(text):
    """Remove HTML tags and normalize whitespace"""
    text = strip_tags(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def generate_seo_title(post):
    """Generate SEO title: 'Post Title | Site Name' (max 60 chars)"""
    site_name = getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog')
    separator = ' | '
    
    # If full title fits, use it
    full_title = f"{post.title}{separator}{site_name}"
    if len(full_title) <= 60:
        return full_title
    
    # Otherwise, truncate post title to fit
    max_post_title = 60 - len(separator) - len(site_name)
    if max_post_title > 20:  # Ensure reasonable minimum
        truncated_title = truncate_at_word(post.title, max_post_title, '')
        return f"{truncated_title}{separator}{site_name}"
    
    # If site name too long, just use post title
    return truncate_at_word(post.title, 60, '')


def generate_meta_description(post):
    """Generate meta description from summary (max 160 chars)"""
    description = clean_text(post.summary)
    return truncate_at_word(description, 160)


def generate_og_title(post):
    """Generate OG title: clean post title (max 70 chars)"""
    return truncate_at_word(post.title, 70, '')


def generate_og_description(post):
    """Generate OG description from summary (max 200 chars)"""
    description = clean_text(post.summary)
    return truncate_at_word(description, 200)


def generate_canonical_url(post):
    """Generate canonical URL from slug"""
    site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
    return f"{site_url.rstrip('/')}/blog/{post.slug}"


def auto_populate_seo(post):
    """Auto-populate all SEO fields if not manually set"""
    if not post.seo_title:
        post.seo_title = generate_seo_title(post)
    
    if not post.seo_description:
        post.seo_description = generate_meta_description(post)
    
    if not post.og_title:
        post.og_title = generate_og_title(post)
    
    if not post.og_description:
        post.og_description = generate_og_description(post)
    
    if not post.canonical_url:
        post.canonical_url = generate_canonical_url(post)
    
    return post
