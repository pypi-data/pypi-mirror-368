"""
ModelBridge - Enterprise-Grade Multi-Provider LLM Gateway
"""

__version__ = "0.1.0"
__author__ = "ModelBridge Contributors"
__email__ = "support@modelbridge.ai"

# Import main components
from .bridge import ModelBridge, IntelligentRouter
from .providers.base import (
    BaseModelProvider,
    GenerationRequest,
    GenerationResponse,
    ModelMetadata,
    ModelCapability,
)

# Export main classes
__all__ = [
    "ModelBridge",
    "IntelligentRouter",
    "BaseModelProvider",
    "GenerationRequest", 
    "GenerationResponse",
    "ModelMetadata",
    "ModelCapability",
]

# Convenience function
async def create_bridge(config_path=None):
    """Create and initialize a ModelBridge instance"""
    bridge = ModelBridge(config_path)
    await bridge.initialize()
    return bridge