"""
Multi-Provider Model Configuration Manager

Handles configuration for multiple AI providers (OpenAI, Gemini, etc.)
and automatically selects the correct client based on the model name.
"""

import os
import logging
from typing import Dict, List, Optional, Union, Any
from enum import Enum

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    pass  # dotenv not available, skip

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """Supported model providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    UNKNOWN = "unknown"

class ModelConfigManager:
    """
    Manages configuration for multiple AI model providers.
    Automatically determines the correct provider and API key based on model name.
    """
    
    # Default model mappings (can be overridden by environment variables)
    DEFAULT_OPENAI_MODELS = [
        "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
        "gpt-3.5-turbo", "gpt-3.5-turbo-16k",
        "o1-preview", "o1-mini"
    ]
    
    DEFAULT_GEMINI_MODELS = [
        "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp",
        "gemini-2.5-flash-preview-04-17", "gemini-pro", "gemini-pro-vision"
    ]
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables."""
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        # Default model
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4")
        
        # Model mappings from environment (with fallbacks to defaults)
        openai_models_str = os.getenv("OPENAI_MODELS", "")
        gemini_models_str = os.getenv("GEMINI_MODELS", "")
        
        self.openai_models = (
            [m.strip() for m in openai_models_str.split(",") if m.strip()]
            if openai_models_str else self.DEFAULT_OPENAI_MODELS
        )
        
        self.gemini_models = (
            [m.strip() for m in gemini_models_str.split(",") if m.strip()]
            if gemini_models_str else self.DEFAULT_GEMINI_MODELS
        )
        
        # Fallback provider
        fallback_str = os.getenv("FALLBACK_PROVIDER", "openai").lower()
        self.fallback_provider = ModelProvider.OPENAI if fallback_str == "openai" else ModelProvider.GEMINI
        
        # Default parameters
        self.openai_defaults = {
            "temperature": float(os.getenv("OPENAI_DEFAULT_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("OPENAI_DEFAULT_TIMEOUT", "120")),
            "max_retries": int(os.getenv("OPENAI_DEFAULT_MAX_RETRIES", "3"))
        }
        
        self.gemini_defaults = {
            "temperature": float(os.getenv("GEMINI_DEFAULT_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("GEMINI_DEFAULT_TIMEOUT", "120")),
            "max_retries": int(os.getenv("GEMINI_DEFAULT_MAX_RETRIES", "3"))
        }
        
        logger.info(f"[ModelConfigManager] Loaded configuration:")
        logger.info(f"  - Default model: {self.default_model}")
        logger.info(f"  - OpenAI models: {len(self.openai_models)} configured")
        logger.info(f"  - Gemini models: {len(self.gemini_models)} configured") 
        logger.info(f"  - Fallback provider: {self.fallback_provider.value}")
        
        # DEBUG logging for detailed configuration
        logger.debug(f"[ModelConfigManager] Detailed configuration:")
        logger.debug(f"  - OpenAI API key configured: {'✓' if self.openai_api_key else '✗'}")
        logger.debug(f"  - Gemini API key configured: {'✓' if self.gemini_api_key else '✗'}")
        logger.debug(f"  - OpenAI models: {self.openai_models}")
        logger.debug(f"  - Gemini models: {self.gemini_models}")
        logger.debug(f"  - OpenAI defaults: {self.openai_defaults}")
        logger.debug(f"  - Gemini defaults: {self.gemini_defaults}")
    
    def get_provider_for_model(self, model_name: str) -> ModelProvider:
        """
        Determine the provider for a given model name.
        
        Args:
            model_name: The name of the model
            
        Returns:
            ModelProvider enum indicating the provider
        """
        if not model_name:
            logger.debug(f"[ModelConfigManager] Empty model name, using fallback provider: {self.fallback_provider.value}")
            return self.fallback_provider
        
        model_lower = model_name.lower()
        
        # Check OpenAI models
        for openai_model in self.openai_models:
            if model_lower == openai_model.lower():
                logger.debug(f"[ModelConfigManager] Model '{model_name}' matched OpenAI model '{openai_model}'")
                return ModelProvider.OPENAI
        
        # Check Gemini models  
        for gemini_model in self.gemini_models:
            if model_lower == gemini_model.lower():
                logger.debug(f"[ModelConfigManager] Model '{model_name}' matched Gemini model '{gemini_model}'")
                return ModelProvider.GEMINI
        
        # Pattern-based detection as fallback
        if any(pattern in model_lower for pattern in ["gpt", "o1"]):
            logger.debug(f"[ModelConfigManager] Model '{model_name}' matched OpenAI pattern")
            return ModelProvider.OPENAI
        elif any(pattern in model_lower for pattern in ["gemini", "bison", "gecko"]):
            logger.debug(f"[ModelConfigManager] Model '{model_name}' matched Gemini pattern")
            return ModelProvider.GEMINI
        
        logger.warning(f"[ModelConfigManager] Unknown model '{model_name}', using fallback provider: {self.fallback_provider.value}")
        return self.fallback_provider
    
    def get_api_key_for_provider(self, provider: ModelProvider) -> str:
        """
        Get the API key for a specific provider.
        
        Args:
            provider: The provider to get the API key for
            
        Returns:
            The API key string
        """
        if provider == ModelProvider.OPENAI:
            return self.openai_api_key
        elif provider == ModelProvider.GEMINI:
            return self.gemini_api_key
        else:
            logger.warning(f"[ModelConfigManager] Unknown provider: {provider}")
            return ""
    
    def get_api_key_for_model(self, model_name: str) -> str:
        """
        Get the appropriate API key for a given model.
        
        Args:
            model_name: The name of the model
            
        Returns:
            The appropriate API key
        """
        provider = self.get_provider_for_model(model_name)
        return self.get_api_key_for_provider(provider)
    
    def get_defaults_for_provider(self, provider: ModelProvider) -> Dict[str, Any]:
        """
        Get default parameters for a specific provider.
        
        Args:
            provider: The provider to get defaults for
            
        Returns:
            Dictionary of default parameters
        """
        if provider == ModelProvider.OPENAI:
            return self.openai_defaults.copy()
        elif provider == ModelProvider.GEMINI:
            return self.gemini_defaults.copy()
        else:
            return self.openai_defaults.copy()  # Fallback to OpenAI defaults
    
    def get_defaults_for_model(self, model_name: str) -> Dict[str, Any]:
        """
        Get default parameters for a given model.
        
        Args:
            model_name: The name of the model
            
        Returns:
            Dictionary of default parameters
        """
        provider = self.get_provider_for_model(model_name)
        return self.get_defaults_for_provider(provider)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return status.
        
        Returns:
            Dictionary with validation results
        """
        status = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "providers": {}
        }
        
        # Check API keys
        if not self.openai_api_key:
            status["warnings"].append("OpenAI API key not configured")
        else:
            status["providers"]["openai"] = "configured"
        
        if not self.gemini_api_key:
            status["warnings"].append("Gemini API key not configured") 
        else:
            status["providers"]["gemini"] = "configured"
        
        if not self.openai_api_key and not self.gemini_api_key:
            status["valid"] = False
            status["errors"].append("No API keys configured")
        
        # Check default model
        default_provider = self.get_provider_for_model(self.default_model)
        default_key = self.get_api_key_for_provider(default_provider)
        if not default_key:
            status["valid"] = False
            status["errors"].append(f"Default model '{self.default_model}' requires {default_provider.value} API key which is not configured")
        
        return status
    
    def get_model_list(self) -> Dict[str, List[str]]:
        """
        Get all configured models by provider.
        
        Returns:
            Dictionary mapping provider names to model lists
        """
        return {
            "openai": self.openai_models.copy(),
            "gemini": self.gemini_models.copy()
        }

# Global instance
model_config = ModelConfigManager() 