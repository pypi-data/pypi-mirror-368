"""
ModelBridge Usage Examples
=========================

This file contains comprehensive examples of using ModelBridge for various scenarios,
from basic text generation to advanced enterprise deployments with monitoring and caching.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any

from modelbridge import ValidatedModelBridge
from modelbridge.config import ModelBridgeConfig, create_provider_config


# =============================================================================
# BASIC USAGE EXAMPLES
# =============================================================================

async def basic_text_generation():
    """Basic text generation with default configuration."""
    print("=== Basic Text Generation ===")
    
    # Initialize with minimal configuration
    bridge = ValidatedModelBridge()
    await bridge.initialize()
    
    # Generate text using intelligent routing
    response = await bridge.generate_text(
        prompt="Explain quantum computing in simple terms",
        model="balanced",  # Use balanced routing algorithm
        temperature=0.7
    )
    
    if response.error:
        print(f"Error: {response.error}")
    else:
        print(f"Generated text: {response.content}")
        print(f"Model used: {response.model_id}")
        print(f"Provider: {response.provider_name}")
        print(f"Cost: ${response.cost:.4f}")
        print(f"Tokens: {response.total_tokens}")
    
    await bridge.shutdown()


async def multiple_provider_setup():
    """Set up multiple providers with specific configurations."""
    print("=== Multiple Provider Setup ===")
    
    config = {
        "providers": {
            "openai": {
                "api_key": "sk-your-openai-key",
                "enabled": True,
                "timeout": 30,
                "max_retries": 3
            },
            "anthropic": {
                "api_key": "sk-ant-your-anthropic-key", 
                "enabled": True,
                "timeout": 60
            },
            "google": {
                "api_key": "your-google-key",
                "enabled": True
            }
        },
        "routing": {
            "strategy": "intelligent",
            "fallback_enabled": True,
            "performance_tracking": True
        }
    }
    
    bridge = ValidatedModelBridge(config)
    success = await bridge.initialize()
    
    if not success:
        print("Failed to initialize bridge")
        return
    
    # Try different models
    models_to_test = ["fastest", "best", "cheapest", "openai:gpt-4", "anthropic:claude-3-sonnet"]
    
    for model in models_to_test:
        print(f"\nTesting model: {model}")
        response = await bridge.generate_text(
            prompt="What is the meaning of life?",
            model=model,
            max_tokens=100
        )
        
        if response.error:
            print(f"  Error: {response.error}")
        else:
            print(f"  Response: {response.content[:100]}...")
            print(f"  Provider: {response.provider_name}")
            print(f"  Cost: ${response.cost:.4f}")
    
    await bridge.shutdown()


# =============================================================================
# ADVANCED CONFIGURATION EXAMPLES
# =============================================================================

async def advanced_caching_example():
    """Advanced caching configuration with Redis and monitoring."""
    print("=== Advanced Caching Example ===")
    
    config = {
        "providers": {
            "openai": {"api_key": "sk-test-key", "enabled": True}
        },
        "cache": {
            "enabled": True,
            "type": "redis",  # Use Redis for distributed caching
            "ttl": 3600,      # 1 hour TTL
            "max_size": 10000,
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0
        }
    }
    
    bridge = ValidatedModelBridge(config)
    await bridge.initialize()
    
    # First request (cache miss)
    print("Making first request (cache miss)...")
    response1 = await bridge.generate_text(
        prompt="Explain machine learning",
        model="balanced"
    )
    print(f"Response time: {response1.response_time:.3f}s")
    
    # Second request (cache hit)
    print("Making second request (cache hit)...")
    response2 = await bridge.generate_text(
        prompt="Explain machine learning", 
        model="balanced"
    )
    print(f"Response time: {response2.response_time:.3f}s")
    
    # Check cache statistics
    cache_stats = await bridge.get_cache_stats()
    if cache_stats:
        print(f"Cache stats: {json.dumps(cache_stats, indent=2)}")
    
    await bridge.shutdown()


async def rate_limiting_example():
    """Rate limiting configuration with different strategies."""
    print("=== Rate Limiting Example ===")
    
    config = {
        "providers": {
            "openai": {"api_key": "sk-test-key", "enabled": True}
        },
        "rate_limiting": {
            "enabled": True,
            "backend": "memory",
            "algorithm": "sliding_window",
            "global_requests_per_minute": 100,
            "global_tokens_per_minute": 10000,
            # Provider-specific limits will override global limits
        }
    }
    
    bridge = ValidatedModelBridge(config)
    await bridge.initialize()
    
    # Test rate limiting by making rapid requests
    print("Making rapid requests to test rate limiting...")
    
    for i in range(5):
        try:
            response = await bridge.generate_text(
                prompt=f"Request number {i+1}",
                model="fastest"
            )
            
            if response.error:
                print(f"Request {i+1}: Error - {response.error}")
            else:
                print(f"Request {i+1}: Success")
                
        except Exception as e:
            print(f"Request {i+1}: Exception - {e}")
    
    await bridge.shutdown()


# =============================================================================
# MONITORING AND OBSERVABILITY EXAMPLES  
# =============================================================================

async def comprehensive_monitoring_example():
    """Comprehensive monitoring with metrics, health checks, and alerts."""
    print("=== Comprehensive Monitoring Example ===")
    
    config = {
        "providers": {
            "openai": {"api_key": "sk-test-key", "enabled": True},
            "anthropic": {"api_key": "sk-ant-test-key", "enabled": True}
        },
        "monitoring": {
            "enabled": True,
            "collect_detailed_metrics": True,
            "performance_monitoring": True,
            "alerting_enabled": True,
            "health_check_interval": 60,
            "webhook_url": "https://your-monitoring-system.com/webhook"
        },
        "cache": {"enabled": True, "type": "memory"},
        "rate_limiting": {"enabled": True}
    }
    
    bridge = ValidatedModelBridge(config)
    await bridge.initialize()
    
    # Start monitoring systems
    await bridge.start_monitoring()
    
    # Generate some test traffic
    print("Generating test traffic for monitoring...")
    prompts = [
        "Explain artificial intelligence",
        "What is machine learning?", 
        "Describe neural networks",
        "How does deep learning work?",
        "What are transformers in AI?"
    ]
    
    for prompt in prompts:
        response = await bridge.generate_text(
            prompt=prompt,
            model="balanced"
        )
        print(f"Generated response for: {prompt[:30]}...")
    
    # Check system health
    print("\n=== System Health Check ===")
    health = await bridge.health_check()
    print(f"Overall status: {health['status']}")
    print(f"Uptime: {health.get('uptime_seconds', 0):.0f} seconds")
    
    for component_name, component_health in health.get('components', {}).items():
        status = component_health['status']
        print(f"{component_name}: {status}")
    
    # Get comprehensive metrics
    print("\n=== System Metrics ===")
    metrics = await bridge.get_metrics()
    if metrics:
        print(f"Metrics collected: {len(metrics)} data points")
        # Print key metrics if available
        for key, value in list(metrics.items())[:10]:  # Show first 10 metrics
            print(f"{key}: {value}")
    
    # Get performance report
    print("\n=== Performance Report ===")
    performance = await bridge.get_performance_report()
    if performance:
        print("Performance analysis available:")
        print(f"- System performance data: {len(performance.get('system_performance', {}))} metrics")
        print(f"- Provider rankings: {len(performance.get('analysis', {}).get('provider_rankings', []))} providers")
    
    # Check active alerts
    print("\n=== Active Alerts ===") 
    alerts = await bridge.get_active_alerts()
    if alerts:
        print(f"Found {len(alerts)} active alerts:")
        for alert in alerts:
            print(f"- {alert['level']}: {alert['message']}")
    else:
        print("No active alerts")
    
    await bridge.stop_monitoring()
    await bridge.shutdown()


# =============================================================================
# PRODUCTION DEPLOYMENT EXAMPLES
# =============================================================================

async def production_configuration_example():
    """Production-ready configuration with all features enabled."""
    print("=== Production Configuration Example ===")
    
    # Load configuration from file in production
    config_path = Path("production_config.yaml")
    
    # Example of production configuration
    production_config = {
        # Provider configuration with proper timeouts and retries
        "providers": {
            "openai": {
                "api_key": "${OPENAI_API_KEY}",  # Use environment variable
                "enabled": True,
                "timeout": 60,
                "max_retries": 3,
                "priority": 1,
                "max_requests_per_minute": 500,
                "max_tokens_per_minute": 50000
            },
            "anthropic": {
                "api_key": "${ANTHROPIC_API_KEY}",
                "enabled": True, 
                "timeout": 90,
                "max_retries": 3,
                "priority": 2,
                "max_requests_per_minute": 300,
                "max_tokens_per_minute": 30000
            }
        },
        
        # Production caching with Redis
        "cache": {
            "enabled": True,
            "type": "redis",
            "ttl": 7200,  # 2 hours
            "max_size": 100000,
            "redis_host": "${REDIS_HOST}",
            "redis_port": 6379,
            "redis_db": 0,
            "redis_password": "${REDIS_PASSWORD}"
        },
        
        # Production rate limiting
        "rate_limiting": {
            "enabled": True,
            "backend": "redis",
            "algorithm": "sliding_window", 
            "global_requests_per_minute": 1000,
            "global_tokens_per_minute": 100000,
            "redis_host": "${REDIS_HOST}",
            "redis_port": 6379,
            "redis_db": 1
        },
        
        # Comprehensive monitoring
        "monitoring": {
            "enabled": True,
            "collect_detailed_metrics": True,
            "performance_monitoring": True,
            "alerting_enabled": True,
            "health_check_interval": 30,
            "metrics_retention_hours": 168,  # 7 days
            "prometheus_format": True,
            "webhook_url": "${MONITORING_WEBHOOK_URL}",
            "slack_webhook_url": "${SLACK_WEBHOOK_URL}"
        },
        
        # Intelligent routing configuration
        "routing": {
            "strategy": "intelligent",
            "fallback_enabled": True,
            "performance_tracking": True,
            "success_rate_weight": 0.4,
            "latency_weight": 0.3,
            "cost_weight": 0.3
        },
        
        # Security configuration
        "security": {
            "api_key_validation": True,
            "request_signing": False,
            "rate_limit_enforcement": True
        },
        
        # Global settings
        "debug": False,
        "log_level": "INFO",
        "default_timeout": 60,
        "max_concurrent_requests": 50
    }
    
    # In production, you would load from file:
    # bridge = ValidatedModelBridge(config_path)
    
    # For this example, use the config dict
    bridge = ValidatedModelBridge(production_config)
    
    try:
        success = await bridge.initialize()
        if not success:
            print("Failed to initialize production bridge")
            return
        
        print("Production bridge initialized successfully")
        
        # Start all monitoring systems
        await bridge.start_monitoring()
        
        # Example production usage
        response = await bridge.generate_text(
            prompt="Generate a professional email response",
            model="best",
            system_message="You are a professional assistant",
            temperature=0.3,
            max_tokens=200
        )
        
        print(f"Production response generated: {response.content[:100]}...")
        print(f"Used model: {response.model_id} via {response.provider_name}")
        
        # Monitor system health
        health = await bridge.health_check()
        print(f"System health: {health['status']}")
        
    except Exception as e:
        print(f"Production error: {e}")
        
    finally:
        await bridge.stop_monitoring()
        await bridge.shutdown()


# =============================================================================
# STRUCTURED OUTPUT EXAMPLES
# =============================================================================

async def structured_output_example():
    """Generate structured JSON output with validation."""
    print("=== Structured Output Example ===")
    
    bridge = ValidatedModelBridge()
    await bridge.initialize()
    
    # Define JSON schema for structured output
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            },
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        },
        "required": ["summary", "key_points", "sentiment", "confidence"]
    }
    
    response = await bridge.generate_structured_output(
        prompt="Analyze this product review: 'This laptop is amazing! Fast performance, great display, but battery life could be better.'",
        schema=schema,
        model="best"
    )
    
    if response.error:
        print(f"Error: {response.error}")
    else:
        try:
            structured_data = json.loads(response.content)
            print("Structured analysis:")
            print(f"Summary: {structured_data['summary']}")
            print(f"Key points: {structured_data['key_points']}")
            print(f"Sentiment: {structured_data['sentiment']}")
            print(f"Confidence: {structured_data['confidence']}")
        except json.JSONDecodeError:
            print(f"Generated content: {response.content}")
    
    await bridge.shutdown()


# =============================================================================
# ERROR HANDLING AND RELIABILITY EXAMPLES
# =============================================================================

async def error_handling_example():
    """Demonstrate error handling and reliability features."""
    print("=== Error Handling and Reliability Example ===")
    
    config = {
        "providers": {
            "openai": {
                "api_key": "invalid-key",  # Intentionally invalid
                "enabled": True,
                "timeout": 5,
                "max_retries": 2
            }
        },
        "routing": {
            "fallback_enabled": True
        }
    }
    
    bridge = ValidatedModelBridge(config)
    
    # This will likely fail due to invalid API key
    success = await bridge.initialize()
    print(f"Initialization success: {success}")
    
    if success:
        # Test request with error handling
        response = await bridge.generate_text(
            prompt="This request may fail",
            model="openai"
        )
        
        if response.error:
            print(f"Request failed as expected: {response.error}")
            print(f"Response time: {response.response_time:.3f}s")
        else:
            print("Request succeeded unexpectedly")
    
    # Check system health to see component status
    health = await bridge.health_check()
    print(f"System health: {health}")
    
    await bridge.shutdown()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Run all examples."""
    examples = [
        ("Basic Text Generation", basic_text_generation),
        ("Multiple Provider Setup", multiple_provider_setup),
        ("Advanced Caching", advanced_caching_example),
        ("Rate Limiting", rate_limiting_example), 
        ("Comprehensive Monitoring", comprehensive_monitoring_example),
        ("Production Configuration", production_configuration_example),
        ("Structured Output", structured_output_example),
        ("Error Handling", error_handling_example)
    ]
    
    for name, example_func in examples:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print('='*60)
        
        try:
            await example_func()
        except Exception as e:
            print(f"Example failed: {e}")
        
        print(f"Completed: {name}")
    
    print(f"\n{'='*60}")
    print("All examples completed!")
    print('='*60)


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())