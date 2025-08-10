"""
Configuration loader with validation
"""
import os
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
from pydantic import ValidationError

from .models import (
    ModelBridgeConfig, 
    ProviderConfig, 
    create_default_config,
    create_provider_config
)

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration validation error"""
    pass


class ConfigLoader:
    """Configuration loader with validation and environment variable support"""
    
    def __init__(self):
        self.supported_providers = ['openai', 'anthropic', 'google', 'groq']
    
    def load_from_env(self) -> ModelBridgeConfig:
        """Load configuration from environment variables"""
        try:
            # Start with default config
            config_dict = self._get_default_config_dict()
            
            # Load provider configurations from environment
            providers = {}
            
            for provider in self.supported_providers:
                api_key_env = f"{provider.upper()}_API_KEY"
                api_key = os.getenv(api_key_env)
                
                if api_key:
                    providers[provider] = {
                        "api_key": api_key,
                        "enabled": True,
                        "priority": self._get_provider_priority(provider),
                        "timeout": int(os.getenv(f"{provider.upper()}_TIMEOUT", "60")),
                        "max_retries": int(os.getenv(f"{provider.upper()}_MAX_RETRIES", "3"))
                    }
            
            config_dict["providers"] = providers
            
            # Load global settings from environment
            config_dict["debug"] = os.getenv("MODELBRIDGE_DEBUG", "false").lower() == "true"
            config_dict["log_level"] = os.getenv("MODELBRIDGE_LOG_LEVEL", "info").lower()
            config_dict["default_timeout"] = int(os.getenv("MODELBRIDGE_TIMEOUT", "60"))
            config_dict["max_concurrent_requests"] = int(os.getenv("MODELBRIDGE_MAX_CONCURRENT", "10"))
            
            # Load cache settings
            config_dict["cache"]["enabled"] = os.getenv("MODELBRIDGE_CACHE_ENABLED", "true").lower() == "true"
            config_dict["cache"]["type"] = os.getenv("MODELBRIDGE_CACHE_TYPE", "memory")
            config_dict["cache"]["ttl"] = int(os.getenv("MODELBRIDGE_CACHE_TTL", "3600"))
            config_dict["cache"]["redis_host"] = os.getenv("MODELBRIDGE_REDIS_HOST", "localhost")
            config_dict["cache"]["redis_port"] = int(os.getenv("MODELBRIDGE_REDIS_PORT", "6379"))
            
            # Load routing settings
            config_dict["routing"]["strategy"] = os.getenv("MODELBRIDGE_ROUTING_STRATEGY", "intelligent")
            config_dict["routing"]["fallback_enabled"] = os.getenv("MODELBRIDGE_FALLBACK", "true").lower() == "true"
            
            return ModelBridgeConfig(**config_dict)
            
        except ValidationError as e:
            raise ConfigError(f"Environment configuration validation failed: {e}")
        except ValueError as e:
            raise ConfigError(f"Invalid environment variable value: {e}")
    
    def load_from_file(self, config_path: Union[str, Path]) -> ModelBridgeConfig:
        """Load configuration from YAML file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_dict = yaml.safe_load(f)
                else:
                    raise ConfigError(f"Unsupported configuration file format: {config_path.suffix}")
            
            if not config_dict:
                config_dict = {}
            
            # Apply environment variable overrides (env vars take precedence)  
            config_dict = self._apply_env_overrides(config_dict)
            
            return ModelBridgeConfig(**config_dict)
            
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse YAML configuration: {e}")
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load configuration file: {e}")
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> ModelBridgeConfig:
        """Load configuration from dictionary"""
        try:
            return ModelBridgeConfig(**config_dict)
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed: {e}")
    
    def validate_config(self, config: ModelBridgeConfig) -> None:
        """Validate configuration beyond Pydantic validation"""
        # Check that we have at least one provider with API key
        providers_with_keys = [
            name for name, provider in config.providers.items() 
            if provider.enabled and provider.api_key
        ]
        
        if not providers_with_keys:
            # Check environment variables as fallback
            env_keys = [
                os.getenv(f"{provider.upper()}_API_KEY")
                for provider in self.supported_providers
            ]
            
            if not any(env_keys):
                logger.warning("No API keys found in configuration or environment variables")
        
        # Validate cache configuration
        if config.cache.enabled and config.cache.type == "redis":
            self._validate_redis_config(config.cache)
        
        # Validate routing weights
        routing = config.routing
        total_weight = routing.success_rate_weight + routing.latency_weight + routing.cost_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ConfigError(f"Routing weights must sum to 1.0, got {total_weight}")
    
    def _get_default_config_dict(self) -> Dict[str, Any]:
        """Get default configuration as dictionary"""
        return create_default_config().model_dump()
    
    def _get_provider_priority(self, provider: str) -> int:
        """Get default priority for provider"""
        priorities = {
            'openai': 1,
            'anthropic': 2, 
            'google': 3,
            'groq': 4
        }
        return priorities.get(provider, 5)
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries"""
        merged = base.copy()
        
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _apply_env_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply only actual environment variable overrides, not defaults"""
        # Global settings
        if os.getenv("MODELBRIDGE_DEBUG"):
            config_dict["debug"] = os.getenv("MODELBRIDGE_DEBUG", "false").lower() == "true"
        if os.getenv("MODELBRIDGE_LOG_LEVEL"):
            config_dict["log_level"] = os.getenv("MODELBRIDGE_LOG_LEVEL", "info").lower()
        if os.getenv("MODELBRIDGE_TIMEOUT"):
            config_dict["default_timeout"] = int(os.getenv("MODELBRIDGE_TIMEOUT", "60"))
        if os.getenv("MODELBRIDGE_MAX_CONCURRENT"):
            config_dict["max_concurrent_requests"] = int(os.getenv("MODELBRIDGE_MAX_CONCURRENT", "10"))
        
        # Cache settings
        cache_config = config_dict.setdefault("cache", {})
        if os.getenv("MODELBRIDGE_CACHE_ENABLED"):
            cache_config["enabled"] = os.getenv("MODELBRIDGE_CACHE_ENABLED", "true").lower() == "true"
        if os.getenv("MODELBRIDGE_CACHE_TYPE"):
            cache_config["type"] = os.getenv("MODELBRIDGE_CACHE_TYPE", "memory")
        if os.getenv("MODELBRIDGE_CACHE_TTL"):
            cache_config["ttl"] = int(os.getenv("MODELBRIDGE_CACHE_TTL", "3600"))
        if os.getenv("MODELBRIDGE_REDIS_HOST"):
            cache_config["redis_host"] = os.getenv("MODELBRIDGE_REDIS_HOST", "localhost")
        if os.getenv("MODELBRIDGE_REDIS_PORT"):
            cache_config["redis_port"] = int(os.getenv("MODELBRIDGE_REDIS_PORT", "6379"))
        
        # Routing settings
        routing_config = config_dict.setdefault("routing", {})
        if os.getenv("MODELBRIDGE_ROUTING_STRATEGY"):
            routing_config["strategy"] = os.getenv("MODELBRIDGE_ROUTING_STRATEGY", "intelligent")
        if os.getenv("MODELBRIDGE_FALLBACK"):
            routing_config["fallback_enabled"] = os.getenv("MODELBRIDGE_FALLBACK", "true").lower() == "true"
        
        # Provider overrides
        providers = config_dict.setdefault("providers", {})
        for provider in self.supported_providers:
            api_key_env = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(api_key_env)
            
            if api_key:
                if provider not in providers:
                    providers[provider] = {}
                providers[provider]["api_key"] = api_key
                providers[provider]["enabled"] = True
                providers[provider]["priority"] = self._get_provider_priority(provider)
                
        return config_dict
    
    def _validate_redis_config(self, cache_config) -> None:
        """Validate Redis configuration"""
        try:
            # Try to import redis
            import redis
            
            # Test connection (optional - might be expensive)
            if cache_config.redis_host and cache_config.redis_port:
                pass  # Connection test could be added here
                
        except ImportError:
            raise ConfigError(
                "Redis cache enabled but redis package not installed. "
                "Install with: pip install redis"
            )


