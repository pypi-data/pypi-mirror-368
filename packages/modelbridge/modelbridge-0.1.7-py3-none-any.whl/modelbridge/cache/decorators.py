"""
Cache decorators and utilities for ModelBridge
"""
import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Union
from datetime import datetime

from .base import CacheInterface

logger = logging.getLogger(__name__)


def cached(
    cache: CacheInterface,
    ttl: Optional[int] = None,
    key_prefix: str = "",
    exclude_args: Optional[list] = None,
    exclude_kwargs: Optional[list] = None
):
    """
    Decorator to cache function results
    
    Args:
        cache: Cache instance to use
        ttl: Time to live override
        key_prefix: Prefix for cache keys
        exclude_args: Arguments to exclude from key generation
        exclude_kwargs: Keyword arguments to exclude from key generation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            filtered_args = args
            filtered_kwargs = kwargs.copy()
            
            if exclude_args:
                filtered_args = args[len(exclude_args):]
            
            if exclude_kwargs:
                for key in exclude_kwargs:
                    filtered_kwargs.pop(key, None)
            
            cache_key = f"{key_prefix}{func.__name__}:{cache.generate_key(*filtered_args, **filtered_kwargs)}"
            
            # Try to get from cache
            try:
                cached_result = await cache.get_with_stats(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache get error for {func.__name__}: {e}")
            
            # Execute function
            try:
                result = await func(*args, **kwargs)
                
                # Store in cache
                try:
                    await cache.set_with_stats(cache_key, result, ttl)
                    logger.debug(f"Cached result for {func.__name__}")
                except Exception as e:
                    logger.warning(f"Cache set error for {func.__name__}: {e}")
                
                return result
                
            except Exception as e:
                logger.error(f"Function execution error for {func.__name__}: {e}")
                raise
        
        # Add cache control methods to function
        wrapper.cache = cache
        wrapper.cache_key_prefix = f"{key_prefix}{func.__name__}:"
        
        async def clear_cache(*args, **kwargs):
            """Clear cache for specific arguments"""
            cache_key = f"{key_prefix}{func.__name__}:{cache.generate_key(*args, **kwargs)}"
            await cache.delete_with_stats(cache_key)
        
        async def clear_all_cache():
            """Clear all cache entries for this function"""
            # This would require pattern matching - simplified for now
            await cache.clear()
        
        wrapper.clear_cache = clear_cache
        wrapper.clear_all_cache = clear_all_cache
        
        return wrapper
    return decorator


def cache_llm_response(cache: CacheInterface, ttl: int = 3600):
    """
    Specialized decorator for caching LLM responses
    
    Args:
        cache: Cache instance
        ttl: Time to live for cached responses
    """
    return cached(
        cache=cache,
        ttl=ttl,
        key_prefix="llm:",
        exclude_args=[],  # Include all args for LLM caching
        exclude_kwargs=["request_id", "timestamp"]  # Exclude metadata
    )


class CacheManager:
    """High-level cache manager for ModelBridge"""
    
    def __init__(self, cache: CacheInterface):
        self.cache = cache
        self._active_requests = {}  # Track in-flight requests
    
    async def get_or_compute(
        self,
        key: str,
        compute_func: Callable,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Get from cache or compute and cache result
        
        Args:
            key: Cache key
            compute_func: Function to compute value if not cached
            ttl: Time to live
            *args: Arguments for compute function
            **kwargs: Keyword arguments for compute function
        """
        # Check cache first
        cached_value = await self.cache.get_with_stats(key)
        if cached_value is not None:
            return cached_value
        
        # Check if request is already in flight
        if key in self._active_requests:
            logger.debug(f"Request already in flight for key: {key[:16]}...")
            return await self._active_requests[key]
        
        # Create future for this request
        future = asyncio.Future()
        self._active_requests[key] = future
        
        try:
            # Compute value
            if asyncio.iscoroutinefunction(compute_func):
                value = await compute_func(*args, **kwargs)
            else:
                value = compute_func(*args, **kwargs)
            
            # Cache the result
            await self.cache.set_with_stats(key, value, ttl)
            
            # Set result for waiting coroutines
            future.set_result(value)
            return value
            
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # Clean up
            self._active_requests.pop(key, None)
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern
        (Implementation depends on cache type)
        """
        # For now, this is a simplified implementation
        # Redis could use SCAN with pattern matching
        logger.warning(f"Pattern invalidation not fully implemented: {pattern}")
        return 0
    
    async def warm_cache(self, keys_and_funcs: list) -> int:
        """
        Warm cache with multiple entries
        
        Args:
            keys_and_funcs: List of (key, func, args, kwargs) tuples
            
        Returns:
            Number of entries warmed
        """
        warmed = 0
        
        for key, func, args, kwargs in keys_and_funcs:
            try:
                # Skip if already cached
                if await self.cache.exists(key):
                    continue
                
                # Compute and cache
                if asyncio.iscoroutinefunction(func):
                    value = await func(*args, **kwargs)
                else:
                    value = func(*args, **kwargs)
                
                await self.cache.set_with_stats(key, value)
                warmed += 1
                
            except Exception as e:
                logger.warning(f"Failed to warm cache for key {key[:16]}...: {e}")
        
        logger.info(f"Warmed {warmed} cache entries")
        return warmed
    
    async def get_cache_info(self) -> dict:
        """Get comprehensive cache information"""
        stats = await self.cache.get_stats()
        
        return {
            **stats,
            'active_requests': len(self._active_requests),
            'cache_type': type(self.cache).__name__,
            'timestamp': datetime.utcnow().isoformat()
        }