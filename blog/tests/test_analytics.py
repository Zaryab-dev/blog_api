from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from datetime import timedelta
import hmac
import hashlib
import json

from blog.models import Post, Author, Category
from blog.models_analytics import PostView, SearchQueryLog, ReferrerLog, DailyMetrics


class AnalyticsModelsTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name='Test Author', slug='test-author')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            summary='Test summary',
            content_html='<p>Test content</p>',
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
    
    def test_post_view_creation(self):
        view = PostView.objects.create(
            post=self.post,
            ip_hash=PostView.hash_identifier('192.168.1.1'),
            user_agent_hash=PostView.hash_identifier('Mozilla/5.0'),
            referrer='https://google.com'
        )
        self.assertEqual(view.post, self.post)
        self.assertEqual(len(view.ip_hash), 64)  # SHA256 hash
    
    def test_search_query_log(self):
        log = SearchQueryLog.objects.create(
            query='django tutorial',
            results_count=10,
            clicked_post=self.post,
            ip_hash=PostView.hash_identifier('192.168.1.1')
        )
        self.assertEqual(log.query, 'django tutorial')
        self.assertEqual(log.results_count, 10)
    
    def test_referrer_log(self):
        ref = ReferrerLog.objects.create(
            post=self.post,
            referrer_url='https://google.com/search',
            referrer_domain='google.com',
            visit_count=5
        )
        self.assertEqual(ref.referrer_domain, 'google.com')
        self.assertEqual(ref.visit_count, 5)


class TrackViewAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name='Test Author', slug='test-author')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            summary='Test summary',
            content_html='<p>Test content</p>',
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
    
    def test_track_view_success(self):
        url = reverse('track-view')
        data = {'slug': 'test-post', 'referrer': 'https://google.com'}
        
        # Sign request
        payload = json.dumps(data)
        secret = 'test-secret'
        signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        
        with self.settings(ANALYTICS_SECRET='test-secret'):
            response = self.client.post(
                url,
                data,
                format='json',
                HTTP_X_SIGNATURE=signature
            )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'tracked')
        self.assertEqual(PostView.objects.count(), 1)
    
    def test_track_view_invalid_signature(self):
        url = reverse('track-view')
        data = {'slug': 'test-post'}
        
        with self.settings(ANALYTICS_SECRET='test-secret'):
            response = self.client.post(
                url,
                data,
                format='json',
                HTTP_X_SIGNATURE='invalid'
            )
        
        self.assertEqual(response.status_code, 403)
    
    def test_track_view_missing_slug(self):
        url = reverse('track-view')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_track_view_deduplication(self):
        url = reverse('track-view')
        data = {'slug': 'test-post'}
        
        # First request
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, 201)
        
        # Second request (should be deduplicated)
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['status'], 'already_counted')


class TrendingPostsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name='Test Author', slug='test-author')
        
        # Create posts
        self.post1 = Post.objects.create(
            title='Popular Post',
            slug='popular-post',
            summary='Summary',
            content_html='<p>Content</p>',
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        self.post2 = Post.objects.create(
            title='Less Popular Post',
            slug='less-popular',
            summary='Summary',
            content_html='<p>Content</p>',
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        
        # Create views
        for _ in range(10):
            PostView.objects.create(
                post=self.post1,
                ip_hash=PostView.hash_identifier(f'192.168.1.{_}'),
                user_agent_hash=PostView.hash_identifier('Mozilla/5.0')
            )
        
        for _ in range(3):
            PostView.objects.create(
                post=self.post2,
                ip_hash=PostView.hash_identifier(f'192.168.2.{_}'),
                user_agent_hash=PostView.hash_identifier('Mozilla/5.0')
            )
    
    def test_trending_posts(self):
        url = reverse('trending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        
        # Most popular post should be first
        results = response.data['results']
        if results:
            self.assertEqual(results[0]['slug'], 'popular-post')


class PopularSearchesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create search logs
        for _ in range(5):
            SearchQueryLog.objects.create(
                query='django tutorial',
                results_count=10,
                ip_hash=PostView.hash_identifier(f'192.168.1.{_}')
            )
        
        for _ in range(3):
            SearchQueryLog.objects.create(
                query='python tips',
                results_count=8,
                ip_hash=PostView.hash_identifier(f'192.168.2.{_}')
            )
    
    def test_popular_searches(self):
        url = reverse('popular-searches')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        
        # Most popular search should be first
        if response.data:
            self.assertEqual(response.data[0]['query'], 'django tutorial')
            self.assertEqual(response.data[0]['searches'], 5)


class DailyMetricsTaskTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name='Test Author', slug='test-author')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            summary='Summary',
            content_html='<p>Content</p>',
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        
        # Create yesterday's data
        yesterday = timezone.now() - timedelta(days=1)
        for i in range(5):
            view = PostView.objects.create(
                post=self.post,
                ip_hash=PostView.hash_identifier(f'192.168.1.{i}'),
                user_agent_hash=PostView.hash_identifier('Mozilla/5.0')
            )
            view.viewed_at = yesterday
            view.save()
    
    def test_aggregate_daily_metrics(self):
        from blog.tasks_analytics import aggregate_daily_metrics
        
        result = aggregate_daily_metrics()
        
        self.assertEqual(result['total_views'], 5)
        self.assertEqual(result['unique_visitors'], 5)
        
        # Check DailyMetrics created
        yesterday = (timezone.now() - timedelta(days=1)).date()
        metrics = DailyMetrics.objects.get(date=yesterday)
        self.assertEqual(metrics.total_views, 5)
