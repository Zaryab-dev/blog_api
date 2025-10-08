class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # HSTS
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # CSP
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline'; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        
        # Frame protection
        response['X-Frame-Options'] = 'DENY'
        
        # MIME sniffing protection
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer policy
        response['Referrer-Policy'] = 'same-origin'
        
        # Permissions policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
