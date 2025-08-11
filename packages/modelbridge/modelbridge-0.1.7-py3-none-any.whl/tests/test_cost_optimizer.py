"""
Comprehensive tests for the cost optimization system
"""
import pytest
from unittest.mock import Mock, patch

from modelbridge.cost.optimizer import (
    CostOptimizer, OptimizationStrategy, OptimizationResult, ModelProfile
)


class TestCostOptimizer:
    """Test suite for CostOptimizer functionality"""
    
    @pytest.fixture
    def cost_optimizer(self):
        """Create cost optimizer instance"""
        return CostOptimizer()
    
    def test_initialization(self, cost_optimizer):
        """Test cost optimizer initialization"""
        assert len(cost_optimizer.model_profiles) > 0
        assert len(cost_optimizer.optimization_pathways) > 0
        assert len(cost_optimizer.task_compatibility) > 0
        
        # Check key models are present
        assert "gpt-5" in cost_optimizer.model_profiles
        assert "gpt-5-mini" in cost_optimizer.model_profiles
        assert "gpt-5-nano" in cost_optimizer.model_profiles
        assert "claude-opus-4-1" in cost_optimizer.model_profiles
    
    def test_model_profiles_structure(self, cost_optimizer):
        """Test model profiles have correct structure"""
        gpt5_profile = cost_optimizer.model_profiles["gpt-5"]
        
        assert gpt5_profile.model_id == "gpt-5"
        assert gpt5_profile.provider == "openai"
        assert gpt5_profile.cost_per_1k_tokens > 0
        assert gpt5_profile.quality_score > 0
        assert gpt5_profile.speed_score > 0
        assert isinstance(gpt5_profile.capabilities, list)
        assert isinstance(gpt5_profile.best_for, list)
    
    def test_optimization_pathways_structure(self, cost_optimizer):
        """Test optimization pathways are properly structured"""
        # Check GPT-5 has downgrade options
        gpt5_pathways = cost_optimizer.optimization_pathways["gpt-5"]
        assert len(gpt5_pathways) > 0
        assert "gpt-5-mini" in gpt5_pathways
        
        # Check all pathway targets exist in model profiles
        for model, pathways in cost_optimizer.optimization_pathways.items():
            for pathway_model in pathways:
                assert pathway_model in cost_optimizer.model_profiles, f"{pathway_model} not in profiles"
    
    def test_task_compatibility_structure(self, cost_optimizer):
        """Test task compatibility matrix structure"""
        coding_tasks = cost_optimizer.task_compatibility["coding"]
        
        assert "high_quality" in coding_tasks
        assert "balanced" in coding_tasks
        assert "economic" in coding_tasks
        
        # Check all models in compatibility exist in profiles
        for task_type, quality_tiers in cost_optimizer.task_compatibility.items():
            for tier, models in quality_tiers.items():
                for model in models:
                    assert model in cost_optimizer.model_profiles, f"{model} not in profiles"
    
    def test_optimize_unknown_model(self, cost_optimizer):
        """Test optimization with unknown model"""
        result = cost_optimizer.optimize_model_selection(
            original_model="unknown-model",
            task_type="coding",
            strategy=OptimizationStrategy.BALANCED
        )
        
        assert result.original_model == "unknown-model"
        assert result.optimized_model == "unknown-model"
        assert result.cost_savings == 0.0
        assert result.confidence == 0.0
        assert "not in optimization profiles" in result.reasoning
    
    def test_optimize_within_budget(self, cost_optimizer):
        """Test optimization when original model is within budget"""
        result = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",
            task_type="coding",
            strategy=OptimizationStrategy.BALANCED,
            max_cost=10.0,  # High budget
            estimated_tokens=1000
        )
        
        # Should not optimize if within budget
        assert result.original_model == "gpt-5"
        assert result.optimized_model == "gpt-5"
        assert result.cost_savings == 0.0
        assert "within cost budget" in result.reasoning
    
    def test_optimize_aggressive_strategy(self, cost_optimizer):
        """Test aggressive optimization strategy"""
        result = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",
            task_type="simple",
            strategy=OptimizationStrategy.AGGRESSIVE,
            estimated_tokens=1000,
            available_providers=["openai", "groq"]
        )
        
        # Should suggest significant cost reduction for simple tasks
        assert result.optimized_model != "gpt-5"  # Should be different
        assert result.cost_savings > 0
        assert result.savings_percentage > 50  # Aggressive should save significant amount
        
        # Check it's actually cheaper
        original_profile = cost_optimizer.model_profiles["gpt-5"]
        optimized_profile = cost_optimizer.model_profiles[result.optimized_model]
        assert optimized_profile.cost_per_1k_tokens < original_profile.cost_per_1k_tokens
    
    def test_optimize_conservative_strategy(self, cost_optimizer):
        """Test conservative optimization strategy"""
        result = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",
            task_type="complex_analysis",
            strategy=OptimizationStrategy.CONSERVATIVE,
            estimated_tokens=1000,
            available_providers=["openai", "anthropic"]
        )
        
        # Conservative should maintain quality
        if result.optimized_model != "gpt-5":
            original_profile = cost_optimizer.model_profiles["gpt-5"]
            optimized_profile = cost_optimizer.model_profiles[result.optimized_model]
            
            # Quality difference should be minimal
            quality_diff = original_profile.quality_score - optimized_profile.quality_score
            assert quality_diff <= 15  # Conservative quality preservation
            assert result.confidence > 0.7  # High confidence for conservative
    
    def test_optimize_emergency_strategy(self, cost_optimizer):
        """Test emergency optimization strategy"""
        result = cost_optimizer.optimize_model_selection(
            original_model="claude-opus-4-1",  # Most expensive model
            task_type="general",
            strategy=OptimizationStrategy.EMERGENCY,
            estimated_tokens=1000
        )
        
        # Emergency should maximize cost savings
        assert result.optimized_model != "claude-opus-4-1"
        assert result.cost_savings > 0
        assert result.savings_percentage > 80  # Emergency should save dramatically
        
        # Should pick very cheap model (cheaper than original claude-opus-4-1 at 15.0)
        optimized_profile = cost_optimizer.model_profiles[result.optimized_model]
        assert optimized_profile.cost_per_1k_tokens < 1.0  # Significantly cheaper
    
    def test_optimize_with_max_cost_constraint(self, cost_optimizer):
        """Test optimization with max cost constraint"""
        result = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",
            task_type="coding",
            strategy=OptimizationStrategy.BALANCED,
            max_cost=0.0001,  # Very tight budget
            estimated_tokens=1000
        )
        
        # Should find model within budget
        if result.optimized_model != "gpt-5":
            optimized_cost = result.optimized_cost
            assert optimized_cost <= 0.0001
    
    def test_optimize_provider_availability(self, cost_optimizer):
        """Test optimization respects provider availability"""
        result = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",
            task_type="coding",
            strategy=OptimizationStrategy.BALANCED,
            available_providers=["groq"]  # Only Groq available
        )
        
        # Should only suggest Groq models
        if result.optimized_model != "gpt-5":
            optimized_profile = cost_optimizer.model_profiles[result.optimized_model]
            assert optimized_profile.provider == "groq"
    
    def test_optimize_task_specific_coding(self, cost_optimizer):
        """Test task-specific optimization for coding"""
        result = cost_optimizer.optimize_model_selection(
            original_model="claude-opus-4-1",  # Expensive but good for analysis
            task_type="coding",
            strategy=OptimizationStrategy.BALANCED,
            estimated_tokens=1000
        )
        
        # Should suggest coding-appropriate model
        if result.optimized_model != "claude-opus-4-1":
            # Check optimized model is good for coding
            coding_models = (
                cost_optimizer.task_compatibility["coding"]["high_quality"] +
                cost_optimizer.task_compatibility["coding"]["balanced"] +
                cost_optimizer.task_compatibility["coding"]["economic"]
            )
            assert result.optimized_model in coding_models
    
    def test_optimize_task_specific_conversation(self, cost_optimizer):
        """Test task-specific optimization for conversation"""
        result = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",  # Expensive for simple conversation
            task_type="conversation",
            strategy=OptimizationStrategy.BALANCED,
            estimated_tokens=500  # Short conversation
        )
        
        # Should suggest conversation-appropriate model
        assert result.cost_savings > 0
        
        # Check optimized model is good for conversation
        conversation_models = (
            cost_optimizer.task_compatibility["conversation"]["high_quality"] +
            cost_optimizer.task_compatibility["conversation"]["balanced"] +
            cost_optimizer.task_compatibility["conversation"]["economic"]
        )
        assert result.optimized_model in conversation_models
    
    def test_optimization_quality_impact_assessment(self, cost_optimizer):
        """Test quality impact assessment"""
        # Test minimal quality impact
        gpt5_profile = cost_optimizer.model_profiles["gpt-5"]
        gpt5_mini_profile = cost_optimizer.model_profiles["gpt-5-mini"]
        
        quality_impact = cost_optimizer._assess_quality_impact(gpt5_profile, gpt5_mini_profile)
        assert quality_impact in ["none", "minimal", "moderate", "significant"]
        
        # Test significant quality impact
        nano_profile = cost_optimizer.model_profiles["gpt-5-nano"]
        quality_impact_large = cost_optimizer._assess_quality_impact(gpt5_profile, nano_profile)
        assert quality_impact_large in ["moderate", "significant"]
    
    def test_optimization_confidence_calculation(self, cost_optimizer):
        """Test confidence calculation for optimizations"""
        gpt5_profile = cost_optimizer.model_profiles["gpt-5"]
        gpt5_mini_profile = cost_optimizer.model_profiles["gpt-5-mini"]
        
        confidence = cost_optimizer._calculate_optimization_confidence(
            gpt5_profile, gpt5_mini_profile, "coding", OptimizationStrategy.BALANCED
        )
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident for good optimization
    
    def test_optimization_reasoning_generation(self, cost_optimizer):
        """Test optimization reasoning generation"""
        gpt5_profile = cost_optimizer.model_profiles["gpt-5"]
        gpt5_mini_profile = cost_optimizer.model_profiles["gpt-5-mini"]
        
        reasoning = cost_optimizer._generate_optimization_reasoning(
            gpt5_profile, gpt5_mini_profile, OptimizationStrategy.BALANCED, "coding", 0.001
        )
        
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
        assert "$" in reasoning  # Should mention cost savings
    
    def test_get_cost_optimization_recommendations(self, cost_optimizer):
        """Test comprehensive optimization recommendations"""
        usage_pattern = {
            "model_usage": {
                "gpt-5": {"total_cost": 15.0, "requests": 100, "total_tokens": 150000},
                "gpt-5-mini": {"total_cost": 5.0, "requests": 200, "total_tokens": 100000}
            }
        }
        
        recommendations = cost_optimizer.get_cost_optimization_recommendations(
            current_usage=20.0,
            budget_limit=50.0,
            usage_pattern=usage_pattern
        )
        
        assert "overall_status" in recommendations
        assert "potential_savings" in recommendations
        assert "model_recommendations" in recommendations
        assert "general_tips" in recommendations
        
        # Should be healthy since under budget
        assert recommendations["overall_status"] == "healthy"
    
    def test_recommendations_critical_status(self, cost_optimizer):
        """Test recommendations when in critical budget state"""
        usage_pattern = {
            "model_usage": {
                "claude-opus-4-1": {"total_cost": 95.0, "requests": 50, "total_tokens": 50000}
            }
        }
        
        recommendations = cost_optimizer.get_cost_optimization_recommendations(
            current_usage=95.0,
            budget_limit=100.0,  # 95% used
            usage_pattern=usage_pattern
        )
        
        assert recommendations["overall_status"] == "critical"
        assert len(recommendations["urgent_actions"]) > 0
        assert "cheaper models" in recommendations["urgent_actions"][0]
    
    def test_suggest_emergency_actions(self, cost_optimizer):
        """Test emergency action suggestions"""
        actions = cost_optimizer.suggest_emergency_actions(budget_exceeded_by=25.0)
        
        assert len(actions) > 0
        assert any("CRITICAL" in action for action in actions)
        assert any("$25.00" in action for action in actions)
        assert any("gpt-5 →" in action for action in actions)  # Should suggest downgrades
    
    def test_optimization_score_calculation(self, cost_optimizer):
        """Test optimization score calculation for ranking"""
        gpt5_profile = cost_optimizer.model_profiles["gpt-5"]
        nano_profile = cost_optimizer.model_profiles["gpt-5-nano"]
        
        # Calculate score for large savings
        score = cost_optimizer._calculate_optimization_score(
            nano_profile, gpt5_profile, "simple", OptimizationStrategy.AGGRESSIVE, 95.0
        )
        
        assert score > 0
        assert score > 50  # Should get good score for high savings
    
    def test_candidate_selection_and_ranking(self, cost_optimizer):
        """Test optimization candidate selection and ranking"""
        candidates = cost_optimizer._get_optimization_candidates(
            "gpt-5", "coding", OptimizationStrategy.BALANCED, ["openai", "groq"]
        )
        
        assert len(candidates) > 0
        
        # All candidates should be cheaper than original
        gpt5_profile = cost_optimizer.model_profiles["gpt-5"]
        for candidate in candidates:
            assert candidate.cost_per_1k_tokens < gpt5_profile.cost_per_1k_tokens
            assert candidate.provider in ["openai", "groq"]
    
    def test_no_optimization_candidates(self, cost_optimizer):
        """Test when no optimization candidates are available"""
        # Use cheapest model with no available providers
        result = cost_optimizer.optimize_model_selection(
            original_model="llama-3.1-8b-instant",
            task_type="general",
            strategy=OptimizationStrategy.BALANCED,
            available_providers=["nonexistent"]
        )
        
        assert result.original_model == result.optimized_model
        assert result.cost_savings == 0.0
        assert "No optimization candidates" in result.reasoning
    
    def test_optimization_edge_cases(self, cost_optimizer):
        """Test optimization edge cases"""
        # Test with zero estimated tokens
        result = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",
            task_type="general",
            strategy=OptimizationStrategy.BALANCED,
            estimated_tokens=0
        )
        
        # Should handle gracefully
        assert result is not None
        
        # Test with extremely high token estimate
        result_high = cost_optimizer.optimize_model_selection(
            original_model="gpt-5",
            task_type="general",
            strategy=OptimizationStrategy.BALANCED,
            estimated_tokens=1000000
        )
        
        # Should still optimize for cost with high token count
        assert result_high.cost_savings > 0


