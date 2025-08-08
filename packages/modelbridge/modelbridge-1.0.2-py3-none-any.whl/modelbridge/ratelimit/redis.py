"""
Redis-based rate limiter implementation
"""
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .base import RateLimiter, RateLimit, RateLimitResult
from .algorithms import TokenBucket, SlidingWindow, FixedWindow, TokenBucketState, SlidingWindowState

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available. Install with: pip install redis")
    REDIS_AVAILABLE = False


class RedisRateLimiter(RateLimiter):
    """Redis-based distributed rate limiter"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        algorithm: str = "sliding_window",
        key_prefix: str = "ratelimit:",
        **kwargs
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is required but not installed. Install with: pip install redis")
        
        super().__init__(algorithm)
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.key_prefix = key_prefix
        self.redis_kwargs = kwargs
        
        self._redis: Optional[redis.Redis] = None
        self._connected = False
        
        # Lua scripts for atomic operations
        self._scripts = {}
    
    async def initialize(self) -> bool:
        """Initialize Redis connection and load Lua scripts"""
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
            
            # Load Lua scripts
            await self._load_lua_scripts()
            
            logger.info(f"Redis rate limiter initialized - {self.host}:{self.port}/{self.db}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis rate limiter: {e}")
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
        logger.info("Redis rate limiter shutdown complete")
    
    async def _load_lua_scripts(self):
        """Load Lua scripts for atomic operations"""
        if not self._redis:
            return
        
        # Token bucket script
        token_bucket_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        -- Calculate tokens to add
        local time_passed = now - last_refill
        local tokens_to_add = time_passed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        
        -- Check if we can consume
        if tokens >= tokens_requested then
            -- Consume tokens
            tokens = tokens - tokens_requested
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 86400)  -- 24 hour expiry
            return {1, tokens}  -- allowed, remaining
        else
            -- Update state but don't consume
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 86400)
            return {0, tokens}  -- not allowed, remaining
        end
        """
        
        # Sliding window script
        sliding_window_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local window_start = now - window
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)
        
        -- Count current entries
        local current_count = redis.call('ZCARD', key)
        
        if current_count + tokens_requested <= limit then
            -- Add new entries
            for i = 1, tokens_requested do
                redis.call('ZADD', key, now + i * 0.001, now + i * 0.001)
            end
            redis.call('EXPIRE', key, window + 60)  -- Window + buffer
            return {1, limit - current_count - tokens_requested}  -- allowed, remaining
        else
            redis.call('EXPIRE', key, window + 60)
            return {0, limit - current_count}  -- not allowed, remaining
        end
        """
        
        # Fixed window script
        fixed_window_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local window_start = math.floor(now / window) * window
        local window_key = key .. ':' .. window_start
        
        local current_count = tonumber(redis.call('GET', window_key)) or 0
        
        if current_count + tokens_requested <= limit then
            -- Increment counter
            local new_count = redis.call('INCRBY', window_key, tokens_requested)
            redis.call('EXPIRE', window_key, window + 60)  -- Window + buffer
            return {1, limit - new_count}  -- allowed, remaining
        else
            return {0, limit - current_count}  -- not allowed, remaining
        end
        """
        
        # Register scripts
        self._scripts = {
            'token_bucket': await self._redis.script_load(token_bucket_script),
            'sliding_window': await self._redis.script_load(sliding_window_script),
            'fixed_window': await self._redis.script_load(fixed_window_script)
        }
    
    def _get_key(self, rate_limit: RateLimit) -> str:
        """Get Redis key for rate limit"""
        return f"{self.key_prefix}{self.algorithm}:{rate_limit.key}:{rate_limit.limit}:{rate_limit.window}"
    
    async def check_rate_limit(self, rate_limit: RateLimit, tokens: int = 1) -> RateLimitResult:
        """Check rate limit using Redis"""
        if not self._connected or not self._redis:
            # Fallback: allow request if Redis is down
            logger.warning("Redis not connected, allowing request")
            return RateLimitResult(
                allowed=True,
                limit=rate_limit.limit,
                remaining=rate_limit.limit,
                reset_time=datetime.utcnow() + timedelta(seconds=rate_limit.window)
            )
        
        try:
            if self.algorithm == "token_bucket":
                return await self._check_token_bucket_redis(rate_limit, tokens)
            elif self.algorithm == "sliding_window":
                return await self._check_sliding_window_redis(rate_limit, tokens)
            elif self.algorithm == "fixed_window":
                return await self._check_fixed_window_redis(rate_limit, tokens)
            else:
                raise ValueError(f"Unknown algorithm: {self.algorithm}")
                
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            self.stats["errors"] += 1
            # Fallback: allow request on error
            return RateLimitResult(
                allowed=True,
                limit=rate_limit.limit,
                remaining=rate_limit.limit,
                reset_time=datetime.utcnow() + timedelta(seconds=rate_limit.window)
            )
    
    async def _check_token_bucket_redis(self, rate_limit: RateLimit, tokens: int) -> RateLimitResult:
        """Check token bucket rate limit using Redis Lua script"""
        key = self._get_key(rate_limit)
        capacity = rate_limit.burst or rate_limit.limit
        refill_rate = rate_limit.limit / rate_limit.window
        now = time.time()
        
        result = await self._redis.evalsha(
            self._scripts['token_bucket'],
            1, key, capacity, refill_rate, tokens, now
        )
        
        allowed = bool(result[0])
        remaining_tokens = int(result[1])
        
        # Calculate reset time (when bucket will be full)
        tokens_needed = capacity - remaining_tokens
        seconds_to_full = tokens_needed / refill_rate if refill_rate > 0 else 0
        reset_time = datetime.utcnow() + timedelta(seconds=seconds_to_full)
        
        # Calculate retry after if not allowed
        retry_after = None
        if not allowed:
            tokens_needed_for_request = tokens - remaining_tokens
            retry_after = max(1, int(tokens_needed_for_request / refill_rate)) if refill_rate > 0 else 60
        
        return RateLimitResult(
            allowed=allowed,
            limit=rate_limit.limit,
            remaining=remaining_tokens,
            reset_time=reset_time,
            retry_after=retry_after
        )
    
    async def _check_sliding_window_redis(self, rate_limit: RateLimit, tokens: int) -> RateLimitResult:
        """Check sliding window rate limit using Redis Lua script"""
        key = self._get_key(rate_limit)
        now = time.time()
        
        result = await self._redis.evalsha(
            self._scripts['sliding_window'],
            1, key, rate_limit.limit, rate_limit.window, tokens, now
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        
        # Calculate reset time
        reset_time = datetime.utcnow() + timedelta(seconds=rate_limit.window)
        
        # Calculate retry after if not allowed
        retry_after = None
        if not allowed:
            # Get oldest entry in window to calculate retry time
            try:
                oldest_entries = await self._redis.zrange(key, 0, 0, withscores=True)
                if oldest_entries:
                    oldest_time = oldest_entries[0][1]
                    retry_after = max(1, int(oldest_time + rate_limit.window - now))
                else:
                    retry_after = 1
            except Exception:
                retry_after = 60
        
        return RateLimitResult(
            allowed=allowed,
            limit=rate_limit.limit,
            remaining=remaining,
            reset_time=reset_time,
            retry_after=retry_after
        )
    
    async def _check_fixed_window_redis(self, rate_limit: RateLimit, tokens: int) -> RateLimitResult:
        """Check fixed window rate limit using Redis Lua script"""
        key = self._get_key(rate_limit)
        now = time.time()
        
        result = await self._redis.evalsha(
            self._scripts['fixed_window'],
            1, key, rate_limit.limit, rate_limit.window, tokens, now
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        
        # Calculate reset time
        window_start = (now // rate_limit.window) * rate_limit.window
        reset_time = datetime.utcfromtimestamp(window_start + rate_limit.window)
        
        # Calculate retry after if not allowed
        retry_after = None
        if not allowed:
            retry_after = max(1, int((reset_time - datetime.utcnow()).total_seconds()))
        
        return RateLimitResult(
            allowed=allowed,
            limit=rate_limit.limit,
            remaining=remaining,
            reset_time=reset_time,
            retry_after=retry_after
        )
    
    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a key"""
        if not self._connected or not self._redis:
            return False
        
        try:
            pattern = f"{self.key_prefix}*{key}*"
            keys = []
            
            async for redis_key in self._redis.scan_iter(match=pattern):
                keys.append(redis_key)
            
            if keys:
                await self._redis.delete(*keys)
                logger.debug(f"Reset rate limit for key: {key}, removed {len(keys)} entries")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
            return False
    
    async def get_rate_limit_info(self, rate_limit: RateLimit) -> Dict[str, Any]:
        """Get current rate limit information"""
        if not self._connected or not self._redis:
            return {"error": "Redis not connected"}
        
        try:
            # Make a read-only check
            result = await self.check_rate_limit(rate_limit, 0)
            
            return {
                "key": rate_limit.key,
                "limit": rate_limit.limit,
                "window": rate_limit.window,
                "remaining": result.remaining,
                "reset_time": result.reset_time.isoformat(),
                "algorithm": self.algorithm,
                "backend": "redis"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def cleanup_expired(self) -> int:
        """Redis automatically handles expiration, so return 0"""
        return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis rate limiter health"""
        try:
            if not self._redis:
                return {"status": "unhealthy", "error": "Not initialized"}
            
            # Test connection
            start_time = time.time()
            await self._redis.ping()
            ping_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "ping_ms": round(ping_time, 2),
                "connected": self._connected,
                "algorithm": self.algorithm
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }