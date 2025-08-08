"""
Routing Strategies for ModelBridge
Various strategies for intelligent provider selection
"""
import time
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from ..providers.base import GenerationRequest, BaseModelProvider, ModelCapability
from .enhanced_router import RoutingContext, ProviderScore

logger = logging.getLogger(__name__)


class RoutingStrategy(ABC):
    """Base class for routing strategies"""
    
    @abstractmethod
    async def score_provider(
        self, 
        provider_name: str, 
        provider: BaseModelProvider, 
        context: RoutingContext
    ) -> ProviderScore:
        """Score a provider for the given context"""
        pass
    
    @abstractmethod 
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        pass


class QualityBasedRouting(RoutingStrategy):
    """Quality-based routing strategy"""
    
    def __init__(self):
        self.quality_profiles = {
            "openai": {"gpt-4": 95, "gpt-4-turbo": 93, "gpt-3.5-turbo": 80},
            "anthropic": {"claude-3-opus": 97, "claude-3-sonnet": 90, "claude-3-haiku": 85},
            "google": {"gemini-1.5-pro": 88, "gemini-1.5-flash": 82},
            "groq": {"mixtral-8x7b": 75, "llama3-8b": 70}
        }
        
        self.task_type_bonuses = {
            "code": {"openai": 10, "anthropic": 8, "google": 6, "groq": 4},
            "creative": {"anthropic": 10, "openai": 8, "google": 6, "groq": 5},
            "analysis": {"anthropic": 10, "openai": 9, "google": 7, "groq": 5},
            "translation": {"google": 10, "openai": 8, "anthropic": 7, "groq": 4},
            "general": {"anthropic": 8, "openai": 8, "google": 6, "groq": 5}
        }
    
    async def score_provider(
        self, 
        provider_name: str, 
        provider: BaseModelProvider, 
        context: RoutingContext
    ) -> ProviderScore:
        
        base_score = 50.0
        reasons = []
        confidence = 0.8
        
        # Get quality profiles for provider
        provider_models = self.quality_profiles.get(provider_name, {})
        if not provider_models:
            base_score = 40.0
            reasons.append(f"No quality profile for {provider_name}")
            confidence = 0.3
        else:
            # Use average quality score for provider
            avg_quality = sum(provider_models.values()) / len(provider_models)
            base_score = avg_quality
            reasons.append(f"Base quality score: {avg_quality}")
        
        # Task type bonus
        task_type = context.metadata.get("task_type", "general")
        task_bonus = self.task_type_bonuses.get(task_type, {}).get(provider_name, 0)
        base_score += task_bonus
        if task_bonus > 0:
            reasons.append(f"Task type '{task_type}' bonus: +{task_bonus}")
        
        # Quality requirement adjustment
        if context.quality_requirement == "critical":
            if provider_name in ["anthropic", "openai"]:
                base_score += 15
                reasons.append("Critical quality requirement bonus: +15")
            else:
                base_score -= 10
                reasons.append("Critical quality requirement penalty: -10")
        elif context.quality_requirement == "high":
            if provider_name in ["anthropic", "openai"]:
                base_score += 8
                reasons.append("High quality requirement bonus: +8")
        
        # Complexity handling
        complexity = context.metadata.get("complexity", "medium")
        if complexity in ["complex", "very_complex"]:
            if provider_name in ["anthropic", "openai"]:
                base_score += 10
                reasons.append(f"Complex task bonus: +10")
        
        # Structured output capability check
        if context.metadata.get("structured_output", False):
            try:
                # Check if provider supports structured output
                if hasattr(provider, 'supports_capability'):
                    supports_structured = provider.supports_capability("", ModelCapability.STRUCTURED_OUTPUT)
                    if supports_structured:
                        base_score += 5
                        reasons.append("Structured output support: +5")
                    else:
                        base_score -= 20
                        reasons.append("No structured output support: -20")
                        confidence *= 0.5
            except Exception as e:
                logger.warning(f"Could not check structured output capability for {provider_name}: {e}")
        
        # Estimate cost and latency (simplified)
        estimated_tokens = context.metadata.get("estimated_total_tokens", 1000)
        cost_per_token = self._get_cost_per_token(provider_name)
        estimated_cost = estimated_tokens * cost_per_token / 1000  # Convert to cost per 1K tokens
        
        latency_profile = self._get_latency_profile(provider_name)
        estimated_latency = latency_profile.get("base_latency", 3.0)
        
        return ProviderScore(
            provider_name=provider_name,
            score=max(0.0, base_score),
            reasons=reasons,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            confidence=confidence
        )
    
    def _get_cost_per_token(self, provider_name: str) -> float:
        """Get estimated cost per token for provider"""
        cost_profiles = {
            "openai": 0.03,  # GPT-4 rate
            "anthropic": 0.015,  # Claude rate
            "google": 0.0075,  # Gemini rate  
            "groq": 0.0008   # Very cheap/free tier
        }
        return cost_profiles.get(provider_name, 0.01)
    
    def _get_latency_profile(self, provider_name: str) -> Dict[str, float]:
        """Get latency profile for provider"""
        profiles = {
            "openai": {"base_latency": 2.5},
            "anthropic": {"base_latency": 3.0},
            "google": {"base_latency": 2.0},
            "groq": {"base_latency": 0.8}  # Very fast
        }
        return profiles.get(provider_name, {"base_latency": 3.0})
    
    def get_strategy_name(self) -> str:
        return "quality_based"


