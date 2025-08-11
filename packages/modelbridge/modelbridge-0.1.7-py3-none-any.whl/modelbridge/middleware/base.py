"""
Base Middleware System for ModelBridge
Core middleware infrastructure and management
"""
import asyncio
import time
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..providers.base import GenerationRequest, GenerationResponse

logger = logging.getLogger(__name__)


class MiddlewarePhase(Enum):
    """Middleware execution phases"""
    PRE_REQUEST = "pre_request"        # Before request validation
    POST_VALIDATION = "post_validation"  # After request validation
    PRE_ROUTING = "pre_routing"        # Before provider routing
    POST_ROUTING = "post_routing"      # After provider selection
    PRE_EXECUTION = "pre_execution"    # Before provider execution
    POST_EXECUTION = "post_execution"  # After provider execution
    PRE_RESPONSE = "pre_response"      # Before response processing
    POST_RESPONSE = "post_response"    # After response ready
    ERROR_HANDLING = "error_handling"  # During error handling


@dataclass
class MiddlewareContext:
    """Context passed through middleware pipeline"""
    request_id: str
    request: GenerationRequest
    response: Optional[GenerationResponse] = None
    
    # Request metadata
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    authentication: Optional[Dict[str, Any]] = None
    
    # Routing information
    selected_provider: Optional[str] = None
    provider_ranking: List[str] = field(default_factory=list)
    routing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution metadata
    execution_start_time: Optional[float] = None
    execution_end_time: Optional[float] = None
    execution_duration: Optional[float] = None
    
    # Error information
    error: Optional[Exception] = None
    error_phase: Optional[MiddlewarePhase] = None
    
    # General metadata storage
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)
    
    def add_performance_metric(self, key: str, value: Any):
        """Add performance metric"""
        self.performance_metrics[key] = value
    
    def start_timing(self, key: str):
        """Start timing for a metric"""
        self.metadata[f"{key}_start_time"] = time.time()
    
    def end_timing(self, key: str) -> float:
        """End timing and return duration"""
        start_time = self.metadata.get(f"{key}_start_time")
        if start_time:
            duration = time.time() - start_time
            self.add_performance_metric(f"{key}_duration", duration)
            return duration
        return 0.0


class Middleware(ABC):
    """Base middleware class"""
    
    def __init__(self, name: str, enabled: bool = True, priority: int = 50):
        self.name = name
        self.enabled = enabled
        self.priority = priority  # Lower numbers execute first
        self.execution_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
    
    @abstractmethod
    async def process(
        self, 
        context: MiddlewareContext, 
        phase: MiddlewarePhase
    ) -> MiddlewareContext:
        """Process middleware logic"""
        pass
    
    def supports_phase(self, phase: MiddlewarePhase) -> bool:
        """Check if middleware supports a specific phase"""
        return True  # Override in subclasses if needed
    
    async def handle_error(
        self, 
        context: MiddlewareContext, 
        error: Exception
    ) -> MiddlewareContext:
        """Handle errors during middleware execution"""
        logger.error(f"Middleware {self.name} error: {error}")
        context.error = error
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        avg_execution_time = (
            self.total_execution_time / self.execution_count 
            if self.execution_count > 0 else 0.0
        )
        
        return {
            "name": self.name,
            "enabled": self.enabled,
            "priority": self.priority,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": avg_execution_time
        }


