"""
Validation utilities for ModelBridge
"""
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class APIKeyValidator:
    """Validates API keys for different providers"""
    
    # API key patterns for validation
    KEY_PATTERNS = {
        "openai": {
            "pattern": r"^sk-[a-zA-Z0-9]{48}$|^sk-proj-[a-zA-Z0-9]{48}$",
            "description": "OpenAI API key should start with 'sk-' or 'sk-proj-' followed by 48 characters"
        },
        "anthropic": {
            "pattern": r"^sk-ant-[a-zA-Z0-9]{95}$",
            "description": "Anthropic API key should start with 'sk-ant-' followed by 95 characters"
        },
        "google": {
            "pattern": r"^[a-zA-Z0-9_-]{39}$",
            "description": "Google API key should be 39 characters long"
        },
        "groq": {
            "pattern": r"^gsk_[a-zA-Z0-9]{52}$",
            "description": "Groq API key should start with 'gsk_' followed by 52 characters"
        }
    }
    
    @classmethod
    def validate_api_key(cls, provider: str, api_key: str, skip_format_check: bool = False) -> tuple[bool, Optional[str]]:
        """
        Validate API key format for a provider
        
        Args:
            provider: Provider name (openai, anthropic, google, groq)
            api_key: API key to validate
            skip_format_check: Skip format validation (for testing)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key:
            return False, "API key is required"
        
        # Strip whitespace
        api_key = api_key.strip()
        
        # Allow test keys in test/development mode
        if api_key.startswith("test-") or api_key == "test_key" or skip_format_check:
            return True, None
        
        # Check if provider is supported
        provider_lower = provider.lower()
        if provider_lower not in cls.KEY_PATTERNS:
            # Unknown provider - basic validation only
            if len(api_key) < 10:
                return False, "API key seems too short"
            return True, None
        
        # Get pattern for provider
        key_info = cls.KEY_PATTERNS[provider_lower]
        pattern = key_info["pattern"]
        
        # Validate against pattern
        if re.match(pattern, api_key):
            return True, None
        else:
            return False, key_info["description"]
    
    @classmethod
    def validate_all_keys(cls, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate all API keys in configuration
        
        Args:
            config: Configuration dictionary with providers
            
        Returns:
            Dictionary of validation errors (empty if all valid)
        """
        errors = {}
        
        providers = config.get("providers", {})
        for provider_name, provider_config in providers.items():
            if not provider_config.get("enabled", True):
                continue
                
            api_key = provider_config.get("api_key")
            if api_key:
                is_valid, error_msg = cls.validate_api_key(provider_name, api_key)
                if not is_valid:
                    errors[provider_name] = error_msg
                    logger.warning(f"Invalid API key format for {provider_name}: {error_msg}")
        
        return errors
    
    @classmethod
    def sanitize_api_key(cls, api_key: str) -> str:
        """
        Sanitize API key for logging (show only first/last few chars)
        
        Args:
            api_key: API key to sanitize
            
        Returns:
            Sanitized version safe for logging
        """
        if not api_key or len(api_key) < 10:
            return "***"
        
        # Show first 4 and last 4 characters
        return f"{api_key[:4]}...{api_key[-4:]}"


class ResponseValidator:
    """Validates and handles malformed responses"""
    
    @staticmethod
    def validate_openai_response(response: Any) -> tuple[bool, Optional[str]]:
        """
        Validate OpenAI API response format
        
        Args:
            response: Response object from OpenAI
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check basic structure
            if not hasattr(response, 'choices'):
                return False, "Response missing 'choices' field"
            
            if not response.choices:
                return False, "Response has empty 'choices' array"
            
            # Check first choice
            first_choice = response.choices[0]
            if not hasattr(first_choice, 'message'):
                return False, "Choice missing 'message' field"
            
            # Check message content
            if not hasattr(first_choice.message, 'content'):
                return False, "Message missing 'content' field"
            
            # Check usage data if present
            if hasattr(response, 'usage'):
                usage = response.usage
                required_fields = ['prompt_tokens', 'completion_tokens', 'total_tokens']
                for field in required_fields:
                    if not hasattr(usage, field):
                        return False, f"Usage missing '{field}' field"
            
            return True, None
            
        except Exception as e:
            return False, f"Response validation error: {str(e)}"
    
    @staticmethod
    def validate_anthropic_response(response: Any) -> tuple[bool, Optional[str]]:
        """
        Validate Anthropic API response format
        
        Args:
            response: Response object from Anthropic
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check basic structure
            if not hasattr(response, 'content'):
                return False, "Response missing 'content' field"
            
            if not response.content:
                return False, "Response has empty 'content' array"
            
            # Check first content block
            first_content = response.content[0]
            if not hasattr(first_content, 'text'):
                return False, "Content missing 'text' field"
            
            # Check usage data if present
            if hasattr(response, 'usage'):
                usage = response.usage
                required_fields = ['input_tokens', 'output_tokens']
                for field in required_fields:
                    if not hasattr(usage, field):
                        return False, f"Usage missing '{field}' field"
            
            return True, None
            
        except Exception as e:
            return False, f"Response validation error: {str(e)}"
    
    @staticmethod
    def extract_safe_content(response: Any, provider: str) -> Optional[str]:
        """
        Safely extract content from potentially malformed response
        
        Args:
            response: Response object
            provider: Provider name
            
        Returns:
            Extracted content or None
        """
        try:
            if provider.lower() == "openai":
                if hasattr(response, 'choices') and response.choices:
                    choice = response.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        return choice.message.content
                    elif hasattr(choice, 'text'):
                        return choice.text
            
            elif provider.lower() == "anthropic":
                if hasattr(response, 'content') and response.content:
                    content = response.content[0]
                    if hasattr(content, 'text'):
                        return content.text
            
            # Generic extraction attempts
            if hasattr(response, 'text'):
                return response.text
            if hasattr(response, 'content'):
                if isinstance(response.content, str):
                    return response.content
                elif isinstance(response.content, list) and response.content:
                    return str(response.content[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract content from response: {e}")
            return None