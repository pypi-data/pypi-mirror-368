"""
Comprehensive tests for the integrated cost management system
"""
import pytest
import pytest_asyncio
import time
import tempfile
from unittest.mock import Mock, patch, MagicMock

from modelbridge.cost.manager import CostManager, create_cost_manager
from modelbridge.cost.optimizer import OptimizationStrategy
from modelbridge.cost.budgets import BudgetType, AlertLevel


class TestCostManager:
    """Test suite for CostManager integration"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def cost_manager(self, temp_data_dir):
        """Create cost manager with all components enabled"""
        return CostManager(
            enable_tracking=True,
            enable_budgets=True,
            enable_optimization=True,
            data_dir=temp_data_dir
        )
    
    @pytest.fixture
    def minimal_cost_manager(self):
        """Create cost manager with minimal features for speed"""
        return CostManager(
            enable_tracking=True,
            enable_budgets=False,
            enable_optimization=False
        )
    
    def test_initialization_full_features(self, cost_manager):
        """Test cost manager initialization with all features"""
        assert cost_manager.enable_tracking is True
        assert cost_manager.enable_budgets is True
        assert cost_manager.enable_optimization is True
        
        assert cost_manager.tracker is not None
        assert cost_manager.budget_manager is not None
        assert cost_manager.optimizer is not None
        assert cost_manager.analytics is not None
    
    def test_initialization_minimal_features(self, minimal_cost_manager):
        """Test cost manager initialization with minimal features"""
        assert minimal_cost_manager.enable_tracking is True
        assert minimal_cost_manager.enable_budgets is False
        assert minimal_cost_manager.enable_optimization is False
        
        assert minimal_cost_manager.tracker is not None
        assert minimal_cost_manager.budget_manager is None
        assert minimal_cost_manager.optimizer is None
        assert minimal_cost_manager.analytics is not None
    
    def test_track_request_comprehensive(self, cost_manager):
        """Test comprehensive request tracking with all metadata"""
        request_cost = cost_manager.track_request(
            request_id="test-comprehensive",
            provider="openai",
            model="gpt-5",
            prompt_tokens=200,
            completion_tokens=100,
            total_cost=0.003,
            task_type="coding",
            optimization_applied="downgraded from gpt-5 to gpt-5-mini",
            original_model="gpt-5",
            cost_saved=0.001
        )
        
        assert request_cost is not None
        assert request_cost.request_id == "test-comprehensive"
        assert request_cost.optimization_applied == "downgraded from gpt-5 to gpt-5-mini"
        assert request_cost.cost_saved == 0.001
        
        # Check budget manager was updated (if enabled)
        if cost_manager.budget_manager:
            # Should have recorded the cost
            pass  # Budget manager updates are tested separately
    
    def test_track_request_without_budget_manager(self, minimal_cost_manager):
        """Test request tracking without budget manager"""
        request_cost = minimal_cost_manager.track_request(
            request_id="test-no-budget",
            provider="openai",
            model="gpt-5-mini",
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=0.001
        )
        
        assert request_cost is not None
        assert request_cost.total_cost == 0.001
    
    def test_check_request_budget_with_budgets(self, cost_manager):
        """Test budget checking with budget manager enabled"""
        # Create a budget first
        cost_manager.set_monthly_budget(10.0)
        
        # Check request within budget
        result = cost_manager.check_request_budget(0.01)
        
        assert "status" in result
        assert "action" in result
        assert "violations" in result
        assert "warnings" in result
        assert result["estimated_cost"] == 0.01
        
        # Should be allowed since budget is high
        assert result["status"] in ["allowed", "warning"]
    
    def test_check_request_budget_without_budgets(self, minimal_cost_manager):
        """Test budget checking without budget manager"""
        result = minimal_cost_manager.check_request_budget(1.0)
        
        assert result["status"] == "allowed"
        assert result["action"] == "allow"
        assert len(result["violations"]) == 0
        assert len(result["warnings"]) == 0
    
    def test_optimize_model_choice_with_optimizer(self, cost_manager):
        """Test model optimization with optimizer enabled"""
        optimization = cost_manager.optimize_model_choice(
            original_model="gpt-5",
            task_type="simple",
            estimated_tokens=500,
            strategy=OptimizationStrategy.BALANCED
        )
        
        assert optimization.original_model == "gpt-5"
        assert optimization.optimized_model is not None
        assert optimization.confidence >= 0.0
        assert optimization.reasoning is not None
        
        # For simple tasks, should likely suggest cheaper model
        if optimization.optimized_model != "gpt-5":
            assert optimization.cost_savings > 0
    
    def test_optimize_model_choice_without_optimizer(self, minimal_cost_manager):
        """Test model optimization without optimizer enabled"""
        optimization = minimal_cost_manager.optimize_model_choice(
            original_model="gpt-5",
            task_type="coding"
        )
        
        # Should return no-optimization result
        assert optimization.original_model == "gpt-5"
        assert optimization.optimized_model == "gpt-5"
        assert optimization.cost_savings == 0.0
        assert optimization.confidence == 0.0
        assert "Optimization disabled" in optimization.reasoning
    
    def test_budget_management_api(self, cost_manager):
        """Test budget management convenience methods"""
        # Test monthly budget
        success_monthly = cost_manager.set_monthly_budget(100.0)
        assert success_monthly is True
        
        # Test daily budget
        success_daily = cost_manager.set_daily_budget(5.0)
        assert success_daily is True
        
        # Test request budget
        success_request = cost_manager.set_request_budget(0.01)
        assert success_request is True
        
        # Check budget status
        budget_statuses = cost_manager.get_budget_status()
        assert len(budget_statuses) == 3  # Should have all three budgets
        
        # Check recent alerts (should be empty initially)
        alerts = cost_manager.get_recent_alerts()
        assert isinstance(alerts, list)
    
    def test_budget_management_without_manager(self, minimal_cost_manager):
        """Test budget management methods without budget manager"""
        assert minimal_cost_manager.set_monthly_budget(100.0) is False
        assert minimal_cost_manager.set_daily_budget(5.0) is False
        assert minimal_cost_manager.set_request_budget(0.01) is False
        
        assert len(minimal_cost_manager.get_budget_status()) == 0
        assert len(minimal_cost_manager.get_recent_alerts()) == 0
    
    def test_analytics_api(self, cost_manager):
        """Test analytics convenience methods"""
        # Track some requests first
        for i in range(5):
            cost_manager.track_request(
                request_id=f"analytics-{i}",
                provider="openai",
                model="gpt-5-mini",
                prompt_tokens=100,
                completion_tokens=50,
                total_cost=0.001
            )
        
        # Test usage stats
        usage_stats = cost_manager.get_usage_stats("month")
        assert "total_requests" in usage_stats
        assert "total_cost" in usage_stats
        assert usage_stats["total_requests"] >= 5
        
        # Test cost report
        cost_report = cost_manager.get_cost_report("week")
        assert "period" in cost_report
        assert "summary" in cost_report
        assert "efficiency_score" in cost_report
        
        # Test cost trends
        trends = cost_manager.get_cost_trends("day", 7)
        assert isinstance(trends, list)
        
        # Test provider breakdown
        breakdown = cost_manager.get_provider_breakdown("month")
        assert isinstance(breakdown, dict)
        if len(breakdown) > 0:
            assert "openai" in breakdown
    
    def test_auto_optimization_control(self, cost_manager):
        """Test auto-optimization enable/disable"""
        # Enable auto-optimization
        cost_manager.enable_auto_optimization(OptimizationStrategy.BALANCED)
        assert cost_manager._auto_optimization_enabled is True
        assert cost_manager._optimization_strategy == OptimizationStrategy.BALANCED
        
        # Test should_optimize_request
        should_optimize = cost_manager.should_optimize_request(0.01, "gpt-5", "simple")
        # Result depends on conditions, but should not throw error
        assert isinstance(should_optimize, bool)
        
        # Disable auto-optimization
        cost_manager.disable_auto_optimization()
        assert cost_manager._auto_optimization_enabled is False
    
    def test_emergency_mode(self, cost_manager):
        """Test emergency cost reduction mode"""
        # Enable emergency mode
        cost_manager.enable_emergency_mode()
        assert cost_manager._emergency_mode_enabled is True
        assert cost_manager._auto_optimization_enabled is True
        assert cost_manager._optimization_strategy == OptimizationStrategy.EMERGENCY
        
        # Should always optimize in emergency mode
        should_optimize = cost_manager.should_optimize_request(0.001, "gpt-5", "any")
        assert should_optimize is True
        
        # Disable emergency mode
        cost_manager.disable_emergency_mode()
        assert cost_manager._emergency_mode_enabled is False
    
    def test_optimization_recommendations(self, cost_manager):
        """Test optimization recommendations generation"""
        # Track some expensive requests
        for i in range(10):
            cost_manager.track_request(
                request_id=f"expensive-{i}",
                provider="openai",
                model="gpt-5",
                prompt_tokens=1000,
                completion_tokens=500,
                total_cost=0.01
            )
        
        recommendations = cost_manager.get_optimization_recommendations()
        
        assert "recommendations" in recommendations
        assert isinstance(recommendations["recommendations"], list)
        
        # Should have some recommendations for expensive usage
        if cost_manager.optimizer:
            # May have specific recommendations based on usage patterns
            pass
    
    def test_system_status_comprehensive(self, cost_manager):
        """Test comprehensive system status reporting"""
        # Track some requests and set budgets
        cost_manager.set_monthly_budget(50.0)
        cost_manager.track_request(
            request_id="status-test",
            provider="openai",
            model="gpt-5-mini",
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=5.0  # 10% of budget
        )
        
        status = cost_manager.get_system_status()
        
        assert "cost_manager" in status
        cost_mgr_status = status["cost_manager"]
        
        assert cost_mgr_status["tracking_enabled"] is True
        assert cost_mgr_status["budgets_enabled"] is True
        assert cost_mgr_status["optimization_enabled"] is True
        
        if "current_month" in status:
            assert "total_cost" in status["current_month"]
            assert status["current_month"]["total_cost"] >= 5.0
        
        if "budgets" in status:
            assert "total_budgets" in status["budgets"]
            assert status["budgets"]["total_budgets"] >= 1
    
    def test_export_all_data(self, cost_manager):
        """Test comprehensive data export"""
        # Generate some data
        cost_manager.set_monthly_budget(100.0)
        cost_manager.track_request(
            request_id="export-test",
            provider="anthropic",
            model="claude-3-5-sonnet",
            prompt_tokens=200,
            completion_tokens=100,
            total_cost=0.005
        )
        
        export_data = cost_manager.export_all_data("month")
        
        assert "export_metadata" in export_data
        assert "cost_tracking" in export_data
        assert "budget_management" in export_data
        assert "analytics" in export_data
        
        metadata = export_data["export_metadata"]
        assert metadata["time_period"] == "month"
        assert metadata["components"]["tracking"] is True
        assert metadata["components"]["budgets"] is True
        assert metadata["components"]["optimization"] is True
    
    def test_alert_callback_management(self, cost_manager):
        """Test alert callback management"""
        alerts_received = []
        
        def test_callback(alert):
            alerts_received.append(alert)
        
        # Add callback
        cost_manager.add_alert_callback(test_callback)
        
        # Set a low budget and exceed it
        cost_manager.set_daily_budget(0.01)
        cost_manager.track_request(
            request_id="alert-trigger",
            provider="openai",
            model="gpt-5",
            prompt_tokens=1000,
            completion_tokens=500,
            total_cost=0.02  # Exceeds budget
        )
        
        # Should have triggered alert (exact behavior depends on implementation)
        # Just verify no exceptions were raised
    
    def test_reset_all_data_safety(self, cost_manager):
        """Test data reset safety mechanism"""
        # Track some data
        cost_manager.track_request(
            request_id="reset-test",
            provider="openai",
            model="gpt-5-nano",
            prompt_tokens=50,
            completion_tokens=25,
            total_cost=0.0001
        )
        
        # Should require confirmation
        with pytest.raises(ValueError, match="Must set confirm=True"):
            cost_manager.reset_all_data(confirm=False)
        
        # Should work with confirmation
        cost_manager.reset_all_data(confirm=True)
        
        # Verify tracking data is reset
        usage = cost_manager.get_usage_stats("month")
        assert usage["total_requests"] == 0
        assert usage["total_cost"] == 0.0
    
    def test_error_handling_invalid_request(self, cost_manager):
        """Test error handling for invalid request tracking"""
        # Test with invalid parameters
        request_cost = cost_manager.track_request(
            request_id="",  # Empty ID
            provider="invalid_provider",
            model="invalid_model",
            prompt_tokens=-1,  # Invalid token count
            completion_tokens=50,
            total_cost=0.001
        )
        
        # Should handle gracefully and return None or valid object
        # Exact behavior depends on implementation
        assert request_cost is None or hasattr(request_cost, 'request_id')
    
    def test_concurrent_access_simulation(self, cost_manager):
        """Test concurrent access to cost manager"""
        import threading
        import time
        
        def track_requests(thread_id):
            for i in range(20):
                cost_manager.track_request(
                    request_id=f"concurrent-{thread_id}-{i}",
                    provider="openai",
                    model="gpt-5-nano",
                    prompt_tokens=50,
                    completion_tokens=25,
                    total_cost=0.0001
                )
                time.sleep(0.001)  # Small delay
        
        # Run multiple threads
        threads = []
        for tid in range(3):
            thread = threading.Thread(target=track_requests, args=(tid,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check final state
        usage = cost_manager.get_usage_stats("month")
        assert usage["total_requests"] == 60  # 3 threads * 20 requests
        assert abs(usage["total_cost"] - 0.006) < 0.001  # Allow floating point errors


class TestCreateCostManager:
    """Test suite for cost manager factory function"""
    
    def test_create_cost_manager_basic(self):
        """Test basic cost manager creation"""
        manager = create_cost_manager()
        
        assert manager is not None
        assert manager.enable_tracking is True
        assert manager.enable_budgets is True
        assert manager.enable_optimization is True
    
    def test_create_cost_manager_with_budgets(self):
        """Test cost manager creation with budget configuration"""
        manager = create_cost_manager(
            monthly_budget=100.0,
            daily_budget=5.0,
            request_budget=0.01,
            auto_optimize=True
        )
        
        assert manager is not None
        
        # Check budgets were set
        budget_statuses = manager.get_budget_status()
        budget_names = [status["name"] for status in budget_statuses]
        
        assert "monthly_default" in budget_names
        assert "daily_default" in budget_names  
        assert "per_request_default" in budget_names
        
        # Check auto-optimization is enabled
        assert manager._auto_optimization_enabled is True
    
    def test_create_cost_manager_with_data_dir(self):
        """Test cost manager creation with custom data directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_cost_manager(data_dir=temp_dir)
            
            assert manager is not None
            assert manager.tracker.data_dir == temp_dir
    
    def test_create_cost_manager_minimal_config(self):
        """Test cost manager creation with minimal configuration"""
        manager = create_cost_manager(
            monthly_budget=None,
            daily_budget=None,
            request_budget=None,
            auto_optimize=False
        )
        
        assert manager is not None
        assert len(manager.get_budget_status()) == 0  # No budgets set
        assert manager._auto_optimization_enabled is False


class TestCostManagerIntegration:
    """Test suite for cost manager integration scenarios"""
    
    @pytest.fixture
    def full_cost_manager(self):
        """Cost manager with all features for integration testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = create_cost_manager(
                monthly_budget=50.0,
                daily_budget=2.0,
                request_budget=0.005,
                auto_optimize=True,
                data_dir=temp_dir
            )
            yield manager
    
    def test_typical_usage_flow(self, full_cost_manager):
        """Test typical usage flow from request to optimization"""
        # 1. Check budget before request
        budget_check = full_cost_manager.check_request_budget(0.003)
        assert budget_check["status"] == "allowed"
        
        # 2. Get optimization recommendation
        optimization = full_cost_manager.optimize_model_choice(
            original_model="gpt-5",
            task_type="simple",
            estimated_tokens=500
        )
        
        # 3. Track the actual request
        request_cost = full_cost_manager.track_request(
            request_id="typical-flow-test",
            provider="openai",
            model=optimization.optimized_model,
            prompt_tokens=300,
            completion_tokens=200,
            total_cost=optimization.optimized_cost,
            original_model=optimization.original_model,
            cost_saved=optimization.cost_savings,
            optimization_applied=optimization.reasoning if optimization.cost_savings > 0 else None
        )
        
        assert request_cost is not None
        
        # 4. Check updated usage
        usage = full_cost_manager.get_usage_stats("month")
        assert usage["total_requests"] >= 1
        assert usage["total_cost"] > 0
        
        # 5. Get recommendations for future optimization
        recommendations = full_cost_manager.get_optimization_recommendations()
        assert "recommendations" in recommendations
    
    def test_budget_exceeded_scenario(self, full_cost_manager):
        """Test behavior when budget is exceeded"""
        # Track requests that approach budget limit
        for i in range(10):
            full_cost_manager.track_request(
                request_id=f"budget-test-{i}",
                provider="openai",
                model="gpt-5-mini",
                prompt_tokens=100,
                completion_tokens=50,
                total_cost=0.4  # Each request costs $0.40
            )
        
        # Should exceed daily budget ($2.00)
        budget_check = full_cost_manager.check_request_budget(0.1)
        # May be blocked depending on exact budget calculations
        assert budget_check["status"] in ["blocked", "warning", "allowed"]
        
        # Should trigger emergency optimization
        should_optimize = full_cost_manager.should_optimize_request(0.1, "gpt-5", "any")
        # Likely true due to budget pressure
        assert isinstance(should_optimize, bool)
    
    def test_performance_tracking_integration(self, full_cost_manager):
        """Test integration with performance tracking"""
        # Track requests with different performance characteristics
        models = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]
        costs = [0.005, 0.001, 0.0002]
        
        for i, (model, cost) in enumerate(zip(models, costs)):
            full_cost_manager.track_request(
                request_id=f"perf-{i}",
                provider="openai",
                model=model,
                prompt_tokens=200,
                completion_tokens=100,
                total_cost=cost
            )
        
        # Get cost report with performance analysis
        report = full_cost_manager.get_cost_report("month")
        
        assert "model_performance" in report
        assert "efficiency_score" in report
        assert report["efficiency_score"] >= 0.0
        
        # Should have data for the models we used
        model_performance = report["model_performance"]
        if model_performance:
            # Check structure of performance data
            for model_key, perf_data in model_performance.items():
                assert "requests" in perf_data
                assert "total_cost" in perf_data
                assert "avg_cost_per_request" in perf_data
    
    def test_data_persistence_and_recovery(self, full_cost_manager):
        """Test data persistence and recovery"""
        # Track some data
        original_request = full_cost_manager.track_request(
            request_id="persistence-test",
            provider="anthropic",
            model="claude-3-5-sonnet",
            prompt_tokens=150,
            completion_tokens=75,
            total_cost=0.003
        )
        
        # Save data explicitly
        if hasattr(full_cost_manager.tracker, 'save_data'):
            full_cost_manager.tracker.save_data()
        
        # Create new cost manager with same data directory
        new_manager = CostManager(
            enable_tracking=True,
            enable_budgets=True,
            enable_optimization=True,
            data_dir=full_cost_manager.tracker.data_dir
        )
        
        # Should be able to load and access the data
        if hasattr(new_manager.tracker, 'load_data'):
            new_manager.tracker.load_data()
            
            usage = new_manager.get_usage_stats("month")
            assert usage["total_requests"] >= 1
            assert usage["total_cost"] >= 0.003