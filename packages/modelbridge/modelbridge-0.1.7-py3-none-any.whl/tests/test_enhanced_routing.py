"""
Tests for Enhanced Routing System
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from modelbridge.routing.enhanced_router import (
    EnhancedRouter, RoutingContext, ProviderScore
)
from modelbridge.routing.routing_strategies import (
    QualityBasedRouting, CostBasedRouting, LatencyBasedRouting, ReliabilityBasedRouting
)
from modelbridge.providers.base import GenerationRequest, BaseModelProvider


class MockProvider(BaseModelProvider):
    def __init__(self, name: str):
        self.name = name
    
    async def initialize(self):
        return True
    
    async def generate_text(self, request, model_id):
        return Mock()
    
    async def generate_structured_output(self, request, model_id):
        return Mock()
    
    async def get_available_models(self):
        return []
    
    async def health_check(self):
        return {"status": "healthy"}
    
    def supports_capability(self, model_id, capability):
        return True


@pytest.fixture
def mock_providers():
    """Create mock providers for testing"""
    return {
        "openai": MockProvider("openai"),
        "anthropic": MockProvider("anthropic"),
        "google": MockProvider("google"),
        "groq": MockProvider("groq")
    }


@pytest.fixture
def sample_request():
    """Create sample generation request"""
    return GenerationRequest(
        prompt="Write a Python function to calculate factorial",
        temperature=0.7,
        max_tokens=1000
    )


@pytest.fixture
def routing_context(mock_providers, sample_request):
    """Create routing context for testing"""
    return RoutingContext(
        request=sample_request,
        available_providers=mock_providers,
        urgency="normal",
        cost_sensitivity="medium",
        quality_requirement="high",
        task_type="code"
    )


class TestEnhancedRouter:
    """Test cases for Enhanced Router"""
    
    @pytest.fixture
    def router(self):
        """Create router instance"""
        return EnhancedRouter()
    
    @pytest.mark.asyncio
    async def test_router_initialization(self, router):
        """Test router initialization"""
        assert router.performance_history == {}
        assert router.provider_health == {}
        assert router.circuit_breakers == {}
        assert len(router.routing_strategies) > 0
    
    @pytest.mark.asyncio
    async def test_route_request_basic(self, router, routing_context):
        """Test basic request routing"""
        rankings = await router.route_request(routing_context)
        
        assert isinstance(rankings, list)
        assert len(rankings) > 0
        
        # Check ranking structure
        for provider_name, score in rankings:
            assert isinstance(provider_name, str)
            assert isinstance(score, ProviderScore)
            assert score.score >= 0.0
    
    @pytest.mark.asyncio
    async def test_request_analysis(self, router, sample_request):
        """Test request analysis"""
        characteristics = await router._analyze_request(sample_request)
        
        assert "prompt_length" in characteristics
        assert "complexity" in characteristics
        assert "task_type" in characteristics
        assert "structured_output" in characteristics
        
        # Check specific values
        assert characteristics["task_type"] == "code"
        assert characteristics["complexity"] in ["simple", "medium", "complex", "very_complex"]
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, router):
        """Test circuit breaker implementation"""
        provider_name = "test_provider"
        
        # Initially should be available
        assert router._is_provider_available(provider_name)
        
        # Simulate failures to trigger circuit breaker
        for _ in range(5):
            await router._update_circuit_breaker(provider_name, False)
        
        # Should now be circuit broken
        assert not router._is_provider_available(provider_name)
        
        # Test recovery after timeout (simulate time passage)
        router.circuit_breakers[provider_name]["last_failure"] = time.time() - 400
        assert router._is_provider_available(provider_name)
    
    @pytest.mark.asyncio
    async def test_performance_metrics_update(self, router):
        """Test performance metrics tracking"""
        provider_name = "test_provider"
        
        await router.update_performance_metrics(
            provider_name=provider_name,
            response_time=2.5,
            cost=0.05,
            success=True,
            quality_score=0.85
        )
        
        assert provider_name in router.performance_history
        history = router.performance_history[provider_name]
        
        assert history["total_requests"] == 1
        assert history["successful_requests"] == 1
        assert history["avg_response_time"] == 2.5
        assert history["avg_cost"] == 0.05
        assert history["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_fallback_routing(self, router, routing_context):
        """Test fallback routing when main routing fails"""
        # Mock strategy to raise exception
        with patch.object(router.routing_strategies[0], 'score_provider', side_effect=Exception("Test error")):
            rankings = await router.route_request(routing_context)
            
            # Should still return rankings (fallback)
            assert isinstance(rankings, list)
    
    @pytest.mark.asyncio
    async def test_concurrent_routing_requests(self, router, mock_providers, sample_request):
        """Test concurrent routing requests"""
        contexts = [
            RoutingContext(
                request=sample_request,
                available_providers=mock_providers,
                task_type=f"task_{i}"
            )
            for i in range(10)
        ]
        
        # Execute concurrent routing
        tasks = [router.route_request(context) for context in contexts]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        for result in results:
            assert isinstance(result, list)


class TestQualityBasedRouting:
    """Test cases for Quality-Based Routing Strategy"""
    
    @pytest.fixture
    def strategy(self):
        return QualityBasedRouting()
    
    @pytest.mark.asyncio
    async def test_provider_scoring(self, strategy, mock_providers, routing_context):
        """Test provider scoring logic"""
        provider = mock_providers["openai"]
        
        score = await strategy.score_provider("openai", provider, routing_context)
        
        assert isinstance(score, ProviderScore)
        assert score.provider_name == "openai"
        assert score.score > 0
        assert len(score.reasons) > 0
        assert score.estimated_cost > 0
        assert score.estimated_latency > 0
    
    @pytest.mark.asyncio
    async def test_task_type_bonuses(self, strategy, mock_providers, routing_context):
        """Test task type specific bonuses"""
        provider = mock_providers["openai"]
        
        # Test code task
        routing_context.task_type = "code"
        code_score = await strategy.score_provider("openai", provider, routing_context)
        
        # Test creative task
        routing_context.task_type = "creative"
        creative_score = await strategy.score_provider("anthropic", mock_providers["anthropic"], routing_context)
        
        # Scores should differ based on task type
        assert code_score.score != creative_score.score
    
    @pytest.mark.asyncio
    async def test_quality_requirements(self, strategy, mock_providers, routing_context):
        """Test quality requirement adjustments"""
        provider = mock_providers["anthropic"]
        
        # Test critical quality requirement
        routing_context.quality_requirement = "critical"
        critical_score = await strategy.score_provider("anthropic", provider, routing_context)
        
        # Test low quality requirement  
        routing_context.quality_requirement = "low"
        low_score = await strategy.score_provider("anthropic", provider, routing_context)
        
        # Critical should score higher for premium providers
        assert critical_score.score > low_score.score


class TestCostBasedRouting:
    """Test cases for Cost-Based Routing Strategy"""
    
    @pytest.fixture
    def strategy(self):
        return CostBasedRouting()
    
    @pytest.mark.asyncio
    async def test_cost_efficiency_scoring(self, strategy, mock_providers, routing_context):
        """Test cost efficiency scoring"""
        # Test cheap provider (groq)
        groq_score = await strategy.score_provider("groq", mock_providers["groq"], routing_context)
        
        # Test expensive provider (openai)
        openai_score = await strategy.score_provider("openai", mock_providers["openai"], routing_context)
        
        # Groq should score higher for cost efficiency
        assert groq_score.score > openai_score.score
    
    @pytest.mark.asyncio
    async def test_cost_sensitivity_adjustments(self, strategy, mock_providers, routing_context):
        """Test cost sensitivity adjustments"""
        provider = mock_providers["groq"]
        
        # High cost sensitivity
        routing_context.cost_sensitivity = "high"
        high_sens_score = await strategy.score_provider("groq", provider, routing_context)
        
        # Low cost sensitivity
        routing_context.cost_sensitivity = "low"
        low_sens_score = await strategy.score_provider("groq", provider, routing_context)
        
        # Should score higher with high cost sensitivity for cheap provider
        assert high_sens_score.score > low_sens_score.score


class TestLatencyBasedRouting:
    """Test cases for Latency-Based Routing Strategy"""
    
    @pytest.fixture
    def strategy(self):
        return LatencyBasedRouting()
    
    @pytest.mark.asyncio
    async def test_latency_scoring(self, strategy, mock_providers, routing_context):
        """Test latency-based scoring"""
        # Test fast provider (groq)
        groq_score = await strategy.score_provider("groq", mock_providers["groq"], routing_context)
        
        # Test slower provider (anthropic)
        anthropic_score = await strategy.score_provider("anthropic", mock_providers["anthropic"], routing_context)
        
        # Groq should score higher for speed
        assert groq_score.score > anthropic_score.score
    
    @pytest.mark.asyncio
    async def test_urgency_adjustments(self, strategy, mock_providers, routing_context):
        """Test urgency-based adjustments"""
        provider = mock_providers["groq"]
        
        # Critical urgency
        routing_context.urgency = "critical"
        critical_score = await strategy.score_provider("groq", provider, routing_context)
        
        # Normal urgency
        routing_context.urgency = "normal"
        normal_score = await strategy.score_provider("groq", provider, routing_context)
        
        # Should score higher with critical urgency for fast provider
        assert critical_score.score > normal_score.score


class TestReliabilityBasedRouting:
    """Test cases for Reliability-Based Routing Strategy"""
    
    @pytest.fixture
    def strategy(self):
        return ReliabilityBasedRouting()
    
    @pytest.mark.asyncio
    async def test_reliability_scoring(self, strategy, mock_providers, routing_context):
        """Test reliability scoring"""
        # Test reliable provider (openai)
        openai_score = await strategy.score_provider("openai", mock_providers["openai"], routing_context)
        
        # Test less reliable provider (groq)
        groq_score = await strategy.score_provider("groq", mock_providers["groq"], routing_context)
        
        # OpenAI should score higher for reliability
        assert openai_score.score > groq_score.score
    
    @pytest.mark.asyncio
    async def test_critical_task_adjustments(self, strategy, mock_providers, routing_context):
        """Test critical task reliability requirements"""
        provider = mock_providers["openai"]
        
        # Critical quality requirement
        routing_context.quality_requirement = "critical"
        critical_score = await strategy.score_provider("openai", provider, routing_context)
        
        # Normal requirement
        routing_context.quality_requirement = "medium"
        normal_score = await strategy.score_provider("openai", provider, routing_context)
        
        # Should score higher for critical tasks with reliable provider
        assert critical_score.score > normal_score.score


class TestRoutingIntegration:
    """Integration tests for routing system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_routing(self, mock_providers):
        """Test complete routing flow"""
        router = EnhancedRouter()
        
        request = GenerationRequest(
            prompt="Explain quantum computing in simple terms",
            temperature=0.5,
            max_tokens=500
        )
        
        context = RoutingContext(
            request=request,
            available_providers=mock_providers,
            urgency="normal",
            cost_sensitivity="medium",
            quality_requirement="high"
        )
        
        # Route request
        rankings = await router.route_request(context)
        
        # Verify results
        assert len(rankings) == len(mock_providers)
        
        # Top provider should have highest score
        scores = [score.score for _, score in rankings]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_routing_with_performance_history(self, mock_providers):
        """Test routing with historical performance data"""
        router = EnhancedRouter()
        
        # Add performance history
        await router.update_performance_metrics("openai", 1.5, 0.02, True, 0.9)
        await router.update_performance_metrics("anthropic", 2.0, 0.015, True, 0.95)
        await router.update_performance_metrics("groq", 0.8, 0.001, True, 0.75)
        
        request = GenerationRequest(prompt="Test prompt")
        context = RoutingContext(
            request=request,
            available_providers=mock_providers
        )
        
        rankings = await router.route_request(context)
        
        # Verify performance history influences scoring
        assert len(rankings) > 0
        
        # Check that performance data is being used
        summary = router.get_performance_summary()
        assert "performance_history" in summary
    
    @pytest.mark.asyncio
    async def test_routing_error_handling(self, mock_providers):
        """Test error handling in routing"""
        router = EnhancedRouter()
        
        # Create invalid context
        invalid_context = RoutingContext(
            request=None,  # Invalid request
            available_providers={}  # No providers
        )
        
        # Should handle gracefully
        rankings = await router.route_request(invalid_context)
        
        # Should return empty or fallback results
        assert isinstance(rankings, list)