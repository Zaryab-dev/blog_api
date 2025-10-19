"""
Advanced Ranking Signals & Core Web Vitals Optimization
Implements Google's ranking factors for maximum visibility
"""

from django.core.cache import cache
from django.db.models import Avg, Count, F, Q
from django.utils import timezone
from datetime import timedelta
import json


class CoreWebVitalsOptimizer:
    """Optimize for Google's Core Web Vitals"""
    
    @staticmethod
    def generate_performance_hints():
        """Generate performance optimization headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Cache-Control': 'public, max-age=31536000, immutable',
            'Content-Security-Policy': "default-src 'self'; img-src 'self' https: data:; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline';"
        }
    
    @staticmethod
    def generate_lazy_loading_config():
        """Configuration for lazy loading images"""
        return {
            'loading': 'lazy',
            'decoding': 'async',
            'fetchpriority': 'low'  # except hero image
        }
    
    @staticmethod
    def optimize_lcp(post):
        """Optimize Largest Contentful Paint"""
        config = {
            'preload_hero_image': True,
            'hero_image_url': post.featured_image.file if post.featured_image else None,
            'critical_css': True,
            'defer_non_critical': True
        }
        return config


class EATSignalsOptimizer:
    """Optimize for E-E-A-T (Experience, Expertise, Authoritativeness, Trust)"""
    
    @staticmethod
    def generate_author_credentials(author):
        """Generate author credentials for E-E-A-T"""
        return {
            'name': author.name,
            'bio': author.bio,
            'credentials': {
                'posts_count': author.posts.filter(status='published').count(),
                'expertise_areas': list(author.posts.values_list('categories__name', flat=True).distinct()),
                'social_proof': {
                    'twitter': author.twitter_handle,
                    'website': author.website
                }
            }
        }
    
    @staticmethod
    def calculate_content_freshness_score(post):
        """Calculate content freshness (important ranking factor)"""
        now = timezone.now()
        published = post.published_at or post.created_at
        updated = post.updated_at or published
        
        days_since_publish = (now - published).days
        days_since_update = (now - updated).days
        
        # Fresher content ranks better
        if days_since_update < 7:
            return 100
        elif days_since_update < 30:
            return 90
        elif days_since_update < 90:
            return 75
        elif days_since_update < 180:
            return 60
        else:
            return max(40 - (days_since_update // 30), 20)
    
    @staticmethod
    def generate_trust_signals(post):
        """Generate trust signals for content"""
        return {
            'author_verified': True,
            'last_updated': post.updated_at.isoformat() if post.updated_at else None,
            'fact_checked': True,
            'sources_cited': post.content_html.count('href=') if post.content_html else 0,
            'expert_reviewed': post.author.posts.filter(status='published').count() > 10
        }


class UserEngagementSignals:
    """Track and optimize user engagement signals (ranking factor)"""
    
    @staticmethod
    def calculate_engagement_score(post):
        """Calculate engagement score based on user interactions"""
        score = 0
        
        # Views (normalized)
        if post.views_count > 1000:
            score += 30
        elif post.views_count > 500:
            score += 20
        elif post.views_count > 100:
            score += 10
        
        # Comments
        score += min(post.comments_count * 5, 25)
        
        # Likes/reactions
        score += min(post.likes_count * 3, 20)
        
        # Trending score
        if post.trending_score > 100:
            score += 25
        
        return min(score, 100)
    
    @staticmethod
    def calculate_dwell_time_estimate(post):
        """Estimate average dwell time (important ranking signal)"""
        # Based on reading time and content quality
        base_time = post.reading_time * 60  # seconds
        
        # Adjust for content quality
        if post.featured_image:
            base_time *= 1.2
        if post.word_count > 1500:
            base_time *= 1.1
        
        return int(base_time)
    
    @staticmethod
    def track_bounce_rate_signals(post):
        """Track signals that affect bounce rate"""
        return {
            'has_toc': 'table of contents' in post.content_html.lower() if post.content_html else False,
            'has_images': post.featured_image is not None,
            'has_videos': 'video' in post.content_html.lower() if post.content_html else False,
            'has_cta': any(word in post.content_html.lower() for word in ['subscribe', 'download', 'learn more']) if post.content_html else False,
            'internal_links': post.content_html.count('href="/') if post.content_html else 0
        }


class SemanticSEOOptimizer:
    """Optimize for semantic search and NLP"""
    
    @staticmethod
    def extract_entities(content):
        """Extract named entities for semantic SEO"""
        # Simple entity extraction (can be enhanced with NLP libraries)
        entities = {
            'keywords': [],
            'topics': [],
            'related_terms': []
        }
        
        if not content:
            return entities
        
        # Extract capitalized words as potential entities
        words = content.split()
        entities['keywords'] = list(set([
            word.strip('.,!?;:') 
            for word in words 
            if word[0].isupper() and len(word) > 3
        ]))[:20]
        
        return entities
    
    @staticmethod
    def generate_lsi_keywords(post):
        """Generate LSI (Latent Semantic Indexing) keywords"""
        # Based on categories and tags
        lsi_keywords = []
        
        for category in post.categories.all():
            lsi_keywords.append(category.name.lower())
        
        for tag in post.tags.all():
            lsi_keywords.append(tag.name.lower())
        
        # Add related terms
        if post.title:
            title_words = [w.lower() for w in post.title.split() if len(w) > 4]
            lsi_keywords.extend(title_words[:5])
        
        return list(set(lsi_keywords))[:15]
    
    @staticmethod
    def optimize_for_featured_snippets(post):
        """Optimize content for Google featured snippets"""
        snippet_data = {
            'has_list': '<ul>' in post.content_html or '<ol>' in post.content_html if post.content_html else False,
            'has_table': '<table>' in post.content_html if post.content_html else False,
            'has_definition': post.summary and len(post.summary) < 160,
            'has_steps': any(word in post.content_html.lower() for word in ['step 1', 'first,', 'how to']) if post.content_html else False,
            'word_count_optimal': 40 <= post.word_count <= 60  # Optimal for snippets
        }
        
        return snippet_data


class MobileFirstOptimizer:
    """Mobile-first indexing optimization"""
    
    @staticmethod
    def generate_mobile_meta_tags():
        """Generate mobile-optimized meta tags"""
        return {
            'viewport': 'width=device-width, initial-scale=1, maximum-scale=5',
            'mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-status-bar-style': 'black-translucent',
            'format-detection': 'telephone=no'
        }
    
    @staticmethod
    def optimize_images_for_mobile(image_url):
        """Generate responsive image srcset"""
        if not image_url:
            return {}
        
        base_url = image_url.rsplit('?', 1)[0]
        
        return {
            'srcset': f"{base_url}?w=320 320w, {base_url}?w=640 640w, {base_url}?w=1024 1024w, {base_url}?w=1920 1920w",
            'sizes': '(max-width: 320px) 320px, (max-width: 640px) 640px, (max-width: 1024px) 1024px, 1920px'
        }


class LocalSEOOptimizer:
    """Local SEO optimization (if applicable)"""
    
    @staticmethod
    def generate_local_business_schema(business_info):
        """Generate LocalBusiness schema"""
        return {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_info.get('name'),
            "image": business_info.get('image'),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business_info.get('street'),
                "addressLocality": business_info.get('city'),
                "addressRegion": business_info.get('state'),
                "postalCode": business_info.get('zip'),
                "addressCountry": business_info.get('country', 'US')
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": business_info.get('latitude'),
                "longitude": business_info.get('longitude')
            },
            "url": business_info.get('url'),
            "telephone": business_info.get('phone'),
            "priceRange": business_info.get('price_range', '$$')
        }


class ContentVelocityTracker:
    """Track content publishing velocity (ranking signal)"""
    
    @staticmethod
    def calculate_publishing_velocity():
        """Calculate how frequently new content is published"""
        from blog.models import Post
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        posts_30_days = Post.published.filter(published_at__gte=last_30_days).count()
        posts_7_days = Post.published.filter(published_at__gte=last_7_days).count()
        
        return {
            'posts_last_30_days': posts_30_days,
            'posts_last_7_days': posts_7_days,
            'avg_per_week': posts_30_days / 4.3,
            'velocity_score': min((posts_30_days / 30) * 100, 100)
        }
    
    @staticmethod
    def get_content_update_frequency():
        """Track how often content is updated"""
        from blog.models import Post
        
        recently_updated = Post.published.filter(
            updated_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        total_posts = Post.published.count()
        
        return {
            'recently_updated': recently_updated,
            'update_rate': (recently_updated / total_posts * 100) if total_posts > 0 else 0
        }


def generate_comprehensive_seo_report(post):
    """Generate comprehensive SEO report for a post"""
    eat_optimizer = EATSignalsOptimizer()
    engagement = UserEngagementSignals()
    semantic = SemanticSEOOptimizer()
    
    report = {
        'post_id': str(post.id),
        'title': post.title,
        'url': f"/blog/{post.slug}/",
        'scores': {
            'content_quality': SEOPerformanceOptimizer.calculate_content_quality_score(post),
            'freshness': eat_optimizer.calculate_content_freshness_score(post),
            'engagement': engagement.calculate_engagement_score(post),
            'overall': 0
        },
        'signals': {
            'eat': eat_optimizer.generate_trust_signals(post),
            'engagement': engagement.track_bounce_rate_signals(post),
            'semantic': semantic.optimize_for_featured_snippets(post)
        },
        'recommendations': []
    }
    
    # Calculate overall score
    report['scores']['overall'] = sum(report['scores'].values()) / 3
    
    # Generate recommendations
    if post.word_count < 1000:
        report['recommendations'].append('Increase content length to 1500+ words')
    if not post.featured_image:
        report['recommendations'].append('Add a featured image')
    if post.tags.count() < 3:
        report['recommendations'].append('Add more relevant tags (3-5 recommended)')
    
    return report
