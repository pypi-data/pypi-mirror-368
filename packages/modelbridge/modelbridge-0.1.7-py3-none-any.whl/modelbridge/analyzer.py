"""
Intelligent Task Analyzer for Smart Model Routing
Analyzes prompts to determine optimal model selection automatically
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TaskAnalysis:
    """Result of prompt analysis"""
    recommended_model: str
    confidence: float  # 0.0 to 1.0
    task_type: str
    complexity_score: int
    reasoning: str
    estimated_cost: float
    estimated_speed: str  # "fast", "medium", "slow"


class TaskAnalyzer:
    """Analyzes prompts to determine optimal model routing"""
    
    def __init__(self):
        # Task type indicators
        self.task_patterns = {
            "coding": [
                r"\b(function|code|implement|debug|class|def|python|javascript|java|c\+\+|rust|go)\b",
                r"\b(algorithm|programming|script|syntax|bug|error|compile)\b",
                r"\b(api|database|sql|query|frontend|backend|framework)\b",
                r"\b(write.*code|create.*function|build.*app|fix.*bug)\b"
            ],
            "analysis": [
                r"\b(analyze|examine|evaluate|assess|review|compare|study)\b",
                r"\b(data|statistics|research|report|findings|insights)\b",
                r"\b(pros.*cons|advantages.*disadvantages|benefits.*risks)\b",
                r"\b(summarize|explain.*detail|break.*down|deep.*dive)\b"
            ],
            "creative": [
                r"\b(write|create|design|compose|generate|craft)\b.*\b(story|poem|article|content|copy)\b",
                r"\b(creative|artistic|imaginative|original|innovative)\b",
                r"\b(blog.*post|social.*media|marketing.*copy|advertisement)\b",
                r"\b(brainstorm|ideate|concept|inspiration)\b"
            ],
            "simple": [
                r"^(what is|define|who is|when did|where is|how many)\b",
                r"^(yes.*no|true.*false|\d+\s*[\+\-\*\/]\s*\d+)\b",
                r"^.{1,20}[?]?$",  # Very short queries
                r"\b(quick.*question|simple.*answer|just.*tell.*me)\b"
            ],
            "reasoning": [
                r"\b(solve|calculate|prove|derive|logic|reasoning|mathematical)\b",
                r"\b(step.*by.*step|explain.*how|show.*work|proof)\b",
                r"\b(math|physics|chemistry|economics|philosophy)\b",
                r"\b(problem|equation|formula|theorem|hypothesis)\b"
            ],
            "translation": [
                r"\b(translate|convert.*to|in\s+(spanish|french|german|chinese|japanese))\b",
                r"\b(language|français|español|deutsch|中文|日本語)\b",
                r"(from|to)\s+(english|spanish|french|german|chinese|japanese)",
                r"\b(localization|i18n|multilingual)\b"
            ],
            "conversation": [
                r"\b(chat|talk|discuss|conversation|dialogue)\b",
                r"^(hi|hello|hey|good.*morning|how.*are.*you)",
                r"\b(tell.*me.*about|what.*do.*you.*think|your.*opinion)\b",
                r"\b(friendly|casual|personal|relationship)\b"
            ]
        }
        
        # Complexity indicators
        self.complexity_patterns = {
            "high": [
                r"\b(complex|complicated|detailed|comprehensive|thorough|extensive)\b",
                r"\b(multi-step|step.*by.*step|detailed.*analysis|in-depth)\b",
                r"\b(research|academic|technical|professional|enterprise)\b",
                r".{500,}",  # Very long prompts
            ],
            "medium": [
                r"\b(explain|describe|outline|overview|summary)\b",
                r"\b(moderate|balanced|standard|typical|normal)\b",
                r".{100,499}",  # Medium length prompts
            ],
            "low": [
                r"\b(quick|simple|basic|easy|brief|short)\b",
                r"\b(yes.*no|true.*false|list|name|define)\b",
                r"^.{1,99}$",  # Short prompts
            ]
        }
        
        # Model capabilities and costs (per 1M input tokens)
        self.model_profiles = {
            # OpenAI GPT-5 Family
            "gpt-5": {
                "strengths": ["coding", "reasoning", "analysis"],
                "cost": 1.25,
                "speed": "medium",
                "context_length": 272000,
                "quality_score": 95
            },
            "gpt-5-mini": {
                "strengths": ["general", "conversation", "analysis"],
                "cost": 0.25,
                "speed": "fast", 
                "context_length": 272000,
                "quality_score": 88
            },
            "gpt-5-nano": {
                "strengths": ["simple", "conversation", "translation"],
                "cost": 0.05,
                "speed": "fastest",
                "context_length": 272000, 
                "quality_score": 75
            },
            
            # Anthropic Claude 4
            "claude-opus-4-1": {
                "strengths": ["analysis", "reasoning", "creative"],
                "cost": 15.00,
                "speed": "slow",
                "context_length": 200000,
                "quality_score": 97
            },
            "claude-sonnet-4": {
                "strengths": ["analysis", "conversation", "coding"],
                "cost": 3.00,
                "speed": "medium",
                "context_length": 200000,
                "quality_score": 90
            },
            
            # Google Gemini 2.5
            "gemini-2.5-flash": {
                "strengths": ["simple", "conversation", "general"],
                "cost": 0.075,
                "speed": "fastest",
                "context_length": 1000000,
                "quality_score": 82
            },
            
            # Groq (Ultra-fast)
            "mixtral-8x7b-32768": {
                "strengths": ["simple", "conversation", "coding"],
                "cost": 0.27,
                "speed": "lightning",
                "context_length": 32768,
                "quality_score": 80
            },
            "llama-3.3-70b-versatile": {
                "strengths": ["general", "conversation", "analysis"],
                "cost": 0.59,
                "speed": "lightning",
                "context_length": 32768,
                "quality_score": 85
            }
        }

    def analyze(
        self, 
        prompt: str, 
        optimize_for: Optional[str] = None,
        max_cost: Optional[float] = None,
        available_providers: Optional[List[str]] = None
    ) -> TaskAnalysis:
        """
        Analyze prompt and return optimal model recommendation
        
        Args:
            prompt: The input prompt to analyze
            optimize_for: "speed", "cost", "quality", or None for balanced
            max_cost: Maximum cost per 1M input tokens (optional)
            available_providers: List of available providers (optional)
        
        Returns:
            TaskAnalysis with model recommendation and reasoning
        """
        
        # Basic prompt analysis
        word_count = len(prompt.split())
        char_count = len(prompt)
        
        # Detect task type
        task_type, task_confidence = self._detect_task_type(prompt)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(prompt, word_count, char_count)
        
        # Get candidate models
        candidates = self._get_candidate_models(
            task_type, 
            complexity_score,
            available_providers or []
        )
        
        # Apply optimization preferences
        recommended_model = self._select_optimal_model(
            candidates,
            optimize_for,
            max_cost,
            complexity_score,
            task_type
        )
        
        # Calculate estimates
        model_profile = self.model_profiles[recommended_model]
        estimated_cost = (model_profile["cost"] * char_count) / 1000000  # Rough estimate
        
        reasoning = self._generate_reasoning(
            recommended_model,
            task_type,
            complexity_score,
            optimize_for
        )
        
        return TaskAnalysis(
            recommended_model=recommended_model,
            confidence=task_confidence,
            task_type=task_type,
            complexity_score=complexity_score,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_speed=model_profile["speed"]
        )

    def _detect_task_type(self, prompt: str) -> Tuple[str, float]:
        """Detect the primary task type from prompt"""
        prompt_lower = prompt.lower()
        
        task_scores = {}
        for task_type, patterns in self.task_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    matches += 1
                    score += 1
            
            # Boost score for multiple pattern matches
            if matches > 1:
                score *= 1.5
                
            task_scores[task_type] = score
        
        # Find the highest scoring task type
        if not task_scores or max(task_scores.values()) == 0:
            return "general", 0.3
            
        best_task = max(task_scores, key=task_scores.get)
        max_score = task_scores[best_task]
        
        # Calculate confidence (0.0 to 1.0)
        total_score = sum(task_scores.values())
        confidence = min(0.95, max_score / max(total_score, 1) + 0.3)
        
        return best_task, confidence

    def _calculate_complexity(self, prompt: str, word_count: int, char_count: int) -> int:
        """Calculate complexity score (0-10)"""
        score = 0
        prompt_lower = prompt.lower()
        
        # Length-based scoring
        if word_count > 200:
            score += 3
        elif word_count > 50:
            score += 2
        elif word_count > 20:
            score += 1
            
        # Pattern-based scoring
        for complexity_level, patterns in self.complexity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    if complexity_level == "high":
                        score += 3
                    elif complexity_level == "medium":
                        score += 1
                    # Low complexity doesn't add score
                    break
        
        # Additional complexity indicators
        if "step by step" in prompt_lower or "detailed" in prompt_lower:
            score += 2
        if prompt.count("?") > 2:  # Multiple questions
            score += 1
        if re.search(r'\b(and|also|additionally|furthermore|moreover)\b', prompt_lower):
            score += 1  # Multiple requirements
            
        return min(10, score)  # Cap at 10

    def _get_candidate_models(
        self, 
        task_type: str, 
        complexity_score: int,
        available_providers: List[str]
    ) -> List[str]:
        """Get candidate models based on task type and complexity"""
        
        candidates = []
        
        # Filter by available providers if specified
        available_models = list(self.model_profiles.keys())
        if available_providers:
            available_models = [
                model for model in available_models 
                if any(provider in model for provider in available_providers)
            ]
        
        # Score each model for this task
        for model, profile in self.model_profiles.items():
            if model not in available_models:
                continue
                
            score = 0
            
            # Task type alignment
            if task_type in profile["strengths"]:
                score += 5
            elif "general" in profile["strengths"]:
                score += 2
                
            # Complexity alignment
            if complexity_score >= 7:  # High complexity
                if profile["quality_score"] >= 90:
                    score += 3
            elif complexity_score <= 3:  # Low complexity  
                if profile["speed"] in ["fastest", "lightning"]:
                    score += 2
            else:  # Medium complexity
                score += 1  # All models viable
                
            if score > 0:
                candidates.append((model, score))
        
        # Sort by score and return model names
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [model for model, score in candidates]

    def _select_optimal_model(
        self,
        candidates: List[str],
        optimize_for: Optional[str],
        max_cost: Optional[float],
        complexity_score: int,
        task_type: str
    ) -> str:
        """Select the optimal model from candidates"""
        
        if not candidates:
            return "gpt-5-mini"  # Safe fallback
            
        # Apply cost constraint first
        if max_cost:
            candidates = [
                model for model in candidates
                if self.model_profiles[model]["cost"] <= max_cost
            ]
            if not candidates:
                # Return cheapest available model
                return min(self.model_profiles.keys(), 
                          key=lambda m: self.model_profiles[m]["cost"])
        
        # Apply optimization preference
        if optimize_for == "speed":
            # Sort by speed (fastest first)
            speed_order = {"lightning": 4, "fastest": 3, "fast": 2, "medium": 1, "slow": 0}
            candidates.sort(
                key=lambda m: speed_order.get(self.model_profiles[m]["speed"], 0),
                reverse=True
            )
        elif optimize_for == "cost":
            # Sort by cost (cheapest first)
            candidates.sort(key=lambda m: self.model_profiles[m]["cost"])
        elif optimize_for == "quality":
            # Sort by quality score (highest first)
            candidates.sort(
                key=lambda m: self.model_profiles[m]["quality_score"],
                reverse=True
            )
        # else: use default candidate order (already sorted by task fit)
        
        return candidates[0]

    def _generate_reasoning(
        self,
        model: str,
        task_type: str,
        complexity_score: int,
        optimize_for: Optional[str]
    ) -> str:
        """Generate human-readable reasoning for the model choice"""
        
        profile = self.model_profiles[model]
        reasons = []
        
        # Task type reasoning
        if task_type in profile["strengths"]:
            reasons.append(f"Excellent for {task_type} tasks")
        elif task_type == "general":
            reasons.append("General-purpose task")
        else:
            reasons.append(f"Suitable for {task_type} tasks")
            
        # Complexity reasoning
        if complexity_score >= 7:
            reasons.append("High complexity requires capable model")
        elif complexity_score <= 3:
            reasons.append("Simple task allows for faster/cheaper model")
        else:
            reasons.append("Medium complexity task")
            
        # Optimization reasoning
        if optimize_for == "speed":
            reasons.append(f"Optimized for speed ({profile['speed']})")
        elif optimize_for == "cost":
            reasons.append(f"Cost-optimized (${profile['cost']}/1M tokens)")
        elif optimize_for == "quality":
            reasons.append(f"Quality-optimized (score: {profile['quality_score']})")
        else:
            reasons.append("Balanced choice")
            
        return " • ".join(reasons)