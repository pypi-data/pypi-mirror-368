"""
Core metrics collection and tracking system
"""
import time
import threading
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp,
            "labels": self.labels
        }
    
    def to_prometheus(self) -> str:
        """Convert to Prometheus format"""
        label_str = ""
        if self.labels:
            label_pairs = [f'{k}="{v}"' for k, v in self.labels.items()]
            label_str = "{" + ",".join(label_pairs) + "}"
        
        return f"{self.name}{label_str} {self.value} {int(self.timestamp * 1000)}"


@dataclass
class HistogramBucket:
    """Histogram bucket for latency tracking"""
    upper_bound: float
    count: int = 0


class MetricsRegistry:
    """Thread-safe metrics registry"""
    
    def __init__(self):
        self._metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[HistogramBucket]] = {}
        self._timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.RLock()
        
        # Standard histogram buckets (in seconds)
        self._default_buckets = [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        labels = labels or {}
        key = self._make_key(name, labels)
        
        with self._lock:
            self._counters[key] += value
            metric = Metric(name, self._counters[key], MetricType.COUNTER, labels=labels)
            self._metrics[name].append(metric)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        labels = labels or {}
        key = self._make_key(name, labels)
        
        with self._lock:
            self._gauges[key] = value
            metric = Metric(name, value, MetricType.GAUGE, labels=labels)
            self._metrics[name].append(metric)
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a value for histogram metric"""
        labels = labels or {}
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = [HistogramBucket(bound) for bound in self._default_buckets]
                # Add +Inf bucket
                self._histograms[key].append(HistogramBucket(float('inf')))
            
            # Update buckets
            for bucket in self._histograms[key]:
                if value <= bucket.upper_bound:
                    bucket.count += 1
            
            metric = Metric(name, value, MetricType.HISTOGRAM, labels=labels)
            self._metrics[name].append(metric)
    
    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """Record a timer measurement"""
        labels = labels or {}
        key = self._make_key(name, labels)
        
        with self._lock:
            self._timers[key].append(duration)
            metric = Metric(name, duration, MetricType.TIMER, labels=labels)
            self._metrics[name].append(metric)
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value"""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._counters.get(key, 0.0)
    
    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get current gauge value"""
        key = self._make_key(name, labels or {})
        with self._lock:
            return self._gauges.get(key)
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get histogram statistics"""
        key = self._make_key(name, labels or {})
        with self._lock:
            if key not in self._histograms:
                return {}
            
            buckets = self._histograms[key]
            total_count = buckets[-1].count if buckets else 0
            
            return {
                "count": total_count,
                "buckets": [(b.upper_bound, b.count) for b in buckets],
            }
    
    def get_timer_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics"""
        key = self._make_key(name, labels or {})
        with self._lock:
            if key not in self._timers or not self._timers[key]:
                return {}
            
            values = list(self._timers[key])
            values.sort()
            
            count = len(values)
            if count == 0:
                return {}
            
            return {
                "count": count,
                "min": values[0],
                "max": values[-1],
                "mean": sum(values) / count,
                "median": values[count // 2],
                "p95": values[int(count * 0.95)] if count > 0 else 0,
                "p99": values[int(count * 0.99)] if count > 0 else 0,
            }
    
    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all recorded metrics"""
        with self._lock:
            return {
                name: [metric.to_dict() for metric in metrics]
                for name, metrics in self._metrics.items()
            }
    
    def get_current_values(self) -> Dict[str, Any]:
        """Get current metric values"""
        with self._lock:
            result = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {k: self.get_histogram_stats("", {"key": k}) for k in self._histograms.keys()},
                "timers": {k: self.get_timer_stats("", {"key": k}) for k in self._timers.keys()}
            }
            return result
    
    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        timestamp = int(time.time() * 1000)
        
        with self._lock:
            # Counters
            for key, value in self._counters.items():
                name, labels = self._parse_key(key)
                label_str = self._labels_to_string(labels)
                lines.append(f"{name}_total{label_str} {value} {timestamp}")
            
            # Gauges  
            for key, value in self._gauges.items():
                name, labels = self._parse_key(key)
                label_str = self._labels_to_string(labels)
                lines.append(f"{name}{label_str} {value} {timestamp}")
            
            # Histograms
            for key, buckets in self._histograms.items():
                name, labels = self._parse_key(key)
                for bucket in buckets:
                    le_labels = {**labels, "le": str(bucket.upper_bound)}
                    label_str = self._labels_to_string(le_labels)
                    lines.append(f"{name}_bucket{label_str} {bucket.count} {timestamp}")
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear all metrics"""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()
    
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """Make a unique key from name and labels"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"
    
    def _parse_key(self, key: str) -> tuple[str, Dict[str, str]]:
        """Parse key back to name and labels"""
        if "[" not in key:
            return key, {}
        
        name, label_part = key.split("[", 1)
        label_part = label_part.rstrip("]")
        
        labels = {}
        if label_part:
            for pair in label_part.split(","):
                k, v = pair.split("=", 1)
                labels[k] = v
        
        return name, labels
    
    def _labels_to_string(self, labels: Dict[str, str]) -> str:
        """Convert labels to Prometheus string format"""
        if not labels:
            return ""
        
        label_pairs = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(label_pairs) + "}"


class MetricsCollector:
    """High-level metrics collector for ModelBridge"""
    
    def __init__(self, registry: Optional[MetricsRegistry] = None):
        self.registry = registry or MetricsRegistry()
        self.start_time = time.time()
        
        # Initialize core metrics
        self._initialize_core_metrics()
    
    def _initialize_core_metrics(self):
        """Initialize core ModelBridge metrics"""
        # System metrics
        self.registry.set_gauge("modelbridge_start_time", self.start_time)
        self.registry.increment_counter("modelbridge_requests_total", 0)
        self.registry.set_gauge("modelbridge_active_requests", 0)
        
        # Provider metrics  
        self.registry.increment_counter("modelbridge_provider_requests_total", 0)
        self.registry.increment_counter("modelbridge_provider_errors_total", 0)
        
        # Cost metrics
        self.registry.set_gauge("modelbridge_total_cost", 0.0)
        self.registry.set_gauge("modelbridge_cost_per_request", 0.0)
    
    def record_request_start(self, provider: str, model: str, method: str) -> str:
        """Record request start and return request ID for tracking"""
        request_id = f"{provider}_{model}_{int(time.time() * 1000000)}"
        
        labels = {"provider": provider, "model": model, "method": method}
        
        self.registry.increment_counter("modelbridge_requests_total", labels=labels)
        self.registry.set_gauge("modelbridge_active_requests", 
                               self.registry.get_gauge("modelbridge_active_requests", {}) + 1)
        
        return request_id
    
    def record_request_complete(self, 
                              request_id: str,
                              provider: str, 
                              model: str,
                              method: str,
                              duration: float,
                              success: bool,
                              error_type: Optional[str] = None,
                              cost: Optional[float] = None,
                              tokens_used: Optional[int] = None):
        """Record completed request metrics"""
        labels = {"provider": provider, "model": model, "method": method}
        
        # Update active requests
        current_active = self.registry.get_gauge("modelbridge_active_requests", {}) or 0
        self.registry.set_gauge("modelbridge_active_requests", max(0, current_active - 1))
        
        # Record latency
        self.registry.observe_histogram("modelbridge_request_duration_seconds", duration, labels)
        self.registry.record_timer("modelbridge_request_timer", duration, labels)
        
        # Record success/failure
        status_labels = {**labels, "status": "success" if success else "error"}
        self.registry.increment_counter("modelbridge_request_status_total", labels=status_labels)
        
        if not success and error_type:
            error_labels = {**labels, "error_type": error_type}
            self.registry.increment_counter("modelbridge_provider_errors_total", labels=error_labels)
        
        # Record cost if available
        if cost is not None:
            self.registry.observe_histogram("modelbridge_request_cost", cost, labels)
            
            # Update total cost
            current_total = self.registry.get_gauge("modelbridge_total_cost", {}) or 0.0
            self.registry.set_gauge("modelbridge_total_cost", current_total + cost)
            
            # Update average cost per request
            total_requests = self.registry.get_counter("modelbridge_requests_total", {})
            if total_requests > 0:
                avg_cost = (current_total + cost) / total_requests
                self.registry.set_gauge("modelbridge_cost_per_request", avg_cost)
        
        # Record tokens if available
        if tokens_used is not None:
            self.registry.observe_histogram("modelbridge_tokens_used", tokens_used, labels)
    
    def record_cache_hit(self, cache_type: str, method: str):
        """Record cache hit"""
        labels = {"cache_type": cache_type, "method": method}
        self.registry.increment_counter("modelbridge_cache_hits_total", labels=labels)
    
    def record_cache_miss(self, cache_type: str, method: str):
        """Record cache miss"""
        labels = {"cache_type": cache_type, "method": method}  
        self.registry.increment_counter("modelbridge_cache_misses_total", labels=labels)
    
    def record_rate_limit_hit(self, provider: str, limit_type: str):
        """Record rate limit hit"""
        labels = {"provider": provider, "limit_type": limit_type}
        self.registry.increment_counter("modelbridge_rate_limits_hit_total", labels=labels)
    
    def record_provider_health(self, provider: str, is_healthy: bool, response_time: Optional[float] = None):
        """Record provider health status"""
        labels = {"provider": provider}
        
        self.registry.set_gauge("modelbridge_provider_healthy", 
                               1.0 if is_healthy else 0.0, labels=labels)
        
        if response_time is not None:
            self.registry.observe_histogram("modelbridge_provider_health_check_duration", 
                                          response_time, labels)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        uptime = time.time() - self.start_time
        total_requests = self.registry.get_counter("modelbridge_requests_total", {})
        total_cost = self.registry.get_gauge("modelbridge_total_cost", {}) or 0.0
        active_requests = self.registry.get_gauge("modelbridge_active_requests", {}) or 0
        
        return {
            "uptime_seconds": uptime,
            "total_requests": total_requests,
            "active_requests": active_requests,
            "requests_per_second": total_requests / uptime if uptime > 0 else 0,
            "total_cost": total_cost,
            "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get per-provider statistics"""
        # This would analyze metrics by provider
        # Implementation depends on how we want to aggregate the data
        return {}


# Context manager for timing operations
class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, labels: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.metric_name = metric_name
        self.labels = labels or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.collector.registry.record_timer(self.metric_name, duration, self.labels)
            self.collector.registry.observe_histogram(f"{self.metric_name}_seconds", duration, self.labels)


def timed_operation(collector: MetricsCollector, metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator for timing function calls"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            with Timer(collector, metric_name, labels):
                return func(*args, **kwargs)
        return wrapper
    return decorator


async def async_timed_operation(collector: MetricsCollector, metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator for timing async function calls"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            with Timer(collector, metric_name, labels):
                return await func(*args, **kwargs)
        return wrapper
    return decorator