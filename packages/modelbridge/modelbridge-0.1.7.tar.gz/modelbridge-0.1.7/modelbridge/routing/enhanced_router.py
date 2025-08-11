"""
Enhanced Routing Algorithm for ModelBridge
Rule-based intelligent routing with performance optimization
"""
import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from ..providers.base import GenerationRequest, BaseModelProvider

logger = logging.getLogger(__name__)


@dataclass
class RoutingContext:
    """Context information for routing decisions"""
    request: GenerationRequest
    available_providers: Dict[str, BaseModelProvider]
    urgency: str = "normal"  # low, normal, high, critical
    cost_sensitivity: str = "medium"  # low, medium, high
    quality_requirement: str = "medium"  # low, medium, high, critical
    task_type: str = "general"  # general, code, creative, analysis, translation
    max_retries: int = 3
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ProviderScore:
    """Provider scoring information"""
    provider_name: str
    score: float
    reasons: List[str]
    estimated_cost: float
    estimated_latency: float
    confidence: float


class RoutingStrategy(Protocol):
    """Protocol for routing strategies"""
    
    async def score_provider(
        self, 
        provider_name: str, 
        provider: BaseModelProvider, 
        context: RoutingContext
    ) -> ProviderScore:
        """Score a provider for the given context"""
        ...
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        ...


class EnhancedRouter:
    """Enhanced rule-based router with multiple strategies"""
    
    def __init__(self):
        self.performance_history: Dict[str, Dict[str, Any]] = {}
        self.provider_health: Dict[str, Dict[str, Any]] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.routing_strategies: List[RoutingStrategy] = []
        self.default_weights = {
            "performance": 0.3,
            "cost": 0.25, 
            "latency": 0.25,
            "reliability": 0.2
        }
        
        # Load default strategies
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize default routing strategies"""
        from .routing_strategies import (
            QualityBasedRouting,
            CostBasedRouting,
            LatencyBasedRouting,
            ReliabilityBasedRouting
        )
        
        self.routing_strategies = [
            QualityBasedRouting(),
            CostBasedRouting(), 
            LatencyBasedRouting(),
            ReliabilityBasedRouting()
        ]
    
    async def route_request(self, context: RoutingContext) -> List[Tuple[str, ProviderScore]]:
        """Route request using enhanced algorithms"""
        start_time = time.time()
        
        try:
            # Analyze request characteristics
            characteristics = await self._analyze_request(context.request)
            context.metadata.update(characteristics)
            
            # Get provider scores from all strategies
            provider_scores = await self._score_providers(context)
            
            # Apply circuit breaker filtering
            available_scores = self._filter_circuit_breakers(provider_scores)
            
            # Combine scores using weighted approach
            final_rankings = await self._combine_strategy_scores(available_scores, context)
            
            # Log routing decision
            routing_time = time.time() - start_time
            logger.info(f"Routing completed in {routing_time:.3f}s, top choice: {final_rankings[0][0] if final_rankings else 'none'}")
            
            return final_rankings
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            # Fallback to simple round-robin
            return await self._fallback_routing(context)
    
    async def _analyze_request(self, request: GenerationRequest) -> Dict[str, Any]:
        """Analyze request characteristics for routing"""
        characteristics = {}
        
        # Analyze prompt complexity
        prompt_length = len(request.prompt)
        characteristics["prompt_length"] = prompt_length
        
        if prompt_length < 100:
            characteristics["complexity"] = "simple"
        elif prompt_length < 500:
            characteristics["complexity"] = "medium" 
        elif prompt_length < 2000:
            characteristics["complexity"] = "complex"
        else:
            characteristics["complexity"] = "very_complex"
        
        # Detect task type from prompt patterns
        prompt_lower = request.prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ['code', 'function', 'class', 'programming', 'debug']):
            characteristics["task_type"] = "code"
        elif any(keyword in prompt_lower for keyword in ['creative', 'story', 'poem', 'creative writing']):
            characteristics["task_type"] = "creative"
        elif any(keyword in prompt_lower for keyword in ['analyze', 'analysis', 'summarize', 'explain']):
            characteristics["task_type"] = "analysis"
        elif any(keyword in prompt_lower for keyword in ['translate', 'translation']):
            characteristics["task_type"] = "translation"
        else:
            characteristics["task_type"] = "general"
        
        # Detect structured output requirement
        characteristics["structured_output"] = bool(getattr(request, 'output_schema', None))
        
        # Estimate token usage
        estimated_input_tokens = prompt_length // 4  # Rough estimate
        characteristics["estimated_input_tokens"] = estimated_input_tokens
        
        max_tokens = getattr(request, 'max_tokens', None) or 1000
        characteristics["estimated_output_tokens"] = max_tokens
        characteristics["estimated_total_tokens"] = estimated_input_tokens + max_tokens
        
        return characteristics
    
    async def _score_providers(self, context: RoutingContext) -> Dict[str, List[ProviderScore]]:
        """Score providers using all strategies"""
        strategy_scores = {}
        
        for strategy in self.routing_strategies:
            strategy_name = strategy.get_strategy_name()
            strategy_scores[strategy_name] = []
            
            for provider_name, provider in context.available_providers.items():
                try:
                    score = await strategy.score_provider(provider_name, provider, context)
                    strategy_scores[strategy_name].append(score)
                except Exception as e:
                    logger.warning(f"Strategy {strategy_name} failed for provider {provider_name}: {e}")
                    # Create default score
                    strategy_scores[strategy_name].append(
                        ProviderScore(
                            provider_name=provider_name,
                            score=0.0,
                            reasons=[f"Strategy failed: {e}"],
                            estimated_cost=0.01,
                            estimated_latency=5.0,
                            confidence=0.0
                        )
                    )
        
        return strategy_scores
    
    def _filter_circuit_breakers(self, strategy_scores: Dict[str, List[ProviderScore]]) -> Dict[str, List[ProviderScore]]:
        """Filter out providers that are circuit broken"""
        filtered_scores = {}
        
        for strategy_name, scores in strategy_scores.items():
            filtered_scores[strategy_name] = []
            
            for score in scores:
                if self._is_provider_available(score.provider_name):
                    filtered_scores[strategy_name].append(score)
                else:
                    logger.warning(f"Provider {score.provider_name} filtered out due to circuit breaker")
        
        return filtered_scores
    
    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if provider is available (not circuit broken)"""
        if provider_name not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[provider_name]
        if breaker.get("state") != "open":
            return True
        
        # Check if circuit breaker should be reset
        last_failure = breaker.get("last_failure", 0)
        reset_timeout = breaker.get("reset_timeout", 300)  # 5 minutes default
        
        if time.time() - last_failure > reset_timeout:
            breaker["state"] = "half_open"
            logger.info(f"Circuit breaker for {provider_name} moved to half-open state")
            return True
        
        return False
    
    async def _combine_strategy_scores(
        self, 
        strategy_scores: Dict[str, List[ProviderScore]], 
        context: RoutingContext
    ) -> List[Tuple[str, ProviderScore]]:
        """Combine scores from multiple strategies"""
        
        # Get all unique providers
        all_providers = set()
        for scores in strategy_scores.values():
            for score in scores:
                all_providers.add(score.provider_name)
        
        # Calculate combined scores
        combined_scores = {}
        
        for provider_name in all_providers:
            total_score = 0.0
            total_weight = 0.0
            reasons = []
            estimated_cost = 0.0
            estimated_latency = 0.0
            confidence_sum = 0.0
            strategy_count = 0
            
            for strategy_name, scores in strategy_scores.items():
                provider_score = next((s for s in scores if s.provider_name == provider_name), None)
                if provider_score:
                    weight = self._get_strategy_weight(strategy_name, context)
                    total_score += provider_score.score * weight
                    total_weight += weight
                    reasons.extend(provider_score.reasons)
                    estimated_cost += provider_score.estimated_cost
                    estimated_latency += provider_score.estimated_latency
                    confidence_sum += provider_score.confidence
                    strategy_count += 1
            
            if total_weight > 0:
                final_score = total_score / total_weight
                avg_cost = estimated_cost / strategy_count if strategy_count > 0 else 0.01
                avg_latency = estimated_latency / strategy_count if strategy_count > 0 else 5.0
                avg_confidence = confidence_sum / strategy_count if strategy_count > 0 else 0.5
                
                combined_scores[provider_name] = ProviderScore(
                    provider_name=provider_name,
                    score=final_score,
                    reasons=reasons,
                    estimated_cost=avg_cost,
                    estimated_latency=avg_latency,
                    confidence=avg_confidence
                )
        
        # Sort by score (descending)
        ranked_providers = [(name, score) for name, score in combined_scores.items()]
        ranked_providers.sort(key=lambda x: x[1].score, reverse=True)
        
        return ranked_providers
    
    def _get_strategy_weight(self, strategy_name: str, context: RoutingContext) -> float:
        """Get weight for strategy based on context"""
        base_weights = {
            "quality": self.default_weights["performance"],
            "cost": self.default_weights["cost"],
            "latency": self.default_weights["latency"],
            "reliability": self.default_weights["reliability"]
        }
        
        # Adjust weights based on context
        if context.cost_sensitivity == "high":
            base_weights["cost"] *= 1.5
            base_weights["performance"] *= 0.8
        elif context.cost_sensitivity == "low":
            base_weights["cost"] *= 0.5
            base_weights["performance"] *= 1.2
        
        if context.urgency in ["high", "critical"]:
            base_weights["latency"] *= 1.5
            base_weights["cost"] *= 0.7
        
        if context.quality_requirement in ["high", "critical"]:
            base_weights["performance"] *= 1.5
            base_weights["cost"] *= 0.8
        
        return base_weights.get(strategy_name.lower().split('_')[0], 1.0)
    
    async def _fallback_routing(self, context: RoutingContext) -> List[Tuple[str, ProviderScore]]:
        """Fallback routing when main routing fails"""
        logger.warning("Using fallback routing")
        
        fallback_scores = []
        for provider_name in context.available_providers.keys():
            if self._is_provider_available(provider_name):
                score = ProviderScore(
                    provider_name=provider_name,
                    score=50.0,
                    reasons=["Fallback routing"],
                    estimated_cost=0.01,
                    estimated_latency=5.0,
                    confidence=0.5
                )
                fallback_scores.append((provider_name, score))
        
        return fallback_scores
    
    async def update_performance_metrics(
        self, 
        provider_name: str, 
        response_time: float, 
        cost: float, 
        success: bool,
        quality_score: Optional[float] = None
    ):
        """Update performance metrics for a provider"""
        current_time = time.time()
        
        if provider_name not in self.performance_history:
            self.performance_history[provider_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_response_time": 0,
                "total_cost": 0,
                "quality_scores": [],
                "last_updated": current_time,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "avg_cost": 0.0,
                "avg_quality": 0.0
            }
        
        history = self.performance_history[provider_name]
        history["total_requests"] += 1
        history["total_response_time"] += response_time
        history["total_cost"] += cost
        history["last_updated"] = current_time
        
        if success:
            history["successful_requests"] += 1
            if quality_score is not None:
                history["quality_scores"].append(quality_score)
                # Keep only last 100 quality scores
                history["quality_scores"] = history["quality_scores"][-100:]
        else:
            history["failed_requests"] += 1
            await self._update_circuit_breaker(provider_name, False)
        
        # Update averages
        history["success_rate"] = history["successful_requests"] / history["total_requests"]
        history["avg_response_time"] = history["total_response_time"] / history["total_requests"]
        history["avg_cost"] = history["total_cost"] / history["total_requests"]
        
        if history["quality_scores"]:
            history["avg_quality"] = sum(history["quality_scores"]) / len(history["quality_scores"])
        
        # Update circuit breaker on success
        if success:
            await self._update_circuit_breaker(provider_name, True)
    
    async def _update_circuit_breaker(self, provider_name: str, success: bool):
        """Update circuit breaker state"""
        if provider_name not in self.circuit_breakers:
            self.circuit_breakers[provider_name] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": 0,
                "reset_timeout": 300,
                "failure_threshold": 5
            }
        
        breaker = self.circuit_breakers[provider_name]
        
        if success:
            if breaker["state"] == "half_open":
                breaker["state"] = "closed"
                breaker["failure_count"] = 0
                logger.info(f"Circuit breaker for {provider_name} closed")
        else:
            breaker["failure_count"] += 1
            breaker["last_failure"] = time.time()
            
            if breaker["failure_count"] >= breaker["failure_threshold"]:
                breaker["state"] = "open"
                logger.warning(f"Circuit breaker for {provider_name} opened after {breaker['failure_count']} failures")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all providers"""
        return {
            "performance_history": self.performance_history.copy(),
            "circuit_breaker_states": {
                name: breaker["state"] 
                for name, breaker in self.circuit_breakers.items()
            },
            "total_providers": len(self.performance_history),
            "healthy_providers": sum(
                1 for breaker in self.circuit_breakers.values() 
                if breaker["state"] != "open"
            )
        }