class MiddlewareManager:
    """Manages middleware pipeline execution"""
    
    def __init__(self):
        self.middlewares: List[Middleware] = []
        self.middleware_by_name: Dict[str, Middleware] = {}
        self.phase_middlewares: Dict[MiddlewarePhase, List[Middleware]] = {}
        self.execution_stats: Dict[str, Dict[str, Any]] = {}
        
        # Initialize phase mappings
        for phase in MiddlewarePhase:
            self.phase_middlewares[phase] = []
    
    def add_middleware(self, middleware: Middleware):
        """Add middleware to the pipeline"""
        if middleware.name in self.middleware_by_name:
            logger.warning(f"Middleware {middleware.name} already exists, replacing")
            self.remove_middleware(middleware.name)
        
        self.middlewares.append(middleware)
        self.middleware_by_name[middleware.name] = middleware
        
        # Add to phase mappings
        for phase in MiddlewarePhase:
            if middleware.supports_phase(phase):
                self.phase_middlewares[phase].append(middleware)
        
        # Sort middlewares by priority
        self._sort_middlewares()
        
        logger.info(f"Added middleware: {middleware.name}")
    
    def remove_middleware(self, name: str):
        """Remove middleware from pipeline"""
        if name not in self.middleware_by_name:
            logger.warning(f"Middleware {name} not found")
            return
        
        middleware = self.middleware_by_name[name]
        
        # Remove from main list
        self.middlewares.remove(middleware)
        del self.middleware_by_name[name]
        
        # Remove from phase mappings
        for phase_list in self.phase_middlewares.values():
            if middleware in phase_list:
                phase_list.remove(middleware)
        
        logger.info(f"Removed middleware: {name}")
    
    def enable_middleware(self, name: str):
        """Enable middleware"""
        if name in self.middleware_by_name:
            self.middleware_by_name[name].enabled = True
            logger.info(f"Enabled middleware: {name}")
    
    def disable_middleware(self, name: str):
        """Disable middleware"""
        if name in self.middleware_by_name:
            self.middleware_by_name[name].enabled = False
            logger.info(f"Disabled middleware: {name}")
    
    def _sort_middlewares(self):
        """Sort middlewares by priority"""
        self.middlewares.sort(key=lambda m: m.priority)
        
        # Re-sort phase mappings
        for phase in MiddlewarePhase:
            self.phase_middlewares[phase].sort(key=lambda m: m.priority)
    
    async def execute_phase(
        self, 
        context: MiddlewareContext, 
        phase: MiddlewarePhase
    ) -> MiddlewareContext:
        """Execute all middlewares for a specific phase"""
        
        phase_middlewares = self.phase_middlewares[phase]
        enabled_middlewares = [m for m in phase_middlewares if m.enabled]
        
        if not enabled_middlewares:
            return context
        
        logger.debug(f"Executing {len(enabled_middlewares)} middlewares for phase {phase.value}")
        
        for middleware in enabled_middlewares:
            try:
                start_time = time.time()
                
                # Execute middleware
                context = await middleware.process(context, phase)
                
                # Update statistics
                execution_time = time.time() - start_time
                middleware.execution_count += 1
                middleware.total_execution_time += execution_time
                
                # Check if middleware set an error
                if context.error:
                    logger.warning(f"Middleware {middleware.name} set error: {context.error}")
                    context.error_phase = phase
                    break
                
            except Exception as e:
                logger.error(f"Middleware {middleware.name} failed in phase {phase.value}: {e}")
                
                middleware.error_count += 1
                
                # Try to handle error
                try:
                    context = await middleware.handle_error(context, e)
                except Exception as handle_error:
                    logger.error(f"Error handling failed for {middleware.name}: {handle_error}")
                    context.error = e
                    context.error_phase = phase
                    break
        
        return context
    
    async def execute_error_handling(self, context: MiddlewareContext) -> MiddlewareContext:
        """Execute error handling middlewares"""
        return await self.execute_phase(context, MiddlewarePhase.ERROR_HANDLING)
    
    def get_middleware_stats(self) -> Dict[str, Any]:
        """Get statistics for all middlewares"""
        return {
            "total_middlewares": len(self.middlewares),
            "enabled_middlewares": len([m for m in self.middlewares if m.enabled]),
            "middleware_stats": [m.get_stats() for m in self.middlewares],
            "phase_distribution": {
                phase.value: len([m for m in middlewares if m.enabled])
                for phase, middlewares in self.phase_middlewares.items()
            }
        }
    
    def get_middleware_by_name(self, name: str) -> Optional[Middleware]:
        """Get middleware by name"""
        return self.middleware_by_name.get(name)
    
    def list_middlewares(self) -> List[str]:
        """List all middleware names"""
        return list(self.middleware_by_name.keys())
    
    def clear_all_middlewares(self):
        """Remove all middlewares"""
        self.middlewares.clear()
        self.middleware_by_name.clear()
        for phase in MiddlewarePhase:
            self.phase_middlewares[phase].clear()
        
        logger.info("Cleared all middlewares")


class ConditionalMiddleware(Middleware):
    """Middleware that executes conditionally"""
    
    def __init__(
        self, 
        name: str, 
        condition_func: Callable[[MiddlewareContext], bool],
        enabled: bool = True,
        priority: int = 50
    ):
        super().__init__(name, enabled, priority)
        self.condition_func = condition_func
    
    async def process(
        self, 
        context: MiddlewareContext, 
        phase: MiddlewarePhase
    ) -> MiddlewareContext:
        """Process only if condition is met"""
        
        if not self.condition_func(context):
            return context
        
        return await self._conditional_process(context, phase)
    
    @abstractmethod
    async def _conditional_process(
        self, 
        context: MiddlewareContext, 
        phase: MiddlewarePhase
    ) -> MiddlewareContext:
        """Override this method in subclasses"""
        pass


class MiddlewareChain:
    """Represents a chain of middlewares for a specific use case"""
    
    def __init__(self, name: str, middlewares: List[Middleware]):
        self.name = name
        self.manager = MiddlewareManager()
        
        # Add middlewares to the chain
        for middleware in middlewares:
            self.manager.add_middleware(middleware)
    
    async def execute(self, context: MiddlewareContext) -> MiddlewareContext:
        """Execute the complete middleware chain"""
        
        phases = [
            MiddlewarePhase.PRE_REQUEST,
            MiddlewarePhase.POST_VALIDATION,
            MiddlewarePhase.PRE_ROUTING,
            MiddlewarePhase.POST_ROUTING,
            MiddlewarePhase.PRE_EXECUTION,
            MiddlewarePhase.POST_EXECUTION,
            MiddlewarePhase.PRE_RESPONSE,
            MiddlewarePhase.POST_RESPONSE
        ]
        
        for phase in phases:
            context = await self.manager.execute_phase(context, phase)
            
            # Handle errors
            if context.error:
                context = await self.manager.execute_error_handling(context)
                break
        
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chain statistics"""
        return {
            "chain_name": self.name,
            "middleware_stats": self.manager.get_middleware_stats()
        }