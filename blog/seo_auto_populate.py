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
    site_url = getattr(settings, 'NEXTJS_URL', 'https://zaryableather.com')
    return f"{site_url.rstrip('/')}/{post.slug}"


def extract_keywords_from_content(post):
    """Extract relevant keywords from post content"""
    keywords = set()
    
    # Common leather-related terms
    leather_terms = [
        'leather', 'genuine leather', 'full grain', 'top grain', 'leather care',
        'leather maintenance', 'leather cleaning', 'leather products', 'leather goods',
        'leather jacket', 'leather bag', 'leather wallet', 'handmade leather',
        'leather craftsmanship', 'leather quality', 'leather style', 'leather fashion'
    ]
    
    content_text = (post.title + ' ' + post.summary + ' ' + clean_text(post.content_html or '')).lower()
    
    for term in leather_terms:
        if term in content_text:
            keywords.add(term)
    
    return list(keywords)[:10]


def auto_populate_seo(post):
    """Auto-populate all SEO fields if not manually set"""
    # SEO Title
    if not post.seo_title:
        post.seo_title = generate_seo_title(post)
    
    # SEO Description
    if not post.seo_description:
        post.seo_description = generate_meta_description(post)
    
    # Open Graph Title
    if not post.og_title:
        post.og_title = generate_og_title(post)
    
    # Open Graph Description
    if not post.og_description:
        post.og_description = generate_og_description(post)
    
    # Open Graph Image (use featured image if available)
    if not post.og_image and post.featured_image:
        post.og_image = post.featured_image.og_image_url or post.featured_image.file
    
    # SEO Keywords (comma-separated string)
    if not post.seo_keywords:
        keywords = extract_keywords_from_content(post)
        post.seo_keywords = ', '.join(keywords) if keywords else ''
    
    return post
