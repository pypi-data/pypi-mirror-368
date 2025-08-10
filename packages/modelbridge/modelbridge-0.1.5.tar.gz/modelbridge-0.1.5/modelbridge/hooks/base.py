"""
Base Hooks System for ModelBridge
Core hook infrastructure for monitoring and logging
"""
import asyncio
import time
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Types of hooks"""
    LOGGING = "logging"
    MONITORING = "monitoring"
    NOTIFICATION = "notification"
    AUTHENTICATION = "authentication"
    CACHING = "caching"
    CUSTOM = "custom"


class HookEvent(Enum):
    """Hook event types"""
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    REQUEST_ERROR = "request_error"
    
    ROUTING_START = "routing_start"
    ROUTING_END = "routing_end"
    ROUTING_DECISION = "routing_decision"
    
    EXECUTION_START = "execution_start"
    EXECUTION_END = "execution_end"
    EXECUTION_ERROR = "execution_error"
    
    RESPONSE_START = "response_start"
    RESPONSE_END = "response_end"
    RESPONSE_ERROR = "response_error"
    
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"
    
    HEALTH_CHECK = "health_check"
    PERFORMANCE_ALERT = "performance_alert"
    
    CUSTOM = "custom"


@dataclass
class HookContext:
    """Context passed to hooks"""
    hook_id: str
    event: HookEvent
    timestamp: float = field(default_factory=time.time)
    
    # Request information
    request_id: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    
    # Provider information
    provider_name: Optional[str] = None
    model_id: Optional[str] = None
    
    # Performance metrics
    duration: Optional[float] = None
    cost: Optional[float] = None
    
    # Error information
    error: Optional[Exception] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # System information
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Custom data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)
    
    def add_system_metric(self, key: str, value: Any):
        """Add system metric"""
        self.system_metrics[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "hook_id": self.hook_id,
            "event": self.event.value,
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "provider_name": self.provider_name,
            "model_id": self.model_id,
            "duration": self.duration,
            "cost": self.cost,
            "error": str(self.error) if self.error else None,
            "error_details": self.error_details,
            "system_metrics": self.system_metrics,
            "metadata": self.metadata
        }


class Hook(ABC):
    """Base hook class"""
    
    def __init__(
        self, 
        name: str,
        events: List[HookEvent],
        enabled: bool = True,
        async_execution: bool = False
    ):
        self.hook_id = str(uuid.uuid4())
        self.name = name
        self.events = events
        self.enabled = enabled
        self.async_execution = async_execution
        
        # Statistics
        self.execution_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None
        
        # State
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the hook"""
        self.initialized = True
        return True
    
    @abstractmethod
    async def execute(self, context: HookContext):
        """Execute hook logic"""
        pass
    
    async def cleanup(self):
        """Cleanup hook resources"""
        pass
    
    def supports_event(self, event: HookEvent) -> bool:
        """Check if hook supports a specific event"""
        return event in self.events
    
    async def handle_error(self, context: HookContext, error: Exception):
        """Handle errors during hook execution"""
        logger.error(f"Hook {self.name} error: {error}")
    
    def get_hook_type(self) -> HookType:
        """Get hook type"""
        return HookType.CUSTOM  # Override in subclasses
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hook statistics"""
        avg_execution_time = (
            self.total_execution_time / self.execution_count
            if self.execution_count > 0 else 0.0
        )
        
        return {
            "hook_id": self.hook_id,
            "name": self.name,
            "enabled": self.enabled,
            "async_execution": self.async_execution,
            "supported_events": [e.value for e in self.events],
            "initialized": self.initialized,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": avg_execution_time,
            "last_execution": self.last_execution
        }


class HookManager:
    """Manages hooks and their execution"""
    
    def __init__(self, max_concurrent_hooks: int = 50):
        self.hooks: Dict[str, Hook] = {}
        self.hooks_by_event: Dict[HookEvent, List[Hook]] = {}
        self.hooks_by_type: Dict[HookType, List[Hook]] = {}
        self.max_concurrent_hooks = max_concurrent_hooks
        
        # Execution control
        self.hook_semaphore = asyncio.Semaphore(max_concurrent_hooks)
        self.execution_timeout = 30.0  # 30 seconds default timeout
        
        # Statistics
        self.total_executions = 0
        self.total_errors = 0
        self.concurrent_executions = 0
        
        # Initialize mappings
        for event in HookEvent:
            self.hooks_by_event[event] = []
        
        for hook_type in HookType:
            self.hooks_by_type[hook_type] = []
    
    async def register_hook(self, hook: Hook) -> bool:
        """Register a hook"""
        try:
            # Initialize hook
            if not await hook.initialize():
                logger.error(f"Failed to initialize hook: {hook.name}")
                return False
            
            # Add to collections
            self.hooks[hook.hook_id] = hook
            
            hook_type = hook.get_hook_type()
            self.hooks_by_type[hook_type].append(hook)
            
            # Add to event mappings
            for event in hook.events:
                self.hooks_by_event[event].append(hook)
            
            logger.info(f"Registered hook: {hook.name} (ID: {hook.hook_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering hook {hook.name}: {e}")
            return False
    
    async def unregister_hook(self, hook_id: str) -> bool:
        """Unregister a hook"""
        if hook_id not in self.hooks:
            logger.warning(f"Hook not found: {hook_id}")
            return False
        
        hook = self.hooks[hook_id]
        
        try:
            # Cleanup hook
            await hook.cleanup()
            
            # Remove from collections
            del self.hooks[hook_id]
            
            hook_type = hook.get_hook_type()
            self.hooks_by_type[hook_type] = [
                h for h in self.hooks_by_type[hook_type] if h.hook_id != hook_id
            ]
            
            # Remove from event mappings
            for event in hook.events:
                self.hooks_by_event[event] = [
                    h for h in self.hooks_by_event[event] if h.hook_id != hook_id
                ]
            
            logger.info(f"Unregistered hook: {hook.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering hook {hook.name}: {e}")
            return False
    
    async def trigger_event(self, event: HookEvent, context: HookContext):
        """Trigger all hooks for a specific event"""
        event_hooks = [h for h in self.hooks_by_event[event] if h.enabled]
        
        if not event_hooks:
            return
        
        logger.debug(f"Triggering {len(event_hooks)} hooks for event {event.value}")
        
        # Execute hooks
        if len(event_hooks) == 1:
            # Single hook - execute directly
            await self._execute_hook(event_hooks[0], context)
        else:
            # Multiple hooks - execute based on their async preference
            sync_hooks = [h for h in event_hooks if not h.async_execution]
            async_hooks = [h for h in event_hooks if h.async_execution]
            
            # Execute sync hooks sequentially
            for hook in sync_hooks:
                await self._execute_hook(hook, context)
            
            # Execute async hooks concurrently
            if async_hooks:
                tasks = [
                    self._execute_hook_with_semaphore(hook, context)
                    for hook in async_hooks
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_hook_with_semaphore(self, hook: Hook, context: HookContext):
        """Execute hook with semaphore protection"""
        async with self.hook_semaphore:
            await self._execute_hook(hook, context)
    
    async def _execute_hook(self, hook: Hook, context: HookContext):
        """Execute a single hook"""
        if not hook.enabled:
            return
        
        start_time = time.time()
        self.concurrent_executions += 1
        
        try:
            # Set hook context
            context.hook_id = hook.hook_id
            
            # Execute with timeout
            await asyncio.wait_for(
                hook.execute(context),
                timeout=self.execution_timeout
            )
            
            # Update statistics
            execution_time = time.time() - start_time
            hook.execution_count += 1
            hook.total_execution_time += execution_time
            hook.last_execution = time.time()
            
            self.total_executions += 1
            
        except asyncio.TimeoutError:
            logger.error(f"Hook {hook.name} timed out after {self.execution_timeout}s")
            hook.error_count += 1
            self.total_errors += 1
            
        except Exception as e:
            logger.error(f"Hook {hook.name} failed: {e}")
            hook.error_count += 1
            self.total_errors += 1
            
            # Try to handle error
            try:
                await hook.handle_error(context, e)
            except Exception as handle_error:
                logger.error(f"Error handling failed for {hook.name}: {handle_error}")
        
        finally:
            self.concurrent_executions -= 1
    
    async def trigger_request_start(
        self,
        request_id: str,
        request_data: Dict[str, Any]
    ):
        """Trigger request start event"""
        context = HookContext(
            hook_id="",
            event=HookEvent.REQUEST_START,
            request_id=request_id,
            request_data=request_data
        )
        
        await self.trigger_event(HookEvent.REQUEST_START, context)
    
    async def trigger_request_end(
        self,
        request_id: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        duration: float,
        cost: float = 0.0
    ):
        """Trigger request end event"""
        context = HookContext(
            hook_id="",
            event=HookEvent.REQUEST_END,
            request_id=request_id,
            request_data=request_data,
            response_data=response_data,
            duration=duration,
            cost=cost
        )
        
        await self.trigger_event(HookEvent.REQUEST_END, context)
    
    async def trigger_request_error(
        self,
        request_id: str,
        request_data: Dict[str, Any],
        error: Exception,
        error_details: Optional[Dict[str, Any]] = None
    ):
        """Trigger request error event"""
        context = HookContext(
            hook_id="",
            event=HookEvent.REQUEST_ERROR,
            request_id=request_id,
            request_data=request_data,
            error=error,
            error_details=error_details
        )
        
        await self.trigger_event(HookEvent.REQUEST_ERROR, context)
    
    async def trigger_routing_decision(
        self,
        request_id: str,
        provider_name: str,
        model_id: str,
        routing_metadata: Dict[str, Any]
    ):
        """Trigger routing decision event"""
        context = HookContext(
            hook_id="",
            event=HookEvent.ROUTING_DECISION,
            request_id=request_id,
            provider_name=provider_name,
            model_id=model_id,
            metadata=routing_metadata
        )
        
        await self.trigger_event(HookEvent.ROUTING_DECISION, context)
    
    async def trigger_performance_alert(
        self,
        alert_type: str,
        alert_data: Dict[str, Any]
    ):
        """Trigger performance alert event"""
        context = HookContext(
            hook_id="",
            event=HookEvent.PERFORMANCE_ALERT,
            metadata={
                "alert_type": alert_type,
                "alert_data": alert_data
            }
        )
        
        await self.trigger_event(HookEvent.PERFORMANCE_ALERT, context)
    
    async def trigger_health_check(self, health_data: Dict[str, Any]):
        """Trigger health check event"""
        context = HookContext(
            hook_id="",
            event=HookEvent.HEALTH_CHECK,
            system_metrics=health_data
        )
        
        await self.trigger_event(HookEvent.HEALTH_CHECK, context)
    
    def get_hooks_by_type(self, hook_type: HookType) -> List[Hook]:
        """Get hooks by type"""
        return [h for h in self.hooks_by_type[hook_type] if h.enabled]
    
    def get_hooks_by_event(self, event: HookEvent) -> List[Hook]:
        """Get hooks by event"""
        return [h for h in self.hooks_by_event[event] if h.enabled]
    
    def enable_hook(self, hook_id: str):
        """Enable a hook"""
        if hook_id in self.hooks:
            self.hooks[hook_id].enabled = True
            logger.info(f"Enabled hook: {self.hooks[hook_id].name}")
    
    def disable_hook(self, hook_id: str):
        """Disable a hook"""
        if hook_id in self.hooks:
            self.hooks[hook_id].enabled = False
            logger.info(f"Disabled hook: {self.hooks[hook_id].name}")
    
    def list_hooks(self) -> List[Dict[str, Any]]:
        """List all hooks with their information"""
        return [hook.get_stats() for hook in self.hooks.values()]
    
    def get_hook_stats(self) -> Dict[str, Any]:
        """Get overall hook statistics"""
        return {
            "total_hooks": len(self.hooks),
            "enabled_hooks": len([h for h in self.hooks.values() if h.enabled]),
            "hooks_by_type": {
                hook_type.value: len([h for h in hooks if h.enabled])
                for hook_type, hooks in self.hooks_by_type.items()
            },
            "hooks_by_event": {
                event.value: len([h for h in hooks if h.enabled])
                for event, hooks in self.hooks_by_event.items()
            },
            "total_executions": self.total_executions,
            "total_errors": self.total_errors,
            "concurrent_executions": self.concurrent_executions,
            "max_concurrent_hooks": self.max_concurrent_hooks
        }
    
    async def shutdown_all_hooks(self):
        """Shutdown all hooks"""
        for hook in list(self.hooks.values()):
            await self.unregister_hook(hook.hook_id)
        
        logger.info("All hooks shut down")
    
    def set_execution_timeout(self, timeout: float):
        """Set execution timeout for hooks"""
        self.execution_timeout = timeout
        logger.info(f"Set hook execution timeout to {timeout}s")


class ConditionalHook(Hook):
    """Hook that executes conditionally based on a function"""
    
    def __init__(
        self,
        name: str,
        events: List[HookEvent],
        condition_func: Callable[[HookContext], bool],
        enabled: bool = True,
        async_execution: bool = False
    ):
        super().__init__(name, events, enabled, async_execution)
        self.condition_func = condition_func
        self.conditions_checked = 0
        self.conditions_met = 0
    
    async def execute(self, context: HookContext):
        """Execute only if condition is met"""
        self.conditions_checked += 1
        
        if not self.condition_func(context):
            return
        
        self.conditions_met += 1
        return await self._conditional_execute(context)
    
    @abstractmethod
    async def _conditional_execute(self, context: HookContext):
        """Override this method in subclasses"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hook statistics including condition stats"""
        base_stats = super().get_stats()
        base_stats.update({
            "conditions_checked": self.conditions_checked,
            "conditions_met": self.conditions_met,
            "condition_success_rate": (
                self.conditions_met / self.conditions_checked
                if self.conditions_checked > 0 else 0.0
            )
        })
        return base_stats