"""
Request Processing Middlewares for ModelBridge
Middlewares that process incoming requests
"""
import re
import json
import time
import logging
from typing import Dict, Any, List, Optional, Set
from abc import abstractmethod

from .base import Middleware, MiddlewareContext, MiddlewarePhase
from ..providers.base import GenerationRequest

logger = logging.getLogger(__name__)


class RequestMiddleware(Middleware):
    """Base class for request processing middlewares"""
    
    def supports_phase(self, phase: MiddlewarePhase) -> bool:
        """Request middlewares typically run in early phases"""
        return phase in [
            MiddlewarePhase.PRE_REQUEST,
            MiddlewarePhase.POST_VALIDATION,
            MiddlewarePhase.PRE_ROUTING
        ]


class ValidationMiddleware(RequestMiddleware):
    """Validates incoming requests"""
    
    def __init__(
        self,
        max_prompt_length: int = 50000,
        max_tokens: int = 8192,
        allowed_models: Optional[Set[str]] = None,
        required_fields: Optional[List[str]] = None,
        priority: int = 10  # High priority - validate early
    ):
        super().__init__("validation", priority=priority)
        self.max_prompt_length = max_prompt_length
        self.max_tokens = max_tokens
        self.allowed_models = allowed_models or set()
        self.required_fields = required_fields or []
        
        # Statistics
        self.validation_errors = 0
        self.prompts_truncated = 0
    
    def supports_phase(self, phase: MiddlewarePhase) -> bool:
        """Validation runs in PRE_REQUEST and POST_VALIDATION phases"""
        return phase in [MiddlewarePhase.PRE_REQUEST, MiddlewarePhase.POST_VALIDATION]
    
    async def process(
        self, 
        context: MiddlewareContext, 
        phase: MiddlewarePhase
    ) -> MiddlewareContext:
        """Validate request"""
        
        if phase == MiddlewarePhase.PRE_REQUEST:
            return await self._validate_basic(context)
        elif phase == MiddlewarePhase.POST_VALIDATION:
            return await self._validate_advanced(context)
        
        return context
    
    async def _validate_basic(self, context: MiddlewareContext) -> MiddlewareContext:
        """Basic validation checks"""
        request = context.request
        
        # Check required fields
        for field in self.required_fields:
            if not hasattr(request, field) or getattr(request, field) is None:
                self.validation_errors += 1
                raise ValueError(f"Required field missing: {field}")
        
        # Validate prompt
        if not request.prompt or not request.prompt.strip():
            self.validation_errors += 1
            raise ValueError("Prompt cannot be empty")
        
        # Check prompt length
        if len(request.prompt) > self.max_prompt_length:
            logger.warning(f"Prompt too long ({len(request.prompt)} chars), truncating")
            request.prompt = request.prompt[:self.max_prompt_length]
            self.prompts_truncated += 1
            context.set_metadata("prompt_truncated", True)
        
        # Validate max_tokens
        if hasattr(request, 'max_tokens') and request.max_tokens:
            if request.max_tokens > self.max_tokens:
                logger.warning(f"max_tokens too high ({request.max_tokens}), capping at {self.max_tokens}")
                request.max_tokens = self.max_tokens
        
        # Validate temperature
        if hasattr(request, 'temperature') and request.temperature is not None:
            if not 0.0 <= request.temperature <= 2.0:
                self.validation_errors += 1
                raise ValueError("Temperature must be between 0.0 and 2.0")
        
        context.add_performance_metric("validation_basic_completed", True)
        return context
    
    async def _validate_advanced(self, context: MiddlewareContext) -> MiddlewareContext:
        """Advanced validation after routing"""
        request = context.request
        
        # Validate model selection if allowed models are specified
        if self.allowed_models and context.selected_provider:
            model_spec = f"{context.selected_provider}:{getattr(request, 'model', 'default')}"
            if model_spec not in self.allowed_models:
                logger.warning(f"Model {model_spec} not in allowed list")
                context.set_metadata("model_validation_warning", True)
        
        # Check for potentially harmful content (basic check)
        if await self._contains_harmful_content(request.prompt):
            self.validation_errors += 1
            raise ValueError("Request contains potentially harmful content")
        
        context.add_performance_metric("validation_advanced_completed", True)
        return context
    
    async def _contains_harmful_content(self, prompt: str) -> bool:
        """Basic harmful content detection"""
        # This is a simple implementation - in production you'd use more sophisticated methods
        harmful_patterns = [
            r'\b(hack|exploit|vulnerability|malware)\b',
            r'\b(bomb|weapon|violence)\b',
            r'\b(illegal|criminal|fraud)\b'
        ]
        
        prompt_lower = prompt.lower()
        for pattern in harmful_patterns:
            if re.search(pattern, prompt_lower):
                logger.warning(f"Potentially harmful content detected: {pattern}")
                return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "validation_errors": self.validation_errors,
            "prompts_truncated": self.prompts_truncated,
            "max_prompt_length": self.max_prompt_length,
            "max_tokens": self.max_tokens
        })
        return base_stats