class CostBasedRouting(RoutingStrategy):
    """Cost-based routing strategy"""
    
    def __init__(self):
        self.cost_profiles = {
            "groq": 0.0008,     # Cheapest
            "google": 0.0075,   # Good value
            "anthropic": 0.015, # Mid-range
            "openai": 0.03      # Most expensive
        }
    
    async def score_provider(
        self, 
        provider_name: str, 
        provider: BaseModelProvider, 
        context: RoutingContext
    ) -> ProviderScore:
        
        base_score = 50.0
        reasons = []
        confidence = 0.9
        
        # Get cost profile
        cost_per_1k_tokens = self.cost_profiles.get(provider_name, 0.01)
        estimated_tokens = context.metadata.get("estimated_total_tokens", 1000)
        estimated_cost = (estimated_tokens * cost_per_1k_tokens) / 1000
        
        # Score based on cost (lower cost = higher score)
        max_cost = max(self.cost_profiles.values())
        cost_score = ((max_cost - cost_per_1k_tokens) / max_cost) * 60  # 0-60 points
        base_score += cost_score
        reasons.append(f"Cost efficiency score: +{cost_score:.1f}")
        
        # Cost sensitivity adjustment
        if context.cost_sensitivity == "high":
            if cost_per_1k_tokens < 0.002:
                base_score += 20
                reasons.append("High cost sensitivity + very cheap provider: +20")
            elif cost_per_1k_tokens < 0.01:
                base_score += 10
                reasons.append("High cost sensitivity + cheap provider: +10")
            else:
                base_score -= 15
                reasons.append("High cost sensitivity + expensive provider: -15")
        
        elif context.cost_sensitivity == "low":
            # When cost doesn't matter, slightly favor quality providers
            if provider_name in ["openai", "anthropic"]:
                base_score += 5
                reasons.append("Low cost sensitivity + premium provider: +5")
        
        # Large request penalty for expensive providers
        if estimated_tokens > 10000:
            if cost_per_1k_tokens > 0.02:
                penalty = (estimated_tokens / 1000) * 0.5
                base_score -= penalty
                reasons.append(f"Large request + expensive provider penalty: -{penalty:.1f}")
        
        # Estimate latency
        estimated_latency = self._estimate_latency_by_cost(cost_per_1k_tokens)
        
        return ProviderScore(
            provider_name=provider_name,
            score=max(0.0, base_score),
            reasons=reasons,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            confidence=confidence
        )
    
    def _estimate_latency_by_cost(self, cost_per_1k_tokens: float) -> float:
        """Estimate latency based on cost (rough correlation)"""
        # Generally: cheaper = faster (due to simpler models or better infrastructure)
        if cost_per_1k_tokens < 0.001:
            return 1.0  # Very fast
        elif cost_per_1k_tokens < 0.01:
            return 2.5  # Fast
        elif cost_per_1k_tokens < 0.02:
            return 3.5  # Medium
        else:
            return 4.0  # Slower (complex models)
    
    def get_strategy_name(self) -> str:
        return "cost_based"


