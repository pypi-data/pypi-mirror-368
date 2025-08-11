"""
Base Plugin System for ModelBridge
Core plugin infrastructure and management
"""
import asyncio
import time
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import importlib
import inspect

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins"""
    ROUTING = "routing"
    PROCESSING = "processing"
    MONITORING = "monitoring"
    AUTHENTICATION = "authentication"
    CACHING = "caching"
    CUSTOM = "custom"


class PluginPhase(Enum):
    """Plugin execution phases"""
    INIT = "init"
    PRE_REQUEST = "pre_request"
    POST_REQUEST = "post_request"
    PRE_ROUTING = "pre_routing"
    POST_ROUTING = "post_routing"
    PRE_EXECUTION = "pre_execution"
    POST_EXECUTION = "post_execution"
    PRE_RESPONSE = "pre_response"
    POST_RESPONSE = "post_response"
    ERROR = "error"
    CLEANUP = "cleanup"


@dataclass
class PluginContext:
    """Context passed to plugins"""
    plugin_id: str
    request_id: str
    phase: PluginPhase
    
    # Core data
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    
    # Provider information
    provider_name: Optional[str] = None
    model_id: Optional[str] = None
    
    # Plugin-specific data storage
    plugin_data: Dict[str, Any] = field(default_factory=dict)
    
    # Shared data between plugins
    shared_data: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Execution metadata
    timestamp: float = field(default_factory=time.time)
    
    def set_plugin_data(self, key: str, value: Any):
        """Set plugin-specific data"""
        self.plugin_data[key] = value
    
    def get_plugin_data(self, key: str, default: Any = None) -> Any:
        """Get plugin-specific data"""
        return self.plugin_data.get(key, default)
    
    def set_shared_data(self, key: str, value: Any):
        """Set shared data between plugins"""
        self.shared_data[key] = value
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """Get shared data"""
        return self.shared_data.get(key, default)
    
    def add_metric(self, key: str, value: Any):
        """Add performance metric"""
        self.metrics[key] = value
    
    def get_metric(self, key: str, default: Any = None) -> Any:
        """Get performance metric"""
        return self.metrics.get(key, default)


@dataclass
class PluginConfig:
    """Plugin configuration"""
    name: str
    enabled: bool = True
    priority: int = 50  # Lower numbers execute first
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    supported_phases: List[PluginPhase] = field(default_factory=list)


class Plugin(ABC):
    """Base plugin class"""
    
    def __init__(self, config: PluginConfig):
        self.config = config
        self.plugin_id = str(uuid.uuid4())
        self.name = config.name
        self.enabled = config.enabled
        self.priority = config.priority
        
        # Statistics
        self.execution_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None
        
        # State
        self.initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    async def execute(self, context: PluginContext) -> PluginContext:
        """Execute plugin logic"""
        pass
    
    async def cleanup(self):
        """Cleanup plugin resources"""
        pass
    
    def supports_phase(self, phase: PluginPhase) -> bool:
        """Check if plugin supports a specific phase"""
        if not self.config.supported_phases:
            return True  # Support all phases if not specified
        return phase in self.config.supported_phases
    
    def get_dependencies(self) -> List[str]:
        """Get plugin dependencies"""
        return self.config.dependencies
    
    async def handle_error(self, context: PluginContext, error: Exception) -> PluginContext:
        """Handle errors during plugin execution"""
        logger.error(f"Plugin {self.name} error: {error}")
        context.error_data = {
            "plugin_name": self.name,
            "error": str(error),
            "timestamp": time.time()
        }
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        avg_execution_time = (
            self.total_execution_time / self.execution_count
            if self.execution_count > 0 else 0.0
        )
        
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "enabled": self.enabled,
            "priority": self.priority,
            "initialized": self.initialized,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": avg_execution_time,
            "last_execution": self.last_execution
        }
    
    def validate_config(self) -> bool:
        """Validate plugin configuration"""
        return True  # Override in subclasses
    
    def get_plugin_type(self) -> PluginType:
        """Get plugin type"""
        return PluginType.CUSTOM  # Override in subclasses


class PluginManager:
    """Manages plugins and their execution"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugins_by_type: Dict[PluginType, List[Plugin]] = {}
        self.plugins_by_phase: Dict[PluginPhase, List[Plugin]] = {}
        self.plugin_registry: Dict[str, Type[Plugin]] = {}
        
        # Dependency graph
        self.dependency_graph: Dict[str, List[str]] = {}
        self.execution_order: List[str] = []
        
        # Statistics
        self.total_executions = 0
        self.total_errors = 0
        
        # Initialize phase mappings
        for plugin_type in PluginType:
            self.plugins_by_type[plugin_type] = []
        
        for phase in PluginPhase:
            self.plugins_by_phase[phase] = []
    
    def register_plugin_class(self, plugin_class: Type[Plugin], name: str):
        """Register a plugin class"""
        self.plugin_registry[name] = plugin_class
        logger.info(f"Registered plugin class: {name}")
    
    async def load_plugin(self, config: PluginConfig) -> bool:
        """Load and initialize a plugin"""
        try:
            # Check if plugin class is registered
            if config.name not in self.plugin_registry:
                logger.error(f"Plugin class not registered: {config.name}")
                return False
            
            # Create plugin instance
            plugin_class = self.plugin_registry[config.name]
            plugin = plugin_class(config)
            
            # Validate configuration
            if not plugin.validate_config():
                logger.error(f"Invalid configuration for plugin: {config.name}")
                return False
            
            # Initialize plugin
            if not await plugin.initialize():
                logger.error(f"Failed to initialize plugin: {config.name}")
                return False
            
            # Add to collections
            self.plugins[plugin.plugin_id] = plugin
            
            plugin_type = plugin.get_plugin_type()
            self.plugins_by_type[plugin_type].append(plugin)
            
            # Add to phase mappings
            for phase in PluginPhase:
                if plugin.supports_phase(phase):
                    self.plugins_by_phase[phase].append(plugin)
            
            # Update dependency graph
            self._update_dependency_graph(plugin)
            
            # Recalculate execution order
            self._calculate_execution_order()
            
            plugin.initialized = True
            logger.info(f"Loaded plugin: {plugin.name} (ID: {plugin.plugin_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading plugin {config.name}: {e}")
            return False
    
    def _update_dependency_graph(self, plugin: Plugin):
        """Update dependency graph with new plugin"""
        self.dependency_graph[plugin.plugin_id] = plugin.get_dependencies()
    
    def _calculate_execution_order(self):
        """Calculate optimal plugin execution order based on dependencies and priorities"""
        # Topological sort considering dependencies and priorities
        plugins_to_sort = list(self.plugins.values())
        
        # Sort by priority first
        plugins_to_sort.sort(key=lambda p: p.priority)
        
        # Use priority-based sorting for plugin execution order
        self.execution_order = [p.plugin_id for p in plugins_to_sort if p.enabled]
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        if plugin_id not in self.plugins:
            logger.warning(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        
        try:
            # Cleanup plugin
            await plugin.cleanup()
            
            # Remove from collections
            del self.plugins[plugin_id]
            
            plugin_type = plugin.get_plugin_type()
            self.plugins_by_type[plugin_type] = [
                p for p in self.plugins_by_type[plugin_type] if p.plugin_id != plugin_id
            ]
            
            # Remove from phase mappings
            for phase in PluginPhase:
                self.plugins_by_phase[phase] = [
                    p for p in self.plugins_by_phase[phase] if p.plugin_id != plugin_id
                ]
            
            # Update dependency graph
            if plugin_id in self.dependency_graph:
                del self.dependency_graph[plugin_id]
            
            # Recalculate execution order
            self._calculate_execution_order()
            
            logger.info(f"Unloaded plugin: {plugin.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin.name}: {e}")
            return False
    
    async def execute_phase(self, phase: PluginPhase, context: PluginContext) -> PluginContext:
        """Execute all plugins for a specific phase"""
        phase_plugins = [p for p in self.plugins_by_phase[phase] if p.enabled]
        
        if not phase_plugins:
            return context
        
        # Sort by execution order
        ordered_plugins = []
        for plugin_id in self.execution_order:
            plugin = self.plugins.get(plugin_id)
            if plugin and plugin in phase_plugins:
                ordered_plugins.append(plugin)
        
        logger.debug(f"Executing {len(ordered_plugins)} plugins for phase {phase.value}")
        
        for plugin in ordered_plugins:
            try:
                start_time = time.time()
                
                # Update context
                context.plugin_id = plugin.plugin_id
                context.phase = phase
                
                # Execute plugin
                context = await plugin.execute(context)
                
                # Update statistics
                execution_time = time.time() - start_time
                plugin.execution_count += 1
                plugin.total_execution_time += execution_time
                plugin.last_execution = time.time()
                
                self.total_executions += 1
                
                # Check for errors in context
                if context.error_data:
                    logger.warning(f"Plugin {plugin.name} reported error: {context.error_data}")
                    break
                
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed in phase {phase.value}: {e}")
                
                plugin.error_count += 1
                self.total_errors += 1
                
                # Try to handle error
                try:
                    context = await plugin.handle_error(context, e)
                except Exception as handle_error:
                    logger.error(f"Error handling failed for {plugin.name}: {handle_error}")
                    context.error_data = {
                        "plugin_name": plugin.name,
                        "error": str(e),
                        "timestamp": time.time()
                    }
                    break
        
        return context
    
    async def execute_plugin_by_name(self, plugin_name: str, context: PluginContext) -> PluginContext:
        """Execute a specific plugin by name"""
        plugin = self.get_plugin_by_name(plugin_name)
        if not plugin:
            logger.warning(f"Plugin not found: {plugin_name}")
            return context
        
        if not plugin.enabled:
            logger.warning(f"Plugin disabled: {plugin_name}")
            return context
        
        try:
            start_time = time.time()
            context.plugin_id = plugin.plugin_id
            context = await plugin.execute(context)
            
            # Update statistics
            execution_time = time.time() - start_time
            plugin.execution_count += 1
            plugin.total_execution_time += execution_time
            plugin.last_execution = time.time()
            
        except Exception as e:
            logger.error(f"Plugin {plugin_name} execution failed: {e}")
            plugin.error_count += 1
            context = await plugin.handle_error(context, e)
        
        return context
    
    def get_plugin_by_name(self, name: str) -> Optional[Plugin]:
        """Get plugin by name"""
        for plugin in self.plugins.values():
            if plugin.name == name:
                return plugin
        return None
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """Get plugins by type"""
        return [p for p in self.plugins_by_type[plugin_type] if p.enabled]
    
    def enable_plugin(self, plugin_id: str):
        """Enable a plugin"""
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = True
            self._calculate_execution_order()
            logger.info(f"Enabled plugin: {self.plugins[plugin_id].name}")
    
    def disable_plugin(self, plugin_id: str):
        """Disable a plugin"""
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = False
            self._calculate_execution_order()
            logger.info(f"Disabled plugin: {self.plugins[plugin_id].name}")
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins with their information"""
        return [plugin.get_stats() for plugin in self.plugins.values()]
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get overall plugin statistics"""
        return {
            "total_plugins": len(self.plugins),
            "enabled_plugins": len([p for p in self.plugins.values() if p.enabled]),
            "plugins_by_type": {
                plugin_type.value: len([p for p in plugins if p.enabled])
                for plugin_type, plugins in self.plugins_by_type.items()
            },
            "total_executions": self.total_executions,
            "total_errors": self.total_errors,
            "plugin_details": self.list_plugins()
        }
    
    async def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a plugin"""
        if plugin_id not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_id]
        config = plugin.config
        
        # Unload current instance
        if not await self.unload_plugin(plugin_id):
            return False
        
        # Load new instance
        return await self.load_plugin(config)
    
    async def load_plugin_from_module(self, module_path: str, config: PluginConfig) -> bool:
        """Dynamically load a plugin from a Python module"""
        try:
            # Import module
            module = importlib.import_module(module_path)
            
            # Find plugin class in module
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Plugin) and obj != Plugin:
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"No Plugin subclass found in module: {module_path}")
                return False
            
            # Register and load
            self.register_plugin_class(plugin_class, config.name)
            return await self.load_plugin(config)
            
        except Exception as e:
            logger.error(f"Error loading plugin from module {module_path}: {e}")
            return False
    
    async def shutdown_all_plugins(self):
        """Shutdown all plugins"""
        for plugin in list(self.plugins.values()):
            await self.unload_plugin(plugin.plugin_id)
        
        logger.info("All plugins shut down")


class AsyncPlugin(Plugin):
    """Async plugin base class"""
    
    async def execute_async(self, context: PluginContext) -> PluginContext:
        """Async execution method"""
        return await self.execute(context)


class SyncPlugin(Plugin):
    """Synchronous plugin base class"""
    
    def execute_sync(self, context: PluginContext) -> PluginContext:
        """Synchronous execution method"""
        # This would be implemented by subclasses
        return context
    
    async def execute(self, context: PluginContext) -> PluginContext:
        """Wrapper for sync execution"""
        return self.execute_sync(context)