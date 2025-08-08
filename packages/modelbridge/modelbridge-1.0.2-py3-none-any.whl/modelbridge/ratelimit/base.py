"""
Base rate limiting interfaces and data structures
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    """Rate limit configuration"""
    key: str  # Rate limit identifier (e.g., "user:123", "api_key:abc")
    limit: int  # Maximum number of requests
    window: int  # Time window in seconds
    burst: Optional[int] = None  # Burst allowance (for token bucket)
    
    def __post_init__(self):
        if self.limit <= 0:
            raise ValueError("Rate limit must be positive")
        if self.window <= 0:
            raise ValueError("Time window must be positive")
        if self.burst is not None and self.burst < self.limit:
            raise ValueError("Burst must be >= limit")


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    limit: int
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None  # Seconds to wait before retry
    
    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers"""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(int(self.reset_time.timestamp()))
        }
        
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)
            
        return headers


class RateLimitError(Exception):
    """Rate limit exceeded error"""
    def __init__(self, message: str, result: RateLimitResult):
        super().__init__(message)
        self.result = result


class RateLimiter(ABC):
    """Abstract rate limiter interface"""
    
    def __init__(self, algorithm: str = "sliding_window"):
        self.algorithm = algorithm
        self.stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "errors": 0
        }
    
    @abstractmethod
    async def check_rate_limit(self, rate_limit: RateLimit, tokens: int = 1) -> RateLimitResult:
        """
        Check if request is within rate limit
        
        Args:
            rate_limit: Rate limit configuration
            tokens: Number of tokens to consume (default: 1)
            
        Returns:
            RateLimitResult with allow/deny decision
        """
        pass
    
    @abstractmethod
    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a key"""
        pass
    
    @abstractmethod
    async def get_rate_limit_info(self, rate_limit: RateLimit) -> Dict[str, Any]:
        """Get current rate limit information"""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired rate limit entries"""
        pass
    
    async def enforce_rate_limit(self, rate_limit: RateLimit, tokens: int = 1) -> RateLimitResult:
        """
        Enforce rate limit and raise exception if exceeded
        
        Args:
            rate_limit: Rate limit configuration
            tokens: Number of tokens to consume
            
        Returns:
            RateLimitResult if allowed
            
        Raises:
            RateLimitError: If rate limit exceeded
        """
        try:
            result = await self.check_rate_limit(rate_limit, tokens)
            
            # Update stats
            self.stats["total_requests"] += 1
            if result.allowed:
                self.stats["allowed_requests"] += 1
            else:
                self.stats["blocked_requests"] += 1
            
            if not result.allowed:
                raise RateLimitError(
                    f"Rate limit exceeded for {rate_limit.key}: {rate_limit.limit}/{rate_limit.window}s",
                    result
                )
            
            return result
            
        except Exception as e:
            if not isinstance(e, RateLimitError):
                self.stats["errors"] += 1
                logger.error(f"Rate limit check failed for {rate_limit.key}: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            **self.stats,
            "algorithm": self.algorithm,
            "block_rate": (
                self.stats["blocked_requests"] / self.stats["total_requests"] 
                if self.stats["total_requests"] > 0 else 0.0
            )
        }
    
    def create_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        burst: Optional[int] = None
    ) -> RateLimit:
        """Convenience method to create RateLimit"""
        return RateLimit(key=key, limit=limit, window=window, burst=burst)


class MultiRateLimiter:
    """Rate limiter that supports multiple limits per key"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
    
    async def check_multiple_limits(self, rate_limits: List[RateLimit], tokens: int = 1) -> RateLimitResult:
        """
        Check multiple rate limits (all must pass)
        
        Args:
            rate_limits: List of rate limit configurations
            tokens: Number of tokens to consume
            
        Returns:
            RateLimitResult (most restrictive if multiple failures)
        """
        most_restrictive_result = None
        
        for rate_limit in rate_limits:
            result = await self.rate_limiter.check_rate_limit(rate_limit, tokens)
            
            if not result.allowed:
                # Track most restrictive (shortest retry time)
                if (most_restrictive_result is None or 
                    (result.retry_after and 
                     (not most_restrictive_result.retry_after or 
                      result.retry_after < most_restrictive_result.retry_after))):
                    most_restrictive_result = result
        
        # If any limit failed, return the most restrictive
        if most_restrictive_result:
            return most_restrictive_result
        
        # All limits passed - return the most restrictive success
        success_results = []
        for rate_limit in rate_limits:
            result = await self.rate_limiter.check_rate_limit(rate_limit, 0)  # Don't consume tokens again
            success_results.append(result)
        
        # Return result with lowest remaining count
        return min(success_results, key=lambda r: r.remaining)
    
    async def enforce_multiple_limits(self, rate_limits: List[RateLimit], tokens: int = 1) -> RateLimitResult:
        """
        Enforce multiple rate limits
        
        Raises:
            RateLimitError: If any rate limit exceeded
        """
        result = await self.check_multiple_limits(rate_limits, tokens)
        
        if not result.allowed:
            # Find which limit was exceeded
            failed_limits = []
            for rate_limit in rate_limits:
                check_result = await self.rate_limiter.check_rate_limit(rate_limit, 0)
                if not check_result.allowed:
                    failed_limits.append(rate_limit.key)
            
            raise RateLimitError(
                f"Rate limits exceeded: {', '.join(failed_limits)}",
                result
            )
        
        return result


class RateLimitRegistry:
    """Registry for managing multiple rate limiters"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
    
    def register(self, name: str, rate_limiter: RateLimiter):
        """Register a rate limiter"""
        self.limiters[name] = rate_limiter
    
    def get(self, name: str) -> Optional[RateLimiter]:
        """Get rate limiter by name"""
        return self.limiters.get(name)
    
    def get_or_default(self, name: str, default: RateLimiter) -> RateLimiter:
        """Get rate limiter or return default"""
        return self.limiters.get(name, default)
    
    async def check_all_limits(
        self, 
        key: str, 
        limits: Dict[str, RateLimit], 
        tokens: int = 1
    ) -> Dict[str, RateLimitResult]:
        """Check rate limits across all registered limiters"""
        results = {}
        
        for limiter_name, rate_limit in limits.items():
            if limiter_name in self.limiters:
                try:
                    result = await self.limiters[limiter_name].check_rate_limit(rate_limit, tokens)
                    results[limiter_name] = result
                except Exception as e:
                    logger.error(f"Rate limit check failed for {limiter_name}: {e}")
                    results[limiter_name] = RateLimitResult(
                        allowed=True,  # Allow on error
                        limit=rate_limit.limit,
                        remaining=rate_limit.limit,
                        reset_time=datetime.utcnow() + timedelta(seconds=rate_limit.window)
                    )
        
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics from all registered limiters"""
        return {name: limiter.get_stats() for name, limiter in self.limiters.items()}