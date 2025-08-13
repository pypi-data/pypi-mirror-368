"""
Agent Framework Library

@AGENT: Describe here what the framework is all about!!!

Generated on: 2025-07-02 15:21:00 CET
"""

import logging
import os

# Create logger for this module
logger = logging.getLogger(__name__)

__version__ = "0.1.0"
__author__ = "Cinco AI Team"

# Core interfaces and base classes
from .agent_interface import (
    AgentInterface,
    StructuredAgentInput,
    StructuredAgentOutput,
    AgentConfig,
    # Input part types
    TextInputPart,
    ImageUrlInputPart,
    FileDataInputPart,
    AgentInputPartUnion,
    # Output part types
    TextOutputPart,
    TextOutputStreamPart,
    JsonOutputPart,
    YamlOutputPart,
    FileContentOutputPart,
    MermaidOutputPart,
    ChartJsOutputPart,
    TableDataOutputPart,
    FormDefinitionOutputPart,
    OptionsBlockOutputPart,
    AgentOutputPartUnion,
)

# AutoGen-based agent base class
from .autogen_based_agent import AutoGenBasedAgent

# Model configuration and clients
from .model_config import ModelConfigManager, ModelProvider, model_config
from .model_clients import ModelClientFactory, client_factory

# Session storage
from .session_storage import (
    SessionStorageInterface,
    SessionStorageFactory,
    SessionData,
    MessageData,
    MessageInsight,
    MessageMetadata,
    AgentLifecycleData,
    MemorySessionStorage,
    MongoDBSessionStorage,
    history_message_to_message_data,
    message_data_to_history_message,
)

# Server application
from .server import app, start_server

# Convenience imports for common use cases
__all__ = [
    # Version info
    "__version__",
    "__author__",
    
    # Core interfaces
    "AgentInterface",
    "StructuredAgentInput", 
    "StructuredAgentOutput",
    "AgentConfig",
    
    # Base implementations
    "AutoGenBasedAgent",
    
    # Input/Output types
    "TextInputPart",
    "ImageUrlInputPart", 
    "FileDataInputPart",
    "AgentInputPartUnion",
    "TextOutputPart",
    "TextOutputStreamPart",
    "JsonOutputPart",
    "YamlOutputPart", 
    "FileContentOutputPart",
    "MermaidOutputPart",
    "ChartJsOutputPart",
    "TableDataOutputPart",
    "FormDefinitionOutputPart",
    "OptionsBlockOutputPart",
    "AgentOutputPartUnion",
    
    # Model configuration
    "ModelConfigManager",
    "ModelProvider", 
    "model_config",
    "ModelClientFactory",
    "client_factory",
    
    # Session storage
    "SessionStorageInterface",
    "SessionStorageFactory",
    "SessionData",
    "MessageData",
    "MessageInsight", 
    "MessageMetadata",
    "AgentLifecycleData",
    "MemorySessionStorage",
    "MongoDBSessionStorage",
    "history_message_to_message_data",
    "message_data_to_history_message",
    
    # Server
    "app",
    "start_server",
    
    # Convenience functions
    "create_basic_agent_server",
]

# Quick start function for convenience
def create_basic_agent_server(agent_class, host="0.0.0.0", port=8000, reload=False):
    """
    Quick start function to create and run an agent server.
    
    This function allows external projects to quickly start an agent server
    without needing to create their own server.py file or set environment variables.
    
    Args:
        agent_class: The agent class that implements AgentInterface
        host: Host to bind the server to (default: "0.0.0.0")
        port: Port to run the server on (default: 8000)
        reload: Whether to enable auto-reload for development (default: False)
                Note: When reload=True, the agent class is temporarily stored in an 
                environment variable to survive module reloads.
    
    Returns:
        None (starts the server and blocks)
    
    Example:
        >>> from agent_framework import create_basic_agent_server
        >>> from my_agent import MyAgent
        >>> create_basic_agent_server(MyAgent, port=8001)
    """
    import uvicorn
    
    # Store the agent class globally for immediate use
    from . import server
    server._GLOBAL_AGENT_CLASS = agent_class
    
    # If reload is enabled, also store in environment variable to survive reloads
    # We use the class's module and name to recreate the import path
    if reload:
        module_name = agent_class.__module__
        class_name = agent_class.__name__
        agent_class_path = f"{module_name}:{class_name}"
        os.environ["AGENT_CLASS_PATH"] = agent_class_path
        logger.info(f"[create_basic_agent_server] Reload enabled. Set AGENT_CLASS_PATH={agent_class_path}")
    
    logger.info(f"[create_basic_agent_server] Starting server for {agent_class.__name__} on {host}:{port}")
    logger.info(f"[create_basic_agent_server] Reload: {reload}")
    
    # When reload=True, uvicorn requires an import string, not the app object directly
    if reload:
        # Use the agent_framework.server:app import string for reload mode
        uvicorn.run(
            "agent_framework.server:app",
            host=host,
            port=port,
            reload=reload
        )
    else:
        # Import the app after setting the global variable for non-reload mode
        from .server import app
        # For non-reload mode, we can pass the app object directly
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload
        ) 