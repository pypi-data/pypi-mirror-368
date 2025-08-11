"""
Comprehensive tests for the budget management system
"""
import pytest
import pytest_asyncio
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from modelbridge.cost.budgets import (
    BudgetManager, BudgetAlert, BudgetStatus, BudgetType, AlertLevel
)
from modelbridge.cost.tracker import CostTracker


class TestBudgetManager:
    """Test suite for BudgetManager functionality"""
    
    @pytest.fixture
    def mock_cost_tracker(self):
        """Mock cost tracker for testing"""
        tracker = Mock(spec=CostTracker)
        tracker.get_current_usage.return_value = {
            "total_cost": 10.0,
            "total_requests": 100,
            "total_tokens": 15000
        }
        tracker.get_cost_trend.return_value = [(f"2025-01-{i:02d}", 1.0) for i in range(1, 8)]
        return tracker
    
    @pytest.fixture
    def budget_manager(self, mock_cost_tracker):
        """Create budget manager with mock cost tracker"""
        return BudgetManager(cost_tracker=mock_cost_tracker)
    
    @pytest.fixture
    def budget_manager_no_tracker(self):
        """Create budget manager without cost tracker"""
        return BudgetManager(cost_tracker=None)
    
    def test_initialization(self, budget_manager):
        """Test budget manager initialization"""
        assert budget_manager.cost_tracker is not None
        assert len(budget_manager.alert_callbacks) == 0
        assert len(budget_manager._budgets) == 0
        assert len(budget_manager._budget_usage) == 0
        assert budget_manager._auto_enforcement_enabled is True
    
    def test_create_monthly_budget(self, budget_manager):
        """Test creating a monthly budget"""
        success = budget_manager.create_budget(
            name="test_monthly",
            budget_type=BudgetType.MONTHLY,
            limit=100.0,
            description="Test monthly budget"
        )
        
        assert success is True
        assert "test_monthly" in budget_manager._budgets
        
        budget = budget_manager._budgets["test_monthly"]
        assert budget["type"] == BudgetType.MONTHLY
        assert budget["limit"] == 100.0
        assert budget["description"] == "Test monthly budget"
        assert budget["enabled"] is True
    
    def test_create_duplicate_budget(self, budget_manager):
        """Test creating duplicate budget fails"""
        # Create first budget
        success1 = budget_manager.create_budget(
            name="duplicate_test",
            budget_type=BudgetType.DAILY,
            limit=10.0
        )
        assert success1 is True
        
        # Try to create duplicate
        success2 = budget_manager.create_budget(
            name="duplicate_test",
            budget_type=BudgetType.DAILY,
            limit=20.0
        )
        assert success2 is False
    
    def test_convenience_budget_methods(self, budget_manager):
        """Test convenience methods for setting budgets"""
        # Test monthly budget
        success_monthly = budget_manager.set_monthly_budget(100.0)
        assert success_monthly is True
        assert "monthly_default" in budget_manager._budgets
        
        # Test daily budget
        success_daily = budget_manager.set_daily_budget(5.0)
        assert success_daily is True
        assert "daily_default" in budget_manager._budgets
        
        # Test request budget
        success_request = budget_manager.set_request_budget(0.01)
        assert success_request is True
        assert "per_request_default" in budget_manager._budgets
    
    def test_check_budget_before_request_allowed(self, budget_manager):
        """Test budget check when request is within limits"""
        # Create budget
        budget_manager.create_budget("test", BudgetType.MONTHLY, 100.0)
        
        # Mock current usage as 50.0 (within limit)
        budget_manager.cost_tracker.get_current_usage.return_value = {"total_cost": 50.0}
        
        result = budget_manager.check_budget_before_request(1.0)
        
        assert result["status"] == "allowed"
        assert result["action"] == "allow"
        assert len(result["violations"]) == 0
        assert len(result["warnings"]) == 0
    
    def test_check_budget_before_request_warning(self, budget_manager):
        """Test budget check when request triggers warning"""
        # Create budget
        budget_manager.create_budget("test", BudgetType.MONTHLY, 100.0)
        
        # Mock current usage as 89.0 (close to limit)
        budget_manager.cost_tracker.get_current_usage.return_value = {"total_cost": 89.0}
        
        result = budget_manager.check_budget_before_request(2.0)  # Would be 91%
        
        assert result["status"] == "warning"
        assert result["action"] == "allow_with_warning"
        assert len(result["violations"]) == 0
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["usage_percentage"] == 91.0
    
    def test_check_budget_before_request_blocked(self, budget_manager):
        """Test budget check when request would exceed limit"""
        # Create budget
        budget_manager.create_budget("test", BudgetType.MONTHLY, 100.0)
        
        # Mock current usage as 95.0 (near limit)
        budget_manager.cost_tracker.get_current_usage.return_value = {"total_cost": 95.0}
        
        result = budget_manager.check_budget_before_request(10.0)  # Would exceed
        
        assert result["status"] == "blocked"
        assert result["action"] == "reject_request"
        assert len(result["violations"]) == 1
        assert "exceed" in result["violations"][0]["message"]
    
    def test_per_request_budget_check(self, budget_manager_no_tracker):
        """Test per-request budget checking"""
        # Create per-request budget
        budget_manager_no_tracker.create_budget("per_req", BudgetType.PER_REQUEST, 0.01)
        
        # Test request within limit
        result_ok = budget_manager_no_tracker.check_budget_before_request(0.005)
        assert result_ok["status"] == "allowed"
        
        # Test request exceeding limit
        result_blocked = budget_manager_no_tracker.check_budget_before_request(0.02)
        assert result_blocked["status"] == "blocked"
        assert len(result_blocked["violations"]) == 1
        assert "per-request budget" in result_blocked["violations"][0]["message"]
    
    def test_record_request_cost(self, budget_manager):
        """Test recording actual request cost"""
        # Create budget
        budget_manager.create_budget("test", BudgetType.MONTHLY, 100.0)
        
        # Record request cost
        budget_manager.record_request_cost(5.0, {"provider": "openai", "model": "gpt-5"})
        
        # Check internal usage tracking
        assert "test" in budget_manager._budget_usage
        assert budget_manager._budget_usage["test"] == 5.0
    
    def test_alert_triggering(self, budget_manager):
        """Test budget alert triggering"""
        alerts_received = []
        
        def alert_callback(alert):
            alerts_received.append(alert)
        
        budget_manager.add_alert_callback(alert_callback)
        budget_manager.create_budget("alert_test", BudgetType.DAILY, 10.0)
        
        # Mock usage at 80% (should trigger warning)
        budget_manager.cost_tracker.get_current_usage.return_value = {"total_cost": 8.0}
        
        # Record cost that triggers alert check
        budget_manager.record_request_cost(0.5)
        
        # Should have received warning alert
        assert len(alerts_received) == 1
        alert = alerts_received[0]
        assert alert.alert_level == AlertLevel.WARNING
        assert alert.budget_name == "alert_test"
        assert alert.usage_percentage >= 75.0
    
    def test_budget_reset_daily(self, budget_manager_no_tracker):
        """Test daily budget reset logic"""
        # Create daily budget
        budget_manager_no_tracker.create_budget("daily_reset", BudgetType.DAILY, 10.0)
        
        # Add some usage
        budget_manager_no_tracker._add_usage_to_budget("daily_reset", 5.0)
        assert budget_manager_no_tracker._budget_usage["daily_reset"] == 5.0
        
        # Mock time to be next day
        with patch('time.time', return_value=time.time() + 86400):
            with patch('datetime.now') as mock_now, patch('datetime.fromtimestamp') as mock_from_ts:
                # Mock dates for reset logic
                yesterday = datetime.now().date() - timedelta(days=1)
                today = datetime.now().date()
                
                mock_from_ts.return_value.date.return_value = yesterday
                mock_now.return_value.date.return_value = today
                
                # Check if reset is needed
                should_reset = budget_manager_no_tracker._should_reset_budget("daily_reset")
                assert should_reset is True
                
                # Perform reset
                budget_manager_no_tracker._reset_budget("daily_reset")
                assert budget_manager_no_tracker._budget_usage["daily_reset"] == 0.0
    
    def test_budget_status_reporting(self, budget_manager):
        """Test comprehensive budget status reporting"""
        # Create multiple budgets
        budget_manager.create_budget("monthly", BudgetType.MONTHLY, 100.0)
        budget_manager.create_budget("daily", BudgetType.DAILY, 5.0)
        
        # Mock different usage levels
        budget_manager._budget_usage["monthly"] = 75.0  # 75% used
        budget_manager._budget_usage["daily"] = 6.0    # Exceeded
        
        # Mock usage data for projections
        budget_manager.cost_tracker.get_current_usage.side_effect = lambda period: {
            "total_cost": 75.0 if period != "day" else 6.0
        }
        
        statuses = budget_manager.get_all_budget_status()
        
        assert len(statuses) == 2
        
        # Find monthly status
        monthly_status = next(s for s in statuses if s.name == "monthly")
        assert monthly_status.usage_percentage == 75.0
        assert monthly_status.is_exceeded is False
        assert monthly_status.remaining == 25.0
        
        # Find daily status
        daily_status = next(s for s in statuses if s.name == "daily")
        assert daily_status.usage_percentage == 120.0  # Exceeded
        assert daily_status.is_exceeded is True
    
    def test_usage_projection(self, budget_manager):
        """Test usage projection for trend analysis"""
        # Create monthly budget
        budget_manager.create_budget("projection_test", BudgetType.MONTHLY, 100.0)
        
        # Mock trend data showing increasing costs
        trend_data = [(f"2025-01-{i:02d}", i * 2.0) for i in range(1, 8)]  # Increasing trend
        budget_manager.cost_tracker.get_cost_trend.return_value = trend_data
        
        # Mock current usage
        budget_manager.cost_tracker.get_current_usage.return_value = {"total_cost": 20.0}
        
        # Get projection
        projected = budget_manager._project_usage("projection_test", BudgetType.MONTHLY, 20.0)
        
        # Should project higher usage based on trend
        assert projected is not None
        assert projected > 20.0  # Should be higher than current
    
    def test_disable_enable_budget(self, budget_manager):
        """Test disabling and enabling budgets"""
        # Create budget
        budget_manager.create_budget("toggle_test", BudgetType.DAILY, 10.0)
        
        # Disable budget
        success_disable = budget_manager.disable_budget("toggle_test")
        assert success_disable is True
        assert budget_manager._budgets["toggle_test"]["enabled"] is False
        
        # Re-enable budget
        success_enable = budget_manager.enable_budget("toggle_test")
        assert success_enable is True
        assert budget_manager._budgets["toggle_test"]["enabled"] is True
        
        # Test with non-existent budget
        assert budget_manager.disable_budget("nonexistent") is False
        assert budget_manager.enable_budget("nonexistent") is False
    
    def test_delete_budget(self, budget_manager):
        """Test budget deletion"""
        # Create budget
        budget_manager.create_budget("delete_test", BudgetType.DAILY, 10.0)
        assert "delete_test" in budget_manager._budgets
        
        # Delete without confirmation should fail
        with pytest.raises(ValueError, match="Must set confirm=True"):
            budget_manager.delete_budget("delete_test", confirm=False)
        
        # Delete with confirmation
        success = budget_manager.delete_budget("delete_test", confirm=True)
        assert success is True
        assert "delete_test" not in budget_manager._budgets
        assert "delete_test" not in budget_manager._budget_usage
    
    def test_recent_alerts(self, budget_manager):
        """Test recent alerts retrieval"""
        # Create alert manually
        alert = BudgetAlert(
            budget_name="test",
            budget_type=BudgetType.DAILY,
            alert_level=AlertLevel.WARNING,
            current_usage=7.5,
            budget_limit=10.0,
            usage_percentage=75.0,
            time_remaining="6 hours remaining",
            message="Test alert",
            timestamp=time.time()
        )
        
        budget_manager._alert_history.append(alert)
        
        # Get recent alerts
        recent = budget_manager.get_recent_alerts(hours=24)
        assert len(recent) == 1
        assert recent[0].budget_name == "test"
        
        # Test with very short time window
        recent_short = budget_manager.get_recent_alerts(hours=0.001)
        assert len(recent_short) == 0
    
    def test_budget_export(self, budget_manager):
        """Test budget configuration export"""
        # Create some budgets
        budget_manager.create_budget("monthly_export", BudgetType.MONTHLY, 100.0)
        budget_manager.create_budget("daily_export", BudgetType.DAILY, 5.0)
        
        # Add some usage
        budget_manager._budget_usage["monthly_export"] = 25.0
        
        # Export budgets
        export_data = budget_manager.export_budgets()
        
        assert "budgets" in export_data
        assert "recent_alerts" in export_data
        assert "exported_at" in export_data
        
        budgets = export_data["budgets"]
        assert "monthly_export" in budgets
        assert "daily_export" in budgets
        
        monthly_budget = budgets["monthly_export"]
        assert monthly_budget["limit"] == 100.0
        assert monthly_budget["type"] == "monthly"
        assert monthly_budget["current_usage"] >= 0
    
    def test_time_remaining_calculations(self, budget_manager_no_tracker):
        """Test time remaining calculations for different budget types"""
        # Test daily budget time remaining
        with patch('datetime.now') as mock_now:
            # Mock current time as 2 PM
            mock_now.return_value = datetime(2025, 1, 15, 14, 0, 0)
            
            time_remaining = budget_manager_no_tracker._calculate_time_remaining(
                BudgetType.DAILY, time.time()
            )
            
            assert time_remaining is not None
            assert "hours remaining" in time_remaining
        
        # Test monthly budget time remaining
        with patch('datetime.now') as mock_now:
            # Mock current time as Jan 15th
            mock_now.return_value = datetime(2025, 1, 15, 12, 0, 0)
            
            time_remaining = budget_manager_no_tracker._calculate_time_remaining(
                BudgetType.MONTHLY, time.time()
            )
            
            assert time_remaining is not None
            assert "days remaining" in time_remaining
    
    def test_thread_safety(self, budget_manager_no_tracker):
        """Test thread safety of budget operations"""
        # Create budget
        budget_manager_no_tracker.create_budget("thread_test", BudgetType.DAILY, 100.0)
        
        def record_costs():
            for i in range(50):
                budget_manager_no_tracker.record_request_cost(0.1)
        
        # Run multiple threads
        threads = []
        for i in range(4):
            thread = threading.Thread(target=record_costs)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check final state (4 threads * 50 requests * 0.1 cost)
        expected_total = 20.0
        actual_total = budget_manager_no_tracker._budget_usage.get("thread_test", 0.0)
        assert abs(actual_total - expected_total) < 0.01  # Allow small floating point errors