class TestOptimizationResult:
    """Test suite for OptimizationResult data class"""
    
    def test_optimization_result_creation(self):
        """Test OptimizationResult creation"""
        result = OptimizationResult(
            original_model="gpt-5",
            optimized_model="gpt-5-mini",
            original_cost=0.0125,
            optimized_cost=0.0025,
            cost_savings=0.01,
            savings_percentage=80.0,
            quality_impact="minimal",
            reasoning="Better cost efficiency for simple tasks",
            confidence=0.85
        )
        
        assert result.original_model == "gpt-5"
        assert result.optimized_model == "gpt-5-mini"
        assert result.cost_savings == 0.01
        assert result.savings_percentage == 80.0
        assert result.confidence == 0.85


class TestModelProfile:
    """Test suite for ModelProfile data class"""
    
    def test_model_profile_creation(self):
        """Test ModelProfile creation"""
        profile = ModelProfile(
            model_id="test-model",
            provider="test-provider",
            cost_per_1k_tokens=0.5,
            quality_score=85,
            speed_score=90,
            capabilities=["text", "coding"],
            best_for=["coding", "analysis"]
        )
        
        assert profile.model_id == "test-model"
        assert profile.provider == "test-provider"
        assert profile.cost_per_1k_tokens == 0.5
        assert profile.quality_score == 85
        assert profile.speed_score == 90
        assert "coding" in profile.capabilities
        assert "coding" in profile.best_for


