"""
Comprehensive tests for the task analysis and smart routing system
"""
import pytest
from unittest.mock import Mock, patch

from modelbridge.analyzer import TaskAnalyzer, TaskAnalysis, TaskType


class TestTaskAnalyzer:
    """Test suite for TaskAnalyzer functionality"""
    
    @pytest.fixture
    def task_analyzer(self):
        """Create task analyzer instance"""
        return TaskAnalyzer()
    
    def test_initialization(self, task_analyzer):
        """Test task analyzer initialization"""
        assert len(task_analyzer.task_patterns) > 0
        assert len(task_analyzer.complexity_indicators) > 0
        assert len(task_analyzer.model_recommendations) > 0
        
        # Check key task patterns exist
        assert TaskType.CODING in task_analyzer.task_patterns
        assert TaskType.ANALYSIS in task_analyzer.task_patterns
        assert TaskType.CONVERSATION in task_analyzer.task_patterns
        assert TaskType.CREATIVE in task_analyzer.task_patterns
    
    def test_task_patterns_structure(self, task_analyzer):
        """Test task patterns have correct structure"""
        coding_patterns = task_analyzer.task_patterns[TaskType.CODING]
        
        assert len(coding_patterns) > 0
        assert any("code" in pattern.lower() for pattern in coding_patterns)
        assert any("debug" in pattern.lower() for pattern in coding_patterns)
        assert any("function" in pattern.lower() for pattern in coding_patterns)
    
    def test_analyze_coding_task(self, task_analyzer):
        """Test analysis of coding-related prompts"""
        coding_prompts = [
            "Write a Python function to sort a list",
            "Debug this JavaScript code that's not working",
            "Create a REST API endpoint for user authentication", 
            "Refactor this code to improve performance",
            "Fix the bug in this SQL query",
            "Write unit tests for this React component"
        ]
        
        for prompt in coding_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "anthropic"]
            )
            
            assert analysis.task_type == TaskType.CODING
            assert analysis.confidence > 0.5
            assert analysis.recommended_model is not None
            assert len(analysis.reasoning) > 0
            
            # Should recommend coding-appropriate models
            recommended_models = ["gpt-5", "gpt-5-mini", "claude-3-5-sonnet", "llama-3.3-70b-versatile"]
            assert any(model in analysis.recommended_model for model in recommended_models)
    
    def test_analyze_analysis_task(self, task_analyzer):
        """Test analysis of analytical prompts"""
        analysis_prompts = [
            "Analyze the market trends in renewable energy",
            "Compare and contrast different machine learning algorithms",
            "Evaluate the pros and cons of remote work",
            "What are the implications of this research paper?",
            "Summarize the key findings from this dataset",
            "Explain the causes of climate change"
        ]
        
        for prompt in analysis_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "anthropic", "google"]
            )
            
            assert analysis.task_type == TaskType.ANALYSIS
            assert analysis.confidence > 0.4
            
            # Should recommend analysis-appropriate models
            recommended_models = ["claude-opus-4-1", "gpt-5", "claude-3-5-sonnet", "gemini-2.5-pro"]
            assert any(model in analysis.recommended_model for model in recommended_models)
    
    def test_analyze_creative_task(self, task_analyzer):
        """Test analysis of creative writing prompts"""
        creative_prompts = [
            "Write a short story about a time traveler",
            "Create a poem about the ocean",
            "Generate marketing copy for a new product",
            "Write dialogue for a dramatic scene",
            "Create a fantasy world with unique magic system",
            "Draft a creative brief for a advertising campaign"
        ]
        
        for prompt in creative_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["anthropic", "openai"]
            )
            
            assert analysis.task_type == TaskType.CREATIVE
            assert analysis.confidence > 0.4
            
            # Should recommend creative-appropriate models
            recommended_models = ["claude-opus-4-1", "gpt-5", "claude-3-5-sonnet"]
            assert any(model in analysis.recommended_model for model in recommended_models)
    
    def test_analyze_conversation_task(self, task_analyzer):
        """Test analysis of conversational prompts"""
        conversation_prompts = [
            "Hello, how are you today?",
            "Can you help me understand this concept?",
            "What's the weather like?",
            "Tell me a joke",
            "I'm feeling sad, can we chat?",
            "What do you think about this situation?"
        ]
        
        for prompt in conversation_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "groq"]
            )
            
            assert analysis.task_type == TaskType.CONVERSATION
            assert analysis.confidence > 0.3
            
            # Should recommend conversational models (often faster/cheaper)
            recommended_models = ["gpt-5-mini", "gpt-5-nano", "llama-3.3-70b-versatile", "claude-3-5-sonnet"]
            assert any(model in analysis.recommended_model for model in recommended_models)
    
    def test_analyze_simple_task(self, task_analyzer):
        """Test analysis of simple tasks"""
        simple_prompts = [
            "Translate 'hello' to French",
            "What is 2+2?",
            "Define 'photosynthesis'",
            "Convert 100 USD to EUR",
            "What time is it in Tokyo?",
            "Spell 'encyclopedia'"
        ]
        
        for prompt in simple_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "groq", "google"]
            )
            
            assert analysis.task_type == TaskType.SIMPLE
            assert analysis.confidence > 0.4
            
            # Should recommend cheaper, faster models
            recommended_models = ["gpt-5-nano", "llama-3.1-8b-instant", "gemini-2.5-flash-lite", "mixtral-8x7b-32768"]
            assert any(model in analysis.recommended_model for model in recommended_models)
    
    def test_analyze_reasoning_task(self, task_analyzer):
        """Test analysis of complex reasoning tasks"""
        reasoning_prompts = [
            "If all A are B, and all B are C, then what can we conclude about A and C?",
            "Solve this logic puzzle step by step",
            "What is the philosophical implication of artificial consciousness?",
            "Derive the mathematical proof for this theorem",
            "Analyze the causal relationships in this complex system",
            "What are the second and third order effects of this policy?"
        ]
        
        for prompt in reasoning_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "anthropic"]
            )
            
            assert analysis.task_type == TaskType.REASONING
            assert analysis.confidence > 0.4
            
            # Should recommend high-quality reasoning models
            recommended_models = ["gpt-5", "claude-opus-4-1", "o3", "claude-3-5-sonnet"]
            assert any(model in analysis.recommended_model for model in recommended_models)
    
    def test_complexity_scoring(self, task_analyzer):
        """Test complexity scoring functionality"""
        test_cases = [
            ("What is 1+1?", 0.1, 0.4),  # Simple - low complexity
            ("Write hello world in Python", 0.3, 0.7),  # Medium complexity
            ("Design a distributed system architecture for handling millions of users with real-time features, considering scalability, fault tolerance, security, and cost optimization", 0.8, 1.0)  # High complexity
        ]
        
        for prompt, min_expected, max_expected in test_cases:
            analysis = task_analyzer.analyze(prompt, available_providers=["openai"])
            
            assert min_expected <= analysis.complexity_score <= max_expected, \
                f"Complexity score {analysis.complexity_score} not in expected range [{min_expected}, {max_expected}] for prompt: {prompt}"
    
    def test_optimize_for_speed(self, task_analyzer):
        """Test optimization for speed preference"""
        analysis = task_analyzer.analyze(
            prompt="Write a simple function to add two numbers",
            optimize_for="speed",
            available_providers=["openai", "groq"]
        )
        
        # Should prefer fast models
        fast_models = ["mixtral-8x7b-32768", "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gpt-5-nano"]
        assert any(model in analysis.recommended_model for model in fast_models)
        assert "speed" in analysis.reasoning.lower() or "fast" in analysis.reasoning.lower()
    
    def test_optimize_for_cost(self, task_analyzer):
        """Test optimization for cost preference"""
        analysis = task_analyzer.analyze(
            prompt="Translate this text to Spanish",
            optimize_for="cost",
            available_providers=["openai", "groq", "google"]
        )
        
        # Should prefer cheap models
        cheap_models = ["gpt-5-nano", "llama-3.1-8b-instant", "gemini-2.5-flash-lite", "mixtral-8x7b-32768"]
        assert any(model in analysis.recommended_model for model in cheap_models)
        assert "cost" in analysis.reasoning.lower() or "cheap" in analysis.reasoning.lower()
    
    def test_optimize_for_quality(self, task_analyzer):
        """Test optimization for quality preference"""
        analysis = task_analyzer.analyze(
            prompt="Write a comprehensive analysis of quantum computing",
            optimize_for="quality",
            available_providers=["openai", "anthropic"]
        )
        
        # Should prefer high-quality models
        quality_models = ["gpt-5", "claude-opus-4-1", "claude-3-5-sonnet", "gpt-4.1"]
        assert any(model in analysis.recommended_model for model in quality_models)
        assert "quality" in analysis.reasoning.lower() or "best" in analysis.reasoning.lower()
    
    def test_max_cost_constraint(self, task_analyzer):
        """Test analysis with maximum cost constraint"""
        analysis = task_analyzer.analyze(
            prompt="Write a detailed report on market analysis",
            max_cost=0.001,  # Very low cost limit
            available_providers=["openai", "groq", "google"]
        )
        
        # Should recommend very cheap models
        ultra_cheap_models = ["gpt-5-nano", "llama-3.1-8b-instant", "gemini-2.5-flash-lite"]
        assert any(model in analysis.recommended_model for model in ultra_cheap_models)
        assert "cost" in analysis.reasoning.lower()
    
    def test_provider_availability_constraint(self, task_analyzer):
        """Test analysis with limited provider availability"""
        # Only Groq available
        analysis_groq = task_analyzer.analyze(
            prompt="Write a Python function",
            available_providers=["groq"]
        )
        
        groq_models = ["mixtral-8x7b-32768", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        assert any(model in analysis_groq.recommended_model for model in groq_models)
        
        # Only Anthropic available
        analysis_anthropic = task_analyzer.analyze(
            prompt="Analyze this complex problem",
            available_providers=["anthropic"]
        )
        
        anthropic_models = ["claude-opus-4-1", "claude-3-5-sonnet"]
        assert any(model in analysis_anthropic.recommended_model for model in anthropic_models)
    
    def test_empty_available_providers(self, task_analyzer):
        """Test analysis with no available providers"""
        analysis = task_analyzer.analyze(
            prompt="Test prompt",
            available_providers=[]
        )
        
        # Should still provide analysis but may have limited recommendations
        assert analysis.task_type is not None
        assert analysis.confidence >= 0.0
        # Recommended model might be None or a default
    
    def test_analyze_mixed_task(self, task_analyzer):
        """Test analysis of mixed/complex tasks"""
        mixed_prompts = [
            "Write a Python script to analyze sales data and create visualizations, then provide insights",
            "Create a creative story about a programmer who discovers a bug that changes reality",
            "Debug this code and explain the solution in simple terms for a beginner"
        ]
        
        for prompt in mixed_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "anthropic", "google"]
            )
            
            # Should detect some task type
            assert analysis.task_type is not None
            assert analysis.confidence > 0.0
            assert analysis.complexity_score > 0.5  # Mixed tasks tend to be more complex
            
            # Should provide reasoning
            assert len(analysis.reasoning) > 10
    
    def test_keyword_pattern_matching(self, task_analyzer):
        """Test keyword pattern matching functionality"""
        # Test specific keywords that should trigger certain classifications
        test_cases = [
            ("function", TaskType.CODING),
            ("debug", TaskType.CODING),
            ("analyze", TaskType.ANALYSIS),
            ("story", TaskType.CREATIVE),
            ("poem", TaskType.CREATIVE),
            ("hello", TaskType.CONVERSATION),
            ("translate", TaskType.SIMPLE)
        ]
        
        for keyword, expected_type in test_cases:
            prompt = f"Can you {keyword} this for me?"
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai"]
            )
            
            # Should detect the expected type (allowing for some flexibility)
            assert analysis.task_type == expected_type or analysis.confidence < 0.7, \
                f"Expected {expected_type} for keyword '{keyword}', got {analysis.task_type}"
    
    def test_confidence_calculation(self, task_analyzer):
        """Test confidence calculation accuracy"""
        # Clear task should have high confidence
        clear_coding_prompt = "Write a Python function to calculate fibonacci numbers"
        analysis_clear = task_analyzer.analyze(clear_coding_prompt, available_providers=["openai"])
        assert analysis_clear.confidence > 0.7
        
        # Ambiguous task should have lower confidence
        ambiguous_prompt = "Help me with this thing"
        analysis_ambiguous = task_analyzer.analyze(ambiguous_prompt, available_providers=["openai"])
        assert analysis_ambiguous.confidence < 0.6
        
        # Very specific task should have high confidence
        specific_prompt = "Debug this TypeError in my Python list comprehension"
        analysis_specific = task_analyzer.analyze(specific_prompt, available_providers=["openai"])
        assert analysis_specific.confidence > 0.8
    
    def test_reasoning_quality(self, task_analyzer):
        """Test quality of reasoning explanations"""
        analysis = task_analyzer.analyze(
            prompt="Create a machine learning model to predict house prices",
            optimize_for="quality",
            available_providers=["openai", "anthropic"]
        )
        
        reasoning = analysis.reasoning.lower()
        
        # Should explain task type detection
        assert any(word in reasoning for word in ["coding", "analysis", "machine learning", "model"])
        
        # Should explain model selection
        assert any(word in reasoning for word in ["quality", "complex", "recommend", "suitable"])
        
        # Should be substantive
        assert len(reasoning) > 50
    
    def test_edge_case_empty_prompt(self, task_analyzer):
        """Test handling of empty or minimal prompts"""
        edge_cases = ["", "   ", "?", "help", "hi"]
        
        for prompt in edge_cases:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai"]
            )
            
            # Should handle gracefully
            assert analysis.task_type is not None
            assert analysis.confidence >= 0.0
            assert analysis.recommended_model is not None
            
            # Low confidence expected for unclear prompts
            if len(prompt.strip()) < 3:
                assert analysis.confidence < 0.5
    
    def test_very_long_prompt(self, task_analyzer):
        """Test handling of very long prompts"""
        long_prompt = "Write a comprehensive analysis of " + "very " * 1000 + "complex system"
        
        analysis = task_analyzer.analyze(
            prompt=long_prompt,
            available_providers=["openai", "anthropic"]
        )
        
        # Should handle without errors
        assert analysis.task_type is not None
        assert analysis.complexity_score > 0.7  # Long prompts tend to be complex
        assert analysis.recommended_model is not None
    
    def test_pattern_matching_accuracy(self, task_analyzer):
        """Test accuracy of pattern matching across task types"""
        # Create test cases with ground truth labels
        test_cases = [
            ("Fix this bug in my code", TaskType.CODING),
            ("What causes global warming?", TaskType.ANALYSIS), 
            ("Write a haiku about spring", TaskType.CREATIVE),
            ("How's your day going?", TaskType.CONVERSATION),
            ("What's 15% of 80?", TaskType.SIMPLE),
            ("Prove that P=NP", TaskType.REASONING)
        ]
        
        correct_predictions = 0
        for prompt, expected_type in test_cases:
            analysis = task_analyzer.analyze(prompt, available_providers=["openai"])
            if analysis.task_type == expected_type:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(test_cases)
        assert accuracy > 0.5, f"Pattern matching accuracy too low: {accuracy:.2%}"


