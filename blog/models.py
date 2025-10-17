import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import EmailValidator
from django.contrib.postgres.indexes import GinIndex
from django_ckeditor_5.fields import CKEditor5Field
from blog.utils_sanitize import sanitize_html, calculate_reading_time, count_words
from blog.seo_auto_populate import auto_populate_seo


class TimeStampedModel(models.Model):
    """Abstract base model with timestamps"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublishedManager(models.Manager):
    """Manager for published content only"""
    def get_queryset(self):
        return super().get_queryset().filter(status='published', published_at__lte=timezone.now())


class Author(TimeStampedModel):
    """Content author with social links"""
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.URLField(max_length=500, blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    website = models.URLField(max_length=500, blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(TimeStampedModel):
    """Post category"""
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(max_length=500, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_image = models.URLField(max_length=500, blank=True)
    count_published_posts = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    """Post tag"""
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(max_length=500, blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_image = models.URLField(max_length=500, blank=True)
    count_published_posts = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ImageAsset(TimeStampedModel):
    """Image with responsive variants - Supabase Storage"""
    file = models.URLField(max_length=500)  # Supabase public URL
    alt_text = models.CharField(max_length=125)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    format = models.CharField(max_length=10, default='webp')
    responsive_set = models.JSONField(default=dict, blank=True)
    lqip = models.TextField(blank=True)  # Base64 LQIP
    og_image_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.alt_text or f"Image {self.id}"


class Post(TimeStampedModel):
    """Blog post with SEO fields"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    summary = models.CharField(max_length=320)
    content = CKEditor5Field('Content', config_name='extends', blank=True)
    content_html = models.TextField(editable=False)  # Sanitized HTML
    content_markdown = models.TextField(blank=True)
    
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    featured_image = models.ForeignKey(ImageAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    allow_index = models.BooleanField(default=True)
    
    reading_time = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    
    # Engagement metrics
    views_count = models.PositiveIntegerField(default=0, db_index=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    trending_score = models.FloatField(default=0, db_index=True)
    
    # SEO Fields
    seo_title = models.CharField(max_length=70, blank=True, help_text='SEO optimized title (max 70 chars)')
    seo_description = models.CharField(max_length=160, blank=True, help_text='SEO meta description (max 160 chars)')
    seo_keywords = models.CharField(max_length=255, blank=True, help_text='Comma-separated SEO keywords')
    canonical_url = models.URLField(max_length=500, blank=True, help_text='Canonical URL for this post')
    
    # Open Graph Fields
    og_title = models.CharField(max_length=70, blank=True, help_text='Open Graph title')
    og_description = models.CharField(max_length=200, blank=True, help_text='Open Graph description')
    og_image = models.URLField(max_length=500, blank=True, help_text='Open Graph image URL')
    og_type = models.CharField(max_length=20, default='article', help_text='Open Graph type')
    
    # Twitter Card Fields
    twitter_card = models.CharField(max_length=20, default='summary_large_image', help_text='Twitter card type')
    
    # Structured Data
    schema_org = models.JSONField(default=dict, blank=True, help_text='Custom schema.org JSON-LD data')
    
    # Sitemap Configuration
    sitemap_priority = models.DecimalField(max_digits=2, decimal_places=1, default=0.8, help_text='Sitemap priority (0.0-1.0)')
    sitemap_changefreq = models.CharField(
        max_length=10,
        default='monthly',
        choices=[
            ('always', 'Always'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('never', 'Never'),
        ],
        help_text='How frequently the page is likely to change'
    )
    last_crawled = models.DateTimeField(null=True, blank=True, help_text='Last time crawled by search engines')
    
    # Other Fields
    legacy_urls = models.JSONField(default=list, blank=True, help_text='Legacy URLs for redirects')
    product_references = models.JSONField(default=list, blank=True, help_text='Referenced product IDs')
    locale = models.CharField(max_length=5, default='en', help_text='Content locale')

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['-published_at']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_post_slug')
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Sanitize HTML content
        if self.content:
            self.content_html = sanitize_html(self.content)
            self.reading_time = calculate_reading_time(self.content_html)
            self.word_count = count_words(self.content_html)
        
        # Auto-populate SEO metadata
        auto_populate_seo(self)
        
        # Auto-set published_at on first publish
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == 'published' and self.published_at and self.published_at <= timezone.now()
    
    def update_trending_score(self):
        """Calculate trending score based on engagement metrics"""
        self.trending_score = (self.views_count * 0.6) + (self.likes_count * 0.3) + (self.comments_count * 0.1)
        self.save(update_fields=['trending_score'])
    
    def increment_views(self):
        """Increment view count and update trending score (async)"""
        from django.db.models import F
        Post.objects.filter(pk=self.pk).update(
            views_count=F('views_count') + 1,
            trending_score=(F('views_count') + 1) * 0.6 + F('likes_count') * 0.3 + F('comments_count') * 0.1
        )

    @property
    def computed_og_image(self):
        """
        Get the computed Open Graph image URL.

        Priority order:
        1. Manual og_image (if set and use_custom_og_image is True)
        2. Featured image URL (preferred for consistency)
        3. None (fallback)

        This ensures featured images are automatically used for SEO
        while still allowing manual override when needed.
        """
        # If we have a manual og_image and it's not empty, use it
        if self.og_image and self.og_image.strip():
            return self.og_image

        # Otherwise, use the featured image if available
        if self.featured_image and self.featured_image.file:
            # Prefer og_image_url if available (optimized for social sharing)
            if self.featured_image.og_image_url:
                return self.featured_image.og_image_url
            # Fallback to main image file
            return self.featured_image.file

        # No image available
        return None


class SEOMetadata(TimeStampedModel):
    """Extended SEO metadata (OneToOne with Post)"""
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='seo_metadata')
    meta_keywords = models.JSONField(default=list, blank=True)
    twitter_card = models.CharField(max_length=20, default='summary_large_image')
    twitter_creator = models.CharField(max_length=50, blank=True)
    facebook_app_id = models.CharField(max_length=50, blank=True)
    structured_data_extra = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'SEO Metadata'
        verbose_name_plural = 'SEO Metadata'

    def __str__(self):
        return f"SEO for {self.post.title}"


class Comment(TimeStampedModel):
    """Post comment with moderation"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('spam', 'Spam'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    content = models.TextField(max_length=1000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"


class Subscriber(TimeStampedModel):
    """Email subscriber"""
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    verified = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']
        indexes = [models.Index(fields=['email'])]

    def __str__(self):
        return self.email


class SiteSettings(models.Model):
    """Singleton site settings"""
    site_name = models.CharField(max_length=100, default='Zaryab Leather Blog')
    site_description = models.TextField(max_length=200)
    site_url = models.URLField(max_length=200)
    default_meta_image = models.URLField(max_length=500)
    default_title_template = models.CharField(max_length=100, default='{title} — {site_name}')
    default_description_template = models.CharField(max_length=200, blank=True)
    robots_txt_content = models.TextField(default='User-agent: *\nAllow: /')
    sitemap_index_url = models.URLField(max_length=200)
    rss_feed_url = models.URLField(max_length=200)
    google_site_verification = models.CharField(max_length=100, blank=True)
    twitter_site = models.CharField(max_length=50, blank=True)
    facebook_app_id = models.CharField(max_length=50, blank=True)
    
    # Store Configuration
    store_url = models.URLField(max_length=500, default='https://store.example.com', help_text='URL to your e-commerce store')
    store_name = models.CharField(max_length=100, default='Our Store', help_text='Name of your store')
    store_description = models.TextField(default='Premium products curated for you', help_text='Short description of your store')
    
    # Social Media Links
    twitter_url = models.URLField(max_length=500, blank=True, null=True, help_text='Twitter profile URL')
    facebook_url = models.URLField(max_length=500, blank=True, null=True, help_text='Facebook page URL')
    instagram_url = models.URLField(max_length=500, blank=True, null=True, help_text='Instagram profile URL')
    linkedin_url = models.URLField(max_length=500, blank=True, null=True, help_text='LinkedIn profile URL')
    github_url = models.URLField(max_length=500, blank=True, null=True, help_text='GitHub profile URL')
    youtube_url = models.URLField(max_length=500, blank=True, null=True, help_text='YouTube channel URL')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Redirect(TimeStampedModel):
    """URL redirect for legacy URLs"""
    from_path = models.CharField(max_length=500, unique=True, db_index=True)
    to_url = models.URLField(max_length=500)
    status_code = models.IntegerField(choices=[(301, '301 Permanent'), (302, '302 Temporary')], default=301)
    active = models.BooleanField(default=True, db_index=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['from_path', 'active']),
        ]

    def __str__(self):
        return f"{self.from_path} → {self.to_url}"


class SitemapGenerationLog(TimeStampedModel):
    """Track sitemap generation state and history"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_posts = models.IntegerField(default=0)
    total_files = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    s3_urls = models.JSONField(default=list, blank=True)  # List of uploaded sitemap URLs
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Sitemap generation {self.id} - {self.status}"
    
    @classmethod
    def get_latest(cls):
        """Get the most recent sitemap generation log"""
        return cls.objects.first()
    
    @classmethod
    def create_pending(cls):
        """Create a new pending sitemap generation task"""
        return cls.objects.create(status='pending')


class HomeCarousel(TimeStampedModel):
    """Homepage carousel/slider with hero images"""
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    image = models.ForeignKey(ImageAsset, on_delete=models.SET_NULL, null=True, related_name='carousel_images')
    cta_label = models.CharField(max_length=50, blank=True, help_text="Button text (e.g. 'Visit Store')")
    cta_url = models.URLField(max_length=500, blank=True, help_text="Destination URL for CTA button")
    position = models.PositiveIntegerField(default=0, help_text="Order of appearance", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    show_on_homepage = models.BooleanField(default=True)

    class Meta:
        ordering = ['position', '-created_at']
        verbose_name = 'Homepage Carousel'
        verbose_name_plural = 'Homepage Carousels'
        indexes = [
            models.Index(fields=['is_active', 'show_on_homepage', 'position']),
        ]

    def __str__(self):
        return self.title
