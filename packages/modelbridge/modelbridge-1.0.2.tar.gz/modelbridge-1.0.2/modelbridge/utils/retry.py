"""
Retry logic with exponential backoff and circuit breaker patterns
"""
import asyncio
import time
import random
from typing import TypeVar, Callable, Optional, Any, Union, Awaitable, Dict
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Circuit tripped, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0     # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_range: float = 0.1  # ±10% random jitter
    
    # Retryable exceptions
    retryable_exceptions: tuple = (
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError,
    )
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: float = 60.0  # Time before trying half-open
    success_threshold: int = 2  # Successes needed to close circuit


@dataclass
class CircuitBreaker:
    """Circuit breaker implementation"""
    name: str
    config: RetryConfig
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    
    def record_success(self):
        """Record a successful call"""
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call"""
        self.last_failure_time = time.time()
        self.failure_count += 1
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._open_circuit()
        elif self.state == CircuitState.HALF_OPEN:
            # Single failure in half-open reopens circuit
            self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit breaker"""
        self.state = CircuitState.OPEN
        self.success_count = 0
        logger.warning(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")
    
    def _close_circuit(self):
        """Close the circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' closed")
    
    def _try_half_open(self):
        """Attempt to move to half-open state"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' attempting recovery (half-open)")
    
    def can_attempt(self) -> bool:
        """Check if a request can be attempted"""
        if not self.config.circuit_breaker_enabled:
            return True
        
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if enough time has passed to try half-open
            if self.last_failure_time:
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure >= self.config.recovery_timeout:
                    self._try_half_open()
                    return True
            return False
        
        # HALF_OPEN state - allow attempt
        return True
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self.state == CircuitState.OPEN


