#!/usr/bin/env python3
"""Simple load testing script"""
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8080"
ENDPOINTS = [
    "/api/v1/healthcheck/",
    "/api/v1/posts/",
    "/api/v1/categories/",
    "/api/v1/tags/",
]


def make_request(url):
    """Make single request and measure time"""
    start = time.time()
    try:
        response = requests.get(url, timeout=10)
        duration = (time.time() - start) * 1000
        return {
            'success': response.status_code == 200,
            'duration': duration,
            'status': response.status_code
        }
    except Exception as e:
        return {
            'success': False,
            'duration': (time.time() - start) * 1000,
            'error': str(e)
        }


def run_load_test(concurrent_users=10, requests_per_user=10):
    """Run load test"""
    print(f"🚀 Starting load test: {concurrent_users} users, {requests_per_user} requests each")
    print(f"📊 Total requests: {concurrent_users * requests_per_user}")
    print("-" * 60)
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []
        for _ in range(concurrent_users):
            for _ in range(requests_per_user):
                endpoint = ENDPOINTS[len(futures) % len(ENDPOINTS)]
                url = f"{BASE_URL}{endpoint}"
                futures.append(executor.submit(make_request, url))
        
        for future in as_completed(futures):
            results.append(future.result())
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    durations = [r['duration'] for r in successful]
    
    print("\n📈 Results:")
    print(f"  Total requests: {len(results)}")
    print(f"  Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"  Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Requests/sec: {len(results)/total_time:.2f}")
    
    if durations:
        print(f"\n⏱️  Response Times:")
        print(f"  Min: {min(durations):.2f}ms")
        print(f"  Max: {max(durations):.2f}ms")
        print(f"  Avg: {statistics.mean(durations):.2f}ms")
        print(f"  Median: {statistics.median(durations):.2f}ms")
        print(f"  P95: {statistics.quantiles(durations, n=20)[18]:.2f}ms")
        print(f"  P99: {statistics.quantiles(durations, n=100)[98]:.2f}ms")
    
    # Status codes
    status_codes = {}
    for r in results:
        code = r.get('status', 'error')
        status_codes[code] = status_codes.get(code, 0) + 1
    
    print(f"\n📊 Status Codes:")
    for code, count in sorted(status_codes.items()):
        print(f"  {code}: {count}")
    
    # Pass/Fail criteria
    print(f"\n✅ Pass/Fail Criteria:")
    success_rate = len(successful) / len(results) * 100
    avg_response = statistics.mean(durations) if durations else 0
    
    print(f"  Success rate: {success_rate:.1f}% {'✅' if success_rate >= 99 else '❌'} (target: 99%)")
    print(f"  Avg response: {avg_response:.2f}ms {'✅' if avg_response < 200 else '❌'} (target: <200ms)")
    print(f"  Throughput: {len(results)/total_time:.2f} req/s {'✅' if len(results)/total_time > 50 else '❌'} (target: >50 req/s)")


if __name__ == "__main__":
    import sys
    
    concurrent = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    requests = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    run_load_test(concurrent, requests)
