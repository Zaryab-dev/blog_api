"""Request validation and attack prevention middleware"""
import re
import logging
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('security')


class RequestValidationMiddleware:
    """Validate requests and detect attacks"""
    
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bexec\b.*\()",
        r"(\bor\b.*\b1\s*=\s*1\b)",
        r"(\band\b.*\b1\s*=\s*1\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bxp_cmdshell\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"\.\.\\",
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_body_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 10485760)
    
    def __call__(self, request):
        # Validate content length
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length and int(content_length) > self.max_body_size:
            logger.warning(f"Request body too large: {content_length} bytes from {self.get_client_ip(request)}")
            return JsonResponse({'error': 'Request body too large'}, status=413)
        
        # Validate Content-Type for POST/PUT/PATCH
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.META.get('CONTENT_TYPE', '')
            if not content_type:
                return JsonResponse({'error': 'Content-Type header required'}, status=400)
        
        # Check for SQL injection in query params
        query_string = request.META.get('QUERY_STRING', '')
        if self.detect_sql_injection(query_string):
            ip = self.get_client_ip(request)
            logger.warning(f"SQL injection attempt detected from {ip}: {query_string[:200]}")
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        # Check for path traversal
        path = request.path
        if self.detect_path_traversal(path):
            ip = self.get_client_ip(request)
            logger.warning(f"Path traversal attempt detected from {ip}: {path}")
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        return self.get_response(request)
    
    def detect_sql_injection(self, text):
        """Detect SQL injection patterns"""
        text_lower = text.lower()
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def detect_path_traversal(self, path):
        """Detect path traversal attempts"""
        for pattern in self.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
