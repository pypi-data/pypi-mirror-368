"""
Redis cache implementation
"""
import asyncio
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta

from .base import CacheInterface, CacheEntry

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available. Install with: pip install redis")
    REDIS_AVAILABLE = False


class RedisCache(CacheInterface):
    """Redis-based cache implementation"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl: int = 3600,
        max_size: int = 10000,
        key_prefix: str = "modelbridge:",
        **kwargs
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is required but not installed. Install with: pip install redis")
        
        super().__init__(ttl, max_size)
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.key_prefix = key_prefix
        self.redis_kwargs = kwargs
        
        self._redis: Optional[redis.Redis] = None
        self._connected = False
    
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        try:
            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                **self.redis_kwargs
            )
            
            # Test connection
            await self._redis.ping()
            self._connected = True
            
            logger.info(
                f"Redis cache initialized - {self.host}:{self.port}/{self.db}, "
                f"TTL: {self.ttl}s, Max size: {self.max_size}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            self._connected = False
            return False
    
    async def shutdown(self) -> None:
        """Shutdown Redis connection"""
        if self._redis:
            try:
                await self._redis.close()
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
        
        self._connected = False
        logger.info("Redis cache shutdown complete")
    
    def _get_key(self, key: str) -> str:
        """Get prefixed Redis key"""
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        entry_data = {
            'value': value,
            'created_at': datetime.utcnow().isoformat(),
            'access_count': 0
        }
        return json.dumps(entry_data, default=str)
    
    def _deserialize_value(self, data: str) -> Any:
        """Deserialize value from Redis"""
        try:
            entry_data = json.loads(data)
            return entry_data['value']
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to deserialize cache data: {e}")
            return None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self._connected or not self._redis:
            return None
        
        try:
            redis_key = self._get_key(key)
            data = await self._redis.get(redis_key)
            
            if data is None:
                return None
            
            value = self._deserialize_value(data)
            
            # Update access count
            await self._redis.hincrby(f"{redis_key}:meta", "access_count", 1)
            await self._redis.hset(f"{redis_key}:meta", "last_accessed", datetime.utcnow().isoformat())
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting from Redis cache: {e}")
            self.stats['errors'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        if not self._connected or not self._redis:
            return False
        
        try:
            ttl = ttl or self.ttl
            redis_key = self._get_key(key)
            
            # Serialize and store value
            serialized_value = self._serialize_value(value)
            
            if ttl > 0:
                await self._redis.setex(redis_key, ttl, serialized_value)
            else:
                await self._redis.set(redis_key, serialized_value)
            
            # Store metadata
            meta_key = f"{redis_key}:meta"
            await self._redis.hset(meta_key, mapping={
                "created_at": datetime.utcnow().isoformat(),
                "access_count": "0",
                "size_bytes": str(len(serialized_value))
            })
            
            if ttl > 0:
                await self._redis.expire(meta_key, ttl)
            
            # Check cache size and evict if necessary
            cache_size = await self.size()
            if cache_size > self.max_size:
                await self._evict_oldest()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")
            self.stats['errors'] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        if not self._connected or not self._redis:
            return False
        
        try:
            redis_key = self._get_key(key)
            deleted = await self._redis.delete(redis_key, f"{redis_key}:meta")
            return deleted > 0
            
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {e}")
            self.stats['errors'] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        if not self._connected or not self._redis:
            return False
        
        try:
            redis_key = self._get_key(key)
            return bool(await self._redis.exists(redis_key))
        except Exception as e:
            logger.error(f"Error checking Redis cache existence: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries with prefix"""
        if not self._connected or not self._redis:
            return False
        
        try:
            # Find all keys with our prefix
            pattern = f"{self.key_prefix}*"
            keys = []
            
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self._redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} Redis cache entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return False
    
    async def size(self) -> int:
        """Get number of items in cache"""
        if not self._connected or not self._redis:
            return 0
        
        try:
            # Count keys with our prefix (excluding meta keys)
            count = 0
            pattern = f"{self.key_prefix}*"
            
            async for key in self._redis.scan_iter(match=pattern):
                if not key.endswith(":meta"):
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting Redis cache size: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        base_stats = self.stats.copy()
        
        if not self._connected or not self._redis:
            return {**base_stats, 'connected': False}
        
        try:
            cache_size = await self.size()
            
            # Get Redis info
            redis_info = await self._redis.info()
            
            return {
                **base_stats,
                'connected': True,
                'size': cache_size,
                'max_size': self.max_size,
                'hit_rate': self.get_hit_rate(),
                'redis_memory_used': redis_info.get('used_memory_human'),
                'redis_connected_clients': redis_info.get('connected_clients'),
                'redis_total_commands': redis_info.get('total_commands_processed')
            }
            
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {**base_stats, 'connected': False, 'error': str(e)}
    
    async def cleanup_expired(self) -> int:
        """Redis automatically handles TTL expiration, so return 0"""
        return 0
    
    async def _evict_oldest(self) -> None:
        """Evict oldest entries when cache is full"""
        try:
            # This is a simplified eviction - in production you might want LRU
            pattern = f"{self.key_prefix}*"
            keys_to_check = []
            
            async for key in self._redis.scan_iter(match=pattern, count=100):
                if not key.endswith(":meta"):
                    keys_to_check.append(key)
            
            if not keys_to_check:
                return
            
            # Get creation times and sort
            oldest_keys = []
            for key in keys_to_check[:50]:  # Check first 50
                meta_key = f"{key}:meta"
                created_at = await self._redis.hget(meta_key, "created_at")
                if created_at:
                    oldest_keys.append((key, created_at))
            
            # Sort by creation time and delete oldest 10%
            oldest_keys.sort(key=lambda x: x[1])
            evict_count = max(1, len(oldest_keys) // 10)
            
            for key, _ in oldest_keys[:evict_count]:
                await self._redis.delete(key, f"{key}:meta")
                self.stats['evictions'] += 1
            
            logger.debug(f"Evicted {evict_count} oldest entries from Redis cache")
            
        except Exception as e:
            logger.error(f"Error evicting from Redis cache: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis cache health"""
        try:
            if not self._redis:
                return {"status": "unhealthy", "error": "Not initialized"}
            
            # Test connection
            start_time = datetime.utcnow()
            await self._redis.ping()
            ping_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "ping_ms": round(ping_time, 2),
                "connected": self._connected
            }
            
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "connected": False
            }