"""
Rate limiting decorators and utilities
"""
import functools
import logging
from typing import Callable, Optional, Union, Dict, Any
from datetime import datetime

from .base import RateLimiter, RateLimit, RateLimitError

logger = logging.getLogger(__name__)


def rate_limited(
    rate_limiter: RateLimiter,
    limit: int,
    window: int,
    key_func: Optional[Callable] = None,
    burst: Optional[int] = None,
    tokens_func: Optional[Callable] = None
):
    """
    Decorator to rate limit function calls
    
    Args:
        rate_limiter: Rate limiter instance
        limit: Maximum requests per window
        window: Time window in seconds
        key_func: Function to generate rate limit key from arguments
        burst: Burst allowance (for token bucket)
        tokens_func: Function to calculate tokens to consume from arguments
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                try:
                    key = key_func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Key function failed for {func.__name__}: {e}")
                    key = f"function:{func.__name__}"
            else:
                key = f"function:{func.__name__}"
            
            # Calculate tokens to consume
            if tokens_func:
                try:
                    tokens = tokens_func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Tokens function failed for {func.__name__}: {e}")
                    tokens = 1
            else:
                tokens = 1
            
            # Create rate limit
            rate_limit = RateLimit(
                key=key,
                limit=limit,
                window=window,
                burst=burst
            )
            
            # Check rate limit
            try:
                await rate_limiter.enforce_rate_limit(rate_limit, tokens)
                logger.debug(f"Rate limit passed for {func.__name__}: {key}")
            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded for {func.__name__}: {key}")
                raise
            
            # Execute function
            return await func(*args, **kwargs)
        
        # Add rate limit management methods
        wrapper.rate_limiter = rate_limiter
        
        async def reset_rate_limit(*args, **kwargs):
            """Reset rate limit for specific arguments"""
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"function:{func.__name__}"
            await rate_limiter.reset_rate_limit(key)
        
        async def get_rate_limit_info(*args, **kwargs):
            """Get rate limit info for specific arguments"""
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"function:{func.__name__}"
            
            rate_limit = RateLimit(key=key, limit=limit, window=window, burst=burst)
            return await rate_limiter.get_rate_limit_info(rate_limit)
        
        wrapper.reset_rate_limit = reset_rate_limit
        wrapper.get_rate_limit_info = get_rate_limit_info
        
        return wrapper
    return decorator


class RateLimitManager:
    """High-level rate limit manager"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.default_limits: Dict[str, RateLimit] = {}
    
    def add_default_limit(self, name: str, limit: int, window: int, burst: Optional[int] = None):
        """Add a default rate limit configuration"""
        self.default_limits[name] = RateLimit(
            key=f"default:{name}",
            limit=limit,
            window=window,
            burst=burst
        )
    
    async def check_limit(
        self, 
        key: str, 
        limit_name: Optional[str] = None,
        custom_limit: Optional[RateLimit] = None,
        tokens: int = 1
    ) -> bool:
        """
        Check rate limit for a key
        
        Args:
            key: Rate limit key
            limit_name: Name of default limit to use
            custom_limit: Custom rate limit configuration
            tokens: Number of tokens to consume
            
        Returns:
            True if allowed, False if rate limited
        """
        try:
            if custom_limit:
                rate_limit = custom_limit
            elif limit_name and limit_name in self.default_limits:
                rate_limit = self.default_limits[limit_name]
                rate_limit.key = key  # Override key
            else:
                logger.warning(f"No rate limit configuration found for {key}")
                return True  # Allow if no config
            
            result = await self.rate_limiter.check_rate_limit(rate_limit, tokens)
            return result.allowed
            
        except Exception as e:
            logger.error(f"Rate limit check failed for {key}: {e}")
            return True  # Allow on error
    
    async def enforce_limit(
        self,
        key: str,
        limit_name: Optional[str] = None,
        custom_limit: Optional[RateLimit] = None,
        tokens: int = 1
    ):
        """
        Enforce rate limit for a key
        
        Raises:
            RateLimitError: If rate limit exceeded
        """
        if custom_limit:
            rate_limit = custom_limit
        elif limit_name and limit_name in self.default_limits:
            rate_limit = self.default_limits[limit_name]
            rate_limit.key = key  # Override key
        else:
            logger.warning(f"No rate limit configuration found for {key}")
            return  # Allow if no config
        
        await self.rate_limiter.enforce_rate_limit(rate_limit, tokens)
    
    async def get_limit_status(self, key: str, limit_name: str) -> Optional[Dict[str, Any]]:
        """Get rate limit status for a key"""
        if limit_name not in self.default_limits:
            return None
        
        rate_limit = self.default_limits[limit_name]
        rate_limit.key = key  # Override key
        
        try:
            return await self.rate_limiter.get_rate_limit_info(rate_limit)
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return None
    
    async def reset_limit(self, key: str) -> bool:
        """Reset rate limit for a key"""
        try:
            return await self.rate_limiter.reset_rate_limit(key)
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            "rate_limiter_stats": self.rate_limiter.get_stats(),
            "default_limits": {
                name: {
                    "limit": limit.limit,
                    "window": limit.window,
                    "burst": limit.burst
                }
                for name, limit in self.default_limits.items()
            },
            "total_default_limits": len(self.default_limits)
        }


