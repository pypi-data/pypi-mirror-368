"""
Production-grade cost tracking with real-time monitoring and persistence
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RequestCost:
    """Detailed cost information for a single request"""
    request_id: str
    timestamp: float
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    task_type: str
    optimization_applied: Optional[str] = None
    original_model: Optional[str] = None  # If downgraded
    cost_saved: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RequestCost':
        return cls(**data)


@dataclass
class ProviderCosts:
    """Cost summary for a provider"""
    provider: str
    total_requests: int
    total_cost: float
    total_tokens: int
    average_cost_per_request: float
    average_cost_per_token: float
    cost_by_model: Dict[str, float]
    requests_by_model: Dict[str, int]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CostTracker:
    """
    Production-grade cost tracker with real-time monitoring,
    persistence, and thread-safe operations
    """
    
    def __init__(self, 
                 persist_data: bool = True,
                 data_dir: Optional[str] = None,
                 max_memory_entries: int = 10000,
                 auto_save_interval: int = 300):  # 5 minutes
        
        self.persist_data = persist_data
        self.max_memory_entries = max_memory_entries
        self.auto_save_interval = auto_save_interval
        
        # Thread safety
        self._lock = threading.RLock()
        
        # In-memory storage (LRU-style with deque)
        self._recent_requests: deque = deque(maxlen=max_memory_entries)
        self._hourly_costs: Dict[str, float] = defaultdict(float)  # hour -> cost
        self._daily_costs: Dict[str, float] = defaultdict(float)   # date -> cost
        self._monthly_costs: Dict[str, float] = defaultdict(float) # month -> cost
        self._provider_totals: Dict[str, ProviderCosts] = {}
        
        # Aggregated statistics (for performance)
        self._total_cost: float = 0.0
        self._total_requests: int = 0
        self._total_tokens: int = 0
        self._total_saved: float = 0.0
        
        # Data persistence
        if self.persist_data:
            self.data_dir = Path(data_dir or os.path.expanduser("~/.modelbridge/costs"))
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self._load_persisted_data()
            self._start_auto_save()
    
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
                     cost_saved: float = 0.0) -> RequestCost:
        """
        Track a request with thread-safe operations and real-time aggregation
        """
        
        with self._lock:
            timestamp = time.time()
            
            # Calculate detailed costs (estimate input/output split)
            total_tokens = prompt_tokens + completion_tokens
            if completion_tokens > 0:
                # Rough estimation: output tokens typically cost 3-5x more
                output_ratio = 0.75  # 75% of cost from output tokens typically
                output_cost = total_cost * output_ratio
                input_cost = total_cost - output_cost
            else:
                input_cost = total_cost
                output_cost = 0.0
            
            # Create request cost record
            request_cost = RequestCost(
                request_id=request_id,
                timestamp=timestamp,
                provider=provider,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                input_cost=input_cost,
                output_cost=output_cost,
                total_cost=total_cost,
                task_type=task_type,
                optimization_applied=optimization_applied,
                original_model=original_model,
                cost_saved=cost_saved
            )
            
            # Add to recent requests (LRU cache)
            self._recent_requests.append(request_cost)
            
            # Update time-based aggregates
            dt = datetime.fromtimestamp(timestamp)
            hour_key = dt.strftime("%Y-%m-%d-%H")
            day_key = dt.strftime("%Y-%m-%d")
            month_key = dt.strftime("%Y-%m")
            
            self._hourly_costs[hour_key] += total_cost
            self._daily_costs[day_key] += total_cost
            self._monthly_costs[month_key] += total_cost
            
            # Update provider totals
            self._update_provider_totals(request_cost)
            
            # Update global statistics
            self._total_cost += total_cost
            self._total_requests += 1
            self._total_tokens += total_tokens
            self._total_saved += cost_saved
            
            logger.debug(f"Tracked request {request_id}: ${total_cost:.4f} "
                        f"({provider}/{model}, {total_tokens} tokens)")
            
            return request_cost
    
    def _update_provider_totals(self, request_cost: RequestCost):
        """Update provider-level cost aggregations"""
        provider = request_cost.provider
        
        if provider not in self._provider_totals:
            self._provider_totals[provider] = ProviderCosts(
                provider=provider,
                total_requests=0,
                total_cost=0.0,
                total_tokens=0,
                average_cost_per_request=0.0,
                average_cost_per_token=0.0,
                cost_by_model={},
                requests_by_model={}
            )
        
        provider_costs = self._provider_totals[provider]
        
        # Update totals
        provider_costs.total_requests += 1
        provider_costs.total_cost += request_cost.total_cost
        provider_costs.total_tokens += request_cost.total_tokens
        
        # Update model-specific data
        model = request_cost.model
        if model not in provider_costs.cost_by_model:
            provider_costs.cost_by_model[model] = 0.0
            provider_costs.requests_by_model[model] = 0
        
        provider_costs.cost_by_model[model] += request_cost.total_cost
        provider_costs.requests_by_model[model] += 1
        
        # Update averages
        provider_costs.average_cost_per_request = (
            provider_costs.total_cost / provider_costs.total_requests
        )
        if provider_costs.total_tokens > 0:
            provider_costs.average_cost_per_token = (
                provider_costs.total_cost / provider_costs.total_tokens
            )
    
    def get_current_usage(self, time_period: str = "month") -> Dict:
        """
        Get current usage statistics for specified time period
        
        Args:
            time_period: "hour", "day", "month", or "all"
        
        Returns:
            Dictionary with cost and usage statistics
        """
        
        with self._lock:
            now = datetime.now()
            
            if time_period == "hour":
                key = now.strftime("%Y-%m-%d-%H")
                cost = self._hourly_costs.get(key, 0.0)
                period_name = "Current Hour"
            elif time_period == "day":
                key = now.strftime("%Y-%m-%d")
                cost = self._daily_costs.get(key, 0.0)
                period_name = "Today"
            elif time_period == "month":
                key = now.strftime("%Y-%m")
                cost = self._monthly_costs.get(key, 0.0)
                period_name = "This Month"
            else:  # "all"
                cost = self._total_cost
                period_name = "All Time"
            
            # Calculate request count for this period
            if time_period == "all":
                request_count = self._total_requests
                token_count = self._total_tokens
            else:
                # Count requests in the time period
                cutoff = self._get_period_cutoff(time_period)
                period_requests = [
                    req for req in self._recent_requests 
                    if req.timestamp >= cutoff
                ]
                request_count = len(period_requests)
                token_count = sum(req.total_tokens for req in period_requests)
            
            return {
                "period": period_name,
                "total_cost": cost,
                "total_requests": request_count,
                "total_tokens": token_count,
                "average_cost_per_request": cost / max(request_count, 1),
                "average_cost_per_token": cost / max(token_count, 1),
                "total_saved": self._total_saved,
                "timestamp": time.time()
            }
    
    def get_provider_breakdown(self, time_period: str = "month") -> Dict[str, ProviderCosts]:
        """Get cost breakdown by provider for specified time period"""
        
        with self._lock:
            if time_period == "all":
                return self._provider_totals.copy()
            
            # For time periods, filter recent requests
            cutoff = self._get_period_cutoff(time_period)
            period_requests = [
                req for req in self._recent_requests 
                if req.timestamp >= cutoff
            ]
            
            # Rebuild provider totals for this period
            period_totals = {}
            for request in period_requests:
                provider = request.provider
                if provider not in period_totals:
                    period_totals[provider] = ProviderCosts(
                        provider=provider,
                        total_requests=0,
                        total_cost=0.0,
                        total_tokens=0,
                        average_cost_per_request=0.0,
                        average_cost_per_token=0.0,
                        cost_by_model={},
                        requests_by_model={}
                    )
                
                p = period_totals[provider]
                p.total_requests += 1
                p.total_cost += request.total_cost
                p.total_tokens += request.total_tokens
                
                model = request.model
                if model not in p.cost_by_model:
                    p.cost_by_model[model] = 0.0
                    p.requests_by_model[model] = 0
                
                p.cost_by_model[model] += request.total_cost
                p.requests_by_model[model] += 1
            
            # Calculate averages
            for provider_costs in period_totals.values():
                if provider_costs.total_requests > 0:
                    provider_costs.average_cost_per_request = (
                        provider_costs.total_cost / provider_costs.total_requests
                    )
                if provider_costs.total_tokens > 0:
                    provider_costs.average_cost_per_token = (
                        provider_costs.total_cost / provider_costs.total_tokens
                    )
            
            return period_totals
    
    def get_cost_trend(self, time_period: str = "day", points: int = 24) -> List[Tuple[str, float]]:
        """
        Get cost trend data for charting/visualization
        
        Args:
            time_period: "hour" or "day"  
            points: Number of data points to return
        
        Returns:
            List of (timestamp, cost) tuples
        """
        
        with self._lock:
            now = datetime.now()
            trend_data = []
            
            if time_period == "hour":
                # Hourly data points
                for i in range(points):
                    dt = now - timedelta(hours=i)
                    key = dt.strftime("%Y-%m-%d-%H")
                    cost = self._hourly_costs.get(key, 0.0)
                    trend_data.append((key, cost))
            else:  # "day"
                # Daily data points  
                for i in range(points):
                    dt = now - timedelta(days=i)
                    key = dt.strftime("%Y-%m-%d")
                    cost = self._daily_costs.get(key, 0.0)
                    trend_data.append((key, cost))
            
            return list(reversed(trend_data))  # Chronological order
    
    def _get_period_cutoff(self, time_period: str) -> float:
        """Get timestamp cutoff for time period"""
        now = time.time()
        
        if time_period == "hour":
            return now - 3600  # 1 hour
        elif time_period == "day":
            return now - 86400  # 24 hours
        elif time_period == "month":
            return now - (30 * 86400)  # 30 days
        else:
            return 0  # All time
    
    def _load_persisted_data(self):
        """Load persisted cost data from disk"""
        if not self.persist_data:
            return
            
        try:
            # Load aggregated data
            totals_file = self.data_dir / "totals.json"
            if totals_file.exists():
                with open(totals_file, 'r') as f:
                    data = json.load(f)
                    self._total_cost = data.get("total_cost", 0.0)
                    self._total_requests = data.get("total_requests", 0)
                    self._total_tokens = data.get("total_tokens", 0)
                    self._total_saved = data.get("total_saved", 0.0)
            
            # Load time-based costs
            for period, storage in [
                ("hourly", self._hourly_costs),
                ("daily", self._daily_costs), 
                ("monthly", self._monthly_costs)
            ]:
                period_file = self.data_dir / f"{period}_costs.json"
                if period_file.exists():
                    with open(period_file, 'r') as f:
                        data = json.load(f)
                        storage.update(data)
            
            # Load provider totals
            providers_file = self.data_dir / "providers.json"
            if providers_file.exists():
                with open(providers_file, 'r') as f:
                    data = json.load(f)
                    for provider, provider_data in data.items():
                        self._provider_totals[provider] = ProviderCosts(**provider_data)
            
            logger.info(f"Loaded persisted cost data: ${self._total_cost:.2f} total")
            
        except Exception as e:
            logger.warning(f"Failed to load persisted cost data: {e}")
    
    def _save_persisted_data(self):
        """Save cost data to disk"""
        if not self.persist_data:
            return
            
        try:
            # Save aggregated totals
            totals_data = {
                "total_cost": self._total_cost,
                "total_requests": self._total_requests,
                "total_tokens": self._total_tokens,
                "total_saved": self._total_saved,
                "last_updated": time.time()
            }
            
            with open(self.data_dir / "totals.json", 'w') as f:
                json.dump(totals_data, f, indent=2)
            
            # Save time-based costs (keep only recent data)
            now = datetime.now()
            
            # Keep last 48 hours of hourly data
            recent_hourly = {
                k: v for k, v in self._hourly_costs.items()
                if datetime.strptime(k, "%Y-%m-%d-%H") > now - timedelta(hours=48)
            }
            with open(self.data_dir / "hourly_costs.json", 'w') as f:
                json.dump(recent_hourly, f)
            
            # Keep last 90 days of daily data
            recent_daily = {
                k: v for k, v in self._daily_costs.items()
                if datetime.strptime(k, "%Y-%m-%d") > now - timedelta(days=90)
            }
            with open(self.data_dir / "daily_costs.json", 'w') as f:
                json.dump(recent_daily, f)
            
            # Keep last 12 months of monthly data
            recent_monthly = {
                k: v for k, v in self._monthly_costs.items()
                if datetime.strptime(k, "%Y-%m") > now - timedelta(days=365)
            }
            with open(self.data_dir / "monthly_costs.json", 'w') as f:
                json.dump(recent_monthly, f)
            
            # Save provider totals
            provider_data = {
                provider: costs.to_dict() 
                for provider, costs in self._provider_totals.items()
            }
            with open(self.data_dir / "providers.json", 'w') as f:
                json.dump(provider_data, f, indent=2)
            
            logger.debug("Saved cost data to disk")
            
        except Exception as e:
            logger.error(f"Failed to save cost data: {e}")
    
    def _start_auto_save(self):
        """Start background thread for periodic data saving"""
        if not self.persist_data:
            return
            
        def auto_save_loop():
            while True:
                time.sleep(self.auto_save_interval)
                try:
                    with self._lock:
                        self._save_persisted_data()
                except Exception as e:
                    logger.error(f"Auto-save failed: {e}")
        
        thread = threading.Thread(target=auto_save_loop, daemon=True)
        thread.start()
        logger.info(f"Started auto-save thread (interval: {self.auto_save_interval}s)")
    
    def save_data(self):
        """Save data to disk (if persistence is enabled)"""
        self._save_persisted_data()
    
    def load_data(self):
        """Load data from disk (if persistence is enabled)"""
        self._load_persisted_data()
    
    def export_data(self, format: str = "json", time_period: str = "month") -> Dict:
        """
        Export cost data in specified format
        
        Args:
            format: "json" or "csv" 
            time_period: "hour", "day", "month", or "all"
        
        Returns:
            Exported data dictionary
        """
        
        with self._lock:
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "time_period": time_period,
                    "format": format,
                    "total_requests": self._total_requests,
                    "total_cost": self._total_cost
                },
                "usage_summary": self.get_current_usage(time_period),
                "provider_breakdown": {
                    name: costs.to_dict() 
                    for name, costs in self.get_provider_breakdown(time_period).items()
                },
                "cost_trend": self.get_cost_trend(time_period, 30)
            }
            
            # Add recent requests if requested
            if time_period != "all":
                cutoff = self._get_period_cutoff(time_period)
                period_requests = [
                    req.to_dict() for req in self._recent_requests
                    if req.timestamp >= cutoff
                ]
                export_data["recent_requests"] = period_requests
            
            return export_data
    
    def reset_data(self, confirm: bool = False):
        """Reset all cost tracking data (use with caution)"""
        if not confirm:
            raise ValueError("Must set confirm=True to reset cost data")
        
        with self._lock:
            self._recent_requests.clear()
            self._hourly_costs.clear()
            self._daily_costs.clear()
            self._monthly_costs.clear()
            self._provider_totals.clear()
            
            self._total_cost = 0.0
            self._total_requests = 0
            self._total_tokens = 0
            self._total_saved = 0.0
            
            if self.persist_data:
                # Remove persisted files
                for file_name in ["totals.json", "hourly_costs.json", 
                                 "daily_costs.json", "monthly_costs.json", "providers.json"]:
                    file_path = self.data_dir / file_name
                    if file_path.exists():
                        file_path.unlink()
            
            logger.warning("All cost tracking data has been reset")