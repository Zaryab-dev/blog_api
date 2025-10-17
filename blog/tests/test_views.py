from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from django.utils import timezone

from blog.models import Post, Author, Category, Tag, Comment, Subscriber
from blog.utils import generate_etag


class PostViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")
        self.category = Category.objects.create(name="Test Category")
        self.tag = Tag.objects.create(name="Test Tag")
        
        self.post = Post.objects.create(
            title="Test Post",
            summary="Test summary",
            content_html="<p>Test content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        self.post.categories.add(self.category)
        self.post.tags.add(self.tag)
        
        cache.clear()
    
    def test_list_posts(self):
        url = reverse('post-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Post')
    
    def test_retrieve_post(self):
        url = reverse('post-detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
        self.assertIn('seo', response.data)
        self.assertIn('open_graph', response.data)
        self.assertIn('ETag', response)
        self.assertIn('Last-Modified', response)
    
    def test_etag_conditional_request(self):
        url = reverse('post-detail', kwargs={'slug': self.post.slug})
        
        # First request
        response1 = self.client.get(url)
        etag = response1['ETag']
        
        # Second request with If-None-Match
        response2 = self.client.get(url, HTTP_IF_NONE_MATCH=etag)
        self.assertEqual(response2.status_code, status.HTTP_304_NOT_MODIFIED)
    
    def test_filter_by_category(self):
        url = reverse('post-list')
        response = self.client.get(url, {'categories__slug': self.category.slug})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_by_tag(self):
        url = reverse('post-list')
        response = self.client.get(url, {'tags__slug': self.tag.slug})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_by_author(self):
        url = reverse('post-list')
        response = self.client.get(url, {'author__slug': self.author.slug})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_pagination(self):
        # Create more posts
        for i in range(25):
            Post.objects.create(
                title=f"Post {i}",
                summary="Summary",
                content_html="<p>Content</p>",
                author=self.author,
                status='published',
                published_at=timezone.now()
            )
        
        url = reverse('post-list')
        response = self.client.get(url, {'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
    
    def test_cache_hit(self):
        url = reverse('post-detail', kwargs={'slug': self.post.slug})
        
        # First request (cache miss)
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second request (cache hit)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify cache was used
        cache_key = f"post:{self.post.slug}"
        self.assertIsNotNone(cache.get(cache_key))


class CategoryViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Test Category")
    
    def test_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')
    
    def test_retrieve_category(self):
        url = reverse('category-detail', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')


class TagViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tag = Tag.objects.create(name="Test Tag")
    
    def test_list_tags(self):
        url = reverse('tag-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Tag')


class AuthorViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")
    
    def test_list_authors(self):
        url = reverse('author-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Author')


class CommentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")
        self.post = Post.objects.create(
            title="Test Post",
            summary="Summary",
            content_html="<p>Content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
    
    def test_create_comment(self):
        url = reverse('comment-list')
        data = {
            'post': self.post.id,
            'name': 'Commenter',
            'email': 'test@example.com',
            'content': 'Great post!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        
        # Verify comment is pending
        comment = Comment.objects.get(id=response.data['id'])
        self.assertEqual(comment.status, 'pending')
    
    def test_list_approved_comments(self):
        Comment.objects.create(
            post=self.post,
            name='User',
            email='user@example.com',
            content='Comment',
            status='approved'
        )
        
        url = reverse('comment-list')
        response = self.client.get(url, {'post_slug': self.post.slug})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_throttling(self):
        url = reverse('comment-list')
        data = {
            'post': self.post.id,
            'name': 'Spammer',
            'email': 'spam@example.com',
            'content': 'Spam'
        }
        
        # Make 6 requests (limit is 5/min)
        for i in range(6):
            response = self.client.post(url, data)
            if i < 5:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            else:
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")
        
        self.post1 = Post.objects.create(
            title="Leather Jacket Care",
            summary="How to care for leather",
            content_html="<p>Leather jackets need special care</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        
        self.post2 = Post.objects.create(
            title="Best Bomber Jackets",
            summary="Top bomber styles",
            content_html="<p>Bomber jackets are classic</p>",
            author=self.author,
            status='published',
            published_at=timezone.now()
        )
        
        cache.clear()
    
    def test_search_by_title(self):
        url = reverse('search')
        response = self.client.get(url, {'q': 'leather'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_search_empty_query(self):
        url = reverse('search')
        response = self.client.get(url, {'q': ''})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_search_cache(self):
        url = reverse('search')
        
        # First request (cache miss)
        response1 = self.client.get(url, {'q': 'leather'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verify cache was set
        cache_key = "search:leather"
        self.assertIsNotNone(cache.get(cache_key))


class SubscribeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_subscribe_new_email(self):
        url = reverse('subscribe')
        data = {'email': 'newuser@example.com'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        
        # Verify subscriber created
        self.assertTrue(Subscriber.objects.filter(email='newuser@example.com').exists())
    
    def test_subscribe_duplicate_email(self):
        Subscriber.objects.create(email='existing@example.com')
        
        url = reverse('subscribe')
        data = {'email': 'existing@example.com'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PostOGImageAPITest(TestCase):
    """Test OG image auto-population in API responses"""

    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")

        # Create image asset
        self.image = ImageAsset.objects.create(
            alt_text="Test Image",
            file="https://supabase.co/storage/test.jpg",
            og_image_url="https://supabase.co/storage/og-test.jpg",
            width=1200,
            height=630
        )

        # Create post with featured image
        self.post = Post.objects.create(
            title="Test Post",
            summary="Test summary",
            content_html="<p>Test content</p>",
            author=self.author,
            status='published',
            published_at=timezone.now(),
            featured_image=self.image
        )

    def test_og_image_in_detail_response(self):
        """Test that OG image appears in post detail API response"""
        url = reverse('post-detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('seo', response.data)
        self.assertIn('open_graph', response.data['seo'])
        self.assertIn('og_image', response.data['seo']['open_graph'])

        # Should use the featured image's og_image_url
        self.assertEqual(
            response.data['seo']['open_graph']['og_image'],
            "https://supabase.co/storage/og-test.jpg"
        )

    def test_twitter_card_image_in_detail_response(self):
        """Test that Twitter Card image uses computed OG image"""
        url = reverse('post-detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('seo', response.data)
        self.assertIn('twitter_card', response.data['seo'])
        self.assertIn('image', response.data['seo']['twitter_card'])

        # Should use the same computed image
        self.assertEqual(
            response.data['seo']['twitter_card']['image'],
            "https://supabase.co/storage/og-test.jpg"
        )

    def test_manual_og_image_override_in_api(self):
        """Test that manual OG image takes precedence in API"""
        # Update post with manual og_image
        self.post.og_image = "https://custom-og.com/image.jpg"
        self.post.save()

        url = reverse('post-detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should use manual og_image
        self.assertEqual(
            response.data['seo']['open_graph']['og_image'],
            "https://custom-og.com/image.jpg"
        )
        self.assertIn('already subscribed', response.data['message'].lower())
    
    def test_subscribe_invalid_email(self):
        url = reverse('subscribe')
        data = {'email': 'invalid-email'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
