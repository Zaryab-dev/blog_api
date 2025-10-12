"""Advanced SEO API Endpoints"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.conf import settings
from .models_seo import SEOHealthLog, IndexingQueue
from .seo_indexing import submit_indexnow, verify_google_search_console, generate_indexnow_key
from .models import Post
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def google_verify(request):
    """Google Search Console verification endpoint"""
    verification_code = getattr(settings, 'GOOGLE_SITE_VERIFICATION', '')
    if not verification_code:
        return Response({'error': 'Verification not configured'}, status=404)
    
    return Response({
        'meta_tag': f'<meta name="google-site-verification" content="{verification_code}" />',
        'verification_code': verification_code
    })


@api_view(['POST'])
def indexnow_submit(request):
    """Submit URLs to IndexNow API"""
    urls = request.data.get('urls', [])
    if not urls:
        return Response({'error': 'No URLs provided'}, status=400)
    
    success = submit_indexnow(urls)
    
    SEOHealthLog.objects.create(
        action='indexnow',
        status='success' if success else 'failed',
        url=urls[0] if urls else '',
        response_message=f"Submitted {len(urls)} URLs"
    )
    
    return Response({
        'success': success,
        'urls_submitted': len(urls)
    })


@api_view(['GET'])
def seo_status(request):
    """SEO system health status"""
    recent_logs = SEOHealthLog.objects.all()[:50]
    pending_queue = IndexingQueue.objects.filter(processed_at__isnull=True).count()
    
    stats = {
        'google_ping': {
            'success': recent_logs.filter(action='google_ping', status='success').count(),
            'failed': recent_logs.filter(action='google_ping', status='failed').count()
        },
        'indexnow': {
            'success': recent_logs.filter(action='indexnow', status='success').count(),
            'failed': recent_logs.filter(action='indexnow', status='failed').count()
        },
        'pending_queue': pending_queue,
        'total_published': Post.published.count()
    }
    
    return Response(stats)


@api_view(['POST'])
def reindex_post(request, slug):
    """Manually trigger reindexing for a post"""
    try:
        post = Post.published.get(slug=slug)
        site_url = getattr(settings, 'SITE_URL', '')
        url = f"{site_url}/blog/{post.slug}/"
        
        IndexingQueue.objects.get_or_create(
            url=url,
            defaults={'priority': 10}
        )
        
        return Response({
            'message': 'Post queued for reindexing',
            'url': url
        })
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)


@api_view(['GET'])
@cache_page(60 * 60 * 24)
def indexnow_key_file(request):
    """Serve IndexNow key file"""
    key = generate_indexnow_key()
    return HttpResponse(key, content_type='text/plain')
