"""
Cache factory for creating cache instances
"""
import logging
from typing import Optional

from ..config.models import CacheConfig
from .base import CacheInterface
from .memory import MemoryCache
from .redis import RedisCache

logger = logging.getLogger(__name__)


class CacheFactory:
    """Factory for creating cache instances"""
    
    @staticmethod
    async def create_cache(config: CacheConfig) -> Optional[CacheInterface]:
        """
        Create cache instance based on configuration
        
        Args:
            config: Cache configuration
            
        Returns:
            Cache instance or None if creation failed
        """
        if not config.enabled:
            logger.info("Cache disabled in configuration")
            return None
        
        try:
            if config.type == "memory":
                cache = MemoryCache(
                    ttl=config.ttl,
                    max_size=config.max_size
                )
                
            elif config.type == "redis":
                cache = RedisCache(
                    host=config.redis_host,
                    port=config.redis_port,
                    db=config.redis_db,
                    password=config.redis_password,
                    ttl=config.ttl,
                    max_size=config.max_size
                )
                
            else:
                logger.error(f"Unknown cache type: {config.type}")
                return None
            
            # Initialize cache
            success = await cache.initialize()
            if not success:
                logger.error(f"Failed to initialize {config.type} cache")
                return None
            
            logger.info(f"Created {config.type} cache successfully")
            return cache
            
        except Exception as e:
            logger.error(f"Error creating {config.type} cache: {e}")
            return None
    
    @staticmethod
    def get_supported_types() -> list[str]:
        """Get list of supported cache types"""
        return ["memory", "redis"]
    
    @staticmethod
    async def create_fallback_cache(ttl: int = 3600, max_size: int = 1000) -> CacheInterface:
        """
        Create fallback memory cache when primary cache fails
        
        Args:
            ttl: Time to live in seconds
            max_size: Maximum number of entries
            
        Returns:
            Memory cache instance
        """
        cache = MemoryCache(ttl=ttl, max_size=max_size)
        await cache.initialize()
        logger.info("Created fallback memory cache")
        return cache