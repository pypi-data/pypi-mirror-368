"""
Health checking and status monitoring system
"""
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a system component"""
    component: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    last_checked: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "last_checked": self.last_checked.isoformat(),
            "response_time_ms": self.response_time_ms
        }
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        return self.status == HealthStatus.HEALTHY
    
    @property
    def is_critical(self) -> bool:
        """Check if component is in critical state"""
        return self.status == HealthStatus.UNHEALTHY


@dataclass
class SystemHealth:
    """Overall system health"""
    status: HealthStatus
    components: Dict[str, ComponentHealth] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "components": {
                name: component.to_dict() 
                for name, component in self.components.items()
            }
        }
    
    @property
    def healthy_components(self) -> List[str]:
        """Get list of healthy components"""
        return [name for name, comp in self.components.items() if comp.is_healthy]
    
    @property
    def unhealthy_components(self) -> List[str]:
        """Get list of unhealthy components"""
        return [name for name, comp in self.components.items() if comp.is_critical]
    
    @property
    def degraded_components(self) -> List[str]:
        """Get list of degraded components"""
        return [name for name, comp in self.components.items() if comp.status == HealthStatus.DEGRADED]


class HealthChecker:
    """Health checker for ModelBridge components"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.start_time = time.time()
        self._health_checks: Dict[str, Callable[[], Awaitable[ComponentHealth]]] = {}
        self._last_results: Dict[str, ComponentHealth] = {}
        self._running = False
        self._check_task: Optional[asyncio.Task] = None
        
        # Register default health checks
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health checks"""
        self.register_check("system", self._check_system_health)
    
    def register_check(self, component: str, check_func: Callable[[], Awaitable[ComponentHealth]]):
        """Register a health check for a component"""
        self._health_checks[component] = check_func
        logger.info(f"Registered health check for component: {component}")
    
    def unregister_check(self, component: str):
        """Unregister a health check"""
        if component in self._health_checks:
            del self._health_checks[component]
            if component in self._last_results:
                del self._last_results[component]
            logger.info(f"Unregistered health check for component: {component}")
    
    async def check_component(self, component: str) -> Optional[ComponentHealth]:
        """Check health of a specific component"""
        if component not in self._health_checks:
            return None
        
        try:
            start_time = time.time()
            health = await self._health_checks[component]()
            response_time = (time.time() - start_time) * 1000
            health.response_time_ms = response_time
            health.last_checked = datetime.utcnow()
            
            self._last_results[component] = health
            return health
            
        except Exception as e:
            logger.error(f"Health check failed for {component}: {e}")
            health = ComponentHealth(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                last_checked=datetime.utcnow()
            )
            self._last_results[component] = health
            return health
    
    async def check_all_components(self) -> Dict[str, ComponentHealth]:
        """Check health of all registered components"""
        if not self._health_checks:
            return {}
        
        # Run all health checks concurrently
        tasks = [
            self.check_component(component)
            for component in self._health_checks.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, result in enumerate(results):
            component = list(self._health_checks.keys())[i]
            if isinstance(result, Exception):
                health_results[component] = ComponentHealth(
                    component=component,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Exception during health check: {str(result)}"
                )
            elif result is not None:
                health_results[component] = result
        
        return health_results
    
    async def get_system_health(self) -> SystemHealth:
        """Get overall system health"""
        components = await self.check_all_components()
        
        # Determine overall system status
        if not components:
            status = HealthStatus.UNKNOWN
        elif all(comp.is_healthy for comp in components.values()):
            status = HealthStatus.HEALTHY
        elif any(comp.is_critical for comp in components.values()):
            status = HealthStatus.UNHEALTHY
        else:
            status = HealthStatus.DEGRADED
        
        uptime = time.time() - self.start_time
        
        return SystemHealth(
            status=status,
            components=components,
            timestamp=datetime.utcnow(),
            uptime_seconds=uptime
        )
    
    async def get_component_health(self, component: str) -> Optional[ComponentHealth]:
        """Get health of specific component"""
        if component in self._last_results:
            # Return cached result if recent (within check interval)
            last_check = self._last_results[component]
            age = (datetime.utcnow() - last_check.last_checked).total_seconds()
            if age < self.check_interval:
                return last_check
        
        # Perform fresh check
        return await self.check_component(component)
    
    async def start_periodic_checks(self):
        """Start periodic health checks"""
        if self._running:
            return
        
        self._running = True
        self._check_task = asyncio.create_task(self._periodic_check_loop())
        logger.info(f"Started periodic health checks (interval: {self.check_interval}s)")
    
    async def stop_periodic_checks(self):
        """Stop periodic health checks"""
        self._running = False
        
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            self._check_task = None
        
        logger.info("Stopped periodic health checks")
    
    async def _periodic_check_loop(self):
        """Periodic health check loop"""
        while self._running:
            try:
                await self.check_all_components()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic health check: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_system_health(self) -> ComponentHealth:
        """Basic system health check"""
        try:
            # Check basic system metrics
            uptime = time.time() - self.start_time
            
            details = {
                "uptime_seconds": uptime,
                "registered_checks": len(self._health_checks),
                "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
            }
            
            # Simple health criteria
            if uptime < 10:  # System just started
                status = HealthStatus.DEGRADED
                message = "System recently started"
            else:
                status = HealthStatus.HEALTHY
                message = "System operational"
            
            return ComponentHealth(
                component="system",
                status=status,
                message=message,
                details=details
            )
            
        except Exception as e:
            return ComponentHealth(
                component="system",
                status=HealthStatus.UNHEALTHY,
                message=f"System check failed: {str(e)}"
            )


class ProviderHealthChecker:
    """Specialized health checker for ModelBridge providers"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.provider_clients: Dict[str, Any] = {}
    
    def register_provider(self, provider_name: str, provider_client: Any):
        """Register a provider for health checking"""
        self.provider_clients[provider_name] = provider_client
        
        # Create health check function for this provider
        async def provider_health_check():
            return await self._check_provider_health(provider_name, provider_client)
        
        self.health_checker.register_check(f"provider_{provider_name}", provider_health_check)
        logger.info(f"Registered health check for provider: {provider_name}")
    
    def unregister_provider(self, provider_name: str):
        """Unregister a provider"""
        if provider_name in self.provider_clients:
            del self.provider_clients[provider_name]
        
        self.health_checker.unregister_check(f"provider_{provider_name}")
        logger.info(f"Unregistered health check for provider: {provider_name}")
    
    async def _check_provider_health(self, provider_name: str, provider_client: Any) -> ComponentHealth:
        """Check health of a specific provider"""
        try:
            # Try to get a health check from the provider
            if hasattr(provider_client, 'health_check'):
                health_result = await provider_client.health_check()
                
                if isinstance(health_result, dict):
                    status_str = health_result.get('status', 'unknown').lower()
                    if status_str == 'healthy':
                        status = HealthStatus.HEALTHY
                    elif status_str == 'degraded':
                        status = HealthStatus.DEGRADED
                    else:
                        status = HealthStatus.UNHEALTHY
                    
                    return ComponentHealth(
                        component=f"provider_{provider_name}",
                        status=status,
                        message=health_result.get('message', f'Provider {provider_name} status: {status_str}'),
                        details=health_result
                    )
            
            # Fallback: assume healthy if provider exists and is initialized
            if hasattr(provider_client, '_initialized') and provider_client._initialized:
                return ComponentHealth(
                    component=f"provider_{provider_name}",
                    status=HealthStatus.HEALTHY,
                    message=f"Provider {provider_name} is initialized"
                )
            else:
                return ComponentHealth(
                    component=f"provider_{provider_name}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Provider {provider_name} not initialized"
                )
                
        except Exception as e:
            return ComponentHealth(
                component=f"provider_{provider_name}",
                status=HealthStatus.UNHEALTHY,
                message=f"Provider {provider_name} health check failed: {str(e)}"
            )


