"""
Tests for configuration validation system
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError

from modelbridge.config import (
    ModelBridgeConfig,
    ProviderConfig,
    CacheConfig,
    RoutingConfig,
    SecurityConfig,
    MonitoringConfig,
    LogLevel,
    RoutingStrategy,
    ConfigLoader,
    ConfigError,
    create_provider_config,
    create_default_config,
    load_config
)


class TestProviderConfig:
    """Test ProviderConfig validation"""

    def test_valid_provider_config(self):
        """Test valid provider configuration"""
        config = ProviderConfig(
            api_key="test-key",
            enabled=True,
            priority=1,
            timeout=60,
            max_retries=3
        )
        
        assert config.api_key == "test-key"
        assert config.enabled is True
        assert config.priority == 1
        assert config.timeout == 60
        assert config.max_retries == 3

    def test_provider_config_defaults(self):
        """Test provider configuration defaults"""
        config = ProviderConfig()
        
        assert config.api_key is None
        assert config.enabled is True
        assert config.priority == 1
        assert config.timeout == 60
        assert config.max_retries == 3

    def test_invalid_priority(self):
        """Test invalid priority values"""
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 1"):
            ProviderConfig(priority=0)
        
        with pytest.raises(ValidationError, match="Input should be less than or equal to 10"):
            ProviderConfig(priority=11)

    def test_invalid_timeout(self):
        """Test invalid timeout values"""
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 1"):
            ProviderConfig(timeout=0)
        
        with pytest.raises(ValidationError, match="Input should be less than or equal to 300"):
            ProviderConfig(timeout=301)

    def test_empty_api_key_validation(self):
        """Test empty API key validation"""
        with pytest.raises(ValidationError, match="API key cannot be empty string"):
            ProviderConfig(api_key="   ")

    def test_invalid_base_url(self):
        """Test invalid base URL validation"""
        with pytest.raises(ValidationError, match="Base URL must start with http:// or https://"):
            ProviderConfig(base_url="invalid-url")

    def test_valid_base_url(self):
        """Test valid base URLs"""
        config1 = ProviderConfig(base_url="https://api.example.com")
        config2 = ProviderConfig(base_url="http://localhost:8080")
        
        assert config1.base_url == "https://api.example.com"
        assert config2.base_url == "http://localhost:8080"


class TestCacheConfig:
    """Test CacheConfig validation"""

    def test_valid_cache_config(self):
        """Test valid cache configuration"""
        config = CacheConfig(
            enabled=True,
            type="redis",
            ttl=3600,
            max_size=1000,
            redis_host="localhost",
            redis_port=6379
        )
        
        assert config.enabled is True
        assert config.type == "redis"
        assert config.ttl == 3600
        assert config.max_size == 1000

    def test_invalid_cache_type(self):
        """Test invalid cache type"""
        with pytest.raises(ValidationError, match="String should match pattern"):
            CacheConfig(type="invalid")

    def test_invalid_ttl(self):
        """Test invalid TTL values"""
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 60"):
            CacheConfig(ttl=30)
        
        with pytest.raises(ValidationError, match="Input should be less than or equal to 86400"):
            CacheConfig(ttl=90000)

    def test_invalid_redis_port(self):
        """Test invalid Redis port"""
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 1"):
            CacheConfig(redis_port=0)
        
        with pytest.raises(ValidationError, match="Input should be less than or equal to 65535"):
            CacheConfig(redis_port=70000)


class TestRoutingConfig:
    """Test RoutingConfig validation"""

    def test_valid_routing_config(self):
        """Test valid routing configuration"""
        config = RoutingConfig(
            strategy=RoutingStrategy.INTELLIGENT,
            fallback_enabled=True,
            success_rate_weight=0.5,
            latency_weight=0.3,
            cost_weight=0.2
        )
        
        assert config.strategy == RoutingStrategy.INTELLIGENT
        assert config.fallback_enabled is True
        assert config.success_rate_weight == 0.5

    def test_invalid_weight_values(self):
        """Test invalid weight values"""
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
            RoutingConfig(success_rate_weight=-0.1)
        
        with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
            RoutingConfig(latency_weight=1.1)

    def test_invalid_weight_sum(self):
        """Test invalid weight sum"""
        with pytest.raises(ValidationError, match="Routing weights must sum to 1.0"):
            RoutingConfig(
                success_rate_weight=0.5,
                latency_weight=0.5,
                cost_weight=0.2  # Sum = 1.2
            )


class TestModelBridgeConfig:
    """Test complete ModelBridge configuration"""

    def test_valid_complete_config(self):
        """Test valid complete configuration"""
        config = ModelBridgeConfig(
            debug=False,
            log_level=LogLevel.INFO,
            providers={
                "openai": ProviderConfig(api_key="test-key", enabled=True)
            },
            cache=CacheConfig(enabled=True, type="memory"),
            routing=RoutingConfig(strategy=RoutingStrategy.INTELLIGENT)
        )
        
        assert config.debug is False
        assert config.log_level == LogLevel.INFO
        assert "openai" in config.providers

    def test_invalid_provider_name(self):
        """Test invalid provider name"""
        with pytest.raises(ValidationError, match="Unknown provider"):
            ModelBridgeConfig(
                providers={
                    "invalid_provider": ProviderConfig(api_key="test-key")
                }
            )

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden"""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ModelBridgeConfig(unknown_field="value")

    def test_default_configuration(self):
        """Test default configuration creation"""
        config = create_default_config()
        
        assert isinstance(config, ModelBridgeConfig)
        assert config.debug is False
        assert config.log_level == LogLevel.INFO
        assert config.cache.enabled is True
        assert config.routing.strategy == RoutingStrategy.INTELLIGENT


