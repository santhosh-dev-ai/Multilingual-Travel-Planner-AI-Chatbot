"""
Cache Service - In-memory caching with TTL support
Production-ready with LRU eviction
"""

from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from collections import OrderedDict
from threading import Lock
import hashlib
import json


class CacheService:
    """
    Thread-safe in-memory cache with TTL and LRU eviction
    
    Features:
    - Time-to-live (TTL) support
    - LRU eviction when max size reached
    - Thread-safe operations
    - Key generation for function memoization
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize cache service
        
        Args:
            max_size: Maximum number of items in cache
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # OrderedDict for LRU behavior
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._lock = Lock()
    
    def _is_expired(self, item: dict) -> bool:
        """Check if cache item is expired"""
        if 'expires_at' not in item:
            return False
        return datetime.utcnow() > item['expires_at']
    
    def _evict_if_needed(self):
        """Evict oldest item if cache is full (LRU)"""
        if len(self._cache) >= self.max_size:
            # Remove oldest (first) item
            self._cache.popitem(last=False)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # Check expiration
            if self._is_expired(item):
                del self._cache[key]
                return None
            
            # Move to end (mark as recently used)
            self._cache.move_to_end(key)
            
            return item['value']
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for default)
        """
        with self._lock:
            ttl = ttl if ttl else self.default_ttl
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.utcnow()
            }
            
            # Move to end (most recent)
            self._cache.move_to_end(key)
            
            # Evict if needed
            self._evict_if_needed()
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed and was deleted
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            total_size = len(self._cache)
            expired_count = sum(
                1 for item in self._cache.values() if self._is_expired(item)
            )
            
            return {
                'total_items': total_size,
                'expired_items': expired_count,
                'max_size': self.max_size,
                'usage_percent': (total_size / self.max_size) * 100
            }
    
    def clean_expired(self) -> int:
        """Remove all expired entries"""
        with self._lock:
            expired_keys = [
                key for key, item in self._cache.items()
                if self._is_expired(item)
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """
        Generate cache key from function arguments
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Hashed cache key
        """
        # Create stable representation
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        # Hash it
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def memoize(
        self,
        ttl: Optional[int] = None,
        key_prefix: str = ""
    ):
        """
        Decorator for function memoization
        
        Args:
            ttl: Cache TTL in seconds
            key_prefix: Prefix for cache keys
            
        Example:
            @cache_service.memoize(ttl=600, key_prefix="destinations")
            def get_destinations():
                # expensive operation
                return destinations
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{self.generate_key(*args, **kwargs)}"
                
                # Try to get from cache
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator


class CacheManager:
    """
    Manage multiple named caches
    """
    
    def __init__(self):
        self.caches: dict[str, CacheService] = {}
    
    def get_cache(
        self,
        name: str,
        max_size: int = 1000,
        default_ttl: int = 300
    ) -> CacheService:
        """
        Get or create named cache
        
        Args:
            name: Cache name
            max_size: Maximum cache size
            default_ttl: Default TTL
            
        Returns:
            CacheService instance
        """
        if name not in self.caches:
            self.caches[name] = CacheService(max_size, default_ttl)
        return self.caches[name]
    
    def clear_all(self):
        """Clear all caches"""
        for cache in self.caches.values():
            cache.clear()
    
    def get_all_stats(self) -> dict:
        """Get statistics for all caches"""
        return {
            name: cache.get_stats()
            for name, cache in self.caches.items()
        }


# Global cache manager
cache_manager = CacheManager()

# Common caches
destinations_cache = cache_manager.get_cache("destinations", max_size=500, default_ttl=300)
recommendations_cache = cache_manager.get_cache("recommendations", max_size=1000, default_ttl=600)
analytics_cache = cache_manager.get_cache("analytics", max_size=200, default_ttl=900)