class RetryManager:
    """Manages retry logic and circuit breakers"""
    
    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def get_circuit_breaker(self, name: str, config: RetryConfig) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self._circuit_breakers:
            self._circuit_breakers[name] = CircuitBreaker(name, config)
        return self._circuit_breakers[name]
    
    async def retry_async(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        config: Optional[RetryConfig] = None,
        circuit_breaker_name: Optional[str] = None,
        **kwargs
    ) -> T:
        """
        Execute an async function with retry logic and circuit breaker
        
        Args:
            func: Async function to execute
            config: Retry configuration
            circuit_breaker_name: Name for circuit breaker tracking
            *args, **kwargs: Arguments for the function
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        config = config or RetryConfig()
        
        # Get circuit breaker if enabled
        circuit_breaker = None
        if config.circuit_breaker_enabled and circuit_breaker_name:
            circuit_breaker = self.get_circuit_breaker(circuit_breaker_name, config)
            
            # Check if circuit allows attempt
            if not circuit_breaker.can_attempt():
                raise ConnectionError(f"Circuit breaker '{circuit_breaker_name}' is open")
        
        last_exception = None
        delay = config.initial_delay
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                # Log attempt
                if attempt > 1:
                    logger.info(f"Retry attempt {attempt}/{config.max_attempts} for {func.__name__}")
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Record success if circuit breaker is active
                if circuit_breaker:
                    circuit_breaker.record_success()
                
                return result
                
            except config.retryable_exceptions as e:
                last_exception = e
                
                # Record failure if circuit breaker is active
                if circuit_breaker:
                    circuit_breaker.record_failure()
                
                # Check if we should retry
                if attempt >= config.max_attempts:
                    logger.error(f"All {config.max_attempts} retry attempts failed for {func.__name__}: {e}")
                    break
                
                # Calculate delay with exponential backoff
                if config.jitter:
                    jitter = delay * config.jitter_range * (2 * random.random() - 1)
                    actual_delay = min(delay + jitter, config.max_delay)
                else:
                    actual_delay = min(delay, config.max_delay)
                
                logger.warning(
                    f"Attempt {attempt} failed for {func.__name__}: {e}. "
                    f"Retrying in {actual_delay:.2f}s..."
                )
                
                # Wait before retry
                await asyncio.sleep(actual_delay)
                
                # Increase delay for next attempt
                delay *= config.exponential_base
                
            except Exception as e:
                # Non-retryable exception
                logger.error(f"Non-retryable exception in {func.__name__}: {e}")
                
                # Record failure if circuit breaker is active
                if circuit_breaker:
                    circuit_breaker.record_failure()
                
                raise
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        
        raise RuntimeError(f"Retry logic failed for {func.__name__}")
    
    def retry_sync(
        self,
        func: Callable[..., T],
        *args,
        config: Optional[RetryConfig] = None,
        circuit_breaker_name: Optional[str] = None,
        **kwargs
    ) -> T:
        """
        Execute a sync function with retry logic and circuit breaker
        
        Args:
            func: Sync function to execute
            config: Retry configuration
            circuit_breaker_name: Name for circuit breaker tracking
            *args, **kwargs: Arguments for the function
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        config = config or RetryConfig()
        
        # Get circuit breaker if enabled
        circuit_breaker = None
        if config.circuit_breaker_enabled and circuit_breaker_name:
            circuit_breaker = self.get_circuit_breaker(circuit_breaker_name, config)
            
            # Check if circuit allows attempt
            if not circuit_breaker.can_attempt():
                raise ConnectionError(f"Circuit breaker '{circuit_breaker_name}' is open")
        
        last_exception = None
        delay = config.initial_delay
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                # Log attempt
                if attempt > 1:
                    logger.info(f"Retry attempt {attempt}/{config.max_attempts} for {func.__name__}")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Record success if circuit breaker is active
                if circuit_breaker:
                    circuit_breaker.record_success()
                
                return result
                
            except config.retryable_exceptions as e:
                last_exception = e
                
                # Record failure if circuit breaker is active
                if circuit_breaker:
                    circuit_breaker.record_failure()
                
                # Check if we should retry
                if attempt >= config.max_attempts:
                    logger.error(f"All {config.max_attempts} retry attempts failed for {func.__name__}: {e}")
                    break
                
                # Calculate delay with exponential backoff
                if config.jitter:
                    jitter = delay * config.jitter_range * (2 * random.random() - 1)
                    actual_delay = min(delay + jitter, config.max_delay)
                else:
                    actual_delay = min(delay, config.max_delay)
                
                logger.warning(
                    f"Attempt {attempt} failed for {func.__name__}: {e}. "
                    f"Retrying in {actual_delay:.2f}s..."
                )
                
                # Wait before retry
                time.sleep(actual_delay)
                
                # Increase delay for next attempt
                delay *= config.exponential_base
                
            except Exception as e:
                # Non-retryable exception
                logger.error(f"Non-retryable exception in {func.__name__}: {e}")
                
                # Record failure if circuit breaker is active
                if circuit_breaker:
                    circuit_breaker.record_failure()
                
                raise
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        
        raise RuntimeError(f"Retry logic failed for {func.__name__}")


# Global retry manager instance
retry_manager = RetryManager()


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    circuit_breaker_name: Optional[str] = None,
    **retry_kwargs
):
    """
    Decorator for adding retry logic to functions
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        exponential_base: Base for exponential backoff
        circuit_breaker_name: Optional circuit breaker name
        **retry_kwargs: Additional arguments for RetryConfig
        
    Usage:
        @with_retry(max_attempts=5, initial_delay=2.0)
        async def fetch_data():
            # Function that might fail
            pass
    """
    def decorator(func):
        config = RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            exponential_base=exponential_base,
            **retry_kwargs
        )
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await retry_manager.retry_async(
                    func, *args,
                    config=config,
                    circuit_breaker_name=circuit_breaker_name,
                    **kwargs
                )
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return retry_manager.retry_sync(
                    func, *args,
                    config=config,
                    circuit_breaker_name=circuit_breaker_name,
                    **kwargs
                )
            return sync_wrapper
    
    return decorator