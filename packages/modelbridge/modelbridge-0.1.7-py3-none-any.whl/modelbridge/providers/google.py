"""
Google Gemini Provider for Unified Model Bridge
Handles all Google AI models including Gemini Pro, Gemini Flash, etc.
"""
import os
import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    LANGCHAIN_GOOGLE_AVAILABLE = True
except ImportError:
    LANGCHAIN_GOOGLE_AVAILABLE = False
    ChatGoogleGenerativeAI = None
    GoogleGenerativeAIEmbeddings = None
from langchain_core.messages import HumanMessage, SystemMessage

from .base import (
    BaseModelProvider, 
    GenerationRequest, 
    GenerationResponse, 
    ModelMetadata, 
    ModelCapability
)
import logging

logger = logging.getLogger(__name__)


class GoogleProvider(BaseModelProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.provider_name = "google"
        self.provider_config = provider_config
        self.api_key = provider_config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        self.chat_models = {}
        self.embeddings_model = None
        self._initialized = False
        self._models_metadata = {}
    
    async def initialize(self) -> bool:
        """Initialize Google provider and models"""
        if self._initialized:
            return True
        
        try:
            if not LANGCHAIN_GOOGLE_AVAILABLE:
                logger.warning("langchain-google-genai not available, Google provider will be disabled")
                return False
                
            if not self.api_key:
                logger.error("Google API key not found. Set GOOGLE_API_KEY environment variable.")
                return False
            
            # Define available models with metadata - Updated August 2025
            self._models_metadata = {
                # Gemini 2.5 Series (LATEST - Released 2025) 🚀
                "gemini-2.5-pro": ModelMetadata(
                    model_id="gemini-2.5-pro",
                    model_name="Gemini 2.5 Pro",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL,
                        ModelCapability.AUDIO_INPUT,
                        ModelCapability.VIDEO_INPUT
                    ],
                    context_length=1000000,  # 1M tokens, expanding to 2M
                    cost_per_1k_tokens=0.00250,  # Estimated competitive pricing
                    max_output_tokens=32768,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2025-06",
                    metadata={
                        "reasoning_capability": "86.7% AIME 2025",
                        "coding_capability": "63.8% SWE-bench Verified",
                        "multimodal_capability": "81.7% MMMU benchmark (industry leading)",
                        "features": ["thinking_capabilities", "tool_use", "grounding_with_search"]
                    }
                ),
                "gemini-2.5-flash": ModelMetadata(
                    model_id="gemini-2.5-flash",
                    model_name="Gemini 2.5 Flash",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL
                    ],
                    context_length=1000000,  # 1M tokens
                    cost_per_1k_tokens=0.00075,  # Fast and cost-effective
                    max_output_tokens=16384,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2025-06",
                    metadata={
                        "speed": "250+ tokens/second",
                        "ttft": "0.25s TTFT",
                        "features": ["ultra_fast", "thinking_capabilities", "well_rounded"]
                    }
                ),
                "gemini-2.5-flash-lite": ModelMetadata(
                    model_id="gemini-2.5-flash-lite",
                    model_name="Gemini 2.5 Flash Lite",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING
                    ],
                    context_length=1000000,
                    cost_per_1k_tokens=0.0001,  # Ultra-cheap: $0.10/$0.40 per 1M tokens
                    max_output_tokens=8192,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2025-06",
                    metadata={
                        "cost_optimization": "Most cost-effective option",
                        "batch_processing": "50% discount available",
                        "features": ["ultra_cheap", "high_volume", "basic_reasoning"]
                    }
                ),

                # Gemini 1.5 Series (Legacy but still available)
                "gemini-1.5-pro": ModelMetadata(
                    model_id="gemini-1.5-pro",
                    model_name="Gemini 1.5 Pro",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL
                    ],
                    context_length=2000000,
                    cost_per_1k_tokens=0.00125,
                    max_output_tokens=8192,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2024-04"
                ),
                "gemini-1.5-pro-002": ModelMetadata(
                    model_id="gemini-1.5-pro-002",
                    model_name="Gemini 1.5 Pro 002",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL
                    ],
                    context_length=2000000,
                    cost_per_1k_tokens=0.00125,
                    max_output_tokens=8192,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2024-10"
                ),
                "gemini-1.5-flash": ModelMetadata(
                    model_id="gemini-1.5-flash",
                    model_name="Gemini 1.5 Flash",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL
                    ],
                    context_length=1000000,
                    cost_per_1k_tokens=0.000075,
                    max_output_tokens=8192,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2024-12"
                ),
                "gemini-1.5-flash-002": ModelMetadata(
                    model_id="gemini-1.5-flash-002",
                    model_name="Gemini 1.5 Flash 002",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL
                    ],
                    context_length=1000000,
                    cost_per_1k_tokens=0.000075,
                    max_output_tokens=8192,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2024-10"
                ),
                "gemini-1.5-pro-latest": ModelMetadata(
                    model_id="gemini-1.5-pro-latest",
                    model_name="Gemini 1.5 Pro Latest",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL
                    ],
                    context_length=2000000,
                    cost_per_1k_tokens=0.00125,
                    max_output_tokens=8192,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2024-04"
                ),
                "gemini-1.5-flash-latest": ModelMetadata(
                    model_id="gemini-1.5-flash-latest",
                    model_name="Gemini 1.5 Flash Latest",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION,
                        ModelCapability.MULTIMODAL
                    ],
                    context_length=1000000,
                    cost_per_1k_tokens=0.000075,
                    max_output_tokens=8192,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2024-12"
                ),
                
                # Gemini Pro Series (Legacy)
                "gemini-pro": ModelMetadata(
                    model_id="gemini-pro",
                    model_name="Gemini Pro",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING
                    ],
                    context_length=32768,
                    cost_per_1k_tokens=0.0005,
                    max_output_tokens=2048,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2023-08"
                ),
                "gemini-pro-vision": ModelMetadata(
                    model_id="gemini-pro-vision",
                    model_name="Gemini Pro Vision",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.FUNCTION_CALLING,
                        ModelCapability.VISION
                    ],
                    context_length=32768,
                    cost_per_1k_tokens=0.0005,
                    max_output_tokens=2048,
                    supports_system_messages=True,
                    supports_temperature=True,
                    knowledge_cutoff="2023-08"
                )
            }
            
            # Initialize chat models
            for model_id, metadata in self._models_metadata.items():
                try:
                    self.chat_models[model_id] = ChatGoogleGenerativeAI(
                        model=metadata.model_name,
                        temperature=self.provider_config.get("temperature", 0.1),
                        max_tokens=metadata.max_output_tokens,
                        google_api_key=self.api_key
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize {model_id}: {str(e)}")
            
            # Initialize embeddings model
            try:
                self.embeddings_model = GoogleGenerativeAIEmbeddings(
                    model=self.provider_config.get("embedding_model", "models/embedding-001"),
                    google_api_key=self.api_key
                )
            except Exception as e:
                logger.warning(f"Failed to initialize embeddings model: {str(e)}")
            
            self._initialized = True
            logger.info(f"Google provider initialized with {len(self.chat_models)} models")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google provider: {str(e)}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Google Gemini"""
        start_time = time.time()
        
        try:
            if not self._initialized:
                await self.initialize()
            
            if model_id not in self.chat_models:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error=f"Model {model_id} not available"
                )
            
            # Prepare messages
            messages = []
            if request.system_message:
                messages.append(SystemMessage(content=request.system_message))
            messages.append(HumanMessage(content=request.prompt))
            
            # Get model
            model = self.chat_models[model_id]
            
            # Override model parameters if specified in request
            if request.temperature is not None or request.max_tokens is not None:
                model_params = {
                    "model": self._models_metadata[model_id].model_name,
                    "google_api_key": self.api_key,
                    "temperature": request.temperature or 0.1,
                    "max_tokens": request.max_tokens or self._models_metadata[model_id].max_output_tokens
                }
                model = ChatGoogleGenerativeAI(**model_params)
            
            # Generate response
            response = await model.ainvoke(messages)
            response_time = time.time() - start_time
            
            # Estimate token usage (Google doesn't always provide exact counts)
            prompt_tokens = self._estimate_tokens(request.prompt + (request.system_message or ""))
            completion_tokens = self._estimate_tokens(response.content)
            
            # Calculate cost
            cost = self.calculate_cost(prompt_tokens, completion_tokens, model_id)
            
            return GenerationResponse(
                content=response.content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost=cost,
                response_time=response_time,
                raw_response=response
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Google text generation failed: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                response_time=response_time,
                error=str(e)
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_structured_output(
        self, 
        request: GenerationRequest, 
        model_id: str
    ) -> GenerationResponse:
        """Generate structured JSON output using Google Gemini"""
        start_time = time.time()
        
        try:
            if not request.output_schema:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="output_schema is required for structured output"
                )
            
            # Create structured prompt
            schema_str = json.dumps(request.output_schema, indent=2)
            structured_prompt = f"""
            {request.prompt}
            
            IMPORTANT: Respond with valid JSON that matches this exact schema:
            {schema_str}
            
            Return only the JSON response, no additional text or formatting.
            """
            
            # Create new request with structured prompt
            structured_request = GenerationRequest(
                prompt=structured_prompt,
                system_message=request.system_message,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stop_sequences=request.stop_sequences,
                extra_params=request.extra_params
            )
            
            # Generate response
            response = await self.generate_text(structured_request, model_id)
            
            if response.error:
                return response
            
            # Parse JSON response
            try:
                parsed_content = json.loads(response.content)
                response.content = json.dumps(parsed_content)  # Ensure valid JSON formatting
                return response
            except json.JSONDecodeError as e:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    try:
                        parsed_content = json.loads(json_match.group())
                        response.content = json.dumps(parsed_content)
                        return response
                    except json.JSONDecodeError:
                        pass
                
                response.error = f"Invalid JSON response: {str(e)}"
                return response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Google structured output failed: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                response_time=response_time,
                error=str(e)
            )
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available Google models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Google provider health"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Try a simple request with the fastest model
            test_request = GenerationRequest(
                prompt="Say 'OK' if you can hear me.",
                temperature=0.1,
                max_tokens=10
            )
            
            response = await self.generate_text(test_request, "gemini-1.5-flash")
            
            return {
                "provider": self.provider_name,
                "status": "healthy" if response.is_success() else "unhealthy",
                "available_models": len(self.chat_models),
                "initialized": self._initialized,
                "test_response": response.content if response.is_success() else response.error,
                "response_time": response.response_time
            }
            
        except Exception as e:
            return {
                "provider": self.provider_name,
                "status": "unhealthy",
                "error": str(e),
                "initialized": self._initialized
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Google model based on capability and complexity"""
        if complexity == "simple":
            return "gemini-1.5-flash"  # Fastest and cheapest
        elif complexity == "complex":
            return "gemini-1.5-pro"    # Most capable
        else:
            return "gemini-pro"        # Balanced option
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count (4 chars per token average)"""
        return max(1, len(text) // 4)
    
    # Embeddings support
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google's embedding model"""
        try:
            if not self.embeddings_model:
                logger.error("Embeddings model not initialized")
                return []
            
            embeddings = await self.embeddings_model.aembed_documents(texts)
            return embeddings
            
        except Exception as e:
            logger.error(f"Google embeddings generation failed: {str(e)}")
            return []