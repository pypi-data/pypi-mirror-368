"""
Smart caching utilities for TWGY_V3 system
Provides TTL, LRU, and performance-aware caching strategies
"""

import time
import threading
from typing import Any, Dict, Optional, Callable, TypeVar, Generic, Union
from dataclasses import dataclass
from collections import OrderedDict
import logging

from ..core.constants import Performance
from ..core.exceptions import CacheError, ErrorCode

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def reset(self) -> None:
        """Reset all statistics"""
        self.hits = 0
        self.misses = 0
        self.evictions = 0


@dataclass
class CacheEntry(Generic[V]):
    """Cache entry with metadata"""
    value: V
    access_time: float
    creation_time: float
    access_count: int = 0
    
    @property
    def age(self) -> float:
        """Age of entry in seconds"""
        return time.time() - self.creation_time
    
    @property
    def idle_time(self) -> float:
        """Time since last access in seconds"""
        return time.time() - self.access_time
    
    def touch(self) -> None:
        """Update access metadata"""
        self.access_time = time.time()
        self.access_count += 1


class SmartCache(Generic[K, V]):
    """
    Smart cache with TTL, LRU, and adaptive eviction
    
    Features:
    - TTL (Time To Live) expiration
    - LRU (Least Recently Used) eviction
    - Thread-safe operations
    - Performance monitoring
    - Adaptive size management
    """
    
    def __init__(
        self,
        max_size: int = Performance.DEFAULT_CACHE_SIZE,
        ttl_seconds: Optional[float] = Performance.DEFAULT_CACHE_TTL_SECONDS,
        enable_stats: bool = True,
        name: str = "default"
    ):
        """
        Initialize smart cache
        
        Args:
            max_size: Maximum number of entries
            ttl_seconds: Time-to-live in seconds (None for no expiration)
            enable_stats: Whether to collect statistics
            name: Cache name for logging
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.enable_stats = enable_stats
        self.name = name
        
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats(max_size=max_size) if enable_stats else None
        
        logger.debug(f"SmartCache '{name}' initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._record_miss()
                return default
            
            # Check TTL expiration
            if self._is_expired(entry):
                del self._cache[key]
                self._record_miss()
                self._record_eviction()
                return default
            
            # Update access metadata
            entry.touch()
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            self._record_hit()
            return entry.value
    
    def put(self, key: K, value: V) -> None:
        """
        Put value into cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            current_time = time.time()
            
            # Remove existing entry if present
            if key in self._cache:
                del self._cache[key]
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                access_time=current_time,
                creation_time=current_time,
                access_count=1
            )
            
            # Add to cache
            self._cache[key] = entry
            self._cache.move_to_end(key)  # Mark as most recently used
            
            # Enforce size limit
            while len(self._cache) > self.max_size:
                self._evict_lru()
            
            # Update stats
            if self._stats:
                self._stats.size = len(self._cache)
    
    def delete(self, key: K) -> bool:
        """
        Delete entry from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if entry was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if self._stats:
                    self._stats.size = len(self._cache)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            if self._stats:
                self._stats.size = 0
                self._stats.evictions += len(self._cache)
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries
        
        Returns:
            Number of entries removed
        """
        if self.ttl_seconds is None:
            return 0
        
        removed_count = 0
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if self._is_expired(entry)
            ]
            
            for key in expired_keys:
                del self._cache[key]
                removed_count += 1
                self._record_eviction()
            
            if self._stats:
                self._stats.size = len(self._cache)
        
        if removed_count > 0:
            logger.debug(f"Cache '{self.name}': cleaned up {removed_count} expired entries")
        
        return removed_count
    
    def resize(self, new_max_size: int) -> None:
        """
        Resize cache maximum size
        
        Args:
            new_max_size: New maximum size
        """
        with self._lock:
            self.max_size = new_max_size
            
            # Evict entries if necessary
            while len(self._cache) > self.max_size:
                self._evict_lru()
            
            if self._stats:
                self._stats.max_size = new_max_size
                self._stats.size = len(self._cache)
        
        logger.debug(f"Cache '{self.name}' resized to {new_max_size}")
    
    def get_stats(self) -> Optional[CacheStats]:
        """Get cache statistics"""
        return self._stats
    
    def get_info(self) -> Dict[str, Any]:
        """Get cache information"""
        with self._lock:
            info = {
                "name": self.name,
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "enable_stats": self.enable_stats
            }
            
            if self._stats:
                info.update({
                    "hits": self._stats.hits,
                    "misses": self._stats.misses,
                    "hit_rate": self._stats.hit_rate,
                    "evictions": self._stats.evictions
                })
        
        return info
    
    def _is_expired(self, entry: CacheEntry[V]) -> bool:
        """Check if cache entry is expired"""
        if self.ttl_seconds is None:
            return False
        return entry.age > self.ttl_seconds
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self._cache:
            # OrderedDict maintains insertion order, first item is LRU
            self._cache.popitem(last=False)
            self._record_eviction()
    
    def _record_hit(self) -> None:
        """Record cache hit"""
        if self._stats:
            self._stats.hits += 1
    
    def _record_miss(self) -> None:
        """Record cache miss"""
        if self._stats:
            self._stats.misses += 1
    
    def _record_eviction(self) -> None:
        """Record cache eviction"""
        if self._stats:
            self._stats.evictions += 1


