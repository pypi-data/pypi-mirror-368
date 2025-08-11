"""
OpenAI Provider for Unified Model Bridge
Supports GPT-4, GPT-3.5, and other OpenAI models with latest syntax
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
from ..utils.retry import with_retry, RetryConfig, retry_manager
from ..utils.validation import APIKeyValidator, ResponseValidator
import logging

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseModelProvider):
    """OpenAI provider with support for all GPT models"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.config = provider_config  # Store config for retry logic
        self.client: Optional[AsyncOpenAI] = None
        self.api_key = provider_config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.organization = provider_config.get("organization") or os.getenv("OPENAI_ORG_ID")
        self.base_url = provider_config.get("base_url", "https://api.openai.com/v1")
        self.default_temperature = provider_config.get("temperature", 1.0)
        self.timeout = provider_config.get("timeout", 60)
        
        # Load models from config with defaults
        self.model_configs = provider_config.get("models", self._get_default_models())
        self._setup_models_metadata()
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Get default OpenAI model configurations - Updated August 2025"""
        return {
            # GPT-5 Family (LATEST - Released August 7, 2025) 🚀
            "gpt-5": {
                "context_length": 272000,
                "cost_per_1k_tokens": 1.25,  # Input cost: $1.25/1M tokens
                "cost_per_1k_tokens_output": 10.00,  # Output cost: $10/1M tokens
                "max_output_tokens": 128000,
                "category": "flagship",
                "speed": "medium",
                "reasoning": "exceptional",
                "capabilities": ["text", "vision", "advanced_reasoning", "function_calling", "tool_use", "agentic"],
                "knowledge_cutoff": "2025-06",
                "description": "Best for coding & agents. State-of-art reasoning. Beats o3 at frontend dev"
            },
            "gpt-5-mini": {
                "context_length": 272000,
                "cost_per_1k_tokens": 0.25,  # Input cost: $0.25/1M tokens
                "cost_per_1k_tokens_output": 2.00,  # Output cost: $2.00/1M tokens
                "max_output_tokens": 128000,
                "category": "balanced",
                "speed": "fast",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "reasoning", "function_calling", "tool_use"],
                "knowledge_cutoff": "2025-06",
                "description": "Balanced performance & cost. Great for most tasks"
            },
            "gpt-5-nano": {
                "context_length": 272000,
                "cost_per_1k_tokens": 0.05,   # Input cost: $0.05/1M tokens
                "cost_per_1k_tokens_output": 0.40,  # Output cost: $0.40/1M tokens
                "max_output_tokens": 128000,
                "category": "fast",
                "speed": "fastest",
                "reasoning": "good", 
                "capabilities": ["text", "basic_reasoning", "function_calling"],
                "knowledge_cutoff": "2025-06",
                "description": "Ultra-fast, cheapest option. Good for simple tasks"
            },
            "gpt-5-chat-latest": {
                "context_length": 272000,
                "cost_per_1k_tokens": 1.25,  # Input cost: $1.25/1M tokens
                "cost_per_1k_tokens_output": 10.00,  # Output cost: $10/1M tokens
                "max_output_tokens": 128000,
                "category": "chat",
                "speed": "fast",
                "reasoning": "good",
                "capabilities": ["text", "conversation", "function_calling"],
                "knowledge_cutoff": "2025-06",
                "description": "Non-reasoning version for ChatGPT-style conversations"
            },

            # GPT-4.1 Series (New)
            "gpt-4.1": {
                "context_length": 128000,
                "cost_per_1k_tokens": 2.50,  # Input cost: $2.50/1M tokens
                "cost_per_1k_tokens_output": 10.00,  # Output cost: $10/1M tokens
                "max_output_tokens": 32000,
                "category": "large",
                "speed": "medium",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "function_calling", "tool_use"],
                "knowledge_cutoff": "2025-06",
                "description": "Better instruction following, long context handling"
            },
            "gpt-4.1-mini": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.15,  # Input cost: $0.15/1M tokens
                "cost_per_1k_tokens_output": 0.60,  # Output cost: $0.60/1M tokens
                "max_output_tokens": 16384,
                "category": "small",
                "speed": "fast",
                "reasoning": "good",
                "capabilities": ["text", "vision", "function_calling"],
                "knowledge_cutoff": "2025-06",
                "description": "Affordable with good performance"
            },

            # O-Series (Reasoning Models)
            "o3": {
                "context_length": 200000,
                "cost_per_1k_tokens": 15.00,  # Input cost: $15/1M tokens
                "cost_per_1k_tokens_output": 60.00,  # Output cost: $60/1M tokens
                "max_output_tokens": 65536,
                "category": "reasoning",
                "speed": "slow",
                "reasoning": "exceptional",
                "capabilities": ["text", "advanced_reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2025-06",
                "description": "Advanced reasoning, math, coding"
            },
            "o3-mini": {
                "context_length": 128000,
                "cost_per_1k_tokens": 1.10,  # Input cost: $1.10/1M tokens
                "cost_per_1k_tokens_output": 4.40,  # Output cost: $4.40/1M tokens
                "max_output_tokens": 65536,
                "category": "reasoning",
                "speed": "medium",
                "reasoning": "excellent",
                "capabilities": ["text", "reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2025-06",
                "description": "Fast reasoning at lower cost"
            },
            "o4-mini": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.30,  # Input cost: $0.30/1M tokens
                "cost_per_1k_tokens_output": 1.20,  # Output cost: $1.20/1M tokens
                "max_output_tokens": 65536,
                "category": "reasoning",
                "speed": "fast",
                "reasoning": "good",
                "capabilities": ["text", "reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2025-06",
                "description": "Newest mini reasoning model"
            },

            # O-Series Reasoning Models (Updated)
            "o1": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.015,
                "max_output_tokens": 65536,
                "category": "reasoning",
                "speed": "slow",
                "reasoning": "exceptional",
                "capabilities": ["text", "advanced_reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2023-10"
            },
            "o1-mini": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.003,
                "max_output_tokens": 65536,
                "category": "reasoning",
                "speed": "medium", 
                "reasoning": "excellent",
                "capabilities": ["text", "reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2023-10"
            },
            
            # GPT-4o Series (Legacy - Superseded by GPT-5 but kept for compatibility)
            "gpt-4o": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.0025,
                "max_output_tokens": 16384,
                "category": "large",
                "speed": "fast",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "function_calling", "json_mode"],
                "knowledge_cutoff": "2024-04"
            },
            "gpt-4o-2024-11-20": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.00250,
                "max_output_tokens": 16384,
                "category": "large",
                "speed": "fast",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "function_calling"],
                "knowledge_cutoff": "2024-04"
            },
            "gpt-4o-mini": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.00015,
                "max_output_tokens": 16384,
                "category": "small",
                "speed": "fastest",
                "reasoning": "good",
                "capabilities": ["text", "vision", "function_calling"],
                "knowledge_cutoff": "2024-07"
            },
            "gpt-4o-mini-2024-07-18": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.00015,
                "max_output_tokens": 16384,
                "category": "small",
                "speed": "fastest",
                "reasoning": "good",
                "capabilities": ["text", "vision", "function_calling"],
                "knowledge_cutoff": "2024-07"
            },
            
            # GPT-4 Turbo Series
            "gpt-4-turbo": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.01,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "medium",
                "reasoning": "excellent"
            },
            "gpt-4-turbo-preview": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.01,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "medium",
                "reasoning": "excellent"
            },
            "gpt-4-1106-preview": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.01,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "medium",
                "reasoning": "excellent"
            },
            "gpt-4-0613": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.03,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            "gpt-4-0314": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.03,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            "gpt-4": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.03,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            
            # GPT-3.5 Turbo Series
            "gpt-3.5-turbo": {
                "context_length": 16385,
                "cost_per_1k_tokens": 0.002,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "gpt-3.5-turbo-16k": {
                "context_length": 16385,
                "cost_per_1k_tokens": 0.004,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "gpt-3.5-turbo-0613": {
                "context_length": 4096,
                "cost_per_1k_tokens": 0.002,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "gpt-3.5-turbo-0301": {
                "context_length": 4096,
                "cost_per_1k_tokens": 0.002,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            
            # Note: Legacy models (text-ada-001, text-babbage-001, text-curie-001, text-davinci-003) 
            # were deprecated on January 4, 2024 and are no longer available
        }
    
    def _setup_models_metadata(self):
        """Setup metadata for all available models"""
        for model_id, config in self.model_configs.items():
            capabilities = [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.STRUCTURED_OUTPUT,
                ModelCapability.STREAMING
            ]
            
            # Add function calling for newer models
            if model_id in ["gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-1106-preview", 
                           "gpt-4-0613", "gpt-4-0314", "gpt-4o", "gpt-4o-mini", 
                           "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-0301"]:
                capabilities.append(ModelCapability.FUNCTION_CALLING)
            
            # Add vision for vision-capable models
            if model_id in ["gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-1106-preview", 
                           "gpt-4-0613", "gpt-4-0314", "gpt-4", "gpt-4o", "gpt-4o-mini"]:
                capabilities.append(ModelCapability.VISION)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"OpenAI {model_id}",
                capabilities=capabilities,
                context_length=config.get("context_length", 4096),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.002),
                max_output_tokens=config.get("max_output_tokens", 4096),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            if not self.api_key:
                logger.warning("OpenAI API key not provided, provider will be disabled")
                return False
            
            # Validate API key format
            is_valid, error_msg = APIKeyValidator.validate_api_key("openai", self.api_key)
            if not is_valid:
                logger.error(f"Invalid OpenAI API key format: {error_msg}")
                sanitized_key = APIKeyValidator.sanitize_api_key(self.api_key)
                logger.debug(f"API key provided: {sanitized_key}")
                return False
            
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                organization=self.organization,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            # Test connection with a simple request
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("OpenAI provider initialized successfully")
                return True
            else:
                logger.error(f"OpenAI provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using OpenAI models"""
        start_time = time.time()
        
        try:
            if not self.client:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="Provider not initialized"
                )
            
            # Prepare messages
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare parameters - handle temperature for different models
            params = {
                "model": model_id,
                "messages": messages,
                "stream": request.stream
            }
            
            # Only add temperature if it's not the default for newer models
            temp_value = request.temperature or self.default_temperature
            if temp_value != 1.0:  # Only set if not default
                params["temperature"] = temp_value
            
            # Handle max_tokens vs max_completion_tokens for newer models
            if request.max_tokens:
                # Use max_completion_tokens for newer models
                if "gpt-5" in model_id or "gpt-4" in model_id:
                    params["max_completion_tokens"] = request.max_tokens
                else:
                    params["max_tokens"] = request.max_tokens
            
            # Add stop sequences if provided
            if request.stop_sequences:
                params["stop"] = request.stop_sequences
            
            # Filter out invalid parameters for OpenAI API
            if request.extra_params:
                valid_params = {k: v for k, v in request.extra_params.items() 
                               if not k.startswith('_smart_routing')}
                params.update(valid_params)
            
            # Make API call with retry logic and timeout
            retry_config = RetryConfig(
                max_attempts=self.config.get('max_retries', 3),
                initial_delay=1.0,
                exponential_base=2.0,
                retryable_exceptions=(
                    ConnectionError,
                    TimeoutError,
                    asyncio.TimeoutError,
                    Exception,  # OpenAI API errors
                ),
                circuit_breaker_enabled=True,
                failure_threshold=5,
                recovery_timeout=60.0
            )
            
            # Apply timeout
            timeout = self.config.get('timeout', 60)
            
            async def api_call_with_timeout():
                return await asyncio.wait_for(
                    self.client.chat.completions.create(**params),
                    timeout=timeout
                )
            
            response = await retry_manager.retry_async(
                api_call_with_timeout,
                config=retry_config,
                circuit_breaker_name=f"openai_{model_id}"
            )
            
            # Validate response format
            is_valid, error_msg = ResponseValidator.validate_openai_response(response)
            if not is_valid:
                logger.warning(f"Malformed OpenAI response: {error_msg}")
                # Try to extract content anyway
                content = ResponseValidator.extract_safe_content(response, "openai")
                if not content:
                    raise ValueError(f"Failed to extract content from response: {error_msg}")
            else:
                # Extract response data normally
                content = response.choices[0].message.content or ""
            
            usage = response.usage if hasattr(response, 'usage') else None
            
            # Calculate cost if usage data available
            if usage:
                cost = self.calculate_cost(
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    model_id
                )
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
            else:
                cost = 0.0
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0
                logger.warning("No usage data in response, cost tracking unavailable")
            
            return GenerationResponse(
                content=content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                response_time=time.time() - start_time,
                raw_response=response
            )
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    async def generate_structured_output(
        self, 
        request: GenerationRequest, 
        model_id: str
    ) -> GenerationResponse:
        """Generate structured JSON output using OpenAI models"""
        if not request.output_schema:
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error="No output schema provided for structured output"
            )
        
        # Use function calling for structured output
        enhanced_request = GenerationRequest(
            prompt=request.prompt,
            system_message=request.system_message,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop_sequences=request.stop_sequences,
            stream=False,  # Structured output doesn't support streaming
            extra_params={
                "tools": [{
                    "type": "function",
                    "function": {
                        "name": "structured_response",
                        "description": "Generate structured response according to schema",
                        "parameters": request.output_schema
                    }
                }],
                "tool_choice": {"type": "function", "function": {"name": "structured_response"}}
            }
        )
        
        response = await self.generate_text(enhanced_request, model_id)
        
        if response.error:
            return response
        
        try:
            # Extract function call result
            raw_response = response.raw_response
            if (raw_response and 
                raw_response.choices[0].message.tool_calls and 
                len(raw_response.choices[0].message.tool_calls) > 0):
                
                function_args = raw_response.choices[0].message.tool_calls[0].function.arguments
                # Validate JSON
                json.loads(function_args)
                response.content = function_args
            else:
                response.error = "No function call in response"
                
        except json.JSONDecodeError as e:
            response.error = f"Invalid JSON in structured output: {str(e)}"
        except Exception as e:
            response.error = f"Error processing structured output: {str(e)}"
        
        return response
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available OpenAI models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test with a simple request
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_available": len(self._models_metadata),
                "test_response": response.choices[0].message.content[:50] if response.choices[0].message.content else ""
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended OpenAI model for specific use case"""
        if complexity == "simple":
            return "gpt-4o-mini"  # Fastest and cheapest
        elif complexity == "complex":
            return "gpt-4-turbo"  # Most capable
        else:
            return "gpt-4o"  # Best balance
