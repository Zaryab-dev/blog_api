#!/usr/bin/env python3
"""
Test all API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
                print(f"✅ SUCCESS")
                
                # Show sample data
                if isinstance(data, dict):
                    if 'results' in data:
                        print(f"Count: {data.get('count', 0)}")
                        print(f"Results: {len(data['results'])} items")
                        if data['results']:
                            print(f"First item keys: {list(data['results'][0].keys())}")
                    else:
                        print(f"Response keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"Results: {len(data)} items")
                    if data:
                        print(f"First item keys: {list(data[0].keys())}")
                
                return True
            except:
                print(f"✅ SUCCESS (non-JSON response)")
                return True
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("="*60)
    print("🚀 API ENDPOINT TESTING")
    print("="*60)
    
    results = {}
    
    # Test endpoints
    tests = [
        ("GET", "/healthcheck/", None, "Health check"),
        ("GET", "/posts/", None, "List all posts"),
        ("GET", "/categories/", None, "List all categories"),
        ("GET", "/tags/", None, "List all tags"),
        ("GET", "/authors/", None, "List all authors"),
        ("GET", "/search/?q=leather", None, "Search posts"),
        ("GET", "/trending/", None, "Trending posts"),
        ("GET", "/sitemap.xml", None, "XML Sitemap"),
        ("GET", "/robots.txt", None, "Robots.txt"),
    ]
    
    for method, endpoint, data, desc in tests:
        results[endpoint] = test_endpoint(method, endpoint, data, desc)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for endpoint, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {endpoint}")
    
    print(f"\n{'='*60}")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed")

if __name__ == "__main__":
    main()
