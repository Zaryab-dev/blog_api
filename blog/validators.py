"""
Input validation utilities for blog app
"""
import re
from django.core.exceptions import ValidationError


def validate_slug(slug):
    """Validate slug format"""
    if not re.match(r'^[a-z0-9-]+$', slug):
        raise ValidationError('Slug must contain only lowercase letters, numbers, and hyphens')
    if len(slug) > 100:
        raise ValidationError('Slug must be 100 characters or less')
    return slug


def validate_search_query(query):
    """Validate and sanitize search query"""
    if not query:
        return ''
    
    # Remove dangerous characters
    query = re.sub(r'[;\\<>]', '', query)
    
    # Limit length
    query = query[:200].strip()
    
    # Minimum length
    if len(query) < 2:
        raise ValidationError('Search query must be at least 2 characters')
    
    return query


def validate_email_domain(email):
    """Validate email domain (prevent disposable emails)"""
    disposable_domains = [
        'tempmail.com', 'throwaway.email', '10minutemail.com',
        'guerrillamail.com', 'mailinator.com'
    ]
    
    domain = email.split('@')[-1].lower()
    if domain in disposable_domains:
        raise ValidationError('Disposable email addresses are not allowed')
    
    return email


def validate_comment_content(content):
    """Validate comment content"""
    if not content or not content.strip():
        raise ValidationError('Comment content cannot be empty')
    
    if len(content) > 1000:
        raise ValidationError('Comment must be 1000 characters or less')
    
    # Check for spam patterns
    spam_patterns = [
        r'http[s]?://.*http[s]?://',  # Multiple URLs
        r'(viagra|cialis|casino|poker)',  # Common spam words
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            raise ValidationError('Comment appears to be spam')
    
    return content.strip()
