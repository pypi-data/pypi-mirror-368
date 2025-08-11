"""
Comprehensive tests for ModelBridge integration with cost management
"""
import pytest
import pytest_asyncio
import time
import tempfile
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from modelbridge import ModelBridge
from modelbridge.providers.base import GenerationRequest, GenerationResponse, ModelMetadata
from modelbridge.cost.optimizer import OptimizationStrategy


class TestModelBridgeCostIntegration:
    """Test suite for ModelBridge cost management integration"""
    
    @pytest_asyncio.fixture
    async def mock_provider(self):
        """Mock provider for testing"""
        provider = Mock()
        provider.initialize = AsyncMock(return_value=True)
        provider.health_check = AsyncMock(return_value={"status": "healthy"})
        provider.supports_capability = Mock(return_value=True)
        
        # Mock generate_text method
        async def mock_generate_text(request, model_id):
            return GenerationResponse(
                content="Mock response content",
                model_id=model_id,
                provider_name="mock_provider",
                metadata=ModelMetadata(
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    response_time=0.5
                ),
                cost=0.001,
                prompt_tokens=100,
                completion_tokens=50
            )
        
        provider.generate_text = mock_generate_text
        provider.generate_structured_output = mock_generate_text
        
        return provider
    
    @pytest_asyncio.fixture
    async def bridge_with_mock_provider(self, mock_provider):
        """ModelBridge with mocked provider"""
        bridge = ModelBridge()
        bridge._initialized = True
        bridge.providers = {"mock_provider": mock_provider}
        
        # Override model aliases to use mock provider
        bridge.model_aliases = {
            "balanced": [
                bridge.ModelAlias("balanced", "mock_provider", "mock-model", 1)
            ],
            "fastest": [
                bridge.ModelAlias("fastest", "mock_provider", "fast-model", 1)
            ],
            "cheapest": [
                bridge.ModelAlias("cheapest", "mock_provider", "cheap-model", 1)
            ]
        }
        
        yield bridge
    
    def test_cost_manager_initialization(self, bridge_with_mock_provider):
        """Test that cost manager is properly initialized"""
        bridge = bridge_with_mock_provider
        
        assert bridge.cost_manager is not None
        assert bridge.cost_manager.enable_tracking is True
        assert bridge.cost_manager.enable_budgets is True
        assert bridge.cost_manager.enable_optimization is True
    
    @pytest.mark.asyncio
    async def test_smart_routing_without_model(self, bridge_with_mock_provider):
        """Test smart routing when no model is specified"""
        bridge = bridge_with_mock_provider
        
        response = await bridge.generate_text(
            prompt="Write a Python function to calculate fibonacci numbers"
            # No model specified - should use smart routing
        )
        
        assert response is not None
        assert response.content == "Mock response content"
        assert response.error is None
        
        # Should have smart routing analysis in metadata
        if hasattr(response, 'extra_params') and response.extra_params:
            assert '_smart_routing_analysis' in response.extra_params
            analysis = response.extra_params['_smart_routing_analysis']
            assert 'task_type' in analysis
            assert 'complexity_score' in analysis
    
    @pytest.mark.asyncio
    async def test_cost_optimization_integration(self, bridge_with_mock_provider):
        """Test cost optimization integration in routing"""
        bridge = bridge_with_mock_provider
        
        # Enable auto-optimization
        bridge.enable_cost_optimization("aggressive")
        
        response = await bridge.generate_text(
            prompt="Simple translation task"  # Should trigger optimization
        )
        
        assert response is not None
        
        # Check if optimization was applied
        if hasattr(response, 'extra_params') and response.extra_params:
            if '_cost_optimization' in response.extra_params:
                optimization = response.extra_params['_cost_optimization']
                assert 'original_model' in optimization
                assert 'cost_savings' in optimization
                assert 'reasoning' in optimization
    
    @pytest.mark.asyncio
    async def test_budget_enforcement(self, bridge_with_mock_provider):
        """Test budget enforcement blocking expensive requests"""
        bridge = bridge_with_mock_provider
        
        # Set very low budget
        bridge.set_request_budget(0.0001)
        
        # Mock the cost check to block request
        with patch.object(bridge.cost_manager, 'check_request_budget') as mock_check:
            mock_check.return_value = {
                'status': 'blocked',
                'violations': [{'message': 'Request exceeds budget'}]
            }
            
            response = await bridge.generate_text(
                prompt="Expensive request that should be blocked"
            )
            
            # Should be blocked by budget
            assert response.error is not None
            assert "budget" in response.error.lower()
    
    @pytest.mark.asyncio
    async def test_cost_tracking_on_request(self, bridge_with_mock_provider):
        """Test that costs are tracked for each request"""
        bridge = bridge_with_mock_provider
        
        # Mock cost tracker to verify tracking calls
        with patch.object(bridge.cost_manager, 'track_request') as mock_track:
            mock_track.return_value = Mock()  # Mock RequestCost object
            
            await bridge.generate_text(
                prompt="Test request for cost tracking",
                model="balanced"
            )
            
            # Should have tracked the request
            mock_track.assert_called_once()
            args, kwargs = mock_track.call_args
            
            assert kwargs['provider'] == 'mock_provider'
            assert kwargs['model'] == 'mock-model'
            assert kwargs['total_cost'] == 0.001
            assert kwargs['prompt_tokens'] == 100
            assert kwargs['completion_tokens'] == 50
    
    @pytest.mark.asyncio
    async def test_structured_output_cost_optimization(self, bridge_with_mock_provider):
        """Test cost optimization for structured output"""
        bridge = bridge_with_mock_provider
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        
        response = await bridge.generate_structured_output(
            prompt="Extract name and age from: John Doe, 30 years old",
            schema=schema
            # Should use smart routing with quality preference for structured output
        )
        
        assert response is not None
        assert response.error is None
    
    def test_budget_convenience_methods(self, bridge_with_mock_provider):
        """Test budget management convenience methods"""
        bridge = bridge_with_mock_provider
        
        # Test setting budgets
        assert bridge.set_monthly_budget(100.0) is True
        assert bridge.set_daily_budget(5.0) is True
        assert bridge.set_request_budget(0.01) is True
        
        # Test getting budget status
        budget_status = bridge.get_budget_status()
        assert isinstance(budget_status, list)
        assert len(budget_status) == 3  # Should have 3 budgets
    
    def test_cost_reporting_methods(self, bridge_with_mock_provider):
        """Test cost reporting convenience methods"""
        bridge = bridge_with_mock_provider
        
        # Test usage stats
        usage_stats = bridge.get_cost_usage_stats("month")
        assert isinstance(usage_stats, dict)
        assert "total_requests" in usage_stats
        assert "total_cost" in usage_stats
        
        # Test cost report
        cost_report = bridge.get_cost_report("week")
        assert isinstance(cost_report, dict)
        assert "period" in cost_report
        assert "summary" in cost_report
    
    def test_optimization_control_methods(self, bridge_with_mock_provider):
        """Test optimization control methods"""
        bridge = bridge_with_mock_provider
        
        # Test enabling optimization
        bridge.enable_cost_optimization("balanced")
        assert bridge.cost_manager._auto_optimization_enabled is True
        
        # Test disabling optimization
        bridge.disable_cost_optimization()
        assert bridge.cost_manager._auto_optimization_enabled is False
        
        # Test emergency mode
        bridge.enable_emergency_mode()
        assert bridge.cost_manager._emergency_mode_enabled is True
    
    def test_system_status_with_cost_management(self, bridge_with_mock_provider):
        """Test system status includes cost management information"""
        bridge = bridge_with_mock_provider
        
        # Set up some cost management state
        bridge.set_monthly_budget(50.0)
        
        system_status = bridge.get_system_status()
        
        assert "providers" in system_status
        assert "total_providers" in system_status
        assert "cost_management" in system_status
        
        cost_mgmt_status = system_status["cost_management"]
        assert "cost_manager" in cost_mgmt_status
        assert cost_mgmt_status["cost_manager"]["tracking_enabled"] is True
        assert cost_mgmt_status["cost_manager"]["budgets_enabled"] is True
    
    def test_optimization_recommendations(self, bridge_with_mock_provider):
        """Test getting optimization recommendations"""
        bridge = bridge_with_mock_provider
        
        recommendations = bridge.get_optimization_recommendations()
        
        assert isinstance(recommendations, dict)
        assert "recommendations" in recommendations
    
    @pytest.mark.asyncio
    async def test_cost_aware_routing_with_max_cost(self, bridge_with_mock_provider):
        """Test cost-aware routing with max cost parameter"""
        bridge = bridge_with_mock_provider
        
        # Mock the optimizer to return a cheaper model
        with patch.object(bridge.cost_manager, 'optimize_model_choice') as mock_optimize:
            mock_optimize.return_value = Mock(
                confidence=0.8,
                optimized_model="cheap-model",
                original_model="expensive-model",
                cost_savings=0.005,
                reasoning="Downgraded for cost savings"
            )
            
            response = await bridge.generate_text(
                prompt="Simple task with cost constraint",
                max_cost=0.001  # Low cost constraint
            )
            
            assert response is not None
            mock_optimize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_with_cost_tracking(self, bridge_with_mock_provider):
        """Test error handling doesn't break cost tracking"""
        bridge = bridge_with_mock_provider
        
        # Make provider return error
        async def mock_error_generate(request, model_id):
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name="mock_provider",
                error="Mock error for testing"
            )
        
        bridge.providers["mock_provider"].generate_text = mock_error_generate
        
        # Should handle error gracefully
        response = await bridge.generate_text(prompt="Test error handling")
        
        assert response.error is not None
        assert "Mock error for testing" in response.error
    
    @pytest.mark.asyncio
    async def test_performance_tracking_integration(self, bridge_with_mock_provider):
        """Test performance tracking integration with cost management"""
        bridge = bridge_with_mock_provider
        
        # Make several requests to build performance history
        for i in range(3):
            await bridge.generate_text(
                prompt=f"Test request {i}",
                model="balanced"
            )
        
        # Check performance stats
        perf_stats = bridge.get_performance_stats()
        assert isinstance(perf_stats, dict)
        
        # Should have stats for our mock provider
        if perf_stats:
            for provider_model, stats in perf_stats.items():
                assert "avg_response_time" in stats
                assert "avg_cost" in stats
                assert "success_rate" in stats
    
    @pytest.mark.asyncio
    async def test_intelligent_routing_integration(self, bridge_with_mock_provider):
        """Test intelligent routing with cost management"""
        bridge = bridge_with_mock_provider
        
        # Different types of prompts should route differently
        test_cases = [
            ("Write a Python function", "coding"),
            ("Hello, how are you?", "conversation"),
            ("Analyze market trends", "analysis")
        ]
        
        for prompt, expected_task in test_cases:
            response = await bridge.generate_text(prompt=prompt)
            
            assert response is not None
            assert response.error is None
            
            # Check if task analysis was performed
            if hasattr(response, 'extra_params') and response.extra_params:
                if '_smart_routing_analysis' in response.extra_params:
                    analysis = response.extra_params['_smart_routing_analysis']
                    # Task type detection may not be perfect, so we just check it's present
                    assert 'task_type' in analysis
    
    def test_cost_management_persistence(self):
        """Test cost management data persistence"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create bridge with persistent cost management
            bridge = ModelBridge()
            bridge.cost_manager = bridge.cost_manager.__class__(
                enable_tracking=True,
                enable_budgets=True,
                enable_optimization=True,
                data_dir=temp_dir
            )
            
            # Set some configuration
            bridge.set_monthly_budget(100.0)
            
            # Should be able to access the data
            budget_status = bridge.get_budget_status()
            assert len(budget_status) >= 1


class TestModelBridgeEdgeCases:
    """Test edge cases in ModelBridge cost integration"""
    
    @pytest_asyncio.fixture
    async def minimal_bridge(self):
        """ModelBridge with minimal setup"""
        bridge = ModelBridge()
        bridge._initialized = True
        bridge.providers = {}  # No providers
        yield bridge
    
    def test_cost_methods_with_no_providers(self, minimal_bridge):
        """Test cost management methods work even with no providers"""
        bridge = minimal_bridge
        
        # Should not crash even with no providers
        usage_stats = bridge.get_cost_usage_stats("month")
        assert isinstance(usage_stats, dict)
        
        cost_report = bridge.get_cost_report("week")
        assert isinstance(cost_report, dict)
        
        system_status = bridge.get_system_status()
        assert isinstance(system_status, dict)
    
    def test_cost_management_disabled_scenarios(self):
        """Test scenarios where cost management is disabled"""
        # Create bridge with cost management disabled
        bridge = ModelBridge()
        bridge.cost_manager = None
        
        # Methods should handle gracefully
        assert bridge.set_monthly_budget(100.0) is False
        assert bridge.set_daily_budget(5.0) is False
        assert len(bridge.get_budget_status()) == 0
        
        usage_stats = bridge.get_cost_usage_stats()
        assert "error" in usage_stats
        
        recommendations = bridge.get_optimization_recommendations()
        assert "Cost management not enabled" in recommendations["recommendations"][0]
    
    @pytest.mark.asyncio
    async def test_routing_with_no_cost_manager(self, minimal_bridge):
        """Test routing works even without cost manager"""
        bridge = minimal_bridge
        bridge.cost_manager = None
        
        # Add a mock provider
        mock_provider = Mock()
        mock_provider.initialize = AsyncMock(return_value=True)
        
        async def mock_generate(request, model_id):
            return GenerationResponse(
                content="Response without cost management",
                model_id=model_id,
                provider_name="test_provider"
            )
        
        mock_provider.generate_text = mock_generate
        bridge.providers = {"test_provider": mock_provider}
        bridge.model_aliases = {
            "balanced": [bridge.ModelAlias("balanced", "test_provider", "test-model", 1)]
        }
        
        # Should work without cost management
        response = await bridge.generate_text(
            prompt="Test without cost management",
            model="balanced"
        )
        
        assert response is not None
        assert response.content == "Response without cost management"
    
    def test_invalid_optimization_strategy(self):
        """Test handling of invalid optimization strategy"""
        bridge = ModelBridge()
        
        # Should handle invalid strategy gracefully
        bridge.enable_cost_optimization("invalid_strategy")
        
        # Should fall back to balanced strategy
        assert bridge.cost_manager._optimization_strategy is not None
    
    def test_concurrent_cost_operations(self):
        """Test thread safety of cost operations"""
        import threading
        import time
        
        bridge = ModelBridge()
        results = []
        
        def set_budgets(thread_id):
            try:
                success = bridge.set_monthly_budget(100.0 + thread_id)
                results.append(('budget', thread_id, success))
                
                usage = bridge.get_cost_usage_stats("month")
                results.append(('usage', thread_id, len(usage) > 0))
            except Exception as e:
                results.append(('error', thread_id, str(e)))
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=set_budgets, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent operations without errors
        error_results = [r for r in results if r[0] == 'error']
        assert len(error_results) == 0, f"Concurrent errors: {error_results}"
        
        # Should have some successful operations
        assert len(results) > 0


class TestModelBridgeRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    @pytest_asyncio.fixture
    async def configured_bridge(self):
        """Fully configured bridge for real-world testing"""
        bridge = ModelBridge()
        bridge._initialized = True
        
        # Mock multiple providers
        providers = {}
        for provider_name in ["openai", "anthropic", "groq"]:
            provider = Mock()
            provider.initialize = AsyncMock(return_value=True)
            provider.health_check = AsyncMock(return_value={"status": "healthy"})
            provider.supports_capability = Mock(return_value=True)
            
            async def make_generator(pname):
                async def mock_generate(request, model_id):
                    # Simulate different costs for different providers/models
                    cost_map = {
                        "openai": {"gpt-5": 0.01, "gpt-5-mini": 0.002, "gpt-5-nano": 0.0002},
                        "anthropic": {"claude-opus-4-1": 0.015, "claude-3-5-sonnet": 0.003},
                        "groq": {"llama-3.3-70b-versatile": 0.0006, "mixtral-8x7b-32768": 0.0003}
                    }
                    
                    cost = cost_map.get(pname, {}).get(model_id, 0.001)
                    
                    return GenerationResponse(
                        content=f"Response from {pname}:{model_id}",
                        model_id=model_id,
                        provider_name=pname,
                        metadata=ModelMetadata(
                            prompt_tokens=100,
                            completion_tokens=50,
                            total_tokens=150,
                            response_time=0.5
                        ),
                        cost=cost,
                        prompt_tokens=100,
                        completion_tokens=50
                    )
                return mock_generate
            
            provider.generate_text = await make_generator(provider_name)
            provider.generate_structured_output = await make_generator(provider_name)
            providers[provider_name] = provider
        
        bridge.providers = providers
        yield bridge
    
    @pytest.mark.asyncio
    async def test_cost_conscious_development_workflow(self, configured_bridge):
        """Test a cost-conscious development workflow"""
        bridge = configured_bridge
        
        # Set up budget constraints
        bridge.set_monthly_budget(10.0)  # $10 monthly budget
        bridge.set_daily_budget(1.0)    # $1 daily budget
        bridge.enable_cost_optimization("balanced")
        
        # Simulate various development tasks
        tasks = [
            ("Write a simple hello world function", "simple", "gpt-5-nano"),
            ("Debug this complex algorithm", "coding", "gpt-5"),
            ("Analyze performance metrics", "analysis", "claude-3-5-sonnet"),
            ("Quick question about syntax", "conversation", "mixtral-8x7b-32768")
        ]
        
        total_cost = 0.0
        
        for prompt, task_type, expected_model_type in tasks:
            response = await bridge.generate_text(prompt=prompt)
            
            assert response is not None
            assert response.error is None
            
            if response.cost:
                total_cost += response.cost
                
                # Cost should be reasonable for task complexity
                if "simple" in prompt or "quick" in prompt:
                    assert response.cost < 0.005, f"Simple task too expensive: ${response.cost}"
                elif "complex" in prompt:
                    assert response.cost >= 0.001, f"Complex task unexpectedly cheap: ${response.cost}"
        
        # Total cost should be within reasonable bounds
        assert total_cost < 1.0, f"Total cost too high: ${total_cost}"
        
        # Check usage statistics
        usage_stats = bridge.get_cost_usage_stats("month")
        assert usage_stats["total_cost"] == total_cost
        assert usage_stats["total_requests"] == len(tasks)
    
    @pytest.mark.asyncio
    async def test_emergency_cost_reduction(self, configured_bridge):
        """Test emergency cost reduction scenario"""
        bridge = configured_bridge
        
        # Set very tight budget
        bridge.set_daily_budget(0.001)  # $0.001 daily budget
        
        # Enable emergency mode
        bridge.enable_emergency_mode()
        
        # All requests should use cheapest available models
        expensive_requests = [
            "Perform complex data analysis",
            "Write sophisticated algorithm",
            "Detailed code review"
        ]
        
        for prompt in expensive_requests:
            response = await bridge.generate_text(prompt=prompt)
            
            if response and not response.error:
                # Should use very cheap models in emergency mode
                assert response.cost < 0.001, f"Emergency mode not working, cost: ${response.cost}"
    
    @pytest.mark.asyncio
    async def test_quality_vs_cost_tradeoffs(self, configured_bridge):
        """Test quality vs cost tradeoffs"""
        bridge = configured_bridge
        
        # Test same task with different optimization preferences
        prompt = "Explain machine learning concepts"
        
        # Quality-first
        response_quality = await bridge.generate_text(
            prompt=prompt,
            optimize_for="quality"
        )
        
        # Cost-first  
        response_cost = await bridge.generate_text(
            prompt=prompt,
            optimize_for="cost"
        )
        
        # Speed-first
        response_speed = await bridge.generate_text(
            prompt=prompt,
            optimize_for="speed"
        )
        
        # All should succeed
        responses = [response_quality, response_cost, response_speed]
        for resp in responses:
            assert resp is not None
            assert resp.error is None
        
        # Cost optimization should result in lower costs
        if response_quality.cost and response_cost.cost:
            assert response_cost.cost <= response_quality.cost, \
                f"Cost optimization failed: {response_cost.cost} > {response_quality.cost}"
    
    @pytest.mark.asyncio
    async def test_high_volume_cost_tracking(self, configured_bridge):
        """Test cost tracking under high volume"""
        bridge = configured_bridge
        
        bridge.set_monthly_budget(5.0)
        
        # Simulate high volume of small requests
        num_requests = 20
        
        for i in range(num_requests):
            await bridge.generate_text(
                prompt=f"Simple request #{i}",
                optimize_for="cost"
            )
        
        # Check final statistics
        usage_stats = bridge.get_cost_usage_stats("month")
        
        assert usage_stats["total_requests"] == num_requests
        assert usage_stats["total_cost"] > 0
        
        # Average cost per request should be reasonable
        avg_cost = usage_stats["total_cost"] / num_requests
        assert avg_cost < 0.01, f"Average cost too high: ${avg_cost}"
        
        # Budget should not be exceeded
        budget_status = bridge.get_budget_status()
        monthly_budget = next(
            (b for b in budget_status if b["name"] == "monthly_default"),
            None
        )
        if monthly_budget:
            assert not monthly_budget["is_exceeded"], "Budget was exceeded"
    
    def test_analytics_and_reporting(self, configured_bridge):
        """Test analytics and reporting functionality"""
        bridge = configured_bridge
        
        # Set up tracking
        bridge.set_monthly_budget(20.0)
        
        # Get comprehensive system status
        system_status = bridge.get_system_status()
        
        assert "cost_management" in system_status
        assert system_status["total_providers"] > 0
        
        # Get optimization recommendations
        recommendations = bridge.get_optimization_recommendations()
        assert isinstance(recommendations["recommendations"], list)
        
        # Test data export capabilities (if implemented)
        if hasattr(bridge.cost_manager, 'export_all_data'):
            export_data = bridge.cost_manager.export_all_data("month")
            assert "export_metadata" in export_data