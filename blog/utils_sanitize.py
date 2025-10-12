"""
HTML sanitization utilities for rich text content
"""
import bleach
from django.conf import settings
from bs4 import BeautifulSoup
import re


def sanitize_html(html_content):
    """
    Sanitize HTML content using bleach
    
    Args:
        html_content: Raw HTML string
        
    Returns:
        Sanitized HTML string
    """
    if not html_content:
        return ''
    
    # Sanitize with bleach
    clean_html = bleach.clean(
        html_content,
        tags=settings.ALLOWED_HTML_TAGS,
        attributes=settings.ALLOWED_HTML_ATTRS,
        strip=True,
    )
    
    # Add rel="noopener noreferrer" to external links
    clean_html = bleach.linkify(
        clean_html,
        callbacks=[add_noopener_callback],
        skip_tags=['pre', 'code'],
    )
    
    return clean_html


def add_noopener_callback(attrs, new=False):
    """Add noopener noreferrer to external links"""
    href = attrs.get((None, 'href'), '')
    
    if href.startswith('http'):
        attrs[(None, 'rel')] = 'noopener noreferrer'
        attrs[(None, 'target')] = '_blank'
    
    return attrs


def strip_html_tags(html_content):
    """
    Strip all HTML tags and return plain text
    
    Args:
        html_content: HTML string
        
    Returns:
        Plain text string
    """
    if not html_content:
        return ''
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def calculate_reading_time(html_content):
    """
    Calculate reading time based on word count
    
    Args:
        html_content: HTML string
        
    Returns:
        Reading time in minutes
    """
    text = strip_html_tags(html_content)
    word_count = len(text.split())
    
    # Average reading speed: 200 words per minute
    reading_time = max(1, round(word_count / 200))
    
    return reading_time


def extract_excerpt(html_content, max_length=320):
    """
    Extract plain text excerpt from HTML
    
    Args:
        html_content: HTML string
        max_length: Maximum excerpt length
        
    Returns:
        Plain text excerpt
    """
    text = strip_html_tags(html_content)
    
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary
    excerpt = text[:max_length].rsplit(' ', 1)[0]
    return f"{excerpt}..."


def count_words(html_content):
    """
    Count words in HTML content
    
    Args:
        html_content: HTML string
        
    Returns:
        Word count
    """
    text = strip_html_tags(html_content)
    return len(text.split())
