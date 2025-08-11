"""
Rate limiting algorithms
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class TokenBucketState:
    """Token bucket state"""
    tokens: float
    last_refill: float
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "tokens": self.tokens,
            "last_refill": self.last_refill,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenBucketState':
        """Create from dictionary"""
        return cls(
            tokens=data["tokens"],
            last_refill=data["last_refill"],
            created_at=data.get("created_at", time.time())
        )


class TokenBucket:
    """Token bucket rate limiting algorithm"""
    
    def __init__(self, capacity: int, refill_rate: float, window: int = 60):
        """
        Initialize token bucket
        
        Args:
            capacity: Maximum number of tokens (burst size)
            refill_rate: Tokens per second refill rate
            window: Time window for rate calculation
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.window = window
        
        # Calculate tokens per window for rate limiting
        self.tokens_per_window = int(refill_rate * window)
    
    def consume_tokens(self, state: TokenBucketState, tokens: int) -> tuple[bool, TokenBucketState]:
        """
        Try to consume tokens from bucket
        
        Args:
            state: Current bucket state
            tokens: Number of tokens to consume
            
        Returns:
            (allowed: bool, new_state: TokenBucketState)
        """
        now = time.time()
        
        # Calculate tokens to add since last refill
        time_passed = now - state.last_refill
        tokens_to_add = time_passed * self.refill_rate
        
        # Update token count (capped at capacity)
        new_tokens = min(self.capacity, state.tokens + tokens_to_add)
        
        # Check if we can consume requested tokens
        if new_tokens >= tokens:
            # Consume tokens
            new_state = TokenBucketState(
                tokens=new_tokens - tokens,
                last_refill=now,
                created_at=state.created_at
            )
            return True, new_state
        else:
            # Not enough tokens
            new_state = TokenBucketState(
                tokens=new_tokens,
                last_refill=now,
                created_at=state.created_at
            )
            return False, new_state
    
    def get_retry_after(self, state: TokenBucketState, tokens: int) -> int:
        """Calculate seconds to wait before retry"""
        tokens_needed = tokens - state.tokens
        if tokens_needed <= 0:
            return 0
        
        # Time to accumulate needed tokens
        return max(1, int(tokens_needed / self.refill_rate))
    
    def get_remaining_tokens(self, state: TokenBucketState) -> int:
        """Get current number of available tokens"""
        now = time.time()
        time_passed = now - state.last_refill
        tokens_to_add = time_passed * self.refill_rate
        return int(min(self.capacity, state.tokens + tokens_to_add))
    
    def get_reset_time(self, state: TokenBucketState) -> datetime:
        """Get time when bucket will be full"""
        tokens_needed = self.capacity - state.tokens
        if tokens_needed <= 0:
            return datetime.utcnow()
        
        seconds_to_full = tokens_needed / self.refill_rate
        return datetime.utcnow() + timedelta(seconds=seconds_to_full)


@dataclass
class SlidingWindowState:
    """Sliding window state"""
    requests: list[float]  # Timestamps of requests
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "requests": self.requests,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SlidingWindowState':
        """Create from dictionary"""
        return cls(
            requests=data["requests"],
            created_at=data.get("created_at", time.time())
        )


class SlidingWindow:
    """Sliding window rate limiting algorithm"""
    
    def __init__(self, limit: int, window: int):
        """
        Initialize sliding window
        
        Args:
            limit: Maximum requests in window
            window: Time window in seconds
        """
        self.limit = limit
        self.window = window
    
    def can_consume(self, state: SlidingWindowState, tokens: int = 1) -> tuple[bool, SlidingWindowState]:
        """
        Check if request can be consumed
        
        Args:
            state: Current window state
            tokens: Number of tokens to consume
            
        Returns:
            (allowed: bool, new_state: SlidingWindowState)
        """
        now = time.time()
        window_start = now - self.window
        
        # Remove old requests outside window
        recent_requests = [req for req in state.requests if req > window_start]
        
        # Check if adding new requests would exceed limit
        if len(recent_requests) + tokens <= self.limit:
            # Add new request timestamps
            new_requests = recent_requests + [now] * tokens
            new_state = SlidingWindowState(
                requests=new_requests,
                created_at=state.created_at
            )
            return True, new_state
        else:
            # Would exceed limit
            new_state = SlidingWindowState(
                requests=recent_requests,
                created_at=state.created_at
            )
            return False, new_state
    
    def get_remaining_requests(self, state: SlidingWindowState) -> int:
        """Get remaining requests in current window"""
        now = time.time()
        window_start = now - self.window
        
        recent_requests = [req for req in state.requests if req > window_start]
        return max(0, self.limit - len(recent_requests))
    
    def get_retry_after(self, state: SlidingWindowState) -> int:
        """Calculate seconds to wait before retry"""
        if not state.requests:
            return 0
        
        now = time.time()
        window_start = now - self.window
        
        # Find oldest request in current window
        recent_requests = [req for req in state.requests if req > window_start]
        if len(recent_requests) < self.limit:
            return 0
        
        # Time until oldest request falls out of window
        oldest_request = min(recent_requests)
        return max(1, int(oldest_request + self.window - now))
    
    def get_reset_time(self, state: SlidingWindowState) -> datetime:
        """Get time when window will reset"""
        if not state.requests:
            return datetime.utcnow()
        
        now = time.time()
        window_start = now - self.window
        recent_requests = [req for req in state.requests if req > window_start]
        
        if not recent_requests:
            return datetime.utcnow()
        
        # Window resets when oldest request expires
        oldest_request = min(recent_requests)
        reset_time = oldest_request + self.window
        return datetime.utcfromtimestamp(reset_time)
    
    def cleanup_old_requests(self, state: SlidingWindowState) -> SlidingWindowState:
        """Remove requests older than window"""
        now = time.time()
        window_start = now - self.window
        
        recent_requests = [req for req in state.requests if req > window_start]
        return SlidingWindowState(
            requests=recent_requests,
            created_at=state.created_at
        )


class FixedWindow:
    """Fixed window rate limiting algorithm"""
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
    
    def get_window_start(self, timestamp: float) -> float:
        """Get start of current window"""
        return (timestamp // self.window) * self.window
    
    def can_consume(self, current_count: int, tokens: int = 1) -> bool:
        """Check if tokens can be consumed in current window"""
        return current_count + tokens <= self.limit
    
    def get_remaining_requests(self, current_count: int) -> int:
        """Get remaining requests in current window"""
        return max(0, self.limit - current_count)
    
    def get_reset_time(self, timestamp: float) -> datetime:
        """Get time when current window resets"""
        window_start = self.get_window_start(timestamp)
        reset_timestamp = window_start + self.window
        return datetime.utcfromtimestamp(reset_timestamp)
    
    def get_retry_after(self, timestamp: float) -> int:
        """Get seconds until window resets"""
        reset_time = self.get_reset_time(timestamp)
        return max(1, int((reset_time - datetime.utcnow()).total_seconds()))