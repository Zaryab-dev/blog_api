#!/usr/bin/env python
"""Update canonical URLs for all existing posts"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from blog.models import Post
from django.conf import settings

def update_canonical_urls():
    site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
    posts = Post.objects.all()
    updated = 0
    
    for post in posts:
        canonical_url = f"{site_url.rstrip('/')}/blog/{post.slug}/"
        if post.canonical_url != canonical_url:
            post.canonical_url = canonical_url
            post.save(update_fields=['canonical_url'])
            updated += 1
            print(f"✅ Updated: {post.title} -> {canonical_url}")
    
    print(f"\n✅ Updated {updated} posts with canonical URLs")

if __name__ == '__main__':
    update_canonical_urls()
