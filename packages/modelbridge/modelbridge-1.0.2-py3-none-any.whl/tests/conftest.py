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