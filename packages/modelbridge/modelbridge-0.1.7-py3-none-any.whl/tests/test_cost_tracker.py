"""
Comprehensive tests for the cost tracking system
"""
import pytest
import pytest_asyncio
import time
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from modelbridge.cost.tracker import CostTracker, RequestCost, ProviderCosts


class TestCostTracker:
    """Test suite for CostTracker functionality"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def cost_tracker(self, temp_data_dir):
        """Create cost tracker with temporary data directory"""
        return CostTracker(persist_data=True, data_dir=temp_data_dir)
    
    @pytest.fixture
    def cost_tracker_no_persist(self):
        """Create cost tracker without persistence for speed"""
        return CostTracker(persist_data=False)
    
    def test_initialization(self, cost_tracker):
        """Test cost tracker initialization"""
        assert cost_tracker.persist_data is True
        assert cost_tracker._total_cost == 0.0
        assert cost_tracker._total_requests == 0
        assert cost_tracker._total_saved == 0.0
        assert len(cost_tracker._recent_requests) == 0
    
    def test_track_request_basic(self, cost_tracker_no_persist):
        """Test basic request tracking"""
        request_cost = cost_tracker_no_persist.track_request(
            request_id="test-123",
            provider="openai",
            model="gpt-5",
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=0.001
        )
        
        assert request_cost is not None
        assert request_cost.request_id == "test-123"
        assert request_cost.provider == "openai"
        assert request_cost.model == "gpt-5"
        assert request_cost.prompt_tokens == 100
        assert request_cost.completion_tokens == 50
        assert request_cost.total_tokens == 150
        assert request_cost.total_cost == 0.001
        assert request_cost.task_type == "general"
        
        # Check totals are updated
        assert cost_tracker_no_persist._total_cost == 0.001
        assert cost_tracker_no_persist._total_requests == 1
        
    def test_track_request_with_optimization(self, cost_tracker_no_persist):
        """Test request tracking with cost optimization"""
        request_cost = cost_tracker_no_persist.track_request(
            request_id="test-opt-123",
            provider="openai",
            model="gpt-5-nano",
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=0.0005,
            task_type="simple",
            optimization_applied="downgraded from gpt-5",
            original_model="gpt-5",
            cost_saved=0.0005
        )
        
        assert request_cost.optimization_applied == "downgraded from gpt-5"
        assert request_cost.original_model == "gpt-5"
        assert request_cost.cost_saved == 0.0005
        assert cost_tracker_no_persist._total_saved == 0.0005
    
    def test_get_current_usage_no_data(self, cost_tracker_no_persist):
        """Test getting current usage with no data"""
        usage = cost_tracker_no_persist.get_current_usage("month")
        
        assert usage["total_cost"] == 0.0
        assert usage["total_requests"] == 0
        assert usage["total_tokens"] == 0
        assert usage["total_saved"] == 0.0
    
    def test_get_current_usage_with_data(self, cost_tracker_no_persist):
        """Test getting current usage with tracked data"""
        # Track some requests
        for i in range(5):
            cost_tracker_no_persist.track_request(
                request_id=f"test-{i}",
                provider="openai",
                model="gpt-5",
                prompt_tokens=100,
                completion_tokens=50,
                total_cost=0.001,
                cost_saved=0.0001
            )
        
        usage = cost_tracker_no_persist.get_current_usage("month")
        
        assert usage["total_cost"] == 0.005
        assert usage["total_requests"] == 5
        assert usage["total_tokens"] == 750  # (100 + 50) * 5
        assert usage["total_saved"] == 0.0005
    
    def test_provider_breakdown(self, cost_tracker_no_persist):
        """Test provider cost breakdown"""
        # Track requests from different providers
        providers = ["openai", "anthropic", "google", "groq"]
        for i, provider in enumerate(providers):
            cost_tracker_no_persist.track_request(
                request_id=f"test-{provider}",
                provider=provider,
                model=f"{provider}-model",
                prompt_tokens=100,
                completion_tokens=50,
                total_cost=0.001 * (i + 1)
            )
        
        breakdown = cost_tracker_no_persist.get_provider_breakdown("month")
        
        assert len(breakdown) == 4
        assert "openai" in breakdown
        assert "anthropic" in breakdown
        
        openai_costs = breakdown["openai"]
        assert openai_costs.total_cost == 0.001
        assert openai_costs.total_requests == 1
        assert openai_costs.total_tokens == 150
        assert "openai-model" in openai_costs.cost_by_model
    
    def test_cost_trends_daily(self, cost_tracker_no_persist):
        """Test daily cost trend calculation"""
        # Track some requests
        cost_tracker_no_persist.track_request(
            request_id="test-day1",
            provider="openai", 
            model="gpt-5",
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=0.001
        )
        
        cost_tracker_no_persist.track_request(
            request_id="test-day2",
            provider="openai",
            model="gpt-5", 
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=0.002
        )
        
        trends = cost_tracker_no_persist.get_cost_trend("day", 2)
        assert len(trends) == 2
        
        # Check that we got some trend data (exact values depend on current time)
        assert isinstance(trends[0], tuple)
        assert len(trends[0]) == 2
        assert isinstance(trends[0][0], str)  # timestamp
        assert isinstance(trends[0][1], float)  # cost
    
    def test_persistence_save_load(self, cost_tracker):
        """Test data persistence to disk"""
        # Track some data
        cost_tracker.track_request(
            request_id="persist-test",
            provider="openai",
            model="gpt-5",
            prompt_tokens=100,
            completion_tokens=50, 
            total_cost=0.001
        )
        
        # Save data
        cost_tracker.save_data()
        
        # Create new tracker and load
        new_tracker = CostTracker(persist_data=True, data_dir=cost_tracker.data_dir)
        
        assert new_tracker._total_cost == 0.001
        assert new_tracker._total_requests == 1
        # Note: recent_requests are not persisted by default for memory efficiency
    
    def test_data_export_json(self, cost_tracker_no_persist):
        """Test data export in JSON format"""
        # Track some requests
        cost_tracker_no_persist.track_request(
            request_id="export-test",
            provider="openai",
            model="gpt-5",
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=0.001,
            task_type="coding"
        )
        
        exported_data = cost_tracker_no_persist.export_data("json", "month")
        
        assert "usage_summary" in exported_data
        assert "provider_breakdown" in exported_data
        assert "metadata" in exported_data
        
        # Check usage summary data
        summary = exported_data["usage_summary"]
        assert summary["total_cost"] == 0.001
        assert summary["total_requests"] == 1
        
        # Check metadata
        metadata = exported_data["metadata"]
        assert metadata["total_requests"] == 1
        assert metadata["total_cost"] == 0.001
    
    def test_recent_requests_limit(self):
        """Test that recent requests are limited to avoid memory issues"""
        # Create tracker with small limit
        tracker = CostTracker(persist_data=False, max_memory_entries=10)
        
        # Track many requests
        for i in range(15):  # More than the limit
            tracker.track_request(
                request_id=f"limit-test-{i}",
                provider="openai",
                model="gpt-5",
                prompt_tokens=10,
                completion_tokens=5,
                total_cost=0.0001
            )
        
        # Should be limited to max_memory_entries
        assert len(tracker._recent_requests) == 10
        
        # Should keep the most recent ones
        recent_ids = [req.request_id for req in tracker._recent_requests]
        assert "limit-test-14" in recent_ids  # Most recent
        assert "limit-test-4" not in recent_ids  # Should be dropped
    
    def test_invalid_time_period(self, cost_tracker_no_persist):
        """Test handling of invalid time periods"""
        usage = cost_tracker_no_persist.get_current_usage("invalid_period")
        
        # Should return empty usage for invalid period
        assert usage["total_cost"] == 0.0
        assert usage["total_requests"] == 0
    
    def test_thread_safety_simulation(self, cost_tracker_no_persist):
        """Test thread safety with concurrent access simulation"""
        import threading
        import time
        
        def track_requests():
            for i in range(10):
                cost_tracker_no_persist.track_request(
                    request_id=f"thread-{threading.current_thread().ident}-{i}",
                    provider="openai",
                    model="gpt-5",
                    prompt_tokens=10,
                    completion_tokens=5,
                    total_cost=0.0001
                )
                time.sleep(0.001)  # Small delay to simulate real usage
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=track_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check final state
        assert cost_tracker_no_persist._total_requests == 50  # 5 threads * 10 requests
        assert cost_tracker_no_persist._total_cost == 0.005   # 50 * 0.0001
        
    def test_reset_data(self, cost_tracker_no_persist):
        """Test data reset functionality"""
        # Track some data
        cost_tracker_no_persist.track_request(
            request_id="reset-test",
            provider="openai",
            model="gpt-5",
            prompt_tokens=100,
            completion_tokens=50,
            total_cost=0.001
        )
        
        # Verify data exists
        assert cost_tracker_no_persist._total_requests > 0
        
        # Reset data
        cost_tracker_no_persist.reset_data(confirm=True)
        
        # Verify data is reset
        assert cost_tracker_no_persist._total_cost == 0.0
        assert cost_tracker_no_persist._total_requests == 0
        assert cost_tracker_no_persist._total_saved == 0.0
        assert len(cost_tracker_no_persist._recent_requests) == 0
    
    def test_reset_data_requires_confirmation(self, cost_tracker_no_persist):
        """Test that reset requires confirmation"""
        with pytest.raises(ValueError, match="Must set confirm=True"):
            cost_tracker_no_persist.reset_data(confirm=False)


class TestRequestCost:
    """Test suite for RequestCost data class"""
    
    def test_request_cost_creation(self):
        """Test RequestCost object creation"""
        request_cost = RequestCost(
            request_id="test-123",
            timestamp=time.time(),
            provider="openai",
            model="gpt-5",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            input_cost=0.0003,
            output_cost=0.0007,
            total_cost=0.001,
            task_type="coding"
        )
        
        assert request_cost.request_id == "test-123"
        assert request_cost.provider == "openai"
        assert request_cost.total_tokens == 150
        assert request_cost.task_type == "coding"
    
    def test_request_cost_to_dict(self):
        """Test RequestCost to_dict conversion"""
        request_cost = RequestCost(
            request_id="test-dict",
            timestamp=1234567890.0,
            provider="anthropic",
            model="claude-3-5-sonnet",
            prompt_tokens=200,
            completion_tokens=100,
            total_tokens=300,
            input_cost=0.002,
            output_cost=0.003,
            total_cost=0.005,
            task_type="analysis"
        )
        
        cost_dict = request_cost.to_dict()
        
        assert cost_dict["request_id"] == "test-dict"
        assert cost_dict["provider"] == "anthropic"
        assert cost_dict["total_tokens"] == 300
        assert cost_dict["task_type"] == "analysis"
        assert cost_dict["timestamp"] == 1234567890.0


class TestProviderCosts:
    """Test suite for ProviderCosts data class"""
    
    def test_provider_costs_creation(self):
        """Test ProviderCosts object creation"""
        provider_costs = ProviderCosts(
            provider="openai",
            total_requests=100,
            total_cost=0.05,
            total_tokens=15000,
            average_cost_per_request=0.0005,
            average_cost_per_token=0.0000033,
            cost_by_model={},
            requests_by_model={}
        )
        
        assert provider_costs.provider == "openai"
        assert provider_costs.total_cost == 0.05
        assert provider_costs.total_requests == 100
        assert provider_costs.total_tokens == 15000
        assert provider_costs.cost_by_model == {}
    
    def test_provider_costs_with_model_breakdown(self):
        """Test ProviderCosts with model breakdown"""
        provider_costs = ProviderCosts(
            provider="openai",
            total_requests=100,
            total_cost=0.05,
            total_tokens=15000,
            average_cost_per_request=0.0005,
            average_cost_per_token=0.0000033,
            cost_by_model={
                "gpt-5": 0.03,
                "gpt-5-mini": 0.02
            },
            requests_by_model={
                "gpt-5": 60,
                "gpt-5-mini": 40
            }
        )
        
        assert len(provider_costs.cost_by_model) == 2
        assert provider_costs.cost_by_model["gpt-5"] == 0.03
        assert provider_costs.cost_by_model["gpt-5-mini"] == 0.02
        assert provider_costs.requests_by_model["gpt-5"] == 60
    
    def test_provider_costs_to_dict(self):
        """Test ProviderCosts to_dict conversion"""
        provider_costs = ProviderCosts(
            provider="google",
            total_requests=50,
            total_cost=0.01,
            total_tokens=5000,
            average_cost_per_request=0.0002,
            average_cost_per_token=0.000002,
            cost_by_model={"gemini-2.5-pro": 0.01},
            requests_by_model={"gemini-2.5-pro": 50}
        )
        
        costs_dict = provider_costs.to_dict()
        
        assert costs_dict["provider"] == "google"
        assert costs_dict["total_cost"] == 0.01
        assert costs_dict["cost_by_model"]["gemini-2.5-pro"] == 0.01