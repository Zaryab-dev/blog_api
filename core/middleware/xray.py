"""AWS X-Ray distributed tracing middleware"""
import logging

logger = logging.getLogger(__name__)

try:
    from aws_xray_sdk.core import xray_recorder
    from aws_xray_sdk.ext.django.middleware import XRayMiddleware as BaseXRayMiddleware
    XRAY_AVAILABLE = True
except ImportError:
    XRAY_AVAILABLE = False
    logger.warning("AWS X-Ray SDK not installed. Install with: pip install aws-xray-sdk")


if XRAY_AVAILABLE:
    class XRayMiddleware(BaseXRayMiddleware):
        """Enhanced X-Ray middleware with custom segments"""
        
        def process_request(self, request):
            segment = xray_recorder.current_segment()
            if segment:
                segment.put_annotation('request_id', getattr(request, 'id', 'unknown'))
                segment.put_annotation('method', request.method)
                segment.put_annotation('path', request.path)
            return super().process_request(request)
else:
    class XRayMiddleware:
        """Dummy middleware when X-Ray not available"""
        def __init__(self, get_response):
            self.get_response = get_response
        
        def __call__(self, request):
            return self.get_response(request)