class TestTaskAnalysis:
    """Test suite for TaskAnalysis data class"""
    
    def test_task_analysis_creation(self):
        """Test TaskAnalysis object creation"""
        analysis = TaskAnalysis(
            task_type=TaskType.CODING,
            complexity_score=0.75,
            confidence=0.85,
            recommended_model="gpt-5",
            reasoning="Detected coding task with high complexity",
            metadata={"keywords": ["function", "python"], "length": 50}
        )
        
        assert analysis.task_type == TaskType.CODING
        assert analysis.complexity_score == 0.75
        assert analysis.confidence == 0.85
        assert analysis.recommended_model == "gpt-5"
        assert "coding task" in analysis.reasoning
        assert len(analysis.metadata) == 2
    
    def test_task_analysis_validation(self):
        """Test TaskAnalysis validation"""
        # Test with valid values
        valid_analysis = TaskAnalysis(
            task_type=TaskType.ANALYSIS,
            complexity_score=0.5,
            confidence=0.7,
            recommended_model="claude-3-5-sonnet",
            reasoning="Valid analysis"
        )
        
        assert 0.0 <= valid_analysis.complexity_score <= 1.0
        assert 0.0 <= valid_analysis.confidence <= 1.0


class TestTaskType:
    """Test suite for TaskType enum"""
    
    def test_task_type_values(self):
        """Test TaskType enum values"""
        expected_types = [
            "coding", "analysis", "creative", "conversation", 
            "simple", "reasoning", "translation"
        ]
        
        for expected_type in expected_types:
            # Should be able to access by attribute
            task_type = getattr(TaskType, expected_type.upper())
            assert task_type.value == expected_type
    
    def test_task_type_iteration(self):
        """Test TaskType enum iteration"""
        task_types = list(TaskType)
        assert len(task_types) >= 7  # Should have at least 7 task types
        
        # All should have string values
        for task_type in task_types:
            assert isinstance(task_type.value, str)
            assert len(task_type.value) > 0


