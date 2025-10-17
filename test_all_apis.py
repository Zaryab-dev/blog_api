#!/usr/bin/env python3
"""
Comprehensive API endpoint testing
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')
django.setup()

from django.test import Client
from blog.models import Post, Author, Category, Tag
import json


def test_api_endpoints():
    """Test all API endpoints"""
    client = Client()
    
    print("\n🧪 COMPREHENSIVE API TESTING")
    print("=" * 70)
    
    # Create test data
    author = Author.objects.get_or_create(name="Test Author", defaults={'slug': 'test-author'})[0]
    category = Category.objects.get_or_create(name="Test Category", defaults={'slug': 'test-category'})[0]
    tag = Tag.objects.get_or_create(name="Test Tag", defaults={'slug': 'test-tag'})[0]
    
    post = Post.objects.create(
        title="Test Post for API",
        slug="test-post-api",
        summary="Test summary for API testing",
        content_html="<p>Test content</p>",
        author=author,
        status='published'
    )
    post.categories.add(category)
    post.tags.add(tag)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Posts List
    print("\n📝 Test 1: GET /api/v1/posts/")
    response = client.get('/api/v1/posts/')
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Posts returned: {data.get('count', 0)}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 2: Post Detail
    print("\n📝 Test 2: GET /api/v1/posts/{slug}/")
    response = client.get(f'/api/v1/posts/{post.slug}/')
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Title: {data.get('title')}")
        print(f"   ✅ SEO title: {data.get('seo', {}).get('title', 'N/A')}")
        print(f"   ✅ Related posts: {len(data.get('related_posts', []))}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 3: Categories
    print("\n📝 Test 3: GET /api/v1/categories/")
    response = client.get('/api/v1/categories/')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 4: Tags
    print("\n📝 Test 4: GET /api/v1/tags/")
    response = client.get('/api/v1/tags/')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 5: Authors
    print("\n📝 Test 5: GET /api/v1/authors/")
    response = client.get('/api/v1/authors/')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 6: Search
    print("\n📝 Test 6: GET /api/v1/search/?q=test")
    response = client.get('/api/v1/search/?q=test')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 7: Sitemap
    print("\n📝 Test 7: GET /sitemap.xml")
    response = client.get('/sitemap.xml')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 8: Robots.txt
    print("\n📝 Test 8: GET /robots.txt")
    response = client.get('/robots.txt')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 9: RSS Feed
    print("\n📝 Test 9: GET /rss/")
    response = client.get('/rss/')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Test 10: API Docs
    print("\n📝 Test 10: GET /api/v1/docs/")
    response = client.get('/api/v1/docs/')
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        tests_passed += 1
    else:
        print(f"   ❌ Status: {response.status_code}")
        tests_failed += 1
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    Post.objects.filter(slug='test-post-api').delete()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Passed: {tests_passed}/10")
    print(f"Tests Failed: {tests_failed}/10")
    
    if tests_failed == 0:
        print("\n🎉 All API tests passed!")
        return True
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed")
        return False


if __name__ == '__main__':
    try:
        success = test_api_endpoints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
