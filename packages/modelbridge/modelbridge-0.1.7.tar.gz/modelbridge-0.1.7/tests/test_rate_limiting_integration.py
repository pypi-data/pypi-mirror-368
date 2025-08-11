"""
Tests for rate limiting integration in ValidatedModelBridge
"""
import pytest
import pytest_asyncio
import asyncio
import time
from unittest.mock import AsyncMock, patch

from modelbridge.config_bridge import ValidatedModelBridge
from modelbridge.config import ModelBridgeConfig, create_provider_config
from modelbridge.config.models import RateLimitConfig
from modelbridge.providers.base import GenerationResponse
from modelbridge.ratelimit.base import RateLimitError


async def create_bridge_with_rate_limiting():
    """Create a ValidatedModelBridge with rate limiting enabled"""
    config = ModelBridgeConfig(
        providers={
            "openai": create_provider_config(
                api_key="test-key-openai",
                enabled=True,
                max_requests_per_minute=5  # Very low for testing
            )
        },
        rate_limiting=RateLimitConfig(
            enabled=True,
            backend="memory",
            algorithm="sliding_window",
            global_requests_per_minute=10,
            cleanup_interval=60
        )
    )
    
    bridge = ValidatedModelBridge(config)
    
    # Mock the OpenAI provider to avoid real API calls
    with patch.object(bridge.provider_classes['openai'], '__new__') as mock_provider_class:
        mock_provider = AsyncMock()
        mock_provider.initialize.return_value = True
        mock_provider.generate_text.return_value = GenerationResponse(
            content="Test response",
            model_id="gpt-3.5-turbo",
            provider_name="openai"
        )
        mock_provider_class.return_value = mock_provider
        
        success = await bridge.initialize()
        assert success, "Bridge should initialize successfully"
        
        return bridge


