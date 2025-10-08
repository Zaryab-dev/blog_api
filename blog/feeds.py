from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from .models import Post


class LatestPostsFeed(Feed):
    """RSS feed for latest blog posts"""
    title = "Zaryab Leather Blog"
    link = "/blog/"
    description = "Latest articles on leather fashion, care, and style"
    feed_type = Atom1Feed
    
    def items(self):
        return Post.published.select_related('author').prefetch_related('categories')[:50]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.summary
    
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
        return f'/blog/{item.slug}/'
    
    def item_guid_is_permalink(self, item):
        return True
