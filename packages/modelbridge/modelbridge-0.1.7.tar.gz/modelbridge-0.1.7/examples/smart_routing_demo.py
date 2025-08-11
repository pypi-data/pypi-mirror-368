"""
Smart Routing Demo - ModelBridge v1.0.2+
Demonstrates the new intelligent model selection system
"""

import asyncio
import os
from modelbridge import ask, ask_json, ask_stream, code, translate, summarize

# For demo purposes, we'll set some fake API keys
# In real usage, set these as environment variables
os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-demo"
os.environ["ANTHROPIC_API_KEY"] = "sk-fake-key-for-demo" 
os.environ["GOOGLE_API_KEY"] = "fake-key-for-demo"
os.environ["GROQ_API_KEY"] = "fake-key-for-demo"


async def demo_smart_routing():
    """Demonstrate automatic model selection"""
    
    print("🧠 Smart Routing Demo - ModelBridge automatically picks the best model\n")
    
    # Example 1: Simple question (should route to cheap/fast model)
    print("Example 1: Simple Question")
    print("Prompt: 'What is 2+2?'")
    try:
        response = await ask("What is 2+2?", debug=True)
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error (expected with fake keys): {e}\n")
    
    # Example 2: Coding task (should route to GPT-5)
    print("Example 2: Coding Task")
    print("Prompt: 'Write a Python function to sort a list'")
    try:
        response = await ask("Write a Python function to sort a list", debug=True)
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error (expected with fake keys): {e}\n")
    
    # Example 3: Complex analysis (should route to Claude Opus)
    print("Example 3: Complex Analysis")
    print("Prompt: 'Analyze this 500-page document and provide detailed insights...'")
    try:
        response = await ask(
            "Analyze this 500-page document and provide detailed insights on market trends, competitive landscape, and strategic recommendations for our enterprise software business",
            debug=True
        )
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error (expected with fake keys): {e}\n")


async def demo_optimization_preferences():
    """Demonstrate optimization hints"""
    
    print("⚡ Optimization Preferences Demo\n")
    
    # Speed optimization
    print("Example 1: Optimize for Speed")
    try:
        response = await ask(
            "Write a short poem about coding",
            optimize_for="speed",
            debug=True
        )
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")
    
    # Cost optimization
    print("Example 2: Optimize for Cost")
    try:
        response = await ask(
            "Tell me a joke",
            optimize_for="cost",
            debug=True
        )
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")
    
    # Quality optimization
    print("Example 3: Optimize for Quality")
    try:
        response = await ask(
            "Explain quantum computing in detail",
            optimize_for="quality",
            debug=True
        )
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")


async def demo_cost_constraints():
    """Demonstrate cost constraints"""
    
    print("💰 Cost Constraints Demo\n")
    
    try:
        response = await ask(
            "This is an expensive query that might cost a lot",
            max_cost=0.001,  # Very low cost limit
            debug=True
        )
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")


async def demo_specialized_functions():
    """Demonstrate specialized convenience functions"""
    
    print("🎯 Specialized Functions Demo\n")
    
    # Code generation
    print("Code Generation:")
    try:
        response = await code("Create a REST API endpoint for user registration", language="python")
        print(f"Generated Code: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")
    
    # Translation
    print("Translation:")
    try:
        response = await translate("Hello, how are you?", "Spanish")
        print(f"Translation: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")
    
    # Summarization
    print("Summarization:")
    long_text = """
    Artificial Intelligence (AI) has been transforming industries across the globe at an unprecedented pace. 
    From healthcare to finance, from transportation to entertainment, AI technologies are being integrated 
    into various sectors to improve efficiency, accuracy, and innovation. Machine learning algorithms, 
    neural networks, and deep learning models are enabling computers to perform tasks that traditionally 
    required human intelligence, such as pattern recognition, natural language processing, and decision making.
    
    The healthcare industry has seen remarkable advancements through AI implementation. Medical imaging 
    analysis, drug discovery, personalized treatment plans, and robotic surgery are just a few examples 
    of how AI is revolutionizing patient care. In finance, algorithmic trading, fraud detection, and 
    risk assessment have become more sophisticated and efficient thanks to AI technologies.
    """
    
    try:
        response = await summarize(long_text, length="short")
        print(f"Summary: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")


async def demo_json_output():
    """Demonstrate structured JSON output"""
    
    print("📋 Structured JSON Output Demo\n")
    
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "skills": {"type": "array", "items": {"type": "string"}},
            "experience_years": {"type": "integer"}
        },
        "required": ["name", "age"]
    }
    
    try:
        response = await ask_json(
            "Extract information: Sarah Johnson, 28 years old, skilled in Python, JavaScript, and React, 5 years experience",
            schema=schema,
            debug=True
        )
        print(f"Extracted JSON: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")


async def demo_streaming():
    """Demonstrate streaming responses"""
    
    print("🌊 Streaming Response Demo\n")
    print("Streaming response for: 'Write a short story about a robot'")
    print("Response: ", end="")
    
    try:
        async for chunk in ask_stream("Write a short story about a robot learning to love"):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"\nDemo error: {e}\n")


async def demo_backward_compatibility():
    """Demonstrate backward compatibility"""
    
    print("🔄 Backward Compatibility Demo\n")
    print("Old API still works - forcing specific model:")
    
    try:
        from modelbridge import ModelBridge
        bridge = ModelBridge()
        await bridge.initialize()
        
        response = await bridge.generate_text(
            prompt="Test backward compatibility",
            model="gpt-5",  # Force specific model
            temperature=0.7
        )
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"Demo error: {e}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("ModelBridge Smart Routing System Demo")
    print("=" * 70)
    print("\nNOTE: This demo uses fake API keys and will show errors.")
    print("Set real API keys as environment variables to see actual results.\n")
    
    async def run_all_demos():
        await demo_smart_routing()
        print("-" * 50)
        await demo_optimization_preferences()
        print("-" * 50)
        await demo_cost_constraints()
        print("-" * 50)
        await demo_specialized_functions()
        print("-" * 50)
        await demo_json_output()
        print("-" * 50)
        await demo_streaming()
        print("-" * 50)
        await demo_backward_compatibility()
        
        print("=" * 70)
        print("Demo Complete! 🎉")
        print("=" * 70)
        print("\nTo use with real API keys:")
        print("export OPENAI_API_KEY='your-key-here'")
        print("export ANTHROPIC_API_KEY='your-key-here'")
        print("export GOOGLE_API_KEY='your-key-here'")
        print("export GROQ_API_KEY='your-key-here'")
        print("\nThen run: python smart_routing_demo.py")
    
    asyncio.run(run_all_demos())