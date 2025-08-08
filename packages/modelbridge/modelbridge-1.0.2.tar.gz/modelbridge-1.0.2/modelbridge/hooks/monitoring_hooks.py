"""
Monitoring Hooks for ModelBridge
Hooks for system monitoring and performance tracking
"""
import time
import json
import psutil
import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque

from .base import Hook, HookContext, HookEvent, HookType

logger = logging.getLogger(__name__)


class MetricsHook(Hook):
    """Hook for collecting and aggregating metrics"""
    
    def __init__(
        self,
        name: str = "metrics_collector",
        events: Optional[List[HookEvent]] = None,
        metrics_store: Optional[Dict] = None
    ):
        if events is None:
            events = [
                HookEvent.REQUEST_END,
                HookEvent.REQUEST_ERROR,
                HookEvent.ROUTING_DECISION,
                HookEvent.EXECUTION_END,
                HookEvent.PERFORMANCE_ALERT
            ]
        
        super().__init__(name, events, enabled=True, async_execution=True)
        
        # Metrics storage
        self.metrics_store = metrics_store or {}
        self.request_metrics: Dict[str, Dict[str, Any]] = {}
        self.provider_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.system_metrics: Dict[str, Any] = {}
        
        # Time-series data
        self.response_times: deque = deque(maxlen=1000)
        self.error_rates: deque = deque(maxlen=1000)
        self.cost_tracking: deque = deque(maxlen=1000)
        
        # Aggregated counters
        self.total_requests = 0
        self.total_errors = 0
        self.total_cost = 0.0
        self.provider_usage: Dict[str, int] = defaultdict(int)
        
        # Performance thresholds
        self.response_time_threshold = 5.0  # seconds
        self.error_rate_threshold = 0.1     # 10%
        self.cost_threshold = 1.0           # per request
    
    def get_hook_type(self) -> HookType:
        """Monitoring hook type"""
        return HookType.MONITORING
    
    async def execute(self, context: HookContext):
        """Collect metrics based on the event"""
        if context.event == HookEvent.REQUEST_END:
            await self._collect_request_metrics(context)
        
        elif context.event == HookEvent.REQUEST_ERROR:
            await self._collect_error_metrics(context)
        
        elif context.event == HookEvent.ROUTING_DECISION:
            await self._collect_routing_metrics(context)
        
        elif context.event == HookEvent.EXECUTION_END:
            await self._collect_execution_metrics(context)
        
        elif context.event == HookEvent.PERFORMANCE_ALERT:
            await self._collect_alert_metrics(context)
    
    async def _collect_request_metrics(self, context: HookContext):
        """Collect metrics from successful requests"""
        if not context.request_id:
            return
        
        self.total_requests += 1
        
        # Store request metrics
        request_metrics = {
            "timestamp": context.timestamp,
            "duration": context.duration or 0.0,
            "cost": context.cost or 0.0,
            "provider": context.provider_name,
            "model": context.model_id
        }
        
        self.request_metrics[context.request_id] = request_metrics
        
        # Update time series
        if context.duration:
            self.response_times.append({
                "timestamp": context.timestamp,
                "value": context.duration,
                "provider": context.provider_name
            })
        
        if context.cost:
            self.total_cost += context.cost
            self.cost_tracking.append({
                "timestamp": context.timestamp,
                "value": context.cost,
                "provider": context.provider_name
            })
        
        # Update provider usage
        if context.provider_name:
            self.provider_usage[context.provider_name] += 1
    
    async def _collect_error_metrics(self, context: HookContext):
        """Collect metrics from error events"""
        self.total_errors += 1
        
        # Update error rate time series
        self.error_rates.append({
            "timestamp": context.timestamp,
            "error": str(context.error) if context.error else "unknown",
            "provider": context.provider_name,
            "request_id": context.request_id
        })
        
        # Update provider error tracking
        if context.provider_name:
            provider_key = context.provider_name
            if provider_key not in self.provider_metrics:
                self.provider_metrics[provider_key] = {"errors": 0, "total_requests": 0}
            
            self.provider_metrics[provider_key]["errors"] += 1
    
    async def _collect_routing_metrics(self, context: HookContext):
        """Collect routing decision metrics"""
        routing_data = {
            "timestamp": context.timestamp,
            "selected_provider": context.provider_name,
            "selected_model": context.model_id,
            "routing_metadata": context.metadata
        }
        
        # Store routing decision
        if context.request_id:
            self.request_metrics.setdefault(context.request_id, {}).update({
                "routing_decision": routing_data
            })
    
    async def _collect_execution_metrics(self, context: HookContext):
        """Collect execution metrics"""
        if context.provider_name and context.duration:
            provider_key = context.provider_name
            if provider_key not in self.provider_metrics:
                self.provider_metrics[provider_key] = {
                    "total_requests": 0,
                    "total_duration": 0.0,
                    "errors": 0
                }
            
            provider_metrics = self.provider_metrics[provider_key]
            provider_metrics["total_requests"] += 1
            provider_metrics["total_duration"] += context.duration
    
    async def _collect_alert_metrics(self, context: HookContext):
        """Collect performance alert metrics"""
        alert_type = context.get_metadata("alert_type", "unknown")
        alert_data = context.get_metadata("alert_data", {})
        
        # Log the alert
        logger.warning(f"Performance alert: {alert_type} - {alert_data}")
        
        # Store alert in metrics
        alerts_key = "performance_alerts"
        if alerts_key not in self.system_metrics:
            self.system_metrics[alerts_key] = []
        
        self.system_metrics[alerts_key].append({
            "timestamp": context.timestamp,
            "type": alert_type,
            "data": alert_data
        })
        
        # Keep only recent alerts
        self.system_metrics[alerts_key] = self.system_metrics[alerts_key][-100:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        current_time = time.time()
        
        # Calculate rates
        error_rate = self.total_errors / self.total_requests if self.total_requests > 0 else 0.0
        avg_cost = self.total_cost / self.total_requests if self.total_requests > 0 else 0.0
        
        # Calculate average response time
        recent_response_times = [r["value"] for r in list(self.response_times)[-100:]]
        avg_response_time = sum(recent_response_times) / len(recent_response_times) if recent_response_times else 0.0
        
        # Provider statistics
        provider_stats = {}
        for provider, metrics in self.provider_metrics.items():
            total_reqs = metrics.get("total_requests", 0)
            provider_stats[provider] = {
                "total_requests": total_reqs,
                "error_rate": metrics.get("errors", 0) / total_reqs if total_reqs > 0 else 0.0,
                "avg_response_time": metrics.get("total_duration", 0.0) / total_reqs if total_reqs > 0 else 0.0,
                "usage_percentage": self.provider_usage.get(provider, 0) / self.total_requests * 100 if self.total_requests > 0 else 0.0
            }
        
        return {
            "timestamp": current_time,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": error_rate,
            "total_cost": self.total_cost,
            "avg_cost_per_request": avg_cost,
            "avg_response_time": avg_response_time,
            "provider_stats": provider_stats,
            "provider_usage": dict(self.provider_usage),
            "recent_alerts": len(self.system_metrics.get("performance_alerts", [])),
            "data_points": {
                "response_times": len(self.response_times),
                "error_events": len(self.error_rates),
                "cost_events": len(self.cost_tracking)
            }
        }
    
    def get_time_series_data(self, metric_type: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get time series data for a specific metric"""
        cutoff_time = time.time() - (hours * 3600)
        
        if metric_type == "response_times":
            return [r for r in self.response_times if r["timestamp"] > cutoff_time]
        elif metric_type == "error_rates":
            return [e for e in self.error_rates if e["timestamp"] > cutoff_time]
        elif metric_type == "costs":
            return [c for c in self.cost_tracking if c["timestamp"] > cutoff_time]
        else:
            return []


class PerformanceHook(Hook):
    """Hook for monitoring system performance"""
    
    def __init__(
        self,
        name: str = "performance_monitor",
        events: Optional[List[HookEvent]] = None,
        monitoring_interval: float = 60.0  # Monitor every minute
    ):
        if events is None:
            events = [HookEvent.HEALTH_CHECK, HookEvent.REQUEST_END]
        
        super().__init__(name, events, enabled=True, async_execution=True)
        
        self.monitoring_interval = monitoring_interval
        self.performance_history: deque = deque(maxlen=1440)  # 24 hours of minute data
        
        # Performance thresholds
        self.cpu_threshold = 80.0      # 80% CPU usage
        self.memory_threshold = 85.0   # 85% Memory usage
        self.disk_threshold = 90.0     # 90% Disk usage
        
        # Last measurements
        self.last_system_check = 0.0
    
    def get_hook_type(self) -> HookType:
        """Monitoring hook type"""
        return HookType.MONITORING
    
    async def execute(self, context: HookContext):
        """Monitor system performance"""
        current_time = time.time()
        
        # Check if it's time for system monitoring
        if current_time - self.last_system_check > self.monitoring_interval:
            await self._collect_system_performance(context)
            self.last_system_check = current_time
        
        # Always check for performance issues on request end
        if context.event == HookEvent.REQUEST_END:
            await self._check_request_performance(context)
    
    async def _collect_system_performance(self, context: HookContext):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O (if available)
            network_io = psutil.net_io_counters()
            
            # Process information
            current_process = psutil.Process()
            process_memory = current_process.memory_info()
            process_cpu = current_process.cpu_percent()
            
            performance_data = {
                "timestamp": context.timestamp,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "network_bytes_sent": network_io.bytes_sent if network_io else 0,
                "network_bytes_recv": network_io.bytes_recv if network_io else 0,
                "process_memory_rss": process_memory.rss,
                "process_memory_vms": process_memory.vms,
                "process_cpu_percent": process_cpu
            }
            
            # Store performance data
            self.performance_history.append(performance_data)
            
            # Check thresholds and generate alerts
            await self._check_performance_thresholds(performance_data, context)
            
        except Exception as e:
            logger.error(f"Error collecting system performance: {e}")
    
    async def _check_performance_thresholds(self, performance_data: Dict[str, Any], context: HookContext):
        """Check performance thresholds and generate alerts"""
        alerts = []
        
        if performance_data["cpu_percent"] > self.cpu_threshold:
            alerts.append({
                "type": "high_cpu_usage",
                "value": performance_data["cpu_percent"],
                "threshold": self.cpu_threshold
            })
        
        if performance_data["memory_percent"] > self.memory_threshold:
            alerts.append({
                "type": "high_memory_usage",
                "value": performance_data["memory_percent"],
                "threshold": self.memory_threshold
            })
        
        if performance_data["disk_percent"] > self.disk_threshold:
            alerts.append({
                "type": "high_disk_usage",
                "value": performance_data["disk_percent"],
                "threshold": self.disk_threshold
            })
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance alert: {alert}")
        
        # Store alerts in context for other hooks to process
        if alerts:
            context.set_metadata("performance_alerts", alerts)
    
    async def _check_request_performance(self, context: HookContext):
        """Check individual request performance"""
        if not context.duration:
            return
        
        # Check for slow requests (> 10 seconds)
        if context.duration > 10.0:
            logger.warning(f"Slow request detected: {context.request_id} took {context.duration:.2f}s")
            
            context.set_metadata("slow_request_alert", {
                "request_id": context.request_id,
                "duration": context.duration,
                "provider": context.provider_name
            })
    
    def get_current_performance(self) -> Dict[str, Any]:
        """Get current system performance"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error getting current performance: {e}")
            return {}
    
    def get_performance_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get performance history for specified hours"""
        cutoff_time = time.time() - (hours * 3600)
        return [p for p in self.performance_history if p["timestamp"] > cutoff_time]


class HealthCheckHook(Hook):
    """Hook for system health monitoring"""
    
    def __init__(
        self,
        name: str = "health_monitor",
        events: Optional[List[HookEvent]] = None,
        health_check_interval: float = 300.0  # 5 minutes
    ):
        if events is None:
            events = [HookEvent.HEALTH_CHECK, HookEvent.SYSTEM_START, HookEvent.SYSTEM_STOP]
        
        super().__init__(name, events, enabled=True, async_execution=True)
        
        self.health_check_interval = health_check_interval
        self.health_history: deque = deque(maxlen=288)  # 24 hours of 5-minute data
        
        # Health components to check
        self.health_components = [
            "system_resources",
            "database_connection",
            "provider_connectivity",
            "cache_status",
            "disk_space"
        ]
        
        self.last_health_check = 0.0
        self.current_health_status = "unknown"
    
    def get_hook_type(self) -> HookType:
        """Monitoring hook type"""
        return HookType.MONITORING
    
    async def execute(self, context: HookContext):
        """Perform health checks"""
        if context.event == HookEvent.HEALTH_CHECK:
            await self._perform_health_check(context)
        
        elif context.event == HookEvent.SYSTEM_START:
            await self._system_startup_health_check(context)
        
        elif context.event == HookEvent.SYSTEM_STOP:
            await self._system_shutdown_health_check(context)
    
    async def _perform_health_check(self, context: HookContext):
        """Perform comprehensive health check"""
        health_results = {}
        overall_healthy = True
        
        # Check system resources
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            
            system_healthy = cpu_percent < 90 and memory_percent < 95 and disk_percent < 95
            health_results["system_resources"] = {
                "status": "healthy" if system_healthy else "unhealthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }
            
            if not system_healthy:
                overall_healthy = False
                
        except Exception as e:
            health_results["system_resources"] = {"status": "error", "error": str(e)}
            overall_healthy = False
        
        # Check disk space
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024**3)  # Convert to GB
            disk_healthy = free_gb > 1.0  # At least 1GB free
            
            health_results["disk_space"] = {
                "status": "healthy" if disk_healthy else "unhealthy",
                "free_gb": free_gb,
                "total_gb": disk.total / (1024**3)
            }
            
            if not disk_healthy:
                overall_healthy = False
                
        except Exception as e:
            health_results["disk_space"] = {"status": "error", "error": str(e)}
            overall_healthy = False
        
        # Store health check results
        health_record = {
            "timestamp": context.timestamp,
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "components": health_results
        }
        
        self.health_history.append(health_record)
        self.current_health_status = health_record["overall_status"]
        
        # Update context with health data
        context.system_metrics.update(health_results)
        
        # Log health status
        if not overall_healthy:
            logger.warning(f"Health check failed: {health_results}")
        else:
            logger.debug("Health check passed")
    
    async def _system_startup_health_check(self, context: HookContext):
        """Perform health check on system startup"""
        logger.info("Performing startup health check")
        
        startup_checks = {
            "system_boot_time": psutil.boot_time(),
            "process_start_time": time.time(),
            "initial_memory": psutil.virtual_memory().percent,
            "initial_cpu": psutil.cpu_percent()
        }
        
        context.system_metrics.update(startup_checks)
        logger.info(f"System startup health: {startup_checks}")
    
    async def _system_shutdown_health_check(self, context: HookContext):
        """Perform health check on system shutdown"""
        logger.info("Performing shutdown health check")
        
        shutdown_checks = {
            "shutdown_time": time.time(),
            "uptime_seconds": time.time() - psutil.boot_time(),
            "final_memory": psutil.virtual_memory().percent,
            "final_cpu": psutil.cpu_percent()
        }
        
        context.system_metrics.update(shutdown_checks)
        logger.info(f"System shutdown health: {shutdown_checks}")
    
    def get_current_health(self) -> Dict[str, Any]:
        """Get current health status"""
        if not self.health_history:
            return {"status": "unknown", "message": "No health checks performed yet"}
        
        latest_health = self.health_history[-1]
        return {
            "status": latest_health["overall_status"],
            "timestamp": latest_health["timestamp"],
            "components": latest_health["components"],
            "checks_performed": len(self.health_history)
        }
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check history"""
        cutoff_time = time.time() - (hours * 3600)
        return [h for h in self.health_history if h["timestamp"] > cutoff_time]
    
    def is_healthy(self) -> bool:
        """Check if system is currently healthy"""
        return self.current_health_status == "healthy"