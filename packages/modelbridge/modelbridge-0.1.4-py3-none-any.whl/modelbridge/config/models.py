"""
Pydantic models for configuration validation
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RoutingStrategy(str, Enum):
    """Routing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LATENCY = "least_latency"
    LEAST_COST = "least_cost"
    HIGHEST_SUCCESS = "highest_success"
    INTELLIGENT = "intelligent"


class ProviderConfig(BaseModel):
    """Configuration for a single provider"""
    api_key: Optional[str] = Field(None, description="API key for the provider")
    enabled: bool = Field(True, description="Whether this provider is enabled")
    priority: int = Field(1, ge=1, le=10, description="Provider priority (1-10)")
    timeout: int = Field(60, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum number of retries")
    base_url: Optional[str] = Field(None, description="Custom base URL for the provider")
    
    # Rate limiting
    max_requests_per_minute: Optional[int] = Field(None, ge=1, description="Max requests per minute")
    max_tokens_per_minute: Optional[int] = Field(None, ge=1, description="Max tokens per minute")
    
    # Model-specific overrides
    models: Optional[Dict[str, Any]] = Field(None, description="Model-specific configurations")
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('API key cannot be empty string')
        return v
    
    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Base URL must start with http:// or https://')
        return v


class CacheConfig(BaseModel):
    """Cache configuration"""
    enabled: bool = Field(True, description="Whether caching is enabled")
    type: str = Field("memory", pattern="^(memory|redis)$", description="Cache backend type")
    ttl: int = Field(3600, ge=60, le=86400, description="Cache TTL in seconds")
    max_size: int = Field(1000, ge=1, le=100000, description="Maximum cache size")
    
    # Redis-specific settings
    redis_host: str = Field("localhost", description="Redis host")
    redis_port: int = Field(6379, ge=1, le=65535, description="Redis port")
    redis_db: int = Field(0, ge=0, le=15, description="Redis database number")
    redis_password: Optional[str] = Field(None, description="Redis password")


class RoutingConfig(BaseModel):
    """Routing configuration"""
    strategy: RoutingStrategy = Field(RoutingStrategy.INTELLIGENT, description="Routing strategy")
    fallback_enabled: bool = Field(True, description="Whether to fallback to other providers")
    performance_tracking: bool = Field(True, description="Whether to track performance metrics")
    
    # Intelligent routing settings
    success_rate_weight: float = Field(0.4, ge=0.0, le=1.0, description="Weight for success rate")
    latency_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for latency")
    cost_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for cost")
    
    @model_validator(mode='after')
    def validate_weights(self):
        success_weight = self.success_rate_weight
        latency_weight = self.latency_weight
        cost_weight = self.cost_weight
        
        total = success_weight + latency_weight + cost_weight
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError('Routing weights must sum to 1.0')
        return self


class SecurityConfig(BaseModel):
    """Security configuration"""
    api_key_validation: bool = Field(True, description="Validate API keys on startup")
    request_signing: bool = Field(False, description="Sign requests with HMAC")
    rate_limit_enforcement: bool = Field(True, description="Enforce rate limits")
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains for requests")
    blocked_ips: Optional[List[str]] = Field(None, description="Blocked IP addresses")


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    enabled: bool = Field(True, description="Whether rate limiting is enabled")
    backend: str = Field("memory", pattern="^(memory|redis)$", description="Rate limiter backend")
    algorithm: str = Field("sliding_window", pattern="^(token_bucket|sliding_window|fixed_window)$", description="Rate limiting algorithm")
    
    # Memory backend settings
    cleanup_interval: int = Field(300, ge=60, le=3600, description="Cleanup interval in seconds")
    
    # Redis backend settings
    redis_host: str = Field("localhost", description="Redis host")
    redis_port: int = Field(6379, ge=1, le=65535, description="Redis port")
    redis_db: int = Field(1, ge=0, le=15, description="Redis database number")
    redis_password: Optional[str] = Field(None, description="Redis password")
    redis_key_prefix: str = Field("ratelimit:", description="Redis key prefix")
    
    # Global rate limits (if not set per provider)
    global_requests_per_minute: Optional[int] = Field(None, ge=1, description="Global requests per minute limit")
    global_tokens_per_minute: Optional[int] = Field(None, ge=1, description="Global tokens per minute limit")
    global_requests_per_hour: Optional[int] = Field(None, ge=1, description="Global requests per hour limit")
    global_tokens_per_hour: Optional[int] = Field(None, ge=1, description="Global tokens per hour limit")


class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    enabled: bool = Field(True, description="Whether monitoring is enabled")
    metrics_endpoint: Optional[str] = Field(None, description="Metrics endpoint URL")
    health_check_interval: int = Field(300, ge=30, le=3600, description="Health check interval in seconds")
    performance_logging: bool = Field(True, description="Log performance metrics")
    error_reporting: bool = Field(True, description="Report errors to monitoring")
    
    # Metrics collection
    collect_detailed_metrics: bool = Field(True, description="Collect detailed metrics")
    metrics_retention_hours: int = Field(168, ge=24, le=8760, description="Metrics retention in hours (default: 7 days)")
    prometheus_format: bool = Field(False, description="Enable Prometheus format export")
    
    # Performance monitoring
    performance_monitoring: bool = Field(True, description="Enable performance monitoring")
    performance_analysis_interval: int = Field(300, ge=60, le=3600, description="Performance analysis interval in seconds")
    
    # Alerting
    alerting_enabled: bool = Field(True, description="Enable alerting system")
    alert_cooldown_seconds: int = Field(300, ge=60, le=3600, description="Alert cooldown period")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for alerts")
    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL for alerts")


class ModelBridgeConfig(BaseModel):
    """Complete ModelBridge configuration"""
    # Core settings
    debug: bool = Field(False, description="Enable debug mode")
    log_level: LogLevel = Field(LogLevel.INFO, description="Logging level")
    config_file_path: Optional[str] = Field(None, description="Path to config file")
    
    # Provider configurations
    providers: Dict[str, ProviderConfig] = Field(
        default_factory=dict,
        description="Provider configurations"
    )
    
    # Feature configurations
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache configuration")
    routing: RoutingConfig = Field(default_factory=RoutingConfig, description="Routing configuration")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Monitoring configuration")
    rate_limiting: RateLimitConfig = Field(default_factory=RateLimitConfig, description="Rate limiting configuration")
    
    # Model aliases
    model_aliases: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        None,
        description="Custom model aliases"
    )
    
    # Global settings
    default_timeout: int = Field(60, ge=1, le=300, description="Default request timeout")
    max_concurrent_requests: int = Field(10, ge=1, le=100, description="Maximum concurrent requests")
    
    @model_validator(mode='after')
    def validate_providers(self):
        providers = self.providers
        if not providers:
            # This is OK - providers can be loaded from environment
            return self
        
        enabled_providers = [name for name, config in providers.items() if config.enabled]
        if not enabled_providers:
            raise ValueError('At least one provider must be enabled')
        
        return self
    
    @field_validator('providers')
    @classmethod
    def validate_provider_names(cls, v):
        valid_providers = {'openai', 'anthropic', 'google', 'groq'}
        for provider_name in v.keys():
            if provider_name not in valid_providers:
                raise ValueError(f'Unknown provider: {provider_name}. Valid providers: {valid_providers}')
        return v

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",  # Don't allow unknown fields
        "use_enum_values": True
    }


# Convenience functions for creating configurations
def create_provider_config(
    api_key: str,
    enabled: bool = True,
    priority: int = 1,
    timeout: int = 60,
    max_retries: int = 3,
    **kwargs
) -> ProviderConfig:
    """Create a provider configuration"""
    return ProviderConfig(
        api_key=api_key,
        enabled=enabled,
        priority=priority,
        timeout=timeout,
        max_retries=max_retries,
        **kwargs
    )


def create_default_config() -> ModelBridgeConfig:
    """Create a default configuration"""
    return ModelBridgeConfig(
        providers={},
        cache=CacheConfig(),
        routing=RoutingConfig(),
        security=SecurityConfig(),
        monitoring=MonitoringConfig(),
        rate_limiting=RateLimitConfig()
    )