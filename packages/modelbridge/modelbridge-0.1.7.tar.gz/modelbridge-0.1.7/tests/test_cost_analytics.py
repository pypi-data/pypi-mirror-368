"""
Comprehensive tests for the cost analytics and reporting system
"""
import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from modelbridge.cost.analytics import (
    CostAnalytics, CostReport, UsageStats
)
from modelbridge.cost.tracker import CostTracker, RequestCost, ProviderCosts
from modelbridge.cost.budgets import BudgetManager, BudgetStatus, BudgetType


class TestCostAnalytics:
    """Test suite for CostAnalytics functionality"""
    
    @pytest.fixture
    def mock_cost_tracker(self):
        """Mock cost tracker with sample data"""
        tracker = Mock(spec=CostTracker)
        
        # Mock current usage data
        tracker.get_current_usage.return_value = {
            "total_cost": 15.50,
            "total_requests": 1000,
            "total_tokens": 150000,
            "total_saved": 2.25
        }
        
        # Mock provider breakdown
        tracker.get_provider_breakdown.return_value = {
            "openai": ProviderCosts(
                provider="openai",
                total_cost=10.0,
                total_requests=600,
                total_tokens=90000,
                cost_by_model={"gpt-5": 6.0, "gpt-5-mini": 4.0}
            ),
            "anthropic": ProviderCosts(
                provider="anthropic",
                total_cost=5.5,
                total_requests=400,
                total_tokens=60000,
                cost_by_model={"claude-3-5-sonnet": 5.5}
            )
        }
        
        # Mock cost trends
        base_time = time.time()
        tracker.get_cost_trend.return_value = [
            (f"2025-01-{i:02d}", i * 0.5) for i in range(1, 31)
        ]
        
        # Mock recent requests for analysis
        tracker._recent_requests = [
            RequestCost(
                request_id=f"req-{i}",
                timestamp=base_time - (i * 3600),
                provider="openai",
                model="gpt-5" if i % 2 == 0 else "gpt-5-mini",
                prompt_tokens=100 + (i * 10),
                completion_tokens=50 + (i * 5),
                total_cost=0.001 * (i + 1),
                task_type="coding" if i % 3 == 0 else "analysis",
                optimization_applied="downgrade" if i % 5 == 0 else None
            ) for i in range(20)
        ]
        
        return tracker
    
    @pytest.fixture
    def mock_budget_manager(self):
        """Mock budget manager with sample data"""
        manager = Mock(spec=BudgetManager)
        
        # Mock budget statuses
        manager.get_all_budget_status.return_value = [
            BudgetStatus(
                name="monthly_budget",
                budget_type=BudgetType.MONTHLY,
                limit=100.0,
                current_usage=65.0,
                remaining=35.0,
                usage_percentage=65.0,
                is_exceeded=False,
                time_remaining="15 days remaining",
                projected_usage=85.0,
                will_exceed=False
            )
        ]
        
        return manager
    
    @pytest.fixture
    def cost_analytics(self, mock_cost_tracker, mock_budget_manager):
        """Create cost analytics with mocked dependencies"""
        return CostAnalytics(
            cost_tracker=mock_cost_tracker,
            budget_manager=mock_budget_manager
        )
    
    @pytest.fixture
    def cost_analytics_no_tracker(self):
        """Create cost analytics without tracker for edge case testing"""
        return CostAnalytics(cost_tracker=None, budget_manager=None)
    
    def test_initialization(self, cost_analytics):
        """Test cost analytics initialization"""
        assert cost_analytics.cost_tracker is not None
        assert cost_analytics.budget_manager is not None
        assert len(cost_analytics.efficiency_baselines) > 0
        
        # Check some key efficiency baselines
        assert "gpt-5" in cost_analytics.efficiency_baselines
        assert "gpt-5-mini" in cost_analytics.efficiency_baselines
        assert "claude-opus-4-1" in cost_analytics.efficiency_baselines
    
    def test_generate_usage_stats_with_data(self, cost_analytics):
        """Test usage statistics generation with data"""
        stats = cost_analytics.generate_usage_stats("month")
        
        assert isinstance(stats, UsageStats)
        assert stats.total_cost == 15.50
        assert stats.total_requests == 1000
        assert stats.total_tokens == 150000
        assert stats.total_savings == 2.25
        
        # Check calculated averages
        assert stats.average_cost_per_request == 15.50 / 1000
        assert stats.average_cost_per_token == 15.50 / 150000
        assert stats.average_tokens_per_request == 150000 / 1000
        
        # Check lists are populated
        assert len(stats.top_models) > 0
        assert len(stats.top_tasks) > 0
    
    def test_generate_usage_stats_no_tracker(self, cost_analytics_no_tracker):
        """Test usage statistics generation without tracker"""
        stats = cost_analytics_no_tracker.generate_usage_stats("month")
        
        assert isinstance(stats, UsageStats)
        assert stats.total_cost == 0.0
        assert stats.total_requests == 0
        assert stats.total_tokens == 0
        assert stats.cost_trend == "unknown"
        assert len(stats.top_models) == 0
        assert len(stats.top_tasks) == 0
    
    def test_cost_trend_analysis_increasing(self, cost_analytics):
        """Test cost trend analysis for increasing trend"""
        # Mock trend with increasing costs
        increasing_trend = [(f"day-{i}", i * 2.0) for i in range(10)]
        cost_analytics.cost_tracker.get_cost_trend.return_value = increasing_trend
        
        trend = cost_analytics._analyze_cost_trend("month")
        assert trend == "increasing"
    
    def test_cost_trend_analysis_decreasing(self, cost_analytics):
        """Test cost trend analysis for decreasing trend"""
        # Mock trend with decreasing costs
        decreasing_trend = [(f"day-{i}", 20.0 - (i * 2.0)) for i in range(10)]
        cost_analytics.cost_tracker.get_cost_trend.return_value = decreasing_trend
        
        trend = cost_analytics._analyze_cost_trend("month")
        assert trend == "decreasing"
    
    def test_cost_trend_analysis_stable(self, cost_analytics):
        """Test cost trend analysis for stable trend"""
        # Mock trend with stable costs
        stable_trend = [(f"day-{i}", 10.0 + (i * 0.1)) for i in range(10)]
        cost_analytics.cost_tracker.get_cost_trend.return_value = stable_trend
        
        trend = cost_analytics._analyze_cost_trend("month")
        assert trend == "stable"
    
    def test_top_models_by_cost(self, cost_analytics):
        """Test top models by cost extraction"""
        provider_breakdown = {
            "openai": Mock(cost_by_model={"gpt-5": 10.0, "gpt-5-mini": 5.0}),
            "anthropic": Mock(cost_by_model={"claude-opus-4-1": 15.0})
        }
        
        top_models = cost_analytics._get_top_models_by_cost(provider_breakdown)
        
        assert len(top_models) <= 5  # Should be limited to top 5
        assert isinstance(top_models, list)
        
        # Should be sorted by cost (highest first)
        for i in range(len(top_models) - 1):
            assert top_models[i][1] >= top_models[i + 1][1]
    
    def test_top_tasks_by_cost(self, cost_analytics):
        """Test top tasks by cost extraction"""
        top_tasks = cost_analytics._get_top_tasks_by_cost("month")
        
        assert isinstance(top_tasks, list)
        assert len(top_tasks) <= 5  # Should be limited to top 5
        
        # Check format
        for task_name, cost in top_tasks:
            assert isinstance(task_name, str)
            assert isinstance(cost, (int, float))
    
    def test_find_peak_usage_hour(self, cost_analytics):
        """Test peak usage hour detection"""
        # Mock hourly data
        hourly_data = [(f"2025-01-15-{i:02d}", i * 2.0) for i in range(24)]
        cost_analytics.cost_tracker.get_cost_trend.return_value = hourly_data
        
        with patch('datetime.strptime') as mock_strptime:
            mock_strptime.return_value = datetime(2025, 1, 15, 23, 0, 0)  # 11 PM
            
            peak_hour = cost_analytics._find_peak_usage_hour()
            
            assert peak_hour is not None
            assert "PM" in peak_hour or "AM" in peak_hour
    
    def test_optimization_rate_calculation(self, cost_analytics):
        """Test optimization rate calculation"""
        # Should calculate based on requests with optimization_applied
        rate = cost_analytics._calculate_optimization_rate("month")
        
        assert isinstance(rate, float)
        assert 0.0 <= rate <= 100.0
        
        # With our mock data, 4 out of 20 requests have optimization (every 5th)
        expected_rate = (4 / 20) * 100  # 20%
        assert abs(rate - expected_rate) < 1.0  # Allow small floating point errors
    
    def test_provider_performance_analysis(self, cost_analytics):
        """Test provider performance analysis"""
        analysis = cost_analytics._analyze_provider_performance("month")
        
        assert "openai" in analysis
        assert "anthropic" in analysis
        
        openai_analysis = analysis["openai"]
        assert "cost_efficiency" in openai_analysis
        assert "model_diversity" in openai_analysis
        assert "performance_rating" in openai_analysis
        
        # Check performance rating values
        assert openai_analysis["performance_rating"] in ["excellent", "good", "fair", "expensive"]
    
    def test_model_performance_analysis(self, cost_analytics):
        """Test individual model performance analysis"""
        analysis = cost_analytics._analyze_model_performance("month")
        
        assert isinstance(analysis, dict)
        
        # Should have model entries based on mock data
        for model_key, performance in analysis.items():
            assert ":" in model_key  # Should be "provider:model" format
            assert "requests" in performance
            assert "total_cost" in performance
            assert "avg_cost_per_request" in performance
            assert "efficiency_score" in performance
            assert 0.0 <= performance["efficiency_score"] <= 100.0
    
    def test_model_efficiency_score_calculation(self, cost_analytics):
        """Test model efficiency score calculation"""
        # Test with known model
        score = cost_analytics._calculate_model_efficiency_score("gpt-5", 0.001, 1.0)
        assert 0.0 <= score <= 100.0
        
        # Test with unknown model (should return neutral score)
        unknown_score = cost_analytics._calculate_model_efficiency_score("unknown-model", 0.001, 1.0)
        assert unknown_score == 50.0
        
        # Test with zero cost (should return perfect score)
        zero_cost_score = cost_analytics._calculate_model_efficiency_score("gpt-5", 0.0, 1.0)
        assert zero_cost_score == 100.0
    
    def test_generate_recommendations_increasing_trend(self, cost_analytics):
        """Test recommendations with increasing cost trend"""
        # Mock stats with increasing trend
        mock_stats = Mock()
        mock_stats.cost_trend = "increasing"
        mock_stats.optimization_rate = 10.0  # Low optimization
        mock_stats.average_cost_per_request = 0.05  # High cost
        mock_stats.peak_usage_hour = "02 PM"
        
        recommendations = cost_analytics._generate_recommendations(
            mock_stats, {}, {}
        )
        
        assert len(recommendations) > 0
        assert any("trending upward" in rec for rec in recommendations)
        assert any("optimization" in rec.lower() for rec in recommendations)
        assert any("02 PM" in rec for rec in recommendations)
    
    def test_generate_recommendations_expensive_models(self, cost_analytics):
        """Test recommendations with expensive models"""
        mock_stats = Mock()
        mock_stats.cost_trend = "stable"
        mock_stats.optimization_rate = 50.0
        mock_stats.average_cost_per_request = 0.01
        mock_stats.peak_usage_hour = None
        
        # Mock expensive model performance
        expensive_model_performance = {
            "openai:gpt-5": {
                "avg_cost_per_request": 0.03,
                "cost_share": 60.0
            }
        }
        
        recommendations = cost_analytics._generate_recommendations(
            mock_stats, {}, expensive_model_performance
        )
        
        assert any("gpt-5" in rec for rec in recommendations)
        assert any("high cost per request" in rec for rec in recommendations)
    
    def test_generate_recommendations_budget_warnings(self, cost_analytics):
        """Test recommendations with budget warnings"""
        mock_stats = Mock()
        mock_stats.cost_trend = "stable"
        mock_stats.optimization_rate = 30.0
        mock_stats.average_cost_per_request = 0.01
        mock_stats.peak_usage_hour = None
        
        # Mock budget manager with high usage
        budget_status = Mock()
        budget_status.name = "monthly_budget"
        budget_status.usage_percentage = 85.0
        cost_analytics.budget_manager.get_all_budget_status.return_value = [budget_status]
        
        recommendations = cost_analytics._generate_recommendations(
            mock_stats, {}, {}
        )
        
        assert any("Budget" in rec and "85.0%" in rec for rec in recommendations)
    
    def test_calculate_potential_savings(self, cost_analytics):
        """Test potential savings calculation"""
        savings = cost_analytics._calculate_potential_savings("month")
        
        assert isinstance(savings, float)
        assert savings >= 0.0
        
        # Should calculate based on expensive model usage for simple tasks
        # Our mock has gpt-5 requests marked as simple tasks (when i % 3 != 0)
    
    def test_calculate_efficiency_score(self, cost_analytics):
        """Test overall efficiency score calculation"""
        mock_stats = Mock()
        mock_stats.optimization_rate = 25.0  # 25%
        mock_stats.cost_trend = "stable"
        mock_stats.total_savings = 2.0
        mock_stats.total_cost = 10.0
        
        mock_model_performance = {
            "model1": {"efficiency_score": 70.0},
            "model2": {"efficiency_score": 80.0}
        }
        
        score = cost_analytics._calculate_efficiency_score(mock_stats, mock_model_performance)
        
        assert 0.0 <= score <= 100.0
        assert score > 50.0  # Should be above base with these positive factors
    
    def test_generate_detailed_report(self, cost_analytics):
        """Test comprehensive detailed report generation"""
        report = cost_analytics.generate_detailed_report("month")
        
        assert isinstance(report, CostReport)
        assert report.period == "month"
        assert report.start_date is not None
        assert report.end_date is not None
        assert isinstance(report.summary, UsageStats)
        assert isinstance(report.provider_breakdown, dict)
        assert isinstance(report.model_performance, dict)
        assert isinstance(report.cost_trends, list)
        assert isinstance(report.recommendations, list)
        assert isinstance(report.potential_savings, float)
        assert 0.0 <= report.efficiency_score <= 100.0
        assert report.generated_at is not None
    
    def test_export_analytics_data(self, cost_analytics):
        """Test analytics data export"""
        export_data = cost_analytics.export_analytics_data("month", "json")
        
        assert "analytics_export" in export_data
        export_info = export_data["analytics_export"]
        
        assert export_info["format"] == "json"
        assert export_info["time_period"] == "month"
        assert "exported_at" in export_info
        assert "report" in export_info
    
    def test_get_period_cutoff(self, cost_analytics):
        """Test time period cutoff calculations"""
        now = time.time()
        
        with patch('time.time', return_value=now):
            hour_cutoff = cost_analytics._get_period_cutoff("hour")
            assert hour_cutoff == now - 3600
            
            day_cutoff = cost_analytics._get_period_cutoff("day")
            assert day_cutoff == now - 86400
            
            week_cutoff = cost_analytics._get_period_cutoff("week")
            assert week_cutoff == now - (7 * 86400)
            
            month_cutoff = cost_analytics._get_period_cutoff("month")
            assert month_cutoff == now - (30 * 86400)
            
            invalid_cutoff = cost_analytics._get_period_cutoff("invalid")
            assert invalid_cutoff == 0
    
    def test_edge_cases_insufficient_data(self, cost_analytics):
        """Test handling of insufficient data scenarios"""
        # Mock empty data
        cost_analytics.cost_tracker.get_cost_trend.return_value = []
        cost_analytics.cost_tracker._recent_requests = []
        
        stats = cost_analytics.generate_usage_stats("month")
        
        # Should handle gracefully
        assert stats.cost_trend in ["insufficient_data", "unknown"]
        assert stats.peak_usage_hour is None
        assert stats.most_expensive_request is None
        assert stats.optimization_rate == 0.0
    
    def test_thread_safety_simulation(self, cost_analytics):
        """Test thread safety during analytics generation"""
        import threading
        import time
        
        results = []
        
        def generate_stats():
            try:
                stats = cost_analytics.generate_usage_stats("month")
                results.append(stats)
            except Exception as e:
                results.append(e)
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_stats)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check all succeeded
        assert len(results) == 5
        for result in results:
            assert isinstance(result, UsageStats)
            assert result.total_cost == 15.50  # Should be consistent