class TestTaskAnalyzerIntegration:
    """Test suite for task analyzer integration scenarios"""
    
    @pytest.fixture
    def task_analyzer(self):
        return TaskAnalyzer()
    
    def test_realistic_coding_workflow(self, task_analyzer):
        """Test realistic coding workflow analysis"""
        # Simulate a coding session with different types of requests
        coding_requests = [
            "Create a REST API for user management",
            "Debug this authentication error",
            "Write unit tests for the API endpoints", 
            "Optimize database queries for better performance",
            "Add input validation to prevent SQL injection"
        ]
        
        for i, prompt in enumerate(coding_requests):
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "anthropic", "groq"]
            )
            
            # All should be classified as coding
            assert analysis.task_type == TaskType.CODING
            
            # Should recommend appropriate models
            coding_models = ["gpt-5", "gpt-5-mini", "claude-3-5-sonnet", "llama-3.3-70b-versatile"]
            assert any(model in analysis.recommended_model for model in coding_models)
            
            # Complexity should vary based on task
            if "create" in prompt.lower() or "api" in prompt.lower():
                assert analysis.complexity_score > 0.6  # Architecture tasks are complex
            elif "debug" in prompt.lower():
                assert analysis.complexity_score > 0.4  # Debugging is moderately complex
    
    def test_cost_optimization_scenarios(self, task_analyzer):
        """Test cost optimization across different scenarios"""
        scenarios = [
            # High-volume simple tasks - should optimize for cost
            ("Translate 'hello' to Spanish", "cost", ["gpt-5-nano", "llama-3.1-8b-instant"]),
            
            # Critical analysis - should optimize for quality
            ("Analyze the security implications of this system architecture", "quality", ["gpt-5", "claude-opus-4-1"]),
            
            # Real-time chat - should optimize for speed
            ("Hey, how's it going?", "speed", ["mixtral-8x7b-32768", "llama-3.3-70b-versatile"])
        ]
        
        for prompt, optimize_for, expected_models in scenarios:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                optimize_for=optimize_for,
                available_providers=["openai", "anthropic", "groq", "google"]
            )
            
            # Should recommend appropriate model type
            assert any(model in analysis.recommended_model for model in expected_models), \
                f"Expected one of {expected_models}, got {analysis.recommended_model} for prompt: {prompt}"
    
    def test_provider_fallback_scenarios(self, task_analyzer):
        """Test provider fallback scenarios"""
        # Test with preferred provider unavailable
        analysis = task_analyzer.analyze(
            prompt="Write a complex algorithm for graph traversal",
            available_providers=["groq"]  # Only Groq available, but task needs quality
        )
        
        # Should still make reasonable recommendation from available providers
        groq_models = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
        assert any(model in analysis.recommended_model for model in groq_models)
        
        # Should explain the limitation in reasoning
        assert "available" in analysis.reasoning.lower() or "groq" in analysis.reasoning.lower()
    
    def test_progressive_complexity_analysis(self, task_analyzer):
        """Test analysis of progressively complex tasks"""
        complexity_prompts = [
            ("Hi", 0.1),  # Very simple
            ("What is Python?", 0.3),  # Simple
            ("Explain object-oriented programming", 0.5),  # Medium  
            ("Design a scalable microservices architecture", 0.7),  # Complex
            ("Create a distributed consensus algorithm that handles Byzantine failures", 0.9)  # Very complex
        ]
        
        for prompt, expected_min_complexity in complexity_prompts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "anthropic"]
            )
            
            assert analysis.complexity_score >= expected_min_complexity, \
                f"Complexity score {analysis.complexity_score} too low for: {prompt}"
            
            # Higher complexity should generally recommend better models
            if analysis.complexity_score > 0.7:
                quality_models = ["gpt-5", "claude-opus-4-1", "claude-3-5-sonnet"]
                assert any(model in analysis.recommended_model for model in quality_models)
    
    def test_context_awareness(self, task_analyzer):
        """Test context awareness in analysis"""
        # Same action, different contexts should yield different analyses
        contexts = [
            ("Debug this code", TaskType.CODING),
            ("Debug this relationship issue", TaskType.CONVERSATION),
            ("Debug this marketing campaign", TaskType.ANALYSIS)
        ]
        
        for prompt, expected_type in contexts:
            analysis = task_analyzer.analyze(
                prompt=prompt,
                available_providers=["openai", "anthropic"]
            )
            
            # Should classify based on context, not just keyword
            # (This test allows for some flexibility as context detection is challenging)
            if analysis.confidence > 0.6:
                assert analysis.task_type == expected_type, \
                    f"Expected {expected_type} for '{prompt}', got {analysis.task_type}"