"""
Tests for base provider functionality
"""
import pytest
from unittest.mock import Mock, AsyncMock
from modelbridge.providers.base import (
    BaseModelProvider,
    GenerationRequest,
    GenerationResponse,
    ModelMetadata,
    ModelCapability
)


class TestGenerationRequest:
    """Test GenerationRequest class"""

    def test_basic_request(self):
        """Test basic request creation"""
        request = GenerationRequest(prompt="Hello world")
        
        assert request.prompt == "Hello world"
        assert request.system_message is None
        assert request.temperature is None
        assert request.max_tokens is None
        assert request.stop_sequences is None
        assert request.stream is False
        assert request.output_schema is None
        assert request.extra_params is None

    def test_full_request(self):
        """Test request with all parameters"""
        schema = {"type": "object"}
        extra = {"custom_param": "value"}
        
        request = GenerationRequest(
            prompt="Test prompt",
            system_message="System",
            temperature=0.7,
            max_tokens=100,
            stop_sequences=["STOP"],
            stream=True,
            output_schema=schema,
            extra_params=extra
        )
        
        assert request.prompt == "Test prompt"
        assert request.system_message == "System"
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.stop_sequences == ["STOP"]
        assert request.stream is True
        assert request.output_schema == schema
        assert request.extra_params == extra


class TestGenerationResponse:
    """Test GenerationResponse class"""

    def test_basic_response(self):
        """Test basic response creation"""
        response = GenerationResponse(
            content="Response text",
            model_id="gpt-3.5-turbo",
            provider_name="openai"
        )
        
        assert response.content == "Response text"
        assert response.model_id == "gpt-3.5-turbo"
        assert response.provider_name == "openai"
        assert response.prompt_tokens is None
        assert response.completion_tokens is None
        assert response.total_tokens is None
        assert response.cost is None
        assert response.response_time is None
        assert response.raw_response is None
        assert response.error is None

    def test_full_response(self):
        """Test response with all parameters"""
        raw_data = {"test": "data"}
        
        response = GenerationResponse(
            content="Response text",
            model_id="claude-3",
            provider_name="anthropic",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            cost=0.001,
            response_time=1.5,
            raw_response=raw_data,
            error=None
        )
        
        assert response.content == "Response text"
        assert response.model_id == "claude-3"
        assert response.provider_name == "anthropic"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 5
        assert response.total_tokens == 15
        assert response.cost == 0.001
        assert response.response_time == 1.5
        assert response.raw_response == raw_data
        assert response.error is None

    def test_is_success(self):
        """Test success checking"""
        # Successful response
        success_response = GenerationResponse(
            content="Success",
            model_id="test",
            provider_name="test"
        )
        assert success_response.is_success() is True
        
        # Failed response with error
        error_response = GenerationResponse(
            content="",
            model_id="test",
            provider_name="test",
            error="API Error"
        )
        assert error_response.is_success() is False
        
        # Response with no content but no error
        empty_response = GenerationResponse(
            content="",
            model_id="test",
            provider_name="test"
        )
        assert empty_response.is_success() is True


class TestModelMetadata:
    """Test ModelMetadata class"""

    def test_model_metadata(self):
        """Test model metadata creation"""
        capabilities = [ModelCapability.TEXT_GENERATION, ModelCapability.VISION]
        
        metadata = ModelMetadata(
            model_id="gpt-4o",
            provider_name="openai",
            model_name="OpenAI GPT-4o",
            capabilities=capabilities,
            context_length=128000,
            cost_per_1k_tokens=0.002,
            max_output_tokens=4096,
            supports_system_messages=True,
            supports_temperature=True
        )
        
        assert metadata.model_id == "gpt-4o"
        assert metadata.provider_name == "openai"
        assert metadata.model_name == "OpenAI GPT-4o"
        assert metadata.capabilities == capabilities
        assert metadata.context_length == 128000
        assert metadata.cost_per_1k_tokens == 0.002
        assert metadata.max_output_tokens == 4096
        assert metadata.supports_system_messages is True
        assert metadata.supports_temperature is True


class TestModelCapability:
    """Test ModelCapability enum"""

    def test_capabilities(self):
        """Test all capabilities exist"""
        assert ModelCapability.TEXT_GENERATION.value == "text_generation"
        assert ModelCapability.STRUCTURED_OUTPUT.value == "structured_output"
        assert ModelCapability.FUNCTION_CALLING.value == "function_calling"
        assert ModelCapability.VISION.value == "vision"
        assert ModelCapability.EMBEDDINGS.value == "embeddings"
        assert ModelCapability.STREAMING.value == "streaming"