class TestConfigLoader:
    """Test ConfigLoader functionality"""

    def test_load_from_env_no_keys(self):
        """Test loading from environment with no API keys"""
        with patch.dict('os.environ', {}, clear=True):
            loader = ConfigLoader()
            config = loader.load_from_env()
            
            assert isinstance(config, ModelBridgeConfig)
            assert len(config.providers) == 0

    def test_load_from_env_with_keys(self):
        """Test loading from environment with API keys"""
        env_vars = {
            'OPENAI_API_KEY': 'test-openai-key',
            'ANTHROPIC_API_KEY': 'test-anthropic-key',
            'MODELBRIDGE_DEBUG': 'true',
            'MODELBRIDGE_LOG_LEVEL': 'debug',
            'MODELBRIDGE_CACHE_ENABLED': 'false'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            loader = ConfigLoader()
            config = loader.load_from_env()
            
            assert config.debug is True
            assert config.log_level == LogLevel.DEBUG
            assert config.cache.enabled is False
            assert len(config.providers) == 2
            assert "openai" in config.providers
            assert "anthropic" in config.providers
            assert config.providers["openai"].api_key == "test-openai-key"

    def test_load_from_dict(self):
        """Test loading from dictionary"""
        config_dict = {
            "debug": True,
            "log_level": "warning",
            "providers": {
                "openai": {
                    "api_key": "test-key",
                    "enabled": True,
                    "priority": 1
                }
            }
        }
        
        loader = ConfigLoader()
        config = loader.load_from_dict(config_dict)
        
        assert config.debug is True
        assert config.log_level == LogLevel.WARNING
        assert config.providers["openai"].api_key == "test-key"

    def test_load_from_invalid_dict(self):
        """Test loading from invalid dictionary"""
        config_dict = {
            "providers": {
                "invalid_provider": {"api_key": "test"}
            }
        }
        
        loader = ConfigLoader()
        with pytest.raises(ConfigError, match="Configuration validation failed"):
            loader.load_from_dict(config_dict)

    def test_load_from_yaml_file(self):
        """Test loading from YAML file"""
        yaml_content = """
debug: true
log_level: "info"
providers:
  openai:
    api_key: "test-openai-key"
    enabled: true
    priority: 1
cache:
  enabled: true
  type: "memory"
  ttl: 1800
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                with patch.dict('os.environ', {'MODELBRIDGE_DEBUG': 'true'}, clear=True):
                    loader = ConfigLoader()
                    config = loader.load_from_file(f.name)
                    
                    assert config.debug is True
                    assert config.log_level == LogLevel.INFO
                    assert config.providers["openai"].api_key == "test-openai-key"
                    assert config.cache.ttl == 1800
            finally:
                os.unlink(f.name)

    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file"""
        loader = ConfigLoader()
        
        with pytest.raises(ConfigError, match="Configuration file not found"):
            loader.load_from_file("nonexistent.yaml")

    def test_load_from_invalid_yaml(self):
        """Test loading from invalid YAML"""
        invalid_yaml = """
debug: true
providers:
  openai:
    api_key: "test"
    invalid_yaml: [unclosed
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()
            
            try:
                loader = ConfigLoader()
                with pytest.raises(ConfigError, match="Failed to parse YAML"):
                    loader.load_from_file(f.name)
            finally:
                os.unlink(f.name)

    def test_validate_config_no_providers(self):
        """Test config validation with no providers"""
        config = ModelBridgeConfig(providers={})
        loader = ConfigLoader()
        
        # Should not raise exception but log warning
        loader.validate_config(config)

    def test_validate_config_invalid_weights(self):
        """Test config validation with invalid routing weights"""
        # Test that invalid weights are caught during model creation
        with pytest.raises(ValidationError, match="Routing weights must sum to 1.0"):
            ModelBridgeConfig(
                routing=RoutingConfig(
                    success_rate_weight=0.5,
                    latency_weight=0.3,
                    cost_weight=0.3  # Sum = 1.1
                )
            )


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_create_provider_config(self):
        """Test create_provider_config function"""
        config = create_provider_config(
            api_key="test-key",
            enabled=True,
            priority=2,
            timeout=30,
            max_requests_per_minute=1000
        )
        
        assert config.api_key == "test-key"
        assert config.enabled is True
        assert config.priority == 2
        assert config.timeout == 30
        assert config.max_requests_per_minute == 1000

    def test_load_config_function(self):
        """Test load_config convenience function"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            config = load_config()
            
            assert isinstance(config, ModelBridgeConfig)
            assert "openai" in config.providers


class TestConfigIntegration:
    """Integration tests for configuration system"""

    def test_full_config_lifecycle(self):
        """Test complete configuration lifecycle"""
        # Create config dict
        config_dict = {
            "debug": True,
            "log_level": "debug",
            "default_timeout": 120,
            "providers": {
                "openai": {
                    "api_key": "test-openai-key",
                    "enabled": True,
                    "priority": 1,
                    "timeout": 60,
                    "max_retries": 2
                },
                "anthropic": {
                    "api_key": "test-anthropic-key",
                    "enabled": True,
                    "priority": 2,
                    "timeout": 90
                }
            },
            "cache": {
                "enabled": True,
                "type": "memory",
                "ttl": 1800,
                "max_size": 500
            },
            "routing": {
                "strategy": "least_latency",
                "fallback_enabled": True,
                "performance_tracking": True,
                "success_rate_weight": 0.3,
                "latency_weight": 0.5,
                "cost_weight": 0.2
            },
            "security": {
                "api_key_validation": True,
                "rate_limit_enforcement": True
            },
            "monitoring": {
                "enabled": True,
                "health_check_interval": 600,
                "performance_logging": False
            }
        }
        
        # Load and validate
        loader = ConfigLoader()
        config = loader.load_from_dict(config_dict)
        
        # Verify all aspects
        assert config.debug is True
        assert config.log_level == LogLevel.DEBUG
        assert config.default_timeout == 120
        
        # Providers
        assert len(config.providers) == 2
        assert config.providers["openai"].api_key == "test-openai-key"
        assert config.providers["anthropic"].timeout == 90
        
        # Cache
        assert config.cache.enabled is True
        assert config.cache.type == "memory"
        assert config.cache.ttl == 1800
        
        # Routing
        assert config.routing.strategy == RoutingStrategy.LEAST_LATENCY
        assert config.routing.fallback_enabled is True
        assert config.routing.latency_weight == 0.5
        
        # Security
        assert config.security.api_key_validation is True
        
        # Monitoring
        assert config.monitoring.enabled is True
        assert config.monitoring.health_check_interval == 600
        assert config.monitoring.performance_logging is False
        
        # Additional validation
        loader.validate_config(config)