"""
Test that all imports work correctly
"""
import pytest


def test_main_imports():
    """Test that main ModelBridge components can be imported"""
    from modelbridge import ModelBridge, IntelligentRouter
    from modelbridge import BaseModelProvider, GenerationRequest, GenerationResponse
    assert ModelBridge is not None
    assert IntelligentRouter is not None
    assert BaseModelProvider is not None
    assert GenerationRequest is not None
    assert GenerationResponse is not None


def test_provider_imports():
    """Test that all providers can be imported"""
    from modelbridge.providers.openai import OpenAIProvider
    from modelbridge.providers.anthropic import AnthropicProvider
    from modelbridge.providers.google import GoogleProvider
    from modelbridge.providers.groq import GroqProvider
    
    assert OpenAIProvider is not None
    assert AnthropicProvider is not None
    assert GoogleProvider is not None
    assert GroqProvider is not None


def test_base_classes():
    """Test that base classes are properly defined"""
    from modelbridge.providers.base import (
        BaseModelProvider, 
        GenerationRequest, 
        GenerationResponse, 
        ModelMetadata, 
        ModelCapability
    )
    
    # Test that these are classes/enums we can instantiate
    assert hasattr(BaseModelProvider, '__init__')
    assert hasattr(GenerationRequest, '__init__')
    assert hasattr(GenerationResponse, '__init__')
    assert hasattr(ModelMetadata, '__init__')
    assert hasattr(ModelCapability, 'TEXT_GENERATION')


def test_convenience_function():
    """Test the convenience create_bridge function"""
    from modelbridge import create_bridge
    assert create_bridge is not None
    assert callable(create_bridge)