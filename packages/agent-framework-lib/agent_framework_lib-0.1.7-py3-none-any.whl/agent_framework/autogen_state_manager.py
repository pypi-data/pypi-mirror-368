"""
AutoGen State Management

This module provides functionalities for managing the state of AutoGen-based agents,
including serialization, compression, and truncation. This is separated from the generic
session storage to keep concerns separate.
"""

import os
import json
import logging
import asyncio
import uuid
import gzip
import sys
import hashlib
import time
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Import AgentInterface for type hinting without creating circular dependencies
from .agent_interface import AgentInterface

logger = logging.getLogger(__name__)

# Configuration for state management, can be overridden by a config file
try:
    from ..docs.mongodb_state_config import (
        MAX_STATE_SIZE_MB, MAX_CONVERSATION_HISTORY, ENABLE_STATE_COMPRESSION,
        COMPRESSION_THRESHOLD_MB, COMPRESSION_EFFICIENCY_THRESHOLD,
        AGGRESSIVE_TRUNCATION_THRESHOLD
    )
except ImportError:
    # Fallback configuration if config file is not available
    MAX_STATE_SIZE_MB = 12
    MAX_CONVERSATION_HISTORY = 100
    ENABLE_STATE_COMPRESSION = True
    COMPRESSION_THRESHOLD_MB = 1.0
    COMPRESSION_EFFICIENCY_THRESHOLD = 0.8
    AGGRESSIVE_TRUNCATION_THRESHOLD = 20


@dataclass
class AgentIdentity:
    """Complete agent identity information"""
    agent_id: str
    agent_type: str
    agent_class: str
    agent_module: str
    created_at: str
    version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure created_at is set if not provided"""
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AgentIdentity to dictionary for serialization"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "agent_class": self.agent_class,
            "agent_module": self.agent_module,
            "created_at": self.created_at,
            "version": self.version,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentIdentity':
        """Create AgentIdentity from dictionary"""
        return cls(
            agent_id=data["agent_id"],
            agent_type=data["agent_type"],
            agent_class=data["agent_class"], 
            agent_module=data["agent_module"],
            created_at=data["created_at"],
            version=data.get("version"),
            metadata=data.get("metadata", {})
        )


def estimate_size_mb(obj: Any) -> float:
    """Estimate the size of an object in MB when serialized to JSON."""
    try:
        json_str = json.dumps(obj, default=str)
        size_bytes = len(json_str.encode('utf-8'))
        return size_bytes / (1024 * 1024)
    except Exception:
        # If we can't serialize, assume it's large
        return MAX_STATE_SIZE_MB + 1

def compress_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Compress agent state using gzip compression."""
    try:
        # Convert to JSON string
        json_str = json.dumps(state, default=str)
        
        # Compress the JSON string
        compressed_data = gzip.compress(json_str.encode('utf-8'))
        
        # Return wrapped compressed state
        return {
            "_compressed": True,
            "_compression_type": "gzip",
            "_original_size": len(json_str),
            "_compressed_size": len(compressed_data),
            "data": compressed_data.hex()  # Store as hex string for JSON compatibility
        }
    except Exception as e:
        logger.warning(f"Failed to compress state: {e}")
        return state

def decompress_state(compressed_state: Dict[str, Any]) -> Dict[str, Any]:
    """Decompress agent state."""
    try:
        if not compressed_state.get("_compressed"):
            return compressed_state
            
        # Extract compressed data
        compressed_data = bytes.fromhex(compressed_state["data"])
        
        # Decompress
        json_str = gzip.decompress(compressed_data).decode('utf-8')
        
        # Parse back to dict
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Failed to decompress state: {e}")
        return compressed_state

