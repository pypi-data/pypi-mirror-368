"""
Pytest configuration and shared fixtures
"""
import pytest
import pytest_asyncio
import asyncio
import os
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Test environment setup
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key") 
os.environ.setdefault("GOOGLE_API_KEY", "test-google-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response from OpenAI"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15
    return mock_response


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response"""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = "Test response from Anthropic"
    mock_response.usage = Mock()
    mock_response.usage.input_tokens = 10
    mock_response.usage.output_tokens = 5
    return mock_response


@pytest.fixture
def sample_generation_request():
    """Sample generation request for testing"""
    from modelbridge.providers.base import GenerationRequest
    return GenerationRequest(
        prompt="Test prompt",
        system_message="You are a helpful assistant",
        temperature=0.7,
        max_tokens=100
    )


@pytest.fixture
def provider_config():
    """Basic provider configuration for testing"""
    return {
        "api_key": "test-key",
        "enabled": True,
        "timeout": 30,
        "temperature": 0.1
    }


@pytest_asyncio.fixture
async def initialized_bridge():
    """Initialized ModelBridge instance for testing"""
    from modelbridge import ModelBridge
    bridge = ModelBridge()
    # Mock the initialization to avoid real API calls
    bridge._initialized = True
    bridge.providers = {}  # Will be populated by specific tests
    return bridge


@pytest_asyncio.fixture
async def memory_cache():
    """Memory cache instance for testing"""
    from modelbridge.cache import MemoryCache
    cache = MemoryCache(ttl=3600, max_size=10)  # Small size for testing
    await cache.initialize()
    yield cache
    await cache.shutdown()


@pytest_asyncio.fixture
async def cache():
    """Generic cache fixture (alias for memory_cache)"""
    from modelbridge.cache import MemoryCache
    cache = MemoryCache(ttl=3600, max_size=1000)
    await cache.initialize()
    yield cache
    await cache.shutdown()


@pytest.fixture
def mock_request_cost():
    """Mock RequestCost object for testing"""
    from modelbridge.cost.tracker import RequestCost
    return RequestCost(
        request_id="test-123",
        timestamp=1234567890.0,
        provider="openai",
        model="gpt-5-mini",
        prompt_tokens=100,
        completion_tokens=50,
        total_cost=0.001,
        task_type="testing"
    )


@pytest.fixture
def mock_optimization_result():
    """Mock OptimizationResult for testing"""
    from modelbridge.cost.optimizer import OptimizationResult
    return OptimizationResult(
        original_model="gpt-5",
        optimized_model="gpt-5-mini",
        original_cost=0.005,
        optimized_cost=0.001,
        cost_savings=0.004,
        savings_percentage=80.0,
        quality_impact="minimal",
        reasoning="Downgraded for cost efficiency",
        confidence=0.85
    )


@pytest.fixture
def mock_task_analysis():
    """Mock TaskAnalysis for testing"""
    from modelbridge.analyzer import TaskAnalysis, TaskType
    return TaskAnalysis(
        task_type=TaskType.CODING,
        complexity_score=0.75,
        confidence=0.9,
        recommended_model="gpt-5-mini",
        reasoning="Detected coding task with moderate complexity",
        metadata={"keywords": ["function", "python"]}
    )


@pytest_asyncio.fixture
async def bridge_with_cost_management():
    """ModelBridge instance with cost management enabled"""
    import tempfile
    from modelbridge import ModelBridge
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bridge = ModelBridge()
        # Initialize cost management with test data directory
        bridge.cost_manager = bridge.cost_manager.__class__(
            enable_tracking=True,
            enable_budgets=True,
            enable_optimization=True,
            data_dir=temp_dir
        )
        bridge._initialized = True
        yield bridge


@pytest.fixture
def sample_usage_stats():
    """Sample UsageStats for testing"""
    from modelbridge.cost.analytics import UsageStats
    return UsageStats(
        total_requests=1000,
        total_cost=25.50,
        total_tokens=150000,
        average_cost_per_request=0.0255,
        average_cost_per_token=0.00017,
        average_tokens_per_request=150.0,
        cost_trend="stable",
        top_models=[("openai:gpt-5", 15.0), ("anthropic:claude-3-5-sonnet", 10.5)],
        top_tasks=[("coding", 12.0), ("analysis", 8.5)],
        peak_usage_hour="02 PM",
        most_expensive_request=0.05,
        total_savings=3.25,
        optimization_rate=35.5
    )


@pytest.fixture 
def sample_budget_alert():
    """Sample BudgetAlert for testing"""
    import time
    from modelbridge.cost.budgets import BudgetAlert, BudgetType, AlertLevel
    
    return BudgetAlert(
        budget_name="test_budget",
        budget_type=BudgetType.MONTHLY,
        alert_level=AlertLevel.WARNING,
        current_usage=75.0,
        budget_limit=100.0,
        usage_percentage=75.0,
        time_remaining="7 days remaining",
        message="Budget warning test",
        timestamp=time.time()
    )