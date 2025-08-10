"""
Anthropic Provider for Unified Model Bridge
Supports Claude 3 models with latest Anthropic SDK
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
import logging

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseModelProvider):
    """Anthropic Claude provider with proper error handling and standard patterns"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[AsyncAnthropic] = None
        self.api_key = provider_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = provider_config.get("base_url", "https://api.anthropic.com")
        self.default_temperature = provider_config.get("temperature", 0.1)
        self.timeout = provider_config.get("timeout", 60)
        self.max_retries = provider_config.get("max_retries", 3)
        
        # Load models from config with defaults
        self.model_configs = provider_config.get("models", self._get_default_models())
        self._setup_models_metadata()
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Get default Anthropic model configurations - Updated August 2025"""
        return {
            # Claude 4 Series (Latest August 2025)
            "claude-opus-4-1": {
                "context_length": 200000,
                "cost_per_1k_tokens": 15.00,  # Input cost: $15/1M tokens
                "cost_per_1k_tokens_output": 75.00,  # Output cost: $75/1M tokens
                "max_output_tokens": 32768,
                "category": "flagship",
                "speed": "slow",
                "reasoning": "exceptional",
                "capabilities": ["text", "vision", "advanced_reasoning", "coding", "mathematics", "tool_use"],
                "knowledge_cutoff": "2025-03",
                "description": "Most capable. Best for complex analysis"
            },
            "claude-opus-4": {
                "context_length": 200000,
                "cost_per_1k_tokens": 15.00,  # Input cost: $15/1M tokens
                "cost_per_1k_tokens_output": 75.00,  # Output cost: $75/1M tokens
                "max_output_tokens": 32768,
                "category": "flagship",
                "speed": "slow",
                "reasoning": "exceptional",
                "capabilities": ["text", "vision", "advanced_reasoning", "coding", "mathematics", "tool_use"],
                "knowledge_cutoff": "2025-03",
                "description": "Previous Opus version"
            },
            "claude-sonnet-4": {
                "context_length": 200000,
                "cost_per_1k_tokens": 3.00,   # Input cost: $3/1M tokens
                "cost_per_1k_tokens_output": 15.00,  # Output cost: $15/1M tokens
                "max_output_tokens": 64000,
                "category": "balanced",
                "speed": "medium",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "reasoning", "coding", "mathematics", "tool_use"],
                "knowledge_cutoff": "2025-03",
                "description": "Balanced performance and cost",
                "features": ["balanced_performance", "high_output_capacity", "cost_effective"]
            },

            # Claude 3.5 Series (Legacy but still excellent)
            "claude-3-5-sonnet-20241022": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.003,
                "max_output_tokens": 8192,
                "category": "large",
                "speed": "fast",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "code", "analysis", "tool_use"],
                "knowledge_cutoff": "2024-04",
                "multimodal": True
            },
            "claude-3-5-sonnet-20240620": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.003,
                "max_output_tokens": 8192,
                "category": "large",
                "speed": "fast",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "code", "analysis", "tool_use"],
                "knowledge_cutoff": "2024-04",
                "multimodal": True
            },
            "claude-3-5-haiku-20241022": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.0008,
                "max_output_tokens": 8192,
                "category": "small",
                "speed": "fastest",
                "reasoning": "good",
                "capabilities": ["text", "vision", "tool_use"],
                "knowledge_cutoff": "2024-07",
                "multimodal": True
            },
            
            # Claude 3 Series
            "claude-3-opus-20240229": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.015,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "superior"
            },
            "claude-3-sonnet-20240229": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.003,
                "max_output_tokens": 4096,
                "category": "medium",
                "speed": "medium",
                "reasoning": "excellent"
            },
            "claude-3-haiku-20240307": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.00025,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fastest",
                "reasoning": "good"
            },
            
            # Claude 2 Series
            "claude-2.1": {
                "context_length": 100000,
                "cost_per_1k_tokens": 0.008,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            "claude-2.0": {
                "context_length": 100000,
                "cost_per_1k_tokens": 0.008,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            
            # Claude Instant Series
            "claude-instant-1.2": {
                "context_length": 100000,
                "cost_per_1k_tokens": 0.00163,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "claude-instant-1.1": {
                "context_length": 100000,
                "cost_per_1k_tokens": 0.00163,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            }
        }
    
    def _setup_models_metadata(self):
        """Setup metadata for all available models"""
        for model_id, config in self.model_configs.items():
            capabilities = [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.STRUCTURED_OUTPUT,
                ModelCapability.FUNCTION_CALLING
            ]
            
            # Add vision for newer Claude models (Claude 3 and 3.5 series)
            if "claude-3" in model_id and model_id != "claude-3-haiku-20240307":
                capabilities.append(ModelCapability.VISION)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"Anthropic {model_id}",
                capabilities=capabilities,
                context_length=config.get("context_length", 200000),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.003),
                max_output_tokens=config.get("max_output_tokens", 4096),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize Anthropic client"""
        try:
            if not ANTHROPIC_AVAILABLE:
                logger.warning("Anthropic SDK not available, install with: pip install anthropic")
                return False
            
            if not self.api_key:
                logger.warning("Anthropic API key not provided, provider will be disabled")
                return False
            
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            
            # Test connection
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("Anthropic provider initialized successfully")
                return True
            else:
                logger.error(f"Anthropic provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Anthropic Claude models"""
        start_time = time.time()
        
        try:
            if not self.client:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="Provider not initialized"
                )
            
            # Prepare parameters following Anthropic's API format
            params = {
                "model": model_id,
                "max_tokens": request.max_tokens or 4096,
                "temperature": request.temperature if request.temperature is not None else self.default_temperature,
                "messages": [{"role": "user", "content": request.prompt}]
            }
            
            # Add system message if provided
            if request.system_message:
                params["system"] = request.system_message
            
            # Add stop sequences if provided
            if request.stop_sequences:
                params["stop_sequences"] = request.stop_sequences
            
            # Add extra parameters
            if request.extra_params:
                # Filter out parameters that Anthropic doesn't support
                allowed_params = ["top_p", "top_k", "metadata"]
                for key, value in request.extra_params.items():
                    if key in allowed_params:
                        params[key] = value
            
            # Make API call
            response = await self.client.messages.create(**params)
            
            # Extract response data
            content = ""
            if response.content and len(response.content) > 0:
                content = response.content[0].text
            
            # Calculate cost
            cost = self.calculate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens,
                model_id
            )
            
            return GenerationResponse(
                content=content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                cost=cost,
                response_time=time.time() - start_time,
                raw_response=response
            )
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {str(e)}")
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
        """Generate structured JSON output using Anthropic models"""
        if not request.output_schema:
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error="No output schema provided for structured output"
            )
        
        # For Anthropic, we use prompt engineering for structured output
        schema_str = json.dumps(request.output_schema, indent=2)
        structured_prompt = f"""{request.prompt}

Please respond with a valid JSON object that matches this exact schema:
{schema_str}

Your response should contain ONLY the JSON object, no additional text or formatting."""
        
        enhanced_request = GenerationRequest(
            prompt=structured_prompt,
            system_message=request.system_message,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop_sequences=request.stop_sequences,
            stream=False
        )
        
        response = await self.generate_text(enhanced_request, model_id)
        
        if response.error:
            return response
        
        try:
            # Validate that the response is valid JSON
            parsed_json = json.loads(response.content)
            # Ensure it's formatted as a string
            response.content = json.dumps(parsed_json)
            
        except json.JSONDecodeError as e:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group()
                    parsed_json = json.loads(json_str)
                    response.content = json.dumps(parsed_json)
                except json.JSONDecodeError:
                    response.error = f"Invalid JSON in structured output: {str(e)}"
            else:
                response.error = f"No valid JSON found in response: {str(e)}"
        except Exception as e:
            response.error = f"Error processing structured output: {str(e)}"
        
        return response
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available Anthropic models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Anthropic provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test with a simple request
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            content = ""
            if response.content and len(response.content) > 0:
                content = response.content[0].text[:50]
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_available": len(self._models_metadata),
                "test_response": content
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Anthropic model for specific use case"""
        if complexity == "simple":
            return "claude-3-haiku-20240307"  # Fastest and cheapest
        elif complexity == "complex":
            return "claude-3-opus-20240229"  # Most capable
        else:
            return "claude-3-5-sonnet-20241022"  # Best balance