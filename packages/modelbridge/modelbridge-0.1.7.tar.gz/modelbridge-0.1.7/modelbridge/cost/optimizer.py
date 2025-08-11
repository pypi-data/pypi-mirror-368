"""
Intelligent cost optimizer with automatic model downgrading and smart routing
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Cost optimization strategies"""
    AGGRESSIVE = "aggressive"    # Maximize cost savings, may reduce quality
    BALANCED = "balanced"       # Balance cost and quality
    CONSERVATIVE = "conservative" # Minimal quality impact
    EMERGENCY = "emergency"     # Emergency cost reduction when budget exceeded


@dataclass
class OptimizationResult:
    """Result of cost optimization analysis"""
    original_model: str
    optimized_model: str
    original_cost: float
    optimized_cost: float
    cost_savings: float
    savings_percentage: float
    quality_impact: str  # "none", "minimal", "moderate", "significant"
    reasoning: str
    confidence: float  # 0.0 to 1.0


@dataclass
class ModelProfile:
    """Profile of a model's characteristics for optimization"""
    model_id: str
    provider: str
    cost_per_1k_tokens: float
    quality_score: int  # 1-100
    speed_score: int   # 1-100
    capabilities: List[str]
    best_for: List[str]  # Task types this model excels at


class CostOptimizer:
    """
    Production-grade cost optimizer that intelligently downgrades models
    while maintaining acceptable quality levels
    """
    
    def __init__(self):
        """Initialize cost optimizer with model profiles and optimization rules"""
        
        # Model profiles with quality and cost information
        self.model_profiles = {
            # OpenAI GPT-5 Family
            "gpt-5": ModelProfile(
                model_id="gpt-5",
                provider="openai",
                cost_per_1k_tokens=1.25,
                quality_score=95,
                speed_score=70,
                capabilities=["text", "coding", "reasoning", "analysis"],
                best_for=["complex_coding", "advanced_reasoning", "research"]
            ),
            "gpt-5-mini": ModelProfile(
                model_id="gpt-5-mini",
                provider="openai", 
                cost_per_1k_tokens=0.25,
                quality_score=88,
                speed_score=85,
                capabilities=["text", "coding", "reasoning"],
                best_for=["general_coding", "analysis", "conversation"]
            ),
            "gpt-5-nano": ModelProfile(
                model_id="gpt-5-nano",
                provider="openai",
                cost_per_1k_tokens=0.05,
                quality_score=75,
                speed_score=95,
                capabilities=["text", "conversation"],
                best_for=["simple_tasks", "conversation", "translation"]
            ),
            
            # Anthropic Claude 4 Family
            "claude-opus-4-1": ModelProfile(
                model_id="claude-opus-4-1",
                provider="anthropic",
                cost_per_1k_tokens=15.0,
                quality_score=97,
                speed_score=60,
                capabilities=["text", "analysis", "reasoning", "creative"],
                best_for=["complex_analysis", "research", "creative_writing"]
            ),
            "claude-sonnet-4": ModelProfile(
                model_id="claude-sonnet-4",
                provider="anthropic",
                cost_per_1k_tokens=3.0,
                quality_score=90,
                speed_score=75,
                capabilities=["text", "analysis", "coding"],
                best_for=["balanced_tasks", "coding", "analysis"]
            ),
            
            # Google Gemini Family
            "gemini-2.5-pro": ModelProfile(
                model_id="gemini-2.5-pro",
                provider="google",
                cost_per_1k_tokens=2.5,
                quality_score=92,
                speed_score=80,
                capabilities=["text", "multimodal", "analysis"],
                best_for=["multimodal_tasks", "analysis", "general"]
            ),
            "gemini-2.5-flash": ModelProfile(
                model_id="gemini-2.5-flash",
                provider="google",
                cost_per_1k_tokens=0.075,
                quality_score=82,
                speed_score=95,
                capabilities=["text", "conversation"],
                best_for=["fast_responses", "conversation", "simple_analysis"]
            ),
            "gemini-2.5-flash-lite": ModelProfile(
                model_id="gemini-2.5-flash-lite",
                provider="google",
                cost_per_1k_tokens=0.001,
                quality_score=70,
                speed_score=98,
                capabilities=["text", "conversation"],
                best_for=["ultra_cheap", "simple_tasks", "high_volume"]
            ),
            
            # Groq Family (Ultra-fast)
            "llama-3.3-70b-versatile": ModelProfile(
                model_id="llama-3.3-70b-versatile",
                provider="groq",
                cost_per_1k_tokens=0.59,
                quality_score=85,
                speed_score=98,
                capabilities=["text", "coding", "analysis"],
                best_for=["fast_coding", "quick_analysis", "conversation"]
            ),
            "mixtral-8x7b-32768": ModelProfile(
                model_id="mixtral-8x7b-32768",
                provider="groq",
                cost_per_1k_tokens=0.27,
                quality_score=80,
                speed_score=100,
                capabilities=["text", "coding"],
                best_for=["ultra_fast", "simple_coding", "conversation"]
            ),
            "llama-3.1-8b-instant": ModelProfile(
                model_id="llama-3.1-8b-instant",
                provider="groq",
                cost_per_1k_tokens=0.05,
                quality_score=72,
                speed_score=100,
                capabilities=["text", "conversation"],
                best_for=["ultra_fast", "ultra_cheap", "simple_tasks"]
            )
        }
        
        # Optimization pathways - defined downgrade paths maintaining quality
        self.optimization_pathways = {
            # Premium to balanced downgrades
            "gpt-5": ["gpt-5-mini", "claude-sonnet-4", "gemini-2.5-pro"],
            "claude-opus-4-1": ["claude-sonnet-4", "gpt-5-mini", "gemini-2.5-pro"],
            
            # Balanced to economic downgrades  
            "gpt-5-mini": ["gpt-5-nano", "gemini-2.5-flash", "llama-3.3-70b-versatile"],
            "claude-sonnet-4": ["gpt-5-mini", "gemini-2.5-flash", "llama-3.3-70b-versatile"],
            "gemini-2.5-pro": ["gemini-2.5-flash", "gpt-5-mini", "llama-3.3-70b-versatile"],
            
            # Economic to ultra-cheap downgrades
            "gpt-5-nano": ["gemini-2.5-flash-lite", "llama-3.1-8b-instant"],
            "gemini-2.5-flash": ["gemini-2.5-flash-lite", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            "llama-3.3-70b-versatile": ["mixtral-8x7b-32768", "llama-3.1-8b-instant"],
            
            # Ultra-cheap models (limited downgrade options)
            "mixtral-8x7b-32768": ["llama-3.1-8b-instant"],
            "gemini-2.5-flash-lite": ["llama-3.1-8b-instant"]
        }
        
        # Task type compatibility matrix
        self.task_compatibility = {
            "coding": {
                "high_quality": ["gpt-5", "claude-sonnet-4", "gpt-5-mini"],
                "balanced": ["llama-3.3-70b-versatile", "gemini-2.5-pro"],
                "economic": ["gpt-5-nano", "mixtral-8x7b-32768"]
            },
            "analysis": {
                "high_quality": ["claude-opus-4-1", "gpt-5", "claude-sonnet-4"],
                "balanced": ["gpt-5-mini", "gemini-2.5-pro"],
                "economic": ["gemini-2.5-flash", "llama-3.3-70b-versatile"]
            },
            "conversation": {
                "high_quality": ["gpt-5-mini", "claude-sonnet-4"],
                "balanced": ["gemini-2.5-flash", "gpt-5-nano"],
                "economic": ["llama-3.1-8b-instant", "gemini-2.5-flash-lite"]
            },
            "simple": {
                "high_quality": ["gpt-5-nano", "gemini-2.5-flash"],
                "balanced": ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                "economic": ["gemini-2.5-flash-lite"]
            },
            "creative": {
                "high_quality": ["claude-opus-4-1", "gpt-5", "claude-sonnet-4"],
                "balanced": ["gpt-5-mini", "gemini-2.5-pro"],
                "economic": ["gemini-2.5-flash"]
            }
        }
    
    def optimize_model_selection(self,
                                original_model: str,
                                task_type: str,
                                strategy: OptimizationStrategy,
                                max_cost: Optional[float] = None,
                                estimated_tokens: int = 1000,
                                available_providers: Optional[List[str]] = None) -> OptimizationResult:
        """
        Find optimal model considering cost constraints and quality requirements
        
        Args:
            original_model: The originally selected model
            task_type: Type of task (coding, analysis, conversation, etc.)
            strategy: Optimization strategy to use
            max_cost: Maximum acceptable cost for the request
            estimated_tokens: Estimated token count for cost calculation
            available_providers: List of available providers
        
        Returns:
            OptimizationResult with recommended model and analysis
        """
        
        # If original model not in profiles, return as-is
        if original_model not in self.model_profiles:
            return OptimizationResult(
                original_model=original_model,
                optimized_model=original_model,
                original_cost=0.0,
                optimized_cost=0.0,
                cost_savings=0.0,
                savings_percentage=0.0,
                quality_impact="none",
                reasoning="Model not in optimization profiles",
                confidence=0.0
            )
        
        original_profile = self.model_profiles[original_model]
        original_cost = (original_profile.cost_per_1k_tokens * estimated_tokens) / 1000
        
        # If max_cost specified and original model is within budget, no optimization needed
        if max_cost and original_cost <= max_cost:
            return OptimizationResult(
                original_model=original_model,
                optimized_model=original_model,
                original_cost=original_cost,
                optimized_cost=original_cost,
                cost_savings=0.0,
                savings_percentage=0.0,
                quality_impact="none",
                reasoning="Original model within cost budget",
                confidence=1.0
            )
        
        # Find optimization candidates
        candidates = self._get_optimization_candidates(
            original_model, 
            task_type, 
            strategy,
            available_providers
        )
        
        if not candidates:
            return OptimizationResult(
                original_model=original_model,
                optimized_model=original_model,
                original_cost=original_cost,
                optimized_cost=original_cost,
                cost_savings=0.0,
                savings_percentage=0.0,
                quality_impact="none",
                reasoning="No optimization candidates available",
                confidence=0.0
            )
        
        # Score and rank candidates
        best_candidate = self._select_best_candidate(
            candidates,
            original_profile,
            task_type,
            strategy,
            max_cost,
            estimated_tokens
        )
        
        if not best_candidate:
            return OptimizationResult(
                original_model=original_model,
                optimized_model=original_model,
                original_cost=original_cost,
                optimized_cost=original_cost,
                cost_savings=0.0,
                savings_percentage=0.0,
                quality_impact="none",
                reasoning="No suitable optimization found",
                confidence=0.0
            )
        
        # Calculate optimization metrics
        optimized_cost = (best_candidate.cost_per_1k_tokens * estimated_tokens) / 1000
        cost_savings = original_cost - optimized_cost
        savings_percentage = (cost_savings / original_cost * 100) if original_cost > 0 else 0.0
        
        # Assess quality impact
        quality_impact = self._assess_quality_impact(original_profile, best_candidate)
        
        # Generate reasoning
        reasoning = self._generate_optimization_reasoning(
            original_profile, best_candidate, strategy, task_type, cost_savings
        )
        
        # Calculate confidence (based on quality difference and task compatibility)
        confidence = self._calculate_optimization_confidence(
            original_profile, best_candidate, task_type, strategy
        )
        
        return OptimizationResult(
            original_model=original_model,
            optimized_model=best_candidate.model_id,
            original_cost=original_cost,
            optimized_cost=optimized_cost,
            cost_savings=cost_savings,
            savings_percentage=savings_percentage,
            quality_impact=quality_impact,
            reasoning=reasoning,
            confidence=confidence
        )
    
    def _get_optimization_candidates(self,
                                   original_model: str,
                                   task_type: str,
                                   strategy: OptimizationStrategy,
                                   available_providers: Optional[List[str]]) -> List[ModelProfile]:
        """Get list of potential optimization candidates"""
        
        candidates = []
        original_profile = self.model_profiles[original_model]
        
        # Start with predefined optimization pathways
        if original_model in self.optimization_pathways:
            pathway_models = self.optimization_pathways[original_model]
            for model_id in pathway_models:
                if model_id in self.model_profiles:
                    profile = self.model_profiles[model_id]
                    # Check if provider is available
                    if available_providers is None or profile.provider in available_providers:
                        candidates.append(profile)
        
        # Add task-compatible models based on strategy
        if task_type in self.task_compatibility:
            task_models = self.task_compatibility[task_type]
            
            # Choose quality tier based on strategy
            if strategy == OptimizationStrategy.AGGRESSIVE:
                tiers = ["economic", "balanced"]
            elif strategy == OptimizationStrategy.BALANCED:
                tiers = ["balanced", "high_quality", "economic"]
            elif strategy == OptimizationStrategy.CONSERVATIVE:
                tiers = ["high_quality", "balanced"]
            else:  # EMERGENCY
                tiers = ["economic"]
            
            for tier in tiers:
                if tier in task_models:
                    for model_id in task_models[tier]:
                        if (model_id in self.model_profiles and 
                            model_id != original_model):
                            profile = self.model_profiles[model_id]
                            # Check cost is lower
                            if profile.cost_per_1k_tokens < original_profile.cost_per_1k_tokens:
                                # Check provider availability
                                if available_providers is None or profile.provider in available_providers:
                                    if profile not in candidates:
                                        candidates.append(profile)
        
        return candidates
    
    def _select_best_candidate(self,
                             candidates: List[ModelProfile],
                             original_profile: ModelProfile,
                             task_type: str,
                             strategy: OptimizationStrategy,
                             max_cost: Optional[float],
                             estimated_tokens: int) -> Optional[ModelProfile]:
        """Select the best optimization candidate from the list"""
        
        if not candidates:
            return None
        
        scored_candidates = []
        
        for candidate in candidates:
            # Calculate cost
            candidate_cost = (candidate.cost_per_1k_tokens * estimated_tokens) / 1000
            
            # Skip if still over max_cost
            if max_cost and candidate_cost > max_cost:
                continue
            
            # Calculate savings
            original_cost = (original_profile.cost_per_1k_tokens * estimated_tokens) / 1000
            savings = original_cost - candidate_cost
            savings_percentage = (savings / original_cost * 100) if original_cost > 0 else 0
            
            # Skip if no savings
            if savings <= 0:
                continue
            
            # Calculate optimization score based on strategy
            score = self._calculate_optimization_score(
                candidate, original_profile, task_type, strategy, savings_percentage
            )
            
            scored_candidates.append((candidate, score, savings, candidate_cost))
        
        if not scored_candidates:
            return None
        
        # Sort by score (higher is better)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return scored_candidates[0][0]  # Return best candidate
    
    def _calculate_optimization_score(self,
                                    candidate: ModelProfile,
                                    original: ModelProfile,
                                    task_type: str,
                                    strategy: OptimizationStrategy,
                                    savings_percentage: float) -> float:
        """Calculate optimization score for ranking candidates"""
        
        score = 0.0
        
        # Cost savings component (0-40 points)
        score += min(40, savings_percentage)  # Up to 40 points for cost savings
        
        # Quality preservation component (0-30 points)
        quality_ratio = candidate.quality_score / original.quality_score
        quality_points = quality_ratio * 30
        score += quality_points
        
        # Speed component (0-15 points)  
        speed_ratio = candidate.speed_score / max(original.speed_score, 1)
        speed_points = min(15, speed_ratio * 15)
        score += speed_points
        
        # Task compatibility component (0-15 points)
        task_bonus = 0
        if task_type in self.task_compatibility:
            task_models = self.task_compatibility[task_type]
            for tier, models in task_models.items():
                if candidate.model_id in models:
                    if tier == "high_quality":
                        task_bonus = 15
                    elif tier == "balanced":
                        task_bonus = 10
                    elif tier == "economic":
                        task_bonus = 5
                    break
        score += task_bonus
        
        # Strategy-specific adjustments
        if strategy == OptimizationStrategy.AGGRESSIVE:
            # Heavily weight cost savings
            score += savings_percentage * 0.5
        elif strategy == OptimizationStrategy.CONSERVATIVE:
            # Heavily weight quality preservation  
            score += quality_points * 0.5
        elif strategy == OptimizationStrategy.EMERGENCY:
            # Maximize cost reduction
            score += savings_percentage * 1.0
        
        return score
    
    def _assess_quality_impact(self, original: ModelProfile, candidate: ModelProfile) -> str:
        """Assess the quality impact of the optimization"""
        
        quality_diff = original.quality_score - candidate.quality_score
        
        if quality_diff <= 2:
            return "none"
        elif quality_diff <= 5:
            return "minimal"
        elif quality_diff <= 15:
            return "moderate"
        else:
            return "significant"
    
    def _generate_optimization_reasoning(self,
                                       original: ModelProfile,
                                       candidate: ModelProfile,
                                       strategy: OptimizationStrategy,
                                       task_type: str,
                                       cost_savings: float) -> str:
        """Generate human-readable reasoning for the optimization"""
        
        reasons = []
        
        # Cost savings
        reasons.append(f"Saves ${cost_savings:.4f} per request")
        
        # Quality comparison
        if candidate.quality_score >= original.quality_score * 0.9:
            reasons.append("maintains similar quality")
        elif candidate.quality_score >= original.quality_score * 0.8:
            reasons.append("minimal quality reduction")
        else:
            reasons.append("moderate quality trade-off for cost savings")
        
        # Speed comparison
        if candidate.speed_score > original.speed_score:
            reasons.append("faster response time")
        
        # Task suitability
        if task_type in self.task_compatibility:
            task_models = self.task_compatibility[task_type]
            for tier, models in task_models.items():
                if candidate.model_id in models:
                    if tier == "high_quality":
                        reasons.append(f"excellent for {task_type} tasks")
                    elif tier == "balanced":
                        reasons.append(f"suitable for {task_type} tasks")
                    break
        
        # Strategy note
        if strategy == OptimizationStrategy.EMERGENCY:
            reasons.append("emergency cost reduction applied")
        elif strategy == OptimizationStrategy.AGGRESSIVE:
            reasons.append("aggressive cost optimization")
        
        return " • ".join(reasons)
    
    def _calculate_optimization_confidence(self,
                                         original: ModelProfile,
                                         candidate: ModelProfile,
                                         task_type: str,
                                         strategy: OptimizationStrategy) -> float:
        """Calculate confidence in the optimization (0.0 to 1.0)"""
        
        confidence = 0.5  # Base confidence
        
        # Quality preservation factor
        quality_ratio = candidate.quality_score / original.quality_score
        if quality_ratio >= 0.95:
            confidence += 0.3
        elif quality_ratio >= 0.85:
            confidence += 0.2
        elif quality_ratio >= 0.75:
            confidence += 0.1
        else:
            confidence -= 0.1  # Lower confidence for significant quality drop
        
        # Task compatibility factor
        if task_type in self.task_compatibility:
            task_models = self.task_compatibility[task_type]
            for tier, models in task_models.items():
                if candidate.model_id in models:
                    if tier == "high_quality":
                        confidence += 0.2
                    elif tier == "balanced":
                        confidence += 0.1
                    break
        
        # Strategy alignment factor
        if strategy == OptimizationStrategy.EMERGENCY:
            confidence += 0.1  # High confidence in emergency situations
        elif strategy == OptimizationStrategy.CONSERVATIVE and quality_ratio >= 0.9:
            confidence += 0.1  # High confidence for conservative + minimal quality loss
        
        return min(1.0, max(0.0, confidence))
    
    def get_cost_optimization_recommendations(self,
                                            current_usage: float,
                                            budget_limit: float,
                                            usage_pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive cost optimization recommendations based on usage patterns
        
        Args:
            current_usage: Current cost usage
            budget_limit: Budget limit
            usage_pattern: Dictionary with usage statistics by model/task
        
        Returns:
            Dictionary with optimization recommendations
        """
        
        recommendations = {
            "overall_status": "healthy",
            "potential_savings": 0.0,
            "urgent_actions": [],
            "model_recommendations": [],
            "general_tips": []
        }
        
        usage_percentage = (current_usage / budget_limit) * 100 if budget_limit > 0 else 0
        
        # Determine overall status
        if usage_percentage > 90:
            recommendations["overall_status"] = "critical"
            recommendations["urgent_actions"].append("Immediately switch to cheaper models")
            recommendations["urgent_actions"].append("Review all non-essential requests")
        elif usage_percentage > 75:
            recommendations["overall_status"] = "warning"
            recommendations["urgent_actions"].append("Consider cost optimization for high-usage models")
        
        # Analyze model usage patterns
        if "model_usage" in usage_pattern:
            model_usage = usage_pattern["model_usage"]
            
            for model_id, usage_stats in model_usage.items():
                if model_id not in self.model_profiles:
                    continue
                
                profile = self.model_profiles[model_id]
                usage_cost = usage_stats.get("total_cost", 0)
                request_count = usage_stats.get("requests", 0)
                
                # High-cost model recommendations
                if profile.cost_per_1k_tokens > 1.0 and usage_cost > budget_limit * 0.1:
                    # This model is expensive and uses >10% of budget
                    alternatives = self.optimization_pathways.get(model_id, [])
                    if alternatives:
                        cheapest_alt = min(
                            [self.model_profiles[alt] for alt in alternatives if alt in self.model_profiles],
                            key=lambda x: x.cost_per_1k_tokens
                        )
                        
                        potential_savings = (profile.cost_per_1k_tokens - cheapest_alt.cost_per_1k_tokens) / 1000 * usage_stats.get("total_tokens", 0)
                        
                        recommendations["model_recommendations"].append({
                            "current_model": model_id,
                            "recommended_model": cheapest_alt.model_id,
                            "potential_savings": potential_savings,
                            "quality_impact": self._assess_quality_impact(profile, cheapest_alt),
                            "reason": f"High-cost model using ${usage_cost:.2f} of budget"
                        })
                        
                        recommendations["potential_savings"] += potential_savings
        
        # General optimization tips
        recommendations["general_tips"] = [
            "Use task-specific optimization (simple tasks don't need premium models)",
            "Enable request deduplication to avoid repeat API calls",
            "Set per-request cost limits for automatic downgrading",
            "Monitor usage patterns to identify optimization opportunities",
            "Use streaming responses only when necessary (can be more expensive)"
        ]
        
        if recommendations["potential_savings"] > budget_limit * 0.1:
            recommendations["general_tips"].insert(0, 
                f"Potential to save ${recommendations['potential_savings']:.2f} with model optimization")
        
        return recommendations
    
    def suggest_emergency_actions(self, budget_exceeded_by: float) -> List[str]:
        """Suggest emergency actions when budget is exceeded"""
        
        actions = []
        
        if budget_exceeded_by > 0:
            actions.append(f"CRITICAL: Budget exceeded by ${budget_exceeded_by:.2f}")
            actions.append("Immediately switch all requests to cheapest available models")
            actions.append("Consider pausing non-essential AI requests")
            actions.append("Review recent high-cost requests for optimization opportunities")
        
        # Specific model downgrades
        actions.append("Emergency model substitutions:")
        actions.append("• gpt-5 → gpt-5-nano (96% cost reduction)")
        actions.append("• claude-opus-4-1 → gemini-2.5-flash (99.5% cost reduction)")
        actions.append("• Any model → llama-3.1-8b-instant (cheapest option)")
        
        return actions