class TestBudgetAlert:
    """Test suite for BudgetAlert data class"""
    
    def test_alert_creation(self):
        """Test BudgetAlert creation"""
        alert = BudgetAlert(
            budget_name="test_budget",
            budget_type=BudgetType.MONTHLY,
            alert_level=AlertLevel.WARNING,
            current_usage=75.0,
            budget_limit=100.0,
            usage_percentage=75.0,
            time_remaining="7 days remaining",
            message="Budget warning",
            timestamp=time.time()
        )
        
        assert alert.budget_name == "test_budget"
        assert alert.budget_type == BudgetType.MONTHLY
        assert alert.alert_level == AlertLevel.WARNING
        assert alert.usage_percentage == 75.0
    
    def test_alert_to_dict(self):
        """Test BudgetAlert to_dict conversion"""
        alert = BudgetAlert(
            budget_name="dict_test",
            budget_type=BudgetType.DAILY,
            alert_level=AlertLevel.CRITICAL,
            current_usage=9.5,
            budget_limit=10.0,
            usage_percentage=95.0,
            time_remaining="1 hour remaining",
            message="Critical alert",
            timestamp=1234567890.0
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict["budget_name"] == "dict_test"
        assert alert_dict["budget_type"] == "daily"  # Should be string value
        assert alert_dict["alert_level"] == "critical"  # Should be string value
        assert alert_dict["usage_percentage"] == 95.0


class TestBudgetStatus:
    """Test suite for BudgetStatus data class"""
    
    def test_status_creation(self):
        """Test BudgetStatus creation"""
        status = BudgetStatus(
            name="status_test",
            budget_type=BudgetType.WEEKLY,
            limit=50.0,
            current_usage=30.0,
            remaining=20.0,
            usage_percentage=60.0,
            is_exceeded=False,
            time_remaining="3 days remaining",
            projected_usage=45.0,
            will_exceed=False
        )
        
        assert status.name == "status_test"
        assert status.budget_type == BudgetType.WEEKLY
        assert status.usage_percentage == 60.0
        assert status.is_exceeded is False
        assert status.will_exceed is False
    
    def test_status_to_dict(self):
        """Test BudgetStatus to_dict conversion"""
        status = BudgetStatus(
            name="dict_status_test",
            budget_type=BudgetType.PER_REQUEST,
            limit=0.01,
            current_usage=0.008,
            remaining=0.002,
            usage_percentage=80.0,
            is_exceeded=False,
            time_remaining=None,
            projected_usage=None,
            will_exceed=False
        )
        
        status_dict = status.to_dict()
        
        assert status_dict["name"] == "dict_status_test"
        assert status_dict["budget_type"] == "per_request"  # Should be string value
        assert status_dict["usage_percentage"] == 80.0
        assert status_dict["time_remaining"] is None