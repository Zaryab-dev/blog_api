from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from blog.models import Author, Category, Tag, Post, ImageAsset, Comment, Subscriber, SiteSettings, Redirect
from blog.utils import generate_slug, estimate_reading_time, count_words, get_canonical_url


class AuthorModelTest(TestCase):
    def test_author_creation(self):
        author = Author.objects.create(name="John Doe", bio="Test bio")
        self.assertEqual(author.name, "John Doe")
        self.assertEqual(author.slug, "john-doe")
    
    def test_slug_auto_generation(self):
        author = Author.objects.create(name="Jane Smith")
        self.assertEqual(author.slug, "jane-smith")
    
    def test_slug_uniqueness(self):
        Author.objects.create(name="Test Author", slug="test-author")
        author2 = Author.objects.create(name="Test Author 2", slug="test-author-2")
        self.assertNotEqual(author2.slug, "test-author")


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Leather Jackets")
        self.assertEqual(category.name, "Leather Jackets")
        self.assertEqual(category.slug, "leather-jackets")
        self.assertEqual(category.count_published_posts, 0)
    
    def test_slug_generation(self):
        category = Category.objects.create(name="Men's Fashion")
        self.assertEqual(category.slug, "mens-fashion")


class TagModelTest(TestCase):
    def test_tag_creation(self):
        tag = Tag.objects.create(name="Bomber")
        self.assertEqual(tag.name, "Bomber")
        self.assertEqual(tag.slug, "bomber")


class PostModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.category = Category.objects.create(name="Test Category")
        self.tag = Tag.objects.create(name="Test Tag")
    
    def test_post_creation(self):
        post = Post.objects.create(
            title="Test Post",
            summary="Test summary",
            content_html="<p>Test content</p>",
            author=self.author,
            status='draft'
        )
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.slug, "test-post")
        self.assertEqual(post.status, 'draft')
        self.assertFalse(post.is_published)
    
    def test_slug_uniqueness(self):
        Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author
        )
        post2 = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author
        )
        self.assertEqual(post2.slug, "test-post-1")
    
    def test_reading_time_calculation(self):
        content = " ".join(["word"] * 500)  # 500 words
        post = Post.objects.create(
            title="Long Post",
            summary="Summary",
            content_html=f"<p>{content}</p>",
            author=self.author
        )
        self.assertEqual(post.reading_time, 2)  # 500 words / 250 = 2 minutes
    
    def test_word_count_calculation(self):
        content = " ".join(["word"] * 100)
        post = Post.objects.create(
            title="Post",
            summary="Summary",
            content_html=f"<p>{content}</p>",
            author=self.author
        )
        self.assertEqual(post.word_count, 100)
    
    def test_published_at_auto_set(self):
        post = Post.objects.create(
            title="Published Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published'
        )
        self.assertIsNotNone(post.published_at)
        self.assertTrue(post.is_published)
    
    def test_published_manager(self):
        # Create draft post
        Post.objects.create(
            title="Draft Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='draft'
        )
        # Create published post
        Post.objects.create(
            title="Published Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.published.count(), 1)
    
    def test_legacy_urls_create_redirects(self):
        post = Post.objects.create(
            title="Post with Legacy URLs",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            legacy_urls=["/old-url-1/", "/old-url-2/"]
        )
        
        self.assertEqual(Redirect.objects.filter(to_url__contains=post.slug).count(), 2)


class ImageAssetModelTest(TestCase):
    def test_image_creation(self):
        image = ImageAsset.objects.create(
            alt_text="Test Image",
            width=1600,
            height=900,
            format='webp'
        )
        self.assertEqual(image.alt_text, "Test Image")
        self.assertEqual(image.width, 1600)


class CommentModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author
        )
    
    def test_comment_creation(self):
        comment = Comment.objects.create(
            post=self.post,
            name="Commenter",
            email="test@example.com",
            content="Great post!",
            status='pending'
        )
        self.assertEqual(comment.status, 'pending')
        self.assertEqual(comment.post, self.post)
    
    def test_comment_approval_invalidates_cache(self):
        cache.set(f"post:{self.post.slug}", "cached_data")
        comment = Comment.objects.create(
            post=self.post,
            name="Commenter",
            email="test@example.com",
            content="Great post!",
            status='pending'
        )
        comment.status = 'approved'
        comment.save()
        
        # Cache should be invalidated
        self.assertIsNone(cache.get(f"post:{self.post.slug}"))


class SubscriberModelTest(TestCase):
    def test_subscriber_creation(self):
        subscriber = Subscriber.objects.create(email="test@example.com")
        self.assertEqual(subscriber.email, "test@example.com")
        self.assertFalse(subscriber.verified)
    
    def test_email_uniqueness(self):
        Subscriber.objects.create(email="test@example.com")
        with self.assertRaises(Exception):
            Subscriber.objects.create(email="test@example.com")


class SiteSettingsModelTest(TestCase):
    def test_singleton_pattern(self):
        settings1 = SiteSettings.objects.create(
            site_name="Test Site",
            site_description="Description",
            site_url="https://example.com",
            default_meta_image="https://example.com/image.jpg",
            sitemap_index_url="https://example.com/sitemap.xml",
            rss_feed_url="https://example.com/rss.xml"
        )
        settings2 = SiteSettings.objects.create(
            site_name="Test Site 2",
            site_description="Description 2",
            site_url="https://example2.com",
            default_meta_image="https://example2.com/image.jpg",
            sitemap_index_url="https://example2.com/sitemap.xml",
            rss_feed_url="https://example2.com/rss.xml"
        )
        
        # Should only have one instance
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(settings2.site_name, "Test Site 2")
    
    def test_load_method(self):
        settings = SiteSettings.load()
        self.assertIsNotNone(settings)
        self.assertEqual(settings.pk, 1)


class RedirectModelTest(TestCase):
    def test_redirect_creation(self):
        redirect = Redirect.objects.create(
            from_path="/old-path/",
            to_url="https://example.com/new-path/",
            status_code=301,
            active=True
        )
        self.assertEqual(redirect.from_path, "/old-path/")
        self.assertEqual(redirect.status_code, 301)
        self.assertTrue(redirect.active)


class UtilsTest(TestCase):
    def test_generate_slug(self):
        slug = generate_slug("Test Post Title")
        self.assertEqual(slug, "test-post-title")
    
    def test_estimate_reading_time(self):
        content = "<p>" + " ".join(["word"] * 500) + "</p>"
        time = estimate_reading_time(content)
        self.assertEqual(time, 2)
    
    def test_count_words(self):
        content = "<p>" + " ".join(["word"] * 100) + "</p>"
        count = count_words(content)
        self.assertEqual(count, 100)
    
    def test_get_canonical_url(self):
        author = Author.objects.create(name="Test Author")
        post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=author
        )
        url = get_canonical_url(post)
        self.assertIn("/blog/test-post/", url)


class SignalsTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        cache.clear()
    
    def test_post_save_invalidates_cache(self):
        cache.set("posts:list:1", "cached_data")
        cache.set("posts:slugs:1", "cached_data")
        
        post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author
        )
        
        # Caches should be cleared
        self.assertIsNone(cache.get("posts:list:1"))
        self.assertIsNone(cache.get("posts:slugs:1"))
    
    def test_category_count_updates(self):
        category = Category.objects.create(name="Test Category")
        post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        post.categories.add(category)
        
        category.refresh_from_db()
        self.assertEqual(category.count_published_posts, 1)
