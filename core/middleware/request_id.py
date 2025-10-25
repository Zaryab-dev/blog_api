"""Request ID middleware for distributed tracing"""
import uuid
import logging

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    """Add unique request ID to each request for tracing"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        
        response = self.get_response(request)
        response['X-Request-ID'] = request.id
        
        return response
