from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import (
    PostViewSet, CategoryViewSet, TagViewSet, AuthorViewSet,
    CommentViewSet, SearchView, SubscribeView
)
from .views_seo import robots_txt, revalidate_webhook, healthcheck
from .views_simple_health import simple_healthcheck
from .views_seo_api import (
    schema_endpoint,
    preview_endpoint,
    all_slugs_endpoint,
    ping_search_engines_endpoint,
    site_metadata_endpoint,
    google_verification,
    seo_health_check
)
from .views_seo_advanced import (
    google_verify,
    indexnow_submit,
    seo_status,
    reindex_post,
    indexnow_key_file
)
from .views_schema import (
    schema_post,
    schema_site,
    schema_author,
    schema_breadcrumbs
)
from .views_analytics import track_view, TrendingPostsView, PopularSearchesView
from .views_analytics_summary import AnalyticsSummaryView
from .views_upload import upload_image as ckeditor_upload_image
from .views_image_upload import upload_image
from .views_carousel import HomeCarouselListView
from .views_settings import site_settings
from .views_seo_ranking import (
    submit_url_to_google, submit_url_to_indexnow, bulk_submit_to_indexnow,
    get_structured_data, get_seo_score, get_core_web_vitals,
    get_eat_signals, get_semantic_keywords, get_engagement_metrics,
    auto_optimize_seo, seo_dashboard
)
from .feeds import LatestPostsFeed, RSSFeed, CategoryFeed
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
    path('settings/', site_settings, name='site-settings-v1'),
    
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
    
    # SEO - Sitemaps & Feeds
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap-v1'),
    path('rss/', LatestPostsFeed(), name='rss-atom-v1'),
    path('rss.xml', RSSFeed(), name='rss-v1'),
    path('feed/category/<slug:slug>/', CategoryFeed(), name='category-feed-v1'),
    path('robots.txt', robots_txt, name='robots-v1'),
    
    # SEO - API Endpoints
    path('seo/schema/<slug:slug>/', schema_endpoint, name='seo-schema-v1'),
    path('seo/preview/<slug:slug>/', preview_endpoint, name='seo-preview-v1'),
    path('seo/slugs/', all_slugs_endpoint, name='seo-slugs-v1'),
    path('seo/ping/', ping_search_engines_endpoint, name='seo-ping-v1'),
    path('seo/site/', site_metadata_endpoint, name='seo-site-v1'),
    path('seo/health/', seo_health_check, name='seo-health-v1'),
    path('google-verification.html', google_verification, name='google-verification-v1'),
    
    # SEO - Advanced Endpoints
    path('seo/google/verify/', google_verify, name='seo-google-verify-v1'),
    path('seo/indexnow/', indexnow_submit, name='seo-indexnow-v1'),
    path('seo/status/', seo_status, name='seo-status-v1'),
    path('seo/reindex/<slug:slug>/', reindex_post, name='seo-reindex-v1'),
    path('<str:key>.txt', indexnow_key_file, name='indexnow-key-v1'),
    
    # SEO Ranking & Indexing
    path('seo/submit-google/<slug:slug>/', submit_url_to_google, name='seo-submit-google-v1'),
    path('seo/submit-indexnow/<slug:slug>/', submit_url_to_indexnow, name='seo-submit-indexnow-v1'),
    path('seo/bulk-submit/', bulk_submit_to_indexnow, name='seo-bulk-submit-v1'),
    path('seo/structured-data/<slug:slug>/', get_structured_data, name='seo-structured-data-v1'),
    path('seo/score/<slug:slug>/', get_seo_score, name='seo-score-v1'),
    path('seo/core-web-vitals/<slug:slug>/', get_core_web_vitals, name='seo-cwv-v1'),
    path('seo/eat-signals/<slug:slug>/', get_eat_signals, name='seo-eat-v1'),
    path('seo/semantic/<slug:slug>/', get_semantic_keywords, name='seo-semantic-v1'),
    path('seo/engagement/<slug:slug>/', get_engagement_metrics, name='seo-engagement-v1'),
    path('seo/auto-optimize/<slug:slug>/', auto_optimize_seo, name='seo-auto-optimize-v1'),
    path('seo/dashboard/', seo_dashboard, name='seo-dashboard-v1'),
    
    # Schema Endpoints
    path('seo/schema/post/<slug:slug>/', schema_post, name='schema-post-v1'),
    path('seo/schema/site/', schema_site, name='schema-site-v1'),
    path('seo/schema/author/<slug:username>/', schema_author, name='schema-author-v1'),
    path('seo/schema/breadcrumbs/<slug:slug>/', schema_breadcrumbs, name='schema-breadcrumbs-v1'),
    
    # Webhooks & Monitoring
    path('revalidate/', revalidate_webhook, name='revalidate-v1'),
    path('healthcheck/', simple_healthcheck, name='healthcheck-v1'),
    path('healthcheck/full/', healthcheck, name='healthcheck-full-v1'),
    
    # Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema-v1'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger-ui-v1'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v1'), name='redoc-v1'),
]
