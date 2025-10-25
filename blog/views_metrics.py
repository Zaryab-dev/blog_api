"""Metrics API endpoint"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.core.cache import cache
import time


@api_view(['GET'])
@permission_classes([IsAdminUser])
def metrics_view(request):
    """Prometheus-compatible metrics endpoint"""
    current_minute = int(time.time() // 60)
    
    # Aggregate last 5 minutes
    all_metrics = {
        'request_count': 0,
        'total_duration': 0,
        'status_codes': {},
        'endpoints': {}
    }
    
    for i in range(5):
        metrics_key = f"metrics:{current_minute - i}"
        metrics = cache.get(metrics_key, {})
        
        all_metrics['request_count'] += metrics.get('request_count', 0)
        all_metrics['total_duration'] += metrics.get('total_duration', 0)
        
        for code, count in metrics.get('status_codes', {}).items():
            all_metrics['status_codes'][code] = all_metrics['status_codes'].get(code, 0) + count
        
        for endpoint, count in metrics.get('endpoints', {}).items():
            all_metrics['endpoints'][endpoint] = all_metrics['endpoints'].get(endpoint, 0) + count
    
    avg_response_time = (all_metrics['total_duration'] / all_metrics['request_count']) if all_metrics['request_count'] > 0 else 0
    
    return Response({
        'request_count': all_metrics['request_count'],
        'avg_response_time_ms': round(avg_response_time, 2),
        'status_codes': all_metrics['status_codes'],
        'top_endpoints': dict(sorted(all_metrics['endpoints'].items(), key=lambda x: x[1], reverse=True)[:10])
    })
