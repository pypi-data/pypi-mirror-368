"""
Comprehensive tests for Anthropic provider
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from modelbridge.providers.anthropic import AnthropicProvider
from modelbridge.providers.base import (
    GenerationRequest, 
    GenerationResponse, 
    ModelMetadata, 
    ModelCapability
)


class TestAnthropicProvider:
    """Test Anthropic provider functionality"""

    def test_provider_initialization(self):
        """Test basic provider initialization"""
        config = {"api_key": "test-key", "timeout": 60}
        provider = AnthropicProvider(config)
        
        assert provider.api_key == "test-key"
        assert provider.timeout == 60
        assert provider.provider_name == "anthropic"
        assert len(provider._models_metadata) > 0

    def test_default_models_setup(self):
        """Test that default models are properly configured"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Check that key models exist
        expected_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022", 
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        
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
        provider = AnthropicProvider(config)
        
        # Test Claude 3.5 Sonnet capabilities
        sonnet_metadata = provider._models_metadata["claude-3-5-sonnet-20241022"]
        capabilities = sonnet_metadata.capabilities
        
        assert ModelCapability.TEXT_GENERATION in capabilities
        assert ModelCapability.STRUCTURED_OUTPUT in capabilities
        assert ModelCapability.FUNCTION_CALLING in capabilities

    def test_get_available_models(self):
        """Test getting available models"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        models = provider.get_available_models()
        
        assert len(models) > 0
        assert all(isinstance(model, ModelMetadata) for model in models)
        assert all(model.provider_name == "anthropic" for model in models)

    def test_supports_capability(self):
        """Test capability checking"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # All models should support text generation
        assert provider.supports_capability("claude-3-opus-20240229", ModelCapability.TEXT_GENERATION)
        assert provider.supports_capability("claude-3-5-sonnet-20241022", ModelCapability.TEXT_GENERATION)

    def test_cost_calculation(self):
        """Test cost calculation"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Test with known model
        cost = provider.calculate_cost(1000, 500, "claude-3-haiku-20240307")
        
        # Should be: (1000 + 500) / 1000 * cost_per_1k
        expected_cost = 1.5 * provider._models_metadata["claude-3-haiku-20240307"].cost_per_1k_tokens
        assert cost == expected_cost

    @pytest.mark.asyncio
    async def test_initialization_success(self):
        """Test successful provider initialization"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
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
        provider = AnthropicProvider(config)
        
        result = await provider.initialize()
        assert result is False

    @pytest.mark.asyncio
    async def test_initialization_failure_bad_key(self):
        """Test initialization failure with invalid API key"""
        config = {"api_key": "invalid-key"}
        provider = AnthropicProvider(config)
        
        # Mock failed health check
        with patch.object(provider, 'health_check', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = {"status": "unhealthy"}
            
            result = await provider.initialize()
            assert result is False

    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        """Test successful text generation"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Mock Anthropic client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response from Claude"
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        
        mock_client.messages.create.return_value = mock_response
        provider.client = mock_client
        
        request = GenerationRequest(
            prompt="Test prompt",
            system_message="You are helpful",
            temperature=0.7,
            max_tokens=100
        )
        
        response = await provider.generate_text(request, "claude-3-sonnet-20240229")
        
        assert response.content == "Test response from Claude"
        assert response.model_id == "claude-3-sonnet-20240229"
        assert response.provider_name == "anthropic"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 5
        assert response.cost > 0
        assert response.response_time > 0
        assert response.error is None

    @pytest.mark.asyncio
    async def test_generate_text_with_parameters(self):
        """Test text generation with various parameters"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Mock Anthropic client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        
        mock_client.messages.create.return_value = mock_response
        provider.client = mock_client
        
        request = GenerationRequest(
            prompt="Test prompt",
            system_message="System message",
            temperature=0.8,
            max_tokens=200,
            stop_sequences=["STOP"],
            stream=False
        )
        
        response = await provider.generate_text(request, "claude-3-opus-20240229")
        
        # Verify the API was called with correct parameters
        call_args = mock_client.messages.create.call_args
        params = call_args[1]  # keyword arguments
        
        assert params["model"] == "claude-3-opus-20240229"
        assert params["temperature"] == 0.8
        assert params["max_tokens"] == 200
        assert params["stop_sequences"] == ["STOP"]
        
        # Check messages structure
        messages = params["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Test prompt"
        
        # Check system message
        assert params["system"] == "System message"

    @pytest.mark.asyncio
    async def test_generate_text_no_client(self):
        """Test text generation without initialized client"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        # Don't initialize client
        
        request = GenerationRequest(prompt="Test")
        response = await provider.generate_text(request, "claude-3-sonnet-20240229")
        
        assert response.content == ""
        assert response.error == "Provider not initialized"

    @pytest.mark.asyncio
    async def test_generate_text_api_error(self):
        """Test text generation with API error"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Mock Anthropic client that raises exception
        mock_client = AsyncMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        provider.client = mock_client
        
        request = GenerationRequest(prompt="Test")
        response = await provider.generate_text(request, "claude-3-sonnet-20240229")
        
        assert response.content == ""
        assert "API Error" in response.error
        assert response.response_time > 0

    @pytest.mark.asyncio 
    async def test_generate_structured_output_success(self):
        """Test successful structured output generation"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Mock Anthropic client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '{"key": "value"}'
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5
        
        mock_client.messages.create.return_value = mock_response
        provider.client = mock_client
        
        request = GenerationRequest(
            prompt="Generate structured data",
            output_schema={
                "type": "object",
                "properties": {"key": {"type": "string"}}
            }
        )
        
        response = await provider.generate_structured_output(request, "claude-3-sonnet-20240229")
        
        assert response.content == '{"key": "value"}'
        assert response.error is None

    @pytest.mark.asyncio
    async def test_generate_structured_output_no_schema(self):
        """Test structured output without schema"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        request = GenerationRequest(prompt="Test")
        response = await provider.generate_structured_output(request, "claude-3-sonnet-20240229")
        
        assert response.content == ""
        assert "No output schema provided" in response.error

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Mock Anthropic client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Hello"
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 5
        mock_response.usage.output_tokens = 2
        
        mock_client.messages.create.return_value = mock_response
        provider.client = mock_client
        
        result = await provider.health_check()
        
        assert result["status"] == "healthy"
        assert result["provider"] == "anthropic"
        assert "models_available" in result
        assert "test_response" in result

    @pytest.mark.asyncio
    async def test_health_check_no_client(self):
        """Test health check without client"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        result = await provider.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["error"] == "Client not initialized"

    @pytest.mark.asyncio
    async def test_health_check_api_error(self):
        """Test health check with API error"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        # Mock Anthropic client that raises exception
        mock_client = AsyncMock()
        mock_client.messages.create.side_effect = Exception("Connection error")
        provider.client = mock_client
        
        result = await provider.health_check()
        
        assert result["status"] == "unhealthy"
        assert "Connection error" in result["error"]

    @pytest.mark.asyncio
    async def test_anthropic_not_available(self):
        """Test behavior when Anthropic SDK is not available"""
        config = {"api_key": "test-key"}
        
        # Mock ANTHROPIC_AVAILABLE as False
        with patch('modelbridge.providers.anthropic.ANTHROPIC_AVAILABLE', False):
            provider = AnthropicProvider(config)
            result = await provider.initialize()
            assert result is False

    def test_string_representations(self):
        """Test string representations"""
        config = {"api_key": "test-key"}
        provider = AnthropicProvider(config)
        
        assert str(provider) == "anthropicProvider"
        assert "models=" in repr(provider)
        assert "AnthropicProvider" in repr(provider)