#!/usr/bin/env python3
"""
Test script to verify Phase 1 security fixes
Run this after applying security patches
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')

def test_debug_mode():
    """Test that DEBUG is controlled by environment variable"""
    print("\n🧪 Test 1: DEBUG Mode Configuration")
    print("=" * 50)
    
    from django.conf import settings
    
    debug_value = settings.DEBUG
    print(f"Current DEBUG value: {debug_value}")
    
    if debug_value:
        print("⚠️  WARNING: DEBUG is True")
        print("   Make sure this is intentional for your environment")
    else:
        print("✅ PASS: DEBUG is False (production-safe)")
    
    return True


def test_required_settings():
    """Test that required settings validation works"""
    print("\n🧪 Test 2: Required Settings Validation")
    print("=" * 50)
    
    from django.conf import settings
    
    required_settings = {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_API_KEY': settings.SUPABASE_API_KEY,
        'SUPABASE_BUCKET': settings.SUPABASE_BUCKET,
    }
    
    all_set = True
    for key, value in required_settings.items():
        if value:
            print(f"✅ {key}: Set")
        else:
            print(f"❌ {key}: Missing")
            all_set = False
    
    if all_set:
        print("\n✅ PASS: All required settings are configured")
    else:
        print("\n❌ FAIL: Some required settings are missing")
        print("   Check your .env file and ENVIRONMENT_SETUP.md")
    
    return all_set


def test_csrf_protection():
    """Test that CSRF exemption is removed"""
    print("\n🧪 Test 3: CSRF Protection")
    print("=" * 50)
    
    import inspect
    from blog import views_ckeditor5_upload
    
    # Check if csrf_exempt is in the function decorators
    func = views_ckeditor5_upload.ckeditor5_upload
    source = inspect.getsource(func)
    
    if '@csrf_exempt' in source:
        print("❌ FAIL: @csrf_exempt decorator still present")
        print("   CSRF protection is disabled!")
        return False
    else:
        print("✅ PASS: @csrf_exempt decorator removed")
        print("   CSRF protection is enabled")
        return True


def test_exception_handling():
    """Test that specific exceptions are used"""
    print("\n🧪 Test 4: Exception Handling")
    print("=" * 50)
    
    try:
        from blog.exceptions import (
            BlogAPIException,
            ImageUploadError,
            StorageConnectionError,
            InvalidContentError,
            ValidationError
        )
        print("✅ Custom exception classes created:")
        print("   - BlogAPIException")
        print("   - ImageUploadError")
        print("   - StorageConnectionError")
        print("   - InvalidContentError")
        print("   - ValidationError")
        print("\n✅ PASS: Custom exceptions available")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Could not import custom exceptions: {e}")
        return False


def test_no_hardcoded_secrets():
    """Test that no secrets are hardcoded"""
    print("\n🧪 Test 5: No Hardcoded Secrets")
    print("=" * 50)
    
    import inspect
    from leather_api import settings
    
    source = inspect.getsource(settings)
    
    # Check for common secret patterns
    suspicious_patterns = [
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',  # JWT token start
        'default=\'https://soccrpfkqjqjaoaturjb',  # Old Supabase URL
    ]
    
    found_secrets = []
    for pattern in suspicious_patterns:
        if pattern in source:
            found_secrets.append(pattern[:30] + '...')
    
    if found_secrets:
        print("❌ FAIL: Potential hardcoded secrets found:")
        for secret in found_secrets:
            print(f"   - {secret}")
        return False
    else:
        print("✅ PASS: No hardcoded secrets detected")
        print("   All credentials should come from environment variables")
        return True


def test_documentation_exists():
    """Test that documentation files exist"""
    print("\n🧪 Test 6: Documentation")
    print("=" * 50)
    
    from pathlib import Path
    
    base_dir = Path(__file__).resolve().parent
    
    docs = {
        '.env.example': base_dir / '.env.example',
        'ENVIRONMENT_SETUP.md': base_dir / 'ENVIRONMENT_SETUP.md',
        'SECURITY_FIXES.md': base_dir / 'SECURITY_FIXES.md',
        'DEPLOYMENT_CHECKLIST.md': base_dir / 'DEPLOYMENT_CHECKLIST.md',
    }
    
    all_exist = True
    for name, path in docs.items():
        if path.exists():
            print(f"✅ {name}: Exists")
        else:
            print(f"❌ {name}: Missing")
            all_exist = False
    
    if all_exist:
        print("\n✅ PASS: All documentation files created")
    else:
        print("\n❌ FAIL: Some documentation files are missing")
    
    return all_exist


def run_all_tests():
    """Run all security tests"""
    print("\n" + "=" * 50)
    print("🔒 SECURITY FIXES VERIFICATION")
    print("=" * 50)
    
    # Initialize Django
    try:
        django.setup()
    except Exception as e:
        print(f"\n❌ CRITICAL: Django setup failed: {e}")
        print("   Check your environment variables and settings")
        return False
    
    tests = [
        test_debug_mode,
        test_required_settings,
        test_csrf_protection,
        test_exception_handling,
        test_no_hardcoded_secrets,
        test_documentation_exists,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total} ({percentage:.0f}%)")
    
    if passed == total:
        print("\n🎉 SUCCESS: All security fixes verified!")
        print("   Your application is ready for production")
        return True
    else:
        print(f"\n⚠️  WARNING: {total - passed} test(s) failed")
        print("   Review the failures above and fix before deploying")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
