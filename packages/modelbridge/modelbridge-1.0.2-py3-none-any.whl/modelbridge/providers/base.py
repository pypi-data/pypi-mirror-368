"""
Base Provider Interface for Unified Model Gateway
All model providers must implement this interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ModelCapability(Enum):
    """Capabilities that models can support"""
    TEXT_GENERATION = "text_generation"
    STRUCTURED_OUTPUT = "structured_output"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    EMBEDDINGS = "embeddings"
    STREAMING = "streaming"


@dataclass
class ModelMetadata:
    """Metadata about a specific model"""
    model_id: str
    provider_name: str
    model_name: str
    capabilities: List[ModelCapability]
    context_length: int
    cost_per_1k_tokens: float
    max_output_tokens: int
    supports_system_messages: bool = True
    supports_temperature: bool = True


@dataclass
class GenerationRequest:
    """Unified request format for all providers"""
    prompt: str
    system_message: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    stream: bool = False
    
    # Structured output specific
    output_schema: Optional[Dict[str, Any]] = None
    
    # Provider-specific parameters
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResponse:
    """Unified response format from all providers"""
    content: str
    model_id: str
    provider_name: str
    
    # Usage and metadata
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost: Optional[float] = None
    response_time: Optional[float] = None
    
    # Raw response for debugging
    raw_response: Optional[Any] = None
    
    # Error information
    error: Optional[str] = None
    
    def is_success(self) -> bool:
        """Check if the generation was successful"""
        return self.error is None and self.content is not None


class BaseModelProvider(ABC):
    """
    Abstract base class that all model providers must implement
    """
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.provider_config = provider_config
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self._models_metadata: Dict[str, ModelMetadata] = {}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the provider (API keys, connections, etc.)
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """
        Generate text using the specified model
        
        Args:
            request: The generation request
            model_id: The specific model to use
            
        Returns:
            GenerationResponse with the result
        """
        pass
    
    @abstractmethod
    async def generate_structured_output(
        self, 
        request: GenerationRequest, 
        model_id: str
    ) -> GenerationResponse:
        """
        Generate structured JSON output using the specified model
        
        Args:
            request: The generation request (must include output_schema)
            model_id: The specific model to use
            
        Returns:
            GenerationResponse with JSON content
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelMetadata]:
        """
        Get list of models available from this provider
        
        Returns:
            List of ModelMetadata objects
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the provider is healthy and responsive
        
        Returns:
            Dict with health status information
        """
        pass
    
    # Optional methods that providers can override
    
    def supports_capability(self, model_id: str, capability: ModelCapability) -> bool:
        """Check if a model supports a specific capability"""
        if model_id in self._models_metadata:
            return capability in self._models_metadata[model_id].capabilities
        return False
    
    def get_model_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """Get metadata for a specific model"""
        return self._models_metadata.get(model_id)
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model_id: str) -> float:
        """Calculate cost for a request"""
        metadata = self.get_model_metadata(model_id)
        if metadata:
            total_tokens = prompt_tokens + completion_tokens
            return (total_tokens / 1000) * metadata.cost_per_1k_tokens
        return 0.0
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended model for a specific capability and complexity"""
        # Default implementation - providers can override with smarter logic
        available_models = self.get_available_models()
        
        # Filter models that support the capability
        suitable_models = [
            model for model in available_models 
            if capability in model.capabilities
        ]
        
        if not suitable_models:
            return None
        
        # Simple heuristic: choose based on complexity
        if complexity == "simple":
            # Choose fastest/cheapest model
            return min(suitable_models, key=lambda m: m.cost_per_1k_tokens).model_id
        elif complexity == "complex":
            # Choose most capable model
            return max(suitable_models, key=lambda m: m.context_length).model_id
        else:
            # Choose balanced model
            return suitable_models[len(suitable_models) // 2].model_id
    
    def __str__(self) -> str:
        return f"{self.provider_name}Provider"
    
    def __repr__(self) -> str:
        models = len(self.get_available_models())
        return f"{self.__class__.__name__}(models={models})"