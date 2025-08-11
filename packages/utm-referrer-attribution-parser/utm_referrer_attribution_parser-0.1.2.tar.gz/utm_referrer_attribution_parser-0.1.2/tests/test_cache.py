"""Tests for caching functionality."""

import time
import pytest
from utm_referrer_parser.cache import LRUCache, ReferrerParserCache, ParameterExtractorCache


class TestLRUCache:
    """Tests for LRU cache implementation."""
    
    def test_basic_get_put(self):
        """Test basic get/put operations."""
        cache = LRUCache(max_size=3, ttl_seconds=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("nonexistent") is None
    
    def test_size_limit(self):
        """Test cache size limit and LRU eviction."""
        cache = LRUCache(max_size=2, ttl_seconds=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_lru_order(self):
        """Test LRU eviction order."""
        cache = LRUCache(max_size=2, ttl_seconds=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Access key1 to make it more recently used
        cache.get("key1")
        
        # Add key3 - should evict key2, not key1
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = LRUCache(max_size=10, ttl_seconds=1)
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_update_existing_key(self):
        """Test updating existing key."""
        cache = LRUCache(max_size=2, ttl_seconds=10)
        
        cache.put("key1", "value1")
        cache.put("key1", "updated_value1")
        
        assert cache.get("key1") == "updated_value1"
        assert cache.size() == 1
    
    def test_clear(self):
        """Test cache clearing."""
        cache = LRUCache(max_size=10, ttl_seconds=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size() == 0


class TestReferrerParserCache:
    """Tests for referrer parser cache."""
    
    def test_parser_caching(self):
        """Test parser instance caching."""
        cache = ReferrerParserCache()
        
        # Mock parser object
        mock_parser = {"type": "mock_parser"}
        
        cache.put_parser("hash123", mock_parser)
        retrieved = cache.get_parser("hash123")
        
        assert retrieved == mock_parser
    
    def test_result_caching(self):
        """Test parse result caching."""
        cache = ReferrerParserCache()
        
        result = {"source": "google", "medium": "organic"}
        
        cache.put_parse_result("cache_key", result)
        retrieved = cache.get_parse_result("cache_key")
        
        assert retrieved == result


class TestParameterExtractorCache:
    """Tests for parameter extractor cache."""
    
    def test_parameter_caching(self):
        """Test parameter extraction result caching."""
        cache = ParameterExtractorCache()
        
        params = {"utm_source": "google", "utm_medium": "cpc"}
        url = "https://example.com/?utm_source=google&utm_medium=cpc"
        
        cache.put(url, params)
        retrieved = cache.get(url)
        
        assert retrieved == params
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = ParameterExtractorCache()
        
        result = cache.get("nonexistent_url")
        
        assert result is None