class LatencyBasedRouting(RoutingStrategy):
    """Latency-based routing strategy"""
    
    def __init__(self):
        self.latency_profiles = {
            "groq": 0.8,      # Very fast (optimized inference)
            "google": 2.0,    # Fast
            "openai": 2.5,    # Medium
            "anthropic": 3.0  # Slightly slower
        }
    
    async def score_provider(
        self, 
        provider_name: str, 
        provider: BaseModelProvider, 
        context: RoutingContext
    ) -> ProviderScore:
        
        base_score = 50.0
        reasons = []
        confidence = 0.85
        
        # Get latency profile
        base_latency = self.latency_profiles.get(provider_name, 3.0)
        
        # Adjust for request size
        estimated_tokens = context.metadata.get("estimated_total_tokens", 1000)
        token_latency_factor = max(1.0, estimated_tokens / 5000)  # Longer requests take more time
        estimated_latency = base_latency * token_latency_factor
        
        # Score based on latency (lower latency = higher score)
        max_latency = max(self.latency_profiles.values()) * 2  # Account for scaling
        latency_score = ((max_latency - estimated_latency) / max_latency) * 70  # 0-70 points
        base_score += latency_score
        reasons.append(f"Latency score: +{latency_score:.1f}")
        
        # Urgency adjustment
        if context.urgency == "critical":
            if base_latency < 1.5:
                base_score += 25
                reasons.append("Critical urgency + very fast provider: +25")
            elif base_latency < 3.0:
                base_score += 10
                reasons.append("Critical urgency + fast provider: +10")
            else:
                base_score -= 20
                reasons.append("Critical urgency + slow provider: -20")
        
        elif context.urgency == "high":
            if base_latency < 2.0:
                base_score += 15
                reasons.append("High urgency + fast provider: +15")
            elif base_latency > 4.0:
                base_score -= 10
                reasons.append("High urgency + slow provider: -10")
        
        # Complexity adjustment (complex requests may be slower)
        complexity = context.metadata.get("complexity", "medium")
        if complexity in ["complex", "very_complex"]:
            estimated_latency *= 1.5
            base_score -= 5
            reasons.append("Complex request latency adjustment: -5")
        
        # Estimate cost
        estimated_cost = self._estimate_cost_by_latency(base_latency, estimated_tokens)
        
        return ProviderScore(
            provider_name=provider_name,
            score=max(0.0, base_score),
            reasons=reasons,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            confidence=confidence
        )
    
    def _estimate_cost_by_latency(self, latency: float, tokens: int) -> float:
        """Estimate cost based on latency (rough correlation)"""
        # Fast providers are often cheaper (or free)
        if latency < 1.5:
            cost_per_1k = 0.0008
        elif latency < 2.5:
            cost_per_1k = 0.0075
        elif latency < 3.5:
            cost_per_1k = 0.015
        else:
            cost_per_1k = 0.025
        
        return (tokens * cost_per_1k) / 1000
    
    def get_strategy_name(self) -> str:
        return "latency_based"


class ReliabilityBasedRouting(RoutingStrategy):
    """Reliability-based routing strategy"""
    
    def __init__(self):
        self.reliability_profiles = {
            "openai": 0.98,    # Very reliable
            "anthropic": 0.97, # Very reliable
            "google": 0.95,    # Reliable
            "groq": 0.90       # Good (newer service)
        }
    
    async def score_provider(
        self, 
        provider_name: str, 
        provider: BaseModelProvider, 
        context: RoutingContext
    ) -> ProviderScore:
        
        base_score = 50.0
        reasons = []
        confidence = 0.7  # Historical data might not predict future
        
        # Base reliability score
        reliability = self.reliability_profiles.get(provider_name, 0.85)
        reliability_score = reliability * 60  # 0-60 points
        base_score += reliability_score
        reasons.append(f"Reliability score: +{reliability_score:.1f}")
        
        # Check if we have actual performance history
        # This would be populated by the router's performance tracking
        performance_history = getattr(context, 'performance_history', {})
        if provider_name in performance_history:
            history = performance_history[provider_name]
            actual_success_rate = history.get("success_rate", reliability)
            
            if actual_success_rate > reliability:
                bonus = (actual_success_rate - reliability) * 30
                base_score += bonus
                reasons.append(f"Better than expected performance: +{bonus:.1f}")
                confidence = 0.9
            elif actual_success_rate < reliability - 0.05:  # Significantly worse
                penalty = (reliability - actual_success_rate) * 50
                base_score -= penalty
                reasons.append(f"Worse than expected performance: -{penalty:.1f}")
                confidence = 0.95
        
        # Critical task adjustment
        if context.quality_requirement == "critical":
            if reliability > 0.96:
                base_score += 15
                reasons.append("Critical task + highly reliable provider: +15")
            elif reliability < 0.90:
                base_score -= 25
                reasons.append("Critical task + less reliable provider: -25")
        
        # Large request reliability consideration
        estimated_tokens = context.metadata.get("estimated_total_tokens", 1000)
        if estimated_tokens > 20000:  # Very large requests
            if reliability < 0.95:
                base_score -= 10
                reasons.append("Large request + lower reliability penalty: -10")
        
        # Estimate cost and latency (generic)
        estimated_cost = 0.01 * (estimated_tokens / 1000)
        estimated_latency = 3.0
        
        return ProviderScore(
            provider_name=provider_name,
            score=max(0.0, base_score),
            reasons=reasons,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            confidence=confidence
        )
    
    def get_strategy_name(self) -> str:
        return "reliability_based"