class ProviderRateLimitManager:
    """Rate limit manager for API providers"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.provider_limits: Dict[str, Dict[str, RateLimit]] = {}
    
    def configure_provider(
        self,
        provider_name: str,
        requests_per_minute: Optional[int] = None,
        tokens_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        tokens_per_hour: Optional[int] = None
    ):
        """Configure rate limits for a provider"""
        limits = {}
        
        if requests_per_minute:
            limits["requests_minute"] = RateLimit(
                key=f"provider:{provider_name}:requests",
                limit=requests_per_minute,
                window=60
            )
        
        if tokens_per_minute:
            limits["tokens_minute"] = RateLimit(
                key=f"provider:{provider_name}:tokens",
                limit=tokens_per_minute,
                window=60
            )
        
        if requests_per_hour:
            limits["requests_hour"] = RateLimit(
                key=f"provider:{provider_name}:requests",
                limit=requests_per_hour,
                window=3600
            )
        
        if tokens_per_hour:
            limits["tokens_hour"] = RateLimit(
                key=f"provider:{provider_name}:tokens",
                limit=tokens_per_hour,
                window=3600
            )
        
        self.provider_limits[provider_name] = limits
        logger.info(f"Configured rate limits for provider {provider_name}: {list(limits.keys())}")
    
    async def check_provider_limits(
        self,
        provider_name: str,
        api_key: Optional[str] = None,
        tokens: int = 1
    ) -> Dict[str, bool]:
        """
        Check all rate limits for a provider
        
        Returns:
            Dictionary of limit_name -> allowed status
        """
        if provider_name not in self.provider_limits:
            return {}  # No limits configured
        
        # Use API key in rate limit key if provided
        key_suffix = f":{api_key}" if api_key else ""
        results = {}
        
        for limit_name, rate_limit in self.provider_limits[provider_name].items():
            # Override key to include API key
            rate_limit_copy = RateLimit(
                key=f"{rate_limit.key}{key_suffix}",
                limit=rate_limit.limit,
                window=rate_limit.window,
                burst=rate_limit.burst
            )
            
            try:
                # Use different token counts for different limit types
                tokens_to_use = tokens if "tokens" in limit_name else 1
                result = await self.rate_limiter.check_rate_limit(rate_limit_copy, tokens_to_use)
                results[limit_name] = result.allowed
            except Exception as e:
                logger.error(f"Rate limit check failed for {provider_name}/{limit_name}: {e}")
                results[limit_name] = True  # Allow on error
        
        return results
    
    async def enforce_provider_limits(
        self,
        provider_name: str,
        api_key: Optional[str] = None,
        tokens: int = 1
    ):
        """
        Enforce all rate limits for a provider
        
        Raises:
            RateLimitError: If any rate limit exceeded
        """
        results = await self.check_provider_limits(provider_name, api_key, tokens)
        
        failed_limits = [name for name, allowed in results.items() if not allowed]
        if failed_limits:
            raise RateLimitError(
                f"Provider {provider_name} rate limits exceeded: {', '.join(failed_limits)}",
                # We'd need to get the actual result for proper error details
                # For now, provide a basic result
                result=None  # This would need proper implementation
            )
    
    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider rate limit configuration"""
        return {
            provider: {
                limit_name: {
                    "limit": limit.limit,
                    "window": limit.window,
                    "burst": limit.burst
                }
                for limit_name, limit in limits.items()
            }
            for provider, limits in self.provider_limits.items()
        }