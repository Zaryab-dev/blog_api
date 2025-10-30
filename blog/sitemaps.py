from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Post, Category, Tag, Author


class PostSitemap(Sitemap):
    """Enhanced sitemap for blog posts with dynamic priority and changefreq"""
    protocol = 'https'
    limit = 5000
    
    def items(self):
        return Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags').order_by('-published_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f'/blog/{obj.slug}/'
    
    def get_urls(self, page=1, site=None, protocol=None):
        urls = super().get_urls(page, site, protocol)
        for url_info in urls:
            obj = url_info.get('item')
            if obj and obj.featured_image:
                url_info['images'] = [{
                    'loc': obj.featured_image.file,
                    'title': obj.featured_image.alt_text or obj.title,
                }]
        return urls
    
    def changefreq(self, obj):
        # Use custom changefreq if set, otherwise calculate based on age
        if obj.sitemap_changefreq:
            return obj.sitemap_changefreq
        
        # Dynamic changefreq based on post age
        age = timezone.now() - obj.published_at if obj.published_at else timedelta(days=365)
        if age < timedelta(days=7):
            return 'daily'
        elif age < timedelta(days=30):
            return 'weekly'
        else:
            return 'monthly'
    
    def priority(self, obj):
        # Use custom priority if set
        if obj.sitemap_priority:
            return float(obj.sitemap_priority)
        
        # Dynamic priority based on engagement and recency
        base_priority = 0.8
        
        # Boost for recent posts
        if obj.published_at:
            age = timezone.now() - obj.published_at
            if age < timedelta(days=7):
                base_priority = 0.9
            elif age < timedelta(days=30):
                base_priority = 0.85
        
        # Boost for high engagement
        if obj.views_count > 1000:
            base_priority = min(1.0, base_priority + 0.1)
        
        return base_priority


class CategorySitemap(Sitemap):
    """Enhanced sitemap for categories"""
    changefreq = "weekly"
    protocol = 'https'
    
    def items(self):
        return Category.objects.filter(count_published_posts__gt=0).order_by('-count_published_posts')
    
    def lastmod(self, obj):
        # Get the latest post update in this category
        latest_post = Post.published.filter(categories=obj).order_by('-updated_at').first()
        return latest_post.updated_at if latest_post else obj.updated_at
    
    def location(self, obj):
        return f'/category/{obj.slug}/'
    
    def priority(self, obj):
        # Higher priority for categories with more posts
        if obj.count_published_posts > 20:
            return 0.7
        elif obj.count_published_posts > 10:
            return 0.6
        return 0.5


class TagSitemap(Sitemap):
    """Enhanced sitemap for tags"""
    changefreq = "weekly"
    protocol = 'https'
    
    def items(self):
        return Tag.objects.filter(count_published_posts__gt=0).order_by('-count_published_posts')
    
    def lastmod(self, obj):
        # Get the latest post update with this tag
        latest_post = Post.published.filter(tags=obj).order_by('-updated_at').first()
        return latest_post.updated_at if latest_post else obj.updated_at
    
    def location(self, obj):
        return f'/tag/{obj.slug}/'
    
    def priority(self, obj):
        # Higher priority for popular tags
        if obj.count_published_posts > 15:
            return 0.6
        elif obj.count_published_posts > 5:
            return 0.5
        return 0.4


class AuthorSitemap(Sitemap):
    """Enhanced sitemap for authors"""
    changefreq = "monthly"
    protocol = 'https'
    
    def items(self):
        return Author.objects.filter(posts__status='published').distinct().order_by('name')
    
    def lastmod(self, obj):
        # Get the latest post update by this author
        latest_post = Post.published.filter(author=obj).order_by('-updated_at').first()
        return latest_post.updated_at if latest_post else obj.updated_at
    
    def location(self, obj):
        return f'/author/{obj.slug}/'
    
    def priority(self, obj):
        # Higher priority for prolific authors
        post_count = Post.published.filter(author=obj).count()
        if post_count > 20:
            return 0.6
        elif post_count > 10:
            return 0.5
        return 0.4


class StaticPagesSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.7
    changefreq = 'monthly'
    protocol = 'https'
    
    def items(self):
        return ['home', 'blog', 'about', 'contact']
    
    def location(self, item):
        if item == 'home':
            return '/'
        return f'/{item}/'


# Sitemap index - all sitemaps available
sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'authors': AuthorSitemap,
    'static': StaticPagesSitemap,
}
