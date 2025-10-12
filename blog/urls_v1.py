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
from .views_analytics_summary import AnalyticsSummaryView
from .views_upload import upload_image as ckeditor_upload_image
from .views_image_upload import upload_image
from .views_carousel import HomeCarouselListView
from .feeds import LatestPostsFeed
from .sitemaps import sitemaps

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Core API
    path('', include(router.urls)),
    path('search/', SearchView.as_view(), name='search-v1'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe-v1'),
    
    # Image Upload
    path('images/upload/', upload_image, name='image-upload-v1'),
    
    # CKEditor Upload (legacy)
    path('upload-image/', ckeditor_upload_image, name='upload-image-v1'),
    
    # Homepage Carousel
    path('homepage/carousel/', HomeCarouselListView.as_view(), name='homepage-carousel-v1'),
    
    # Analytics
    path('track-view/', track_view, name='track-view-v1'),
    path('trending/', TrendingPostsView.as_view(), name='trending-v1'),
    path('popular-searches/', PopularSearchesView.as_view(), name='popular-searches-v1'),
    path('analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary-v1'),
    
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap-v1'),
    path('rss.xml', LatestPostsFeed(), name='rss-v1'),
    path('robots.txt', robots_txt, name='robots-v1'),
    
    # Webhooks & Monitoring
    path('revalidate/', revalidate_webhook, name='revalidate-v1'),
    path('healthcheck/', healthcheck, name='healthcheck-v1'),
    
    # Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema-v1'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger-ui-v1'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v1'), name='redoc-v1'),
]