def truncate_conversation_history(state: Dict[str, Any], max_exchanges: int = MAX_CONVERSATION_HISTORY) -> Dict[str, Any]:
    """Truncate conversation history in agent state to manage size."""
    try:
        # Look for conversation history in various AutoGen state structures
        if isinstance(state, dict):
            for session_id, session_state in state.items():
                if isinstance(session_state, dict):
                    # Handle RoundRobinGroupChatManager message thread
                    if "RoundRobinGroupChatManager" in session_state:
                        manager_state = session_state["RoundRobinGroupChatManager"]
                        if "message_thread" in manager_state and isinstance(manager_state["message_thread"], list):
                            thread = manager_state["message_thread"]
                            if len(thread) > max_exchanges * 2:  # Each exchange = user + agent message
                                # Keep the most recent exchanges
                                truncated_thread = thread[-(max_exchanges * 2):]
                                manager_state["message_thread"] = truncated_thread
                                logger.info(f"Truncated message thread from {len(thread)} to {len(truncated_thread)} messages")
                    
                    # Handle individual agent states with LLM context
                    if "agent_states" in session_state:
                        for agent_name, agent_state in session_state["agent_states"].items():
                            if isinstance(agent_state, dict) and "agent_state" in agent_state:
                                inner_state = agent_state["agent_state"]
                                if "llm_context" in inner_state and "messages" in inner_state["llm_context"]:
                                    messages = inner_state["llm_context"]["messages"]
                                    if isinstance(messages, list) and len(messages) > max_exchanges * 2:
                                        # Keep the most recent messages
                                        truncated_messages = messages[-(max_exchanges * 2):]
                                        inner_state["llm_context"]["messages"] = truncated_messages
                                        logger.info(f"Truncated {agent_name} LLM context from {len(messages)} to {len(truncated_messages)} messages")
        
        return state
    except Exception as e:
        logger.warning(f"Failed to truncate conversation history: {e}")
        return state

async def agent_instance_to_config_async(agent_instance) -> Dict[str, Any]:
    """
    Convert an agent instance to a configuration dictionary that can be used to recreate it.
    Optimized version with proper async handling and state management.
    
    This version:
    1. Uses async/await for save_state if available
    2. Calls both save_state and _sessions serialization for maximum compatibility
    3. Includes proper error handling and fallbacks
    4. Optimizes for storage size while preserving functionality
    """
    logger.info(f"🔧 [CONFIG DEBUG] === Converting agent instance to config ===")
    logger.info(f"   🤖 Agent type: {type(agent_instance).__name__}")
    logger.info(f"   📦 Agent module: {type(agent_instance).__module__}")
    
    try:
        config = {
            "agent_class": type(agent_instance).__name__,
            "agent_module": type(agent_instance).__module__,
            "agent_id": getattr(agent_instance, '_agent_id', None),
            "saved_state": None  # Will be filled below
        }
        
        logger.info(f"   🆔 Agent ID: {config['agent_id']}")
        
        # PRIORITY 1: Try async save_state method (for new agents like ThinkingChatAgent)
        saved_state = None
        state_source = "none"
        
        if hasattr(agent_instance, 'save_state') and callable(getattr(agent_instance, 'save_state')):
            try:
                logger.info(f"   💾 Found save_state method, attempting to call...")
                save_method = getattr(agent_instance, 'save_state')
                
                if asyncio.iscoroutinefunction(save_method):
                    logger.info(f"   🔄 Calling async save_state method...")
                    saved_state = await save_method()
                    state_source = "async_save_state"
                else:
                    logger.info(f"   🔄 Calling sync save_state method...")
                    saved_state = save_method()
                
                if saved_state:
                    logger.info(f"   ✅ Got state from {state_source}: {type(saved_state)} size={len(str(saved_state))} chars")
                    if isinstance(saved_state, dict):
                        logger.info(f"   🔑 State keys: {list(saved_state.keys())}")
                else:
                    logger.info(f"   ⚠️  save_state returned None or empty")
                    
            except Exception as e:
                logger.error(f"   ❌ Error calling save_state method: {e}")
                saved_state = None
                state_source = "error"
        
        # PRIORITY 2: Fallback to _sessions attribute for AutoGen-based agents
        if saved_state is None and hasattr(agent_instance, '_sessions'):
            try:
                logger.info(f"   📚 No save_state result, trying _sessions attribute...")
                sessions_data = getattr(agent_instance, '_sessions', {})
                if sessions_data:
                    logger.info(f"   📊 Found _sessions data: {len(sessions_data)} sessions")
                    saved_state = sessions_data
                    state_source = "_sessions"
                else:
                    logger.info(f"   ℹ️  _sessions attribute is empty")
            except Exception as e:
                logger.error(f"   ❌ Error accessing _sessions: {e}")
        
        # PRIORITY 3: Fallback to basic agent attributes
        if saved_state is None:
            logger.info(f"   🔄 No state from methods, collecting basic attributes...")
            try:
                # Collect essential agent state
                basic_state = {}
                
                # Common attributes to preserve
                for attr in ['_conversation_context', '_current_context', '_thinking_history', 
                           '_saved_conversations', '_conversation_memory']:
                    if hasattr(agent_instance, attr):
                        value = getattr(agent_instance, attr)
                        if value:
                            basic_state[attr] = value
                            logger.debug(f"   📋 Collected {attr}: {type(value)} size={len(str(value))}")
                
                if basic_state:
                    saved_state = basic_state
                    state_source = "basic_attributes"
                    logger.info(f"   📦 Collected basic state: {list(basic_state.keys())}")
                else:
                    logger.info(f"   ℹ️  No basic attributes to save")
                    
            except Exception as e:
                logger.error(f"   ❌ Error collecting basic attributes: {e}")
        
        # Compress large states if needed
        if saved_state:
            state_size = len(str(saved_state))
            logger.info(f"   📏 Final state size: {state_size} characters from {state_source}")
            
            # Apply compression if state is large
            if state_size > COMPRESSION_THRESHOLD_MB * 1024 * 1024:
                logger.info(f"   🗜️  State is large ({state_size} chars), applying compression...")
                try:
                    compressed_state = compress_state(saved_state)
                    compressed_size = len(str(compressed_state))
                    compression_ratio = (state_size - compressed_size) / state_size * 100
                    logger.info(f"   ✅ Compressed: {state_size} → {compressed_size} chars ({compression_ratio:.1f}% reduction)")
                    saved_state = compressed_state
                except Exception as e:
                    logger.error(f"   ❌ Compression failed: {e}")
        else:
            logger.info(f"   ℹ️  No state to save for this agent")
        
        config["saved_state"] = saved_state
        
        total_config_size = len(str(config))
        logger.info(f"🎉 [CONFIG DEBUG] Config creation complete:")
        logger.info(f"   📊 Total config size: {total_config_size} characters")
        logger.info(f"   🔑 Config keys: {list(config.keys())}")
        logger.info(f"   💾 State source: {state_source}")
        
        return config
        
    except Exception as e:
        logger.error(f"❌ [CONFIG DEBUG] Error in agent_instance_to_config_async: {e}")
        import traceback
        logger.error(f"   📜 Traceback: {traceback.format_exc()}")
        
        # Return minimal config as fallback
        return {
            "agent_class": type(agent_instance).__name__,
            "agent_module": type(agent_instance).__module__,
            "agent_id": getattr(agent_instance, '_agent_id', None),
            "saved_state": None,
            "error": str(e)
        }

