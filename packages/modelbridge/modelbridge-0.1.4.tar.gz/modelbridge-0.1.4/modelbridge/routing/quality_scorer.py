"""
Quality Scoring System for ModelBridge
Measures and tracks response quality across providers
"""
import json
import time
import logging
import asyncio
import statistics
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from ..providers.base import GenerationResponse

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Quality metrics for a response"""
    response_id: str
    provider_name: str
    model_id: str
    timestamp: float
    
    # Content quality metrics
    coherence_score: float = 0.0
    relevance_score: float = 0.0
    completeness_score: float = 0.0
    accuracy_score: Optional[float] = None
    
    # Technical quality metrics
    response_length: int = 0
    follows_instructions: bool = True
    proper_format: bool = True
    
    # Performance metrics
    response_time: float = 0.0
    cost: float = 0.0
    
    # Aggregate scores
    overall_quality: float = 0.0
    confidence: float = 0.0
    
    # Additional metadata
    task_type: str = "general"
    complexity: str = "medium"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderQualityProfile:
    """Quality profile for a provider"""
    provider_name: str
    total_responses: int = 0
    quality_history: List[QualityMetrics] = field(default_factory=list)
    
    # Aggregated metrics
    avg_coherence: float = 0.0
    avg_relevance: float = 0.0
    avg_completeness: float = 0.0
    avg_accuracy: float = 0.0
    avg_overall_quality: float = 0.0
    
    # Performance metrics
    avg_response_time: float = 0.0
    avg_cost: float = 0.0
    success_rate: float = 0.0
    
    # Task-specific performance
    task_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Quality trends
    quality_trend: str = "stable"  # improving, declining, stable
    last_updated: float = field(default_factory=time.time)


class QualityScorer:
    """Advanced quality scoring system"""
    
    def __init__(self, max_history_per_provider: int = 1000):
        self.max_history_per_provider = max_history_per_provider
        self.provider_profiles: Dict[str, ProviderQualityProfile] = {}
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.75,
            "acceptable": 0.6,
            "poor": 0.4
        }
        
        # Quality measurement weights
        self.quality_weights = {
            "coherence": 0.25,
            "relevance": 0.25,
            "completeness": 0.20,
            "format_compliance": 0.15,
            "instruction_following": 0.15
        }
    
    async def score_response(
        self, 
        response: GenerationResponse, 
        original_request: str,
        expected_format: Optional[str] = None,
        task_type: str = "general",
        complexity: str = "medium"
    ) -> QualityMetrics:
        """Score a response and return quality metrics"""
        
        start_time = time.time()
        
        try:
            # Create quality metrics object
            metrics = QualityMetrics(
                response_id=f"{response.provider_name}_{int(time.time() * 1000)}",
                provider_name=response.provider_name,
                model_id=response.model_id or "unknown",
                timestamp=time.time(),
                task_type=task_type,
                complexity=complexity,
                response_time=getattr(response, 'response_time', 0.0),
                cost=response.cost or 0.0,
                response_length=len(response.content)
            )
            
            # Calculate individual quality scores
            metrics.coherence_score = await self._score_coherence(response.content)
            metrics.relevance_score = await self._score_relevance(response.content, original_request)
            metrics.completeness_score = await self._score_completeness(response.content, original_request)
            
            # Format and instruction compliance
            metrics.proper_format = self._check_format_compliance(response.content, expected_format)
            metrics.follows_instructions = await self._check_instruction_following(response.content, original_request)
            
            # Calculate overall quality score
            metrics.overall_quality = self._calculate_overall_quality(metrics)
            metrics.confidence = self._calculate_confidence(metrics)
            
            # Store metrics
            await self._store_quality_metrics(metrics)
            
            # Update provider profile
            await self._update_provider_profile(metrics)
            
            scoring_time = time.time() - start_time
            logger.debug(f"Quality scoring completed in {scoring_time:.3f}s for {response.provider_name}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality scoring failed: {e}")
            # Return default metrics on error
            return QualityMetrics(
                response_id=f"error_{int(time.time() * 1000)}",
                provider_name=response.provider_name,
                model_id=response.model_id or "unknown",
                timestamp=time.time(),
                overall_quality=0.5,  # Neutral score
                confidence=0.0
            )
    
    async def _score_coherence(self, content: str) -> float:
        """Score content coherence (0.0 - 1.0)"""
        if not content.strip():
            return 0.0
        
        # Simple coherence scoring based on text structure
        score = 0.5  # Base score
        
        # Check for proper sentence structure
        sentences = content.split('.')
        if len(sentences) > 1:
            score += 0.1
        
        # Check for logical flow indicators
        flow_indicators = ['therefore', 'however', 'moreover', 'furthermore', 'additionally', 'consequently']
        flow_count = sum(1 for indicator in flow_indicators if indicator in content.lower())
        if flow_count > 0:
            score += min(0.2, flow_count * 0.05)
        
        # Check for repetition (negative indicator)
        words = content.lower().split()
        if len(words) > 10:
            unique_words = len(set(words))
            repetition_ratio = unique_words / len(words)
            if repetition_ratio < 0.5:
                score -= 0.2
        
        # Check for reasonable length
        if 50 <= len(content) <= 5000:
            score += 0.1
        elif len(content) < 10:
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    async def _score_relevance(self, content: str, original_request: str) -> float:
        """Score content relevance to original request (0.0 - 1.0)"""
        if not content.strip() or not original_request.strip():
            return 0.0
        
        # Simple keyword overlap scoring
        request_words = set(original_request.lower().split())
        content_words = set(content.lower().split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        request_words -= stop_words
        content_words -= stop_words
        
        if not request_words:
            return 0.5  # Neutral if no meaningful words in request
        
        # Calculate overlap
        overlap = len(request_words.intersection(content_words))
        relevance_score = overlap / len(request_words)
        
        # Boost score if content directly addresses the request
        if any(phrase in content.lower() for phrase in ['your question', 'you asked', 'as requested']):
            relevance_score += 0.1
        
        return max(0.0, min(1.0, relevance_score))
    
    async def _score_completeness(self, content: str, original_request: str) -> float:
        """Score response completeness (0.0 - 1.0)"""
        if not content.strip():
            return 0.0
        
        score = 0.5  # Base score
        
        # Check if response seems complete (not cut off)
        if content.endswith('.') or content.endswith('!') or content.endswith('?'):
            score += 0.1
        elif content.endswith('...') or len(content) > 1000 and not content.rstrip()[-1].isalnum():
            score -= 0.2  # Might be cut off
        
        # Check for appropriate length relative to request complexity
        request_length = len(original_request)
        content_length = len(content)
        
        if request_length < 100:  # Simple request
            if 50 <= content_length <= 1000:
                score += 0.2
        elif request_length < 500:  # Medium request
            if 100 <= content_length <= 2000:
                score += 0.2
        else:  # Complex request
            if 200 <= content_length <= 4000:
                score += 0.2
        
        # Check for structure (lists, examples, explanations)
        if any(indicator in content for indicator in ['1.', '2.', '•', '-', 'example:', 'for instance']):
            score += 0.1
        
        # Check for conclusion or summary
        if any(phrase in content.lower() for phrase in ['in conclusion', 'to summarize', 'overall', 'in summary']):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _check_format_compliance(self, content: str, expected_format: Optional[str]) -> bool:
        """Check if response follows expected format"""
        if not expected_format:
            return True
        
        format_type = expected_format.lower()
        
        if format_type == "json":
            try:
                json.loads(content.strip())
                return True
            except json.JSONDecodeError:
                return False
        
        elif format_type == "list":
            return bool(any(indicator in content for indicator in ['1.', '2.', '•', '-', '\n-']))
        
        elif format_type == "markdown":
            return bool(any(indicator in content for indicator in ['#', '**', '*', '`', '```']))
        
        elif format_type == "code":
            return bool(any(indicator in content for indicator in ['def ', 'function', 'class ', '```', 'import']))
        
        return True  # Default to compliant if format not recognized
    
    async def _check_instruction_following(self, content: str, original_request: str) -> bool:
        """Check if response follows specific instructions in request"""
        request_lower = original_request.lower()
        content_lower = content.lower()
        
        # Check for specific instruction patterns
        instruction_patterns = [
            ('list', ['1.', '2.', '•', '-']),
            ('explain', ['because', 'due to', 'reason', 'explanation']),
            ('compare', ['versus', 'vs', 'compared to', 'difference', 'similar']),
            ('summarize', ['summary', 'in short', 'briefly', 'main points']),
            ('example', ['example', 'for instance', 'such as'])
        ]
        
        for instruction, indicators in instruction_patterns:
            if instruction in request_lower:
                if not any(indicator in content_lower for indicator in indicators):
                    return False
        
        # Check for length restrictions
        if 'brief' in request_lower or 'short' in request_lower:
            if len(content) > 1000:  # Too long for brief response
                return False
        
        if 'detailed' in request_lower or 'comprehensive' in request_lower:
            if len(content) < 200:  # Too short for detailed response
                return False
        
        return True
    
    def _calculate_overall_quality(self, metrics: QualityMetrics) -> float:
        """Calculate overall quality score from individual metrics"""
        scores = {
            "coherence": metrics.coherence_score,
            "relevance": metrics.relevance_score,
            "completeness": metrics.completeness_score,
            "format_compliance": 1.0 if metrics.proper_format else 0.0,
            "instruction_following": 1.0 if metrics.follows_instructions else 0.0
        }
        
        weighted_score = sum(
            scores[metric] * weight 
            for metric, weight in self.quality_weights.items()
        )
        
        return max(0.0, min(1.0, weighted_score))
    
    def _calculate_confidence(self, metrics: QualityMetrics) -> float:
        """Calculate confidence in quality assessment"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence for longer responses (more data)
        if metrics.response_length > 100:
            confidence += 0.1
        if metrics.response_length > 500:
            confidence += 0.1
        
        # Lower confidence for very short responses
        if metrics.response_length < 50:
            confidence -= 0.3
        
        # Adjust based on consistency of scores
        individual_scores = [
            metrics.coherence_score,
            metrics.relevance_score,
            metrics.completeness_score
        ]
        
        if len(individual_scores) > 1:
            score_variance = statistics.variance(individual_scores)
            if score_variance < 0.1:  # Consistent scores
                confidence += 0.1
            elif score_variance > 0.3:  # Inconsistent scores
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    async def _store_quality_metrics(self, metrics: QualityMetrics):
        """Store quality metrics (override in subclass for persistence)"""
        # In-memory storage for now
        # Could be extended to store in database or file system
        pass
    
    async def _update_provider_profile(self, metrics: QualityMetrics):
        """Update provider quality profile with new metrics"""
        provider_name = metrics.provider_name
        
        if provider_name not in self.provider_profiles:
            self.provider_profiles[provider_name] = ProviderQualityProfile(
                provider_name=provider_name
            )
        
        profile = self.provider_profiles[provider_name]
        
        # Add to history
        profile.quality_history.append(metrics)
        profile.total_responses += 1
        
        # Limit history size
        if len(profile.quality_history) > self.max_history_per_provider:
            profile.quality_history = profile.quality_history[-self.max_history_per_provider:]
        
        # Update aggregated metrics
        recent_history = profile.quality_history[-100:]  # Last 100 responses
        
        profile.avg_coherence = statistics.mean([m.coherence_score for m in recent_history])
        profile.avg_relevance = statistics.mean([m.relevance_score for m in recent_history])
        profile.avg_completeness = statistics.mean([m.completeness_score for m in recent_history])
        profile.avg_overall_quality = statistics.mean([m.overall_quality for m in recent_history])
        
        # Performance metrics
        profile.avg_response_time = statistics.mean([m.response_time for m in recent_history])
        profile.avg_cost = statistics.mean([m.cost for m in recent_history])
        
        # Task-specific performance
        task_type = metrics.task_type
        if task_type not in profile.task_performance:
            profile.task_performance[task_type] = {}
        
        task_metrics = [m for m in recent_history if m.task_type == task_type]
        if task_metrics:
            profile.task_performance[task_type] = {
                "avg_quality": statistics.mean([m.overall_quality for m in task_metrics]),
                "avg_response_time": statistics.mean([m.response_time for m in task_metrics]),
                "sample_count": len(task_metrics)
            }
        
        # Calculate quality trend
        if len(profile.quality_history) >= 20:
            recent_scores = [m.overall_quality for m in profile.quality_history[-10:]]
            older_scores = [m.overall_quality for m in profile.quality_history[-20:-10]]
            
            recent_avg = statistics.mean(recent_scores)
            older_avg = statistics.mean(older_scores)
            
            if recent_avg > older_avg + 0.05:
                profile.quality_trend = "improving"
            elif recent_avg < older_avg - 0.05:
                profile.quality_trend = "declining"
            else:
                profile.quality_trend = "stable"
        
        profile.last_updated = time.time()
    
    def get_provider_quality_summary(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get quality summary for provider(s)"""
        if provider_name:
            if provider_name not in self.provider_profiles:
                return {"error": f"No quality data for provider {provider_name}"}
            
            profile = self.provider_profiles[provider_name]
            return {
                "provider_name": provider_name,
                "total_responses": profile.total_responses,
                "avg_overall_quality": profile.avg_overall_quality,
                "avg_coherence": profile.avg_coherence,
                "avg_relevance": profile.avg_relevance,
                "avg_completeness": profile.avg_completeness,
                "avg_response_time": profile.avg_response_time,
                "avg_cost": profile.avg_cost,
                "quality_trend": profile.quality_trend,
                "task_performance": profile.task_performance
            }
        else:
            # Return summary for all providers
            return {
                provider_name: {
                    "total_responses": profile.total_responses,
                    "avg_overall_quality": profile.avg_overall_quality,
                    "quality_trend": profile.quality_trend,
                    "last_updated": profile.last_updated
                }
                for provider_name, profile in self.provider_profiles.items()
            }
    
    def get_quality_recommendations(self, task_type: str = "general") -> List[Tuple[str, float, str]]:
        """Get provider recommendations based on quality scores"""
        recommendations = []
        
        for provider_name, profile in self.provider_profiles.items():
            if profile.total_responses < 5:  # Skip providers with insufficient data
                continue
            
            # Get task-specific quality if available
            if task_type in profile.task_performance:
                quality_score = profile.task_performance[task_type]["avg_quality"]
                reason = f"Task-specific quality for {task_type}"
            else:
                quality_score = profile.avg_overall_quality
                reason = "Overall quality score"
            
            # Apply trend adjustment
            if profile.quality_trend == "improving":
                quality_score += 0.05
                reason += " (improving trend)"
            elif profile.quality_trend == "declining":
                quality_score -= 0.05
                reason += " (declining trend)"
            
            recommendations.append((provider_name, quality_score, reason))
        
        # Sort by quality score (descending)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations