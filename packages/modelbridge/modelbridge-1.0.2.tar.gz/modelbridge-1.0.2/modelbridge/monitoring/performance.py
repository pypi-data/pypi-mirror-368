"""
Performance monitoring and analysis system
"""
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque, defaultdict
import statistics
import logging

from .metrics import MetricsCollector
from .health import HealthChecker

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a component"""
    component: str
    timestamp: datetime
    
    # Latency metrics
    avg_latency: float = 0.0
    p50_latency: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    min_latency: float = 0.0
    max_latency: float = 0.0
    
    # Throughput metrics
    requests_per_second: float = 0.0
    total_requests: int = 0
    
    # Error metrics
    error_rate: float = 0.0
    total_errors: int = 0
    
    # Resource metrics
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    
    # Cost metrics
    avg_cost_per_request: float = 0.0
    total_cost: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "component": self.component,
            "timestamp": self.timestamp.isoformat(),
            "latency": {
                "avg": self.avg_latency,
                "p50": self.p50_latency,
                "p95": self.p95_latency,
                "p99": self.p99_latency,
                "min": self.min_latency,
                "max": self.max_latency
            },
            "throughput": {
                "requests_per_second": self.requests_per_second,
                "total_requests": self.total_requests
            },
            "errors": {
                "error_rate": self.error_rate,
                "total_errors": self.total_errors
            },
            "resources": {
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage
            },
            "costs": {
                "avg_cost_per_request": self.avg_cost_per_request,
                "total_cost": self.total_cost
            }
        }


@dataclass
class ProviderPerformance:
    """Provider-specific performance data"""
    provider_name: str
    model_name: str
    
    # Request tracking
    request_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    success_count: int = 0
    error_count: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    
    # Time windows for rate calculations
    window_size: int = 300  # 5 minutes
    request_timestamps: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_request(self, duration: float, success: bool, cost: float = 0.0, tokens: int = 0):
        """Add a request result"""
        now = time.time()
        
        self.request_times.append(duration)
        self.request_timestamps.append(now)
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        self.total_cost += cost
        self.total_tokens += tokens
    
    def get_metrics(self) -> PerformanceMetrics:
        """Calculate current performance metrics"""
        now = time.time()
        window_start = now - self.window_size
        
        # Filter recent requests for rate calculations
        recent_requests = [ts for ts in self.request_timestamps if ts >= window_start]
        recent_times = list(self.request_times)[-len(recent_requests):]
        
        # Calculate latency metrics
        if recent_times:
            sorted_times = sorted(recent_times)
            avg_latency = statistics.mean(sorted_times)
            p50_latency = statistics.median(sorted_times)
            p95_latency = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
            p99_latency = sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0
            min_latency = min(sorted_times)
            max_latency = max(sorted_times)
        else:
            avg_latency = p50_latency = p95_latency = p99_latency = min_latency = max_latency = 0.0
        
        # Calculate throughput
        requests_per_second = len(recent_requests) / self.window_size if recent_requests else 0.0
        
        # Calculate error rate
        total_requests = self.success_count + self.error_count
        error_rate = self.error_count / total_requests if total_requests > 0 else 0.0
        
        # Calculate cost metrics
        avg_cost_per_request = self.total_cost / total_requests if total_requests > 0 else 0.0
        
        return PerformanceMetrics(
            component=f"{self.provider_name}:{self.model_name}",
            timestamp=datetime.utcnow(),
            avg_latency=avg_latency,
            p50_latency=p50_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            min_latency=min_latency,
            max_latency=max_latency,
            requests_per_second=requests_per_second,
            total_requests=total_requests,
            error_rate=error_rate,
            total_errors=self.error_count,
            avg_cost_per_request=avg_cost_per_request,
            total_cost=self.total_cost
        )


class PerformanceMonitor:
    """Performance monitoring system for ModelBridge"""
    
    def __init__(self, 
                 metrics_collector: Optional[MetricsCollector] = None,
                 health_checker: Optional[HealthChecker] = None,
                 history_size: int = 1000):
        self.metrics_collector = metrics_collector
        self.health_checker = health_checker
        self.history_size = history_size
        
        # Performance tracking
        self.provider_performance: Dict[str, ProviderPerformance] = {}
        self.system_metrics_history: deque = deque(maxlen=history_size)
        
        # Analysis results
        self.performance_analysis: Dict[str, Any] = {}
        self.recommendations: List[str] = []
        
        # Monitoring settings
        self.monitoring_interval = 60  # seconds
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
    
    def register_provider(self, provider_name: str, model_name: str = "default"):
        """Register a provider for performance monitoring"""
        key = f"{provider_name}:{model_name}"
        if key not in self.provider_performance:
            self.provider_performance[key] = ProviderPerformance(provider_name, model_name)
            logger.info(f"Registered performance monitoring for {key}")
    
    def record_request(self, 
                      provider_name: str,
                      model_name: str,
                      duration: float,
                      success: bool,
                      cost: float = 0.0,
                      tokens: int = 0,
                      error_type: Optional[str] = None):
        """Record a request for performance analysis"""
        key = f"{provider_name}:{model_name}"
        
        if key not in self.provider_performance:
            self.register_provider(provider_name, model_name)
        
        self.provider_performance[key].add_request(duration, success, cost, tokens)
        
        # Also record in metrics collector if available
        if self.metrics_collector:
            labels = {"provider": provider_name, "model": model_name}
            self.metrics_collector.record_request_complete(
                request_id="",
                provider=provider_name,
                model=model_name,
                method="generate_text",
                duration=duration,
                success=success,
                error_type=error_type,
                cost=cost,
                tokens_used=tokens
            )
    
    def get_provider_performance(self, provider_name: str, model_name: str = "default") -> Optional[PerformanceMetrics]:
        """Get performance metrics for a specific provider"""
        key = f"{provider_name}:{model_name}"
        if key in self.provider_performance:
            return self.provider_performance[key].get_metrics()
        return None
    
    def get_all_performance_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get performance metrics for all providers"""
        return {
            key: perf.get_metrics()
            for key, perf in self.provider_performance.items()
        }
    
    def get_system_performance(self) -> PerformanceMetrics:
        """Get overall system performance metrics"""
        all_metrics = self.get_all_performance_metrics()
        
        if not all_metrics:
            return PerformanceMetrics(
                component="system",
                timestamp=datetime.utcnow()
            )
        
        # Aggregate metrics across all providers
        total_requests = sum(m.total_requests for m in all_metrics.values())
        total_errors = sum(m.total_errors for m in all_metrics.values())
        total_cost = sum(m.total_cost for m in all_metrics.values())
        
        # Weighted averages
        if total_requests > 0:
            avg_latency = sum(m.avg_latency * m.total_requests for m in all_metrics.values()) / total_requests
            avg_cost_per_request = total_cost / total_requests
            error_rate = total_errors / total_requests
        else:
            avg_latency = avg_cost_per_request = error_rate = 0.0
        
        # Calculate system RPS
        requests_per_second = sum(m.requests_per_second for m in all_metrics.values())
        
        # Get latency percentiles from all request times
        all_latencies = []
        for perf in self.provider_performance.values():
            all_latencies.extend(list(perf.request_times))
        
        if all_latencies:
            sorted_latencies = sorted(all_latencies)
            p50_latency = statistics.median(sorted_latencies)
            p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]
            min_latency = min(sorted_latencies)
            max_latency = max(sorted_latencies)
        else:
            p50_latency = p95_latency = p99_latency = min_latency = max_latency = 0.0
        
        return PerformanceMetrics(
            component="system",
            timestamp=datetime.utcnow(),
            avg_latency=avg_latency,
            p50_latency=p50_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            min_latency=min_latency,
            max_latency=max_latency,
            requests_per_second=requests_per_second,
            total_requests=total_requests,
            error_rate=error_rate,
            total_errors=total_errors,
            avg_cost_per_request=avg_cost_per_request,
            total_cost=total_cost
        )
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance and generate insights"""
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider_rankings": self._rank_providers(),
            "performance_trends": self._analyze_trends(),
            "bottlenecks": self._identify_bottlenecks(),
            "recommendations": self._generate_recommendations(),
            "cost_analysis": self._analyze_costs()
        }
        
        self.performance_analysis = analysis
        return analysis
    
    def _rank_providers(self) -> List[Dict[str, Any]]:
        """Rank providers by performance"""
        provider_metrics = self.get_all_performance_metrics()
        
        rankings = []
        for key, metrics in provider_metrics.items():
            provider_name, model_name = key.split(":", 1)
            
            # Calculate performance score (lower is better)
            latency_score = metrics.avg_latency * 1000  # Convert to ms
            error_score = metrics.error_rate * 1000
            cost_score = metrics.avg_cost_per_request * 100
            
            # Weighted performance score
            performance_score = (
                latency_score * 0.4 +   # 40% latency
                error_score * 0.4 +     # 40% reliability  
                cost_score * 0.2        # 20% cost
            )
            
            rankings.append({
                "provider": provider_name,
                "model": model_name,
                "performance_score": performance_score,
                "avg_latency_ms": latency_score,
                "error_rate": metrics.error_rate,
                "avg_cost": metrics.avg_cost_per_request,
                "requests_per_second": metrics.requests_per_second,
                "total_requests": metrics.total_requests
            })
        
        # Sort by performance score (lower is better)
        rankings.sort(key=lambda x: x["performance_score"])
        return rankings
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze performance trends"""
        trends = {
            "latency_trend": "stable",
            "error_rate_trend": "stable", 
            "cost_trend": "stable",
            "throughput_trend": "stable"
        }
        
        # This would analyze historical data to determine trends
        # For now, return placeholder data
        if len(self.system_metrics_history) > 10:
            recent_metrics = list(self.system_metrics_history)[-10:]
            # Analyze trends in recent metrics
            # Implementation would compare recent vs historical averages
            pass
        
        return trends
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        system_metrics = self.get_system_performance()
        
        # High latency bottleneck
        if system_metrics.avg_latency > 2.0:  # 2 seconds
            bottlenecks.append({
                "type": "high_latency",
                "severity": "high" if system_metrics.avg_latency > 5.0 else "medium",
                "description": f"Average latency is {system_metrics.avg_latency:.2f}s",
                "recommendation": "Consider using faster providers or implementing request optimization"
            })
        
        # High error rate bottleneck  
        if system_metrics.error_rate > 0.05:  # 5%
            bottlenecks.append({
                "type": "high_error_rate",
                "severity": "high" if system_metrics.error_rate > 0.1 else "medium",
                "description": f"Error rate is {system_metrics.error_rate:.2%}",
                "recommendation": "Investigate provider reliability and implement better error handling"
            })
        
        # High cost bottleneck
        if system_metrics.avg_cost_per_request > 0.1:  # $0.10 per request
            bottlenecks.append({
                "type": "high_cost",
                "severity": "medium",
                "description": f"Average cost per request is ${system_metrics.avg_cost_per_request:.4f}",
                "recommendation": "Consider using cheaper providers for appropriate use cases"
            })
        
        # Provider-specific bottlenecks
        for key, perf in self.provider_performance.items():
            metrics = perf.get_metrics()
            provider_name, model_name = key.split(":", 1)
            
            if metrics.error_rate > 0.1:  # 10% error rate for specific provider
                bottlenecks.append({
                    "type": "provider_reliability",
                    "provider": provider_name,
                    "model": model_name,
                    "severity": "high",
                    "description": f"Provider {provider_name} has {metrics.error_rate:.2%} error rate",
                    "recommendation": f"Consider reducing traffic to {provider_name} or investigating issues"
                })
        
        return bottlenecks
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        provider_rankings = self._rank_providers()
        system_metrics = self.get_system_performance()
        
        # Recommendation based on provider performance
        if len(provider_rankings) > 1:
            best_provider = provider_rankings[0]
            worst_provider = provider_rankings[-1]
            
            if best_provider["performance_score"] * 2 < worst_provider["performance_score"]:
                recommendations.append(
                    f"Consider routing more traffic to {best_provider['provider']} "
                    f"({best_provider['model']}) and less to {worst_provider['provider']} "
                    f"({worst_provider['model']}) for better performance"
                )
        
        # Latency recommendations
        if system_metrics.avg_latency > 3.0:
            recommendations.append(
                "System latency is high. Consider implementing request caching, "
                "using faster providers, or optimizing request sizes"
            )
        
        # Error rate recommendations
        if system_metrics.error_rate > 0.05:
            recommendations.append(
                "Error rate is elevated. Implement better retry logic, "
                "health checks, and failover mechanisms"
            )
        
        # Cost recommendations
        if system_metrics.avg_cost_per_request > 0.05:
            recommendations.append(
                "Cost per request is high. Consider using cheaper providers "
                "for simpler tasks and reserving expensive providers for complex requests"
            )
        
        # Throughput recommendations
        if system_metrics.requests_per_second > 0:
            for provider_ranking in provider_rankings:
                if provider_ranking["requests_per_second"] < 1.0 and provider_ranking["total_requests"] > 10:
                    recommendations.append(
                        f"Provider {provider_ranking['provider']} has low throughput. "
                        f"Consider scaling up or investigating performance issues"
                    )
        
        self.recommendations = recommendations
        return recommendations
    
    def _analyze_costs(self) -> Dict[str, Any]:
        """Analyze cost patterns"""
        provider_metrics = self.get_all_performance_metrics()
        system_metrics = self.get_system_performance()
        
        provider_costs = {}
        for key, metrics in provider_metrics.items():
            provider_name, model_name = key.split(":", 1)
            provider_costs[provider_name] = {
                "total_cost": metrics.total_cost,
                "avg_cost_per_request": metrics.avg_cost_per_request,
                "requests": metrics.total_requests,
                "cost_per_second": metrics.avg_cost_per_request * metrics.requests_per_second
            }
        
        # Find most/least expensive providers
        if provider_costs:
            most_expensive = max(provider_costs.items(), key=lambda x: x[1]["avg_cost_per_request"])
            least_expensive = min(provider_costs.items(), key=lambda x: x[1]["avg_cost_per_request"])
        else:
            most_expensive = least_expensive = None
        
        return {
            "system_total_cost": system_metrics.total_cost,
            "system_avg_cost_per_request": system_metrics.avg_cost_per_request,
            "provider_costs": provider_costs,
            "most_expensive_provider": most_expensive[0] if most_expensive else None,
            "least_expensive_provider": least_expensive[0] if least_expensive else None,
            "cost_efficiency_ratio": (
                system_metrics.requests_per_second / system_metrics.avg_cost_per_request
                if system_metrics.avg_cost_per_request > 0 else 0
            )
        }
    
    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started performance monitoring (interval: {self.monitoring_interval}s)")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        
        logger.info("Stopped performance monitoring")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self._running:
            try:
                # Collect current metrics
                system_metrics = self.get_system_performance()
                self.system_metrics_history.append(system_metrics)
                
                # Run performance analysis
                self.analyze_performance()
                
                # Log performance summary
                logger.debug(
                    f"Performance: {system_metrics.requests_per_second:.1f} RPS, "
                    f"{system_metrics.avg_latency:.3f}s avg latency, "
                    f"{system_metrics.error_rate:.2%} error rate, "
                    f"${system_metrics.avg_cost_per_request:.4f} avg cost"
                )
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_performance": self.get_system_performance().to_dict(),
            "provider_performance": {
                key: metrics.to_dict()
                for key, metrics in self.get_all_performance_metrics().items()
            },
            "analysis": self.performance_analysis,
            "recommendations": self.recommendations
        }