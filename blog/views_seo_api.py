"""
SEO-specific API endpoints for Django Blog API
Provides schema.org, Open Graph preview, and SEO metadata endpoints
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Post, SiteSettings
from .seo_utils import (
    generate_schema_article,
    generate_schema_breadcrumb,
    generate_open_graph_data,
    generate_twitter_card_data,
    notify_search_engines,
    get_site_url
)


@api_view(['GET'])
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def schema_endpoint(request, slug):
    """
    Get schema.org JSON-LD structured data for a specific post
    
    GET /api/seo/schema/<slug>/
    
    Returns:
        JSON-LD structured data for BlogPosting
    """
    post = get_object_or_404(
        Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags'),
        slug=slug
    )
    
    # Generate schema.org Article
    schema_article = generate_schema_article(post)
    
    # Generate breadcrumb
    schema_breadcrumb = generate_schema_breadcrumb(post)
    
    # Return both schemas in a graph
    response_data = {
        "@context": "https://schema.org",
        "@graph": [
            schema_article,
            schema_breadcrumb
        ]
    }
    
    return Response(response_data)


@api_view(['GET'])
@cache_page(60 * 60 * 12)  # Cache for 12 hours
def preview_endpoint(request, slug):
    """
    Get complete SEO preview data for a specific post
    Useful for social media preview cards and SEO tools
    
    GET /api/seo/preview/<slug>/
    
    Returns:
        Complete SEO metadata including OG, Twitter, and meta tags
    """
    post = get_object_or_404(
        Post.published.select_related('author', 'featured_image').prefetch_related('categories', 'tags'),
        slug=slug
    )
    
    # Generate all SEO data
    open_graph = generate_open_graph_data(post)
    twitter_card = generate_twitter_card_data(post)
    
    response_data = {
        "url": post.canonical_url or f"{get_site_url()}/blog/{post.slug}/",
        "title": post.seo_title or post.title,
        "description": post.seo_description or post.summary,
        "image": post.og_image or (post.featured_image.file if post.featured_image else None),
        "open_graph": open_graph,
        "twitter_card": twitter_card,
        "meta": {
            "robots": "index, follow" if post.allow_index else "noindex, nofollow",
            "keywords": post.seo_keywords or ", ".join([tag.name for tag in post.tags.all()]),
            "author": post.author.name,
            "published_time": post.published_at.isoformat() if post.published_at else None,
            "modified_time": post.updated_at.isoformat(),
        }
    }
    
    return Response(response_data)


@api_view(['GET'])
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def all_slugs_endpoint(request):
    """
    Get all published post slugs with metadata for sitemap generation
    
    GET /api/seo/slugs/
    
    Query params:
        - limit: Number of slugs to return (default: all)
        - offset: Offset for pagination
    
    Returns:
        List of post slugs with last modified dates
    """
    queryset = Post.published.only('slug', 'updated_at', 'published_at', 'sitemap_priority', 'sitemap_changefreq')
    
    # Pagination
    limit = request.query_params.get('limit')
    offset = request.query_params.get('offset', 0)
    
    if limit:
        queryset = queryset[int(offset):int(offset) + int(limit)]
    
    slugs = [
        {
            "slug": post.slug,
            "last_modified": post.updated_at.isoformat(),
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "priority": float(post.sitemap_priority),
            "changefreq": post.sitemap_changefreq
        }
        for post in queryset
    ]
    
    return Response({
        "count": Post.published.count(),
        "slugs": slugs
    })


@api_view(['POST'])
def ping_search_engines_endpoint(request):
    """
    Manually trigger search engine ping for sitemap
    
    POST /api/seo/ping/
    
    Body (optional):
        {
            "sitemap_url": "https://example.com/sitemap.xml"
        }
    
    Returns:
        Status of ping attempts to Google and Bing
    """
    # Check for authorization (optional - add your own auth logic)
    auth_header = request.headers.get('Authorization')
    expected_token = getattr(settings, 'SEO_PING_TOKEN', '')
    
    if expected_token and auth_header != f"Bearer {expected_token}":
        return Response(
            {"error": "Unauthorized"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    sitemap_url = request.data.get('sitemap_url')
    
    # Ping search engines
    results = notify_search_engines(sitemap_url)
    
    return Response({
        "message": "Search engines notified",
        "results": results,
        "sitemap_url": sitemap_url or f"{get_site_url()}/sitemap.xml"
    })


@api_view(['GET'])
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def site_metadata_endpoint(request):
    """
    Get site-wide SEO metadata
    
    GET /api/seo/site/
    
    Returns:
        Site-wide SEO configuration and metadata
    """
    site_settings = SiteSettings.load()
    site_url = get_site_url()
    
    return Response({
        "site_name": site_settings.site_name,
        "site_description": site_settings.site_description,
        "site_url": site_settings.site_url or site_url,
        "default_meta_image": site_settings.default_meta_image,
        "sitemap_url": f"{site_url}/sitemap.xml",
        "rss_feed_url": f"{site_url}/rss/",
        "robots_txt_url": f"{site_url}/robots.txt",
        "twitter_site": site_settings.twitter_site,
        "facebook_app_id": site_settings.facebook_app_id,
        "google_site_verification": site_settings.google_site_verification
    })


@require_http_methods(["GET"])
@cache_page(60 * 60 * 24)  # Cache for 24 hours
def google_verification(request):
    """
    Serve Google Search Console verification file
    
    GET /google<verification_code>.html
    """
    site_settings = SiteSettings.load()
    verification_code = site_settings.google_site_verification
    
    if not verification_code:
        return HttpResponse("Google verification not configured", status=404)
    
    content = f"google-site-verification: {verification_code}"
    return HttpResponse(content, content_type='text/html')


@api_view(['GET'])
def seo_health_check(request):
    """
    SEO health check endpoint
    
    GET /api/seo/health/
    
    Returns:
        SEO configuration status and recommendations
    """
    site_settings = SiteSettings.load()
    
    # Check various SEO configurations
    checks = {
        "sitemap_configured": bool(site_settings.sitemap_index_url),
        "robots_txt_configured": bool(site_settings.robots_txt_content),
        "rss_feed_configured": bool(site_settings.rss_feed_url),
        "google_verification_configured": bool(site_settings.google_site_verification),
        "default_og_image_configured": bool(site_settings.default_meta_image),
        "twitter_configured": bool(site_settings.twitter_site),
    }
    
    # Count posts with SEO optimization
    total_posts = Post.published.count()
    posts_with_seo_title = Post.published.exclude(seo_title='').count()
    posts_with_seo_description = Post.published.exclude(seo_description='').count()
    posts_with_og_image = Post.published.exclude(og_image='').count()
    
    seo_coverage = {
        "total_published_posts": total_posts,
        "posts_with_seo_title": posts_with_seo_title,
        "posts_with_seo_description": posts_with_seo_description,
        "posts_with_og_image": posts_with_og_image,
        "seo_title_coverage": f"{(posts_with_seo_title / total_posts * 100):.1f}%" if total_posts > 0 else "0%",
        "seo_description_coverage": f"{(posts_with_seo_description / total_posts * 100):.1f}%" if total_posts > 0 else "0%",
        "og_image_coverage": f"{(posts_with_og_image / total_posts * 100):.1f}%" if total_posts > 0 else "0%",
    }
    
    # Recommendations
    recommendations = []
    if not checks["sitemap_configured"]:
        recommendations.append("Configure sitemap URL in site settings")
    if not checks["google_verification_configured"]:
        recommendations.append("Add Google Search Console verification code")
    if not checks["default_og_image_configured"]:
        recommendations.append("Set a default Open Graph image")
    if posts_with_seo_title < total_posts:
        recommendations.append(f"Add SEO titles to {total_posts - posts_with_seo_title} posts")
    if posts_with_seo_description < total_posts:
        recommendations.append(f"Add SEO descriptions to {total_posts - posts_with_seo_description} posts")
    
    return Response({
        "status": "healthy" if all(checks.values()) else "needs_attention",
        "checks": checks,
        "seo_coverage": seo_coverage,
        "recommendations": recommendations
    })
