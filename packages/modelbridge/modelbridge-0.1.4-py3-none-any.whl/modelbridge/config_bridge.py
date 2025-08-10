"""
Enhanced ModelBridge with Pydantic configuration validation
"""
import asyncio
import os
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging
from pydantic import ValidationError

from .config import (
    ModelBridgeConfig, 
    ConfigLoader, 
    ConfigError,
    load_config
)
from .bridge import IntelligentRouter, ModelAlias
from .cache import CacheFactory, CacheInterface
from .cache.decorators import CacheManager
from .ratelimit import RateLimitFactory
from .ratelimit.base import RateLimiter, RateLimitError
from .ratelimit.decorators import ProviderRateLimitManager
from .monitoring import (
    MetricsCollector, HealthChecker, AlertManager, PerformanceMonitor,
    console_notification_handler, log_notification_handler,
    WebhookNotificationHandler, SlackNotificationHandler
)
from .monitoring.health import ProviderHealthChecker, CacheHealthChecker, RateLimitHealthChecker
from .providers.base import (
    BaseModelProvider, 
    GenerationRequest, 
    GenerationResponse
)
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.groq import GroqProvider

logger = logging.getLogger(__name__)


class ValidatedModelBridge:
    """
    Enterprise-grade ModelBridge with comprehensive features for production use.
    
    ValidatedModelBridge provides a robust, production-ready interface to multiple
    LLM providers with advanced features including:
    
    - **Multi-Provider Support**: OpenAI, Anthropic, Google, Groq
    - **Intelligent Routing**: Fallback, load balancing, performance-based routing
    - **Caching**: Redis/Memory-based response caching with TTL
    - **Rate Limiting**: Per-provider and global rate limiting with backpressure
    - **Monitoring**: Comprehensive metrics, health checks, and alerting
    - **Reliability**: Retry logic, circuit breakers, timeout handling
    - **Configuration**: Pydantic V2 validation with YAML/JSON/env support
    
    Example:
        ```python
        # Basic usage
        bridge = ValidatedModelBridge()
        await bridge.initialize()
        
        response = await bridge.generate_text(
            prompt="Explain quantum computing",
            model="best",
            temperature=0.7
        )
        
        # Advanced configuration
        config = {
            "providers": {
                "openai": {"api_key": "sk-...", "enabled": True},
                "anthropic": {"api_key": "sk-ant-...", "enabled": True}
            },
            "cache": {"enabled": True, "type": "redis", "ttl": 3600},
            "rate_limiting": {"enabled": True, "global_requests_per_minute": 1000},
            "monitoring": {"enabled": True, "collect_detailed_metrics": True}
        }
        
        bridge = ValidatedModelBridge(config)
        await bridge.initialize()
        
        # Access monitoring data
        health = await bridge.health_check()
        metrics = await bridge.get_metrics()
        alerts = await bridge.get_active_alerts()
        ```
    
    Attributes:
        config (ModelBridgeConfig): Validated configuration object
        providers (Dict[str, BaseModelProvider]): Initialized provider instances
        cache (CacheInterface): Cache system instance
        metrics_collector (MetricsCollector): Metrics collection system
        health_checker (HealthChecker): Health monitoring system
        alert_manager (AlertManager): Alert management system
        performance_monitor (PerformanceMonitor): Performance analysis system
    """
    
    def __init__(self, config: Optional[Union[str, Path, Dict[str, Any], ModelBridgeConfig]] = None):
        """
        Initialize ModelBridge with validated configuration.
        
        Args:
            config: Configuration source. Can be:
                - None: Load from environment variables
                - str/Path: Path to YAML/JSON configuration file
                - dict: Configuration dictionary
                - ModelBridgeConfig: Pre-validated configuration object
                
        Raises:
            ConfigError: If configuration is invalid or cannot be loaded
            ValidationError: If configuration fails Pydantic validation
            
        Example:
            ```python
            # From environment variables
            bridge = ValidatedModelBridge()
            
            # From file
            bridge = ValidatedModelBridge("config.yaml")
            
            # From dictionary
            bridge = ValidatedModelBridge({
                "providers": {"openai": {"api_key": "sk-..."}}
            })
            ```
        """
        self.config: ModelBridgeConfig = self._load_and_validate_config(config)
        self.providers: Dict[str, BaseModelProvider] = {}
        self.intelligent_router = IntelligentRouter()
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        
        # Initialize caching system
        self.cache: Optional[CacheInterface] = None
        self.cache_manager: Optional[CacheManager] = None
        
        # Initialize rate limiting system
        self.rate_limiter: Optional[RateLimiter] = None
        self.rate_limit_manager: Optional[ProviderRateLimitManager] = None
        
        # Initialize monitoring system
        self.metrics_collector: Optional[MetricsCollector] = None
        self.health_checker: Optional[HealthChecker] = None
        self.alert_manager: Optional[AlertManager] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        self.provider_health_checker: Optional[ProviderHealthChecker] = None
        self.cache_health_checker: Optional[CacheHealthChecker] = None
        self.rate_limit_health_checker: Optional[RateLimitHealthChecker] = None
        
        # Provider classes mapping
        self.provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
            "groq": GroqProvider,
        }
        
        # Setup model aliases from config
        self.model_aliases = self._setup_model_aliases()
        
        # Configure logging
        self._setup_logging()
        
        logger.info(f"ModelBridge initialized with {len(self._get_available_providers())} available providers")
    
    def _load_and_validate_config(self, config: Optional[Union[str, Path, Dict, ModelBridgeConfig]]) -> ModelBridgeConfig:
        """Load and validate configuration"""
        try:
            if config is None:
                # Load from environment variables
                return load_config()
            elif isinstance(config, ModelBridgeConfig):
                # Already validated
                return config
            elif isinstance(config, (str, Path)):
                # Load from file
                return load_config(config)
            elif isinstance(config, dict):
                # Load from dictionary
                loader = ConfigLoader()
                return loader.load_from_dict(config)
            else:
                raise ConfigError(f"Unsupported config type: {type(config)}")
                
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            raise ConfigError(f"Failed to load configuration: {e}")
    
    def _setup_logging(self):
        """Setup logging based on configuration"""
        log_level = getattr(logging, self.config.log_level.upper())
        logging.getLogger('modelbridge').setLevel(log_level)
        
        if self.config.debug:
            logging.getLogger('modelbridge').setLevel(logging.DEBUG)
    
    def _get_available_providers(self) -> List[str]:
        """Get list of providers with valid API keys"""
        available = []
        
        for provider_name, provider_config in self.config.providers.items():
            if provider_config.enabled and provider_config.api_key:
                available.append(provider_name)
            elif provider_config.enabled:
                # Check environment variables as fallback
                env_key = f"{provider_name.upper()}_API_KEY"
                if os.getenv(env_key):
                    available.append(provider_name)
        
        return available
    
    def _setup_model_aliases(self) -> Dict[str, List[ModelAlias]]:
        """Setup model aliases from configuration"""
        aliases = {}
        
        # Use custom aliases from config if provided
        if self.config.model_aliases:
            for alias_name, models in self.config.model_aliases.items():
                aliases[alias_name] = [
                    ModelAlias(
                        alias=model["alias"],
                        provider=model["provider"],
                        model_id=model["model_id"],
                        priority=model.get("priority", 1)
                    )
                    for model in models
                ]
        else:
            # Use default aliases
            aliases = {
                "fastest": [
                    ModelAlias("fastest", "groq", "llama3-8b-8192", 1),
                    ModelAlias("fastest", "openai", "gpt-3.5-turbo", 2),
                    ModelAlias("fastest", "google", "gemini-1.5-flash", 3),
                ],
                "cheapest": [
                    ModelAlias("cheapest", "groq", "llama3-8b-8192", 1),
                    ModelAlias("cheapest", "google", "gemini-1.5-flash", 2),
                    ModelAlias("cheapest", "openai", "gpt-3.5-turbo", 3),
                ],
                "best": [
                    ModelAlias("best", "anthropic", "claude-3-opus-20240229", 1),
                    ModelAlias("best", "openai", "gpt-4-turbo", 2),
                    ModelAlias("best", "google", "gemini-1.5-pro", 3),
                ],
                "balanced": [
                    ModelAlias("balanced", "anthropic", "claude-3-sonnet-20240229", 1),
                    ModelAlias("balanced", "openai", "gpt-4", 2),
                    ModelAlias("balanced", "google", "gemini-1.5-pro", 3),
                    ModelAlias("balanced", "groq", "mixtral-8x7b-32768", 4),
                ],
            }
        
        return aliases
    
    async def initialize(self, force_reload: bool = False) -> bool:
        """
        Initialize all systems including providers, caching, rate limiting, and monitoring.
        
        This method performs comprehensive system initialization:
        - Validates configuration
        - Initializes cache system (Memory/Redis)
        - Sets up rate limiting with backpressure
        - Starts monitoring and health checking
        - Initializes all enabled providers
        - Configures intelligent routing
        
        Args:
            force_reload: If True, reinitialize even if already initialized
            
        Returns:
            bool: True if initialization successful, False otherwise
            
        Raises:
            ConfigError: If configuration validation fails
            ConnectionError: If critical services (Redis, providers) fail
            
        Example:
            ```python
            bridge = ValidatedModelBridge(config)
            
            # Initialize all systems
            success = await bridge.initialize()
            if not success:
                print("Failed to initialize ModelBridge")
                return
            
            # Bridge is ready for use
            response = await bridge.generate_text("Hello, world!")
            ```
        """
        if self._initialized and not force_reload:
            return True
        
        try:
            # Additional config validation
            loader = ConfigLoader()
            loader.validate_config(self.config)
            
            # Initialize caching system
            await self._initialize_cache()
            
            # Initialize rate limiting system
            await self._initialize_rate_limiting()
            
            # Initialize monitoring system
            await self._initialize_monitoring()
            
            # Get available providers
            available_providers = self._get_available_providers()
            
            if not available_providers:
                logger.warning("No providers with valid API keys found")
                return False
            
            # Initialize providers
            for provider_name in available_providers:
                if provider_name not in self.provider_classes:
                    logger.warning(f"Unknown provider: {provider_name}")
                    continue
                
                # Get provider config
                provider_config = self.config.providers.get(provider_name)
                if not provider_config:
                    # Fallback to environment variables
                    api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
                    if not api_key:
                        continue
                    
                    # Create basic config
                    config_dict = {
                        "api_key": api_key,
                        "timeout": self.config.default_timeout,
                        "enabled": True
                    }
                else:
                    # Use validated config
                    config_dict = provider_config.model_dump()
                
                success = await self._initialize_provider(provider_name, config_dict)
                if success:
                    logger.info(f"Initialized provider: {provider_name}")
                else:
                    logger.warning(f"Failed to initialize provider: {provider_name}")
            
            if self.providers:
                # Configure provider rate limits
                await self._configure_provider_rate_limits()
                
                self._initialized = True
                logger.info(f"ModelBridge initialized with {len(self.providers)} providers")
                return True
            else:
                logger.error("No providers initialized successfully")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize ModelBridge: {str(e)}")
            return False
    
    async def _initialize_cache(self) -> None:
        """Initialize cache system based on configuration"""
        try:
            self.cache = await CacheFactory.create_cache(self.config.cache)
            
            if self.cache:
                self.cache_manager = CacheManager(self.cache)
                logger.info(f"Cache initialized: {self.config.cache.type}")
            else:
                logger.info("Cache disabled or initialization failed")
                
        except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
            # Create fallback cache
            try:
                self.cache = await CacheFactory.create_fallback_cache()
                self.cache_manager = CacheManager(self.cache)
                logger.info("Using fallback memory cache")
            except Exception as fallback_error:
                logger.error(f"Failed to create fallback cache: {fallback_error}")
                self.cache = None
                self.cache_manager = None
    
    async def _initialize_rate_limiting(self) -> None:
        """Initialize rate limiting system based on configuration"""
        try:
            if not self.config.rate_limiting.enabled:
                logger.info("Rate limiting disabled")
                return
            
            # Convert config to rate limit factory format
            redis_config = {
                "host": self.config.rate_limiting.redis_host,
                "port": self.config.rate_limiting.redis_port,
                "db": self.config.rate_limiting.redis_db,
                "password": self.config.rate_limiting.redis_password,
                "key_prefix": self.config.rate_limiting.redis_key_prefix
            }
            
            self.rate_limiter = await RateLimitFactory.create_rate_limiter(
                backend=self.config.rate_limiting.backend,
                algorithm=self.config.rate_limiting.algorithm,
                redis_config=redis_config if self.config.rate_limiting.backend == "redis" else None,
                cleanup_interval=self.config.rate_limiting.cleanup_interval
            )
            
            if self.rate_limiter:
                self.rate_limit_manager = ProviderRateLimitManager(self.rate_limiter)
                logger.info(f"Rate limiter initialized: {self.config.rate_limiting.backend}/{self.config.rate_limiting.algorithm}")
            else:
                logger.warning("Rate limiter initialization failed, attempting fallback")
                # Attempt fallback to memory rate limiter
                self.rate_limiter = await RateLimitFactory.create_fallback_rate_limiter(
                    algorithm=self.config.rate_limiting.algorithm,
                    cleanup_interval=self.config.rate_limiting.cleanup_interval
                )
                if self.rate_limiter:
                    self.rate_limit_manager = ProviderRateLimitManager(self.rate_limiter)
                    logger.info("Using fallback memory rate limiter")
                
        except Exception as e:
            logger.warning(f"Failed to initialize rate limiting: {e}")
            # Create fallback rate limiter
            try:
                self.rate_limiter = await RateLimitFactory.create_fallback_rate_limiter(
                    algorithm=self.config.rate_limiting.algorithm,
                    cleanup_interval=self.config.rate_limiting.cleanup_interval
                )
                self.rate_limit_manager = ProviderRateLimitManager(self.rate_limiter)
                logger.info("Using fallback memory rate limiter")
            except Exception as fallback_error:
                logger.error(f"Failed to create fallback rate limiter: {fallback_error}")
                self.rate_limiter = None
                self.rate_limit_manager = None
    
    async def _initialize_monitoring(self) -> None:
        """Initialize monitoring system based on configuration"""
        try:
            if not self.config.monitoring.enabled:
                logger.info("Monitoring system disabled")
                return
            
            # Initialize metrics collector
            self.metrics_collector = MetricsCollector()
            
            # Initialize health checker
            self.health_checker = HealthChecker(
                check_interval=self.config.monitoring.health_check_interval
            )
            
            # Initialize specialized health checkers
            self.provider_health_checker = ProviderHealthChecker(self.health_checker)
            self.cache_health_checker = CacheHealthChecker(self.health_checker)
            self.rate_limit_health_checker = RateLimitHealthChecker(self.health_checker)
            
            # Initialize alert manager
            self.alert_manager = AlertManager()
            
            # Setup notification handlers
            if self.config.monitoring.alerting_enabled:
                self.alert_manager.add_notification_handler(console_notification_handler)
                self.alert_manager.add_notification_handler(log_notification_handler)
                
                if self.config.monitoring.webhook_url:
                    webhook_handler = WebhookNotificationHandler(self.config.monitoring.webhook_url)
                    self.alert_manager.add_notification_handler(webhook_handler)
                
                if self.config.monitoring.slack_webhook_url:
                    slack_handler = SlackNotificationHandler(self.config.monitoring.slack_webhook_url)
                    self.alert_manager.add_notification_handler(slack_handler)
            
            # Initialize performance monitor
            if self.config.monitoring.performance_monitoring:
                self.performance_monitor = PerformanceMonitor(
                    metrics_collector=self.metrics_collector,
                    health_checker=self.health_checker
                )
            
            # Register cache and rate limiter for health checking
            if self.cache:
                self.cache_health_checker.register_cache("main", self.cache)
            
            if self.rate_limiter:
                self.rate_limit_health_checker.register_rate_limiter("main", self.rate_limiter)
            
            logger.info("Monitoring system initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize monitoring system: {e}")
            # Create minimal monitoring components to prevent errors
            try:
                self.metrics_collector = MetricsCollector()
                self.health_checker = HealthChecker()
                self.alert_manager = AlertManager()
                self.performance_monitor = None
            except Exception as fallback_error:
                logger.error(f"Failed to create fallback monitoring components: {fallback_error}")
                # Set to None to avoid further errors
                self.metrics_collector = None
                self.health_checker = None
                self.alert_manager = None
                self.performance_monitor = None
    
    async def _configure_provider_rate_limits(self) -> None:
        """Configure rate limits for each provider"""
        if not self.rate_limit_manager:
            return
        
        for provider_name, provider_config in self.config.providers.items():
            if provider_name not in self.providers or not provider_config.enabled:
                continue
            
            # Configure provider-specific rate limits
            requests_per_minute = provider_config.max_requests_per_minute
            tokens_per_minute = provider_config.max_tokens_per_minute
            
            # Use global defaults if provider-specific limits not set
            if not requests_per_minute:
                requests_per_minute = self.config.rate_limiting.global_requests_per_minute
            if not tokens_per_minute:
                tokens_per_minute = self.config.rate_limiting.global_tokens_per_minute
            
            # Configure rate limits for this provider
            self.rate_limit_manager.configure_provider(
                provider_name=provider_name,
                requests_per_minute=requests_per_minute,
                tokens_per_minute=tokens_per_minute,
                requests_per_hour=self.config.rate_limiting.global_requests_per_hour,
                tokens_per_hour=self.config.rate_limiting.global_tokens_per_hour
            )
        
        logger.info(f"Configured rate limits for {len(self.providers)} providers")
    
    async def _initialize_provider(self, provider_name: str, provider_config: Dict[str, Any]) -> bool:
        """Initialize a single provider"""
        try:
            provider_class = self.provider_classes.get(provider_name)
            if not provider_class:
                return False
            
            provider = provider_class(provider_config)
            success = await provider.initialize()
            
            if success:
                self.providers[provider_name] = provider
                
                # Register provider with monitoring systems
                if self.provider_health_checker:
                    self.provider_health_checker.register_provider(provider_name, provider)
                
                if self.performance_monitor:
                    self.performance_monitor.register_provider(provider_name)
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error initializing provider {provider_name}: {str(e)}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "balanced",
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> GenerationResponse:
        """
        Generate text using intelligent provider routing with caching and monitoring.
        
        This method provides the core text generation functionality with enterprise
        features including automatic failover, response caching, rate limiting,
        and comprehensive monitoring.
        
        Args:
            prompt: The input text prompt for generation
            model: Model specification. Can be:
                - Model alias: "best", "fastest", "cheapest", "balanced"
                - Provider:model: "openai:gpt-4", "anthropic:claude-3-opus"
                - Direct model ID: "gpt-4-turbo"
            system_message: Optional system message to guide model behavior
            temperature: Sampling temperature (0.0-2.0). Controls randomness
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            GenerationResponse: Response object containing:
                - content: Generated text content
                - model_id: Actual model used
                - provider_name: Provider that handled the request
                - usage: Token usage statistics
                - cost: Estimated cost for the request
                - response_time: Request duration in seconds
                - error: Error message if request failed
                
        Raises:
            ValueError: If prompt is empty or invalid
            RateLimitError: If rate limits are exceeded
            ConnectionError: If all providers fail
            
        Example:
            ```python
            # Basic usage
            response = await bridge.generate_text(
                prompt="Explain machine learning in simple terms",
                model="best"
            )
            
            # Advanced usage with parameters
            response = await bridge.generate_text(
                prompt="Write a Python function to calculate fibonacci",
                model="openai:gpt-4",
                system_message="You are an expert Python developer",
                temperature=0.1,
                max_tokens=500,
                stop=["def", "class"]  # Provider-specific parameter
            )
            
            # Handle response
            if response.error:
                print(f"Error: {response.error}")
            else:
                print(f"Generated: {response.content}")
                print(f"Cost: ${response.cost:.4f}")
                print(f"Model: {response.model_id}")
            ```
        """
        request = GenerationRequest(
            prompt=prompt,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_params=kwargs
        )
        
        return await self._route_request(request, model, "generate_text")
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        model: str = "balanced",
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> GenerationResponse:
        """Generate structured output with validated configuration"""
        request = GenerationRequest(
            prompt=prompt,
            system_message=system_message,
            temperature=temperature,
            output_schema=schema,
            extra_params=kwargs
        )
        
        return await self._route_request(request, model, "generate_structured_output")
    
    async def _route_request(
        self,
        request: GenerationRequest,
        model_spec: str,
        method_name: str
    ) -> GenerationResponse:
        """Route request with configuration-aware routing and caching"""
        if not self._initialized:
            return GenerationResponse(
                content="",
                model_id=model_spec,
                provider_name="gateway",
                error="ModelBridge not initialized"
            )
        
        # Generate cache key if caching is enabled
        cache_key = None
        if self.cache_manager and self.config.cache.enabled:
            key_part = self.cache.generate_key(
                request.prompt, 
                request.system_message,
                request.temperature,
                request.max_tokens,
                request.output_schema
            )
            cache_key = f"{method_name}:{model_spec}:{key_part}"
            
            # Try to get cached response
            try:
                cached_response = await self.cache.get_with_stats(cache_key)
                if cached_response is not None:
                    logger.debug(f"Cache hit for {method_name} request")
                    return cached_response
            except Exception as e:
                logger.warning(f"Cache lookup failed: {e}")
        
        # Resolve model specification
        model_options = self._resolve_model_spec(model_spec)
        
        if not model_options:
            return GenerationResponse(
                content="",
                model_id=model_spec,
                provider_name="gateway",
                error=f"No providers available for model: {model_spec}"
            )
        
        # Try each model option with fallback if enabled
        last_error = None
        request_id = f"{int(time.time() * 1000)}_{hash(request.prompt) % 10000}"
        start_time = time.time()
        
        # Record request start in metrics
        if self.metrics_collector:
            self.metrics_collector.record_request_start(request_id, model_spec, method_name)
        
        for alias in model_options:
            provider = self.providers.get(alias.provider)
            if not provider:
                continue
            
            try:
                # Check rate limits before making request
                if self.rate_limit_manager:
                    try:
                        # Calculate token count (estimate based on prompt length for now)
                        estimated_tokens = len(request.prompt.split()) * 2  # Rough estimate
                        
                        await self.rate_limit_manager.enforce_provider_limits(
                            provider_name=alias.provider,
                            api_key=None,  # Could extract from provider config if needed
                            tokens=estimated_tokens
                        )
                    except RateLimitError as e:
                        logger.warning(f"Rate limit exceeded for {alias.provider}: {e}")
                        if not self.config.routing.fallback_enabled:
                            return GenerationResponse(
                                content="",
                                model_id=model_spec,
                                provider_name=alias.provider,
                                error=f"Rate limit exceeded: {str(e)}"
                            )
                        continue  # Try next provider
                
                # Make request
                method = getattr(provider, method_name)
                provider_start_time = time.time()
                response = await method(request, alias.model_id)
                provider_duration = time.time() - provider_start_time
                
                # Record metrics and performance data
                success = not response.error
                
                if self.metrics_collector:
                    self.metrics_collector.record_request_complete(
                        request_id=request_id,
                        provider=alias.provider,
                        model=alias.model_id,
                        method=method_name,
                        duration=provider_duration,
                        success=success,
                        error_type=response.error if not success else None,
                        cost=response.cost or 0.0,
                        tokens_used=getattr(response, 'usage', {}).get('total_tokens', 0)
                    )
                
                if self.performance_monitor:
                    self.performance_monitor.record_request(
                        provider_name=alias.provider,
                        model_name=alias.model_id,
                        duration=provider_duration,
                        success=success,
                        cost=response.cost or 0.0,
                        tokens=getattr(response, 'usage', {}).get('total_tokens', 0),
                        error_type=response.error if not success else None
                    )
                
                # Update performance tracking if enabled
                if self.config.routing.performance_tracking and success:
                    self._update_performance_stats(
                        alias.provider,
                        alias.model_id,
                        response.response_time or provider_duration,
                        response.cost or 0,
                        success
                    )
                
                # Cache successful response
                if cache_key and not response.error and self.cache_manager:
                    try:
                        await self.cache.set_with_stats(cache_key, response, self.config.cache.ttl)
                        logger.debug(f"Cached successful {method_name} response")
                    except Exception as e:
                        logger.warning(f"Failed to cache response: {e}")
                
                # Return successful response or continue if fallback enabled
                if not response.error or not self.config.routing.fallback_enabled:
                    return response
                
                last_error = response.error
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error with provider {alias.provider}: {str(e)}")
                
                if not self.config.routing.fallback_enabled:
                    break
                continue
        
        # All providers failed
        return GenerationResponse(
            content="",
            model_id=model_spec,
            provider_name="gateway",
            error=f"All providers failed. Last error: {last_error}"
        )
    
    def _resolve_model_spec(self, model_spec: str) -> List[ModelAlias]:
        """Resolve model specification to available providers"""
        # Check if it's an alias
        if model_spec in self.model_aliases:
            available_aliases = []
            for alias in self.model_aliases[model_spec]:
                if alias.provider in self.providers:
                    available_aliases.append(alias)
            return available_aliases
        
        # Check if it's a direct provider:model specification
        if ":" in model_spec:
            provider_name, model_id = model_spec.split(":", 1)
            if provider_name in self.providers:
                return [ModelAlias(model_spec, provider_name, model_id, 1)]
        
        # Fallback to balanced alias
        if model_spec != "balanced" and "balanced" in self.model_aliases:
            return self._resolve_model_spec("balanced")
        
        return []
    
    def _update_performance_stats(
        self,
        provider: str,
        model_id: str,
        response_time: float,
        cost: float,
        success: bool
    ):
        """Update performance statistics"""
        key = f"{provider}:{model_id}"
        
        if key not in self.performance_stats:
            self.performance_stats[key] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0,
                "total_cost": 0,
                "avg_response_time": 0,
                "avg_cost": 0,
                "success_rate": 0
            }
        
        stats = self.performance_stats[key]
        stats["total_requests"] += 1
        stats["total_response_time"] += response_time
        stats["total_cost"] += cost
        
        if success:
            stats["successful_requests"] += 1
        
        # Update averages
        stats["avg_response_time"] = stats["total_response_time"] / stats["total_requests"]
        stats["avg_cost"] = stats["total_cost"] / stats["total_requests"]
        stats["success_rate"] = stats["successful_requests"] / stats["total_requests"]
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics"""
        return self.performance_stats.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all system components.
        
        Checks the health of providers, cache systems, rate limiters, and
        overall system status. Useful for monitoring, load balancing, and
        debugging system issues.
        
        Returns:
            Dict containing health information:
                - status: Overall system status ("healthy", "degraded", "unhealthy")
                - timestamp: When the check was performed
                - uptime_seconds: System uptime
                - components: Individual component health status
                    - providers: Each provider's health and response time
                    - cache: Cache system health and statistics
                    - rate_limiter: Rate limiting system status
                    - monitoring: Monitoring system status
                    
        Example:
            ```python
            health = await bridge.health_check()
            
            print(f"System status: {health['status']}")
            print(f"Uptime: {health['uptime_seconds']:.0f}s")
            
            # Check individual components
            for name, component in health['components'].items():
                status = component['status']
                response_time = component.get('response_time_ms', 0)
                print(f"{name}: {status} ({response_time}ms)")
                
            # Alert if any component is unhealthy
            unhealthy = [name for name, comp in health['components'].items() 
                        if comp['status'] == 'unhealthy']
            if unhealthy:
                print(f"Unhealthy components: {unhealthy}")
            ```
        """
        if self.health_checker:
            # Use comprehensive health checking system
            system_health = await self.health_checker.get_system_health()
            return system_health.to_dict()
        else:
            # Fallback to basic provider health checks
            health_results = {}
            overall_healthy = False
            
            for provider_name, provider in self.providers.items():
                try:
                    health_result = await provider.health_check()
                    health_results[provider_name] = health_result
                    if health_result.get("status") == "healthy":
                        overall_healthy = True
                except Exception as e:
                    health_results[provider_name] = {
                        "status": "unhealthy",
                        "error": str(e),
                        "provider": provider_name
                    }
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "providers": health_results,
                "total_providers": len(self.providers),
                "healthy_providers": sum(1 for result in health_results.values() if result.get("status") == "healthy"),
                "config_valid": True,
                "configuration": {
                    "routing_strategy": self.config.routing.strategy,
                    "cache_enabled": self.config.cache.enabled,
                    "fallback_enabled": self.config.routing.fallback_enabled
                }
            }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "providers": {
                name: {
                    "enabled": config.enabled,
                    "priority": config.priority,
                    "timeout": config.timeout
                }
                for name, config in self.config.providers.items()
            },
            "routing": {
                "strategy": self.config.routing.strategy,
                "fallback_enabled": self.config.routing.fallback_enabled,
                "performance_tracking": self.config.routing.performance_tracking
            },
            "cache": {
                "enabled": self.config.cache.enabled,
                "type": self.config.cache.type,
                "ttl": self.config.cache.ttl
            }
        }
    
    async def get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics"""
        if not self.cache:
            return None
        
        try:
            return await self.cache.get_stats()
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return None
    
    async def clear_cache(self, pattern: Optional[str] = None) -> bool:
        """Clear cache entries"""
        if not self.cache:
            return False
        
        try:
            if pattern:
                # Pattern-based clearing would require cache-specific implementation
                logger.warning("Pattern-based cache clearing not implemented")
                return False
            else:
                return await self.cache.clear()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def warm_cache(self, requests: list) -> int:
        """
        Warm cache with common requests
        
        Args:
            requests: List of (prompt, model, options) tuples
            
        Returns:
            Number of requests cached
        """
        if not self.cache_manager:
            return 0
        
        warmed = 0
        for prompt, model, options in requests:
            try:
                # Create request object
                request = GenerationRequest(
                    prompt=prompt,
                    system_message=options.get("system_message"),
                    temperature=options.get("temperature"),
                    max_tokens=options.get("max_tokens")
                )
                
                # Generate response and cache it
                response = await self.generate_text(
                    prompt=prompt,
                    model=model,
                    **options
                )
                
                if not response.error:
                    warmed += 1
                    
            except Exception as e:
                logger.warning(f"Failed to warm cache for request: {e}")
        
        logger.info(f"Warmed cache with {warmed} requests")
        return warmed
    
    async def get_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive system metrics for monitoring and analysis.
        
        Retrieves real-time metrics including request counts, response times,
        error rates, costs, and provider performance statistics.
        
        Returns:
            Dict containing metrics data:
                - request_metrics: Total requests, successes, failures
                - performance_metrics: Latency percentiles, throughput
                - cost_metrics: Total costs, cost per request
                - provider_metrics: Per-provider statistics
                - cache_metrics: Hit rates, eviction stats
                - rate_limit_metrics: Throttling statistics
                
            None if metrics collection is disabled
            
        Example:
            ```python
            metrics = await bridge.get_metrics()
            
            if metrics:
                print(f"Total requests: {metrics['request_total']}")
                print(f"Average latency: {metrics['avg_response_time']:.3f}s")
                print(f"Cache hit rate: {metrics['cache_hit_rate']:.2%}")
                print(f"Total cost: ${metrics['total_cost']:.4f}")
            ```
        """
        if not self.metrics_collector:
            return None
        
        try:
            return self.metrics_collector.registry.get_all_metrics()
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return None
    
    async def get_performance_report(self) -> Optional[Dict[str, Any]]:
        """Get comprehensive performance report"""
        if not self.performance_monitor:
            return None
        
        try:
            return self.performance_monitor.get_performance_report()
        except Exception as e:
            logger.error(f"Error getting performance report: {e}")
            return None
    
    async def get_alert_stats(self) -> Optional[Dict[str, Any]]:
        """Get alert statistics"""
        if not self.alert_manager:
            return None
        
        try:
            return self.alert_manager.get_alert_stats()
        except Exception as e:
            logger.error(f"Error getting alert stats: {e}")
            return None
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        if not self.alert_manager:
            return []
        
        try:
            alerts = self.alert_manager.get_active_alerts()
            return [alert.to_dict() for alert in alerts]
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def start_monitoring(self) -> bool:
        """Start monitoring systems"""
        try:
            if self.health_checker:
                await self.health_checker.start_periodic_checks()
            
            if self.performance_monitor:
                await self.performance_monitor.start_monitoring()
            
            logger.info("Monitoring systems started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop monitoring systems"""
        try:
            if self.health_checker:
                await self.health_checker.stop_periodic_checks()
            
            if self.performance_monitor:
                await self.performance_monitor.stop_monitoring()
            
            logger.info("Monitoring systems stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown ModelBridge and cleanup resources"""
        try:
            # Stop monitoring systems
            await self.stop_monitoring()
            
            # Shutdown cache
            if self.cache:
                await self.cache.shutdown()
                logger.info("Cache shutdown complete")
            
            # Shutdown rate limiter
            if self.rate_limiter:
                await self.rate_limiter.shutdown()
                logger.info("Rate limiter shutdown complete")
            
            # Reset initialization state
            self._initialized = False
            self.providers.clear()
            
            logger.info("ModelBridge shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")