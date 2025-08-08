"""
Groq Provider for Ultra-Fast LLM Inference
Supports Llama, Mixtral, and other models with lightning-fast inference
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
from groq import AsyncGroq

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
import logging

logger = logging.getLogger(__name__)


class GroqProvider(BaseModelProvider):
    """Groq provider for ultra-fast inference"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[AsyncGroq] = None
        self.api_key = provider_config.get("api_key") or os.getenv("GROQ_API_KEY")
        self.base_url = provider_config.get("base_url", "https://api.groq.com/openai/v1")
        self.default_temperature = provider_config.get("temperature", 0.1)
        self.timeout = provider_config.get("timeout", 30)
        
        # Load models from config with defaults
        self.model_configs = provider_config.get("models", self._get_default_models())
        self._setup_models_metadata()
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Get default Groq model configurations - Updated August 2025"""
        return {
            # Llama 3.3 Series (LATEST - 2025) 🚀 - Ultra Fast Performance
            "llama-3.3-70b-versatile": {
                "context_length": 32768,
                "cost_per_1k_tokens": 0.00059,  # Input cost
                "cost_per_1k_tokens_output": 0.00079,  # Output cost
                "max_output_tokens": 8192,
                "category": "large",
                "speed": "ultra_fast",
                "reasoning": "excellent",
                "performance": {
                    "tokens_per_second": 276,  # 276 tokens/second
                    "description": "Latest Meta model with enhanced performance"
                },
                "features": ["latest_meta_model", "ultra_fast_inference", "balanced_performance"],
                "knowledge_cutoff": "2024-12"
            },

            # Llama 3.1 Series - Proven Performance
            "llama-3.1-405b-reasoning": {
                "context_length": 131072,
                "cost_per_1k_tokens": 0.00059,
                "max_output_tokens": 8192,
                "category": "large",
                "speed": "fast",
                "reasoning": "exceptional",
                "specialty": "reasoning"
            },
            "llama-3.1-70b-versatile": {
                "context_length": 131072,
                "cost_per_1k_tokens": 0.00059,
                "max_output_tokens": 8192,
                "category": "large", 
                "speed": "ultra_fast",
                "reasoning": "excellent"
            },
            "llama-3.1-8b-instant": {
                "context_length": 131072,
                "cost_per_1k_tokens": 0.00005,
                "max_output_tokens": 8192,
                "category": "small",
                "speed": "lightning",
                "reasoning": "good"
            },
            
            # Llama 3 Series - Stable and Reliable
            "llama3-70b-8192": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.00059,
                "max_output_tokens": 8192,
                "category": "large",
                "speed": "ultra_fast",
                "reasoning": "excellent"
            },
            "llama3-8b-8192": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.00005,
                "max_output_tokens": 8192,
                "category": "small",
                "speed": "lightning",
                "reasoning": "good"
            },
            
            # Mixtral Series - Mixture of Experts (FASTEST MODEL AVAILABLE!) 🚀
            "mixtral-8x7b-32768": {
                "context_length": 32768,
                "cost_per_1k_tokens": 0.00027,  # ~$0.27 per 1M tokens
                "max_output_tokens": 32768,
                "category": "medium",
                "speed": "lightning",  # FASTEST IN THE WORLD!
                "reasoning": "excellent",
                "performance": {
                    "tokens_per_second": 500,  # 500+ tokens/second - WORLD RECORD!
                    "description": "Fastest model available anywhere"
                },
                "features": ["mixture_of_experts", "world_fastest_inference", "excellent_quality"]
            },
            
            # Gemma 2 Series - Google's Models on Groq
            "gemma2-9b-it": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.00002,
                "max_output_tokens": 8192,
                "category": "small",
                "speed": "lightning",
                "reasoning": "good"
            },
            "gemma-7b-it": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.0001,
                "max_output_tokens": 8192,
                "category": "small",
                "speed": "lightning", 
                "reasoning": "basic"
            }
        }
    
    def _setup_models_metadata(self):
        """Setup metadata for all available models"""
        for model_id, config in self.model_configs.items():
            capabilities = [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.STREAMING
            ]
            
            # Add structured output for compatible models
            if "llama" in model_id.lower() or "mixtral" in model_id.lower():
                capabilities.append(ModelCapability.STRUCTURED_OUTPUT)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"Groq {model_id}",
                capabilities=capabilities,
                context_length=config.get("context_length", 8192),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.0001),
                max_output_tokens=config.get("max_output_tokens", 4096),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize Groq client"""
        try:
            if not self.api_key:
                logger.warning("Groq API key not provided, provider will be disabled")
                return False
            
            self.client = AsyncGroq(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            # Test connection
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("Groq provider initialized successfully")
                return True
            else:
                logger.error(f"Groq provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Groq provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Groq models"""
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
            
            # Prepare parameters
            params = {
                "model": model_id,
                "messages": messages,
                "temperature": request.temperature or self.default_temperature,
                "stream": request.stream
            }
            
            # Add max_tokens if specified
            if request.max_tokens:
                params["max_tokens"] = request.max_tokens
            
            # Add stop sequences if provided
            if request.stop_sequences:
                params["stop"] = request.stop_sequences
            
            # Add extra parameters
            if request.extra_params:
                params.update(request.extra_params)
            
            # Make API call
            response = await self.client.chat.completions.create(**params)
            
            # Extract response data
            content = response.choices[0].message.content or ""
            usage = response.usage
            
            # Calculate cost (Groq is very cheap)
            cost = self.calculate_cost(
                usage.prompt_tokens,
                usage.completion_tokens,
                model_id
            )
            
            return GenerationResponse(
                content=content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost,
                response_time=time.time() - start_time,
                raw_response=response
            )
            
        except Exception as e:
            logger.error(f"Groq generation error: {str(e)}")
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
        """Generate structured JSON output using Groq models"""
        if not request.output_schema:
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error="No output schema provided for structured output"
            )
        
        # Add JSON schema instruction to prompt
        schema_prompt = f"""
{request.prompt}

Please respond with valid JSON that matches this schema:
{json.dumps(request.output_schema, indent=2)}

Respond only with the JSON, no additional text.
"""
        
        enhanced_request = GenerationRequest(
            prompt=schema_prompt,
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
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Validate JSON
            json.loads(content)
            response.content = content
            
        except json.JSONDecodeError as e:
            response.error = f"Invalid JSON in structured output: {str(e)}"
        except Exception as e:
            response.error = f"Error processing structured output: {str(e)}"
        
        return response
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available Groq models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Groq provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test with a simple request using the fastest model
            test_model = "llama3-8b-8192"
            if test_model not in self.model_configs:
                # Fallback to first available model
                test_model = list(self.model_configs.keys())[0] if self.model_configs else "llama3-8b-8192"
            
            response = await self.client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_available": len(self._models_metadata),
                "test_response": response.choices[0].message.content[:50] if response.choices[0].message.content else "",
                "speed": "ultra_fast"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Groq model for specific use case"""
        if complexity == "simple":
            return "llama3-8b-8192"  # Fastest
        elif complexity == "complex":
            return "llama3-70b-8192"  # Most capable
        else:
            return "mixtral-8x7b-32768"  # Good balance
