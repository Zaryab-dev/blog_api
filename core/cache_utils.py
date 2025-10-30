"""
Production-grade cache utilities with Redis support
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def generate_cache_key(prefix, *args, **kwargs):
    """Generate consistent cache key from arguments"""
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(timeout=300, key_prefix='view'):
    """
    Decorator to cache function responses
    
    Usage:
        @cache_response(timeout=600, key_prefix='posts')
        def get_posts():
            return Post.objects.all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f'Cache HIT: {cache_key}')
                return result
            
            # Execute function and cache result
            logger.debug(f'Cache MISS: {cache_key}')
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def invalidate_cache(key_prefix, *args, **kwargs):
    """Invalidate specific cache key"""
    cache_key = generate_cache_key(key_prefix, *args, **kwargs)
    cache.delete(cache_key)
    logger.info(f'Cache invalidated: {cache_key}')


def invalidate_pattern(pattern):
    """Invalidate all cache keys matching pattern (Redis only)"""
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        keys = conn.keys(f"blog:{pattern}*")
        if keys:
            conn.delete(*keys)
            logger.info(f'Invalidated {len(keys)} cache keys matching: {pattern}')
    except Exception as e:
        logger.warning(f'Pattern invalidation failed: {e}')


def warm_cache(key, value, timeout=300):
    """Proactively warm cache with data"""
    cache.set(key, value, timeout)
    logger.info(f'Cache warmed: {key}')


class CacheManager:
    """Context manager for cache operations"""
    
    def __init__(self, key, timeout=300):
        self.key = key
        self.timeout = timeout
        self.value = None
    
    def __enter__(self):
        self.value = cache.get(self.key)
        return self.value
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and self.value is None:
            # Cache miss, could set value here if needed
            pass
        return False
