"""Admin IP Restriction Middleware"""
from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.cache import cache
import logging

logger = logging.getLogger('security')


class AdminIPRestrictionMiddleware:
    """Restrict admin access to allowed IPs only"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'ADMIN_IP_RESTRICTION_ENABLED', False)
        self.allowed_ips = getattr(settings, 'ALLOWED_ADMIN_IPS', [])
    
    def __call__(self, request):
        if self.enabled and request.path.startswith('/admin'):
            client_ip = self.get_client_ip(request)
            
            if not self.is_ip_allowed(client_ip):
                user = getattr(request, 'user', 'Anonymous')
                logger.warning(
                    f"Blocked admin access from unauthorized IP: {client_ip} "
                    f"Path: {request.path} User: {user}"
                )
                return HttpResponseForbidden(
                    '<h1>403 Forbidden</h1>'
                    '<p>Access to admin panel is restricted.</p>'
                )
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_ip_allowed(self, ip):
        """Check if IP is in allowed list"""
        if not self.allowed_ips:
            return True  # If no IPs configured, allow all
        
        # Check exact match
        if ip in self.allowed_ips:
            return True
        
        # Check CIDR ranges
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            for allowed in self.allowed_ips:
                if '/' in allowed:  # CIDR notation
                    network = ipaddress.ip_network(allowed, strict=False)
                    if ip_obj in network:
                        return True
        except Exception as e:
            logger.error(f"Error checking IP {ip}: {e}")
        
        return False