class CacheHealthChecker:
    """Specialized health checker for cache systems"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.cache_instances: Dict[str, Any] = {}
    
    def register_cache(self, cache_name: str, cache_instance: Any):
        """Register a cache for health checking"""
        self.cache_instances[cache_name] = cache_instance
        
        async def cache_health_check():
            return await self._check_cache_health(cache_name, cache_instance)
        
        self.health_checker.register_check(f"cache_{cache_name}", cache_health_check)
        logger.info(f"Registered health check for cache: {cache_name}")
    
    def unregister_cache(self, cache_name: str):
        """Unregister a cache"""
        if cache_name in self.cache_instances:
            del self.cache_instances[cache_name]
        
        self.health_checker.unregister_check(f"cache_{cache_name}")
    
    async def _check_cache_health(self, cache_name: str, cache_instance: Any) -> ComponentHealth:
        """Check health of a cache instance"""
        try:
            # Try to perform a basic cache operation
            test_key = f"__health_check_{int(time.time())}"
            test_value = "health_check"
            
            # Test write
            await cache_instance.set(test_key, test_value, ttl=5)
            
            # Test read
            retrieved_value = await cache_instance.get(test_key)
            
            # Test delete
            await cache_instance.delete(test_key)
            
            # Get cache stats if available
            stats = {}
            if hasattr(cache_instance, 'get_stats'):
                stats = await cache_instance.get_stats()
            
            if retrieved_value == test_value:
                return ComponentHealth(
                    component=f"cache_{cache_name}",
                    status=HealthStatus.HEALTHY,
                    message=f"Cache {cache_name} operations successful",
                    details={"stats": stats}
                )
            else:
                return ComponentHealth(
                    component=f"cache_{cache_name}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Cache {cache_name} read/write test failed"
                )
                
        except Exception as e:
            return ComponentHealth(
                component=f"cache_{cache_name}",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache {cache_name} health check failed: {str(e)}"
            )


class RateLimitHealthChecker:
    """Specialized health checker for rate limiting systems"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.rate_limiters: Dict[str, Any] = {}
    
    def register_rate_limiter(self, name: str, rate_limiter: Any):
        """Register a rate limiter for health checking"""
        self.rate_limiters[name] = rate_limiter
        
        async def rate_limit_health_check():
            return await self._check_rate_limiter_health(name, rate_limiter)
        
        self.health_checker.register_check(f"ratelimit_{name}", rate_limit_health_check)
        logger.info(f"Registered health check for rate limiter: {name}")
    
    def unregister_rate_limiter(self, name: str):
        """Unregister a rate limiter"""
        if name in self.rate_limiters:
            del self.rate_limiters[name]
        
        self.health_checker.unregister_check(f"ratelimit_{name}")
    
    async def _check_rate_limiter_health(self, name: str, rate_limiter: Any) -> ComponentHealth:
        """Check health of a rate limiter"""
        try:
            # Try to get health check from rate limiter if available
            if hasattr(rate_limiter, 'health_check'):
                health_result = await rate_limiter.health_check()
                
                if isinstance(health_result, dict):
                    status_str = health_result.get('status', 'unknown').lower()
                    if status_str == 'healthy':
                        status = HealthStatus.HEALTHY
                    elif status_str == 'degraded':
                        status = HealthStatus.DEGRADED
                    else:
                        status = HealthStatus.UNHEALTHY
                    
                    return ComponentHealth(
                        component=f"ratelimit_{name}",
                        status=status,
                        message=health_result.get('message', f'Rate limiter {name} status: {status_str}'),
                        details=health_result
                    )
            
            # Fallback: check basic attributes
            if hasattr(rate_limiter, '_initialized') and rate_limiter._initialized:
                return ComponentHealth(
                    component=f"ratelimit_{name}",
                    status=HealthStatus.HEALTHY,
                    message=f"Rate limiter {name} is initialized"
                )
            else:
                return ComponentHealth(
                    component=f"ratelimit_{name}",
                    status=HealthStatus.DEGRADED,
                    message=f"Rate limiter {name} initialization status unknown"
                )
                
        except Exception as e:
            return ComponentHealth(
                component=f"ratelimit_{name}",
                status=HealthStatus.UNHEALTHY,
                message=f"Rate limiter {name} health check failed: {str(e)}"
            )