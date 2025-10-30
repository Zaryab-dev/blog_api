"""IP blocking and malicious user agent detection"""
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('security')


class IPBlockingMiddleware:
    """Block malicious IPs and user agents"""
    
    MALICIOUS_USER_AGENTS = [
        'sqlmap', 'nmap', 'nikto', 'masscan', 'nessus',
        'openvas', 'metasploit', 'burpsuite', 'acunetix',
        'w3af', 'skipfish', 'havij', 'pangolin', 'jsql',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_ips = self.load_blocked_ips()
    
    def __call__(self, request):
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Check if IP is blocked
        if self.is_ip_blocked(ip):
            logger.warning(f"Blocked IP attempted access: {ip}")
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Check for malicious user agents
        if self.is_malicious_user_agent(user_agent):
            logger.warning(f"Malicious user agent detected: {user_agent[:100]} from IP: {ip}")
            self.block_ip_temporarily(ip)
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def load_blocked_ips(self):
        """Load blocked IPs from settings"""
        blocked = getattr(settings, 'BLOCKED_IPS', '')
        if blocked:
            return set(ip.strip() for ip in blocked.split(','))
        return set()
    
    def is_ip_blocked(self, ip):
        """Check if IP is permanently or temporarily blocked"""
        if ip in self.blocked_ips:
            return True
        
        # Check temporary block in Redis
        cache_key = f"blocked_ip:{ip}"
        return cache.get(cache_key, False)
    
    def is_malicious_user_agent(self, user_agent):
        """Check if user agent is malicious"""
        return any(agent in user_agent for agent in self.MALICIOUS_USER_AGENTS)
    
    def block_ip_temporarily(self, ip, duration=3600):
        """Temporarily block IP for 1 hour"""
        cache_key = f"blocked_ip:{ip}"
        cache.set(cache_key, True, duration)
        logger.warning(f"Temporarily blocked IP: {ip} for {duration} seconds")
