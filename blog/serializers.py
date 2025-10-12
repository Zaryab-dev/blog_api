from rest_framework import serializers
from .models import Post, Author, Category, Tag, Comment, Subscriber, ImageAsset, SEOMetadata, SiteSettings, Redirect, HomeCarousel
from .utils import get_canonical_url


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'slug', 'bio', 'avatar_url', 'twitter_handle', 'website']
    
    avatar_url = serializers.URLField(source='avatar', read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'count_published_posts']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'count_published_posts']


class ImageAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageAsset
        fields = ['url', 'width', 'height', 'alt', 'srcset', 'lqip', 'webp_url', 'og_image_url']
    
    url = serializers.SerializerMethodField()
    alt = serializers.CharField(source='alt_text')
    srcset = serializers.JSONField(source='responsive_set')
    webp_url = serializers.SerializerMethodField()
    
    def get_url(self, obj):
        # file is now a URLField (string), not ImageField
        return obj.file if obj.file else None
    
    def get_webp_url(self, obj):
        return self.get_url(obj)


class SEOSerializer(serializers.Serializer):
    """SEO metadata serializer"""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    meta_keywords = serializers.SerializerMethodField()
    meta_robots = serializers.SerializerMethodField()
    
    def get_title(self, obj):
        if obj.seo_title:
            return obj.seo_title
        site_name = getattr(self.context.get('site_settings'), 'site_name', 'Zaryab Leather Blog')
        return f"{obj.title} — {site_name}"
    
    def get_description(self, obj):
        return obj.seo_description or obj.summary
    
    def get_meta_keywords(self, obj):
        keywords = [tag.name for tag in obj.tags.all()]
        return keywords
    
    def get_meta_robots(self, obj):
        if not obj.allow_index:
            return "noindex, nofollow"
        return "index, follow"


class OpenGraphSerializer(serializers.Serializer):
    """Open Graph metadata serializer"""
    og_title = serializers.SerializerMethodField()
    og_description = serializers.SerializerMethodField()
    og_image = serializers.SerializerMethodField()
    og_image_width = serializers.IntegerField(default=1200)
    og_image_height = serializers.IntegerField(default=630)
    og_type = serializers.CharField(default='article')
    og_url = serializers.SerializerMethodField()
    
    def get_og_title(self, obj):
        return obj.og_title or obj.seo_title or obj.title
    
    def get_og_description(self, obj):
        return obj.og_description or obj.seo_description or obj.summary
    
    def get_og_image(self, obj):
        if obj.og_image:
            return obj.og_image
        if obj.featured_image:
            return obj.featured_image.og_image_url or obj.featured_image.file
        return None
    
    def get_og_url(self, obj):
        return get_canonical_url(obj)


class TwitterCardSerializer(serializers.Serializer):
    """Twitter Card metadata serializer"""
    card = serializers.CharField(default='summary_large_image')
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    site = serializers.CharField(default='@zaryableather')
    
    def get_title(self, obj):
        return obj.og_title or obj.seo_title or obj.title
    
    def get_description(self, obj):
        return obj.og_description or obj.seo_description or obj.summary
    
    def get_image(self, obj):
        if obj.og_image:
            return obj.og_image
        if obj.featured_image:
            return obj.featured_image.file
        return None
    
    def get_creator(self, obj):
        if obj.author.twitter_handle:
            return f"@{obj.author.twitter_handle}"
        return None


class PostSlugSerializer(serializers.ModelSerializer):
    """Minimal serializer for slug list endpoint"""
    class Meta:
        model = Post
        fields = ['slug', 'published_at', 'last_modified', 'canonical_url', 'status']
    
    last_modified = serializers.DateTimeField(source='updated_at')
    canonical_url = serializers.SerializerMethodField()
    
    def get_canonical_url(self, obj):
        return get_canonical_url(obj)


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list views"""
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'summary', 'featured_image',
            'author', 'categories', 'tags', 'published_at',
            'reading_time', 'canonical_url', 'views_count', 'likes_count', 'trending_score'
        ]
    
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image = ImageAssetSerializer(read_only=True)
    canonical_url = serializers.SerializerMethodField()
    views_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    trending_score = serializers.FloatField(read_only=True)
    
    def get_canonical_url(self, obj):
        return get_canonical_url(obj)


class PostDetailSerializer(serializers.ModelSerializer):
    """Full serializer for post detail view"""
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'summary', 'content_html', 'content_markdown',
            'author', 'categories', 'tags', 'featured_image',
            'seo', 'open_graph', 'twitter_card', 'schema_org',
            'published_at', 'last_modified', 'status', 'allow_index',
            'reading_time', 'word_count', 'canonical_url',
            'product_references', 'locale'
        ]
    
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image = ImageAssetSerializer(read_only=True)
    seo = serializers.SerializerMethodField()
    open_graph = serializers.SerializerMethodField()
    twitter_card = serializers.SerializerMethodField()
    last_modified = serializers.DateTimeField(source='updated_at')
    canonical_url = serializers.SerializerMethodField()
    
    def get_seo(self, obj):
        return SEOSerializer(obj, context=self.context).data
    
    def get_open_graph(self, obj):
        return OpenGraphSerializer(obj).data
    
    def get_twitter_card(self, obj):
        return TwitterCardSerializer(obj).data
    
    def get_canonical_url(self, obj):
        return get_canonical_url(obj)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'parent', 'name', 'email', 'content', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['id', 'email', 'verified', 'subscribed_at']
        read_only_fields = ['verified', 'subscribed_at']


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'site_description', 'site_url',
            'default_meta_image', 'default_title_template',
            'robots_txt_url', 'sitemap_index_url', 'rss_feed_url',
            'twitter_site', 'facebook_app_id'
        ]
    
    robots_txt_url = serializers.SerializerMethodField()
    
    def get_robots_txt_url(self, obj):
        return f"{obj.site_url}/robots.txt"


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ['from_path', 'to_url', 'status_code']


class HomeCarouselSerializer(serializers.ModelSerializer):
    """Serializer for homepage carousel with responsive images"""
    image = serializers.SerializerMethodField()

    class Meta:
        model = HomeCarousel
        fields = [
            'id', 'title', 'subtitle', 'description',
            'image', 'cta_label', 'cta_url',
            'position', 'is_active', 'show_on_homepage'
        ]
    
    def get_image(self, obj):
        if obj.image:
            return {
                'file': obj.image.file,
                'alt_text': obj.image.alt_text,
                'width': obj.image.width,
                'height': obj.image.height,
                'format': obj.image.format,
                'responsive_set': obj.image.responsive_set,
                'lqip': obj.image.lqip,
                'og_image_url': obj.image.og_image_url
            }
        return None
