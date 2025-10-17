#!/usr/bin/env python
"""
Quick test script for landing page
Run: python test_landing_page.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from django.test import RequestFactory
from blog.views import landing_page

def test_landing_page():
    """Test landing page view"""
    print("Testing Landing Page...")
    print("-" * 50)
    
    # Create request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Call view
    response = landing_page(request)
    
    # Check response
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Content Type: {response.get('Content-Type', 'text/html')}")
    
    # Check content
    content = response.content.decode('utf-8')
    
    checks = [
        ('Django Blog API' in content, 'Title present'),
        ('API is Running' in content, 'Status indicator present'),
        ('/api/v1/posts/' in content, 'API endpoints listed'),
        ('GET' in content and 'POST' in content, 'HTTP methods shown'),
        ('Quick Start' in content, 'Quick start section present'),
        ('Documentation' in content, 'Documentation section present'),
    ]
    
    print("\nContent Checks:")
    all_passed = True
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"{status} {description}")
        if not check:
            all_passed = False
    
    print("-" * 50)
    if all_passed:
        print("✓ All tests passed! Landing page is working correctly.")
    else:
        print("✗ Some tests failed. Check the implementation.")
    
    return all_passed

if __name__ == '__main__':
    try:
        success = test_landing_page()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
