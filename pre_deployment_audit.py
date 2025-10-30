#!/usr/bin/env python3
"""
Pre-deployment audit: SEO, Security, Performance
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from django.conf import settings
from django.test import Client


def audit_seo():
    """Audit SEO configuration"""
    print("\n🔍 SEO AUDIT")
    print("=" * 70)
    
    checks = []
    
    # Check sitemap
    client = Client()
    response = client.get('/sitemap.xml')
    checks.append(("Sitemap accessible", response.status_code == 200))
    
    # Check robots.txt
    response = client.get('/robots.txt')
    checks.append(("Robots.txt accessible", response.status_code == 200))
    
    # Check RSS feed
    response = client.get('/rss/')
    checks.append(("RSS feed accessible", response.status_code == 200))
    
    # Check meta tags in post
    from blog.models import Post
    if Post.published.exists():
        post = Post.published.first()
        checks.append(("Posts have SEO title", bool(post.seo_title)))
        checks.append(("Posts have SEO description", bool(post.seo_description)))
        checks.append(("Posts have canonical URL", bool(post.canonical_url)))
        checks.append(("Posts have OG image", bool(post.computed_og_image)))
    
    for check, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(passed for _, passed in checks)


def audit_security():
    """Audit security configuration"""
    print("\n🔒 SECURITY AUDIT")
    print("=" * 70)
    
    checks = []
    
    # Critical settings
    checks.append(("DEBUG is False", not settings.DEBUG))
    checks.append(("SECRET_KEY is strong", len(settings.SECRET_KEY) >= 50))
    checks.append(("ALLOWED_HOSTS configured", bool(settings.ALLOWED_HOSTS)))
    
    # Security middleware
    required_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    for mw in required_middleware:
        checks.append((f"{mw.split('.')[-1]}", mw in settings.MIDDLEWARE))
    
    # HTTPS settings (if not DEBUG)
    if not settings.DEBUG:
        checks.append(("CSRF_COOKIE_SECURE", getattr(settings, 'CSRF_COOKIE_SECURE', False)))
        checks.append(("SESSION_COOKIE_SECURE", getattr(settings, 'SESSION_COOKIE_SECURE', False)))
    
    # Environment variables
    checks.append(("SUPABASE_URL set", bool(getattr(settings, 'SUPABASE_URL', None))))
    checks.append(("SUPABASE_API_KEY set", bool(getattr(settings, 'SUPABASE_API_KEY', None))))
    
    for check, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(passed for _, passed in checks)


def audit_performance():
    """Audit performance configuration"""
    print("\n⚡ PERFORMANCE AUDIT")
    print("=" * 70)
    
    checks = []
    
    # Database
    db_engine = settings.DATABASES['default']['ENGINE']
    checks.append(("Using PostgreSQL", 'postgresql' in db_engine))
    
    # Caching
    cache_backend = settings.CACHES['default']['BACKEND']
    checks.append(("Caching configured", 'dummy' not in cache_backend.lower()))
    
    # Static files
    checks.append(("STATIC_ROOT set", bool(settings.STATIC_ROOT)))
    
    for check, passed in checks:
        status = "✅" if passed else "⚠️ "
        print(f"  {status} {check}")
    
    return True  # Performance checks are warnings, not failures


def run_audit():
    """Run all audits"""
    print("\n" + "=" * 70)
    print("🔍 PRE-DEPLOYMENT AUDIT")
    print("=" * 70)
    
    seo_pass = audit_seo()
    security_pass = audit_security()
    perf_pass = audit_performance()
    
    print("\n" + "=" * 70)
    print("📊 AUDIT SUMMARY")
    print("=" * 70)
    
    print(f"SEO:         {'✅ PASS' if seo_pass else '❌ FAIL'}")
    print(f"Security:    {'✅ PASS' if security_pass else '❌ FAIL'}")
    print(f"Performance: {'✅ PASS' if perf_pass else '⚠️  WARNINGS'}")
    
    if seo_pass and security_pass:
        print("\n🎉 Ready for deployment!")
        return True
    else:
        print("\n⚠️  Fix issues before deploying")
        return False


if __name__ == '__main__':
    try:
        success = run_audit()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
