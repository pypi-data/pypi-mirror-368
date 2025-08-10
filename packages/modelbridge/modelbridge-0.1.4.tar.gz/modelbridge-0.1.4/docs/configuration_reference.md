# ModelBridge Configuration Reference

This document provides a comprehensive reference for configuring ModelBridge with all available options and examples.

## Table of Contents

- [Overview](#overview)
- [Configuration Sources](#configuration-sources)
- [Provider Configuration](#provider-configuration)
- [Routing Configuration](#routing-configuration)
- [Cache Configuration](#cache-configuration)
- [Rate Limiting Configuration](#rate-limiting-configuration)
- [Monitoring Configuration](#monitoring-configuration)
- [Security Configuration](#security-configuration)
- [Global Settings](#global-settings)
- [Model Aliases](#model-aliases)
- [Environment Variables](#environment-variables)
- [Configuration Examples](#configuration-examples)
- [Validation Rules](#validation-rules)

## Overview

ModelBridge uses Pydantic V2 for configuration validation, supporting multiple configuration sources including YAML files, JSON files, dictionaries, and environment variables.

## Configuration Sources

### 1. Environment Variables (Default)
```python
from modelbridge import ValidatedModelBridge

# Loads configuration from environment variables
bridge = ValidatedModelBridge()
```

### 2. Configuration File
```python
# YAML or JSON file
bridge = ValidatedModelBridge("config.yaml")
bridge = ValidatedModelBridge("config.json")
```

### 3. Dictionary Configuration
```python
config = {
    "providers": {
        "openai": {"api_key": "sk-...", "enabled": True}
    }
}
bridge = ValidatedModelBridge(config)
```

### 4. Pydantic Configuration Object
```python
from modelbridge.config import ModelBridgeConfig, create_provider_config

config = ModelBridgeConfig(
    providers={
        "openai": create_provider_config("sk-...")
    }
)
bridge = ValidatedModelBridge(config)
```

## Provider Configuration

### Supported Providers
- `openai` - OpenAI GPT models
- `anthropic` - Anthropic Claude models
- `google` - Google Gemini models
- `groq` - Groq models

### Provider Settings

```yaml
providers:
  openai:
    api_key: "sk-your-openai-key"          # API key (required)
    enabled: true                          # Enable/disable provider
    priority: 1                            # Priority (1-10, lower = higher priority)
    timeout: 60                            # Request timeout in seconds (1-300)
    max_retries: 3                         # Maximum retry attempts (0-10)
    base_url: "https://api.openai.com/v1"  # Custom base URL (optional)
    
    # Rate limiting (optional)
    max_requests_per_minute: 1000          # Per-provider request limit
    max_tokens_per_minute: 50000           # Per-provider token limit
    
    # Model-specific overrides (optional)
    models:
      gpt-4:
        timeout: 120
        max_tokens_default: 4000
```

### Provider-Specific Configuration

#### OpenAI
```yaml
providers:
  openai:
    api_key: "sk-..."
    models:
      gpt-4:
        temperature: 0.7
        max_tokens: 4000
      gpt-3.5-turbo:
        temperature: 0.5
        max_tokens: 2000
```

#### Anthropic
```yaml
providers:
  anthropic:
    api_key: "sk-ant-..."
    models:
      claude-3-opus:
        max_tokens: 4000
      claude-3-sonnet:
        max_tokens: 2000
```

## Routing Configuration

Controls how requests are distributed across providers.

```yaml
routing:
  strategy: "intelligent"           # Routing strategy
  fallback_enabled: true           # Enable fallback to other providers
  performance_tracking: true       # Track provider performance
  
  # Intelligent routing weights (must sum to 1.0)
  success_rate_weight: 0.4        # Weight for success rate (0.0-1.0)
  latency_weight: 0.3             # Weight for latency (0.0-1.0)
  cost_weight: 0.3                # Weight for cost (0.0-1.0)
```

### Routing Strategies
- `round_robin` - Distribute requests evenly
- `least_latency` - Route to fastest provider
- `least_cost` - Route to cheapest provider
- `highest_success` - Route to most reliable provider
- `intelligent` - ML-based routing using weighted metrics

## Cache Configuration

### Memory Cache (Default)
```yaml
cache:
  enabled: true
  type: "memory"
  ttl: 3600                       # Time to live in seconds (60-86400)
  max_size: 1000                  # Maximum cache entries (1-100000)
```

### Redis Cache
```yaml
cache:
  enabled: true
  type: "redis"
  ttl: 7200
  max_size: 10000
  redis_host: "localhost"         # Redis host
  redis_port: 6379                # Redis port (1-65535)
  redis_db: 0                     # Redis database number (0-15)
  redis_password: "password"      # Redis password (optional)
```

## Rate Limiting Configuration

### Memory-Based Rate Limiting
```yaml
rate_limiting:
  enabled: true
  backend: "memory"               # "memory" or "redis"
  algorithm: "sliding_window"     # "token_bucket", "sliding_window", "fixed_window"
  cleanup_interval: 300           # Cleanup interval in seconds (60-3600)
  
  # Global limits (optional)
  global_requests_per_minute: 1000
  global_tokens_per_minute: 100000
  global_requests_per_hour: 10000
  global_tokens_per_hour: 1000000
```

### Redis-Based Rate Limiting
```yaml
rate_limiting:
  enabled: true
  backend: "redis"
  algorithm: "sliding_window"
  
  # Redis settings
  redis_host: "localhost"
  redis_port: 6379
  redis_db: 1
  redis_password: "password"
  redis_key_prefix: "ratelimit:"
  
  # Global limits
  global_requests_per_minute: 5000
  global_tokens_per_minute: 500000
```

## Monitoring Configuration

```yaml
monitoring:
  enabled: true
  health_check_interval: 300      # Health check interval (30-3600)
  performance_logging: true       # Log performance metrics
  error_reporting: true           # Report errors
  
  # Metrics collection
  collect_detailed_metrics: true  # Collect detailed metrics
  metrics_retention_hours: 168    # Retention period in hours (24-8760)
  prometheus_format: false        # Enable Prometheus format export
  
  # Performance monitoring
  performance_monitoring: true
  performance_analysis_interval: 300  # Analysis interval (60-3600)
  
  # Alerting
  alerting_enabled: true
  alert_cooldown_seconds: 300     # Alert cooldown (60-3600)
  webhook_url: "https://..."      # Webhook for alerts (optional)
  slack_webhook_url: "https://..."  # Slack webhook (optional)
```

## Security Configuration

```yaml
security:
  api_key_validation: true        # Validate API keys on startup
  request_signing: false          # Sign requests with HMAC
  rate_limit_enforcement: true    # Enforce rate limits
  allowed_domains:                # Allowed domains (optional)
    - "example.com"
    - "*.trusted.com"
  blocked_ips:                    # Blocked IP addresses (optional)
    - "192.168.1.100"
    - "10.0.0.0/8"
```

## Global Settings

```yaml
# Global configuration
debug: false                      # Enable debug mode
log_level: "INFO"                # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
default_timeout: 60               # Default request timeout (1-300)
max_concurrent_requests: 10       # Max concurrent requests (1-100)
```

## Model Aliases

Define custom model aliases for intelligent routing:

```yaml
model_aliases:
  custom_fast:
    - alias: "custom_fast"
      provider: "groq"
      model_id: "llama3-8b-8192"
      priority: 1
    - alias: "custom_fast"
      provider: "openai"
      model_id: "gpt-3.5-turbo"
      priority: 2
  
  custom_quality:
    - alias: "custom_quality"
      provider: "anthropic"
      model_id: "claude-3-opus-20240229"
      priority: 1
    - alias: "custom_quality"
      provider: "openai"
      model_id: "gpt-4-turbo"
      priority: 2
```

## Environment Variables

### Provider API Keys
```bash
# Provider API keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-key
GROQ_API_KEY=your-groq-key
```

### Cache Configuration
```bash
# Redis cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password
```

### Monitoring
```bash
# Monitoring webhooks
MONITORING_WEBHOOK_URL=https://your-monitoring-system.com/webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Global Settings
```bash
# Global settings
MODELBRIDGE_DEBUG=false
MODELBRIDGE_LOG_LEVEL=INFO
MODELBRIDGE_DEFAULT_TIMEOUT=60
```

## Configuration Examples

### Basic Configuration
```yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    enabled: true

cache:
  enabled: true
  type: "memory"
  ttl: 3600

routing:
  strategy: "intelligent"
  fallback_enabled: true
```

### Production Configuration
```yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    enabled: true
    timeout: 60
    max_retries: 3
    priority: 1
    max_requests_per_minute: 1000
  
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    enabled: true
    timeout: 90
    max_retries: 3
    priority: 2
    max_requests_per_minute: 500

cache:
  enabled: true
  type: "redis"
  ttl: 7200
  max_size: 100000
  redis_host: "${REDIS_HOST}"
  redis_password: "${REDIS_PASSWORD}"

rate_limiting:
  enabled: true
  backend: "redis"
  algorithm: "sliding_window"
  global_requests_per_minute: 5000
  global_tokens_per_minute: 500000

monitoring:
  enabled: true
  collect_detailed_metrics: true
  performance_monitoring: true
  alerting_enabled: true
  webhook_url: "${MONITORING_WEBHOOK_URL}"

routing:
  strategy: "intelligent"
  fallback_enabled: true
  performance_tracking: true
  success_rate_weight: 0.4
  latency_weight: 0.3
  cost_weight: 0.3

security:
  api_key_validation: true
  rate_limit_enforcement: true

debug: false
log_level: "INFO"
default_timeout: 60
max_concurrent_requests: 50
```

### High-Performance Configuration
```yaml
providers:
  groq:
    api_key: "${GROQ_API_KEY}"
    enabled: true
    priority: 1
    max_requests_per_minute: 2000
  
  openai:
    api_key: "${OPENAI_API_KEY}"
    enabled: true
    priority: 2
    max_requests_per_minute: 1000

cache:
  enabled: true
  type: "redis"
  ttl: 1800  # 30 minutes for faster responses
  max_size: 50000

rate_limiting:
  enabled: true
  backend: "redis"
  global_requests_per_minute: 10000
  global_tokens_per_minute: 1000000

routing:
  strategy: "least_latency"
  fallback_enabled: true

max_concurrent_requests: 100
```

### Development Configuration
```yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    enabled: true

cache:
  enabled: false  # Disable caching for development

rate_limiting:
  enabled: false  # Disable rate limiting for development

monitoring:
  enabled: true
  collect_detailed_metrics: false  # Reduce overhead
  
debug: true
log_level: "DEBUG"
```

## Validation Rules

### Provider Validation
- At least one provider must be enabled
- API keys cannot be empty strings
- Priority must be between 1-10
- Timeout must be between 1-300 seconds
- Max retries must be between 0-10
- Base URLs must start with http:// or https://

### Routing Validation
- Routing weights must sum to 1.0 (with 0.01 tolerance)
- Weights must be between 0.0-1.0

### Cache Validation
- TTL must be between 60-86400 seconds (1 minute to 24 hours)
- Max size must be between 1-100000
- Redis port must be between 1-65535
- Redis DB must be between 0-15

### Rate Limiting Validation
- Redis port must be between 1-65535
- Redis DB must be between 0-15
- Cleanup interval must be between 60-3600 seconds
- All rate limits must be positive integers

### Monitoring Validation
- Health check interval must be between 30-3600 seconds
- Metrics retention must be between 24-8760 hours
- Performance analysis interval must be between 60-3600 seconds
- Alert cooldown must be between 60-3600 seconds

### Security Validation
- Domain patterns must be valid
- IP addresses must be valid IPv4/IPv6 or CIDR notation

### Global Settings Validation
- Default timeout must be between 1-300 seconds
- Max concurrent requests must be between 1-100
- Log level must be valid Python logging level

## Error Handling

### Configuration Errors
The system will raise `ConfigError` for:
- Invalid configuration syntax
- Missing required fields
- Invalid field values
- Failed validation rules

### Provider Errors
The system will raise `ProviderError` for:
- Invalid API keys
- Provider initialization failures
- Network connectivity issues

### Validation Errors
The system will raise `ValidationError` for:
- Pydantic validation failures
- Type mismatches
- Constraint violations

## Best Practices

### Production Deployments
1. Use Redis for caching and rate limiting in distributed systems
2. Enable comprehensive monitoring and alerting
3. Set appropriate timeouts and retry limits
4. Use environment variables for secrets
5. Enable API key validation
6. Configure proper rate limits
7. Use intelligent routing for optimal performance

### Development
1. Enable debug mode for detailed logging
2. Disable caching for fresh responses
3. Use relaxed rate limits
4. Enable detailed metrics collection

### Security
1. Never commit API keys to version control
2. Use environment variables or secure secret management
3. Validate all API keys on startup
4. Configure allowed domains and blocked IPs
5. Enable rate limit enforcement
6. Use HTTPS for all webhook URLs

### Performance
1. Use Redis for high-performance caching
2. Configure appropriate cache TTLs
3. Use connection pooling
4. Set optimal concurrency limits
5. Monitor and tune routing weights
6. Use performance-based routing strategies