def agent_instance_to_config(agent_instance) -> Dict[str, Any]:
    """Convert AgentInterface instance to serializable configuration with size management."""
    # Use the same agent_type logic as get_agent_identity for consistency
    agent_type = os.getenv('AGENT_TYPE')
    if not agent_type:
        agent_type = agent_instance.__class__.__name__
    
    config = {
        "agent_type": agent_type,
        "agent_config": getattr(agent_instance, 'config', {}),
    }
    
    # *** ENHANCED FIX: Support both new save_state method and legacy _sessions approach ***
    saved_state = None
    
    # First priority: Agent has a save_state method (new approach for ThinkingAgent, etc.)
    if hasattr(agent_instance, 'save_state') and callable(getattr(agent_instance, 'save_state')):
        try:
            logger.debug(f"Agent has save_state method, calling it for state capture")
            import asyncio
            # Handle both sync and async save_state methods
            save_method = getattr(agent_instance, 'save_state')
            if asyncio.iscoroutinefunction(save_method):
                # Async save_state method
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're in an async context, but can't await here
                    # Store a flag to indicate we need async handling
                    logger.warning("Cannot call async save_state in sync context. State may not be saved.")
                    saved_state = None
                else:
                    saved_state = loop.run_until_complete(save_method())
            else:
                # Sync save_state method
                saved_state = save_method()
            
            if saved_state:
                logger.info(f"Agent save_state returned state with keys: {list(saved_state.keys())}")
            else:
                logger.debug("Agent save_state returned None or empty state")
                
        except Exception as e:
            logger.error(f"Error calling agent's save_state method: {e}")
            saved_state = None
    
    # Second priority: Legacy _sessions approach (for AutoGen-based agents)
    elif hasattr(agent_instance, '_sessions') and agent_instance._sessions:
        logger.debug(f"Using legacy _sessions approach for {len(agent_instance._sessions)} sessions")
        
        # Start with the full state
        full_state = {}
        for session_id, state in agent_instance._sessions.items():
            try:
                # The state should be serializable (it's typically AutoGen's saved state)
                full_state[session_id] = state
            except Exception as e:
                logger.warning(f"Could not serialize state for session {session_id}: {e}")
        
        saved_state = full_state if full_state else None
    
    # If we have state to save, process it
    if saved_state:
        # Check the size of the state
        estimated_size = estimate_size_mb(saved_state)
        logger.debug(f"Agent state estimated size: {estimated_size:.2f} MB")
        
        # If state is too large, apply truncation (only for legacy _sessions format)
        if estimated_size > MAX_STATE_SIZE_MB and hasattr(agent_instance, '_sessions'):
            logger.warning(f"Agent state size ({estimated_size:.2f} MB) exceeds limit ({MAX_STATE_SIZE_MB} MB), applying truncation")
            saved_state = truncate_conversation_history(saved_state)
            
            # Re-check size after truncation
            truncated_size = estimate_size_mb(saved_state)
            logger.info(f"Agent state size after truncation: {truncated_size:.2f} MB")
            
            # If still too large, apply more aggressive truncation
            if truncated_size > MAX_STATE_SIZE_MB:
                logger.warning(f"State still too large after truncation, applying aggressive truncation")
                saved_state = truncate_conversation_history(saved_state, max_exchanges=AGGRESSIVE_TRUNCATION_THRESHOLD)
                final_size = estimate_size_mb(saved_state)
                logger.info(f"Agent state size after aggressive truncation: {final_size:.2f} MB")
        
        # Apply compression if enabled and beneficial
        if ENABLE_STATE_COMPRESSION:
            original_size = estimate_size_mb(saved_state)
            if original_size > COMPRESSION_THRESHOLD_MB:
                compressed_state = compress_state(saved_state)
                compressed_size = estimate_size_mb(compressed_state)
                
                if compressed_size < original_size * COMPRESSION_EFFICIENCY_THRESHOLD:
                    logger.info(f"Applied compression: {original_size:.2f} MB -> {compressed_size:.2f} MB")
                    config["saved_state"] = compressed_state
                else:
                    logger.debug(f"Compression not beneficial: {original_size:.2f} MB -> {compressed_size:.2f} MB")
                    config["saved_state"] = saved_state
            else:
                config["saved_state"] = saved_state
        else:
            config["saved_state"] = saved_state
    else:
        logger.debug("No agent state to save")
    
    return config

