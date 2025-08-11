"""
Basic Usage Example for ModelBridge
"""
import asyncio
import os
from dotenv import load_dotenv
from modelbridge import ModelBridge

# Load environment variables
load_dotenv()

async def main():
    """Basic example of using ModelBridge"""
    
    # Initialize the bridge
    bridge = ModelBridge()
    await bridge.initialize()
    
    # Example 1: Simple text generation with balanced routing
    print("1. Simple Text Generation")
    response = await bridge.generate_text(
        prompt="What are the benefits of renewable energy?",
        model="balanced"
    )
    print(f"Response: {response.content[:200]}...")
    print(f"Provider: {response.provider_name}")
    print(f"Model: {response.model_id}")
    print(f"Cost: ${response.cost:.4f}" if response.cost else "Cost: N/A")
    print(f"Latency: {response.response_time:.2f}s" if response.response_time else "Latency: N/A")
    
    # Example 2: Fast response for simple queries
    print("2. Speed-Optimized Generation")
    response = await bridge.generate_text(
        prompt="List 3 popular programming languages",
        model="fastest"
    )
    print(f"Response: {response.content}")
    print(f"Latency: {response.response_time:.2f}s" if response.response_time else "Latency: N/A")

    
    # Example 3: Cost-optimized generation
    print("3. Cost-Optimized Generation")
    response = await bridge.generate_text(
        prompt="Write a haiku about coding",
        model="cheapest"
    )
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost:.5f}" if response.cost else "Cost: N/A")

    
    # Example 4: Direct provider selection
    print("4. Direct Provider Selection")
    response = await bridge.generate_text(
        prompt="Explain machine learning",
        model="openai:gpt-3.5-turbo"  # Direct model specification
    )
    print(f"Response: {response.content[:200]}...")
    print(f"Provider: {response.provider_name}\n")
    
    # Example 5: Structured output
    print("5. Structured Output Generation")
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
    
    response = await bridge.generate_structured_output(
        prompt="Summarize the benefits of exercise",
        schema=schema,
        model="balanced"
    )
    if response.content and not response.error:
        print(f"Structured Response: {response.content}")
    elif response.error:
        print(f"Structured Output Error: {response.error}")
    
    # Show performance stats
    stats = bridge.get_performance_stats()
    print("\n📊 Performance Statistics:")
    for model, metrics in stats.items():
        if metrics['total_requests'] > 0:
            print(f"{model}:")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")
            print(f"  Avg Response Time: {metrics['avg_response_time']:.2f}s")
            print(f"  Avg Cost: ${metrics['avg_cost']:.4f}")

if __name__ == "__main__":
    asyncio.run(main())