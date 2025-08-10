"""
Basic tests for ModelBridge core functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from modelbridge import ModelBridge
from modelbridge.providers.base import GenerationRequest, GenerationResponse


class TestModelBridgeBasic:
    """Test basic ModelBridge functionality"""

    def test_bridge_initialization(self):
        """Test that ModelBridge can be initialized"""
        bridge = ModelBridge()
        assert bridge is not None
        assert not bridge._initialized
        assert bridge.providers == {}
        assert bridge.intelligent_router is not None

    def test_bridge_with_config_path(self):
        """Test ModelBridge initialization with config path"""
        bridge = ModelBridge(config_path="test_config.yaml")
        assert bridge.config_path == "test_config.yaml"

    def test_model_aliases_setup(self):
        """Test that default model aliases are set up correctly"""
        bridge = ModelBridge()
        
        # Check that aliases exist
        assert "fastest" in bridge.model_aliases
        assert "cheapest" in bridge.model_aliases
        assert "best" in bridge.model_aliases
        assert "balanced" in bridge.model_aliases
        
        # Check that each alias has at least one model
        for alias_name, models in bridge.model_aliases.items():
            assert len(models) > 0
            assert all(hasattr(model, 'provider') for model in models)
            assert all(hasattr(model, 'model_id') for model in models)

    def test_provider_classes_mapping(self):
        """Test that provider classes are correctly mapped"""
        bridge = ModelBridge()
        
        expected_providers = ["openai", "anthropic", "google", "groq"]
        for provider in expected_providers:
            assert provider in bridge.provider_classes
            assert bridge.provider_classes[provider] is not None

    @pytest.mark.asyncio
    async def test_bridge_initialization_no_api_keys(self):
        """Test bridge initialization without API keys"""
        # Clear environment variables for this test
        with patch.dict('os.environ', {}, clear=True):
            bridge = ModelBridge()
            success = await bridge.initialize()
            assert not success  # Should fail without API keys

    @pytest.mark.asyncio
    async def test_bridge_initialization_with_mock_provider(self):
        """Test successful initialization with mocked provider"""
        bridge = ModelBridge()
        
        # Mock a provider
        mock_provider = AsyncMock()
        mock_provider.initialize.return_value = True
        
        # Mock the provider creation
        with patch.object(bridge, 'provider_classes', {"test": lambda config: mock_provider}):
            with patch.object(bridge.config, 'available_providers', ["test"]):
                with patch.object(bridge.config, 'providers', {"test": Mock(api_key="test", priority=1)}):
                    success = await bridge.initialize()
                    assert success
                    assert "test" in bridge.providers

    def test_resolve_model_spec_alias(self):
        """Test model specification resolution for aliases"""
        bridge = ModelBridge()
        
        # Mock having available providers for this test
        bridge.providers = {"groq": Mock(), "openai": Mock(), "google": Mock()}
        
        # Test resolving a known alias
        models = bridge._resolve_model_spec("fastest")
        assert len(models) > 0
        assert all(model.alias == "fastest" for model in models)

    def test_resolve_model_spec_direct(self):
        """Test model specification resolution for direct provider:model"""
        bridge = ModelBridge()
        
        # Mock having an available provider
        bridge.providers["openai"] = Mock()
        
        models = bridge._resolve_model_spec("openai:gpt-3.5-turbo")
        assert len(models) == 1
        assert models[0].provider == "openai"
        assert models[0].model_id == "gpt-3.5-turbo"

    def test_resolve_model_spec_fallback(self):
        """Test model specification resolution fallback to balanced"""
        bridge = ModelBridge()
        
        # Test with unknown spec - should fallback to balanced
        models = bridge._resolve_model_spec("unknown-model")
        balanced_models = bridge._resolve_model_spec("balanced")
        
        # Should get the same result as balanced alias
        assert len(models) == len(balanced_models)

    def test_performance_stats_initialization(self):
        """Test that performance stats are properly initialized"""
        bridge = ModelBridge()
        assert bridge.performance_stats == {}
        
        stats = bridge.get_performance_stats()
        assert isinstance(stats, dict)

    def test_update_performance_stats(self):
        """Test performance stats updating"""
        bridge = ModelBridge()
        
        # Update stats
        bridge._update_performance_stats(
            provider="test_provider",
            model_id="test_model", 
            response_time=1.5,
            cost=0.001,
            success=True
        )
        
        key = "test_provider:test_model"
        assert key in bridge.performance_stats
        
        stats = bridge.performance_stats[key]
        assert stats["total_requests"] == 1
        assert stats["successful_requests"] == 1
        assert stats["avg_response_time"] == 1.5
        assert stats["avg_cost"] == 0.001
        assert stats["success_rate"] == 1.0

    def test_update_performance_stats_multiple_calls(self):
        """Test performance stats with multiple updates"""
        bridge = ModelBridge()
        
        # Multiple updates
        bridge._update_performance_stats("test", "model", 1.0, 0.001, True)
        bridge._update_performance_stats("test", "model", 2.0, 0.002, False)
        
        key = "test:model"
        stats = bridge.performance_stats[key]
        
        assert stats["total_requests"] == 2
        assert stats["successful_requests"] == 1
        assert stats["avg_response_time"] == 1.5  # (1.0 + 2.0) / 2
        assert stats["avg_cost"] == 0.0015  # (0.001 + 0.002) / 2
        assert stats["success_rate"] == 0.5  # 1 success out of 2