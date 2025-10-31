"""
Caching utilities for ML-Battle backend.
Implements caching strategies for frequently accessed data.
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json


def cache_key(*args, **kwargs):
    """Generate a consistent cache key from arguments."""
    key_data = f"{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_result(timeout=300, key_prefix=''):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    
    Usage:
        @cache_result(timeout=600, key_prefix='leaderboard')
        def get_leaderboard(competition_id):
            return expensive_query()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # If not in cache, execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_prefix, *args, **kwargs):
    """
    Invalidate cache for a specific key.
    
    Usage:
        invalidate_cache('leaderboard', competition_id=123)
    """
    key = f"{key_prefix}:{cache_key(*args, **kwargs)}"
    cache.delete(key)


def invalidate_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    Note: This only works with cache backends that support pattern deletion (like Redis).
    
    Usage:
        invalidate_pattern('leaderboard:*')
    """
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)


# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'leaderboard': 300,  # 5 minutes
    'competitions': 600,  # 10 minutes
    'events': 600,  # 10 minutes
    'user_profile': 300,  # 5 minutes
    'ratings': 300,  # 5 minutes
}


def get_cache_timeout(key_type):
    """Get cache timeout for a specific key type."""
    return CACHE_TIMEOUTS.get(key_type, 300)


class CacheHelper:
    """Helper class for common caching operations."""
    
    @staticmethod
    def get_or_set(key, callable_fn, timeout=300):
        """
        Get value from cache or set it if not exists.
        
        Usage:
            value = CacheHelper.get_or_set(
                'my_key',
                lambda: expensive_operation(),
                timeout=600
            )
        """
        result = cache.get(key)
        if result is None:
            result = callable_fn()
            cache.set(key, result, timeout)
        return result
    
    @staticmethod
    def get_competition_leaderboard_key(competition_id):
        """Get cache key for competition leaderboard."""
        return f"leaderboard:competition:{competition_id}"
    
    @staticmethod
    def get_event_competitions_key(event_slug):
        """Get cache key for event competitions."""
        return f"event:competitions:{event_slug}"
    
    @staticmethod
    def get_user_submissions_key(user_id):
        """Get cache key for user submissions."""
        return f"user:submissions:{user_id}"
    
    @staticmethod
    def invalidate_competition_cache(competition_id):
        """Invalidate all cache related to a competition."""
        keys = [
            f"leaderboard:competition:{competition_id}",
            f"competition:{competition_id}",
        ]
        for key in keys:
            cache.delete(key)
    
    @staticmethod
    def invalidate_event_cache(event_slug):
        """Invalidate all cache related to an event."""
        keys = [
            f"event:competitions:{event_slug}",
            f"event:{event_slug}",
        ]
        for key in keys:
            cache.delete(key)
