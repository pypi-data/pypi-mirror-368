"""
Test error handling throughout the system
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from modelbridge import ModelBridge
from modelbridge.providers.base import GenerationRequest, GenerationResponse
from modelbridge.providers.openai import OpenAIProvider


class TestErrorHandling:
    """Test comprehensive error handling"""

    @pytest.mark.asyncio
    async def test_provider_initialization_failure(self):
        """Test handling of provider initialization failures"""
        bridge = ModelBridge()
        
        # Mock provider that fails to initialize
        with patch.object(bridge, 'provider_classes', {"test": lambda config: AsyncMock(initialize=AsyncMock(return_value=False))}):
            with patch.object(bridge.config, 'available_providers', ["test"]):
                with patch.object(bridge.config, 'providers', {"test": Mock(api_key="test", priority=1)}):
                    success = await bridge.initialize()
                    assert not success or "test" not in bridge.providers

    @pytest.mark.asyncio 
    async def test_all_providers_fail_initialization(self):
        """Test when all providers fail to initialize"""
        bridge = ModelBridge()
        
        # Mock all providers failing
        failing_provider = AsyncMock()
        failing_provider.initialize.return_value = False
        
        with patch.object(bridge, 'provider_classes', {"test": lambda config: failing_provider}):
            with patch.object(bridge.config, 'available_providers', ["test"]):
                with patch.object(bridge.config, 'providers', {"test": Mock(api_key="test", priority=1)}):
                    success = await bridge.initialize()
                    assert not success

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        bridge = ModelBridge() 
        bridge._initialized = True
        
        # Mock provider that raises timeout
        mock_provider = AsyncMock()
        mock_provider.generate_text.side_effect = asyncio.TimeoutError("Request timed out")
        bridge.providers = {"test": mock_provider}
        
        request = GenerationRequest(prompt="test")
        response = await bridge._route_request(request, "test:model", "generate_text")
        
        assert response.error is not None
        assert "timed out" in response.error.lower() or "error" in response.error.lower()

    @pytest.mark.asyncio
    async def test_invalid_api_key_handling(self):
        """Test handling of invalid API keys"""
        provider_config = {"api_key": "invalid-key"}
        provider = OpenAIProvider(provider_config)
        
        # This should not crash - initialization should fail gracefully
        result = await provider.initialize()
        assert not result  # Should return False for invalid key

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses"""
        bridge = ModelBridge()
        bridge._initialized = True
        
        # Mock provider that returns malformed response
        mock_provider = AsyncMock()
        malformed_response = GenerationResponse(
            content="",
            model_id="test",
            provider_name="test",
            error="Malformed response from API"
        )
        mock_provider.generate_text.return_value = malformed_response
        bridge.providers = {"test": mock_provider}
        
        request = GenerationRequest(prompt="test")
        response = await bridge._route_request(request, "test:model", "generate_text")
        
        assert response.error is not None

    @pytest.mark.asyncio
    async def test_fallback_when_primary_fails(self):
        """Test fallback to secondary provider when primary fails"""
        bridge = ModelBridge()
        bridge._initialized = True
        bridge._fallback_enabled = True
        
        # Mock providers - first fails, second succeeds
        failing_provider = AsyncMock()
        failing_provider.generate_text.return_value = GenerationResponse(
            content="", model_id="fail", provider_name="fail", error="API Error"
        )
        
        working_provider = AsyncMock()
        working_provider.generate_text.return_value = GenerationResponse(
            content="Success!", model_id="work", provider_name="work"
        )
        
        bridge.providers = {"fail": failing_provider, "work": working_provider}
        
        # Setup aliases to use both providers
        from modelbridge.bridge import ModelAlias
        bridge.model_aliases = {
            "test": [
                ModelAlias("test", "fail", "model1", 1),
                ModelAlias("test", "work", "model2", 2)
            ]
        }
        
        request = GenerationRequest(prompt="test")
        response = await bridge._route_request(request, "test", "generate_text")
        
        assert response.error is None
        assert response.content == "Success!"
        assert response.provider_name == "work"

    @pytest.mark.asyncio
    async def test_no_fallback_when_disabled(self):
        """Test that fallback is disabled when configured off"""
        bridge = ModelBridge()
        bridge._initialized = True
        bridge._fallback_enabled = False
        
        # Mock failing provider
        failing_provider = AsyncMock()
        failing_provider.generate_text.return_value = GenerationResponse(
            content="", model_id="fail", provider_name="fail", error="API Error"
        )
        bridge.providers = {"fail": failing_provider}
        
        from modelbridge.bridge import ModelAlias
        bridge.model_aliases = {
            "test": [ModelAlias("test", "fail", "model1", 1)]
        }
        
        request = GenerationRequest(prompt="test")
        response = await bridge._route_request(request, "test", "generate_text")
        
        # Should return the error response, not attempt fallback
        assert response.error is not None

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self):
        """Test handling of empty prompts"""
        bridge = ModelBridge()
        bridge._initialized = True
        
        mock_provider = AsyncMock()
        mock_provider.generate_text.return_value = GenerationResponse(
            content="", model_id="test", provider_name="test", 
            error="Empty prompt provided"
        )
        bridge.providers = {"test": mock_provider}
        
        # Empty prompt should be handled gracefully
        response = await bridge.generate_text(prompt="", model="test:model")
        
        # Should not crash, may return error response
        assert response is not None

    def test_invalid_model_spec(self):
        """Test handling of invalid model specifications"""
        bridge = ModelBridge()
        
        # Test with completely invalid spec
        models = bridge._resolve_model_spec("invalid::model::spec")
        
        # Should fallback to balanced alias
        balanced_models = bridge._resolve_model_spec("balanced")
        assert len(models) == len(balanced_models)

    def test_config_missing_api_keys(self):
        """Test configuration when API keys are missing"""
        # Clear environment for this test
        with patch.dict('os.environ', {}, clear=True):
            bridge = ModelBridge()
            
            # Should handle missing API keys gracefully
            assert len(bridge.config.available_providers) == 0
            
    def test_performance_stats_edge_cases(self):
        """Test performance stats with edge case inputs"""
        bridge = ModelBridge()
        
        # Test with zero values
        bridge._update_performance_stats("test", "model", 0.0, 0.0, True)
        
        key = "test:model"
        stats = bridge.performance_stats[key]
        assert stats["avg_response_time"] == 0.0
        assert stats["avg_cost"] == 0.0
        assert stats["success_rate"] == 1.0
        
        # Test with negative values (should be handled gracefully)
        bridge._update_performance_stats("test", "model", -1.0, -0.001, False)
        
        # Should still work without crashing
        assert stats["total_requests"] == 2