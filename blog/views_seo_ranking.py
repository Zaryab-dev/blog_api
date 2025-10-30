"""
Advanced SEO & Ranking API Views
Endpoints for SEO optimization and search engine indexing
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
from blog.models import Post
from blog.seo_advanced_ranking import (
    GoogleIndexingAPI, IndexNowAPI, StructuredDataGenerator,
    SEOPerformanceOptimizer, submit_to_search_engines
)
from blog.seo_ranking_signals import (
    CoreWebVitalsOptimizer, EATSignalsOptimizer,
    UserEngagementSignals, SemanticSEOOptimizer,
    generate_comprehensive_seo_report
)
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_url_to_google(request, slug):
    """
    Submit URL to Google Indexing API for instant indexing
    POST /api/v1/seo/submit-to-google/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        site_url = getattr(settings, 'SITE_URL', 'https://example.com')
        post_url = f"{site_url}/blog/{post.slug}/"
        
        google_api = GoogleIndexingAPI()
        result = google_api.notify_google(post_url)
        
        return Response({
            'success': result.get('success', False),
            'url': post_url,
            'result': result
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_url_to_indexnow(request, slug):
    """
    Submit URL to IndexNow for instant indexing across search engines
    POST /api/v1/seo/submit-to-indexnow/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        site_url = getattr(settings, 'SITE_URL', 'https://example.com')
        post_url = f"{site_url}/blog/{post.slug}/"
        
        indexnow = IndexNowAPI()
        result = indexnow.submit_url(post_url)
        
        return Response({
            'success': result.get('success', False),
            'url': post_url,
            'engines': result.get('results', [])
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_submit_to_indexnow(request):
    """
    Submit multiple URLs to IndexNow at once
    POST /api/v1/seo/bulk-submit/
    Body: {"slugs": ["slug1", "slug2", ...]}
    """
    try:
        slugs = request.data.get('slugs', [])
        if not slugs:
            return Response({'error': 'No slugs provided'}, status=400)
        
        posts = Post.published.filter(slug__in=slugs)
        site_url = getattr(settings, 'SITE_URL', 'https://example.com')
        urls = [f"{site_url}/blog/{post.slug}/" for post in posts]
        
        indexnow = IndexNowAPI()
        result = indexnow.submit_bulk(urls)
        
        return Response({
            'success': result.get('success', False),
            'submitted_count': len(urls),
            'urls': urls
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_structured_data(request, slug):
    """
    Get comprehensive structured data for a post
    GET /api/v1/seo/structured-data/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        generator = StructuredDataGenerator()
        
        structured_data = {
            'article': generator.generate_article_schema(post),
            'breadcrumb': generator.generate_breadcrumb_schema(post),
        }
        
        return Response({
            'success': True,
            'post': post.title,
            'structured_data': structured_data
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_seo_score(request, slug):
    """
    Get comprehensive SEO score and recommendations
    GET /api/v1/seo/score/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        report = generate_comprehensive_seo_report(post)
        
        return Response({
            'success': True,
            'report': report
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_core_web_vitals(request, slug):
    """
    Get Core Web Vitals optimization data
    GET /api/v1/seo/core-web-vitals/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        optimizer = CoreWebVitalsOptimizer()
        
        vitals = {
            'lcp_optimization': optimizer.optimize_lcp(post),
            'performance_hints': optimizer.generate_performance_hints(),
            'lazy_loading': optimizer.generate_lazy_loading_config()
        }
        
        return Response({
            'success': True,
            'post': post.title,
            'core_web_vitals': vitals
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_eat_signals(request, slug):
    """
    Get E-E-A-T signals for a post
    GET /api/v1/seo/eat-signals/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        eat_optimizer = EATSignalsOptimizer()
        
        signals = {
            'author_credentials': eat_optimizer.generate_author_credentials(post.author),
            'freshness_score': eat_optimizer.calculate_content_freshness_score(post),
            'trust_signals': eat_optimizer.generate_trust_signals(post)
        }
        
        return Response({
            'success': True,
            'post': post.title,
            'eat_signals': signals
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_semantic_keywords(request, slug):
    """
    Get semantic SEO keywords and LSI terms
    GET /api/v1/seo/semantic-keywords/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        semantic = SemanticSEOOptimizer()
        
        keywords = {
            'lsi_keywords': semantic.generate_lsi_keywords(post),
            'entities': semantic.extract_entities(post.content_html or ''),
            'featured_snippet_optimization': semantic.optimize_for_featured_snippets(post)
        }
        
        return Response({
            'success': True,
            'post': post.title,
            'semantic_data': keywords
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_engagement_metrics(request, slug):
    """
    Get user engagement metrics (ranking signals)
    GET /api/v1/seo/engagement/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        engagement = UserEngagementSignals()
        
        metrics = {
            'engagement_score': engagement.calculate_engagement_score(post),
            'dwell_time_estimate': engagement.calculate_dwell_time_estimate(post),
            'bounce_rate_signals': engagement.track_bounce_rate_signals(post),
            'views': post.views_count,
            'likes': post.likes_count,
            'comments': post.comments_count,
            'trending_score': post.trending_score
        }
        
        return Response({
            'success': True,
            'post': post.title,
            'engagement_metrics': metrics
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_optimize_seo(request, slug):
    """
    Automatically optimize all SEO aspects of a post
    POST /api/v1/seo/auto-optimize/{slug}/
    """
    try:
        post = Post.objects.get(slug=slug)
        
        # Auto-populate SEO fields if empty
        from blog.seo_automation import SEOAutomation
        SEOAutomation.auto_populate_post_seo(post)
        
        # Generate structured data
        generator = StructuredDataGenerator()
        post.schema_org = generator.generate_article_schema(post)
        
        post.save()
        
        # Submit to search engines
        site_url = getattr(settings, 'SITE_URL', 'https://example.com')
        post_url = f"{site_url}/blog/{post.slug}/"
        indexing_results = submit_to_search_engines(post_url)
        
        return Response({
            'success': True,
            'post': post.title,
            'optimizations_applied': [
                'SEO metadata populated',
                'Structured data generated',
                'Submitted to search engines'
            ],
            'indexing_results': indexing_results
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def seo_dashboard(request):
    """
    Get overall SEO dashboard with site-wide metrics
    GET /api/v1/seo/dashboard/
    """
    try:
        from blog.seo_ranking_signals import ContentVelocityTracker
        
        total_posts = Post.published.count()
        posts_with_seo = Post.published.exclude(seo_title='').count()
        posts_with_images = Post.published.exclude(featured_image=None).count()
        
        velocity = ContentVelocityTracker.calculate_publishing_velocity()
        update_frequency = ContentVelocityTracker.get_content_update_frequency()
        
        # Calculate average scores
        avg_word_count = Post.published.aggregate(avg=models.Avg('word_count'))['avg'] or 0
        avg_views = Post.published.aggregate(avg=models.Avg('views_count'))['avg'] or 0
        
        dashboard = {
            'total_posts': total_posts,
            'seo_completion_rate': (posts_with_seo / total_posts * 100) if total_posts > 0 else 0,
            'images_completion_rate': (posts_with_images / total_posts * 100) if total_posts > 0 else 0,
            'content_velocity': velocity,
            'update_frequency': update_frequency,
            'avg_word_count': int(avg_word_count),
            'avg_views': int(avg_views),
            'recommendations': []
        }
        
        # Generate recommendations
        if dashboard['seo_completion_rate'] < 80:
            dashboard['recommendations'].append('Improve SEO metadata completion rate')
        if dashboard['images_completion_rate'] < 90:
            dashboard['recommendations'].append('Add featured images to more posts')
        if avg_word_count < 1000:
            dashboard['recommendations'].append('Increase average content length')
        if velocity['posts_last_30_days'] < 4:
            dashboard['recommendations'].append('Increase publishing frequency')
        
        return Response({
            'success': True,
            'dashboard': dashboard
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def indexnow_key_file(request):
    """
    Serve IndexNow key file for verification
    GET /api/v1/{key}.txt
    """
    indexnow_key = getattr(settings, 'INDEXNOW_KEY', '')
    if not indexnow_key:
        return Response('', status=404)
    
    from django.http import HttpResponse
    return HttpResponse(indexnow_key, content_type='text/plain')
