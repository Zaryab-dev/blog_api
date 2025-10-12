"""Security audit management command"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from core.security_utils import SecurityAudit


class Command(BaseCommand):
    help = 'Run security audit checks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            type=str,
            choices=['all', 'admins', 'sessions', 'settings'],
            default='all',
            help='Type of security check to run'
        )
    
    def handle(self, *args, **options):
        check_type = options['check']
        
        self.stdout.write(self.style.SUCCESS('=== Security Audit Report ===\n'))
        
        if check_type in ['all', 'admins']:
            self.check_admin_accounts()
        
        if check_type in ['all', 'sessions']:
            self.check_sessions()
        
        if check_type in ['all', 'settings']:
            self.check_settings()
        
        self.stdout.write(self.style.SUCCESS('\n=== Audit Complete ==='))
    
    def check_admin_accounts(self):
        """Check admin/superuser accounts"""
        self.stdout.write(self.style.WARNING('\n[Admin Accounts Check]'))
        
        admins = SecurityAudit.check_admin_accounts()
        
        self.stdout.write(f"Total superuser accounts: {len(admins)}")
        
        for admin in admins:
            last_login = admin['last_login'].strftime('%Y-%m-%d %H:%M') if admin['last_login'] else 'Never'
            self.stdout.write(f"  - {admin['username']} ({admin['email']}) - Last login: {last_login}")
        
        # Check for inactive admins
        inactive_admins = User.objects.filter(is_superuser=True, is_active=False).count()
        if inactive_admins > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠ {inactive_admins} inactive superuser accounts found"))
    
    def check_sessions(self):
        """Check session security"""
        self.stdout.write(self.style.WARNING('\n[Session Security Check]'))
        
        total_sessions = Session.objects.count()
        self.stdout.write(f"Total active sessions: {total_sessions}")
        
        # Check for stale sessions
        stale_count = SecurityAudit.check_stale_sessions()
        if stale_count > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠ {stale_count} stale sessions (>30 days old)"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ No stale sessions found"))
    
    def check_settings(self):
        """Check security settings"""
        from django.conf import settings
        
        self.stdout.write(self.style.WARNING('\n[Security Settings Check]'))
        
        checks = {
            'DEBUG': (not settings.DEBUG, 'DEBUG should be False in production'),
            'SECRET_KEY': (len(settings.SECRET_KEY) >= 50, 'SECRET_KEY should be at least 50 characters'),
            'ALLOWED_HOSTS': (len(settings.ALLOWED_HOSTS) > 0, 'ALLOWED_HOSTS should be configured'),
            'SECURE_SSL_REDIRECT': (getattr(settings, 'SECURE_SSL_REDIRECT', False), 'SECURE_SSL_REDIRECT should be True'),
            'SESSION_COOKIE_SECURE': (getattr(settings, 'SESSION_COOKIE_SECURE', False), 'SESSION_COOKIE_SECURE should be True'),
            'CSRF_COOKIE_SECURE': (getattr(settings, 'CSRF_COOKIE_SECURE', False), 'CSRF_COOKIE_SECURE should be True'),
            'SECURE_HSTS_SECONDS': (getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0, 'SECURE_HSTS_SECONDS should be set'),
        }
        
        for check_name, (passed, message) in checks.items():
            if passed:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {check_name}: OK"))
            else:
                self.stdout.write(self.style.ERROR(f"  ✗ {check_name}: {message}"))