class AuthenticationMiddleware(RequestMiddleware):
    """Handles request authentication and authorization"""
    
    def __init__(
        self,
        api_keys: Optional[Set[str]] = None,
        require_authentication: bool = False,
        rate_limit_per_key: Optional[Dict[str, int]] = None,
        priority: int = 5  # Very high priority
    ):
        super().__init__("authentication", priority=priority)
        self.api_keys = api_keys or set()
        self.require_authentication = require_authentication
        self.rate_limit_per_key = rate_limit_per_key or {}
        
        # Track usage per key
        self.key_usage: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.auth_failures = 0
        self.auth_successes = 0
        self.rate_limit_violations = 0
    
    def supports_phase(self, phase: MiddlewarePhase) -> bool:
        """Authentication runs in PRE_REQUEST phase"""
        return phase == MiddlewarePhase.PRE_REQUEST
    
    async def process(
        self, 
        context: MiddlewareContext, 
        phase: MiddlewarePhase
    ) -> MiddlewareContext:
        """Process authentication"""
        
        if phase != MiddlewarePhase.PRE_REQUEST:
            return context
        
        # Extract authentication info from context
        auth_header = context.get_metadata("authorization_header")
        api_key = context.get_metadata("api_key")
        
        # Try to extract API key from different sources
        if not api_key and auth_header:
            if auth_header.startswith("Bearer "):
                api_key = auth_header[7:]
            elif auth_header.startswith("ApiKey "):
                api_key = auth_header[7:]
        
        # Check if authentication is required
        if self.require_authentication and not api_key:
            self.auth_failures += 1
            raise ValueError("Authentication required but no API key provided")
        
        # Validate API key if provided
        if api_key:
            if self.api_keys and api_key not in self.api_keys:
                self.auth_failures += 1
                raise ValueError("Invalid API key")
            
            # Check rate limiting
            if await self._check_rate_limit(api_key):
                self.rate_limit_violations += 1
                raise ValueError("Rate limit exceeded for API key")
            
            # Store authentication info
            context.authentication = {
                "api_key": api_key,
                "authenticated": True,
                "timestamp": time.time()
            }
            
            # Update usage tracking
            await self._update_key_usage(api_key)
            
            self.auth_successes += 1
        else:
            context.authentication = {
                "authenticated": False,
                "timestamp": time.time()
            }
        
        return context
    
    async def _check_rate_limit(self, api_key: str) -> bool:
        """Check if API key has exceeded rate limit"""
        if api_key not in self.rate_limit_per_key:
            return False
        
        current_time = time.time()
        rate_limit = self.rate_limit_per_key[api_key]
        
        # Initialize usage tracking if not exists
        if api_key not in self.key_usage:
            self.key_usage[api_key] = {
                "requests": [],
                "total_requests": 0
            }
        
        usage = self.key_usage[api_key]
        
        # Remove requests older than 1 hour
        usage["requests"] = [
            timestamp for timestamp in usage["requests"] 
            if current_time - timestamp < 3600
        ]
        
        # Check if rate limit exceeded
        return len(usage["requests"]) >= rate_limit
    
    async def _update_key_usage(self, api_key: str):
        """Update usage statistics for API key"""
        current_time = time.time()
        
        if api_key not in self.key_usage:
            self.key_usage[api_key] = {
                "requests": [],
                "total_requests": 0,
                "first_request": current_time,
                "last_request": current_time
            }
        
        usage = self.key_usage[api_key]
        usage["requests"].append(current_time)
        usage["total_requests"] += 1
        usage["last_request"] = current_time
    
    def get_key_stats(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get usage statistics for a specific API key"""
        if api_key not in self.key_usage:
            return None
        
        usage = self.key_usage[api_key]
        current_time = time.time()
        
        # Count recent requests (last hour)
        recent_requests = [
            timestamp for timestamp in usage["requests"]
            if current_time - timestamp < 3600
        ]
        
        return {
            "total_requests": usage["total_requests"],
            "recent_requests": len(recent_requests),
            "first_request": usage.get("first_request"),
            "last_request": usage.get("last_request"),
            "rate_limit": self.rate_limit_per_key.get(api_key),
            "rate_limit_remaining": max(0, self.rate_limit_per_key.get(api_key, 0) - len(recent_requests))
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "auth_failures": self.auth_failures,
            "auth_successes": self.auth_successes,
            "rate_limit_violations": self.rate_limit_violations,
            "tracked_keys": len(self.key_usage),
            "require_authentication": self.require_authentication
        })
        return base_stats


class RequestEnrichmentMiddleware(RequestMiddleware):
    """Enriches requests with additional metadata"""
    
    def __init__(self, priority: int = 20):
        super().__init__("request_enrichment", priority=priority)
        self.enrichments_applied = 0
    
    def supports_phase(self, phase: MiddlewarePhase) -> bool:
        """Enrichment runs after validation"""
        return phase in [MiddlewarePhase.POST_VALIDATION, MiddlewarePhase.PRE_ROUTING]
    
    async def process(
        self, 
        context: MiddlewareContext, 
        phase: MiddlewarePhase
    ) -> MiddlewareContext:
        """Enrich request with metadata"""
        
        if phase == MiddlewarePhase.POST_VALIDATION:
            await self._enrich_with_analysis(context)
        elif phase == MiddlewarePhase.PRE_ROUTING:
            await self._enrich_with_routing_hints(context)
        
        return context
    
    async def _enrich_with_analysis(self, context: MiddlewareContext):
        """Enrich with request analysis"""
        request = context.request
        
        # Analyze prompt characteristics
        prompt_analysis = {
            "word_count": len(request.prompt.split()),
            "character_count": len(request.prompt),
            "has_code": self._contains_code(request.prompt),
            "has_math": self._contains_math(request.prompt),
            "estimated_complexity": self._estimate_complexity(request.prompt),
            "language": self._detect_language(request.prompt),
            "sentiment": self._analyze_sentiment(request.prompt)
        }
        
        context.set_metadata("prompt_analysis", prompt_analysis)
        self.enrichments_applied += 1
    
    async def _enrich_with_routing_hints(self, context: MiddlewareContext):
        """Add routing hints based on analysis"""
        analysis = context.get_metadata("prompt_analysis", {})
        
        routing_hints = {}
        
        # Code-related requests
        if analysis.get("has_code", False):
            routing_hints["preferred_providers"] = ["openai", "anthropic"]
            routing_hints["task_type"] = "code"
        
        # Math-related requests
        if analysis.get("has_math", False):
            routing_hints["preferred_providers"] = ["openai", "anthropic"]
            routing_hints["task_type"] = "math"
        
        # Complex requests
        complexity = analysis.get("estimated_complexity", "medium")
        if complexity in ["high", "very_high"]:
            routing_hints["quality_requirement"] = "high"
            routing_hints["preferred_providers"] = ["anthropic", "openai"]
        
        # Simple requests - can use faster/cheaper providers
        if complexity == "low":
            routing_hints["cost_sensitivity"] = "high"
            routing_hints["preferred_providers"] = ["groq", "google"]
        
        context.set_metadata("routing_hints", routing_hints)
        self.enrichments_applied += 1
    
    def _contains_code(self, text: str) -> bool:
        """Check if text contains code"""
        code_patterns = [
            r'```',  # Code blocks
            r'def\s+\w+\s*\(',  # Python functions
            r'function\s+\w+\s*\(',  # JavaScript functions
            r'class\s+\w+\s*\{',  # Class definitions
            r'import\s+\w+',  # Import statements
            r'#include\s*<',  # C/C++ includes
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _contains_math(self, text: str) -> bool:
        """Check if text contains mathematical content"""
        math_patterns = [
            r'\$[^$]+\$',  # LaTeX math
            r'\\[a-zA-Z]+\{',  # LaTeX commands
            r'\b(equation|formula|theorem|proof)\b',
            r'[∑∏∫∮∂∇≤≥±×÷]',  # Math symbols
            r'\b(sin|cos|tan|log|exp|sqrt)\s*\(',  # Math functions
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _estimate_complexity(self, text: str) -> str:
        """Estimate prompt complexity"""
        word_count = len(text.split())
        
        if word_count < 20:
            return "low"
        elif word_count < 100:
            return "medium"
        elif word_count < 500:
            return "high"
        else:
            return "very_high"
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # This is a very basic implementation
        # In production, you might use a proper language detection library
        
        # Check for common non-English patterns
        if re.search(r'[¿¡ñáéíóúü]', text.lower()):
            return "spanish"
        elif re.search(r'[àâäéèêëïîôöùûüç]', text.lower()):
            return "french"
        elif re.search(r'[äöüß]', text.lower()):
            return "german"
        else:
            return "english"
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        # This is a very simple implementation
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'frustrating']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enrichment statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "enrichments_applied": self.enrichments_applied
        })
        return base_stats