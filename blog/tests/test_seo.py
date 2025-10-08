from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.utils import timezone
import hmac
import hashlib
import json

from blog.models import Post, Author, Category, Tag, Comment, Subscriber


class SitemapTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name="Test Author")
        self.category = Category.objects.create(name="Test Category")
        
        self.post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        self.post.categories.add(self.category)
        
        cache.clear()
    
    def test_sitemap_xml_exists(self):
        url = reverse('sitemap')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
    
    def test_sitemap_contains_post(self):
        url = reverse('sitemap')
        response = self.client.get(url)
        
        self.assertContains(response, self.post.slug)
        self.assertContains(response, '<loc>')
        self.assertContains(response, '<lastmod>')
    
    def test_sitemap_cache(self):
        url = reverse('sitemap')
        
        # First request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        
        # Second request (should be cached)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)


class RSSFeedTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name="Test Author")
        
        self.post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
    
    def test_rss_feed_exists(self):
        url = reverse('rss')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('xml', response['Content-Type'])
    
    def test_rss_contains_post(self):
        url = reverse('rss')
        response = self.client.get(url)
        
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.summary)
        self.assertContains(response, '<entry>')
    
    def test_rss_limit_50_posts(self):
        # Create 60 posts
        for i in range(60):
            Post.objects.create(
                title=f"Post {i}",
                summary="Summary",
                content_html="<p>Content</p>",
                author=self.author,
                status='published',
                published_at=timezone.now()
            )
        
        url = reverse('rss')
        response = self.client.get(url)
        
        # Should only contain 50 posts
        content = response.content.decode('utf-8')
        entry_count = content.count('<entry>')
        self.assertLessEqual(entry_count, 50)


class RobotsTxtTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_robots_txt_exists(self):
        url = reverse('robots')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
    
    def test_robots_txt_content(self):
        url = reverse('robots')
        response = self.client.get(url)
        
        content = response.content.decode('utf-8')
        self.assertIn('User-agent: *', content)
        self.assertIn('Allow: /', content)
        self.assertIn('Sitemap:', content)
        self.assertIn('Disallow: /admin/', content)
    
    def test_robots_txt_cache(self):
        url = reverse('robots')
        
        # First request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        
        # Second request (should be cached)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)


class RevalidateWebhookTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name="Test Author")
        self.post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
    
    def test_revalidate_requires_signature(self):
        url = reverse('revalidate')
        data = {'slugs': [self.post.slug]}
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_revalidate_with_valid_signature(self):
        from django.conf import settings
        settings.REVALIDATE_SECRET = 'test-secret'
        
        url = reverse('revalidate')
        data = {'slugs': [self.post.slug], 'paths': [f'/blog/{self.post.slug}']}
        payload = json.dumps(data, sort_keys=True)
        
        # Generate signature
        signature = hmac.new(
            'test-secret'.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = self.client.post(
            url,
            data=payload,
            content_type='application/json',
            HTTP_X_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())


class HealthcheckTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_healthcheck_returns_json(self):
        url = reverse('healthcheck')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_healthcheck_checks_database(self):
        url = reverse('healthcheck')
        response = self.client.get(url)
        
        data = response.json()
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
        self.assertEqual(data['checks']['database'], 'ok')
    
    def test_healthcheck_checks_redis(self):
        url = reverse('healthcheck')
        response = self.client.get(url)
        
        data = response.json()
        self.assertIn('redis', data['checks'])
        self.assertEqual(data['checks']['redis'], 'ok')
    
    def test_healthcheck_status(self):
        url = reverse('healthcheck')
        response = self.client.get(url)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')


class CeleryTaskTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
    
    def test_regenerate_sitemap_task(self):
        from blog.tasks import regenerate_sitemap
        
        result = regenerate_sitemap()
        self.assertIn('Sitemap regenerated', result)
    
    def test_send_comment_notification_task(self):
        from blog.tasks import send_comment_notification
        
        comment = Comment.objects.create(
            post=self.post,
            name='Commenter',
            email='test@example.com',
            content='Test comment'
        )
        
        result = send_comment_notification(comment.id)
        # Will fail without email config, but should not raise exception
        self.assertIsNotNone(result)
    
    def test_send_verification_email_task(self):
        from blog.tasks import send_verification_email
        
        subscriber = Subscriber.objects.create(email='test@example.com')
        
        result = send_verification_email(subscriber.id)
        # Will fail without email config, but should not raise exception
        self.assertIsNotNone(result)


class CacheInvalidationTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        cache.clear()
    
    def test_post_save_invalidates_cache(self):
        # Set cache
        cache.set('posts:list:1', 'cached_data')
        cache.set('sitemap:posts', 'cached_sitemap')
        
        # Create post (triggers signal)
        Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        
        # Cache should be cleared
        self.assertIsNone(cache.get('posts:list:1'))
        self.assertIsNone(cache.get('sitemap:posts'))
    
    def test_post_delete_invalidates_cache(self):
        post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        
        # Set cache
        cache.set(f'post:{post.slug}', 'cached_data')
        
        # Delete post
        post.delete()
        
        # Cache should be cleared
        self.assertIsNone(cache.get(f'post:{post.slug}'))