def config_to_agent_instance(config: Dict[str, Any], agent_class):
    """Convert serializable configuration back to AgentInterface instance."""
    return agent_class()

def generate_agent_id(agent_instance) -> str:
    """Generate a unique identifier for an agent instance."""
    import hashlib
    import time
    
    # Use the same agent_type logic as get_agent_identity for consistency
    agent_type = os.getenv('AGENT_TYPE')
    if not agent_type:
        agent_type = agent_instance.__class__.__name__
    
    # Create unique agent ID based on agent type, timestamp, and random component
    timestamp = str(int(time.time() * 1000))  # milliseconds
    random_component = str(uuid.uuid4())[:8]
    
    # Create a hash for shorter, consistent IDs
    content = f"{agent_type}_{timestamp}_{random_component}"
    agent_id = hashlib.md5(content.encode()).hexdigest()[:16]
    
    return f"{agent_type.lower()}_{agent_id}"

def get_enhanced_agent_identity(agent_instance: AgentInterface) -> AgentIdentity:
    """Enhanced version of existing get_agent_identity with full metadata"""
    # Try to get agent_type from environment variable first
    agent_type = os.getenv('AGENT_TYPE')
    if not agent_type:
        agent_type = agent_instance.__class__.__name__
        logger.debug(f"No AGENT_TYPE environment variable set, using class name: {agent_type}")
    else:
        logger.debug(f"Using AGENT_TYPE from environment: {agent_type}")
    
    # Check if agent already has an ID stored
    if hasattr(agent_instance, '_agent_id') and agent_instance._agent_id:
        agent_id = agent_instance._agent_id
    else:
        # Generate new ID and store it on the agent
        agent_id = generate_agent_id(agent_instance)
        agent_instance._agent_id = agent_id
        logger.debug(f"Generated new agent ID: {agent_id} for agent type: {agent_type}")
    
    # Create complete identity with metadata
    agent_class = agent_instance.__class__.__name__
    agent_module = agent_instance.__class__.__module__
    
    # Get version from agent if available
    version = getattr(agent_instance, '__version__', None) or getattr(agent_instance, 'version', None)
    
    # Collect metadata
    metadata = {
        "environment_agent_type": os.getenv('AGENT_TYPE'),
        "has_save_state_method": hasattr(agent_instance, 'save_state'),
        "has_sessions_attribute": hasattr(agent_instance, '_sessions'),
        "python_version": sys.version,
        "creation_timestamp": time.time()
    }
    
    # Check if agent already has stored identity
    if hasattr(agent_instance, '_agent_identity') and isinstance(agent_instance._agent_identity, AgentIdentity):
        # Update existing identity if needed
        stored_identity = agent_instance._agent_identity
        if stored_identity.agent_id != agent_id or stored_identity.agent_type != agent_type:
            logger.warning(f"Agent identity mismatch detected - updating stored identity")
        stored_identity.agent_id = agent_id
        stored_identity.agent_type = agent_type
        stored_identity.metadata.update(metadata)
        return stored_identity
    
    # Create new identity
    identity = AgentIdentity(
        agent_id=agent_id,
        agent_type=agent_type,
        agent_class=agent_class,
        agent_module=agent_module,
        created_at=datetime.now(timezone.utc).isoformat(),
        version=version,
        metadata=metadata
    )
    
    # Store identity on agent instance
    agent_instance._agent_identity = identity
    
    return identity