class CacheManager:
    """
    Global cache manager for multiple named caches
    """
    
    def __init__(self):
        self._caches: Dict[str, SmartCache] = {}
        self._lock = threading.RLock()
        
        logger.debug("CacheManager initialized")
    
    def get_cache(
        self,
        name: str,
        max_size: int = Performance.DEFAULT_CACHE_SIZE,
        ttl_seconds: Optional[float] = Performance.DEFAULT_CACHE_TTL_SECONDS,
        **kwargs
    ) -> SmartCache:
        """
        Get or create named cache
        
        Args:
            name: Cache name
            max_size: Maximum cache size
            ttl_seconds: TTL in seconds
            **kwargs: Additional cache options
            
        Returns:
            SmartCache instance
        """
        with self._lock:
            if name not in self._caches:
                self._caches[name] = SmartCache(
                    max_size=max_size,
                    ttl_seconds=ttl_seconds,
                    name=name,
                    **kwargs
                )
                logger.debug(f"Created new cache: '{name}'")
            
            return self._caches[name]
    
    def clear_cache(self, name: str) -> bool:
        """
        Clear specific cache
        
        Args:
            name: Cache name
            
        Returns:
            True if cache was cleared, False if not found
        """
        with self._lock:
            if name in self._caches:
                self._caches[name].clear()
                logger.debug(f"Cleared cache: '{name}'")
                return True
            return False
    
    def clear_all_caches(self) -> None:
        """Clear all caches"""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()
            logger.debug("Cleared all caches")
    
    def cleanup_expired(self) -> Dict[str, int]:
        """
        Cleanup expired entries from all caches
        
        Returns:
            Dictionary of cache name to count of expired entries removed
        """
        results = {}
        
        with self._lock:
            for name, cache in self._caches.items():
                count = cache.cleanup_expired()
                if count > 0:
                    results[name] = count
        
        return results
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        stats = {}
        
        with self._lock:
            for name, cache in self._caches.items():
                stats[name] = cache.get_info()
        
        return stats
    
    def remove_cache(self, name: str) -> bool:
        """
        Remove cache entirely
        
        Args:
            name: Cache name
            
        Returns:
            True if cache was removed, False if not found
        """
        with self._lock:
            if name in self._caches:
                del self._caches[name]
                logger.debug(f"Removed cache: '{name}'")
                return True
            return False


def cached(
    cache_name: str = "default",
    ttl_seconds: Optional[float] = None,
    max_size: int = Performance.DEFAULT_CACHE_SIZE,
    key_func: Optional[Callable[..., str]] = None
) -> Callable:
    """
    Decorator for caching function results
    
    Args:
        cache_name: Name of cache to use
        ttl_seconds: TTL for cached results
        max_size: Maximum cache size
        key_func: Custom function to generate cache keys
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Get or create cache
        cache = _cache_manager.get_cache(
            name=f"{cache_name}_{func.__name__}",
            max_size=max_size,
            ttl_seconds=ttl_seconds
        )
        
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{args}_{kwargs}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                cache.put(key, result)
                return result
            except Exception as e:
                logger.error(f"Cached function '{func.__name__}' failed: {e}")
                raise
        
        # Add cache management methods to function
        wrapper.clear_cache = lambda: cache.clear()
        wrapper.get_cache_stats = lambda: cache.get_stats()
        wrapper.get_cache_info = lambda: cache.get_info()
        
        return wrapper
    
    return decorator


# Global cache manager instance
_cache_manager = CacheManager()

# Convenience functions
def get_cache(name: str, **kwargs) -> SmartCache:
    """Get named cache from global manager"""
    return _cache_manager.get_cache(name, **kwargs)

def clear_cache(name: str) -> bool:
    """Clear named cache"""
    return _cache_manager.clear_cache(name)

def clear_all_caches() -> None:
    """Clear all caches"""
    _cache_manager.clear_all_caches()

def cleanup_expired() -> Dict[str, int]:
    """Cleanup expired entries from all caches"""
    return _cache_manager.cleanup_expired()

def get_all_cache_stats() -> Dict[str, Any]:
    """Get statistics for all caches"""
    return _cache_manager.get_all_stats()