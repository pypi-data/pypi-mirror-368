"""
Rate limiter factory for creating rate limiter instances
"""
import logging
from typing import Optional, Dict, Any

from .base import RateLimiter
from .memory import MemoryRateLimiter
from .redis import RedisRateLimiter, REDIS_AVAILABLE

logger = logging.getLogger(__name__)


class RateLimitFactory:
    """Factory for creating rate limiter instances"""
    
    @staticmethod
    async def create_rate_limiter(
        backend: str = "memory",
        algorithm: str = "sliding_window",
        redis_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[RateLimiter]:
        """
        Create rate limiter instance
        
        Args:
            backend: Backend type ("memory" or "redis")
            algorithm: Algorithm ("token_bucket", "sliding_window", "fixed_window")
            redis_config: Redis configuration if using Redis backend
            **kwargs: Additional configuration
            
        Returns:
            Rate limiter instance or None if creation failed
        """
        try:
            if backend == "memory":
                rate_limiter = MemoryRateLimiter(
                    algorithm=algorithm,
                    cleanup_interval=kwargs.get("cleanup_interval", 300)
                )
                
            elif backend == "redis":
                if not REDIS_AVAILABLE:
                    logger.error("Redis backend requested but redis package not available")
                    return None
                
                redis_config = redis_config or {}
                rate_limiter = RedisRateLimiter(
                    algorithm=algorithm,
                    host=redis_config.get("host", "localhost"),
                    port=redis_config.get("port", 6379),
                    db=redis_config.get("db", 0),
                    password=redis_config.get("password"),
                    key_prefix=redis_config.get("key_prefix", "ratelimit:"),
                    **{k: v for k, v in redis_config.items() if k not in 
                       ["host", "port", "db", "password", "key_prefix"]}
                )
                
            else:
                logger.error(f"Unknown rate limiter backend: {backend}")
                return None
            
            # Initialize rate limiter
            success = await rate_limiter.initialize()
            if not success:
                logger.error(f"Failed to initialize {backend} rate limiter")
                return None
            
            logger.info(f"Created {backend} rate limiter with {algorithm} algorithm")
            return rate_limiter
            
        except Exception as e:
            logger.error(f"Error creating {backend} rate limiter: {e}")
            return None
    
    @staticmethod
    def get_supported_backends() -> list[str]:
        """Get list of supported backends"""
        backends = ["memory"]
        if REDIS_AVAILABLE:
            backends.append("redis")
        return backends
    
    @staticmethod
    def get_supported_algorithms() -> list[str]:
        """Get list of supported algorithms"""
        return ["token_bucket", "sliding_window", "fixed_window"]
    
    @staticmethod
    async def create_fallback_rate_limiter(
        algorithm: str = "sliding_window",
        cleanup_interval: int = 300
    ) -> RateLimiter:
        """
        Create fallback memory rate limiter when primary fails
        
        Args:
            algorithm: Algorithm to use
            cleanup_interval: Cleanup interval in seconds
            
        Returns:
            Memory rate limiter instance
        """
        rate_limiter = MemoryRateLimiter(
            algorithm=algorithm,
            cleanup_interval=cleanup_interval
        )
        await rate_limiter.initialize()
        logger.info("Created fallback memory rate limiter")
        return rate_limiter


class RateLimitConfig:
    """Configuration for rate limiting"""
    
    def __init__(
        self,
        backend: str = "memory",
        algorithm: str = "sliding_window",
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        cleanup_interval: int = 300,
        enabled: bool = True
    ):
        self.backend = backend
        self.algorithm = algorithm
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password
        self.cleanup_interval = cleanup_interval
        self.enabled = enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "backend": self.backend,
            "algorithm": self.algorithm,
            "redis_host": self.redis_host,
            "redis_port": self.redis_port,
            "redis_db": self.redis_db,
            "redis_password": self.redis_password,
            "cleanup_interval": self.cleanup_interval,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RateLimitConfig':
        """Create from dictionary"""
        return cls(
            backend=data.get("backend", "memory"),
            algorithm=data.get("algorithm", "sliding_window"),
            redis_host=data.get("redis_host", "localhost"),
            redis_port=data.get("redis_port", 6379),
            redis_db=data.get("redis_db", 0),
            redis_password=data.get("redis_password"),
            cleanup_interval=data.get("cleanup_interval", 300),
            enabled=data.get("enabled", True)
        )
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            "host": self.redis_host,
            "port": self.redis_port,
            "db": self.redis_db,
            "password": self.redis_password
        }