def ensure_agent_identity(agent_instance: AgentInterface) -> AgentIdentity:
    """Ensures agent has identity, creating if needed. Backward compatible with existing _agent_id attribute"""
    # Check if agent already has enhanced identity
    if hasattr(agent_instance, '_agent_identity') and isinstance(agent_instance._agent_identity, AgentIdentity):
        return agent_instance._agent_identity
    
    # Create enhanced identity
    identity = get_enhanced_agent_identity(agent_instance)
    
    # Ensure backward compatibility with _agent_id attribute
    agent_instance._agent_id = identity.agent_id
    
    logger.debug(f"Ensured agent identity: {identity.agent_id} ({identity.agent_type})")
    return identity

def validate_agent_identity(agent_instance: AgentInterface, expected_agent_id: Optional[str] = None, 
                           expected_agent_type: Optional[str] = None) -> bool:
    """Validate agent identity and resolve conflicts if necessary"""
    try:
        current_identity = ensure_agent_identity(agent_instance)
        
        conflicts = []
        
        # Check agent_id conflict
        if expected_agent_id and current_identity.agent_id != expected_agent_id:
            conflicts.append(f"agent_id mismatch: expected {expected_agent_id}, got {current_identity.agent_id}")
        
        # Check agent_type conflict
        if expected_agent_type and current_identity.agent_type != expected_agent_type:
            conflicts.append(f"agent_type mismatch: expected {expected_agent_type}, got {current_identity.agent_type}")
        
        if conflicts:
            logger.warning(f"Agent identity conflicts detected: {'; '.join(conflicts)}")
            # Log the conflict but don't fail - use current identity as authoritative
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating agent identity: {e}")
        return False

def get_agent_identity(agent_instance) -> Tuple[str, str]:
    """Get or create agent identity (agent_id, agent_type) for an agent instance.
    
    Agent type is determined from AGENT_TYPE environment variable if set,
    otherwise falls back to the agent class name for backward compatibility.
    
    This function maintains backward compatibility with existing code.
    """
    # Use enhanced identity function but return only the tuple for compatibility
    identity = ensure_agent_identity(agent_instance)
    return identity.agent_id, identity.agent_type