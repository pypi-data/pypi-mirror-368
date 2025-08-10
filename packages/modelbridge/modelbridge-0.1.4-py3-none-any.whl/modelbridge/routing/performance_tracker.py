"""
Performance Tracking System for ModelBridge
Comprehensive performance monitoring and analytics
"""
import time
import json
import asyncio
import logging
import statistics
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric record"""
    timestamp: float
    provider_name: str
    model_id: str
    request_id: str
    
    # Timing metrics
    response_time: float
    queue_time: float = 0.0
    processing_time: float = 0.0
    
    # Cost metrics
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    
    # Quality metrics
    success: bool = True
    error_type: Optional[str] = None
    quality_score: Optional[float] = None
    
    # Request characteristics
    request_size: int = 0
    response_size: int = 0
    task_type: str = "general"
    complexity: str = "medium"
    
    # System metrics
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderPerformanceProfile:
    """Performance profile for a provider"""
    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Timing statistics
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    avg_response_time: float = 0.0
    median_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Cost statistics
    total_cost: float = 0.0
    avg_cost_per_request: float = 0.0
    avg_cost_per_token: float = 0.0
    
    # Quality statistics
    avg_quality_score: float = 0.0
    success_rate: float = 0.0
    
    # Error analysis
    error_breakdown: Dict[str, int] = field(default_factory=dict)
    
    # Performance trends
    hourly_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)
    daily_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Task-specific performance
    task_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    last_updated: float = field(default_factory=time.time)
    
    # Recent metrics for trend analysis
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_costs: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_quality_scores: deque = field(default_factory=lambda: deque(maxlen=100))


class PerformanceTracker:
    """Advanced performance tracking and analytics system"""
    
    def __init__(self, max_metrics_per_provider: int = 10000):
        self.max_metrics_per_provider = max_metrics_per_provider
        self.provider_profiles: Dict[str, ProviderPerformanceProfile] = {}
        self.raw_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_provider))
        
        # Real-time performance monitoring
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.performance_alerts: List[Dict[str, Any]] = []
        
        # Thresholds for alerts
        self.alert_thresholds = {
            "response_time": 10.0,      # seconds
            "error_rate": 0.1,          # 10% error rate
            "cost_spike": 2.0,          # 2x normal cost
            "quality_drop": 0.2         # 20% quality drop
        }
        
        # Background tasks
        self._analysis_tasks: List[asyncio.Task] = []
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background analysis tasks"""
        try:
            # Only start if we have an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._analysis_tasks.append(
                    asyncio.create_task(self._periodic_analysis())
                )
                self._analysis_tasks.append(
                    asyncio.create_task(self._performance_monitoring())
                )
        except RuntimeError:
            # No event loop available, skip background tasks
            logger.info("No event loop available for background tasks")
    
    async def record_request_start(self, request_id: str, provider_name: str, model_id: str, request_data: Dict[str, Any]) -> str:
        """Record start of a request"""
        start_time = time.time()
        
        self.active_requests[request_id] = {
            "provider_name": provider_name,
            "model_id": model_id,
            "start_time": start_time,
            "request_data": request_data,
            "task_type": request_data.get("task_type", "general"),
            "complexity": request_data.get("complexity", "medium")
        }
        
        logger.debug(f"Started tracking request {request_id} for {provider_name}")
        return request_id
    
    async def record_request_completion(
        self, 
        request_id: str, 
        success: bool = True,
        response_data: Optional[Dict[str, Any]] = None,
        error_type: Optional[str] = None,
        quality_score: Optional[float] = None
    ) -> PerformanceMetric:
        """Record completion of a request"""
        
        end_time = time.time()
        
        if request_id not in self.active_requests:
            logger.warning(f"Request {request_id} not found in active requests")
            return None
        
        request_info = self.active_requests.pop(request_id)
        start_time = request_info["start_time"]
        response_time = end_time - start_time
        
        # Extract metrics from response data
        response_data = response_data or {}
        
        metric = PerformanceMetric(
            timestamp=end_time,
            provider_name=request_info["provider_name"],
            model_id=request_info["model_id"],
            request_id=request_id,
            response_time=response_time,
            input_tokens=response_data.get("input_tokens", 0),
            output_tokens=response_data.get("output_tokens", 0),
            total_tokens=response_data.get("total_tokens", 0),
            cost=response_data.get("cost", 0.0),
            success=success,
            error_type=error_type,
            quality_score=quality_score,
            request_size=len(str(request_info.get("request_data", {}))),
            response_size=response_data.get("response_size", 0),
            task_type=request_info.get("task_type", "general"),
            complexity=request_info.get("complexity", "medium")
        )
        
        # Store the metric
        await self._store_metric(metric)
        
        # Update provider profile
        await self._update_provider_profile(metric)
        
        # Check for alerts
        await self._check_performance_alerts(metric)
        
        logger.debug(f"Recorded completion for request {request_id}: {response_time:.3f}s, success={success}")
        
        return metric
    
    async def _store_metric(self, metric: PerformanceMetric):
        """Store performance metric"""
        provider_name = metric.provider_name
        self.raw_metrics[provider_name].append(metric)
        
        # Could be extended to persist to database/file
        logger.debug(f"Stored metric for {provider_name}: {metric.response_time:.3f}s")
    
    async def _update_provider_profile(self, metric: PerformanceMetric):
        """Update provider performance profile"""
        provider_name = metric.provider_name
        
        if provider_name not in self.provider_profiles:
            self.provider_profiles[provider_name] = ProviderPerformanceProfile(
                provider_name=provider_name
            )
        
        profile = self.provider_profiles[provider_name]
        
        # Update counters
        profile.total_requests += 1
        if metric.success:
            profile.successful_requests += 1
        else:
            profile.failed_requests += 1
            if metric.error_type:
                profile.error_breakdown[metric.error_type] = profile.error_breakdown.get(metric.error_type, 0) + 1
        
        # Update timing statistics
        profile.recent_response_times.append(metric.response_time)
        if metric.response_time < profile.min_response_time:
            profile.min_response_time = metric.response_time
        if metric.response_time > profile.max_response_time:
            profile.max_response_time = metric.response_time
        
        # Recalculate timing statistics from recent data
        if profile.recent_response_times:
            response_times = list(profile.recent_response_times)
            profile.avg_response_time = statistics.mean(response_times)
            profile.median_response_time = statistics.median(response_times)
            
            if len(response_times) >= 20:  # Need sufficient data for percentiles
                sorted_times = sorted(response_times)
                profile.p95_response_time = sorted_times[int(0.95 * len(sorted_times))]
                profile.p99_response_time = sorted_times[int(0.99 * len(sorted_times))]
        
        # Update cost statistics
        profile.total_cost += metric.cost
        profile.recent_costs.append(metric.cost)
        if profile.total_requests > 0:
            profile.avg_cost_per_request = profile.total_cost / profile.total_requests
        
        if metric.total_tokens > 0:
            profile.avg_cost_per_token = metric.cost / metric.total_tokens
        
        # Update quality statistics
        if metric.quality_score is not None:
            profile.recent_quality_scores.append(metric.quality_score)
            if profile.recent_quality_scores:
                profile.avg_quality_score = statistics.mean(profile.recent_quality_scores)
        
        # Update success rate
        profile.success_rate = profile.successful_requests / profile.total_requests
        
        # Update task-specific performance
        task_type = metric.task_type
        if task_type not in profile.task_performance:
            profile.task_performance[task_type] = {
                "total_requests": 0,
                "avg_response_time": 0.0,
                "avg_cost": 0.0,
                "success_rate": 0.0,
                "response_times": deque(maxlen=50)
            }
        
        task_perf = profile.task_performance[task_type]
        task_perf["total_requests"] += 1
        task_perf["response_times"].append(metric.response_time)
        
        if task_perf["response_times"]:
            task_perf["avg_response_time"] = statistics.mean(task_perf["response_times"])
        
        # Update time-based statistics
        await self._update_time_based_stats(profile, metric)
        
        profile.last_updated = time.time()
    
    async def _update_time_based_stats(self, profile: ProviderPerformanceProfile, metric: PerformanceMetric):
        """Update hourly and daily statistics"""
        timestamp = metric.timestamp
        dt = datetime.fromtimestamp(timestamp)
        
        # Hourly stats
        hour_key = dt.strftime("%Y-%m-%d-%H")
        if hour_key not in profile.hourly_stats:
            profile.hourly_stats[hour_key] = {
                "requests": 0,
                "total_response_time": 0.0,
                "total_cost": 0.0,
                "errors": 0
            }
        
        hour_stats = profile.hourly_stats[hour_key]
        hour_stats["requests"] += 1
        hour_stats["total_response_time"] += metric.response_time
        hour_stats["total_cost"] += metric.cost
        if not metric.success:
            hour_stats["errors"] += 1
        
        # Daily stats  
        day_key = dt.strftime("%Y-%m-%d")
        if day_key not in profile.daily_stats:
            profile.daily_stats[day_key] = {
                "requests": 0,
                "total_response_time": 0.0,
                "total_cost": 0.0,
                "errors": 0
            }
        
        day_stats = profile.daily_stats[day_key]
        day_stats["requests"] += 1
        day_stats["total_response_time"] += metric.response_time
        day_stats["total_cost"] += metric.cost
        if not metric.success:
            day_stats["errors"] += 1
        
        # Cleanup old stats (keep last 30 days)
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        profile.daily_stats = {k: v for k, v in profile.daily_stats.items() if k >= cutoff_date}
        
        # Cleanup old hourly stats (keep last 7 days)
        cutoff_hour = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d-%H")
        profile.hourly_stats = {k: v for k, v in profile.hourly_stats.items() if k >= cutoff_hour}
    
    async def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance issues and generate alerts"""
        provider_name = metric.provider_name
        
        alerts = []
        
        # Response time alert
        if metric.response_time > self.alert_thresholds["response_time"]:
            alerts.append({
                "type": "high_response_time",
                "provider": provider_name,
                "value": metric.response_time,
                "threshold": self.alert_thresholds["response_time"],
                "timestamp": metric.timestamp
            })
        
        # Cost spike alert
        if provider_name in self.provider_profiles:
            profile = self.provider_profiles[provider_name]
            if profile.avg_cost_per_request > 0:
                cost_ratio = metric.cost / profile.avg_cost_per_request
                if cost_ratio > self.alert_thresholds["cost_spike"]:
                    alerts.append({
                        "type": "cost_spike", 
                        "provider": provider_name,
                        "value": cost_ratio,
                        "threshold": self.alert_thresholds["cost_spike"],
                        "timestamp": metric.timestamp
                    })
        
        # Error rate alert
        if not metric.success and provider_name in self.provider_profiles:
            profile = self.provider_profiles[provider_name]
            if profile.success_rate < (1 - self.alert_thresholds["error_rate"]):
                alerts.append({
                    "type": "high_error_rate",
                    "provider": provider_name,
                    "value": 1 - profile.success_rate,
                    "threshold": self.alert_thresholds["error_rate"],
                    "timestamp": metric.timestamp
                })
        
        # Add alerts to queue
        for alert in alerts:
            self.performance_alerts.append(alert)
            logger.warning(f"Performance alert: {alert}")
        
        # Keep only recent alerts (last 1000)
        self.performance_alerts = self.performance_alerts[-1000:]
    
    async def _periodic_analysis(self):
        """Periodic performance analysis background task"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._run_performance_analysis()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic analysis: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _performance_monitoring(self):
        """Real-time performance monitoring background task"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                await self._monitor_active_requests()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _run_performance_analysis(self):
        """Run comprehensive performance analysis"""
        logger.debug("Running performance analysis...")
        
        for provider_name, profile in self.provider_profiles.items():
            # Analyze performance trends
            await self._analyze_trends(provider_name, profile)
            
            # Check for anomalies
            await self._detect_anomalies(provider_name, profile)
        
        logger.debug("Performance analysis completed")
    
    async def _analyze_trends(self, provider_name: str, profile: ProviderPerformanceProfile):
        """Analyze performance trends for a provider"""
        # This is a simplified trend analysis
        # Could be enhanced with more sophisticated statistical methods
        
        if len(profile.recent_response_times) < 20:
            return  # Need sufficient data
        
        response_times = list(profile.recent_response_times)
        recent_half = response_times[-10:]
        older_half = response_times[-20:-10]
        
        recent_avg = statistics.mean(recent_half)
        older_avg = statistics.mean(older_half)
        
        # Detect significant changes
        if recent_avg > older_avg * 1.5:
            logger.warning(f"{provider_name}: Response time increased significantly")
        elif recent_avg < older_avg * 0.7:
            logger.info(f"{provider_name}: Response time improved significantly")
    
    async def _detect_anomalies(self, provider_name: str, profile: ProviderPerformanceProfile):
        """Detect performance anomalies"""
        if len(profile.recent_response_times) < 10:
            return
        
        response_times = list(profile.recent_response_times)
        mean_time = statistics.mean(response_times)
        
        try:
            stdev = statistics.stdev(response_times)
            
            # Check for outliers (values > 2 standard deviations from mean)
            outliers = [t for t in response_times if abs(t - mean_time) > 2 * stdev]
            if len(outliers) / len(response_times) > 0.1:  # More than 10% outliers
                logger.warning(f"{provider_name}: High number of response time outliers detected")
        except statistics.StatisticsError:
            # Not enough data for standard deviation
            pass
    
    async def _monitor_active_requests(self):
        """Monitor active requests for timeouts"""
        current_time = time.time()
        timeout_threshold = 60.0  # 60 seconds
        
        timed_out_requests = []
        
        for request_id, request_info in self.active_requests.items():
            request_age = current_time - request_info["start_time"]
            if request_age > timeout_threshold:
                timed_out_requests.append(request_id)
        
        # Clean up timed out requests
        for request_id in timed_out_requests:
            request_info = self.active_requests.pop(request_id, {})
            logger.warning(f"Request {request_id} timed out after {timeout_threshold}s")
            
            # Record as failed request
            if request_info:
                await self.record_request_completion(
                    request_id, 
                    success=False, 
                    error_type="timeout"
                )
    
    def get_performance_summary(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary"""
        if provider_name:
            if provider_name not in self.provider_profiles:
                return {"error": f"No performance data for provider {provider_name}"}
            
            profile = self.provider_profiles[provider_name]
            return {
                "provider_name": provider_name,
                "total_requests": profile.total_requests,
                "success_rate": profile.success_rate,
                "avg_response_time": profile.avg_response_time,
                "p95_response_time": profile.p95_response_time,
                "avg_cost_per_request": profile.avg_cost_per_request,
                "avg_quality_score": profile.avg_quality_score,
                "error_breakdown": profile.error_breakdown,
                "task_performance": profile.task_performance,
                "last_updated": profile.last_updated
            }
        else:
            return {
                provider_name: {
                    "total_requests": profile.total_requests,
                    "success_rate": profile.success_rate,
                    "avg_response_time": profile.avg_response_time,
                    "avg_cost_per_request": profile.avg_cost_per_request
                }
                for provider_name, profile in self.provider_profiles.items()
            }
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        return self.performance_alerts[-limit:]
    
    def export_metrics(self, provider_name: str, format: str = "json") -> str:
        """Export metrics for a provider"""
        if provider_name not in self.raw_metrics:
            return "{}" if format == "json" else ""
        
        metrics = list(self.raw_metrics[provider_name])
        
        if format == "json":
            return json.dumps([asdict(metric) for metric in metrics], indent=2)
        elif format == "csv":
            # Simple CSV export
            if not metrics:
                return ""
            
            headers = list(asdict(metrics[0]).keys())
            lines = [",".join(headers)]
            
            for metric in metrics:
                values = [str(v) for v in asdict(metric).values()]
                lines.append(",".join(values))
            
            return "\n".join(lines)
        else:
            return str(metrics)
    
    def cleanup(self):
        """Cleanup background tasks"""
        for task in self._analysis_tasks:
            task.cancel()
        self._analysis_tasks.clear()