from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.shortcuts import render
from django.conf import settings

from .models import Post, Category, Tag, Author, Comment, Subscriber
from .serializers import (
    PostListSerializer, PostDetailSerializer, CategorySerializer,
    TagSerializer, AuthorSerializer, CommentSerializer, SubscriberSerializer
)
from .search import PostSearchManager
from .pagination import StandardPagination
from .throttles import CommentRateThrottle
from .utils import generate_etag


def landing_page(request):
    """Landing page view"""
    site_url = getattr(settings, 'SITE_URL', request.build_absolute_uri('/').rstrip('/'))
    return render(request, 'landing.html', {'site_url': site_url})


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for blog posts
    
    list: GET /api/posts/ - List all published posts (paginated, filterable)
    retrieve: GET /api/posts/{slug}/ - Get single post by slug
    """
    queryset = Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags')
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['categories__slug', 'tags__slug', 'author__slug']
    ordering_fields = ['published_at', 'reading_time']
    ordering = ['-published_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search with validation
        search_query = self.request.query_params.get('search', '').strip()
        if search_query and len(search_query) >= 2:  # Minimum 2 characters
            queryset = PostSearchManager.search(queryset, search_query)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check cache first
        cache_key = f"post:{instance.slug}"
        cached_data = cache.get(cache_key)
        
        if not cached_data:
            serializer = self.get_serializer(instance)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, 3600)  # 1 hour
        
        # Increment view count asynchronously (non-blocking)
        instance.increment_views()
        
        # Check ETag for conditional request
        etag = generate_etag(instance)
        if request.META.get('HTTP_IF_NONE_MATCH') == etag:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        
        response = Response(cached_data)
        response['ETag'] = etag
        response['Last-Modified'] = instance.updated_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
        response['Cache-Control'] = 'public, max-age=3600, stale-while-revalidate=600'
        
        return response
    
    @method_decorator(cache_page(3600))
    @method_decorator(vary_on_headers('Accept'))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600, stale-while-revalidate=600'
        return response


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for categories
    
    list: GET /api/categories/ - List all categories with post counts
    retrieve: GET /api/categories/{slug}/ - Get single category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    @method_decorator(cache_page(3600))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for tags
    
    list: GET /api/tags/ - List all tags with post counts
    retrieve: GET /api/tags/{slug}/ - Get single tag
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    
    @method_decorator(cache_page(3600))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600'
        return response


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for authors
    
    list: GET /api/authors/ - List all authors
    retrieve: GET /api/authors/{slug}/ - Get single author
    posts: GET /api/authors/{slug}/posts/ - Get all posts by author
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        """Get all posts by this author"""
        author = self.get_object()
        posts = Post.published.filter(author=author).select_related('author', 'featured_image').prefetch_related('categories', 'tags')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @method_decorator(cache_page(3600))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600'
        return response


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments
    
    list: GET /api/comments/?post_slug={slug} - List approved comments for a post
    create: POST /api/comments/ - Create new comment (requires throttling)
    """
    serializer_class = CommentSerializer
    throttle_classes = [CommentRateThrottle]
    
    def get_queryset(self):
        queryset = Comment.objects.filter(status='approved')
        post_slug = self.request.query_params.get('post_slug')
        if post_slug:
            queryset = queryset.filter(post__slug=post_slug)
        return queryset.select_related('post')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # TODO: Send admin notification email (Celery task)
        # from .tasks import send_comment_notification
        # send_comment_notification.delay(serializer.instance.id)
        
        return Response(
            {'message': 'Comment submitted for moderation', 'id': serializer.instance.id},
            status=status.HTTP_201_CREATED
        )


class SearchView(generics.ListAPIView):
    """
    API endpoint for full-text search
    
    GET /api/search/?q={query} - Search posts by title, summary, content
    """
    serializer_class = PostListSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return Post.published.none()
        
        # Check cache
        cache_key = f"search:{query}"
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            return cached_results
        
        queryset = Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags')
        results = PostSearchManager.search(queryset, query)
        
        # Cache for 5 minutes
        cache.set(cache_key, results, 300)
        
        return results
    
    @method_decorator(cache_page(300))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=300'
        return response


class SubscribeView(generics.CreateAPIView):
    """
    API endpoint for email subscription
    
    POST /api/subscribe/ - Add new email subscriber
    """
    serializer_class = SubscriberSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if already subscribed
        email = serializer.validated_data['email']
        if Subscriber.objects.filter(email=email).exists():
            return Response(
                {'message': 'Email already subscribed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        
        # TODO: Send verification email (Celery task)
        # from .tasks import send_verification_email
        # send_verification_email.delay(serializer.instance.id)
        
        return Response(
            {'message': 'Subscription successful. Please check your email to verify.'},
            status=status.HTTP_201_CREATED
        )
