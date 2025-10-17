#!/usr/bin/env python3
"""
Comprehensive security audit script
Run before deployment to check for security issues
"""
import os
import sys
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from django.conf import settings
from pathlib import Path


def check_debug_mode():
    """Check DEBUG setting"""
    print("\n🔍 Checking DEBUG mode...")
    if settings.DEBUG:
        print("  ⚠️  WARNING: DEBUG is True")
        return False
    print("  ✅ DEBUG is False")
    return True


def check_secret_key():
    """Check SECRET_KEY strength"""
    print("\n🔍 Checking SECRET_KEY...")
    if settings.SECRET_KEY == 'django-insecure-change-in-production':
        print("  ❌ FAIL: Using default SECRET_KEY")
        return False
    if len(settings.SECRET_KEY) < 50:
        print("  ⚠️  WARNING: SECRET_KEY is too short")
        return False
    print("  ✅ SECRET_KEY is properly configured")
    return True


def check_allowed_hosts():
    """Check ALLOWED_HOSTS configuration"""
    print("\n🔍 Checking ALLOWED_HOSTS...")
    if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
        print("  ❌ FAIL: ALLOWED_HOSTS not properly configured")
        return False
    print(f"  ✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    return True


def check_database():
    """Check database configuration"""
    print("\n🔍 Checking database...")
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'sqlite' in db_engine and not settings.DEBUG:
        print("  ⚠️  WARNING: Using SQLite in production")
        return False
    print(f"  ✅ Database: {db_engine}")
    return True


def check_security_middleware():
    """Check security middleware"""
    print("\n🔍 Checking security middleware...")
    required_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    
    missing = []
    for mw in required_middleware:
        if mw not in settings.MIDDLEWARE:
            missing.append(mw)
    
    if missing:
        print(f"  ❌ FAIL: Missing middleware: {missing}")
        return False
    print("  ✅ All security middleware present")
    return True


def check_csrf_settings():
    """Check CSRF settings"""
    print("\n🔍 Checking CSRF settings...")
    if not settings.DEBUG:
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            print("  ⚠️  WARNING: CSRF_COOKIE_SECURE not enabled")
            return False
    print("  ✅ CSRF settings OK")
    return True


def check_session_security():
    """Check session security"""
    print("\n🔍 Checking session security...")
    if not settings.DEBUG:
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            print("  ⚠️  WARNING: SESSION_COOKIE_SECURE not enabled")
            return False
        if not getattr(settings, 'SESSION_COOKIE_HTTPONLY', False):
            print("  ⚠️  WARNING: SESSION_COOKIE_HTTPONLY not enabled")
            return False
    print("  ✅ Session security OK")
    return True


def check_hardcoded_secrets():
    """Scan for hardcoded secrets in code"""
    print("\n🔍 Scanning for hardcoded secrets...")
    
    patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', 'password'),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'API key'),
        (r'secret\s*=\s*["\'][^"\']+["\']', 'secret'),
        (r'token\s*=\s*["\'][^"\']+["\']', 'token'),
    ]
    
    base_dir = Path(settings.BASE_DIR)
    issues = []
    
    for py_file in base_dir.rglob('*.py'):
        if 'venv' in str(py_file) or 'migrations' in str(py_file):
            continue
        
        try:
            content = py_file.read_text()
            for pattern, name in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Exclude env() calls
                    if 'env(' not in content[max(0, content.find(pattern)-20):content.find(pattern)+50]:
                        issues.append(f"{py_file}: Possible hardcoded {name}")
        except:
            pass
    
    if issues:
        print(f"  ⚠️  WARNING: Found {len(issues)} potential issues")
        for issue in issues[:5]:  # Show first 5
            print(f"    - {issue}")
        return False
    print("  ✅ No hardcoded secrets found")
    return True


def check_cors_settings():
    """Check CORS configuration"""
    print("\n🔍 Checking CORS settings...")
    if getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False):
        print("  ⚠️  WARNING: CORS_ALLOW_ALL_ORIGINS is True")
        return False
    print("  ✅ CORS properly configured")
    return True


def check_file_upload_security():
    """Check file upload settings"""
    print("\n🔍 Checking file upload security...")
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 0)
    if max_size == 0 or max_size > 10 * 1024 * 1024:
        print("  ⚠️  WARNING: MAX_UPLOAD_SIZE not set or too large")
        return False
    print(f"  ✅ MAX_UPLOAD_SIZE: {max_size / (1024*1024):.1f}MB")
    return True


def check_logging():
    """Check logging configuration"""
    print("\n🔍 Checking logging...")
    if not hasattr(settings, 'LOGGING'):
        print("  ⚠️  WARNING: LOGGING not configured")
        return False
    print("  ✅ Logging configured")
    return True


def check_environment_variables():
    """Check required environment variables"""
    print("\n🔍 Checking environment variables...")
    required = [
        'SUPABASE_URL',
        'SUPABASE_API_KEY',
        'SUPABASE_BUCKET',
    ]
    
    missing = []
    for var in required:
        if not getattr(settings, var, None):
            missing.append(var)
    
    if missing:
        print(f"  ❌ FAIL: Missing variables: {missing}")
        return False
    print("  ✅ All required variables set")
    return True


def run_audit():
    """Run all security checks"""
    print("=" * 60)
    print("🔒 SECURITY AUDIT")
    print("=" * 60)
    
    checks = [
        check_debug_mode,
        check_secret_key,
        check_allowed_hosts,
        check_database,
        check_security_middleware,
        check_csrf_settings,
        check_session_security,
        check_hardcoded_secrets,
        check_cors_settings,
        check_file_upload_security,
        check_logging,
        check_environment_variables,
    ]
    
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 AUDIT SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"Checks Passed: {passed}/{total} ({percentage:.0f}%)")
    
    if passed == total:
        print("\n🎉 SUCCESS: All security checks passed!")
        print("   Your application is ready for production")
        return True
    else:
        print(f"\n⚠️  WARNING: {total - passed} check(s) failed")
        print("   Review the failures above before deploying")
        return False


if __name__ == '__main__':
    success = run_audit()
    sys.exit(0 if success else 1)
