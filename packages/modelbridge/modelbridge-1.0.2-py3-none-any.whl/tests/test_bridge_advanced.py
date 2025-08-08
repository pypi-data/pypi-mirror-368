"""
Advanced tests for ModelBridge functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from modelbridge import ModelBridge, IntelligentRouter
from modelbridge.bridge import Config, ModelAlias
from modelbridge.providers.base import GenerationRequest, GenerationResponse


class TestConfig:
    """Test Config class functionality"""

    def test_config_initialization(self):
        """Test config initialization"""
        config = Config()
        
        assert hasattr(config, 'available_providers')
        assert hasattr(config, 'providers')
        assert isinstance(config.available_providers, list)
        assert isinstance(config.providers, dict)

    def test_config_with_env_vars(self):
        """Test config loading from environment variables"""
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-openai-key',
            'ANTHROPIC_API_KEY': 'test-anthropic-key'
        }):
            config = Config()
            
            assert 'openai' in config.available_providers
            assert 'anthropic' in config.available_providers
            assert config.providers['openai'].api_key == 'test-openai-key'
            assert config.providers['anthropic'].api_key == 'test-anthropic-key'

    def test_config_empty_env(self):
        """Test config with no environment variables"""
        with patch.dict('os.environ', {}, clear=True):
            config = Config()
            
            assert len(config.available_providers) == 0
            assert len(config.providers) == 0


class TestModelAlias:
    """Test ModelAlias class"""

    def test_model_alias_creation(self):
        """Test creating model alias"""
        alias = ModelAlias("fastest", "groq", "llama3-8b-8192", 1)
        
        assert alias.alias == "fastest"
        assert alias.provider == "groq"
        assert alias.model_id == "llama3-8b-8192"
        assert alias.priority == 1

    def test_model_alias_default_priority(self):
        """Test model alias with default priority"""
        alias = ModelAlias("test", "openai", "gpt-3.5-turbo")
        
        assert alias.priority == 0


class TestIntelligentRouter:
    """Test IntelligentRouter functionality"""

    def test_router_initialization(self):
        """Test router initialization"""
        router = IntelligentRouter()
        
        assert router.performance_history == {}
        assert router.provider_health_cache == {}
        assert router.last_health_check is None

    def test_analyze_request_characteristics(self):
        """Test request characteristics analysis"""
        router = IntelligentRouter()
        
        # Test short prompt
        short_request = GenerationRequest(prompt="Hi")
        characteristics = router.analyze_request_characteristics(short_request)
        
        assert characteristics["complexity"] == "simple"
        assert "urgency" in characteristics
        assert "cost_sensitivity" in characteristics
        assert "quality_requirement" in characteristics

        # Test long prompt
        long_request = GenerationRequest(prompt="x" * 1500)
        characteristics = router.analyze_request_characteristics(long_request)
        
        assert characteristics["complexity"] == "complex"

        # Test medium prompt
        medium_request = GenerationRequest(prompt="x" * 500)
        characteristics = router.analyze_request_characteristics(medium_request)
        
        assert characteristics["complexity"] == "medium"

    def test_get_provider_ranking_empty(self):
        """Test provider ranking with no providers"""
        router = IntelligentRouter()
        
        characteristics = {"complexity": "medium"}
        ranking = router.get_provider_ranking(characteristics, {})
        
        assert ranking == []

    def test_get_provider_ranking(self):
        """Test provider ranking with mock providers"""
        router = IntelligentRouter()
        
        mock_providers = {
            "openai": Mock(),
            "anthropic": Mock()
        }
        
        characteristics = {
            "complexity": "medium",
            "urgency": "normal", 
            "cost_sensitivity": "medium",
            "quality_requirement": "medium"
        }
        ranking = router.get_provider_ranking(characteristics, mock_providers)
        
        assert len(ranking) == 2
        assert all(isinstance(item, tuple) for item in ranking)
        assert all(len(item) == 2 for item in ranking)
        assert all(isinstance(item[1], float) for item in ranking)

    def test_calculate_provider_score(self):
        """Test provider score calculation"""
        router = IntelligentRouter()
        
        # Test with no performance history
        characteristics = {
            "complexity": "medium",
            "urgency": "normal",
            "cost_sensitivity": "medium", 
            "quality_requirement": "medium"
        }
        score = router._calculate_provider_score("test-provider", characteristics)
        
        assert score == 50.0  # Base score

        # Test with performance history
        router.performance_history["test-provider"] = {
            "success_rate": 0.9,
            "avg_response_time": 1.5,
            "avg_cost": 0.005
        }
        
        score = router._calculate_provider_score("test-provider", characteristics)
        assert score > 50.0  # Should be higher with good performance

    @pytest.mark.asyncio
    async def test_update_performance_history(self):
        """Test updating performance history"""
        router = IntelligentRouter()
        
        # First update
        await router.update_performance_history("test-provider", 2.0, 0.01, True)
        
        assert "test-provider" in router.performance_history
        perf = router.performance_history["test-provider"]
        
        assert perf["total_requests"] == 1
        assert perf["successful_requests"] == 1
        assert perf["avg_response_time"] == 2.0
        assert perf["avg_cost"] == 0.01
        assert perf["success_rate"] == 1.0

        # Second update
        await router.update_performance_history("test-provider", 3.0, 0.02, False)
        
        perf = router.performance_history["test-provider"]
        assert perf["total_requests"] == 2
        assert perf["successful_requests"] == 1
        assert perf["avg_response_time"] == 2.5  # (2.0 + 3.0) / 2
        assert perf["avg_cost"] == 0.015  # (0.01 + 0.02) / 2
        assert perf["success_rate"] == 0.5  # 1 success out of 2


class TestModelBridgeAdvanced:
    """Test advanced ModelBridge functionality"""

    @pytest.mark.asyncio
    async def test_initialize_with_config_file(self):
        """Test initialization with config file"""
        bridge = ModelBridge(config_path="test_config.yaml")
        
        # Should handle missing config file gracefully
        success = await bridge.initialize()
        # May succeed or fail depending on available providers

    @pytest.mark.asyncio
    async def test_initialize_force_reload(self):
        """Test forced reinitialization"""
        bridge = ModelBridge()
        bridge._initialized = True
        
        # Should call initialize again even if already initialized
        success = await bridge.initialize(force_reload=True)
        # Just verify it doesn't crash - success depends on available providers

    @pytest.mark.asyncio
    async def test_initialize_provider_success(self):
        """Test successful provider initialization"""
        bridge = ModelBridge()
        
        mock_provider_class = Mock()
        mock_provider = AsyncMock()
        mock_provider.initialize.return_value = True
        mock_provider_class.return_value = mock_provider
        
        config = {'api_key': 'test-key', 'enabled': True, 'priority': 1}
        
        with patch.object(bridge, 'provider_classes', {'test': mock_provider_class}):
            success = await bridge._initialize_provider('test', config)
            
            assert success is True
            mock_provider_class.assert_called_once_with(config)
            mock_provider.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_provider_failure(self):
        """Test provider initialization failure"""
        bridge = ModelBridge()
        
        # Test with non-existent provider
        success = await bridge._initialize_provider('nonexistent', {})
        assert success is False

        # Test with provider that fails to initialize
        mock_provider_class = Mock()
        mock_provider = AsyncMock()
        mock_provider.initialize.return_value = False
        mock_provider_class.return_value = mock_provider
        
        with patch.object(bridge, 'provider_classes', {'test': mock_provider_class}):
            success = await bridge._initialize_provider('test', {'api_key': 'key'})
            assert success is False

    @pytest.mark.asyncio
    async def test_generate_text_full_parameters(self):
        """Test text generation with all parameters"""
        bridge = ModelBridge()
        bridge._initialized = True
        
        # Mock provider
        mock_provider = AsyncMock()
        mock_response = GenerationResponse(
            content="Test response",
            model_id="test-model",
            provider_name="test-provider",
            cost=0.001,
            response_time=1.5
        )
        mock_provider.generate_text.return_value = mock_response
        bridge.providers = {"test": mock_provider}
        
        # Mock model aliases
        bridge.model_aliases = {
            "test-alias": [ModelAlias("test-alias", "test", "test-model", 1)]
        }
        
        response = await bridge.generate_text(
            prompt="Test prompt",
            model="test-alias",
            system_message="System message",
            temperature=0.8,
            max_tokens=200,
            custom_param="value"
        )
        
        assert response.content == "Test response"
        assert response.model_id == "test-model"

    @pytest.mark.asyncio
    async def test_generate_structured_output_full(self):
        """Test structured output generation"""
        bridge = ModelBridge()
        bridge._initialized = True
        
        # Mock provider
        mock_provider = AsyncMock()
        mock_response = GenerationResponse(
            content='{"key": "value"}',
            model_id="test-model",
            provider_name="test-provider"
        )
        mock_provider.generate_structured_output.return_value = mock_response
        bridge.providers = {"test": mock_provider}
        
        # Mock model aliases
        bridge.model_aliases = {
            "test-alias": [ModelAlias("test-alias", "test", "test-model", 1)]
        }
        
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        response = await bridge.generate_structured_output(
            prompt="Generate JSON",
            schema=schema,
            model="test-alias",
            system_message="System message",
            temperature=0.7
        )
        
        assert response.content == '{"key": "value"}'

    @pytest.mark.asyncio
    async def test_route_request_capability_check(self):
        """Test routing with capability checking"""
        bridge = ModelBridge()
        bridge._initialized = True
        
        # Mock provider that doesn't support structured output
        mock_provider = AsyncMock()
        mock_provider.supports_capability.return_value = False
        bridge.providers = {"test": mock_provider}
        
        # Mock model aliases
        bridge.model_aliases = {
            "test-alias": [ModelAlias("test-alias", "test", "test-model", 1)]
        }
        
        request = GenerationRequest(
            prompt="Test",
            output_schema={"type": "object"}
        )
        
        response = await bridge._route_request(request, "test-alias", "generate_structured_output")
        
        # Should fail because provider doesn't support structured output
        assert response.error is not None

    @pytest.mark.asyncio
    async def test_route_request_performance_tracking(self):
        """Test performance tracking during routing"""
        bridge = ModelBridge()
        bridge._initialized = True
        bridge._performance_tracking = True
        
        # Mock provider
        mock_provider = AsyncMock()
        mock_response = GenerationResponse(
            content="Success",
            model_id="test-model",
            provider_name="test"
        )
        mock_provider.generate_text.return_value = mock_response
        bridge.providers = {"test": mock_provider}
        
        # Mock model aliases
        bridge.model_aliases = {
            "test-alias": [ModelAlias("test-alias", "test", "test-model", 1)]
        }
        
        request = GenerationRequest(prompt="Test")
        
        response = await bridge._route_request(request, "test-alias", "generate_text")
        
        # Check that performance stats were updated
        assert len(bridge.performance_stats) > 0
        key = "test:test-model"
        assert key in bridge.performance_stats

    def test_setup_default_aliases(self):
        """Test default aliases setup"""
        bridge = ModelBridge()
        
        # Should have default aliases
        expected_aliases = ["fastest", "cheapest", "best", "balanced"]
        
        for alias in expected_aliases:
            assert alias in bridge.model_aliases
            assert len(bridge.model_aliases[alias]) > 0

    def test_resolve_model_spec_direct_provider(self):
        """Test resolving direct provider:model specification"""
        bridge = ModelBridge()
        bridge.providers = {"openai": Mock()}
        
        models = bridge._resolve_model_spec("openai:gpt-3.5-turbo")
        
        assert len(models) == 1
        assert models[0].provider == "openai"
        assert models[0].model_id == "gpt-3.5-turbo"

    def test_resolve_model_spec_unknown(self):
        """Test resolving unknown model spec"""
        bridge = ModelBridge()
        bridge.providers = {}
        
        # Should fallback to empty list when no providers available
        models = bridge._resolve_model_spec("unknown-spec")
        
        assert models == []

    @pytest.mark.asyncio
    async def test_health_check_mixed_results(self):
        """Test health check with mixed provider results"""
        bridge = ModelBridge()
        
        # Mock providers with different health states
        healthy_provider = AsyncMock()
        healthy_provider.health_check.return_value = {"status": "healthy"}
        
        unhealthy_provider = AsyncMock()
        unhealthy_provider.health_check.side_effect = Exception("Connection failed")
        
        bridge.providers = {
            "healthy": healthy_provider,
            "unhealthy": unhealthy_provider
        }
        
        health_result = await bridge.health_check()
        
        assert health_result["status"] == "healthy"  # At least one healthy
        assert health_result["total_providers"] == 2
        assert health_result["healthy_providers"] == 1
        assert "healthy" in health_result["providers"]
        assert "unhealthy" in health_result["providers"]

    def test_get_routing_recommendations(self):
        """Test getting routing recommendations"""
        bridge = ModelBridge()
        bridge.intelligent_router.performance_history["test"] = {"success_rate": 0.9}
        
        recommendations = bridge.get_routing_recommendations()
        
        assert "performance_history" in recommendations
        assert "provider_health" in recommendations
        assert recommendations["performance_history"]["test"]["success_rate"] == 0.9