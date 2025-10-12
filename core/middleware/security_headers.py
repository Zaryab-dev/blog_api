"""Enhanced security headers middleware"""
from django.conf import settings


class SecurityHeadersMiddleware:
    """Add comprehensive security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # HSTS (only in production)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",  # CKEditor needs inline styles
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Frame protection
        response['X-Frame-Options'] = 'DENY'
        
        # MIME sniffing protection
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS protection (legacy but still useful)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=()'
        
        # Remove server fingerprints
        response['Server'] = 'webserver'
        if 'X-Powered-By' in response:
            del response['X-Powered-By']
        
        return response
