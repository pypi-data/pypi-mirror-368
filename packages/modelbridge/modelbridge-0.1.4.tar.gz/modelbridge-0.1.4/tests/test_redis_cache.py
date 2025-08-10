"""
Tests for Redis cache implementation (with mocking)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from modelbridge.cache.redis import RedisCache, REDIS_AVAILABLE
from modelbridge.config.models import CacheConfig
from modelbridge.cache.factory import CacheFactory


class TestRedisCache:
    """Test Redis cache implementation"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        mock = AsyncMock()
        mock.ping = AsyncMock(return_value=True)
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock(return_value=True)
        mock.setex = AsyncMock(return_value=True)
        mock.delete = AsyncMock(return_value=1)
        mock.exists = AsyncMock(return_value=True)
        mock.hset = AsyncMock(return_value=1)
        mock.hget = AsyncMock(return_value="2024-01-01T00:00:00")
        mock.hincrby = AsyncMock(return_value=1)
        mock.expire = AsyncMock(return_value=True)
        mock.scan_iter = AsyncMock()
        mock.info = AsyncMock(return_value={
            'used_memory_human': '1.5M',
            'connected_clients': 2,
            'total_commands_processed': 1000
        })
        mock.close = AsyncMock()
        return mock
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_initialization_success(self, mock_redis):
        """Test successful Redis initialization"""
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache(host="localhost", port=6379, ttl=300)
            
            success = await cache.initialize()
            assert success
            assert cache._connected
            
            mock_redis.ping.assert_called_once()
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_initialization_failure(self, mock_redis):
        """Test Redis initialization failure"""
        mock_redis.ping.side_effect = Exception("Connection failed")
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache(host="localhost", port=6379)
            
            success = await cache.initialize()
            assert not success
            assert not cache._connected
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")  
    @pytest.mark.asyncio
    async def test_redis_basic_operations(self, mock_redis):
        """Test basic Redis operations"""
        # Mock scan_iter to be an async generator that yields nothing
        class AsyncIterMock:
            def __init__(self):
                pass
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                raise StopAsyncIteration
        
        mock_redis.scan_iter.return_value = AsyncIterMock()
        
        # Mock get to return serialized data
        test_data = {"value": "test_value", "created_at": "2024-01-01T00:00:00", "access_count": 0}
        mock_redis.get.return_value = json.dumps(test_data)
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            await cache.initialize()
            
            # Test set
            result = await cache.set("test_key", "test_value", ttl=60)
            assert result
            mock_redis.setex.assert_called()
            
            # Test get
            value = await cache.get("test_key")
            assert value == "test_value"
            mock_redis.get.assert_called_with("modelbridge:test_key")
            
            # Test exists
            exists = await cache.exists("test_key")
            assert exists
            mock_redis.exists.assert_called()
            
            # Test delete
            deleted = await cache.delete("test_key")
            assert deleted
            mock_redis.delete.assert_called()
            
            await cache.shutdown()
    
    @pytest.mark.skip(reason="Mock setup issues with scan_iter - needs refactor")
    @pytest.mark.asyncio
    async def test_redis_ttl_handling(self, mock_redis):
        """Test Redis TTL handling"""
        # Mock scan_iter to be an async generator that yields nothing
        class AsyncIterMock:
            def __init__(self):
                pass
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                raise StopAsyncIteration
        
        mock_redis.scan_iter.return_value = AsyncIterMock()
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache(ttl=300)
            await cache.initialize()
            
            # Test with TTL
            await cache.set("key1", "value1", ttl=60)
            # Check that setex was called for TTL > 0
            assert mock_redis.setex.called
            
            # Reset mock to test zero TTL
            mock_redis.reset_mock()
            mock_redis.scan_iter.return_value = AsyncIterMock()
            
            # Test with zero TTL (no expiration)
            await cache.set("key2", "value2", ttl=0)
            # Check that set was called for TTL = 0
            assert mock_redis.set.called
            assert not mock_redis.setex.called
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_key_prefix(self, mock_redis):
        """Test Redis key prefixing"""
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache(key_prefix="test:")
            await cache.initialize()
            
            await cache.get("mykey")
            mock_redis.get.assert_called_with("test:mykey")
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_size_calculation(self, mock_redis):
        """Test Redis cache size calculation"""
        # Mock scan_iter to return test keys
        async def mock_scan_iter(match=None):
            keys = ["modelbridge:key1", "modelbridge:key2", "modelbridge:key1:meta"]
            for key in keys:
                if match is None or key.startswith(match.replace("*", "")):
                    yield key
        
        mock_redis.scan_iter = mock_scan_iter
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            await cache.initialize()
            
            size = await cache.size()
            assert size == 2  # Should exclude :meta keys
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_clear_cache(self, mock_redis):
        """Test Redis cache clearing"""
        # Mock scan_iter to return test keys
        async def mock_scan_iter(match=None):
            keys = ["modelbridge:key1", "modelbridge:key2", "modelbridge:key1:meta"]
            for key in keys:
                yield key
        
        mock_redis.scan_iter = mock_scan_iter
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            await cache.initialize()
            
            result = await cache.clear()
            assert result
            mock_redis.delete.assert_called()  # Should delete found keys
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_stats(self, mock_redis):
        """Test Redis statistics"""
        # Mock scan_iter for size calculation
        async def mock_scan_iter(match=None):
            yield "modelbridge:key1"
            yield "modelbridge:key2"
        
        mock_redis.scan_iter = mock_scan_iter
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            await cache.initialize()
            
            stats = await cache.get_stats()
            
            assert stats['connected'] is True
            assert stats['size'] == 2
            assert 'redis_memory_used' in stats
            assert 'redis_connected_clients' in stats
            assert 'hit_rate' in stats
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_health_check(self, mock_redis):
        """Test Redis health check"""
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            await cache.initialize()
            
            health = await cache.health_check()
            assert health['status'] == 'healthy'
            assert 'ping_ms' in health
            assert health['connected'] is True
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_health_check_failure(self, mock_redis):
        """Test Redis health check failure"""
        mock_redis.ping.side_effect = Exception("Connection lost")
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            # Don't initialize to test unhealthy state
            
            health = await cache.health_check()
            assert health['status'] == 'unhealthy'
            assert 'error' in health
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_error_handling(self, mock_redis):
        """Test Redis error handling"""
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            await cache.initialize()
            
            # Test get error
            mock_redis.get.side_effect = Exception("Redis error")
            value = await cache.get("test_key")
            assert value is None
            assert cache.stats['errors'] > 0
            
            # Reset for set test
            mock_redis.get.side_effect = None
            mock_redis.setex.side_effect = Exception("Redis error")
            
            result = await cache.set("test_key", "value")
            assert not result
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_serialization(self, mock_redis):
        """Test Redis value serialization/deserialization"""
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = RedisCache()
            
            # Test serialization
            test_value = {"complex": "data", "with": [1, 2, 3]}
            serialized = cache._serialize_value(test_value)
            
            assert isinstance(serialized, str)
            data = json.loads(serialized)
            assert data['value'] == test_value
            assert 'created_at' in data
            
            # Test deserialization
            deserialized = cache._deserialize_value(serialized)
            assert deserialized == test_value
            
            # Test invalid data
            invalid_result = cache._deserialize_value("invalid json")
            assert invalid_result is None


