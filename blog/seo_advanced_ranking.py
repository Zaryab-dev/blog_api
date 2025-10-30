"""
Advanced SEO & Google Indexing System for Maximum Ranking
Implements cutting-edge SEO techniques for top search engine visibility
"""

import requests
import json
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib


class GoogleIndexingAPI:
    """Google Indexing API integration for instant indexing"""
    
    def __init__(self):
        self.api_url = "https://indexing.googleapis.com/v3/urlNotifications:publish"
        self.service_account_file = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_FILE', None)
    
    def notify_google(self, url, action='URL_UPDATED'):
        """
        Notify Google of URL updates for instant indexing
        Actions: URL_UPDATED, URL_DELETED
        """
        if not self.service_account_file:
            return {'success': False, 'error': 'Service account not configured'}
        
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/indexing']
            )
            credentials.refresh(Request())
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials.token}'
            }
            
            payload = {
                'url': url,
                'type': action
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            return {'success': response.status_code == 200, 'response': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class IndexNowAPI:
    """IndexNow API for instant indexing across multiple search engines"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'INDEXNOW_KEY', '')
        self.host = getattr(settings, 'SITE_URL', '').replace('https://', '').replace('http://', '')
    
    def submit_url(self, url):
        """Submit URL to IndexNow for instant indexing"""
        if not self.api_key:
            return {'success': False, 'error': 'IndexNow key not configured'}
        
        endpoints = [
            'https://api.indexnow.org/indexnow',
            'https://www.bing.com/indexnow',
            'https://yandex.com/indexnow'
        ]
        
        payload = {
            'host': self.host,
            'key': self.api_key,
            'keyLocation': f"https://{self.host}/{self.api_key}.txt",
            'urlList': [url]
        }
        
        results = []
        for endpoint in endpoints:
            try:
                response = requests.post(endpoint, json=payload, timeout=10)
                results.append({
                    'endpoint': endpoint,
                    'success': response.status_code in [200, 202],
                    'status': response.status_code
                })
            except Exception as e:
                results.append({'endpoint': endpoint, 'success': False, 'error': str(e)})
        
        return {'success': any(r['success'] for r in results), 'results': results}
    
    def submit_bulk(self, urls):
        """Submit multiple URLs at once"""
        if not self.api_key or not urls:
            return {'success': False}
        
        payload = {
            'host': self.host,
            'key': self.api_key,
            'keyLocation': f"https://{self.host}/{self.api_key}.txt",
            'urlList': urls[:10000]  # Max 10,000 URLs
        }
        
        try:
            response = requests.post('https://api.indexnow.org/indexnow', json=payload, timeout=30)
            return {'success': response.status_code in [200, 202], 'count': len(urls)}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class StructuredDataGenerator:
    """Generate advanced Schema.org structured data for rich snippets"""
    
    @staticmethod
    def generate_article_schema(post):
        """Generate Article schema with all SEO enhancements"""
        site_url = getattr(settings, 'SITE_URL', 'https://example.com')
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.title,
            "description": post.seo_description or post.summary,
            "image": {
                "@type": "ImageObject",
                "url": post.og_image or (post.featured_image.file if post.featured_image else ''),
                "width": 1200,
                "height": 630
            },
            "datePublished": post.published_at.isoformat() if post.published_at else post.created_at.isoformat(),
            "dateModified": post.updated_at.isoformat() if post.updated_at else post.created_at.isoformat(),
            "author": {
                "@type": "Person",
                "name": post.author.name,
                "url": f"{site_url}/authors/{post.author.slug}/",
                "description": post.author.bio
            },
            "publisher": {
                "@type": "Organization",
                "name": getattr(settings, 'SITE_NAME', 'Blog'),
                "url": site_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{site_url}/static/images/logo.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{site_url}/blog/{post.slug}/"
            },
            "articleSection": [cat.name for cat in post.categories.all()],
            "keywords": [tag.name for tag in post.tags.all()],
            "wordCount": post.word_count,
            "timeRequired": f"PT{post.reading_time}M",
            "inLanguage": "en-US",
            "isAccessibleForFree": True
        }
        
        return schema
    
    @staticmethod
    def generate_breadcrumb_schema(post):
        """Generate BreadcrumbList schema for navigation"""
        site_url = getattr(settings, 'SITE_URL', 'https://example.com')
        
        items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{site_url}/blog/"},
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
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
    
    @staticmethod
    def generate_faq_schema(faqs):
        """Generate FAQ schema for Q&A content"""
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq['answer']
                    }
                }
                for faq in faqs
            ]
        }


class SEOPerformanceOptimizer:
    """Advanced SEO performance optimization techniques"""
    
    @staticmethod
    def generate_critical_css(post):
        """Generate critical CSS for above-the-fold content"""
        return """
        <style>
        body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
        .post-header{padding:2rem 1rem;max-width:800px;margin:0 auto}
        .post-title{font-size:2.5rem;font-weight:700;line-height:1.2;margin:0 0 1rem}
        .post-meta{color:#666;font-size:0.9rem}
        .post-image{width:100%;height:auto;display:block}
        </style>
        """
    
    @staticmethod
    def generate_preload_hints(post):
        """Generate resource hints for faster loading"""
        hints = []
        
        if post.featured_image:
            hints.append(f'<link rel="preload" as="image" href="{post.featured_image.file}">')
        
        hints.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
        hints.append('<link rel="dns-prefetch" href="https://www.google-analytics.com">')
        
        return '\n'.join(hints)
    
    @staticmethod
    def calculate_content_quality_score(post):
        """Calculate content quality score for SEO"""
        score = 0
        
        # Word count (optimal: 1500-2500 words)
        if 1500 <= post.word_count <= 2500:
            score += 30
        elif post.word_count >= 1000:
            score += 20
        
        # Has featured image
        if post.featured_image:
            score += 15
        
        # Has categories and tags
        if post.categories.count() > 0:
            score += 10
        if post.tags.count() >= 3:
            score += 10
        
        # SEO fields filled
        if post.seo_title and post.seo_description:
            score += 15
        
        # Has internal links (check content)
        if post.content_html and 'href=' in post.content_html:
            score += 10
        
        # Reading time appropriate
        if 5 <= post.reading_time <= 15:
            score += 10
        
        return min(score, 100)


class LinkBuildingHelper:
    """Internal linking and link building optimization"""
    
    @staticmethod
    def suggest_internal_links(post, limit=5):
        """Suggest related posts for internal linking"""
        from blog.models import Post
        
        # Find related posts by tags and categories
        related = Post.published.filter(
            models.Q(tags__in=post.tags.all()) | 
            models.Q(categories__in=post.categories.all())
        ).exclude(id=post.id).distinct()[:limit]
        
        return [
            {
                'title': p.title,
                'url': f"/blog/{p.slug}/",
                'relevance': 'high' if p.tags.filter(id__in=post.tags.all()).exists() else 'medium'
            }
            for p in related
        ]
    
    @staticmethod
    def generate_related_posts_schema(post, related_posts):
        """Generate schema for related posts"""
        site_url = getattr(settings, 'SITE_URL', 'https://example.com')
        
        return {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": f"{site_url}/blog/{p.slug}/"
                }
                for i, p in enumerate(related_posts)
            ]
        }


def submit_to_search_engines(post_url):
    """Submit URL to all major search engines"""
    results = {}
    
    # Google Indexing API
    google_api = GoogleIndexingAPI()
    results['google'] = google_api.notify_google(post_url)
    
    # IndexNow (Bing, Yandex, etc.)
    indexnow = IndexNowAPI()
    results['indexnow'] = indexnow.submit_url(post_url)
    
    # Cache result
    cache_key = f"indexing_result_{hashlib.md5(post_url.encode()).hexdigest()}"
    cache.set(cache_key, results, 3600)
    
    return results