class TestOptimizationStrategies:
    """Test suite for optimization strategy behaviors"""
    
    @pytest.fixture
    def cost_optimizer(self):
        return CostOptimizer()
    
    def test_all_strategies_produce_valid_results(self, cost_optimizer):
        """Test all optimization strategies produce valid results"""
        strategies = [
            OptimizationStrategy.AGGRESSIVE,
            OptimizationStrategy.BALANCED, 
            OptimizationStrategy.CONSERVATIVE,
            OptimizationStrategy.EMERGENCY
        ]
        
        for strategy in strategies:
            result = cost_optimizer.optimize_model_selection(
                original_model="gpt-5",
                task_type="general",
                strategy=strategy,
                estimated_tokens=1000
            )
            
            assert result is not None
            assert isinstance(result.confidence, float)
            assert 0.0 <= result.confidence <= 1.0
            assert isinstance(result.reasoning, str)
            assert len(result.reasoning) > 0
    
    def test_strategy_cost_savings_order(self, cost_optimizer):
        """Test that strategies produce expected cost savings order"""
        strategies = [
            OptimizationStrategy.EMERGENCY,
            OptimizationStrategy.AGGRESSIVE,
            OptimizationStrategy.BALANCED,
            OptimizationStrategy.CONSERVATIVE
        ]
        
        results = []
        for strategy in strategies:
            result = cost_optimizer.optimize_model_selection(
                original_model="claude-opus-4-1",  # Expensive model
                task_type="simple",
                strategy=strategy,
                estimated_tokens=1000
            )
            results.append((strategy, result.savings_percentage))
        
        # Emergency should save most, conservative should save least
        emergency_savings = next(savings for strategy, savings in results 
                                if strategy == OptimizationStrategy.EMERGENCY)
        conservative_savings = next(savings for strategy, savings in results 
                                   if strategy == OptimizationStrategy.CONSERVATIVE)
        
        if emergency_savings > 0 and conservative_savings > 0:
            assert emergency_savings >= conservative_savings