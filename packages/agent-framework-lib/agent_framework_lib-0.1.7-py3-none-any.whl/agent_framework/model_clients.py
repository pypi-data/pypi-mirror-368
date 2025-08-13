"""
Multi-Provider Model Client Factory

Creates appropriate model clients (OpenAI, Gemini, etc.) based on model configuration.
"""

import logging
from typing import Any, Dict, Optional, Union
from .model_config import ModelConfigManager, ModelProvider, model_config
from .agent_interface import AgentConfig

logger = logging.getLogger(__name__)

try:
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("[ModelClientFactory] OpenAI client not available")
    OPENAI_AVAILABLE = False

try:
    # Try importing Gemini client - adjust import path as needed
    from autogen_ext.models.gemini import GeminiChatCompletionClient
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("[ModelClientFactory] Gemini client not available, will use OpenAI client for Gemini models")
    GEMINI_AVAILABLE = False

class ModelClientFactory:
    """
    Factory class for creating appropriate model clients based on model names.
    """
    
    def __init__(self, config_manager: ModelConfigManager = None):
        """
        Initialize the client factory.
        
        Args:
            config_manager: Optional ModelConfigManager instance. If None, uses global instance.
        """
        self.config = config_manager or model_config
    
    def create_client(
        self, 
        model_name: str = None, 
        agent_config: AgentConfig = None,
        **override_params
    ) -> Any:
        """
        Create an appropriate model client for the given model.
        
        Args:
            model_name: Name of the model. If None, uses default model.
            agent_config: Optional agent configuration with overrides.
            **override_params: Additional parameters to override defaults.
            
        Returns:
            Configured model client instance.
        """
        # Use default model if none specified
        if not model_name:
            model_name = self.config.default_model
            logger.debug(f"[ModelClientFactory] No model specified, using default: {model_name}")
        
        # Determine provider and get configuration
        provider = self.config.get_provider_for_model(model_name)
        api_key = self.config.get_api_key_for_provider(provider)
        defaults = self.config.get_defaults_for_provider(provider)
        
        logger.debug(f"[ModelClientFactory] Creating client for model '{model_name}':")
        logger.debug(f"  - Provider: {provider.value}")
        logger.debug(f"  - API key configured: {'✓' if api_key else '✗'}")
        logger.debug(f"  - Provider defaults: {defaults}")
        
        if not api_key:
            raise ValueError(f"No API key configured for provider {provider.value} (model: {model_name})")
        
        # Build parameters with precedence: override_params > agent_config > defaults
        params = defaults.copy()
        params.update(override_params)
        
        # Apply agent config overrides if provided
        if agent_config:
            logger.debug(f"[ModelClientFactory] Applying agent configuration overrides:")
            logger.debug(f"  - Agent config: {agent_config.dict(exclude_unset=True)}")
            
            if agent_config.temperature is not None:
                params["temperature"] = agent_config.temperature
                logger.debug(f"  - Temperature override: {agent_config.temperature}")
            if agent_config.timeout is not None:
                params["timeout"] = agent_config.timeout
                logger.debug(f"  - Timeout override: {agent_config.timeout}")
            if agent_config.max_retries is not None:
                params["max_retries"] = agent_config.max_retries
                logger.debug(f"  - Max retries override: {agent_config.max_retries}")
            if agent_config.model_selection is not None:
                old_model = model_name
                model_name = agent_config.model_selection
                logger.debug(f"  - Model override: {old_model} → {model_name}")
                # Re-determine provider if model was overridden
                provider = self.config.get_provider_for_model(model_name)
                api_key = self.config.get_api_key_for_provider(provider)
                logger.debug(f"  - Provider changed to: {provider.value}")
        
        # Add required parameters
        params.update({
            "model": model_name,
            "api_key": api_key
        })
        
        # Create client based on provider
        if provider == ModelProvider.OPENAI:
            return self._create_openai_client(params, agent_config)
        elif provider == ModelProvider.GEMINI:
            return self._create_gemini_client(params, agent_config)
        else:
            logger.warning(f"[ModelClientFactory] Unknown provider {provider}, falling back to OpenAI")
            return self._create_openai_client(params, agent_config)
    
    def _create_openai_client(self, params: Dict[str, Any], agent_config: AgentConfig = None) -> Any:
        """Create an OpenAI client with the given parameters."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI client not available. Please install autogen-ext[openai]")
        
        # Add OpenAI-specific parameters
        client_params = params.copy()
        
        # Add model info for OpenAI
        client_params["model_info"] = {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "openai",
            "structured_output": True,
            "thinking": False
        }
        
        # Apply agent config overrides for OpenAI-specific parameters
        if agent_config:
            extra_params = {}
            if agent_config.max_tokens is not None:
                extra_params["max_tokens"] = agent_config.max_tokens
            if agent_config.top_p is not None:
                extra_params["top_p"] = agent_config.top_p
            if agent_config.frequency_penalty is not None:
                extra_params["frequency_penalty"] = agent_config.frequency_penalty
            if agent_config.presence_penalty is not None:
                extra_params["presence_penalty"] = agent_config.presence_penalty
            if agent_config.stop_sequences is not None:
                extra_params["stop"] = agent_config.stop_sequences
            
            client_params.update(extra_params)
        
        logger.info(f"[ModelClientFactory] Creating OpenAI client for model: {client_params['model']}")
        logger.debug(f"[ModelClientFactory] OpenAI client params: {list(client_params.keys())}")
        
        try:
            return OpenAIChatCompletionClient(**client_params)
        except Exception as e:
            logger.error(f"[ModelClientFactory] Failed to create OpenAI client: {e}")
            # Try with minimal parameters as fallback
            minimal_params = {
                "model": client_params["model"],
                "api_key": client_params["api_key"],
                "temperature": client_params.get("temperature", 0.7),
                "timeout": client_params.get("timeout", 120),
                "max_retries": client_params.get("max_retries", 3),
                "model_info": client_params["model_info"]
            }
            logger.warning(f"[ModelClientFactory] Retrying with minimal parameters")
            return OpenAIChatCompletionClient(**minimal_params)
    
    def _create_gemini_client(self, params: Dict[str, Any], agent_config: AgentConfig = None) -> Any:
        """Create a Gemini client with the given parameters."""
        if GEMINI_AVAILABLE:
            # TODO: Implement Gemini client creation when available
            logger.info(f"[ModelClientFactory] Creating Gemini client for model: {params['model']}")
            # For now, this would create a GeminiChatCompletionClient
            # return GeminiChatCompletionClient(**params)
            pass
        
        # Fallback to OpenAI client for Gemini models, but filter unsupported parameters
        logger.warning(f"[ModelClientFactory] Gemini client not available, using OpenAI client as fallback")
        logger.warning(f"[ModelClientFactory] Filtering out Gemini-unsupported parameters")
        
        # Filter out parameters that Gemini doesn't support
        gemini_compatible_params = self._filter_params_for_gemini(params, agent_config)
        return self._create_openai_client_for_gemini(gemini_compatible_params)
    
    def _filter_params_for_gemini(self, params: Dict[str, Any], agent_config: AgentConfig = None) -> Dict[str, Any]:
        """Filter out parameters that Gemini API doesn't support."""
        # Gemini-compatible base parameters
        filtered_params = {
            "model": params["model"],
            "api_key": params["api_key"],
            "temperature": params.get("temperature", 0.7),
            "timeout": params.get("timeout", 120),
            "max_retries": params.get("max_retries", 3)
        }
        
        # Add max_tokens if available (Gemini supports this)
        if agent_config and agent_config.max_tokens is not None:
            filtered_params["max_tokens"] = agent_config.max_tokens
        
        # Add top_p if available (Gemini supports this)
        if agent_config and agent_config.top_p is not None:
            filtered_params["top_p"] = agent_config.top_p
        
        # Add stop sequences if available (Gemini supports this)
        if agent_config and agent_config.stop_sequences is not None:
            filtered_params["stop"] = agent_config.stop_sequences
        
        # Log filtered out parameters
        unsupported = []
        if agent_config:
            if agent_config.frequency_penalty is not None:
                unsupported.append("frequency_penalty")
            if agent_config.presence_penalty is not None:
                unsupported.append("presence_penalty")
        
        if unsupported:
            logger.warning(f"[ModelClientFactory] Filtered out Gemini-unsupported parameters: {unsupported}")
        
        return filtered_params
    
    def _create_openai_client_for_gemini(self, params: Dict[str, Any]) -> Any:
        """Create OpenAI client for Gemini models with filtered parameters."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI client not available. Please install autogen-ext[openai]")
        
        # Add model info for Gemini (using OpenAI client as proxy)
        client_params = params.copy()
        client_params["model_info"] = {
            "vision": False,
            "function_calling": True, 
            "json_output": True,
            "family": "gemini",  # Mark as gemini family
            "structured_output": True,
            "thinking": False
        }
        
        logger.info(f"[ModelClientFactory] Creating OpenAI client (Gemini proxy) for model: {client_params['model']}")
        logger.debug(f"[ModelClientFactory] Gemini-compatible params: {list(client_params.keys())}")
        
        try:
            return OpenAIChatCompletionClient(**client_params)
        except Exception as e:
            logger.error(f"[ModelClientFactory] Failed to create Gemini-compatible client: {e}")
            # Try with minimal parameters as fallback
            minimal_params = {
                "model": client_params["model"],
                "api_key": client_params["api_key"],
                "temperature": client_params.get("temperature", 0.7),
                "timeout": client_params.get("timeout", 120),
                "max_retries": client_params.get("max_retries", 3),
                "model_info": client_params["model_info"]
            }
            logger.warning(f"[ModelClientFactory] Retrying with minimal parameters for Gemini")
            return OpenAIChatCompletionClient(**minimal_params)
    
    def get_supported_providers(self) -> Dict[str, bool]:
        """
        Get information about which providers are available.
        
        Returns:
            Dictionary mapping provider names to availability status.
        """
        return {
            "openai": OPENAI_AVAILABLE,
            "gemini": GEMINI_AVAILABLE
        }
    
    def validate_model_support(self, model_name: str) -> Dict[str, Any]:
        """
        Validate if a model is supported and properly configured.
        
        Args:
            model_name: The model name to validate.
            
        Returns:
            Dictionary with validation results.
        """
        provider = self.config.get_provider_for_model(model_name)
        api_key = self.config.get_api_key_for_provider(provider)
        
        result = {
            "model": model_name,
            "provider": provider.value,
            "supported": False,
            "api_key_configured": bool(api_key),
            "client_available": False,
            "issues": []
        }
        
        # Check if client is available
        if provider == ModelProvider.OPENAI and OPENAI_AVAILABLE:
            result["client_available"] = True
        elif provider == ModelProvider.GEMINI and GEMINI_AVAILABLE:
            result["client_available"] = True
        else:
            result["issues"].append(f"Client for {provider.value} not available")
        
        # Check API key
        if not api_key:
            result["issues"].append(f"API key for {provider.value} not configured")
        
        # Overall support
        result["supported"] = result["client_available"] and result["api_key_configured"]
        
        return result

# Global factory instance
client_factory = ModelClientFactory() 