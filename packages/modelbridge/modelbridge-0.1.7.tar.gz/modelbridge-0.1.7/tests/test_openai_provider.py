"""
Comprehensive tests for OpenAI provider
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
import json
from modelbridge.providers.openai import OpenAIProvider
from modelbridge.providers.base import (
    GenerationRequest, 
    GenerationResponse, 
    ModelMetadata, 
    ModelCapability
)


class TestOpenAIProvider:
    """Test OpenAI provider functionality"""

    def test_provider_initialization(self):
        """Test basic provider initialization"""
        config = {"api_key": "test-key", "timeout": 30}
        provider = OpenAIProvider(config)
        
        assert provider.api_key == "test-key"
        assert provider.timeout == 30
        assert provider.provider_name == "openai"
        assert len(provider._models_metadata) > 0

    def test_default_models_setup(self):
        """Test that default models are properly configured"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Check that key models exist
        expected_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1", "o1-mini"]
        
        for model in expected_models:
            assert model in provider._models_metadata
            metadata = provider._models_metadata[model]
            assert isinstance(metadata, ModelMetadata)
            assert metadata.context_length > 0
            assert metadata.cost_per_1k_tokens > 0
            assert metadata.max_output_tokens > 0

    def test_model_capabilities(self):
        """Test model capabilities are correctly assigned"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Test GPT-4o capabilities
        gpt4o_metadata = provider._models_metadata["gpt-4o"]
        capabilities = gpt4o_metadata.capabilities
        
        assert ModelCapability.TEXT_GENERATION in capabilities
        assert ModelCapability.STRUCTURED_OUTPUT in capabilities
        assert ModelCapability.STREAMING in capabilities
        assert ModelCapability.FUNCTION_CALLING in capabilities
        assert ModelCapability.VISION in capabilities

    def test_get_available_models(self):
        """Test getting available models"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        models = provider.get_available_models()
        
        assert len(models) > 0
        assert all(isinstance(model, ModelMetadata) for model in models)
        assert all(model.provider_name == "openai" for model in models)

    def test_supports_capability(self):
        """Test capability checking"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # GPT-4o should support vision
        assert provider.supports_capability("gpt-4o", ModelCapability.VISION)
        
        # GPT-3.5-turbo should support function calling but not vision
        assert provider.supports_capability("gpt-3.5-turbo", ModelCapability.FUNCTION_CALLING)
        
        # All models should support text generation
        assert provider.supports_capability("gpt-4o", ModelCapability.TEXT_GENERATION)
        assert provider.supports_capability("gpt-3.5-turbo", ModelCapability.TEXT_GENERATION)

    def test_cost_calculation(self):
        """Test cost calculation"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Test with known model
        cost = provider.calculate_cost(1000, 500, "gpt-3.5-turbo")
        
        # Should be: (1000 + 500) / 1000 * cost_per_1k
        expected_cost = 1.5 * provider._models_metadata["gpt-3.5-turbo"].cost_per_1k_tokens
        assert cost == expected_cost

    def test_get_recommended_model(self):
        """Test model recommendation logic"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Test different complexity levels
        simple = provider.get_recommended_model(ModelCapability.TEXT_GENERATION, "simple")
        complex = provider.get_recommended_model(ModelCapability.TEXT_GENERATION, "complex")
        medium = provider.get_recommended_model(ModelCapability.TEXT_GENERATION, "medium")
        
        assert simple == "gpt-4o-mini"  # Fastest and cheapest
        assert complex == "gpt-4-turbo"  # Most capable
        assert medium == "gpt-4o"  # Best balance

    @pytest.mark.asyncio
    async def test_initialization_success(self):
        """Test successful provider initialization"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock successful health check
        with patch.object(provider, 'health_check', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {"status": "healthy"}
            
            result = await provider.initialize()
            assert result is True
            assert provider.client is not None

    @pytest.mark.asyncio
    async def test_initialization_failure_no_key(self):
        """Test initialization failure without API key"""
        config = {}  # No API key
        provider = OpenAIProvider(config)
        
        result = await provider.initialize()
        assert result is False

    @pytest.mark.asyncio
    async def test_initialization_failure_bad_key(self):
        """Test initialization failure with invalid API key"""
        config = {"api_key": "invalid-key"}
        provider = OpenAIProvider(config)
        
        # Mock failed health check
        with patch.object(provider, 'health_check', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {"status": "unhealthy"}
            
            result = await provider.initialize()
            assert result is False

    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        """Test successful text generation"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client.chat.completions.create.return_value = mock_response
        provider.client = mock_client
        
        request = GenerationRequest(
            prompt="Test prompt",
            system_message="You are helpful",
            temperature=0.7,
            max_tokens=100
        )
        
        response = await provider.generate_text(request, "gpt-3.5-turbo")
        
        assert response.content == "Test response"
        assert response.model_id == "gpt-3.5-turbo"
        assert response.provider_name == "openai"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 5
        assert response.total_tokens == 15
        assert response.cost > 0
        assert response.response_time > 0
        assert response.error is None

    @pytest.mark.asyncio
    async def test_generate_text_with_parameters(self):
        """Test text generation with various parameters"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client.chat.completions.create.return_value = mock_response
        provider.client = mock_client
        
        request = GenerationRequest(
            prompt="Test prompt",
            system_message="System message",
            temperature=0.8,
            max_tokens=200,
            stop_sequences=["STOP"],
            stream=False,
            extra_params={"presence_penalty": 0.1}
        )
        
        response = await provider.generate_text(request, "gpt-4o")
        
        # Verify the API was called with correct parameters
        call_args = mock_client.chat.completions.create.call_args
        params = call_args[1]  # keyword arguments
        
        assert params["model"] == "gpt-4o"
        assert params["temperature"] == 0.8
        assert params["max_tokens"] == 200
        assert params["stop"] == ["STOP"]
        assert params["stream"] is False
        assert params["presence_penalty"] == 0.1
        
        # Check messages structure
        messages = params["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System message"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Test prompt"

    @pytest.mark.asyncio
    async def test_generate_text_no_client(self):
        """Test text generation without initialized client"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        # Don't initialize client
        
        request = GenerationRequest(prompt="Test")
        response = await provider.generate_text(request, "gpt-3.5-turbo")
        
        assert response.content == ""
        assert response.error == "Provider not initialized"

    @pytest.mark.asyncio
    async def test_generate_text_api_error(self):
        """Test text generation with API error"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock OpenAI client that raises exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        provider.client = mock_client
        
        request = GenerationRequest(prompt="Test")
        response = await provider.generate_text(request, "gpt-3.5-turbo")
        
        assert response.content == ""
        assert "API Error" in response.error
        assert response.response_time > 0

    @pytest.mark.asyncio
    async def test_generate_structured_output_success(self):
        """Test successful structured output generation"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function.arguments = '{"key": "value"}'
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client.chat.completions.create.return_value = mock_response
        provider.client = mock_client
        
        request = GenerationRequest(
            prompt="Generate structured data",
            output_schema={
                "type": "object",
                "properties": {"key": {"type": "string"}}
            }
        )
        
        response = await provider.generate_structured_output(request, "gpt-4o")
        
        assert response.content == '{"key": "value"}'
        assert response.error is None

    @pytest.mark.asyncio
    async def test_generate_structured_output_no_schema(self):
        """Test structured output without schema"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        request = GenerationRequest(prompt="Test")
        response = await provider.generate_structured_output(request, "gpt-4o")
        
        assert response.content == ""
        assert "No output schema provided" in response.error

    @pytest.mark.asyncio
    async def test_generate_structured_output_invalid_json(self):
        """Test structured output with invalid JSON"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock OpenAI client returning invalid JSON
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function.arguments = 'invalid json'
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client.chat.completions.create.return_value = mock_response
        provider.client = mock_client
        
        request = GenerationRequest(
            prompt="Test",
            output_schema={"type": "object"}
        )
        
        response = await provider.generate_structured_output(request, "gpt-4o")
        
        assert "Invalid JSON in structured output" in response.error

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello"
        
        mock_client.chat.completions.create.return_value = mock_response
        provider.client = mock_client
        
        result = await provider.health_check()
        
        assert result["status"] == "healthy"
        assert result["provider"] == "openai"
        assert "models_available" in result
        assert "test_response" in result

    @pytest.mark.asyncio
    async def test_health_check_no_client(self):
        """Test health check without client"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        result = await provider.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["error"] == "Client not initialized"

    @pytest.mark.asyncio
    async def test_health_check_api_error(self):
        """Test health check with API error"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        # Mock OpenAI client that raises exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("Connection error")
        provider.client = mock_client
        
        result = await provider.health_check()
        
        assert result["status"] == "unhealthy"
        assert "Connection error" in result["error"]

    def test_string_representations(self):
        """Test string representations"""
        config = {"api_key": "test-key"}
        provider = OpenAIProvider(config)
        
        assert str(provider) == "openaiProvider"
        assert "models=" in repr(provider)
        assert "OpenAIProvider" in repr(provider)