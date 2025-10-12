from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed
from django.conf import settings
from .models import Post, Category


class LatestPostsFeed(Feed):
    """Enhanced RSS/Atom feed for latest blog posts"""
    title = "Zaryab Leather Blog"
    link = "/blog/"
    description = "Latest articles on leather fashion, care, and style"
    feed_type = Atom1Feed
    language = 'en'
    
    def items(self):
        return Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags')[:50]
    
    def item_title(self, item):
        return item.seo_title or item.title
    
    def item_description(self, item):
        return item.seo_description or item.summary
    
    def item_link(self, item):
        return f'/blog/{item.slug}/'
    
    def item_pubdate(self, item):
        return item.published_at
    
    def item_updateddate(self, item):
        return item.updated_at
    
    def item_author_name(self, item):
        return item.author.name
    
    def item_author_email(self, item):
        # Only include if configured
        return None
    
    def item_categories(self, item):
        return [cat.name for cat in item.categories.all()]
    
    def item_guid(self, item):
        site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
        return f'{site_url}/blog/{item.slug}/'
    
    def item_guid_is_permalink(self, item):
        return True
    
    def item_enclosures(self, item):
        """Add featured image as enclosure"""
        if item.featured_image:
            from django.utils.feedgenerator import Enclosure
            return [Enclosure(
                url=item.featured_image.file,
                length=str(0),  # Unknown length
                mime_type='image/jpeg'
            )]
        return []


class RSSFeed(LatestPostsFeed):
    """RSS 2.0 feed"""
    feed_type = Rss201rev2Feed
    subtitle = LatestPostsFeed.description


class CategoryFeed(Feed):
    """RSS feed for specific category"""
    feed_type = Atom1Feed
    language = 'en'
    
    def get_object(self, request, slug):
        return Category.objects.get(slug=slug)
    
    def title(self, obj):
        return f"Zaryab Leather Blog - {obj.name}"
    
    def link(self, obj):
        return f'/category/{obj.slug}/'
    
    def description(self, obj):
        return obj.description or f"Latest posts in {obj.name}"
    
    def items(self, obj):
        return Post.published.filter(categories=obj).select_related('author', 'featured_image').prefetch_related('categories', 'tags')[:20]
    
    def item_title(self, item):
        return item.seo_title or item.title
    
    def item_description(self, item):
        return item.seo_description or item.summary
    
    def item_link(self, item):
        return f'/blog/{item.slug}/'
    
    def item_pubdate(self, item):
        return item.published_at
    
    def item_updateddate(self, item):
        return item.updated_at
    
    def item_author_name(self, item):
        return item.author.name
    
    def item_categories(self, item):
        return [cat.name for cat in item.categories.all()]
    
    def item_guid(self, item):
        site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
        return f'{site_url}/blog/{item.slug}/'
    
    def item_guid_is_permalink(self, item):
        return True
