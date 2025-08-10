"""
Tests for Quality Scoring System
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from modelbridge.routing.quality_scorer import QualityScorer, QualityMetrics, ProviderQualityProfile
from modelbridge.providers.base import GenerationResponse


@pytest.fixture
def quality_scorer():
    """Create quality scorer instance"""
    return QualityScorer(max_history_per_provider=100)


@pytest.fixture
def sample_response():
    """Create sample response for testing"""
    return GenerationResponse(
        content="Here's a Python function to calculate factorial:\n\n```python\ndef factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n```\n\nThis function uses recursion to calculate the factorial.",
        model_id="gpt-4",
        provider_name="openai",
        cost=0.03,
        response_time=2.5
    )


@pytest.fixture
def sample_request():
    """Sample request prompt"""
    return "Write a Python function to calculate factorial"


class TestQualityScorer:
    """Test cases for Quality Scorer"""
    
    @pytest.mark.asyncio
    async def test_scorer_initialization(self, quality_scorer):
        """Test quality scorer initialization"""
        assert quality_scorer.max_history_per_provider == 100
        assert quality_scorer.provider_profiles == {}
        assert "excellent" in quality_scorer.quality_thresholds
        assert "coherence" in quality_scorer.quality_weights
    
    @pytest.mark.asyncio
    async def test_score_response_basic(self, quality_scorer, sample_response, sample_request):
        """Test basic response scoring"""
        metrics = await quality_scorer.score_response(
            response=sample_response,
            original_request=sample_request,
            task_type="code",
            complexity="medium"
        )
        
        assert isinstance(metrics, QualityMetrics)
        assert metrics.provider_name == "openai"
        assert metrics.model_id == "gpt-4"
        assert metrics.task_type == "code"
        assert metrics.complexity == "medium"
        assert 0.0 <= metrics.overall_quality <= 1.0
        assert 0.0 <= metrics.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_coherence_scoring(self, quality_scorer):
        """Test coherence scoring"""
        # Test coherent text
        coherent_score = await quality_scorer._score_coherence(
            "This is a well-structured response. It has proper sentences. The ideas flow logically from one to the next."
        )
        
        # Test incoherent text
        incoherent_score = await quality_scorer._score_coherence(
            "Random words. No structure here. Very bad text example."
        )
        
        assert 0.0 <= coherent_score <= 1.0
        assert 0.0 <= incoherent_score <= 1.0
        assert coherent_score > incoherent_score
    
    @pytest.mark.asyncio
    async def test_relevance_scoring(self, quality_scorer):
        """Test relevance scoring"""
        request = "Explain machine learning algorithms"
        
        # Test relevant response
        relevant_response = "Machine learning algorithms are computational methods that learn patterns from data. Popular algorithms include linear regression, decision trees, and neural networks."
        relevant_score = await quality_scorer._score_relevance(relevant_response, request)
        
        # Test irrelevant response
        irrelevant_response = "The weather is nice today. I like pizza and movies."
        irrelevant_score = await quality_scorer._score_relevance(irrelevant_response, request)
        
        assert 0.0 <= relevant_score <= 1.0
        assert 0.0 <= irrelevant_score <= 1.0
        assert relevant_score > irrelevant_score
    
    @pytest.mark.asyncio
    async def test_completeness_scoring(self, quality_scorer):
        """Test completeness scoring"""
        request = "Explain how to bake a cake"
        
        # Test complete response
        complete_response = "To bake a cake, follow these steps: 1. Preheat oven to 350°F. 2. Mix dry ingredients. 3. Add wet ingredients. 4. Pour into pan. 5. Bake for 30 minutes. The cake is done when a toothpick comes out clean."
        complete_score = await quality_scorer._score_completeness(complete_response, request)
        
        # Test incomplete response
        incomplete_response = "Mix ingredients and bake."
        incomplete_score = await quality_scorer._score_completeness(incomplete_response, request)
        
        assert 0.0 <= complete_score <= 1.0
        assert 0.0 <= incomplete_score <= 1.0
        assert complete_score > incomplete_score
    
    @pytest.mark.asyncio
    async def test_format_compliance_checking(self, quality_scorer):
        """Test format compliance checking"""
        # Test JSON format
        json_content = '{"name": "test", "value": 42}'
        assert quality_scorer._check_format_compliance(json_content, "json")
        
        invalid_json = '{"name": "test", value: }'
        assert not quality_scorer._check_format_compliance(invalid_json, "json")
        
        # Test list format
        list_content = "1. First item\n2. Second item\n3. Third item"
        assert quality_scorer._check_format_compliance(list_content, "list")
        
        # Test markdown format
        markdown_content = "# Header\n\n**Bold text** and *italic text*"
        assert quality_scorer._check_format_compliance(markdown_content, "markdown")
    
    @pytest.mark.asyncio
    async def test_instruction_following(self, quality_scorer):
        """Test instruction following detection"""
        # Test list instruction
        list_request = "List the top 3 programming languages"
        list_response = "1. Python\n2. JavaScript\n3. Java"
        assert await quality_scorer._check_instruction_following(list_response, list_request)
        
        non_list_response = "There are many programming languages like Python, JavaScript, and Java."
        assert not await quality_scorer._check_instruction_following(non_list_response, list_request)
        
        # Test explanation instruction
        explain_request = "Explain how databases work"
        explain_response = "Databases work because they store data in structured formats that allow for efficient retrieval."
        assert await quality_scorer._check_instruction_following(explain_response, explain_request)
    
    @pytest.mark.asyncio
    async def test_provider_profile_updates(self, quality_scorer, sample_response, sample_request):
        """Test provider profile updates"""
        # Score a response
        metrics = await quality_scorer.score_response(
            response=sample_response,
            original_request=sample_request
        )
        
        # Check that provider profile was created
        assert "openai" in quality_scorer.provider_profiles
        profile = quality_scorer.provider_profiles["openai"]
        
        assert isinstance(profile, ProviderQualityProfile)
        assert profile.provider_name == "openai"
        assert profile.total_responses == 1
        assert len(profile.quality_history) == 1
        assert profile.avg_overall_quality > 0
    
    @pytest.mark.asyncio
    async def test_quality_trends(self, quality_scorer, sample_request):
        """Test quality trend detection"""
        # Add multiple responses with declining quality
        for i in range(10):
            # Create response with declining quality
            content = "Good response" if i < 5 else "Bad"
            response = GenerationResponse(
                content=content,
                model_id="gpt-4",
                provider_name="test_provider",
                cost=0.01
            )
            
            await quality_scorer.score_response(response, sample_request)
        
        # Add more responses to trigger trend analysis
        for i in range(10):
            content = "Excellent detailed response with comprehensive information"
            response = GenerationResponse(
                content=content,
                model_id="gpt-4", 
                provider_name="test_provider",
                cost=0.01
            )
            
            await quality_scorer.score_response(response, sample_request)
        
        profile = quality_scorer.provider_profiles["test_provider"]
        # Should have detected trend (though simple implementation)
        assert profile.quality_trend in ["improving", "declining", "stable"]
    
    @pytest.mark.asyncio
    async def test_task_specific_performance(self, quality_scorer, sample_request):
        """Test task-specific performance tracking"""
        # Score responses for different task types
        code_response = GenerationResponse(
            content="def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
            model_id="gpt-4",
            provider_name="test_provider"
        )
        
        creative_response = GenerationResponse(
            content="Once upon a time, in a land far away, there lived a brave knight who sought adventure.",
            model_id="gpt-4",
            provider_name="test_provider"
        )
        
        await quality_scorer.score_response(code_response, "Write a factorial function", task_type="code")
        await quality_scorer.score_response(creative_response, "Write a story", task_type="creative")
        
        profile = quality_scorer.provider_profiles["test_provider"]
        
        # Check task-specific performance
        assert "code" in profile.task_performance
        assert "creative" in profile.task_performance
        assert profile.task_performance["code"]["sample_count"] == 1
        assert profile.task_performance["creative"]["sample_count"] == 1
    
    @pytest.mark.asyncio
    async def test_quality_recommendations(self, quality_scorer, sample_request):
        """Test quality-based recommendations"""
        # Add responses for multiple providers
        providers = ["openai", "anthropic", "google", "groq"]
        qualities = [0.9, 0.95, 0.8, 0.7]
        
        for provider, quality in zip(providers, qualities):
            for _ in range(5):  # Add multiple responses per provider
                content = "Excellent response" if quality > 0.85 else "Good response"
                response = GenerationResponse(
                    content=content,
                    model_id="model",
                    provider_name=provider
                )
                
                await quality_scorer.score_response(response, sample_request, task_type="general")
        
        # Get recommendations
        recommendations = quality_scorer.get_quality_recommendations(task_type="general")
        
        assert len(recommendations) > 0
        # Should be sorted by quality score (descending)
        scores = [score for _, score, _ in recommendations]
        assert scores == sorted(scores, reverse=True)
        
        # Top recommendation should be anthropic (highest quality)
        top_provider = recommendations[0][0]
        assert top_provider == "anthropic"
    
    @pytest.mark.asyncio
    async def test_concurrent_scoring(self, quality_scorer, sample_request):
        """Test concurrent response scoring"""
        responses = []
        for i in range(20):
            response = GenerationResponse(
                content=f"Response {i} with varied content length and quality",
                model_id="gpt-4",
                provider_name=f"provider_{i % 4}",
                cost=0.01
            )
            responses.append(response)
        
        # Score all responses concurrently
        tasks = [
            quality_scorer.score_response(response, sample_request)
            for response in responses
        ]
        
        metrics_list = await asyncio.gather(*tasks)
        
        assert len(metrics_list) == 20
        for metrics in metrics_list:
            assert isinstance(metrics, QualityMetrics)
            assert metrics.overall_quality >= 0.0
    
    @pytest.mark.asyncio
    async def test_quality_scorer_error_handling(self, quality_scorer):
        """Test error handling in quality scoring"""
        # Test with invalid response
        invalid_response = GenerationResponse(
            content=None,  # Invalid content
            model_id="test",
            provider_name="test"
        )
        
        # Should handle gracefully
        metrics = await quality_scorer.score_response(
            response=invalid_response,
            original_request="test request"
        )
        
        assert isinstance(metrics, QualityMetrics)
        assert metrics.confidence == 0.0  # Should indicate low confidence


class TestQualityMetrics:
    """Test cases for Quality Metrics"""
    
    def test_quality_metrics_creation(self):
        """Test quality metrics creation"""
        metrics = QualityMetrics(
            response_id="test_123",
            provider_name="openai",
            model_id="gpt-4",
            timestamp=time.time()
        )
        
        assert metrics.response_id == "test_123"
        assert metrics.provider_name == "openai"
        assert metrics.model_id == "gpt-4"
        assert metrics.coherence_score == 0.0  # Default value
    
    def test_quality_metrics_scoring(self):
        """Test quality metrics with scores"""
        metrics = QualityMetrics(
            response_id="test_123",
            provider_name="openai",
            model_id="gpt-4",
            timestamp=time.time(),
            coherence_score=0.9,
            relevance_score=0.85,
            completeness_score=0.8,
            overall_quality=0.85,
            confidence=0.9
        )
        
        assert metrics.coherence_score == 0.9
        assert metrics.relevance_score == 0.85
        assert metrics.completeness_score == 0.8
        assert metrics.overall_quality == 0.85
        assert metrics.confidence == 0.9


class TestQualityIntegration:
    """Integration tests for quality scoring system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_quality_workflow(self):
        """Test complete quality scoring workflow"""
        scorer = QualityScorer()
        
        # Create realistic responses
        responses = [
            GenerationResponse(
                content="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nThis function calculates Fibonacci numbers recursively.",
                model_id="gpt-4",
                provider_name="openai",
                cost=0.02,
                response_time=1.5
            ),
            GenerationResponse(
                content="fib func: if n<=1 return n else return fib(n-1)+fib(n-2)",
                model_id="llama-7b",
                provider_name="groq",
                cost=0.001,
                response_time=0.8
            )
        ]
        
        request = "Write a Python function to calculate Fibonacci numbers"
        
        # Score both responses
        metrics_list = []
        for response in responses:
            metrics = await scorer.score_response(
                response=response,
                original_request=request,
                task_type="code",
                complexity="medium"
            )
            metrics_list.append(metrics)
        
        # Verify scoring
        assert len(metrics_list) == 2
        
        # First response should have higher quality
        openai_metrics = metrics_list[0]
        groq_metrics = metrics_list[1]
        
        assert openai_metrics.overall_quality > groq_metrics.overall_quality
        assert openai_metrics.coherence_score > groq_metrics.coherence_score
        assert openai_metrics.completeness_score > groq_metrics.completeness_score
        
        # Check provider profiles
        assert len(scorer.provider_profiles) == 2
        assert "openai" in scorer.provider_profiles
        assert "groq" in scorer.provider_profiles
        
        # Get quality summary
        summary = scorer.get_provider_quality_summary()
        assert "openai" in summary
        assert "groq" in summary
    
    @pytest.mark.asyncio
    async def test_quality_based_provider_ranking(self):
        """Test provider ranking based on quality scores"""
        scorer = QualityScorer()
        
        # Add multiple responses for each provider
        providers_data = {
            "openai": {"quality": 0.9, "count": 10},
            "anthropic": {"quality": 0.95, "count": 8},
            "google": {"quality": 0.8, "count": 12},
            "groq": {"quality": 0.7, "count": 15}
        }
        
        request = "Explain machine learning concepts"
        
        for provider_name, data in providers_data.items():
            for i in range(data["count"]):
                # Vary quality slightly
                base_quality = data["quality"]
                content_quality = "excellent" if base_quality > 0.85 else "good"
                
                response = GenerationResponse(
                    content=f"This is a {content_quality} explanation of machine learning with detailed information and examples.",
                    model_id="model",
                    provider_name=provider_name,
                    cost=0.01
                )
                
                await scorer.score_response(response, request, task_type="analysis")
        
        # Get recommendations
        recommendations = scorer.get_quality_recommendations(task_type="analysis")
        
        # Should be ranked by quality
        assert len(recommendations) == 4
        
        # Anthropic should be first (highest quality)
        assert recommendations[0][0] == "anthropic"
        assert recommendations[-1][0] == "groq"  # Lowest quality should be last