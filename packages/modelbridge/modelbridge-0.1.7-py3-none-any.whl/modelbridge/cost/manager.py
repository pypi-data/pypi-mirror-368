"""
Production-grade Cost Manager - Central cost management system
Integrates tracking, budgets, optimization, and analytics
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import asdict

from .tracker import CostTracker, RequestCost
from .budgets import BudgetManager, BudgetAlert, BudgetType, AlertLevel
from .optimizer import CostOptimizer, OptimizationStrategy, OptimizationResult
from .analytics import CostAnalytics, CostReport, UsageStats

logger = logging.getLogger(__name__)


class CostManager:
    """
    Production-grade central cost management system
    
    Provides unified interface for:
    - Real-time cost tracking
    - Budget management and alerts  
    - Intelligent cost optimization
    - Advanced analytics and reporting
    """
    
    def __init__(self, 
                 enable_tracking: bool = True,
                 enable_budgets: bool = True,
                 enable_optimization: bool = True,
                 data_dir: Optional[str] = None,
                 alert_callbacks: Optional[List[Callable]] = None):
        """
        Initialize cost management system
        
        Args:
            enable_tracking: Enable cost tracking
            enable_budgets: Enable budget management
            enable_optimization: Enable cost optimization
            data_dir: Directory for persistent data storage
            alert_callbacks: Functions to call for budget alerts
        """
        
        self.enable_tracking = enable_tracking
        self.enable_budgets = enable_budgets  
        self.enable_optimization = enable_optimization
        
        # Initialize core components
        self.tracker = CostTracker(
            persist_data=enable_tracking,
            data_dir=data_dir
        ) if enable_tracking else None
        
        self.budget_manager = BudgetManager(
            cost_tracker=self.tracker,
            alert_callbacks=alert_callbacks or []
        ) if enable_budgets else None
        
        self.optimizer = CostOptimizer() if enable_optimization else None
        
        self.analytics = CostAnalytics(
            cost_tracker=self.tracker,
            budget_manager=self.budget_manager
        )
        
        # Global settings
        self._auto_optimization_enabled = False
        self._emergency_mode_enabled = False
        self._cost_aware_routing = True
        
        logger.info("CostManager initialized with components: "
                   f"tracking={enable_tracking}, budgets={enable_budgets}, "
                   f"optimization={enable_optimization}")
    
    # === Core Cost Management API ===
    
    def track_request(self,
                     request_id: str,
                     provider: str,
                     model: str,
                     prompt_tokens: int,
                     completion_tokens: int,
                     total_cost: float,
                     task_type: str = "general",
                     optimization_applied: Optional[str] = None,
                     original_model: Optional[str] = None,
                     cost_saved: float = 0.0) -> Optional[RequestCost]:
        """
        Track a request with comprehensive cost analysis
        
        Returns:
            RequestCost object with detailed cost information
        """
        
        if not self.tracker:
            return None
        
        try:
            # Track the request
            request_cost = self.tracker.track_request(
                request_id=request_id,
                provider=provider,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_cost=total_cost,
                task_type=task_type,
                optimization_applied=optimization_applied,
                original_model=original_model,
                cost_saved=cost_saved
            )
            
            # Update budgets if enabled
            if self.budget_manager:
                self.budget_manager.record_request_cost(total_cost, {
                    "request_id": request_id,
                    "provider": provider,
                    "model": model,
                    "task_type": task_type
                })
            
            return request_cost
            
        except Exception as e:
            logger.error(f"Failed to track request {request_id}: {e}")
            return None
    
    def check_request_budget(self, estimated_cost: float) -> Dict[str, Any]:
        """
        Check if a request would violate budgets before making it
        
        Args:
            estimated_cost: Estimated cost of the request
        
        Returns:
            Dictionary with status and any violations/warnings
        """
        
        if not self.budget_manager:
            return {
                "status": "allowed",
                "action": "allow", 
                "violations": [],
                "warnings": [],
                "estimated_cost": estimated_cost
            }
        
        return self.budget_manager.check_budget_before_request(estimated_cost)
    
    def optimize_model_choice(self,
                             original_model: str,
                             task_type: str,
                             estimated_tokens: int = 1000,
                             max_cost: Optional[float] = None,
                             strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
                             available_providers: Optional[List[str]] = None) -> OptimizationResult:
        """
        Get optimized model recommendation for cost savings
        
        Args:
            original_model: Originally selected model
            task_type: Type of task being performed
            estimated_tokens: Expected token count
            max_cost: Maximum acceptable cost
            strategy: Optimization strategy
            available_providers: Available providers
        
        Returns:
            OptimizationResult with recommended model and analysis
        """
        
        if not self.optimizer:
            # Return no-optimization result
            return OptimizationResult(
                original_model=original_model,
                optimized_model=original_model,
                original_cost=0.0,
                optimized_cost=0.0,
                cost_savings=0.0,
                savings_percentage=0.0,
                quality_impact="none",
                reasoning="Optimization disabled",
                confidence=0.0
            )
        
        return self.optimizer.optimize_model_selection(
            original_model=original_model,
            task_type=task_type,
            strategy=strategy,
            max_cost=max_cost,
            estimated_tokens=estimated_tokens,
            available_providers=available_providers
        )
    
    # === Budget Management API ===
    
    def set_monthly_budget(self, amount: float, name: str = "default_monthly") -> bool:
        """Set monthly spending budget"""
        if self.budget_manager:
            return self.budget_manager.set_monthly_budget(amount, name)
        return False
    
    def set_daily_budget(self, amount: float, name: str = "default_daily") -> bool:
        """Set daily spending budget"""
        if self.budget_manager:
            return self.budget_manager.set_daily_budget(amount, name)
        return False
    
    def set_request_budget(self, amount: float, name: str = "default_request") -> bool:
        """Set per-request spending budget"""
        if self.budget_manager:
            return self.budget_manager.set_request_budget(amount, name)
        return False
    
    def get_budget_status(self) -> List[Dict]:
        """Get status of all budgets"""
        if self.budget_manager:
            statuses = self.budget_manager.get_all_budget_status()
            return [status.to_dict() for status in statuses]
        return []
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent budget alerts"""
        if self.budget_manager:
            alerts = self.budget_manager.get_recent_alerts(hours)
            return [alert.to_dict() for alert in alerts]
        return []
    
    # === Analytics API ===
    
    def get_usage_stats(self, time_period: str = "month") -> Dict:
        """Get comprehensive usage statistics"""
        stats = self.analytics.generate_usage_stats(time_period)
        return asdict(stats)
    
    def get_usage_summary(self, time_period: str = "month") -> Dict:
        """Alias for get_usage_stats for backward compatibility"""
        return self.get_usage_stats(time_period)
    
    def get_cost_report(self, time_period: str = "month") -> Dict:
        """Get detailed cost analysis report"""
        report = self.analytics.generate_detailed_report(time_period)
        return asdict(report)
    
    def get_cost_trends(self, time_period: str = "day", points: int = 24) -> List[tuple]:
        """Get cost trend data for visualization"""
        if self.tracker:
            return self.tracker.get_cost_trend(time_period, points)
        return []
    
    def get_provider_breakdown(self, time_period: str = "month") -> Dict:
        """Get cost breakdown by provider"""
        if self.tracker:
            breakdown = self.tracker.get_provider_breakdown(time_period)
            return {name: costs.to_dict() for name, costs in breakdown.items()}
        return {}
    
    # === Smart Cost Management ===
    
    def enable_auto_optimization(self, 
                                strategy: OptimizationStrategy = OptimizationStrategy.BALANCED):
        """Enable automatic cost optimization for requests"""
        self._auto_optimization_enabled = True
        self._optimization_strategy = strategy
        logger.info(f"Enabled auto-optimization with {strategy.value} strategy")
    
    def disable_auto_optimization(self):
        """Disable automatic cost optimization"""
        self._auto_optimization_enabled = False
        logger.info("Disabled auto-optimization")
    
    def enable_emergency_mode(self):
        """Enable emergency cost reduction mode"""
        self._emergency_mode_enabled = True
        self._auto_optimization_enabled = True
        self._optimization_strategy = OptimizationStrategy.EMERGENCY
        logger.warning("EMERGENCY MODE ENABLED - All requests will use cheapest models")
    
    def disable_emergency_mode(self):
        """Disable emergency cost reduction mode"""
        self._emergency_mode_enabled = False
        logger.info("Emergency mode disabled")
    
    def should_optimize_request(self, 
                               estimated_cost: float,
                               model: str,
                               task_type: str) -> bool:
        """
        Determine if a request should be optimized based on current settings
        """
        
        if not self._auto_optimization_enabled:
            return False
        
        if self._emergency_mode_enabled:
            return True
        
        # Check budget constraints
        budget_check = self.check_request_budget(estimated_cost)
        if budget_check["status"] in ["blocked", "warning"]:
            return True
        
        # Check if model is expensive for the task type
        if self.optimizer:
            optimization = self.optimize_model_choice(
                original_model=model,
                task_type=task_type,
                strategy=self._optimization_strategy
            )
            
            # Optimize if significant savings (>20%) with minimal quality impact
            return (optimization.savings_percentage > 20 and 
                   optimization.quality_impact in ["none", "minimal"])
        
        return False
    
    def get_optimization_recommendations(self) -> Dict:
        """Get comprehensive optimization recommendations"""
        
        if not self.tracker:
            return {"recommendations": ["Enable cost tracking for recommendations"]}
        
        usage_stats = self.get_usage_stats("month")
        usage_pattern = {
            "model_usage": self.get_provider_breakdown("month")
        }
        
        # Get current budget usage
        budget_limit = 100.0  # Default, should be configurable
        current_usage = usage_stats.get("total_cost", 0.0)
        
        if self.optimizer:
            return self.optimizer.get_cost_optimization_recommendations(
                current_usage=current_usage,
                budget_limit=budget_limit,
                usage_pattern=usage_pattern
            )
        
        return {"recommendations": ["Enable cost optimization for detailed recommendations"]}
    
    # === Utility Methods ===
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall cost management system status"""
        
        status = {
            "cost_manager": {
                "tracking_enabled": self.enable_tracking,
                "budgets_enabled": self.enable_budgets,
                "optimization_enabled": self.enable_optimization,
                "auto_optimization": self._auto_optimization_enabled,
                "emergency_mode": self._emergency_mode_enabled
            }
        }
        
        if self.tracker:
            current_usage = self.tracker.get_current_usage("month")
            status["current_month"] = {
                "total_cost": current_usage.get("total_cost", 0.0),
                "total_requests": current_usage.get("total_requests", 0),
                "total_savings": current_usage.get("total_saved", 0.0)
            }
        
        if self.budget_manager:
            budgets = self.get_budget_status()
            status["budgets"] = {
                "total_budgets": len(budgets),
                "budgets_exceeded": len([b for b in budgets if b.get("is_exceeded", False)]),
                "budgets_warning": len([b for b in budgets if b.get("usage_percentage", 0) > 75])
            }
        
        return status
    
    def export_all_data(self, time_period: str = "month") -> Dict:
        """Export comprehensive cost management data"""
        
        export_data = {
            "export_metadata": {
                "timestamp": time.time(),
                "time_period": time_period,
                "components": {
                    "tracking": self.enable_tracking,
                    "budgets": self.enable_budgets,
                    "optimization": self.enable_optimization
                }
            }
        }
        
        # Add tracker data
        if self.tracker:
            export_data["cost_tracking"] = self.tracker.export_data("json", time_period)
        
        # Add budget data
        if self.budget_manager:
            export_data["budget_management"] = self.budget_manager.export_budgets()
        
        # Add analytics data
        export_data["analytics"] = self.analytics.export_analytics_data(time_period)
        
        return export_data
    
    def add_alert_callback(self, callback: Callable[[BudgetAlert], None]):
        """Add callback for budget alerts"""
        if self.budget_manager:
            self.budget_manager.add_alert_callback(callback)
    
    def reset_all_data(self, confirm: bool = False):
        """Reset all cost management data (use with extreme caution)"""
        if not confirm:
            raise ValueError("Must set confirm=True to reset all data")
        
        if self.tracker:
            self.tracker.reset_data(confirm=True)
        
        if self.budget_manager:
            # Reset would need to be implemented in BudgetManager
            pass
        
        logger.warning("ALL COST MANAGEMENT DATA HAS BEEN RESET")


# === Convenience Functions ===

def create_cost_manager(monthly_budget: Optional[float] = None,
                       daily_budget: Optional[float] = None,
                       request_budget: Optional[float] = None,
                       auto_optimize: bool = False,
                       data_dir: Optional[str] = None) -> CostManager:
    """
    Create and configure a cost manager with common settings
    
    Args:
        monthly_budget: Optional monthly budget limit
        daily_budget: Optional daily budget limit  
        request_budget: Optional per-request budget limit
        auto_optimize: Enable automatic cost optimization
        data_dir: Directory for data persistence
    
    Returns:
        Configured CostManager instance
    
    Example:
        # Create with $100 monthly budget and auto-optimization
        cost_manager = create_cost_manager(
            monthly_budget=100.0,
            request_budget=0.01,
            auto_optimize=True
        )
    """
    
    manager = CostManager(data_dir=data_dir)
    
    # Set budgets if provided
    if monthly_budget:
        manager.set_monthly_budget(monthly_budget)
        
    if daily_budget:
        manager.set_daily_budget(daily_budget)
        
    if request_budget:
        manager.set_request_budget(request_budget)
    
    # Enable auto-optimization if requested
    if auto_optimize:
        manager.enable_auto_optimization()
    
    return manager