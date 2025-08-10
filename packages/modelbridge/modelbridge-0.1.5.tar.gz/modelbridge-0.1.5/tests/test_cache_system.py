"""
Tests for the caching system
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from modelbridge.cache import (
    CacheInterface, 
    CacheEntry, 
    MemoryCache, 
    CacheFactory
)
from modelbridge.cache.decorators import cached, CacheManager
from modelbridge.config.models import CacheConfig


async def create_memory_cache(ttl=3600, max_size=10):
    """Create and initialize a memory cache for testing"""
    cache = MemoryCache(ttl=ttl, max_size=max_size)
    await cache.initialize()
    return cache


class TestCacheEntry:
    """Test CacheEntry functionality"""
    
    def test_cache_entry_creation(self):
        """Test creating cache entry"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=60)
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.access_count == 0
        assert entry.last_accessed is None
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration"""
        # Not expired
        entry = CacheEntry(
            key="test",
            value="value", 
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=60)
        )
        assert not entry.is_expired()
        
        # Expired
        entry_expired = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.utcnow() - timedelta(seconds=120),
            expires_at=datetime.utcnow() - timedelta(seconds=60)
        )
        assert entry_expired.is_expired()
        
        # No expiration
        entry_no_expire = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.utcnow(),
            expires_at=None
        )
        assert not entry_no_expire.is_expired()
    
    def test_cache_entry_access(self):
        """Test cache entry access tracking"""
        entry = CacheEntry(
            key="test",
            value="value",
            created_at=datetime.utcnow(),
            expires_at=None
        )
        
        assert entry.access_count == 0
        assert entry.last_accessed is None
        
        entry.access()
        assert entry.access_count == 1
        assert entry.last_accessed is not None
        
        entry.access()
        assert entry.access_count == 2
    
    def test_cache_entry_serialization(self):
        """Test cache entry to/from dict"""
        now = datetime.utcnow()
        expires = now + timedelta(seconds=60)
        
        entry = CacheEntry(
            key="test",
            value={"data": "value"},
            created_at=now,
            expires_at=expires,
            access_count=5
        )
        entry.access()  # Update last_accessed
        
        # To dict
        data = entry.to_dict()
        assert data["key"] == "test"
        assert data["value"] == {"data": "value"}
        assert data["access_count"] == 6  # After access()
        
        # From dict
        restored = CacheEntry.from_dict(data)
        assert restored.key == entry.key
        assert restored.value == entry.value
        assert restored.access_count == entry.access_count


class TestMemoryCache:
    """Test MemoryCache implementation"""
    
    @pytest.mark.asyncio
    async def test_basic_operations(self):
        """Test basic cache operations"""
        cache = MemoryCache(ttl=60, max_size=10)
        await cache.initialize()
        
        try:
            # Set and get
            assert await cache.set("key1", "value1")
            assert await cache.get("key1") == "value1"
            
            # Exists
            assert await cache.exists("key1")
            assert not await cache.exists("nonexistent")
            
            # Delete
            assert await cache.delete("key1")
            assert not await cache.exists("key1")
            assert await cache.get("key1") is None
            
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        """Test TTL expiration"""
        memory_cache = await create_memory_cache(ttl=3600, max_size=10)
        
        try:
            # Set with short TTL
            await memory_cache.set("expire_key", "value", ttl=1)
            assert await memory_cache.get("expire_key") == "value"
            
            # Wait for expiration
            await asyncio.sleep(1.1)
            assert await memory_cache.get("expire_key") is None
        finally:
            await memory_cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_size_limits(self):
        """Test cache size limits"""
        memory_cache = await create_memory_cache(ttl=3600, max_size=10)
        
        try:
            # Fill cache to max size
            for i in range(10):
                await memory_cache.set(f"key_{i}", f"value_{i}")
            
            assert await memory_cache.size() == 10
            
            # Add one more - should evict oldest
            await memory_cache.set("overflow", "value")
            assert await memory_cache.size() == 10
            
            # First key should be evicted
            assert await memory_cache.get("key_0") is None
            assert await memory_cache.get("overflow") == "value"
        finally:
            await memory_cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_lru_behavior(self):
        """Test LRU eviction behavior"""
        memory_cache = await create_memory_cache(ttl=3600, max_size=10)
        
        try:
            # Fill cache
            for i in range(10):
                await memory_cache.set(f"key_{i}", f"value_{i}")
            
            # Access key_0 to make it recently used
            await memory_cache.get("key_0")
            
            # Add new item - should evict key_1 (oldest unaccessed)
            await memory_cache.set("new_key", "new_value")
            
            assert await memory_cache.get("key_0") == "value_0"  # Should still exist
            assert await memory_cache.get("key_1") is None      # Should be evicted
            assert await memory_cache.get("new_key") == "new_value"
        finally:
            await memory_cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_stats(self):
        """Test cache statistics"""
        memory_cache = await create_memory_cache(ttl=3600, max_size=10)
        
        try:
            initial_stats = await memory_cache.get_stats()
            assert initial_stats["size"] == 0
            assert initial_stats["hits"] == 0
            assert initial_stats["misses"] == 0
            
            # Set some values
            await memory_cache.set("key1", "value1")
            await memory_cache.set("key2", "value2")
            
            # Get hits and misses
            await memory_cache.get_with_stats("key1")  # Hit
            await memory_cache.get_with_stats("nonexistent")  # Miss
            
            stats = await memory_cache.get_stats()
            assert stats["size"] == 2
            assert stats["hits"] == 1
            assert stats["misses"] == 1
            assert stats["hit_rate"] == 0.5
        finally:
            await memory_cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self):
        """Test cleanup of expired entries"""
        memory_cache = await create_memory_cache(ttl=3600, max_size=10)
        
        try:
            # Add entries with different TTL
            await memory_cache.set("key1", "value1", ttl=10)  # Long TTL
            await memory_cache.set("key2", "value2", ttl=1)   # Short TTL
            
            assert await memory_cache.size() == 2
            
            # Wait for short TTL to expire
            await asyncio.sleep(1.1)
            
            # Cleanup expired entries
            expired_count = await memory_cache.cleanup_expired()
            assert expired_count == 1
            assert await memory_cache.size() == 1
            assert await memory_cache.exists("key1")
            assert not await memory_cache.exists("key2")
        finally:
            await memory_cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_clear(self):
        """Test clearing cache"""
        memory_cache = await create_memory_cache(ttl=3600, max_size=10)
        
        try:
            # Add multiple entries
            for i in range(5):
                await memory_cache.set(f"key_{i}", f"value_{i}")
            
            assert await memory_cache.size() == 5
            
            # Clear cache
            await memory_cache.clear()
            assert await memory_cache.size() == 0
            
            # Verify all entries are gone
            for i in range(5):
                assert not await memory_cache.exists(f"key_{i}")
        finally:
            await memory_cache.shutdown()


class TestCacheFactory:
    """Test CacheFactory"""
    
    @pytest.mark.asyncio
    async def test_create_memory_cache(self):
        """Test creating memory cache via factory"""
        config = CacheConfig(
            enabled=True,
            type="memory",
            ttl=300,
            max_size=500
        )
        
        cache = await CacheFactory.create_cache(config)
        assert cache is not None
        assert isinstance(cache, MemoryCache)
        assert cache.ttl == 300
        assert cache.max_size == 500
        
        await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_create_disabled_cache(self):
        """Test creating disabled cache"""
        config = CacheConfig(enabled=False)
        cache = await CacheFactory.create_cache(config)
        assert cache is None
    
    @pytest.mark.asyncio
    async def test_create_unknown_cache_type(self):
        """Test creating cache with unknown type"""
        from pydantic import ValidationError
        
        # Pydantic should validate the config and reject unknown types
        with pytest.raises(ValidationError):
            config = CacheConfig(
                enabled=True,
                type="unknown"
            )
    
    @pytest.mark.asyncio
    async def test_create_fallback_cache(self):
        """Test creating fallback cache"""
        cache = await CacheFactory.create_fallback_cache(ttl=120, max_size=50)
        assert cache is not None
        assert isinstance(cache, MemoryCache)
        assert cache.ttl == 120
        assert cache.max_size == 50
        
        await cache.shutdown()
    
    def test_supported_types(self):
        """Test getting supported cache types"""
        types = CacheFactory.get_supported_types()
        assert "memory" in types
        assert "redis" in types


class TestCacheDecorators:
    """Test cache decorators"""
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self):
        """Test @cached decorator"""
        cache = await create_memory_cache(ttl=60, max_size=100)
        
        try:
            call_count = 0
            
            @cached(cache, ttl=30)
            async def expensive_function(x: int, y: int) -> int:
                nonlocal call_count
                call_count += 1
                return x + y
            
            # First call - should execute function
            result1 = await expensive_function(1, 2)
            assert result1 == 3
            assert call_count == 1
            
            # Second call with same args - should use cache
            result2 = await expensive_function(1, 2)
            assert result2 == 3
            assert call_count == 1  # Not incremented
            
            # Different args - should execute function
            result3 = await expensive_function(2, 3)
            assert result3 == 5
            assert call_count == 2
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_manager(self):
        """Test CacheManager"""
        cache = await create_memory_cache(ttl=60, max_size=100)
        
        try:
            manager = CacheManager(cache)
            
            call_count = 0
            
            async def compute_value(x: int) -> int:
                nonlocal call_count
                call_count += 1
                return x * 2
            
            # First call - should compute
            result1 = await manager.get_or_compute("test_key", compute_value, None, 5)
            assert result1 == 10
            assert call_count == 1
            
            # Second call - should use cache
            result2 = await manager.get_or_compute("test_key", compute_value, None, 5)
            assert result2 == 10
            assert call_count == 1  # Not incremented
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_manager_concurrent_requests(self):
        """Test CacheManager with concurrent requests"""
        cache = await create_memory_cache(ttl=60, max_size=100)
        
        try:
            manager = CacheManager(cache)
            
            call_count = 0
            
            async def slow_compute_value(x: int) -> int:
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.1)  # Simulate slow computation
                return x * 3
            
            # Start multiple concurrent requests for same key
            tasks = [
                manager.get_or_compute("concurrent_key", slow_compute_value, None, 7)
                for _ in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All should return same result
            assert all(result == 21 for result in results)
            
            # Function should only be called once
            assert call_count == 1
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_info(self):
        """Test cache info"""
        cache = await create_memory_cache(ttl=60, max_size=100)
        
        try:
            manager = CacheManager(cache)
            
            # Add some data
            await cache.set("key1", "value1")
            await cache.get_with_stats("key1")  # Generate hit
            await cache.get_with_stats("nonexistent")  # Generate miss
            
            info = await manager.get_cache_info()
            
            assert info["cache_type"] == "MemoryCache"
            assert info["size"] == 1
            assert info["hits"] == 1
            assert info["misses"] == 1
            assert "timestamp" in info
        finally:
            await cache.shutdown()


class TestCacheIntegration:
    """Test cache integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_cache_with_different_data_types(self):
        """Test caching different data types"""
        cache = MemoryCache(ttl=60, max_size=100)
        await cache.initialize()
        
        try:
            # Test various data types
            test_data = [
                ("string", "hello world"),
                ("int", 42),
                ("float", 3.14159),
                ("bool", True),
                ("list", [1, 2, 3, "four"]),
                ("dict", {"key": "value", "number": 123}),
                ("none", None)
            ]
            
            # Set all values
            for key, value in test_data:
                assert await cache.set(key, value)
            
            # Get and verify all values
            for key, expected_value in test_data:
                cached_value = await cache.get(key)
                assert cached_value == expected_value
                
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance characteristics"""
        cache = MemoryCache(ttl=300, max_size=1000)
        await cache.initialize()
        
        try:
            # Measure set performance
            start_time = time.time()
            for i in range(100):
                await cache.set(f"perf_key_{i}", f"value_{i}")
            set_time = time.time() - start_time
            
            # Measure get performance
            start_time = time.time()
            for i in range(100):
                await cache.get(f"perf_key_{i}")
            get_time = time.time() - start_time
            
            # Basic performance assertions
            assert set_time < 1.0  # Should set 100 items in under 1 second
            assert get_time < 0.5  # Should get 100 items in under 0.5 seconds
            
            print(f"Set 100 items in {set_time:.3f}s")
            print(f"Got 100 items in {get_time:.3f}s")
            
        finally:
            await cache.shutdown()


@pytest.mark.asyncio
async def test_key_generation():
    """Test cache key generation"""
    cache = MemoryCache()
    
    # Test with various arguments
    key1 = cache.generate_key("arg1", "arg2", kwarg1="value1", kwarg2="value2")
    key2 = cache.generate_key("arg1", "arg2", kwarg1="value1", kwarg2="value2")
    key3 = cache.generate_key("arg1", "arg2", kwarg1="value1", kwarg2="different")
    
    # Same arguments should generate same key
    assert key1 == key2
    
    # Different arguments should generate different keys
    assert key1 != key3
    
    # Keys should be reasonable length
    assert len(key1) == 32  # SHA256 truncated to 32 chars