# Convenience functions
def load_config(config_path: Optional[Union[str, Path]] = None) -> ModelBridgeConfig:
    """
    Load configuration from file or environment variables
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Validated ModelBridge configuration
        
    Raises:
        ConfigError: If configuration is invalid
    """
    loader = ConfigLoader()
    
    if config_path:
        return loader.load_from_file(config_path)
    else:
        return loader.load_from_env()


def create_sample_config() -> str:
    """Create a sample YAML configuration file content"""
    return """# ModelBridge Configuration File
# This is a complete example showing all available options

# Global settings
debug: false
log_level: "info"
default_timeout: 60
max_concurrent_requests: 10

# Provider configurations
providers:
  openai:
    api_key: "your-openai-api-key"  # Or use OPENAI_API_KEY env var
    enabled: true
    priority: 1
    timeout: 60
    max_retries: 3
    max_requests_per_minute: 1000
    
  anthropic:
    api_key: "your-anthropic-api-key"  # Or use ANTHROPIC_API_KEY env var
    enabled: true
    priority: 2
    timeout: 60
    max_retries: 3
    max_requests_per_minute: 500
    
  google:
    api_key: "your-google-api-key"  # Or use GOOGLE_API_KEY env var
    enabled: false  # Disabled by default
    priority: 3
    timeout: 60
    
  groq:
    api_key: "your-groq-api-key"  # Or use GROQ_API_KEY env var
    enabled: true
    priority: 4
    timeout: 30

# Cache configuration
cache:
  enabled: true
  type: "memory"  # "memory" or "redis"
  ttl: 3600  # Cache TTL in seconds
  max_size: 1000
  
  # Redis settings (if type: redis)
  redis_host: "localhost"
  redis_port: 6379
  redis_db: 0
  redis_password: null

# Routing configuration
routing:
  strategy: "intelligent"  # round_robin, least_latency, least_cost, highest_success, intelligent
  fallback_enabled: true
  performance_tracking: true
  
  # Intelligent routing weights (must sum to 1.0)
  success_rate_weight: 0.4
  latency_weight: 0.3
  cost_weight: 0.3

# Security settings
security:
  api_key_validation: true
  rate_limit_enforcement: true
  allowed_domains: null
  blocked_ips: null

# Monitoring settings
monitoring:
  enabled: true
  health_check_interval: 300
  performance_logging: true
  error_reporting: true

# Custom model aliases (optional)
model_aliases:
  fastest:
    - alias: "fastest"
      provider: "groq"
      model_id: "llama3-8b-8192"
      priority: 1
    - alias: "fastest"
      provider: "openai" 
      model_id: "gpt-3.5-turbo"
      priority: 2
"""