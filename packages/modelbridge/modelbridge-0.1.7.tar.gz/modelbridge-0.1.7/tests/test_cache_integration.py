"""
Integration tests for the caching system
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from modelbridge.cache import MemoryCache, CacheFactory
from modelbridge.cache.decorators import CacheManager
from modelbridge.config.models import CacheConfig
from modelbridge.config_bridge import ValidatedModelBridge


class TestCacheIntegration:
    """Test cache integration with ModelBridge"""
    
    @pytest.mark.asyncio
    async def test_memory_cache_basic_operations(self):
        """Test basic memory cache operations"""
        cache = MemoryCache(ttl=60, max_size=100)
        await cache.initialize()
        
        try:
            # Basic operations
            assert await cache.set("test_key", "test_value")
            assert await cache.get("test_key") == "test_value"
            assert await cache.exists("test_key")
            
            # Statistics
            stats = await cache.get_stats()
            assert stats["size"] == 1
            
            # Clear
            assert await cache.clear()
            assert await cache.size() == 0
            
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_factory(self):
        """Test cache factory creation"""
        # Memory cache
        config = CacheConfig(enabled=True, type="memory", ttl=300, max_size=500)
        cache = await CacheFactory.create_cache(config)
        
        assert cache is not None
        assert isinstance(cache, MemoryCache)
        
        await cache.shutdown()
        
        # Disabled cache
        config = CacheConfig(enabled=False)
        cache = await CacheFactory.create_cache(config)
        assert cache is None
    
    @pytest.mark.asyncio
    async def test_cache_manager(self):
        """Test cache manager functionality"""
        cache = MemoryCache(ttl=60, max_size=100)
        await cache.initialize()
        manager = CacheManager(cache)
        
        try:
            call_count = 0
            
            async def test_function(x: int) -> int:
                nonlocal call_count
                call_count += 1
                return x * 2
            
            # First call - should execute function
            result1 = await manager.get_or_compute("test_key", test_function, None, 5)
            assert result1 == 10
            assert call_count == 1
            
            # Second call - should use cache  
            result2 = await manager.get_or_compute("test_key", test_function, None, 5)
            assert result2 == 10
            assert call_count == 1  # Should not increment
            
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_model_bridge_cache_integration(self):
        """Test cache integration with ValidatedModelBridge"""
        # Create config with caching enabled
        config_dict = {
            "cache": {
                "enabled": True,
                "type": "memory",
                "ttl": 300,
                "max_size": 100
            },
            "providers": {},  # No providers for this test
            "routing": {"fallback_enabled": False}
        }
        
        bridge = ValidatedModelBridge(config_dict)
        
        # Initialize should set up cache
        success = await bridge.initialize()
        # May fail due to no providers, but cache should be initialized
        
        # Check cache was created
        assert bridge.cache is not None
        assert bridge.cache_manager is not None
        
        # Test cache methods
        stats = await bridge.get_cache_stats()
        assert stats is not None
        assert "size" in stats
        
        # Test clear cache
        result = await bridge.clear_cache()
        assert result is True
        
        await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_with_ttl(self):
        """Test cache TTL functionality"""
        cache = MemoryCache(ttl=60, max_size=100)
        await cache.initialize()
        
        try:
            # Set with custom TTL
            await cache.set("short_ttl", "value", ttl=1)
            assert await cache.get("short_ttl") == "value"
            
            # Wait and check expiration
            await asyncio.sleep(1.1)
            assert await cache.get("short_ttl") is None
            
        finally:
            await cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_eviction(self):
        """Test cache eviction when size limit reached"""
        cache = MemoryCache(ttl=60, max_size=3)  # Small cache
        await cache.initialize()
        
        try:
            # Fill cache to limit
            await cache.set("key1", "value1")
            await cache.set("key2", "value2") 
            await cache.set("key3", "value3")
            
            assert await cache.size() == 3
            
            # Add one more - should evict oldest
            await cache.set("key4", "value4")
            assert await cache.size() == 3
            
            # First key should be gone
            assert await cache.get("key1") is None
            assert await cache.get("key4") == "value4"
            
        finally:
            await cache.shutdown()


class TestCacheConfiguration:
    """Test cache configuration scenarios"""
    
    @pytest.mark.asyncio
    async def test_cache_disabled_config(self):
        """Test ModelBridge with cache disabled"""
        config_dict = {
            "cache": {"enabled": False},
            "providers": {},
            "routing": {"fallback_enabled": False}
        }
        
        bridge = ValidatedModelBridge(config_dict)
        await bridge.initialize()
        
        # Cache should be None when disabled
        stats = await bridge.get_cache_stats()
        assert stats is None
        
        await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_cache_fallback_creation(self):
        """Test fallback cache creation"""
        cache = await CacheFactory.create_fallback_cache(ttl=120, max_size=50)
        
        assert cache is not None
        assert isinstance(cache, MemoryCache)
        assert cache.ttl == 120
        assert cache.max_size == 50
        
        await cache.shutdown()


class TestCacheKeyGeneration:
    """Test cache key generation"""
    
    def test_cache_key_generation(self):
        """Test cache key generation consistency"""
        cache = MemoryCache()
        
        # Same inputs should generate same key
        key1 = cache.generate_key("prompt", model="gpt-4", temp=0.7)
        key2 = cache.generate_key("prompt", model="gpt-4", temp=0.7)
        assert key1 == key2
        
        # Different inputs should generate different keys
        key3 = cache.generate_key("different", model="gpt-4", temp=0.7)
        assert key1 != key3
        
        # Key should be reasonable length
        assert len(key1) == 32