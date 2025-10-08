from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import (
    PostViewSet, CategoryViewSet, TagViewSet, AuthorViewSet,
    CommentViewSet, SearchView, SubscribeView
)
from .views_seo import robots_txt, revalidate_webhook, healthcheck
from .views_analytics import track_view, TrendingPostsView, PopularSearchesView
from .feeds import LatestPostsFeed
from .sitemaps import sitemaps

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'comments', CommentViewSet, basename='comment')

# V1 API (current)
urlpatterns = [
    path('v1/', include('blog.urls_v1')),
]

# Legacy redirects (backward compatibility)
from django.views.generic import RedirectView

legacy_redirects = [
    path('posts/', RedirectView.as_view(url='/api/v1/posts/', permanent=True)),
    path('posts/<slug:slug>/', RedirectView.as_view(url='/api/v1/posts/%(slug)s/', permanent=True)),
    path('categories/', RedirectView.as_view(url='/api/v1/categories/', permanent=True)),
    path('tags/', RedirectView.as_view(url='/api/v1/tags/', permanent=True)),
    path('authors/', RedirectView.as_view(url='/api/v1/authors/', permanent=True)),
    path('search/', RedirectView.as_view(url='/api/v1/search/', permanent=True)),
    path('trending/', RedirectView.as_view(url='/api/v1/trending/', permanent=True)),
    path('healthcheck/', RedirectView.as_view(url='/api/v1/healthcheck/', permanent=True)),
    path('docs/', RedirectView.as_view(url='/api/v1/docs/', permanent=True)),
]

urlpatterns += legacy_redirects