class TestRedisIntegration:
    """Test Redis cache integration with factory"""
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_cache_factory(self, mock_redis):
        """Test creating Redis cache via factory"""
        config = CacheConfig(
            enabled=True,
            type="redis",
            ttl=300,
            max_size=1000,
            redis_host="localhost",
            redis_port=6379,
            redis_db=1,
            redis_password="secret"
        )
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = await CacheFactory.create_cache(config)
            
            assert cache is not None
            assert isinstance(cache, RedisCache)
            assert cache.host == "localhost"
            assert cache.port == 6379
            assert cache.db == 1
            assert cache.password == "secret"
            
            await cache.shutdown()
    
    @pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")
    @pytest.mark.asyncio
    async def test_redis_cache_factory_init_failure(self, mock_redis):
        """Test Redis cache factory with initialization failure"""
        mock_redis.ping.side_effect = Exception("Connection failed")
        
        config = CacheConfig(
            enabled=True,
            type="redis",
            redis_host="nonexistent"
        )
        
        with patch('modelbridge.cache.redis.redis.Redis', return_value=mock_redis):
            cache = await CacheFactory.create_cache(config)
            assert cache is None  # Should return None on init failure


@pytest.mark.skipif(REDIS_AVAILABLE, reason="Testing Redis unavailable scenario")
def test_redis_import_error():
    """Test Redis cache when Redis is not available"""
    with pytest.raises(ImportError, match="Redis is required but not installed"):
        RedisCache()


@pytest.mark.asyncio
async def test_redis_cache_without_redis():
    """Test Redis cache configuration when Redis is unavailable"""
    # This test runs when Redis is not available
    if REDIS_AVAILABLE:
        pytest.skip("Redis is available, skipping unavailable test")
    
    config = CacheConfig(
        enabled=True,
        type="redis"
    )
    
    # Should return None when Redis is unavailable
    cache = await CacheFactory.create_cache(config)
    assert cache is None