class ConcreteProvider(BaseModelProvider):
    """Concrete implementation for testing base provider"""
    
    def __init__(self, config):
        super().__init__(config)
        # Add some test models
        self._models_metadata = {
            "test-model": ModelMetadata(
                model_id="test-model",
                provider_name="test",
                model_name="Test Model",
                capabilities=[ModelCapability.TEXT_GENERATION],
                context_length=4096,
                cost_per_1k_tokens=0.001,
                max_output_tokens=2048
            ),
            "test-model-expensive": ModelMetadata(
                model_id="test-model-expensive",
                provider_name="test",
                model_name="Expensive Test Model",
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.VISION],
                context_length=8192,
                cost_per_1k_tokens=0.01,
                max_output_tokens=4096
            ),
            "test-model-cheap": ModelMetadata(
                model_id="test-model-cheap",
                provider_name="test",
                model_name="Cheap Test Model",
                capabilities=[ModelCapability.TEXT_GENERATION],
                context_length=2048,
                cost_per_1k_tokens=0.0001,
                max_output_tokens=1024
            )
        }
    
    async def initialize(self):
        return True
    
    async def generate_text(self, request, model_id):
        return GenerationResponse(
            content="Test response",
            model_id=model_id,
            provider_name="test"
        )
    
    async def generate_structured_output(self, request, model_id):
        return GenerationResponse(
            content='{"test": "value"}',
            model_id=model_id,
            provider_name="test"
        )
    
    def get_available_models(self):
        return list(self._models_metadata.values())
    
    async def health_check(self):
        return {"status": "healthy"}


class TestBaseModelProvider:
    """Test BaseModelProvider functionality"""

    def test_provider_initialization(self):
        """Test basic provider initialization"""
        config = {"api_key": "test-key", "timeout": 30}
        provider = ConcreteProvider(config)
        
        assert provider.provider_config == config
        assert provider.provider_name == "concrete"
        assert len(provider._models_metadata) == 3

    def test_supports_capability(self):
        """Test capability checking"""
        provider = ConcreteProvider({})
        
        # Test model with text generation
        assert provider.supports_capability("test-model", ModelCapability.TEXT_GENERATION) is True
        assert provider.supports_capability("test-model", ModelCapability.VISION) is False
        
        # Test model with multiple capabilities
        assert provider.supports_capability("test-model-expensive", ModelCapability.TEXT_GENERATION) is True
        assert provider.supports_capability("test-model-expensive", ModelCapability.VISION) is True
        
        # Test non-existent model
        assert provider.supports_capability("non-existent", ModelCapability.TEXT_GENERATION) is False

    def test_get_model_metadata(self):
        """Test getting model metadata"""
        provider = ConcreteProvider({})
        
        # Test existing model
        metadata = provider.get_model_metadata("test-model")
        assert metadata is not None
        assert metadata.model_id == "test-model"
        assert metadata.provider_name == "test"
        
        # Test non-existent model
        metadata = provider.get_model_metadata("non-existent")
        assert metadata is None

    def test_calculate_cost(self):
        """Test cost calculation"""
        provider = ConcreteProvider({})
        
        # Test with existing model
        cost = provider.calculate_cost(1000, 500, "test-model")
        expected_cost = (1000 + 500) / 1000 * 0.001
        assert cost == expected_cost
        
        # Test with non-existent model
        cost = provider.calculate_cost(1000, 500, "non-existent")
        assert cost == 0.0

    def test_get_recommended_model_simple(self):
        """Test model recommendation for simple tasks"""
        provider = ConcreteProvider({})
        
        # Should choose cheapest model
        model = provider.get_recommended_model(ModelCapability.TEXT_GENERATION, "simple")
        assert model == "test-model-cheap"

    def test_get_recommended_model_complex(self):
        """Test model recommendation for complex tasks"""
        provider = ConcreteProvider({})
        
        # Should choose model with highest context length
        model = provider.get_recommended_model(ModelCapability.TEXT_GENERATION, "complex")
        assert model == "test-model-expensive"

    def test_get_recommended_model_medium(self):
        """Test model recommendation for medium tasks"""
        provider = ConcreteProvider({})
        
        # Should choose middle model
        models = provider.get_available_models()
        model = provider.get_recommended_model(ModelCapability.TEXT_GENERATION, "medium")
        
        # Should be one of the available models
        model_ids = [m.model_id for m in models if ModelCapability.TEXT_GENERATION in m.capabilities]
        assert model in model_ids

    def test_get_recommended_model_no_capability(self):
        """Test model recommendation for unsupported capability"""
        provider = ConcreteProvider({})
        
        # Should return None for unsupported capability
        model = provider.get_recommended_model(ModelCapability.EMBEDDINGS, "simple")
        assert model is None

    def test_string_representations(self):
        """Test string representations"""
        provider = ConcreteProvider({})
        
        assert str(provider) == "concreteProvider"
        assert "ConcreteProvider" in repr(provider)
        assert "models=3" in repr(provider)

    def test_get_available_models(self):
        """Test getting available models"""
        provider = ConcreteProvider({})
        
        models = provider.get_available_models()
        assert len(models) == 3
        assert all(isinstance(model, ModelMetadata) for model in models)

    @pytest.mark.asyncio
    async def test_abstract_methods_implemented(self):
        """Test that concrete provider implements abstract methods"""
        provider = ConcreteProvider({})
        
        # Test initialize
        result = await provider.initialize()
        assert result is True
        
        # Test generate_text
        request = GenerationRequest(prompt="test")
        response = await provider.generate_text(request, "test-model")
        assert response.content == "Test response"
        
        # Test generate_structured_output
        response = await provider.generate_structured_output(request, "test-model")
        assert response.content == '{"test": "value"}'
        
        # Test health_check
        health = await provider.health_check()
        assert health["status"] == "healthy"