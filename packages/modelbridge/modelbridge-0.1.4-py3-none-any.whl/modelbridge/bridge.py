"""
ModelBridge - Enhanced Unified Model Bridge
Central service that manages ALL model providers and routes requests intelligently
"""
import asyncio
import json
import yaml
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import time
import logging
import uuid
from datetime import datetime

from .providers.base import (
    BaseModelProvider, 
    GenerationRequest, 
    GenerationResponse, 
    ModelMetadata, 
    ModelCapability
)

# Import caching system
from .cache import CacheFactory, CacheInterface
from .cache.decorators import CacheManager

# Import all providers
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.groq import GroqProvider

# Import smart routing
from .analyzer import TaskAnalyzer

# Import cost management
from .cost import CostManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Simple configuration manager"""
    def __init__(self):
        self.available_providers = []
        self.providers = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load API keys from environment variables"""
        provider_configs = {
            "openai": {"key": "OPENAI_API_KEY", "priority": 1},
            "anthropic": {"key": "ANTHROPIC_API_KEY", "priority": 2},
            "google": {"key": "GOOGLE_API_KEY", "priority": 3},
            "groq": {"key": "GROQ_API_KEY", "priority": 4},
        }
        
        for provider, config in provider_configs.items():
            api_key = os.getenv(config["key"])
            if api_key:
                self.available_providers.append(provider)
                self.providers[provider] = type('Provider', (), {
                    'api_key': api_key,
                    'priority': config["priority"]
                })


class IntelligentRouter:
    """Enhanced intelligent router for smart provider selection"""
    
    def __init__(self):
        self.performance_history = {}
        self.provider_health_cache = {}
        self.last_health_check = None
        
    def analyze_request_characteristics(self, request: GenerationRequest) -> Dict[str, Any]:
        """Analyze request to determine optimal routing strategy"""
        characteristics = {
            "complexity": "medium",
            "urgency": "normal",
            "cost_sensitivity": "medium",
            "quality_requirement": "medium",
            "task_type": getattr(request, 'task_type', None) or "general"
        }
        
        # Analyze prompt length and complexity
        prompt_length = len(request.prompt)
        if prompt_length < 100:
            characteristics["complexity"] = "simple"
        elif prompt_length > 1000:
            characteristics["complexity"] = "complex"
        
        return characteristics
    
    def get_provider_ranking(self, characteristics: Dict[str, Any], available_providers: Dict[str, BaseModelProvider]) -> List[Tuple[str, float]]:
        """Rank providers based on request characteristics and performance history"""
        rankings = []
        
        for provider_name, provider in available_providers.items():
            score = self._calculate_provider_score(provider_name, characteristics)
            rankings.append((provider_name, score))
        
        # Sort by score (higher is better)
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings
    
    def _calculate_provider_score(self, provider_name: str, characteristics: Dict[str, Any]) -> float:
        """Calculate provider score based on characteristics and performance"""
        score = 50.0  # Base score
        
        # Performance-based scoring
        if provider_name in self.performance_history:
            perf = self.performance_history[provider_name]
            success_rate = perf.get("success_rate", 0.5)
            avg_response_time = perf.get("avg_response_time", 5.0)
            avg_cost = perf.get("avg_cost", 0.01)
            
            # Success rate bonus (0-20 points)
            score += success_rate * 20
            
            # Response time bonus (0-15 points)
            if avg_response_time < 2.0:
                score += 15
            elif avg_response_time < 5.0:
                score += 10
            elif avg_response_time < 10.0:
                score += 5
            
            # Cost optimization (0-15 points)
            if characteristics["cost_sensitivity"] == "high":
                if avg_cost < 0.001:
                    score += 15
                elif avg_cost < 0.01:
                    score += 10
                elif avg_cost < 0.05:
                    score += 5
        
        # Provider-specific bonuses
        if characteristics["urgency"] == "high":
            if provider_name in ["groq", "openai"]:
                score += 10
        elif characteristics["quality_requirement"] == "high":
            if provider_name in ["anthropic", "openai"]:
                score += 15
        
        # Health check penalty
        if provider_name in self.provider_health_cache:
            health = self.provider_health_cache[provider_name]
            if health.get("status") != "healthy":
                score -= 50
        
        return max(0.0, score)
    
    async def update_performance_history(self, provider_name: str, response_time: float, cost: float, success: bool):
        """Update performance history for a provider"""
        if provider_name not in self.performance_history:
            self.performance_history[provider_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0,
                "total_cost": 0,
                "avg_response_time": 0,
                "avg_cost": 0,
                "success_rate": 0,
            }
        
        perf = self.performance_history[provider_name]
        perf["total_requests"] += 1
        perf["total_response_time"] += response_time
        perf["total_cost"] += cost
        
        if success:
            perf["successful_requests"] += 1
        
        # Update averages
        perf["avg_response_time"] = perf["total_response_time"] / perf["total_requests"]
        perf["avg_cost"] = perf["total_cost"] / perf["total_requests"]
        perf["success_rate"] = perf["successful_requests"] / perf["total_requests"]


