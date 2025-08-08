"""
In-memory rate limiter implementation
"""
import asyncio
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .base import RateLimiter, RateLimit, RateLimitResult
from .algorithms import TokenBucket, SlidingWindow, FixedWindow, TokenBucketState, SlidingWindowState

logger = logging.getLogger(__name__)


class MemoryRateLimiter(RateLimiter):
    """Thread-safe in-memory rate limiter"""
    
    def __init__(self, algorithm: str = "sliding_window", cleanup_interval: int = 300):
        """
        Initialize memory rate limiter
        
        Args:
            algorithm: Algorithm to use ("token_bucket", "sliding_window", "fixed_window")  
            cleanup_interval: Seconds between cleanup runs
        """
        super().__init__(algorithm)
        self.algorithm = algorithm
        self.cleanup_interval = cleanup_interval
        
        # Storage for rate limit states
        self._states: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False
        
        # Algorithm instances (stateless)
        self._token_bucket_cache: Dict[str, TokenBucket] = {}
        self._sliding_window_cache: Dict[str, SlidingWindow] = {}
        self._fixed_window_cache: Dict[str, FixedWindow] = {}
    
    async def initialize(self) -> bool:
        """Initialize rate limiter and start cleanup task"""
        try:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            self._initialized = True
            logger.info(f"Memory rate limiter initialized with {self.algorithm} algorithm")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize memory rate limiter: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown rate limiter"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        with self._lock:
            self._states.clear()
            self._token_bucket_cache.clear()
            self._sliding_window_cache.clear()
            self._fixed_window_cache.clear()
        
        self._initialized = False
        logger.info("Memory rate limiter shutdown complete")
    
    async def check_rate_limit(self, rate_limit: RateLimit, tokens: int = 1) -> RateLimitResult:
        """Check rate limit using configured algorithm"""
        if self.algorithm == "token_bucket":
            return await self._check_token_bucket(rate_limit, tokens)
        elif self.algorithm == "sliding_window":
            return await self._check_sliding_window(rate_limit, tokens)
        elif self.algorithm == "fixed_window":
            return await self._check_fixed_window(rate_limit, tokens)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
    
    async def _check_token_bucket(self, rate_limit: RateLimit, tokens: int) -> RateLimitResult:
        """Check rate limit using token bucket algorithm"""
        bucket_key = f"tb:{rate_limit.key}:{rate_limit.limit}:{rate_limit.window}"
        
        with self._lock:
            # Get or create token bucket
            if bucket_key not in self._token_bucket_cache:
                # Calculate refill rate (tokens per second)
                refill_rate = rate_limit.limit / rate_limit.window
                capacity = rate_limit.burst or rate_limit.limit
                self._token_bucket_cache[bucket_key] = TokenBucket(capacity, refill_rate, rate_limit.window)
            
            bucket = self._token_bucket_cache[bucket_key]
            
            # Get current state or create new one
            if bucket_key not in self._states:
                self._states[bucket_key] = TokenBucketState(
                    tokens=float(bucket.capacity),
                    last_refill=time.time()
                )
            
            current_state = self._states[bucket_key]
            
            # Try to consume tokens
            allowed, new_state = bucket.consume_tokens(current_state, tokens)
            
            # Update state
            self._states[bucket_key] = new_state
            
            # Create result
            remaining = bucket.get_remaining_tokens(new_state)
            reset_time = bucket.get_reset_time(new_state)
            retry_after = bucket.get_retry_after(new_state, tokens) if not allowed else None
            
            return RateLimitResult(
                allowed=allowed,
                limit=rate_limit.limit,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
    
    async def _check_sliding_window(self, rate_limit: RateLimit, tokens: int) -> RateLimitResult:
        """Check rate limit using sliding window algorithm"""
        window_key = f"sw:{rate_limit.key}:{rate_limit.limit}:{rate_limit.window}"
        
        with self._lock:
            # Get or create sliding window
            if window_key not in self._sliding_window_cache:
                self._sliding_window_cache[window_key] = SlidingWindow(rate_limit.limit, rate_limit.window)
            
            window = self._sliding_window_cache[window_key]
            
            # Get current state or create new one
            if window_key not in self._states:
                self._states[window_key] = SlidingWindowState(requests=[])
            
            current_state = self._states[window_key]
            
            # Try to consume tokens
            allowed, new_state = window.can_consume(current_state, tokens)
            
            # Update state
            self._states[window_key] = new_state
            
            # Create result
            remaining = window.get_remaining_requests(new_state)
            reset_time = window.get_reset_time(new_state)
            retry_after = window.get_retry_after(new_state) if not allowed else None
            
            return RateLimitResult(
                allowed=allowed,
                limit=rate_limit.limit,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
    
    async def _check_fixed_window(self, rate_limit: RateLimit, tokens: int) -> RateLimitResult:
        """Check rate limit using fixed window algorithm"""
        now = time.time()
        
        # Get or create fixed window algorithm
        window_key = f"fw:{rate_limit.key}:{rate_limit.limit}:{rate_limit.window}"
        
        with self._lock:
            if window_key not in self._fixed_window_cache:
                self._fixed_window_cache[window_key] = FixedWindow(rate_limit.limit, rate_limit.window)
            
            window = self._fixed_window_cache[window_key]
            
            # Get current window
            window_start = window.get_window_start(now)
            state_key = f"{window_key}:{int(window_start)}"
            
            # Get current count for this window
            current_count = self._states.get(state_key, 0)
            
            # Check if tokens can be consumed
            allowed = window.can_consume(current_count, tokens)
            
            # Update count if allowed
            if allowed:
                self._states[state_key] = current_count + tokens
                new_count = current_count + tokens
            else:
                new_count = current_count
            
            # Create result
            remaining = window.get_remaining_requests(new_count)
            reset_time = window.get_reset_time(now)
            retry_after = window.get_retry_after(now) if not allowed else None
            
            return RateLimitResult(
                allowed=allowed,
                limit=rate_limit.limit,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
    
    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit for a key"""
        with self._lock:
            removed = False
            keys_to_remove = []
            
            for state_key in self._states.keys():
                if key in state_key:
                    keys_to_remove.append(state_key)
            
            for state_key in keys_to_remove:
                del self._states[state_key]
                removed = True
            
            logger.debug(f"Reset rate limit for key: {key}, removed {len(keys_to_remove)} states")
            return removed
    
    async def get_rate_limit_info(self, rate_limit: RateLimit) -> Dict[str, Any]:
        """Get current rate limit information"""
        # This will make a read-only check (0 tokens)
        result = await self.check_rate_limit(rate_limit, 0)
        
        return {
            "key": rate_limit.key,
            "limit": rate_limit.limit,
            "window": rate_limit.window,
            "remaining": result.remaining,
            "reset_time": result.reset_time.isoformat(),
            "algorithm": self.algorithm
        }
    
    async def cleanup_expired(self) -> int:
        """Clean up expired states"""
        now = time.time()
        cleaned = 0
        
        with self._lock:
            if self.algorithm == "token_bucket":
                # Token bucket states don't really expire, but we can clean very old ones
                old_threshold = now - 3600  # 1 hour
                keys_to_remove = []
                
                for key, state in self._states.items():
                    if isinstance(state, TokenBucketState) and state.last_refill < old_threshold:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self._states[key]
                    cleaned += 1
            
            elif self.algorithm == "sliding_window":
                # Clean up sliding window states
                keys_to_remove = []
                
                for key, state in self._states.items():
                    if isinstance(state, SlidingWindowState):
                        # Extract window size from key
                        try:
                            parts = key.split(":")
                            window_size = int(parts[-1])
                            window_start = now - window_size
                            
                            # Remove old requests
                            recent_requests = [req for req in state.requests if req > window_start]
                            
                            if not recent_requests and state.created_at < now - window_size:
                                keys_to_remove.append(key)
                            else:
                                # Update state with cleaned requests
                                self._states[key] = SlidingWindowState(
                                    requests=recent_requests,
                                    created_at=state.created_at
                                )
                        except (IndexError, ValueError):
                            # Malformed key, remove it
                            keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self._states[key]
                    cleaned += 1
            
            elif self.algorithm == "fixed_window":
                # Clean up old fixed window states
                keys_to_remove = []
                
                for key in self._states.keys():
                    if key.startswith("fw:"):
                        try:
                            # Extract timestamp from key
                            timestamp = float(key.split(":")[-1])
                            if timestamp < now - 86400:  # Older than 24 hours
                                keys_to_remove.append(key)
                        except (IndexError, ValueError):
                            keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self._states[key]
                    cleaned += 1
        
        if cleaned > 0:
            logger.debug(f"Cleaned up {cleaned} expired rate limit states")
        
        return cleaned
    
    async def get_all_states(self) -> Dict[str, Any]:
        """Get all current states (for debugging)"""
        with self._lock:
            return {
                "algorithm": self.algorithm,
                "total_states": len(self._states),
                "states": dict(self._states),
                "cache_sizes": {
                    "token_buckets": len(self._token_bucket_cache),
                    "sliding_windows": len(self._sliding_window_cache),
                    "fixed_windows": len(self._fixed_window_cache)
                }
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check memory rate limiter health"""
        try:
            with self._lock:
                return {
                    "status": "healthy",
                    "initialized": self._initialized,
                    "algorithm": self.algorithm,
                    "total_states": len(self._states),
                    "cache_sizes": {
                        "token_buckets": len(self._token_bucket_cache),
                        "sliding_windows": len(self._sliding_window_cache),
                        "fixed_windows": len(self._fixed_window_cache)
                    }
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self._initialized
            }
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired states"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                cleaned = await self.cleanup_expired()
                
                # Log stats periodically
                total_states = len(self._states)
                logger.debug(f"Rate limiter cleanup: {cleaned} cleaned, {total_states} remaining")
                
            except asyncio.CancelledError:
                logger.debug("Rate limiter cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
                await asyncio.sleep(60)  # Wait before retrying