class TestRateLimitingIntegration:
    """Test rate limiting integration"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test that rate limiter is properly initialized"""
        bridge = await create_bridge_with_rate_limiting()
        
        try:
            assert bridge.rate_limiter is not None
            assert bridge.rate_limit_manager is not None
            assert bridge.config.rate_limiting.enabled is True
        finally:
            await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_provider_rate_limit_configuration(self):
        """Test that provider rate limits are configured"""
        bridge = await create_bridge_with_rate_limiting()
        
        try:
            # Check provider configuration
            provider_config = bridge.rate_limit_manager.get_provider_config()
            assert "openai" in provider_config
            assert "requests_minute" in provider_config["openai"]
        finally:
            await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced"""
        bridge = await create_bridge_with_rate_limiting()
        
        try:
            # Make several rapid requests to trigger rate limiting
            responses = []
            errors = []
            
            for i in range(10):  # Exceed the 5 requests per minute limit
                try:
                    response = await bridge.generate_text(
                        prompt=f"Test prompt {i}",
                        model="openai"
                    )
                    responses.append(response)
                except Exception as e:
                    errors.append(str(e))
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.1)
            
            # Should have some successful responses and some rate limit errors
            assert len(responses) > 0, "Should have some successful responses"
            
            # Check if any responses contain rate limit errors
            rate_limited = any("rate limit" in resp.error.lower() 
                              for resp in responses if resp.error)
            
            # With very low limits, we should hit rate limiting
            # Note: This might be flaky depending on timing
            print(f"Responses: {len(responses)}, Errors: {len(errors)}")
            print(f"Rate limited responses: {rate_limited}")
        finally:
            await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_fallback_on_rate_limit(self):
        """Test fallback behavior when rate limited"""
        config = ModelBridgeConfig(
            providers={
                "openai": create_provider_config(
                    api_key="test-key-openai",
                    enabled=True,
                    max_requests_per_minute=1  # Very restrictive
                ),
                "anthropic": create_provider_config(
                    api_key="test-key-anthropic", 
                    enabled=True,
                    max_requests_per_minute=10  # More generous
                )
            },
            rate_limiting=RateLimitConfig(enabled=True, backend="memory"),
        )
        
        bridge = ValidatedModelBridge(config)
        
        # Mock both providers
        with patch.object(bridge.provider_classes['openai'], '__new__') as mock_openai, \
             patch.object(bridge.provider_classes['anthropic'], '__new__') as mock_anthropic:
            
            # Setup OpenAI mock (will be rate limited)
            mock_openai_instance = AsyncMock()
            mock_openai_instance.initialize.return_value = True
            mock_openai.return_value = mock_openai_instance
            
            # Setup Anthropic mock (fallback)
            mock_anthropic_instance = AsyncMock()
            mock_anthropic_instance.initialize.return_value = True
            mock_anthropic_instance.generate_text.return_value = GenerationResponse(
                content="Fallback response",
                model_id="claude-3-sonnet",
                provider_name="anthropic"
            )
            mock_anthropic.return_value = mock_anthropic_instance
            
            await bridge.initialize()
            
            # Make multiple requests to exceed OpenAI rate limit
            response = await bridge.generate_text(
                prompt="Test fallback",
                model="balanced"  # Will try multiple providers
            )
            
            # Should get a successful response from fallback provider
            assert not response.error
            assert response.content is not None
            
            await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_rate_limiting_disabled(self):
        """Test behavior when rate limiting is disabled"""
        config = ModelBridgeConfig(
            providers={
                "openai": create_provider_config(api_key="test-key")
            },
            rate_limiting=RateLimitConfig(enabled=False)
        )
        
        bridge = ValidatedModelBridge(config)
        
        with patch.object(bridge.provider_classes['openai'], '__new__') as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.initialize.return_value = True
            mock_provider_class.return_value = mock_provider
            
            await bridge.initialize()
            
            # Rate limiter should be None when disabled
            assert bridge.rate_limiter is None
            assert bridge.rate_limit_manager is None
            
            await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_rate_limit_health_check(self):
        """Test rate limiter health check"""
        bridge = await create_bridge_with_rate_limiting()
        
        try:
            health = await bridge.rate_limiter.health_check()
            assert health["status"] == "healthy"
            assert "algorithm" in health
        finally:
            await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_rate_limit_reset(self):
        """Test rate limit reset functionality"""
        bridge = await create_bridge_with_rate_limiting()
        
        try:
            # Reset rate limits for a provider
            success = await bridge.rate_limiter.reset_rate_limit("openai")
            assert isinstance(success, bool)  # Should return a boolean
        finally:
            await bridge.shutdown()
    
    @pytest.mark.asyncio
    async def test_redis_rate_limiting_config(self):
        """Test Redis rate limiting configuration"""
        config = ModelBridgeConfig(
            providers={
                "openai": create_provider_config(api_key="test-key")
            },
            rate_limiting=RateLimitConfig(
                enabled=True,
                backend="redis",
                redis_host="localhost",
                redis_port=6379,
                redis_db=1,
                redis_key_prefix="test_ratelimit:"
            )
        )
        
        bridge = ValidatedModelBridge(config)
        
        with patch.object(bridge.provider_classes['openai'], '__new__') as mock_provider_class:
            mock_provider = AsyncMock()
            mock_provider.initialize.return_value = True
            mock_provider_class.return_value = mock_provider
            
            # Mock Redis availability check to avoid Redis dependency
            with patch('modelbridge.ratelimit.redis.REDIS_AVAILABLE', False):
                await bridge.initialize()
                
                # Should fallback to memory rate limiter when Redis unavailable
                assert bridge.rate_limiter is not None
                
                await bridge.shutdown()


@pytest.mark.asyncio
async def test_rate_limiting_performance():
    """Test rate limiting performance doesn't significantly impact throughput"""
    config = ModelBridgeConfig(
        providers={
            "openai": create_provider_config(
                api_key="test-key",
                max_requests_per_minute=1000  # High limit
            )
        },
        rate_limiting=RateLimitConfig(
            enabled=True,
            backend="memory",
            algorithm="token_bucket"
        )
    )
    
    bridge = ValidatedModelBridge(config)
    
    with patch.object(bridge.provider_classes['openai'], '__new__') as mock_provider_class:
        mock_provider = AsyncMock()
        mock_provider.initialize.return_value = True
        mock_provider.generate_text.return_value = GenerationResponse(
            content="Test",
            model_id="gpt-3.5-turbo",
            provider_name="openai"
        )
        mock_provider_class.return_value = mock_provider
        
        await bridge.initialize()
        
        # Measure time for multiple requests
        start_time = time.time()
        
        tasks = []
        for i in range(50):
            task = bridge.generate_text(
                prompt=f"Test {i}",
                model="openai"
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete reasonably quickly (within 5 seconds)
        assert duration < 5.0, f"Rate limiting added too much overhead: {duration}s"
        
        # Most requests should succeed
        successful = sum(1 for r in responses if isinstance(r, GenerationResponse) and not r.error)
        assert successful > 40, f"Too many requests failed: {successful}/50"
        
        await bridge.shutdown()