class ModelAlias:
    """Configuration for model aliases"""
    def __init__(self, alias: str, provider: str, model_id: str, priority: int = 0):
        self.alias = alias
        self.provider = provider
        self.model_id = model_id
        self.priority = priority


class ModelBridge:
    """Enhanced central gateway for ALL LLM providers with intelligent routing"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.providers: Dict[str, BaseModelProvider] = {}
        self.model_aliases: Dict[str, List[ModelAlias]] = {}
        self._initialized = False
        self._fallback_enabled = True
        self._performance_tracking = True
        
        # Enhanced intelligent routing
        self.intelligent_router = IntelligentRouter()
        
        # Smart task analyzer
        self.task_analyzer = TaskAnalyzer()
        
        # Production-grade cost management
        self.cost_manager = CostManager(
            enable_tracking=True,
            enable_budgets=True,
            enable_optimization=True
        )
        
        # Performance tracking
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        
        # Initialize configuration
        self.config = Config()
        
        # Provider classes
        self.provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
            "groq": GroqProvider,
        }
        
        logger.info(f"Available providers: {list(self.config.available_providers)}")
        
        # Setup default aliases
        self._setup_default_aliases()
    
    def _setup_default_aliases(self):
        """Setup default model aliases - Updated August 2025 🚀
        
        REVOLUTIONARY UPDATE: Based on latest 2025 models
        - GPT-5 family: 40x cheaper than old routing!
        - Groq Mixtral: 500+ tokens/sec (25x faster!)
        - Claude 4.1: 74.5% SWE-bench performance
        - Gemini 2.5: 1M+ context, ultra-cheap options
        """
        self.model_aliases = {
            "fastest": [
                # 🚀 WORLD'S FASTEST: Groq Mixtral at ultra-fast inference
                ModelAlias("fastest", "groq", "mixtral-8x7b-32768", 1),
                # Latest Llama 3.3 with fast inference
                ModelAlias("fastest", "groq", "llama-3.3-70b-versatile", 2), 
                # GPT-5 Nano: Ultra-fast, cheapest OpenAI option
                ModelAlias("fastest", "openai", "gpt-5-nano", 3),
                # Groq's fastest small model
                ModelAlias("fastest", "groq", "llama-3.1-8b-instant", 4),
            ],
            "cheapest": [
                # 💰 ULTRA-CHEAP: GPT-5 Nano at $0.05/0.40 per 1M tokens
                ModelAlias("cheapest", "openai", "gpt-5-nano", 1),
                # Groq's cheapest option
                ModelAlias("cheapest", "groq", "llama-3.1-8b-instant", 2),
                # Google's cheapest option
                ModelAlias("cheapest", "google", "gemini-1.5-flash-8b", 3),
                # Groq Llama 3.2 small model
                ModelAlias("cheapest", "groq", "llama-3.2-3b-preview", 4),
            ],
            "best": [
                # 🏆 TOP QUALITY: GPT-5 - Best for coding & agents, beats o3
                ModelAlias("best", "openai", "gpt-5", 1),
                # Claude Opus 4.1: Most capable Anthropic model
                ModelAlias("best", "anthropic", "claude-opus-4-1", 2),
                # GPT-4.1: Better instruction following
                ModelAlias("best", "openai", "gpt-4.1", 3),
                # Claude 3.5 Sonnet: Great coding performance
                ModelAlias("best", "anthropic", "claude-3-5-sonnet", 4),
            ],
            "balanced": [
                # ⚖️ PERFECT BALANCE: GPT-5 Mini - great performance at reasonable cost
                ModelAlias("balanced", "openai", "gpt-5-mini", 1),
                # Claude 3.5 Sonnet: Sweet spot for most users
                ModelAlias("balanced", "anthropic", "claude-3-5-sonnet", 2),
                # Groq Llama 3.3: Fast inference with good performance
                ModelAlias("balanced", "groq", "llama-3.3-70b-versatile", 3),
                # GPT-4.1 Mini: Affordable with good performance
                ModelAlias("balanced", "openai", "gpt-4.1-mini", 4),
            ],
        }
    
    async def initialize(self, force_reload: bool = False) -> bool:
        """Initialize the gateway and all providers"""
        if self._initialized and not force_reload:
            return True
        
        try:
            # Initialize only providers with valid API keys
            available_providers = self.config.available_providers
            
            if not available_providers:
                logger.warning("No providers with valid API keys found. Please set at least one API key.")
                return False
            
            for provider_name in available_providers:
                if provider_name not in self.provider_classes:
                    continue
                
                provider_config = {
                    "api_key": self.config.providers[provider_name].api_key,
                    "enabled": True,
                    "priority": self.config.providers[provider_name].priority,
                }
                
                success = await self._initialize_provider(provider_name, provider_config)
                if not success:
                    logger.warning(f"Failed to initialize {provider_name}")
            
            if self.providers:
                self._initialized = True
                logger.info(f"ModelBridge initialized with {len(self.providers)} providers")
                return True
            else:
                logger.error("No providers initialized successfully")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize ModelBridge: {str(e)}")
            return False
    
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
                logger.info(f"Provider {provider_name} initialized successfully")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error initializing provider {provider_name}: {str(e)}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        optimize_for: Optional[str] = None,
        max_cost: Optional[float] = None,
        **kwargs
    ) -> GenerationResponse:
        """Generate text with intelligent routing
        
        Args:
            prompt: The text prompt to generate from
            model: Optional specific model (if None, uses smart routing)
            system_message: Optional system message
            temperature: Optional temperature (0.0 to 1.0)
            max_tokens: Optional maximum tokens to generate
            optimize_for: Optional optimization - "speed", "cost", "quality"
            max_cost: Optional maximum cost per request in USD
            **kwargs: Additional parameters
        """
        
        # Smart routing if no model specified
        if model is None:
            analysis = self.task_analyzer.analyze(
                prompt=prompt,
                optimize_for=optimize_for,
                max_cost=max_cost,
                available_providers=list(self.providers.keys())
            )
            model = analysis.recommended_model
            
            # Cost-aware optimization
            if self.cost_manager:
                # Estimate token count for cost calculation
                estimated_tokens = len(prompt.split()) * 1.3  # Rough estimate
                
                # Check if we should optimize for cost
                if self.cost_manager.should_optimize_request(
                    estimated_cost=estimated_tokens * 0.001,  # Rough cost estimate
                    model=model,
                    task_type=analysis.task_type
                ):
                    # Get cost-optimized model recommendation
                    optimization = self.cost_manager.optimize_model_choice(
                        original_model=model,
                        task_type=analysis.task_type,
                        estimated_tokens=int(estimated_tokens),
                        max_cost=max_cost,
                        available_providers=list(self.providers.keys())
                    )
                    
                    # Use optimized model if confidence is high enough
                    if optimization.confidence > 0.7:
                        model = optimization.optimized_model
                        kwargs['_cost_optimization'] = {
                            'original_model': optimization.original_model,
                            'cost_savings': optimization.cost_savings,
                            'reasoning': optimization.reasoning
                        }
            
            # Store analysis metadata separately (don't pass to API)
            analysis_metadata = {
                'task_type': analysis.task_type,
                'complexity_score': analysis.complexity_score,
                'reasoning': analysis.reasoning,
                'confidence': analysis.confidence
            }
        
        # Fallback to balanced if model still not resolved
        if model is None:
            model = "balanced"
        
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
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        optimize_for: Optional[str] = None,
        max_cost: Optional[float] = None,
        **kwargs
    ) -> GenerationResponse:
        """Generate structured JSON output with intelligent routing
        
        Args:
            prompt: The text prompt
            schema: JSON schema for structured output
            model: Optional specific model (if None, uses smart routing)
            system_message: Optional system message
            temperature: Optional temperature (0.0 to 1.0)
            optimize_for: Optional optimization - "speed", "cost", "quality"
            max_cost: Optional maximum cost per request in USD
            **kwargs: Additional parameters
        """
        
        # Smart routing if no model specified
        if model is None:
            # For structured output, prefer quality unless specified otherwise
            analysis = self.task_analyzer.analyze(
                prompt=f"{prompt} [STRUCTURED_OUTPUT_TASK]",
                optimize_for=optimize_for or "quality",
                max_cost=max_cost,
                available_providers=list(self.providers.keys())
            )
            model = analysis.recommended_model
            
            # Cost-aware optimization (more conservative for structured output)
            if self.cost_manager:
                estimated_tokens = len(prompt.split()) * 1.5  # Structured output uses more tokens
                
                if self.cost_manager.should_optimize_request(
                    estimated_cost=estimated_tokens * 0.001,
                    model=model,
                    task_type="structured_output"
                ):
                    optimization = self.cost_manager.optimize_model_choice(
                        original_model=model,
                        task_type="structured_output",
                        estimated_tokens=int(estimated_tokens),
                        max_cost=max_cost,
                        strategy="conservative",  # More conservative for structured output
                        available_providers=list(self.providers.keys())
                    )
                    
                    # Higher confidence threshold for structured output
                    if optimization.confidence > 0.8:
                        model = optimization.optimized_model
                        kwargs['_cost_optimization'] = {
                            'original_model': optimization.original_model,
                            'cost_savings': optimization.cost_savings,
                            'reasoning': optimization.reasoning
                        }
            
            # Store analysis metadata separately (don't pass to API)
            analysis_metadata = {
                'task_type': analysis.task_type,
                'complexity_score': analysis.complexity_score,
                'reasoning': analysis.reasoning,
                'confidence': analysis.confidence
            }
        
        # Fallback to balanced if model still not resolved
        if model is None:
            model = "balanced"
        
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
        """Route request through providers with intelligent routing and fallback"""
        
        # Analyze request characteristics
        characteristics = self.intelligent_router.analyze_request_characteristics(request)
        
        # Get provider rankings
        provider_rankings = self.intelligent_router.get_provider_ranking(characteristics, self.providers)
        
        # Resolve model specification
        model_options = self._resolve_model_spec(model_spec)
        
        # Try each model option
        last_error = None
        
        for alias in model_options:
            provider = self.providers.get(alias.provider)
            if not provider:
                continue
            
            try:
                # Check capability support
                if hasattr(request, 'output_schema') and request.output_schema:
                    if not provider.supports_capability(alias.model_id, ModelCapability.STRUCTURED_OUTPUT):
                        continue
                
                # Track performance
                start_time = time.time()
                
                # Check budget before making request
                estimated_cost = 0.001  # Default estimate
                if self.cost_manager and hasattr(request, 'extra_params'):
                    extra_params = request.extra_params or {}
                    if '_estimated_cost' in extra_params:
                        estimated_cost = extra_params['_estimated_cost']
                
                # Pre-request budget check
                budget_check = None
                if self.cost_manager:
                    budget_check = self.cost_manager.check_request_budget(estimated_cost)
                    if budget_check['status'] == 'blocked':
                        return GenerationResponse(
                            content="",
                            model_id=alias.model_id,
                            provider_name=alias.provider,
                            error=f"Request blocked by budget constraints: {budget_check['violations'][0]['message']}"
                        )
                
                # Make request
                method = getattr(provider, method_name)
                response = await method(request, alias.model_id)
                
                # Calculate actual costs and metrics
                response_time = time.time() - start_time
                actual_cost = response.cost or estimated_cost
                
                # Track request cost with comprehensive details
                if self.cost_manager and not response.error:
                    request_id = f"{alias.provider}_{alias.model_id}_{int(time.time())}_{hash(request.prompt) % 10000}"
                    
                    # Extract token counts if available
                    prompt_tokens = getattr(response, 'prompt_tokens', 0)
                    completion_tokens = getattr(response, 'completion_tokens', 0)
                    
                    # If no token info, estimate from response
                    if prompt_tokens == 0 and completion_tokens == 0:
                        prompt_tokens = len(request.prompt.split()) * 1.3
                        completion_tokens = len(response.content.split()) * 1.3
                    
                    # Determine task type
                    task_type = "general"
                    if hasattr(request, 'extra_params') and request.extra_params:
                        analysis = request.extra_params.get('_smart_routing_analysis', {})
                        task_type = analysis.get('task_type', 'general')
                    
                    # Check if optimization was applied
                    optimization_info = None
                    cost_saved = 0.0
                    original_model = None
                    
                    if hasattr(request, 'extra_params') and request.extra_params:
                        cost_opt = request.extra_params.get('_cost_optimization', {})
                        if cost_opt:
                            original_model = cost_opt.get('original_model')
                            cost_saved = cost_opt.get('cost_savings', 0.0)
                            optimization_info = cost_opt.get('reasoning')
                    
                    # Track the request
                    self.cost_manager.track_request(
                        request_id=request_id,
                        provider=alias.provider,
                        model=alias.model_id,
                        prompt_tokens=int(prompt_tokens),
                        completion_tokens=int(completion_tokens),
                        total_cost=actual_cost,
                        task_type=task_type,
                        optimization_applied=optimization_info,
                        original_model=original_model,
                        cost_saved=cost_saved
                    )
                
                # Update performance stats
                if self._performance_tracking:
                    self._update_performance_stats(
                        alias.provider, 
                        alias.model_id, 
                        response_time,
                        actual_cost,
                        not response.error
                    )
                
                # Update router history
                await self.intelligent_router.update_performance_history(
                    alias.provider, 
                    response_time, 
                    actual_cost, 
                    not response.error
                )
                
                # Return successful response
                if not response.error:
                    return response
                
                last_error = response.error
                
                # If fallback is disabled, return first response
                if not self._fallback_enabled:
                    return response
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error with provider {alias.provider}: {str(e)}")
                continue
        
        # All providers failed
        return GenerationResponse(
            content="",
            model_id=model_spec,
            provider_name="gateway",
            error=f"All providers failed. Last error: {last_error}"
        )
    
    def _resolve_model_spec(self, model_spec: str) -> List[ModelAlias]:
        """Resolve model specification to list of provider/model pairs"""
        
        # Check if it's an alias
        if model_spec in self.model_aliases:
            # Filter to only available providers
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
        
        # Fallback to balanced alias (avoid infinite recursion)
        if model_spec != "balanced" and "balanced" in self.model_aliases:
            return self._resolve_model_spec("balanced")
        
        # Ultimate fallback - return empty list if no providers available
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
        """Get performance statistics for all models"""
        return self.performance_stats.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
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
        }
    
    def get_routing_recommendations(self) -> Dict[str, Any]:
        """Get routing recommendations"""
        return {
            "performance_history": self.intelligent_router.performance_history,
            "provider_health": self.intelligent_router.provider_health_cache,
        }
    
    # === Cost Management API ===
    
    def set_monthly_budget(self, amount: float, name: str = "default_monthly") -> bool:
        """Set monthly spending budget"""
        if self.cost_manager:
            return self.cost_manager.set_monthly_budget(amount, name)
        return False
    
    def set_daily_budget(self, amount: float, name: str = "default_daily") -> bool:
        """Set daily spending budget"""
        if self.cost_manager:
            return self.cost_manager.set_daily_budget(amount, name)
        return False
    
    def set_request_budget(self, amount: float, name: str = "default_request") -> bool:
        """Set per-request spending budget"""
        if self.cost_manager:
            return self.cost_manager.set_request_budget(amount, name)
        return False
    
    def get_cost_usage_stats(self, time_period: str = "month") -> Dict:
        """Get comprehensive cost usage statistics"""
        if self.cost_manager:
            return self.cost_manager.get_usage_stats(time_period)
        return {"error": "Cost management not enabled"}
    
    def get_cost_report(self, time_period: str = "month") -> Dict:
        """Get detailed cost analysis report"""
        if self.cost_manager:
            return self.cost_manager.get_cost_report(time_period)
        return {"error": "Cost management not enabled"}
    
    def get_budget_status(self) -> List[Dict]:
        """Get status of all budgets"""
        if self.cost_manager:
            return self.cost_manager.get_budget_status()
        return []
    
    def enable_cost_optimization(self, strategy: str = "balanced"):
        """Enable automatic cost optimization"""
        if self.cost_manager:
            from .cost.optimizer import OptimizationStrategy
            strategy_map = {
                "aggressive": OptimizationStrategy.AGGRESSIVE,
                "balanced": OptimizationStrategy.BALANCED,
                "conservative": OptimizationStrategy.CONSERVATIVE
            }
            self.cost_manager.enable_auto_optimization(strategy_map.get(strategy, OptimizationStrategy.BALANCED))
    
    def disable_cost_optimization(self):
        """Disable automatic cost optimization"""
        if self.cost_manager:
            self.cost_manager.disable_auto_optimization()
    
    def enable_emergency_mode(self):
        """Enable emergency cost reduction mode"""
        if self.cost_manager:
            self.cost_manager.enable_emergency_mode()
            logger.warning("EMERGENCY COST MODE ENABLED - All requests will use cheapest models")
    
    def get_optimization_recommendations(self) -> Dict:
        """Get cost optimization recommendations"""
        if self.cost_manager:
            return self.cost_manager.get_optimization_recommendations()
        return {"recommendations": ["Cost management not enabled"]}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including cost management"""
        
        # Get base status
        base_status = {
            "providers": list(self.providers.keys()),
            "total_providers": len(self.providers),
            "intelligent_routing": {
                "enabled": True,
                "performance_tracking": self._performance_tracking,
                "fallback_enabled": self._fallback_enabled
            }
        }
        
        # Add cost management status
        if self.cost_manager:
            cost_status = self.cost_manager.get_system_status()
            base_status["cost_management"] = cost_status
        
        return base_status