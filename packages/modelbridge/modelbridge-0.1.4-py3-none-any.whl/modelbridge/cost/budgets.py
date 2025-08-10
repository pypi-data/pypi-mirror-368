"""
Production-grade budget management with alerts, limits, and intelligent controls
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BudgetType(Enum):
    """Types of budget constraints"""
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    PER_REQUEST = "per_request"
    PER_HOUR = "per_hour"
    TOTAL = "total"  # Lifetime budget


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"       # 50% of budget used
    WARNING = "warning"  # 75% of budget used  
    CRITICAL = "critical" # 90% of budget used
    EXCEEDED = "exceeded" # Budget exceeded


@dataclass
class BudgetAlert:
    """Budget alert information"""
    budget_name: str
    budget_type: BudgetType
    alert_level: AlertLevel
    current_usage: float
    budget_limit: float
    usage_percentage: float
    time_remaining: Optional[str]  # e.g., "2 days remaining"
    message: str
    timestamp: float
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'budget_type': self.budget_type.value,
            'alert_level': self.alert_level.value
        }


@dataclass 
class BudgetStatus:
    """Current status of a budget"""
    name: str
    budget_type: BudgetType
    limit: float
    current_usage: float
    remaining: float
    usage_percentage: float
    is_exceeded: bool
    time_remaining: Optional[str]
    projected_usage: Optional[float]  # Based on current trend
    will_exceed: bool  # Projection indicates budget will be exceeded
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'budget_type': self.budget_type.value
        }


class BudgetManager:
    """
    Production-grade budget management with real-time monitoring,
    intelligent alerts, and automatic enforcement
    """
    
    def __init__(self, cost_tracker=None, alert_callbacks: List[Callable] = None):
        """
        Initialize budget manager
        
        Args:
            cost_tracker: CostTracker instance for usage data
            alert_callbacks: List of functions to call when alerts are triggered
        """
        self.cost_tracker = cost_tracker
        self.alert_callbacks = alert_callbacks or []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Budget storage
        self._budgets: Dict[str, Dict[str, Any]] = {}
        self._budget_usage: Dict[str, float] = {}
        self._alert_history: List[BudgetAlert] = []
        
        # Alert thresholds (percentage of budget)
        self.alert_thresholds = {
            AlertLevel.INFO: 0.5,      # 50%
            AlertLevel.WARNING: 0.75,   # 75% 
            AlertLevel.CRITICAL: 0.9,   # 90%
            AlertLevel.EXCEEDED: 1.0    # 100%
        }
        
        # Tracking which alerts have been sent (to avoid spam)
        self._alerts_sent: Dict[str, set] = {}
        
        # Auto-enforcement settings
        self._auto_enforcement_enabled = True
        self._enforcement_actions = {
            AlertLevel.CRITICAL: "warn_user",
            AlertLevel.EXCEEDED: "block_requests"
        }
    
    def create_budget(self,
                     name: str,
                     budget_type: BudgetType,
                     limit: float,
                     auto_reset: bool = True,
                     description: Optional[str] = None) -> bool:
        """
        Create a new budget with specified parameters
        
        Args:
            name: Unique budget identifier
            budget_type: Type of budget (daily, monthly, etc.)
            limit: Budget limit in USD
            auto_reset: Whether to automatically reset when period expires
            description: Optional description of the budget
        
        Returns:
            True if budget was created successfully
        """
        
        with self._lock:
            if name in self._budgets:
                logger.warning(f"Budget '{name}' already exists")
                return False
            
            self._budgets[name] = {
                "type": budget_type,
                "limit": limit,
                "auto_reset": auto_reset,
                "description": description,
                "created_at": time.time(),
                "last_reset": time.time(),
                "enabled": True
            }
            
            self._budget_usage[name] = 0.0
            self._alerts_sent[name] = set()
            
            logger.info(f"Created {budget_type.value} budget '{name}': ${limit:.2f}")
            return True
    
    def set_monthly_budget(self, limit: float, name: str = "monthly_default") -> bool:
        """Convenience method to set monthly budget"""
        return self.create_budget(name, BudgetType.MONTHLY, limit, description="Default monthly budget")
    
    def set_daily_budget(self, limit: float, name: str = "daily_default") -> bool:
        """Convenience method to set daily budget"""
        return self.create_budget(name, BudgetType.DAILY, limit, description="Default daily budget")
    
    def set_request_budget(self, limit: float, name: str = "per_request_default") -> bool:
        """Convenience method to set per-request budget"""
        return self.create_budget(name, BudgetType.PER_REQUEST, limit, description="Default per-request budget")
    
    def check_budget_before_request(self, estimated_cost: float) -> Dict[str, Any]:
        """
        Check if a request would exceed budgets before making it
        
        Args:
            estimated_cost: Estimated cost of the upcoming request
        
        Returns:
            Dictionary with status and any budget violations
        """
        
        with self._lock:
            violations = []
            warnings = []
            
            for name, budget in self._budgets.items():
                if not budget["enabled"]:
                    continue
                
                current_usage = self._get_current_usage(name, budget["type"])
                projected_usage = current_usage + estimated_cost
                limit = budget["limit"]
                
                if budget["type"] == BudgetType.PER_REQUEST:
                    # For per-request budgets, check the estimated cost directly
                    if estimated_cost > limit:
                        violations.append({
                            "budget_name": name,
                            "type": "per_request",
                            "limit": limit,
                            "estimated_cost": estimated_cost,
                            "message": f"Request cost ${estimated_cost:.4f} exceeds per-request budget ${limit:.4f}"
                        })
                else:
                    # For time-based budgets, check projected usage
                    if projected_usage > limit:
                        violations.append({
                            "budget_name": name,
                            "type": budget["type"].value,
                            "current_usage": current_usage,
                            "projected_usage": projected_usage,
                            "limit": limit,
                            "message": f"Request would exceed {budget['type'].value} budget (${projected_usage:.4f} > ${limit:.4f})"
                        })
                    elif projected_usage > limit * 0.9:  # 90% threshold
                        warnings.append({
                            "budget_name": name,
                            "type": budget["type"].value,
                            "current_usage": current_usage,
                            "projected_usage": projected_usage,
                            "limit": limit,
                            "usage_percentage": (projected_usage / limit) * 100,
                            "message": f"Request will use {(projected_usage/limit)*100:.1f}% of {budget['type'].value} budget"
                        })
            
            # Determine overall status
            if violations:
                status = "blocked"
                action = "reject_request"
            elif warnings:
                status = "warning"
                action = "allow_with_warning"
            else:
                status = "allowed"
                action = "allow"
            
            return {
                "status": status,
                "action": action,
                "violations": violations,
                "warnings": warnings,
                "estimated_cost": estimated_cost
            }
    
    def record_request_cost(self, cost: float, metadata: Optional[Dict] = None):
        """
        Record actual cost of a completed request and update budgets
        
        Args:
            cost: Actual cost of the request
            metadata: Optional metadata about the request
        """
        
        with self._lock:
            # Update all applicable budgets
            for name, budget in self._budgets.items():
                if not budget["enabled"]:
                    continue
                
                # For time-based budgets, add to current period usage
                if budget["type"] != BudgetType.PER_REQUEST:
                    self._add_usage_to_budget(name, cost)
                
                # Check for alert conditions
                self._check_and_send_alerts(name)
    
    def _add_usage_to_budget(self, budget_name: str, cost: float):
        """Add usage to a budget, handling period resets"""
        
        budget = self._budgets[budget_name]
        budget_type = budget["type"]
        
        # Check if budget period has expired and needs reset
        if self._should_reset_budget(budget_name):
            self._reset_budget(budget_name)
        
        # Add cost to current usage
        if budget_name not in self._budget_usage:
            self._budget_usage[budget_name] = 0.0
        
        self._budget_usage[budget_name] += cost
    
    def _should_reset_budget(self, budget_name: str) -> bool:
        """Check if a budget period has expired"""
        
        budget = self._budgets[budget_name]
        if not budget.get("auto_reset", True):
            return False
        
        budget_type = budget["type"]
        last_reset = budget["last_reset"]
        now = time.time()
        
        if budget_type == BudgetType.DAILY:
            # Reset daily at midnight
            last_reset_date = datetime.fromtimestamp(last_reset).date()
            current_date = datetime.now().date()
            return current_date > last_reset_date
        
        elif budget_type == BudgetType.WEEKLY:
            # Reset weekly on Monday
            last_reset_week = datetime.fromtimestamp(last_reset).isocalendar()[1]
            current_week = datetime.now().isocalendar()[1]
            return current_week != last_reset_week
        
        elif budget_type == BudgetType.MONTHLY:
            # Reset monthly on 1st
            last_reset_month = datetime.fromtimestamp(last_reset).month
            current_month = datetime.now().month
            return current_month != last_reset_month
        
        elif budget_type == BudgetType.PER_HOUR:
            # Reset hourly
            return now - last_reset >= 3600
        
        return False
    
    def _reset_budget(self, budget_name: str):
        """Reset a budget for a new period"""
        
        with self._lock:
            self._budget_usage[budget_name] = 0.0
            self._budgets[budget_name]["last_reset"] = time.time()
            self._alerts_sent[budget_name] = set()  # Reset alert tracking
            
            logger.info(f"Reset budget '{budget_name}' for new period")
    
    def _get_current_usage(self, budget_name: str, budget_type: BudgetType) -> float:
        """Get current usage for a budget"""
        
        if not self.cost_tracker:
            # Fallback to internal tracking if no cost tracker
            return self._budget_usage.get(budget_name, 0.0)
        
        # Use cost tracker for more accurate time-based queries
        if budget_type == BudgetType.DAILY:
            usage_data = self.cost_tracker.get_current_usage("day")
        elif budget_type == BudgetType.MONTHLY:
            usage_data = self.cost_tracker.get_current_usage("month")
        elif budget_type == BudgetType.PER_HOUR:
            usage_data = self.cost_tracker.get_current_usage("hour")
        else:
            # For other types, use internal tracking
            return self._budget_usage.get(budget_name, 0.0)
        
        return usage_data.get("total_cost", 0.0)
    
    def _check_and_send_alerts(self, budget_name: str):
        """Check budget status and send alerts if needed"""
        
        budget = self._budgets[budget_name]
        limit = budget["limit"]
        current_usage = self._get_current_usage(budget_name, budget["type"])
        usage_percentage = current_usage / limit if limit > 0 else 0
        
        # Check each alert threshold
        for alert_level, threshold in self.alert_thresholds.items():
            if usage_percentage >= threshold:
                # Only send alert if we haven't sent this level before
                if alert_level not in self._alerts_sent[budget_name]:
                    self._send_alert(budget_name, alert_level, current_usage, limit, usage_percentage)
                    self._alerts_sent[budget_name].add(alert_level)
    
    def _send_alert(self, 
                   budget_name: str, 
                   alert_level: AlertLevel,
                   current_usage: float,
                   limit: float, 
                   usage_percentage: float):
        """Send budget alert"""
        
        budget = self._budgets[budget_name]
        budget_type = budget["type"]
        
        # Calculate time remaining in budget period
        time_remaining = self._calculate_time_remaining(budget_type, budget["last_reset"])
        
        # Create alert message
        if alert_level == AlertLevel.EXCEEDED:
            message = f"🚨 Budget '{budget_name}' EXCEEDED: ${current_usage:.2f} / ${limit:.2f} ({usage_percentage:.1f}%)"
        elif alert_level == AlertLevel.CRITICAL:
            message = f"⚠️  Budget '{budget_name}' at {usage_percentage:.1f}%: ${current_usage:.2f} / ${limit:.2f}"
        elif alert_level == AlertLevel.WARNING:
            message = f"💰 Budget '{budget_name}' at {usage_percentage:.1f}%: ${current_usage:.2f} / ${limit:.2f}"
        else:
            message = f"ℹ️  Budget '{budget_name}' at {usage_percentage:.1f}%: ${current_usage:.2f} / ${limit:.2f}"
        
        # Create alert object
        alert = BudgetAlert(
            budget_name=budget_name,
            budget_type=budget_type,
            alert_level=alert_level,
            current_usage=current_usage,
            budget_limit=limit,
            usage_percentage=usage_percentage * 100,
            time_remaining=time_remaining,
            message=message,
            timestamp=time.time()
        )
        
        # Store alert in history
        self._alert_history.append(alert)
        
        # Keep only recent alerts (last 100)
        if len(self._alert_history) > 100:
            self._alert_history = self._alert_history[-100:]
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        logger.warning(message)
    
    def _calculate_time_remaining(self, budget_type: BudgetType, last_reset: float) -> Optional[str]:
        """Calculate time remaining in budget period"""
        
        now = time.time()
        
        if budget_type == BudgetType.DAILY:
            # Time until midnight
            tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            seconds_left = (tomorrow - datetime.now()).total_seconds()
            hours_left = int(seconds_left / 3600)
            return f"{hours_left} hours remaining"
        
        elif budget_type == BudgetType.MONTHLY:
            # Time until end of month
            now_dt = datetime.now()
            if now_dt.month == 12:
                next_month = now_dt.replace(year=now_dt.year + 1, month=1, day=1)
            else:
                next_month = now_dt.replace(month=now_dt.month + 1, day=1)
            
            days_left = (next_month - now_dt).days
            return f"{days_left} days remaining"
        
        elif budget_type == BudgetType.PER_HOUR:
            # Time until next hour
            minutes_left = 60 - datetime.now().minute
            return f"{minutes_left} minutes remaining"
        
        return None
    
    def get_all_budget_status(self) -> List[BudgetStatus]:
        """Get current status of all budgets"""
        
        with self._lock:
            statuses = []
            
            for name, budget in self._budgets.items():
                if not budget["enabled"]:
                    continue
                
                limit = budget["limit"]
                budget_type = budget["type"]
                current_usage = self._get_current_usage(name, budget_type)
                remaining = max(0, limit - current_usage)
                usage_percentage = (current_usage / limit * 100) if limit > 0 else 0
                is_exceeded = current_usage > limit
                
                # Calculate time remaining
                time_remaining = self._calculate_time_remaining(budget_type, budget["last_reset"])
                
                # Project future usage based on current trend
                projected_usage = self._project_usage(name, budget_type, current_usage)
                will_exceed = projected_usage > limit if projected_usage else False
                
                status = BudgetStatus(
                    name=name,
                    budget_type=budget_type,
                    limit=limit,
                    current_usage=current_usage,
                    remaining=remaining,
                    usage_percentage=usage_percentage,
                    is_exceeded=is_exceeded,
                    time_remaining=time_remaining,
                    projected_usage=projected_usage,
                    will_exceed=will_exceed
                )
                
                statuses.append(status)
            
            return statuses
    
    def _project_usage(self, budget_name: str, budget_type: BudgetType, current_usage: float) -> Optional[float]:
        """Project end-of-period usage based on current trend"""
        
        if not self.cost_tracker:
            return None
        
        try:
            if budget_type == BudgetType.DAILY:
                # Project based on hourly trend
                trend_data = self.cost_tracker.get_cost_trend("hour", 24)
                if len(trend_data) < 2:
                    return None
                
                # Calculate average hourly cost
                recent_costs = [cost for _, cost in trend_data[-6:]]  # Last 6 hours
                if not recent_costs:
                    return None
                
                avg_hourly = sum(recent_costs) / len(recent_costs)
                hours_remaining = 24 - datetime.now().hour
                projected = current_usage + (avg_hourly * hours_remaining)
                
                return projected
                
            elif budget_type == BudgetType.MONTHLY:
                # Project based on daily trend
                trend_data = self.cost_tracker.get_cost_trend("day", 30)
                if len(trend_data) < 7:  # Need at least a week of data
                    return None
                
                # Calculate average daily cost from recent week
                recent_costs = [cost for _, cost in trend_data[-7:]]
                avg_daily = sum(recent_costs) / len(recent_costs)
                
                days_in_month = 30  # Rough estimate
                current_day = datetime.now().day
                days_remaining = days_in_month - current_day
                
                projected = current_usage + (avg_daily * days_remaining)
                return projected
                
        except Exception as e:
            logger.debug(f"Failed to project usage for {budget_name}: {e}")
        
        return None
    
    def add_alert_callback(self, callback: Callable[[BudgetAlert], None]):
        """Add callback function to be called when alerts are triggered"""
        self.alert_callbacks.append(callback)
    
    def get_recent_alerts(self, hours: int = 24) -> List[BudgetAlert]:
        """Get recent alerts within specified hours"""
        
        cutoff = time.time() - (hours * 3600)
        return [alert for alert in self._alert_history if alert.timestamp >= cutoff]
    
    def disable_budget(self, name: str) -> bool:
        """Disable a budget without deleting it"""
        
        with self._lock:
            if name in self._budgets:
                self._budgets[name]["enabled"] = False
                logger.info(f"Disabled budget '{name}'")
                return True
            return False
    
    def enable_budget(self, name: str) -> bool:
        """Re-enable a disabled budget"""
        
        with self._lock:
            if name in self._budgets:
                self._budgets[name]["enabled"] = True
                logger.info(f"Enabled budget '{name}'")
                return True
            return False
    
    def delete_budget(self, name: str, confirm: bool = False) -> bool:
        """Delete a budget permanently"""
        
        if not confirm:
            raise ValueError("Must set confirm=True to delete budget")
        
        with self._lock:
            if name in self._budgets:
                del self._budgets[name]
                if name in self._budget_usage:
                    del self._budget_usage[name]
                if name in self._alerts_sent:
                    del self._alerts_sent[name]
                
                logger.warning(f"Deleted budget '{name}'")
                return True
            return False
    
    def export_budgets(self) -> Dict:
        """Export all budget configurations and status"""
        
        with self._lock:
            return {
                "budgets": {
                    name: {
                        **budget,
                        "type": budget["type"].value,
                        "current_usage": self._get_current_usage(name, budget["type"])
                    }
                    for name, budget in self._budgets.items()
                },
                "recent_alerts": [alert.to_dict() for alert in self._alert_history[-20:]],
                "exported_at": datetime.now().isoformat()
            }