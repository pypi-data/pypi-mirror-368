"""
In-memory caching system for performance optimization.

Provides caching for referrer parser instances and parsed results
to avoid repeated processing of the same data.
"""

import time
from typing import Dict, Optional, Any, Tuple
from threading import Lock


class LRUCache:
    """Simple thread-safe LRU cache implementation."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600) -> None:
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time-to-live for cached items in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self._access_order: Dict[str, int] = {}  # key -> access_counter
        self._access_counter = 0
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if it exists and is not expired."""
        with self._lock:
            if key not in self._cache:
                return None

            value, timestamp = self._cache[key]

            # Check if item has expired
            if self.ttl_seconds > 0 and (time.time() - timestamp) > self.ttl_seconds:
                del self._cache[key]
                if key in self._access_order:
                    del self._access_order[key]
                return None

            # Update access order
            self._access_counter += 1
            self._access_order[key] = self._access_counter

            return value

    def put(self, key: str, value: Any) -> None:
        """Put item in cache, evicting LRU items if necessary."""
        with self._lock:
            current_time = time.time()

            # If cache is at capacity and key doesn't exist, evict LRU item
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()

            # Store item
            self._cache[key] = (value, current_time)
            self._access_counter += 1
            self._access_order[key] = self._access_counter

    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self._access_order:
            return

        # Find key with minimum access counter
        lru_key = min(self._access_order.keys(), key=lambda k: self._access_order[k])

        # Remove from both caches
        if lru_key in self._cache:
            del self._cache[lru_key]
        del self._access_order[lru_key]

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._access_counter = 0

    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)


class ReferrerParserCache:
    """Cached referrer parser instances."""

    def __init__(self) -> None:
        self._parser_cache = LRUCache(max_size=10, ttl_seconds=3600)  # 1 hour TTL
        self._result_cache = LRUCache(max_size=10000, ttl_seconds=1800)  # 30 min TTL

    def get_parser(self, database_hash: str):
        """Get cached parser instance for given database hash."""
        return self._parser_cache.get(database_hash)

    def put_parser(self, database_hash: str, parser) -> None:
        """Cache parser instance with database hash as key."""
        self._parser_cache.put(database_hash, parser)

    def get_parse_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached parse result."""
        return self._result_cache.get(cache_key)

    def put_parse_result(self, cache_key: str, result: Dict) -> None:
        """Cache parse result."""
        self._result_cache.put(cache_key, result)

    def clear(self) -> None:
        """Clear all caches."""
        self._parser_cache.clear()
        self._result_cache.clear()


class ParameterExtractorCache:
    """Cached parameter extraction results."""

    def __init__(self) -> None:
        self._cache = LRUCache(max_size=5000, ttl_seconds=1800)  # 30 min TTL

    def get(self, url: str) -> Optional[Dict[str, str]]:
        """Get cached parameter extraction result."""
        return self._cache.get(url)

    def put(self, url: str, parameters: Dict[str, str]) -> None:
        """Cache parameter extraction result."""
        self._cache.put(url, parameters)

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()


# Global cache instances
_referrer_parser_cache: Optional[ReferrerParserCache] = None
_parameter_extractor_cache: Optional[ParameterExtractorCache] = None


def get_referrer_parser_cache() -> ReferrerParserCache:
    """Get global referrer parser cache instance."""
    global _referrer_parser_cache
    if _referrer_parser_cache is None:
        _referrer_parser_cache = ReferrerParserCache()
    return _referrer_parser_cache


def get_parameter_extractor_cache() -> ParameterExtractorCache:
    """Get global parameter extractor cache instance."""
    global _parameter_extractor_cache
    if _parameter_extractor_cache is None:
        _parameter_extractor_cache = ParameterExtractorCache()
    return _parameter_extractor_cache


def clear_all_caches() -> None:
    """Clear all global caches."""
    global _referrer_parser_cache, _parameter_extractor_cache

    if _referrer_parser_cache:
        _referrer_parser_cache.clear()

    if _parameter_extractor_cache:
        _parameter_extractor_cache.clear()


def create_cache_key(*args: str) -> str:
    """Create cache key from multiple string arguments."""
    return '|'.join(str(arg) for arg in args)
