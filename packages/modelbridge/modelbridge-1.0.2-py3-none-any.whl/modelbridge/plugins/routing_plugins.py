"""
Routing Plugins for ModelBridge
Custom routing logic implementations
"""
import time
import random
import logging
from typing import Dict, Any, List, Optional, Tuple
from abc import abstractmethod

from .base import Plugin, PluginConfig, PluginContext, PluginType, PluginPhase

logger = logging.getLogger(__name__)


class RoutingPlugin(Plugin):
    """Base class for routing plugins"""
    
    def get_plugin_type(self) -> PluginType:
        """Routing plugin type"""
        return PluginType.ROUTING
    
    def supports_phase(self, phase: PluginPhase) -> bool:
        """Routing plugins work in routing phases"""
        return phase in [
            PluginPhase.PRE_ROUTING,
            PluginPhase.POST_ROUTING
        ]
    
    @abstractmethod
    async def calculate_provider_scores(
        self, 
        context: PluginContext,
        available_providers: List[str]
    ) -> Dict[str, float]:
        """Calculate provider scores for routing"""
        pass


class CustomRoutingPlugin(RoutingPlugin):
    """Custom routing plugin with user-defined logic"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.routing_rules = config.config.get("routing_rules", {})
        self.provider_weights = config.config.get("provider_weights", {})
        self.fallback_strategy = config.config.get("fallback_strategy", "round_robin")
        
        # Statistics
        self.routing_decisions = 0
        self.fallback_used = 0
    
    async def initialize(self) -> bool:
        """Initialize routing plugin"""
        # Validate routing rules
        if not isinstance(self.routing_rules, dict):
            logger.error("routing_rules must be a dictionary")
            return False
        
        logger.info(f"Custom routing plugin initialized with {len(self.routing_rules)} rules")
        return True
    
    async def execute(self, context: PluginContext) -> PluginContext:
        """Execute routing logic"""
        if context.phase == PluginPhase.PRE_ROUTING:
            return await self._pre_routing(context)
        elif context.phase == PluginPhase.POST_ROUTING:
            return await self._post_routing(context)
        
        return context
    
    async def _pre_routing(self, context: PluginContext) -> PluginContext:
        """Pre-routing logic"""
        request_data = context.request_data or {}
        
        # Apply routing rules based on request characteristics
        routing_hints = {}
        
        # Check for specific routing rules
        for rule_name, rule_config in self.routing_rules.items():
            if await self._matches_rule(request_data, rule_config):
                logger.debug(f"Request matches routing rule: {rule_name}")
                
                # Apply rule modifications
                if "preferred_providers" in rule_config:
                    routing_hints["preferred_providers"] = rule_config["preferred_providers"]
                
                if "quality_requirement" in rule_config:
                    routing_hints["quality_requirement"] = rule_config["quality_requirement"]
                
                if "cost_sensitivity" in rule_config:
                    routing_hints["cost_sensitivity"] = rule_config["cost_sensitivity"]
                
                if "urgency" in rule_config:
                    routing_hints["urgency"] = rule_config["urgency"]
                
                break  # Use first matching rule
        
        # Store routing hints
        context.set_shared_data("custom_routing_hints", routing_hints)
        
        return context
    
    async def _post_routing(self, context: PluginContext) -> PluginContext:
        """Post-routing logic"""
        # Log routing decision
        selected_provider = context.provider_name
        routing_hints = context.get_shared_data("custom_routing_hints", {})
        
        self.routing_decisions += 1
        
        logger.info(f"Routing decision: {selected_provider}, hints: {routing_hints}")
        
        # Add routing metadata
        context.add_metric("custom_routing_applied", bool(routing_hints))
        context.add_metric("routing_rule_matched", len(routing_hints) > 0)
        
        return context
    
    async def _matches_rule(self, request_data: Dict[str, Any], rule_config: Dict[str, Any]) -> bool:
        """Check if request matches a routing rule"""
        conditions = rule_config.get("conditions", {})
        
        # Check prompt length condition
        if "prompt_length" in conditions:
            length_condition = conditions["prompt_length"]
            prompt = request_data.get("prompt", "")
            
            if "min" in length_condition and len(prompt) < length_condition["min"]:
                return False
            if "max" in length_condition and len(prompt) > length_condition["max"]:
                return False
        
        # Check model condition
        if "model" in conditions:
            required_model = conditions["model"]
            request_model = request_data.get("model", "")
            if required_model not in request_model:
                return False
        
        # Check prompt content condition
        if "prompt_contains" in conditions:
            required_content = conditions["prompt_contains"]
            prompt = request_data.get("prompt", "").lower()
            if required_content.lower() not in prompt:
                return False
        
        # Check time-based conditions
        if "time_of_day" in conditions:
            time_condition = conditions["time_of_day"]
            current_hour = time.localtime().tm_hour
            
            if "start_hour" in time_condition and current_hour < time_condition["start_hour"]:
                return False
            if "end_hour" in time_condition and current_hour > time_condition["end_hour"]:
                return False
        
        # Check user/auth conditions
        if "user_tier" in conditions and context.request_data:
            auth_data = context.request_data.get("authentication", {})
            user_tier = auth_data.get("tier", "free")
            if user_tier not in conditions["user_tier"]:
                return False
        
        return True
    
    async def calculate_provider_scores(
        self, 
        context: PluginContext,
        available_providers: List[str]
    ) -> Dict[str, float]:
        """Calculate provider scores based on custom logic"""
        scores = {}
        
        # Get routing hints
        routing_hints = context.get_shared_data("custom_routing_hints", {})
        preferred_providers = routing_hints.get("preferred_providers", [])
        
        # Base scores from configuration
        for provider in available_providers:
            base_score = self.provider_weights.get(provider, 50.0)
            
            # Boost preferred providers
            if preferred_providers and provider in preferred_providers:
                base_score += 20.0
                logger.debug(f"Boosting preferred provider {provider}: +20")
            
            scores[provider] = base_score
        
        return scores
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "routing_decisions": self.routing_decisions,
            "fallback_used": self.fallback_used,
            "routing_rules": len(self.routing_rules),
            "provider_weights": self.provider_weights
        })
        return base_stats


class LoadBalancingPlugin(RoutingPlugin):
    """Load balancing routing plugin"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.strategy = config.config.get("strategy", "round_robin")  # round_robin, weighted, least_connections
        self.provider_weights = config.config.get("provider_weights", {})
        self.connection_tracking = config.config.get("connection_tracking", True)
        
        # State tracking
        self.provider_connections: Dict[str, int] = {}
        self.round_robin_index = 0
        self.provider_response_times: Dict[str, List[float]] = {}
        
        # Statistics
        self.load_balancing_decisions = 0
        self.rebalancing_events = 0
    
    async def initialize(self) -> bool:
        """Initialize load balancing plugin"""
        logger.info(f"Load balancing plugin initialized with strategy: {self.strategy}")
        return True
    
    async def execute(self, context: PluginContext) -> PluginContext:
        """Execute load balancing logic"""
        if context.phase == PluginPhase.PRE_ROUTING:
            return await self._apply_load_balancing(context)
        elif context.phase == PluginPhase.POST_EXECUTION:
            return await self._update_load_metrics(context)
        
        return context
    
    def supports_phase(self, phase: PluginPhase) -> bool:
        """Load balancing works in routing and post-execution phases"""
        return phase in [
            PluginPhase.PRE_ROUTING,
            PluginPhase.POST_EXECUTION
        ]
    
    async def _apply_load_balancing(self, context: PluginContext) -> PluginContext:
        """Apply load balancing strategy"""
        available_providers = context.get_shared_data("available_providers", [])
        
        if not available_providers:
            return context
        
        # Calculate load balancing scores
        lb_scores = await self.calculate_provider_scores(context, available_providers)
        
        # Store load balancing scores
        context.set_shared_data("load_balancing_scores", lb_scores)
        
        self.load_balancing_decisions += 1
        
        logger.debug(f"Load balancing scores: {lb_scores}")
        
        return context
    
    async def _update_load_metrics(self, context: PluginContext) -> PluginContext:
        """Update load metrics after request execution"""
        provider_name = context.provider_name
        
        if not provider_name:
            return context
        
        # Update connection count
        if self.connection_tracking:
            if provider_name not in self.provider_connections:
                self.provider_connections[provider_name] = 0
            self.provider_connections[provider_name] += 1
        
        # Track response time
        response_time = context.get_metric("response_time")
        if response_time:
            if provider_name not in self.provider_response_times:
                self.provider_response_times[provider_name] = []
            
            self.provider_response_times[provider_name].append(response_time)
            
            # Keep only recent response times
            self.provider_response_times[provider_name] = \
                self.provider_response_times[provider_name][-100:]
        
        # Check if rebalancing is needed
        if await self._should_rebalance():
            await self._trigger_rebalancing()
        
        return context
    
    async def calculate_provider_scores(
        self, 
        context: PluginContext,
        available_providers: List[str]
    ) -> Dict[str, float]:
        """Calculate provider scores based on load balancing strategy"""
        scores = {}
        
        if self.strategy == "round_robin":
            # Round robin - give highest score to next provider in rotation
            for i, provider in enumerate(available_providers):
                if i == self.round_robin_index % len(available_providers):
                    scores[provider] = 100.0
                else:
                    scores[provider] = 50.0
            
            self.round_robin_index += 1
        
        elif self.strategy == "weighted":
            # Weighted distribution based on configured weights
            total_weight = sum(self.provider_weights.values()) or len(available_providers)
            
            for provider in available_providers:
                weight = self.provider_weights.get(provider, 1.0)
                scores[provider] = (weight / total_weight) * 100.0
        
        elif self.strategy == "least_connections":
            # Route to provider with least active connections
            if self.connection_tracking:
                min_connections = min(
                    self.provider_connections.get(p, 0) for p in available_providers
                )
                
                for provider in available_providers:
                    connections = self.provider_connections.get(provider, 0)
                    if connections == min_connections:
                        scores[provider] = 100.0
                    else:
                        # Inverse scoring based on connections
                        max_connections = max(self.provider_connections.values()) or 1
                        score = 100.0 - ((connections / max_connections) * 50.0)
                        scores[provider] = max(10.0, score)
            else:
                # Fall back to round robin
                return await self._round_robin_scores(available_providers)
        
        elif self.strategy == "response_time":
            # Route based on historical response times
            for provider in available_providers:
                response_times = self.provider_response_times.get(provider, [])
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    # Lower response time = higher score
                    scores[provider] = max(10.0, 100.0 - (avg_response_time * 10))
                else:
                    scores[provider] = 50.0  # Neutral score for new providers
        
        else:
            # Default to equal scoring
            for provider in available_providers:
                scores[provider] = 50.0
        
        return scores
    
    async def _round_robin_scores(self, available_providers: List[str]) -> Dict[str, float]:
        """Round robin scoring fallback"""
        scores = {}
        for i, provider in enumerate(available_providers):
            if i == self.round_robin_index % len(available_providers):
                scores[provider] = 100.0
            else:
                scores[provider] = 50.0
        
        self.round_robin_index += 1
        return scores
    
    async def _should_rebalance(self) -> bool:
        """Check if load rebalancing is needed"""
        if not self.provider_connections or len(self.provider_connections) < 2:
            return False
        
        connections = list(self.provider_connections.values())
        if not connections:
            return False
        
        max_conn = max(connections)
        min_conn = min(connections)
        
        # Rebalance if difference is significant
        return max_conn > min_conn + 10
    
    async def _trigger_rebalancing(self):
        """Trigger load rebalancing"""
        logger.info("Triggering load rebalancing")
        
        # Reset connection counts for rebalancing
        total_connections = sum(self.provider_connections.values())
        num_providers = len(self.provider_connections)
        
        if num_providers > 0:
            avg_connections = total_connections // num_providers
            
            for provider in self.provider_connections:
                self.provider_connections[provider] = avg_connections
        
        self.rebalancing_events += 1
    
    def get_load_balancing_stats(self) -> Dict[str, Any]:
        """Get detailed load balancing statistics"""
        return {
            "strategy": self.strategy,
            "provider_connections": self.provider_connections.copy(),
            "provider_avg_response_times": {
                provider: sum(times) / len(times) if times else 0.0
                for provider, times in self.provider_response_times.items()
            },
            "round_robin_index": self.round_robin_index,
            "load_balancing_decisions": self.load_balancing_decisions,
            "rebalancing_events": self.rebalancing_events
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        base_stats = super().get_stats()
        base_stats.update(self.get_load_balancing_stats())
        return base_stats


class GeographicRoutingPlugin(RoutingPlugin):
    """Geographic-based routing plugin"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.provider_regions = config.config.get("provider_regions", {})
        self.region_preferences = config.config.get("region_preferences", {})
        self.latency_weights = config.config.get("latency_weights", True)
        
        # Statistics
        self.geographic_routings = 0
        self.region_overrides = 0
    
    async def initialize(self) -> bool:
        """Initialize geographic routing plugin"""
        if not self.provider_regions:
            logger.warning("No provider regions configured for geographic routing")
        
        logger.info(f"Geographic routing plugin initialized for {len(self.provider_regions)} providers")
        return True
    
    async def execute(self, context: PluginContext) -> PluginContext:
        """Execute geographic routing logic"""
        if context.phase == PluginPhase.PRE_ROUTING:
            return await self._apply_geographic_routing(context)
        
        return context
    
    async def _apply_geographic_routing(self, context: PluginContext) -> PluginContext:
        """Apply geographic routing preferences"""
        client_region = context.get_shared_data("client_region")
        available_providers = context.get_shared_data("available_providers", [])
        
        if not client_region or not available_providers:
            return context
        
        # Calculate geographic scores
        geo_scores = await self.calculate_provider_scores(context, available_providers)
        
        # Store geographic routing scores
        context.set_shared_data("geographic_routing_scores", geo_scores)
        
        self.geographic_routings += 1
        
        logger.debug(f"Geographic routing scores for region {client_region}: {geo_scores}")
        
        return context
    
    async def calculate_provider_scores(
        self, 
        context: PluginContext,
        available_providers: List[str]
    ) -> Dict[str, float]:
        """Calculate provider scores based on geographic proximity"""
        client_region = context.get_shared_data("client_region", "unknown")
        scores = {}
        
        for provider in available_providers:
            provider_region = self.provider_regions.get(provider, "unknown")
            
            # Same region gets highest score
            if provider_region == client_region:
                scores[provider] = 100.0
            
            # Regional preferences
            elif client_region in self.region_preferences:
                preferred_regions = self.region_preferences[client_region]
                if provider_region in preferred_regions:
                    # Score based on preference order
                    preference_index = preferred_regions.index(provider_region)
                    scores[provider] = 90.0 - (preference_index * 10.0)
                else:
                    scores[provider] = 40.0  # Non-preferred region
            
            else:
                # Default scoring for unknown regions
                scores[provider] = 50.0
        
        return scores
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "geographic_routings": self.geographic_routings,
            "region_overrides": self.region_overrides,
            "provider_regions": self.provider_regions,
            "region_preferences": self.region_preferences
        })
        return base_stats