class TestUsageStats:
    """Test suite for UsageStats data class"""
    
    def test_usage_stats_creation(self):
        """Test UsageStats creation"""
        stats = UsageStats(
            total_requests=1000,
            total_cost=25.50,
            total_tokens=150000,
            average_cost_per_request=0.0255,
            average_cost_per_token=0.00017,
            average_tokens_per_request=150.0,
            cost_trend="increasing",
            top_models=[("openai:gpt-5", 15.0), ("anthropic:claude-3-5-sonnet", 10.5)],
            top_tasks=[("coding", 12.0), ("analysis", 8.5)],
            peak_usage_hour="02 PM",
            most_expensive_request=0.05,
            total_savings=3.25,
            optimization_rate=35.5
        )
        
        assert stats.total_requests == 1000
        assert stats.total_cost == 25.50
        assert stats.cost_trend == "increasing"
        assert len(stats.top_models) == 2
        assert len(stats.top_tasks) == 2
        assert stats.optimization_rate == 35.5


class TestCostReport:
    """Test suite for CostReport data class"""
    
    def test_cost_report_creation(self):
        """Test CostReport creation"""
        mock_stats = UsageStats(
            total_requests=500,
            total_cost=12.75,
            total_tokens=75000,
            average_cost_per_request=0.0255,
            average_cost_per_token=0.00017,
            average_tokens_per_request=150.0,
            cost_trend="stable",
            top_models=[],
            top_tasks=[],
            peak_usage_hour=None,
            most_expensive_request=None,
            total_savings=1.5,
            optimization_rate=20.0
        )
        
        report = CostReport(
            period="week",
            start_date="2025-01-08T00:00:00",
            end_date="2025-01-15T00:00:00",
            summary=mock_stats,
            provider_breakdown={"openai": {"total_cost": 12.75}},
            model_performance={"openai:gpt-5": {"requests": 500}},
            cost_trends=[("2025-01-08", 1.5), ("2025-01-09", 2.0)],
            recommendations=["Consider cost optimization"],
            potential_savings=2.5,
            efficiency_score=75.0,
            generated_at="2025-01-15T12:00:00"
        )
        
        assert report.period == "week"
        assert report.summary.total_cost == 12.75
        assert report.efficiency_score == 75.0
        assert len(report.recommendations) == 1
        assert report.potential_savings == 2.5