from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category, Tag, Author


class PostSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = "monthly"
    priority = 0.8
    protocol = 'https'
    
    def items(self):
        return Post.published.all()
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f'/blog/{obj.slug}/'
    
    def priority(self, obj):
        # Featured posts get higher priority
        if hasattr(obj, 'is_featured') and obj.is_featured:
            return 0.9
        return 0.8


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'
    
    def items(self):
        return Category.objects.filter(count_published_posts__gt=0)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f'/category/{obj.slug}/'


class TagSitemap(Sitemap):
    """Sitemap for tags"""
    changefreq = "weekly"
    priority = 0.5
    protocol = 'https'
    
    def items(self):
        return Tag.objects.filter(count_published_posts__gt=0)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f'/tag/{obj.slug}/'


class AuthorSitemap(Sitemap):
    """Sitemap for authors"""
    changefreq = "monthly"
    priority = 0.5
    protocol = 'https'
    
    def items(self):
        return Author.objects.filter(posts__status='published').distinct()
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f'/author/{obj.slug}/'


# Sitemap index
sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'authors': AuthorSitemap,
}
