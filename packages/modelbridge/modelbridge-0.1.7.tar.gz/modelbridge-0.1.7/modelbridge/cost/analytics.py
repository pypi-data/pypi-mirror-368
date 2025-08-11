"""
Advanced cost analytics and reporting system with insights and predictions
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
import logging

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Comprehensive usage statistics"""
    total_requests: int
    total_cost: float
    total_tokens: int
    average_cost_per_request: float
    average_cost_per_token: float
    average_tokens_per_request: float
    cost_trend: str  # "increasing", "decreasing", "stable"
    top_models: List[Tuple[str, float]]  # (model, cost)
    top_tasks: List[Tuple[str, float]]   # (task_type, cost)
    peak_usage_hour: Optional[str]
    most_expensive_request: Optional[float]
    total_savings: float
    optimization_rate: float  # Percentage of requests optimized


@dataclass 
class CostReport:
    """Detailed cost analysis report"""
    period: str
    start_date: str
    end_date: str
    summary: UsageStats
    provider_breakdown: Dict[str, Dict[str, Any]]
    model_performance: Dict[str, Dict[str, Any]]
    cost_trends: List[Tuple[str, float]]
    recommendations: List[str]
    potential_savings: float
    efficiency_score: float  # 0-100 score
    generated_at: str


class CostAnalytics:
    """
    Production-grade cost analytics with advanced insights,
    predictions, and optimization recommendations
    """
    
    def __init__(self, cost_tracker=None, budget_manager=None):
        """
        Initialize cost analytics
        
        Args:
            cost_tracker: CostTracker instance for data
            budget_manager: BudgetManager instance for budget analysis
        """
        self.cost_tracker = cost_tracker
        self.budget_manager = budget_manager
        
        # Model efficiency baselines (cost per quality point)
        self.efficiency_baselines = {
            "gpt-5": 1.25 / 95,  # cost / quality_score
            "gpt-5-mini": 0.25 / 88,
            "gpt-5-nano": 0.05 / 75,
            "claude-opus-4-1": 15.0 / 97,
            "claude-sonnet-4": 3.0 / 90,
            "gemini-2.5-pro": 2.5 / 92,
            "gemini-2.5-flash": 0.075 / 82,
            "llama-3.3-70b-versatile": 0.59 / 85,
            "mixtral-8x7b-32768": 0.27 / 80,
        }
    
    def generate_usage_stats(self, time_period: str = "month") -> UsageStats:
        """Generate comprehensive usage statistics for specified period"""
        
        if not self.cost_tracker:
            return self._empty_usage_stats()
        
        # Get basic usage data
        usage_data = self.cost_tracker.get_current_usage(time_period)
        provider_breakdown = self.cost_tracker.get_provider_breakdown(time_period)
        
        total_requests = usage_data.get("total_requests", 0)
        total_cost = usage_data.get("total_cost", 0.0)
        total_tokens = usage_data.get("total_tokens", 0)
        total_savings = usage_data.get("total_saved", 0.0)
        
        # Calculate averages
        avg_cost_per_request = total_cost / max(total_requests, 1)
        avg_cost_per_token = total_cost / max(total_tokens, 1)
        avg_tokens_per_request = total_tokens / max(total_requests, 1)
        
        # Analyze cost trend
        cost_trend = self._analyze_cost_trend(time_period)
        
        # Get top models by cost
        top_models = self._get_top_models_by_cost(provider_breakdown)
        
        # Get top tasks by cost (from recent requests)
        top_tasks = self._get_top_tasks_by_cost(time_period)
        
        # Find peak usage hour
        peak_hour = self._find_peak_usage_hour()
        
        # Find most expensive request
        most_expensive = self._find_most_expensive_request(time_period)
        
        # Calculate optimization rate
        optimization_rate = self._calculate_optimization_rate(time_period)
        
        return UsageStats(
            total_requests=total_requests,
            total_cost=total_cost,
            total_tokens=total_tokens,
            average_cost_per_request=avg_cost_per_request,
            average_cost_per_token=avg_cost_per_token,
            average_tokens_per_request=avg_tokens_per_request,
            cost_trend=cost_trend,
            top_models=top_models,
            top_tasks=top_tasks,
            peak_usage_hour=peak_hour,
            most_expensive_request=most_expensive,
            total_savings=total_savings,
            optimization_rate=optimization_rate
        )
    
    def generate_detailed_report(self, time_period: str = "month") -> CostReport:
        """Generate comprehensive cost analysis report"""
        
        # Calculate date range
        end_date = datetime.now()
        if time_period == "day":
            start_date = end_date - timedelta(days=1)
        elif time_period == "week":
            start_date = end_date - timedelta(weeks=1)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Generate core statistics
        summary = self.generate_usage_stats(time_period)
        
        # Provider breakdown with analysis
        provider_breakdown = self._analyze_provider_performance(time_period)
        
        # Model performance analysis
        model_performance = self._analyze_model_performance(time_period)
        
        # Cost trends
        cost_trends = self.cost_tracker.get_cost_trend(time_period, 30) if self.cost_tracker else []
        
        # Generate recommendations
        recommendations = self._generate_recommendations(summary, provider_breakdown, model_performance)
        
        # Calculate potential savings
        potential_savings = self._calculate_potential_savings(time_period)
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(summary, model_performance)
        
        return CostReport(
            period=time_period,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            summary=summary,
            provider_breakdown=provider_breakdown,
            model_performance=model_performance,
            cost_trends=cost_trends,
            recommendations=recommendations,
            potential_savings=potential_savings,
            efficiency_score=efficiency_score,
            generated_at=datetime.now().isoformat()
        )
    
    def _analyze_cost_trend(self, time_period: str) -> str:
        """Analyze whether costs are increasing, decreasing, or stable"""
        
        if not self.cost_tracker:
            return "unknown"
        
        try:
            if time_period == "month":
                trend_data = self.cost_tracker.get_cost_trend("day", 30)
            else:
                trend_data = self.cost_tracker.get_cost_trend("hour", 24)
            
            if len(trend_data) < 5:
                return "insufficient_data"
            
            # Get recent costs (last 50% of data points)
            recent_costs = [cost for _, cost in trend_data[-len(trend_data)//2:]]
            earlier_costs = [cost for _, cost in trend_data[:len(trend_data)//2]]
            
            if not recent_costs or not earlier_costs:
                return "insufficient_data"
            
            recent_avg = statistics.mean(recent_costs)
            earlier_avg = statistics.mean(earlier_costs)
            
            # Calculate percentage change
            if earlier_avg == 0:
                return "stable" if recent_avg == 0 else "increasing"
            
            change_percentage = ((recent_avg - earlier_avg) / earlier_avg) * 100
            
            if change_percentage > 10:
                return "increasing"
            elif change_percentage < -10:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.debug(f"Failed to analyze cost trend: {e}")
            return "unknown"
    
    def _get_top_models_by_cost(self, provider_breakdown: Dict) -> List[Tuple[str, float]]:
        """Get top models by total cost"""
        
        model_costs = []
        
        for provider_name, provider_data in provider_breakdown.items():
            if isinstance(provider_data, dict) and "cost_by_model" in provider_data:
                for model, cost in provider_data["cost_by_model"].items():
                    model_costs.append((f"{provider_name}:{model}", cost))
        
        # Sort by cost (highest first) and return top 5
        model_costs.sort(key=lambda x: x[1], reverse=True)
        return model_costs[:5]
    
    def _get_top_tasks_by_cost(self, time_period: str) -> List[Tuple[str, float]]:
        """Get top task types by cost from recent requests"""
        
        if not self.cost_tracker:
            return []
        
        try:
            # Get recent requests
            cutoff = self._get_period_cutoff(time_period)
            task_costs = defaultdict(float)
            
            # Sum costs by task type
            for request in self.cost_tracker._recent_requests:
                if request.timestamp >= cutoff:
                    task_costs[request.task_type] += request.total_cost
            
            # Sort and return top 5
            sorted_tasks = sorted(task_costs.items(), key=lambda x: x[1], reverse=True)
            return sorted_tasks[:5]
            
        except Exception as e:
            logger.debug(f"Failed to get top tasks: {e}")
            return []
    
    def _find_peak_usage_hour(self) -> Optional[str]:
        """Find the hour with highest usage"""
        
        if not self.cost_tracker:
            return None
        
        try:
            # Get hourly data for last 48 hours
            hourly_data = self.cost_tracker.get_cost_trend("hour", 48)
            
            if not hourly_data:
                return None
            
            # Find hour with maximum cost
            max_hour = max(hourly_data, key=lambda x: x[1])
            
            # Convert to readable format
            hour_str = max_hour[0]  # Format: "2025-08-08-14"
            dt = datetime.strptime(hour_str, "%Y-%m-%d-%H")
            return dt.strftime("%I %p")  # e.g., "02 PM"
            
        except Exception as e:
            logger.debug(f"Failed to find peak usage hour: {e}")
            return None
    
    def _find_most_expensive_request(self, time_period: str) -> Optional[float]:
        """Find the most expensive request in the period"""
        
        if not self.cost_tracker:
            return None
        
        try:
            cutoff = self._get_period_cutoff(time_period)
            max_cost = 0.0
            
            for request in self.cost_tracker._recent_requests:
                if request.timestamp >= cutoff:
                    max_cost = max(max_cost, request.total_cost)
            
            return max_cost if max_cost > 0 else None
            
        except Exception as e:
            logger.debug(f"Failed to find most expensive request: {e}")
            return None
    
    def _calculate_optimization_rate(self, time_period: str) -> float:
        """Calculate percentage of requests that were optimized"""
        
        if not self.cost_tracker:
            return 0.0
        
        try:
            cutoff = self._get_period_cutoff(time_period)
            total_requests = 0
            optimized_requests = 0
            
            for request in self.cost_tracker._recent_requests:
                if request.timestamp >= cutoff:
                    total_requests += 1
                    if request.optimization_applied:
                        optimized_requests += 1
            
            return (optimized_requests / max(total_requests, 1)) * 100
            
        except Exception as e:
            logger.debug(f"Failed to calculate optimization rate: {e}")
            return 0.0
    
    def _analyze_provider_performance(self, time_period: str) -> Dict[str, Dict[str, Any]]:
        """Analyze performance metrics for each provider"""
        
        if not self.cost_tracker:
            return {}
        
        provider_breakdown = self.cost_tracker.get_provider_breakdown(time_period)
        enhanced_breakdown = {}
        
        for provider_name, provider_data in provider_breakdown.items():
            if not isinstance(provider_data, dict):
                continue
            
            # Calculate additional metrics
            total_cost = provider_data.get("total_cost", 0.0)
            total_requests = provider_data.get("total_requests", 0)
            
            # Calculate cost efficiency (cost per successful request)
            cost_efficiency = total_cost / max(total_requests, 1)
            
            # Calculate model diversity (number of different models used)
            model_diversity = len(provider_data.get("cost_by_model", {}))
            
            # Performance rating (subjective, based on cost efficiency and usage)
            if cost_efficiency < 0.001:
                performance_rating = "excellent"
            elif cost_efficiency < 0.01:
                performance_rating = "good"
            elif cost_efficiency < 0.05:
                performance_rating = "fair"
            else:
                performance_rating = "expensive"
            
            base_data = provider_data.to_dict() if hasattr(provider_data, 'to_dict') else provider_data
            enhanced_breakdown[provider_name] = {
                **base_data,
                "cost_efficiency": cost_efficiency,
                "model_diversity": model_diversity,
                "performance_rating": performance_rating
            }
        
        return enhanced_breakdown
    
    def _analyze_model_performance(self, time_period: str) -> Dict[str, Dict[str, Any]]:
        """Analyze performance metrics for each model"""
        
        if not self.cost_tracker:
            return {}
        
        model_performance = {}
        
        try:
            cutoff = self._get_period_cutoff(time_period)
            
            # Aggregate data by model
            model_stats = defaultdict(lambda: {
                "requests": 0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "response_times": []
            })
            
            for request in self.cost_tracker._recent_requests:
                if request.timestamp >= cutoff:
                    model_key = f"{request.provider}:{request.model}"
                    stats = model_stats[model_key]
                    
                    stats["requests"] += 1
                    stats["total_cost"] += request.total_cost
                    stats["total_tokens"] += request.total_tokens
                    # Note: response_times would need to be tracked separately
            
            # Calculate performance metrics for each model
            for model_key, stats in model_stats.items():
                requests = stats["requests"]
                total_cost = stats["total_cost"]
                total_tokens = stats["total_tokens"]
                
                avg_cost_per_request = total_cost / max(requests, 1)
                avg_cost_per_token = total_cost / max(total_tokens, 1)
                avg_tokens_per_request = total_tokens / max(requests, 1)
                
                # Calculate efficiency score based on baseline
                provider, model = model_key.split(":", 1)
                efficiency_score = self._calculate_model_efficiency_score(
                    model, avg_cost_per_token, total_cost
                )
                
                model_performance[model_key] = {
                    "requests": requests,
                    "total_cost": total_cost,
                    "total_tokens": total_tokens,
                    "avg_cost_per_request": avg_cost_per_request,
                    "avg_cost_per_token": avg_cost_per_token,
                    "avg_tokens_per_request": avg_tokens_per_request,
                    "efficiency_score": efficiency_score,
                    "cost_share": (total_cost / self.cost_tracker._total_cost * 100) if self.cost_tracker._total_cost > 0 else 0
                }
                
        except Exception as e:
            logger.debug(f"Failed to analyze model performance: {e}")
        
        return model_performance
    
    def _calculate_model_efficiency_score(self, model: str, avg_cost_per_token: float, total_cost: float) -> float:
        """Calculate efficiency score for a model (0-100)"""
        
        if model not in self.efficiency_baselines:
            return 50.0  # Neutral score for unknown models
        
        baseline_efficiency = self.efficiency_baselines[model]
        
        if avg_cost_per_token == 0:
            return 100.0
        
        # Compare actual efficiency to baseline
        efficiency_ratio = baseline_efficiency / avg_cost_per_token
        
        # Convert to 0-100 score
        score = min(100.0, max(0.0, efficiency_ratio * 50))
        
        return score
    
    def _generate_recommendations(self, 
                                summary: UsageStats,
                                provider_breakdown: Dict,
                                model_performance: Dict) -> List[str]:
        """Generate actionable cost optimization recommendations"""
        
        recommendations = []
        
        # High-level recommendations based on usage stats
        if summary.cost_trend == "increasing":
            recommendations.append("⚠️ Costs are trending upward - review recent usage patterns")
        
        if summary.optimization_rate < 20:
            recommendations.append("💡 Enable more aggressive cost optimization - only {:.1f}% of requests are optimized".format(summary.optimization_rate))
        
        if summary.average_cost_per_request > 0.01:
            recommendations.append("💰 Average request cost is high (${:.4f}) - consider cheaper models for simple tasks".format(summary.average_cost_per_request))
        
        # Model-specific recommendations
        expensive_models = [
            (model, data) for model, data in model_performance.items()
            if data.get("avg_cost_per_request", 0) > 0.02 and data.get("cost_share", 0) > 10
        ]
        
        if expensive_models:
            for model, data in expensive_models[:3]:  # Top 3 expensive models
                recommendations.append(
                    f"🎯 Consider optimizing '{model}' - high cost per request (${data['avg_cost_per_request']:.4f})"
                )
        
        # Provider-specific recommendations
        for provider, data in provider_breakdown.items():
            if data.get("performance_rating") == "expensive":
                recommendations.append(f"⚡ Review '{provider}' usage - marked as expensive")
        
        # Budget-based recommendations
        if self.budget_manager:
            budget_statuses = self.budget_manager.get_all_budget_status()
            for status in budget_statuses:
                if status.usage_percentage > 75:
                    recommendations.append(
                        f"🚨 Budget '{status.name}' at {status.usage_percentage:.1f}% - implement cost controls"
                    )
        
        # Peak usage recommendations
        if summary.peak_usage_hour:
            recommendations.append(
                f"📊 Peak usage at {summary.peak_usage_hour} - consider rate limiting during high-traffic hours"
            )
        
        # Default recommendations if none specific
        if not recommendations:
            recommendations = [
                "✅ Usage patterns look optimized",
                "💡 Consider setting up budget alerts for proactive cost management",
                "📈 Monitor cost trends regularly for early detection of issues"
            ]
        
        return recommendations
    
    def _calculate_potential_savings(self, time_period: str) -> float:
        """Calculate potential savings from various optimizations"""
        
        potential_savings = 0.0
        
        try:
            if not self.cost_tracker:
                return 0.0
            
            cutoff = self._get_period_cutoff(time_period)
            
            # Calculate savings from model downgrades
            for request in self.cost_tracker._recent_requests:
                if request.timestamp >= cutoff:
                    # Example: if using gpt-5 for simple tasks, could use gpt-5-nano
                    if request.model == "gpt-5" and request.task_type == "simple":
                        # Potential savings: difference between gpt-5 and gpt-5-nano
                        current_cost = request.total_cost
                        nano_cost = current_cost * (0.05 / 1.25)  # Cost ratio
                        potential_savings += (current_cost - nano_cost)
                    
                    # Similar logic for other expensive models...
            
            # Add potential savings from deduplication
            # (This would require tracking duplicate requests)
            
        except Exception as e:
            logger.debug(f"Failed to calculate potential savings: {e}")
        
        return potential_savings
    
    def _calculate_efficiency_score(self, summary: UsageStats, model_performance: Dict) -> float:
        """Calculate overall efficiency score (0-100)"""
        
        score = 50.0  # Base score
        
        # Optimization rate factor (0-20 points)
        score += (summary.optimization_rate / 100) * 20
        
        # Cost trend factor (0-15 points)
        if summary.cost_trend == "decreasing":
            score += 15
        elif summary.cost_trend == "stable":
            score += 10
        elif summary.cost_trend == "increasing":
            score -= 5
        
        # Model efficiency factor (0-15 points)
        if model_performance:
            avg_efficiency = statistics.mean([
                data.get("efficiency_score", 50) for data in model_performance.values()
            ])
            score += (avg_efficiency / 100) * 15
        
        # Savings factor (0-10 points)
        if summary.total_savings > 0:
            savings_ratio = summary.total_savings / max(summary.total_cost, 1)
            score += min(10, savings_ratio * 100)
        
        return min(100.0, max(0.0, score))
    
    def _get_period_cutoff(self, time_period: str) -> float:
        """Get timestamp cutoff for time period"""
        now = time.time()
        
        if time_period == "hour":
            return now - 3600
        elif time_period == "day":
            return now - 86400
        elif time_period == "week":
            return now - (7 * 86400)
        elif time_period == "month":
            return now - (30 * 86400)
        else:
            return 0
    
    def _empty_usage_stats(self) -> UsageStats:
        """Return empty usage stats when no tracker available"""
        return UsageStats(
            total_requests=0,
            total_cost=0.0,
            total_tokens=0,
            average_cost_per_request=0.0,
            average_cost_per_token=0.0,
            average_tokens_per_request=0.0,
            cost_trend="unknown",
            top_models=[],
            top_tasks=[],
            peak_usage_hour=None,
            most_expensive_request=None,
            total_savings=0.0,
            optimization_rate=0.0
        )
    
    def export_analytics_data(self, time_period: str = "month", format: str = "json") -> Dict:
        """Export comprehensive analytics data"""
        
        report = self.generate_detailed_report(time_period)
        
        export_data = {
            "analytics_export": {
                "format": format,
                "exported_at": datetime.now().isoformat(),
                "time_period": time_period,
                "report": asdict(report)
            }
        }
        
        return export_data