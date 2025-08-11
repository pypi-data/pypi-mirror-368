"""
ModelBridge - Simple Multi-Provider LLM Gateway
"""

__version__ = "0.1.7"
__author__ = "ModelBridge Contributors"
__email__ = "support@modelbridge.ai"

# Import main components
from .bridge import ModelBridge, IntelligentRouter
from .analyzer import TaskAnalyzer, TaskAnalysis
from .providers.base import (
    BaseModelProvider,
    GenerationRequest,
    GenerationResponse,
    ModelMetadata,
    ModelCapability,
)

# Import simplified API
from .simple import (
    ask,
    ask_json,
    ask_stream,
    code,
    translate,
    summarize,
)

# Export main classes and functions
__all__ = [
    # Core classes
    "ModelBridge",
    "IntelligentRouter", 
    "TaskAnalyzer",
    "TaskAnalysis",
    "BaseModelProvider",
    "GenerationRequest", 
    "GenerationResponse",
    "ModelMetadata",
    "ModelCapability",
    
    # Simple API - most users will use these
    "ask",
    "ask_json",
    "ask_stream",
    "code",
    "translate",
    "summarize",
    
    # Convenience function
    "create_bridge",
]

# Convenience function
async def create_bridge(config_path=None):
    """Create and initialize a ModelBridge instance"""
    bridge = ModelBridge(config_path)
    await bridge.initialize()
    return bridge