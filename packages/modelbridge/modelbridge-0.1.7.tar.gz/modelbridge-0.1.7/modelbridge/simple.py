"""
Simplified API for ModelBridge - Smart routing without complexity
The easiest way to use multiple LLM providers with automatic model selection
"""

import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, Union
import logging

from .bridge import ModelBridge
from .analyzer import TaskAnalyzer, TaskAnalysis
from .providers.base import GenerationResponse

logger = logging.getLogger(__name__)

# Global instances for convenience
_bridge_instance: Optional[ModelBridge] = None
_analyzer_instance: Optional[TaskAnalyzer] = None


async def _get_bridge() -> ModelBridge:
    """Get or create the global ModelBridge instance"""
    global _bridge_instance
    
    if _bridge_instance is None:
        _bridge_instance = ModelBridge()
        await _bridge_instance.initialize()
        
    return _bridge_instance


def _get_analyzer() -> TaskAnalyzer:
    """Get or create the global TaskAnalyzer instance"""
    global _analyzer_instance
    
    if _analyzer_instance is None:
        _analyzer_instance = TaskAnalyzer()
        
    return _analyzer_instance


async def ask(
    prompt: str,
    *,
    model: Optional[str] = None,
    optimize_for: Optional[str] = None,
    max_cost: Optional[float] = None,
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    debug: bool = False,
    **kwargs
) -> GenerationResponse:
    """
    Ask a question and get an intelligent response with automatic model selection.
    
    This is the main function for simple LLM interactions. The system automatically
    selects the best model based on your prompt unless you specify otherwise.
    
    Args:
        prompt: Your question or request
        model: Optional specific model to use (e.g., "gpt-5", "claude-opus-4-1")
               If None, system automatically selects optimal model
        optimize_for: Optional optimization hint - "speed", "cost", "quality"
                     If None, system balances all factors
        max_cost: Optional maximum cost per request in USD
                 System will choose cheaper models if needed
        system_message: Optional system prompt to set AI behavior
        temperature: Optional creativity level (0.0 to 1.0)
        max_tokens: Optional maximum response length
        debug: Show reasoning behind model selection
        **kwargs: Additional parameters passed to the provider
    
    Returns:
        GenerationResponse with content, metadata, and cost information
    
    Example:
        # Simple usage - system picks best model automatically
        response = await ask("Explain quantum computing")
        print(response.content)
        
        # With optimization preferences
        response = await ask(
            "Write a Python function to sort a list",
            optimize_for="speed"
        )
        
        # With cost constraints
        response = await ask(
            "Simple math question: what's 2+2?",
            max_cost=0.001  # Use cheapest model
        )
        
        # Force specific model if needed
        response = await ask(
            "Complex analysis needed",
            model="claude-opus-4-1"
        )
    """
    
    bridge = await _get_bridge()
    
    # If no model specified, use intelligent routing
    if model is None:
        analyzer = _get_analyzer()
        available_providers = list(bridge.providers.keys())
        
        analysis = analyzer.analyze(
            prompt=prompt,
            optimize_for=optimize_for,
            max_cost=max_cost,
            available_providers=available_providers
        )
        
        model = analysis.recommended_model
        
        if debug:
            print(f"🧠 Smart Routing Analysis:")
            print(f"   Task Type: {analysis.task_type}")
            print(f"   Complexity: {analysis.complexity_score}/10")
            print(f"   Selected Model: {analysis.recommended_model}")
            print(f"   Reasoning: {analysis.reasoning}")
            print(f"   Estimated Cost: ${analysis.estimated_cost:.4f}")
            print(f"   Estimated Speed: {analysis.estimated_speed}")
            print(f"   Confidence: {analysis.confidence:.1%}")
            print()
    
    # Make the request
    response = await bridge.generate_text(
        prompt=prompt,
        model=model,
        system_message=system_message,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    
    if debug and response:
        print(f"📊 Request Results:")
        print(f"   Provider Used: {response.provider_name}")
        print(f"   Model Used: {response.model_id}")
        print(f"   Response Time: {response.response_time:.2f}s")
        print(f"   Tokens Used: {response.total_tokens}")
        print(f"   Actual Cost: ${response.cost:.4f}")
        if response.error:
            print(f"   ❌ Error: {response.error}")
        else:
            print(f"   ✅ Success")
        print()
    
    return response


async def ask_json(
    prompt: str,
    schema: Dict[str, Any],
    *,
    model: Optional[str] = None,
    optimize_for: Optional[str] = None,
    max_cost: Optional[float] = None,
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    debug: bool = False,
    **kwargs
) -> GenerationResponse:
    """
    Ask for structured JSON output with automatic model selection.
    
    This function is perfect when you need the AI to return data in a specific
    JSON format. The system automatically picks models good at structured output.
    
    Args:
        prompt: Your question or request
        schema: JSON schema defining the expected output structure
        model: Optional specific model (auto-selected if None)
        optimize_for: "speed", "cost", "quality", or None for balanced
        max_cost: Maximum cost per request in USD
        system_message: Optional system prompt
        temperature: Creativity level (0.0 to 1.0)
        debug: Show model selection reasoning
        **kwargs: Additional parameters
    
    Returns:
        GenerationResponse with JSON content that matches your schema
    
    Example:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "skills": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["name", "age"]
        }
        
        response = await ask_json(
            "Extract info: John Doe, 30, knows Python and JavaScript",
            schema=schema
        )
        
        import json
        data = json.loads(response.content)
        print(data["name"])  # "John Doe"
    """
    
    bridge = await _get_bridge()
    
    # For structured output, prefer models known for accuracy
    if model is None:
        analyzer = _get_analyzer()
        available_providers = list(bridge.providers.keys())
        
        # Boost preference for structured output capable models
        modified_prompt = f"{prompt} [STRUCTURED_OUTPUT_TASK]"
        analysis = analyzer.analyze(
            prompt=modified_prompt,
            optimize_for=optimize_for or "quality",  # Default to quality for JSON
            max_cost=max_cost,
            available_providers=available_providers
        )
        
        model = analysis.recommended_model
        
        if debug:
            print(f"🧠 JSON Task Analysis:")
            print(f"   Selected Model: {analysis.recommended_model}")
            print(f"   Reasoning: {analysis.reasoning}")
            print()
    
    # Make the structured output request
    response = await bridge.generate_structured_output(
        prompt=prompt,
        schema=schema,
        model=model,
        system_message=system_message,
        temperature=temperature,
        **kwargs
    )
    
    if debug and response:
        print(f"📊 JSON Request Results:")
        print(f"   Provider: {response.provider_name}")
        print(f"   Model: {response.model_id}")
        print(f"   Cost: ${response.cost:.4f}")
        print(f"   Valid JSON: {'✅' if not response.error else '❌'}")
        if response.error:
            print(f"   Error: {response.error}")
        print()
    
    return response


async def ask_stream(
    prompt: str,
    *,
    model: Optional[str] = None,
    optimize_for: Optional[str] = None,
    max_cost: Optional[float] = None,
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    debug: bool = False,
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    Ask a question and get a streaming response (like ChatGPT).
    
    Perfect for building chat interfaces where you want to show the response
    as it's being generated, character by character.
    
    Args:
        prompt: Your question or request
        model: Optional specific model (auto-selected if None)
        optimize_for: "speed", "cost", "quality", or None for balanced
                     For streaming, "speed" is often preferred
        max_cost: Maximum cost per request in USD
        system_message: Optional system prompt
        temperature: Creativity level (0.0 to 1.0)
        debug: Show model selection reasoning
        **kwargs: Additional parameters
    
    Yields:
        str: Chunks of the response as they're generated
    
    Example:
        async for chunk in ask_stream("Write a short story about a robot"):
            print(chunk, end="", flush=True)  # Print as it generates
        print()  # New line when done
        
        # Or collect all chunks
        chunks = []
        async for chunk in ask_stream("Explain machine learning"):
            chunks.append(chunk)
        full_response = "".join(chunks)
    """
    
    # For streaming, prefer fast models unless specified
    if optimize_for is None:
        optimize_for = "speed"
    
    bridge = await _get_bridge()
    
    # Smart model selection for streaming
    if model is None:
        analyzer = _get_analyzer()
        available_providers = list(bridge.providers.keys())
        
        analysis = analyzer.analyze(
            prompt=prompt,
            optimize_for=optimize_for,
            max_cost=max_cost,
            available_providers=available_providers
        )
        
        model = analysis.recommended_model
        
        if debug:
            print(f"🧠 Streaming Analysis:")
            print(f"   Selected Model: {analysis.recommended_model}")
            print(f"   Reasoning: {analysis.reasoning}")
            print(f"   Expected Speed: {analysis.estimated_speed}")
            print()
    
    # Note: This is a placeholder for streaming implementation
    # The actual streaming would need to be implemented in the providers
    # For now, we'll simulate streaming by yielding chunks of a regular response
    
    response = await bridge.generate_text(
        prompt=prompt,
        model=model,
        system_message=system_message,
        temperature=temperature,
        stream=True,  # Enable streaming if supported
        **kwargs
    )
    
    if response.error:
        if debug:
            print(f"❌ Streaming Error: {response.error}")
        yield f"Error: {response.error}"
        return
    
    # TODO: Implement proper streaming when providers support it
    # For now, yield the full response in chunks to simulate streaming
    content = response.content
    chunk_size = 10  # Characters per chunk
    
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i + chunk_size]
        yield chunk
        await asyncio.sleep(0.05)  # Simulate streaming delay
    
    if debug:
        print(f"\n📊 Streaming Complete:")
        print(f"   Provider: {response.provider_name}")
        print(f"   Model: {response.model_id}")
        print(f"   Total Cost: ${response.cost:.4f}")


# Convenience functions for common tasks

async def code(
    prompt: str,
    language: Optional[str] = None,
    **kwargs
) -> GenerationResponse:
    """
    Generate code with automatic model selection optimized for coding tasks.
    
    Args:
        prompt: Description of the code you want
        language: Optional programming language hint
        **kwargs: Additional parameters for ask()
    
    Example:
        response = await code("Sort a list of numbers", language="python")
        response = await code("Create a REST API endpoint")
    """
    
    full_prompt = prompt
    if language:
        full_prompt = f"Write {language} code: {prompt}"
    
    # Force coding-optimized model selection
    modified_prompt = f"{full_prompt} [CODING_TASK]"
    
    return await ask(
        modified_prompt,
        optimize_for="quality",  # Code needs to be correct
        **kwargs
    )


async def translate(
    text: str,
    target_language: str,
    source_language: Optional[str] = None,
    **kwargs
) -> GenerationResponse:
    """
    Translate text with models optimized for translation.
    
    Args:
        text: Text to translate
        target_language: Target language (e.g., "Spanish", "French")
        source_language: Source language (auto-detected if None)
        **kwargs: Additional parameters for ask()
    
    Example:
        response = await translate("Hello world", "Spanish")
        response = await translate("Bonjour", "English", source_language="French")
    """
    
    if source_language:
        prompt = f"Translate from {source_language} to {target_language}: {text}"
    else:
        prompt = f"Translate to {target_language}: {text}"
    
    return await ask(
        prompt,
        optimize_for="speed",  # Translation can be fast
        **kwargs
    )


async def summarize(
    text: str,
    length: str = "medium",
    **kwargs
) -> GenerationResponse:
    """
    Summarize text with models optimized for analysis.
    
    Args:
        text: Text to summarize
        length: "short", "medium", or "long"
        **kwargs: Additional parameters for ask()
    
    Example:
        response = await summarize(long_article, length="short")
    """
    
    length_instructions = {
        "short": "in 2-3 sentences",
        "medium": "in 1-2 paragraphs", 
        "long": "in detailed bullet points"
    }
    
    instruction = length_instructions.get(length, "concisely")
    prompt = f"Summarize the following text {instruction}:\n\n{text}"
    
    return await ask(
        prompt,
        optimize_for="quality",  # Summaries need accuracy
        **kwargs
    )