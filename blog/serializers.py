from rest_framework import serializers
from .models import Post, Author, Category, Tag, Comment, Subscriber, ImageAsset, SEOMetadata, SiteSettings, Redirect, HomeCarousel
from .utils import get_canonical_url
from .seo_utils import (
    generate_schema_article,
    generate_schema_breadcrumb,
    generate_open_graph_data,
    generate_twitter_card_data,
    generate_meta_robots,
    get_canonical_url as get_seo_canonical_url
)


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
    """Enhanced SEO metadata serializer with comprehensive meta tags"""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    canonical_url = serializers.SerializerMethodField()
    meta_robots = serializers.SerializerMethodField()
    og_image = serializers.SerializerMethodField()
    published_time = serializers.SerializerMethodField()
    modified_time = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    locale = serializers.CharField(default='en')
    
    def get_title(self, obj):
        if obj.seo_title:
            return obj.seo_title
        from django.conf import settings
        site_name = getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog')
        return f"{obj.title} — {site_name}"
    
    def get_description(self, obj):
        return obj.seo_description or obj.summary
    
    def get_keywords(self, obj):
        if obj.seo_keywords:
            return obj.seo_keywords
        return ", ".join([tag.name for tag in obj.tags.all()])
    
    def get_canonical_url(self, obj):
        return get_seo_canonical_url(obj)
    
    def get_meta_robots(self, obj):
        return generate_meta_robots(obj)
    
    def get_og_image(self, obj):
        if obj.og_image:
            return obj.og_image
        if obj.featured_image:
            return obj.featured_image.og_image_url or obj.featured_image.file
        return None
    
    def get_published_time(self, obj):
        return obj.published_at.isoformat() if obj.published_at else None
    
    def get_modified_time(self, obj):
        return obj.updated_at.isoformat()
    
    def get_author_name(self, obj):
        return obj.author.name


class OpenGraphSerializer(serializers.Serializer):
    """Enhanced Open Graph metadata serializer with full OG protocol support"""
    og_type = serializers.SerializerMethodField()
    og_title = serializers.SerializerMethodField()
    og_description = serializers.SerializerMethodField()
    og_url = serializers.SerializerMethodField()
    og_site_name = serializers.SerializerMethodField()
    og_locale = serializers.SerializerMethodField()
    og_image = serializers.SerializerMethodField()
    og_image_width = serializers.SerializerMethodField()
    og_image_height = serializers.SerializerMethodField()
    article_published_time = serializers.SerializerMethodField()
    article_modified_time = serializers.SerializerMethodField()
    article_author = serializers.SerializerMethodField()
    article_section = serializers.SerializerMethodField()
    article_tag = serializers.SerializerMethodField()
    
    def get_og_type(self, obj):
        return obj.og_type or 'article'
    
    def get_og_title(self, obj):
        return obj.og_title or obj.seo_title or obj.title
    
    def get_og_description(self, obj):
        return obj.og_description or obj.seo_description or obj.summary
    
    def get_og_url(self, obj):
        return get_seo_canonical_url(obj)
    
    def get_og_site_name(self, obj):
        from django.conf import settings
        return getattr(settings, 'SITE_NAME', 'Zaryab Leather Blog')
    
    def get_og_locale(self, obj):
        return obj.locale or 'en_US'
    
    def get_og_image(self, obj):
        if obj.og_image:
            return obj.og_image
        if obj.featured_image:
            return obj.featured_image.og_image_url or obj.featured_image.file
        return None
    
    def get_og_image_width(self, obj):
        if obj.featured_image:
            return obj.featured_image.width
        return 1200
    
    def get_og_image_height(self, obj):
        if obj.featured_image:
            return obj.featured_image.height
        return 630
    
    def get_article_published_time(self, obj):
        return obj.published_at.isoformat() if obj.published_at else None
    
    def get_article_modified_time(self, obj):
        return obj.updated_at.isoformat()
    
    def get_article_author(self, obj):
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', 'https://zaryableather.com')
        return f"{site_url}/author/{obj.author.slug}/"
    
    def get_article_section(self, obj):
        if obj.categories.exists():
            return obj.categories.first().name
        return None
    
    def get_article_tag(self, obj):
        return [tag.name for tag in obj.tags.all()]


class TwitterCardSerializer(serializers.Serializer):
    """Enhanced Twitter Card metadata serializer"""
    card = serializers.SerializerMethodField()
    site = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    image_alt = serializers.SerializerMethodField()
    
    def get_card(self, obj):
        return obj.twitter_card or 'summary_large_image'
    
    def get_site(self, obj):
        from django.conf import settings
        return getattr(settings, 'TWITTER_SITE', '@zaryableather')
    
    def get_creator(self, obj):
        if obj.author.twitter_handle:
            handle = obj.author.twitter_handle.lstrip('@')
            return f"@{handle}"
        return None
    
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
    
    def get_image_alt(self, obj):
        if obj.featured_image:
            return obj.featured_image.alt_text
        return obj.title


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
    """Full serializer for post detail view with comprehensive SEO data"""
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'summary', 'content_html', 'content_markdown',
            'author', 'categories', 'tags', 'featured_image',
            'seo', 'open_graph', 'twitter_card', 'schema_org', 'breadcrumb',
            'published_at', 'last_modified', 'status', 'allow_index',
            'reading_time', 'word_count', 'canonical_url',
            'product_references', 'locale', 'views_count', 'likes_count'
        ]
    
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image = ImageAssetSerializer(read_only=True)
    seo = serializers.SerializerMethodField()
    open_graph = serializers.SerializerMethodField()
    twitter_card = serializers.SerializerMethodField()
    schema_org = serializers.SerializerMethodField()
    breadcrumb = serializers.SerializerMethodField()
    last_modified = serializers.DateTimeField(source='updated_at')
    canonical_url = serializers.SerializerMethodField()
    
    def get_seo(self, obj):
        return SEOSerializer(obj, context=self.context).data
    
    def get_open_graph(self, obj):
        return OpenGraphSerializer(obj).data
    
    def get_twitter_card(self, obj):
        return TwitterCardSerializer(obj).data
    
    def get_schema_org(self, obj):
        # Return custom schema if set, otherwise generate default
        if obj.schema_org:
            return obj.schema_org
        return generate_schema_article(obj)
    
    def get_breadcrumb(self, obj):
        return generate_schema_breadcrumb(obj)
    
    def get_canonical_url(self, obj):
        return get_seo_canonical_url(obj)


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
