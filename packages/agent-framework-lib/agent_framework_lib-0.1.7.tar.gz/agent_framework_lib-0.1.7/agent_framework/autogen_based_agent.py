"""
AutoGen Based Agent Base Class

This module provides a base class for agents built using Microsoft AutoGen framework.
It handles all the boilerplate code for AutoGen integration, MCP tools, session management,
and message processing, allowing concrete agents to focus only on their specific logic.
"""

from typing import Any, Dict, Optional, List, AsyncGenerator
import asyncio
import json
import re
import logging
from datetime import datetime
from abc import abstractmethod

from .agent_interface import (
    AgentInterface,
    StructuredAgentInput,
    StructuredAgentOutput,
    TextOutputPart,
    TextOutputStreamPart,
    OptionsBlockOutputPart,
    FormDefinitionOutputPart,
)
from .model_clients import ModelClientFactory

logger = logging.getLogger(__name__)

# --- AutoGen Imports ---
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_core.model_context import UnboundedChatCompletionContext
    from autogen_agentchat.messages import (
        ModelClientStreamingChunkEvent,
        ThoughtEvent,
        TextMessage,
        ToolCallRequestEvent,
        ToolCallExecutionEvent,
        ToolCallSummaryMessage
    )
    from autogen_agentchat.base import TaskResult
    from autogen_ext.tools.mcp import StdioServerParams, SseServerParams, StreamableHttpServerParams, mcp_server_tools
except ImportError:
    raise ImportError(
        "AutoGen dependencies are not installed. Please run 'pip install autogen-agentchat~=0.4.5' to install the required packages."
    )


def parse_special_blocks_from_text(text: str) -> tuple[str, list]:
    """
    Parse optionsblock and formDefinition code blocks from text and return cleaned text + parts.
    
    Args:
        text: The text content to parse
        
    Returns:
        tuple: (cleaned_text, list_of_parsed_parts)
    """
    if not text:
        return text, []
    
    special_parts = []
    cleaned_text = text
    
    # Pattern to match ```json blocks with formDefinition
    json_formdefinition_pattern = r'```json\s*\n(.*?)\n```'
    json_matches = re.findall(json_formdefinition_pattern, text, re.DOTALL)
    
    for match in json_matches:
        try:
            # Parse the JSON content
            json_data = json.loads(match.strip())
            
            # Check if it contains formDefinition
            if isinstance(json_data, dict) and "formDefinition" in json_data:
                # Create a FormDefinitionOutputPart
                form_part = FormDefinitionOutputPart(definition=json_data["formDefinition"])
                special_parts.append(form_part)
                
                logger.info(f"Successfully parsed formDefinition: {json_data['formDefinition']}")
            else:
                # This JSON block doesn't contain formDefinition, leave it in the text
                continue
                
        except json.JSONDecodeError as e:
            # Invalid JSON, leave it in the text
            continue
        
        
    # Pattern to match ```optionsblock...``` blocks
    optionsblock_pattern = r'```optionsblock\s*\n(.*?)\n```'
    optionsblock_matches = re.findall(optionsblock_pattern, text, re.DOTALL)
    
    for match in optionsblock_matches:
        try:
            # Parse the JSON content
            options_data = json.loads(match.strip())
            
            # Create an OptionsBlockOutputPart
            options_part = OptionsBlockOutputPart(definition=options_data)
            special_parts.append(options_part)
            
            logger.info(f"Successfully parsed optionsblock: {options_data}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse optionsblock JSON: {e}")
            logger.error(f"Invalid JSON content: {match}")
            continue
    
    # Remove all optionsblock code blocks from the text
    cleaned_text = re.sub(optionsblock_pattern, '', cleaned_text, flags=re.DOTALL)
    
    # Remove JSON blocks that contain formDefinition
    for match in json_matches:
        try:
            json_data = json.loads(match.strip())
            if isinstance(json_data, dict) and "formDefinition" in json_data:
                # Remove this specific JSON block
                block_pattern = r'```json\s*\n' + re.escape(match) + r'\n```'
                cleaned_text = re.sub(block_pattern, '', cleaned_text, flags=re.DOTALL)
        except json.JSONDecodeError:
            continue
    
    # Clean up any extra whitespace left behind
    cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text, special_parts


class AutoGenBasedAgent(AgentInterface):
    """
    Base class for agents built using Microsoft AutoGen framework.
    
    This class handles all the boilerplate code for:
    - AutoGen agent initialization and lifecycle
    - MCP tools integration
    - Session and state management
    - Message processing (both streaming and non-streaming)
    - Model client management
    - Special block parsing (forms, options, etc.)
    
    Concrete agents should inherit from this class and implement the abstract methods
    to define their specific behavior, tools, and prompts.
    """
    
    def __init__(self):
        """Initialize the AutoGen-based agent with default configuration."""
        # Store configuration that can be overridden per session
        self._session_system_prompt = self.get_agent_prompt()
        self._session_model_config = {}
        self._session_model_name = None
        
        # Initialize MCP tools
        self._mcp_tools = None
        self._tools_initialization_task = None
        
        # Initialize model client
        factory = ModelClientFactory()
        try:
            self.model_client = factory.create_client()
        except ValueError as e:
            raise ValueError(
                f"Failed to create model client: {e}. "
                "Ensure your .env file is set up correctly with an API key."
            )

        # Initialize the autogen agent - will be recreated if session config changes
        self._create_autogen_agent()
        self._full_state = {}
        
        # MCP tools initialization will be done lazily when needed
        self._tools_initialization_task = None

    # --- Abstract Methods (Must be implemented by concrete agents) ---
    
    @abstractmethod
    def get_agent_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    def get_agent_tools(self) -> List[callable]:
        """Return list of tool functions for this agent."""
        pass

    @abstractmethod
    def get_agent_metadata(self) -> Dict[str, Any]:
        """Return agent-specific metadata."""
        pass

    @abstractmethod
    def create_autogen_agent(self, tools: List[callable], model_client: Any, system_message: str) -> Any:
        """
        Create and return the AutoGen agent instance.
        
        This method gives concrete agents full control over which AutoGen agent type to use
        and how to configure it. The base class provides the prepared tools, model client,
        and system message.
        
        Args:
            tools: Combined list of agent-specific tools and MCP tools
            model_client: Configured model client for the session
            system_message: Current system prompt for the session
            
        Returns:
            Configured AutoGen agent instance (AssistantAgent, GroupChatManager, etc.)
        """
        pass

    # --- Optional Methods (Can be overridden by concrete agents) ---
    
    def get_mcp_server_params(self) -> List["StdioServerParams | SseServerParams | StreamableHttpServerParams"]:
        """Return MCP server configurations. Override to customize MCP tools."""
        return []

    # --- Private Implementation Methods ---

    async def _initialize_tools(self):
        """Initialize the MCP tools for the agent."""
        if self._mcp_tools is None:
            try:
                logger.info("Initializing MCP tools...")
                
                # Get MCP server parameters from the concrete agent
                mcp_server_params_list = self.get_mcp_server_params()
                
                if not mcp_server_params_list:
                    logger.info("No MCP server parameters provided. Skipping MCP tools initialization.")
                    self._mcp_tools = []
                    return
                
                # Initialize MCP tools from all server params
                all_mcp_tools = []
                for server_params in mcp_server_params_list:
                    try:
                        tools = await mcp_server_tools(server_params)
                        all_mcp_tools.extend(tools)
                        logger.info(f"Initialized {len(tools)} tools from MCP server")
                    except Exception as e:
                        logger.error(f"Failed to initialize MCP server: {e}")
                
                self._mcp_tools = all_mcp_tools
                
                logger.info(f"MCP tools initialized successfully: {len(self._mcp_tools)} tools")
                logger.info(f"Available MCP tools: {[getattr(tool, 'name', str(tool)) for tool in self._mcp_tools]}")
                
                # Preserve existing state before recreating the agent
                existing_state = None
                if hasattr(self, 'autogen_agent') and self.autogen_agent:
                    try:
                        existing_state = await self.autogen_agent.save_state()
                        logger.info(f"Preserved existing agent state before MCP tools integration")
                    except Exception as e:
                        logger.warning(f"Could not save existing agent state: {e}")
                
                # Recreate the agent with the new tools
                self._create_autogen_agent()
                
                # Restore the preserved state if it exists
                if existing_state:
                    try:
                        await self.autogen_agent.load_state(existing_state)
                        logger.info(f"Restored agent state after MCP tools integration")
                    except Exception as e:
                        logger.warning(f"Could not restore agent state: {e}")
                
            except Exception as e:
                logger.error(f"Failed to initialize MCP tools: {e}")
                self._mcp_tools = []

    async def _ensure_tools_ready(self):
        """Ensure MCP tools are initialized before agent operations."""
        if self._tools_initialization_task is None:
            # Start MCP tools initialization if not started yet
            self._tools_initialization_task = asyncio.create_task(self._initialize_tools())
        
        if not self._tools_initialization_task.done():
            logger.info("Waiting for MCP tools initialization to complete...")
            try:
                await self._tools_initialization_task
            except Exception as e:
                logger.error(f"Error during tools initialization: {e}")

    def _create_autogen_agent(self):
        """Create the AutoGen agent with current configuration."""
        # Combine agent-specific tools with MCP tools
        all_tools = list(self.get_agent_tools())
        
        # Add MCP tools if they're available
        if self._mcp_tools:
            all_tools.extend(self._mcp_tools)
            logger.info(f"Agent created with {len(all_tools)} tools total ({len(self._mcp_tools)} MCP tools)")
        else:
            logger.info(f"Agent created with {len(all_tools)} agent tools only (MCP tools not yet initialized)")
        
        # Let the concrete agent create its specific AutoGen agent type
        self.autogen_agent = self.create_autogen_agent(
            tools=all_tools,
            model_client=self.model_client,
            system_message=self._session_system_prompt
        )

    # --- AgentInterface Implementation ---

    async def configure_session(self, session_configuration: Dict[str, Any]) -> None:
        """
        Configure the agent with session-level settings.
        Called by AgentManager after agent creation but before state loading.
        """
        logger.info(f"AutoGenBasedAgent: Configuring session with: {session_configuration}")
        
        # Extract session-level configuration
        if "system_prompt" in session_configuration:
            self._session_system_prompt = session_configuration["system_prompt"]
            logger.info(f"AutoGenBasedAgent: Set system prompt to: {self._session_system_prompt[:100]}...")
        
        if "model_config" in session_configuration:
            self._session_model_config = session_configuration["model_config"]
            logger.info(f"AutoGenBasedAgent: Set model config to: {self._session_model_config}")
        
        if "model_name" in session_configuration:
            self._session_model_name = session_configuration["model_name"]
            logger.info(f"AutoGenBasedAgent: Set model name to: {self._session_model_name}")
            
            # If a different model is specified, recreate the model client
            if self._session_model_name:
                try:
                    factory = ModelClientFactory()
                    # Create client with specific model if supported
                    self.model_client = factory.create_client()
                    logger.info(f"AutoGenBasedAgent: Updated model client for model: {self._session_model_name}")
                except Exception as e:
                    logger.warning(f"AutoGenBasedAgent: Failed to update model client: {e}")
        
        # Ensure tools are ready before recreating the agent
        await self._ensure_tools_ready()
        
        # Preserve existing state before recreating the agent with new configuration
        existing_state = None
        if hasattr(self, 'autogen_agent') and self.autogen_agent:
            try:
                existing_state = await self.autogen_agent.save_state()
                logger.info(f"Preserved existing agent state before session reconfiguration")
            except Exception as e:
                logger.warning(f"Could not save existing agent state: {e}")
        
        # Recreate the AutoGen agent with new configuration
        self._create_autogen_agent()
        
        # Restore the preserved state if it exists
        if existing_state:
            try:
                await self.autogen_agent.load_state(existing_state)
                logger.info(f"Restored agent state after session reconfiguration")
            except Exception as e:
                logger.warning(f"Could not restore agent state: {e}")
        
        logger.info("AutoGenBasedAgent: Agent reconfigured with session settings")

    async def get_system_prompt(self) -> Optional[str]:
        """Return the current system prompt for this session."""
        return self._session_system_prompt

    async def get_current_model(self, session_id: str) -> Optional[str]:
        """Return the current model name for this session."""
        return self._session_model_name

    async def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata about the agent."""
        # Wait for tools to be ready to get accurate count
        await self._ensure_tools_ready()
        
        # Get agent-specific metadata
        agent_metadata = self.get_agent_metadata()
        
        # Get tool information
        agent_tools = self.get_agent_tools()
        mcp_tool_count = len(self._mcp_tools) if self._mcp_tools else 0
        total_tools = len(agent_tools) + mcp_tool_count
        
        # Build tool list
        tool_list = []
        for tool in agent_tools:
            tool_list.append({
                "name": getattr(tool, '__name__', str(tool)),
                "description": getattr(tool, '__doc__', 'Agent tool'),
                "type": "agent"
            })
        
        # Add MCP tools to metadata
        if self._mcp_tools:
            for tool in self._mcp_tools:
                tool_list.append({
                    "name": getattr(tool, 'name', str(tool)),
                    "description": getattr(tool, 'description', 'MCP tool'),
                    "type": "mcp"
                })
        
        # Merge with agent-specific metadata
        base_metadata = {
            "capabilities": {
                "streaming": True,
                "tool_use": True,
                "reasoning": True,
                "multimodal": False,
                "mcp_integration": True
            },
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text", "structured"],
            "tools": tool_list,
            "tool_summary": {
                "total_tools": total_tools,
                "agent_tools": len(agent_tools),
                "mcp_tools": mcp_tool_count
            },
            "streaming_features": [
                "Real-time token streaming",
                "Tool call visualization", 
                "Reasoning step display",
                "Activity timeline",
                "Final answer formatting"
            ]
        }
        
        # Merge with agent-specific metadata (agent metadata takes precedence)
        base_metadata.update(agent_metadata)
        return base_metadata

    async def handle_message(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> StructuredAgentOutput:
        """
        Handles a user message in non-streaming mode.
        This is required by the interface, but for AutoGen agents, we recommend using the stream endpoint.
        """
        logger.info(f"Handling non streaming message")
        if not agent_input.query:
            return StructuredAgentOutput(
                response_text="Input query cannot be empty.", parts=[]
            )

        # Ensure tools are ready before processing
        await self._ensure_tools_ready()

        task_result = await self.autogen_agent.run(task=agent_input.query)
        final_response_message = task_result.messages[-1]
        response_text = final_response_message.content

        # Parse special blocks (optionsblocks and formDefinition) from the final message
        cleaned_text, special_parts = parse_special_blocks_from_text(response_text)
        
        # Build the parts list
        parts = [TextOutputPart(text=cleaned_text)]
        parts.extend(special_parts)

        return StructuredAgentOutput(
            response_text=cleaned_text,
            parts=parts,
        )

    async def handle_message_stream(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> AsyncGenerator[StructuredAgentOutput, None]:
        """
        Handles a user message by passing it to the internal Autogen agent's
        run_stream method and yielding responses as they are generated.
        """
        logger.info(f"Handling streaming message")
        if not agent_input.query:
            yield StructuredAgentOutput(
                response_text="Input query cannot be empty.", parts=[]
            )
            return

        # Ensure tools are ready before processing
        await self._ensure_tools_ready()

        response_stream = self.autogen_agent.run_stream(task=agent_input.query)

        async for message in response_stream:
            try:
                # Handle different AutoGen event types with proper formatting
                if hasattr(message, 'type') and message.type == "ModelClientStreamingChunkEvent":
                    # Streaming text tokens
                    chunk_text = message.content
                    if chunk_text:
                        yield StructuredAgentOutput(
                            response_text="",  # Don't accumulate in response_text for chunks
                            parts=[TextOutputStreamPart(text=f"__STREAM_CHUNK__{chunk_text}")]
                        )
                        
                elif isinstance(message, ToolCallRequestEvent):
                    # Tool call requests - format nicely
                    tool_calls = []
                    if hasattr(message, 'content') and message.content:
                        for call in message.content:
                            tool_calls.append({
                                "name": call.name,
                                "arguments": call.arguments,
                                "id": getattr(call, 'id', 'unknown')
                            })
                    
                    activity_data = {
                        "type": "tool_request",
                        "source": getattr(message, 'source', 'agent'),
                        "tools": tool_calls,
                        "timestamp": str(datetime.now())
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                    )
                    
                elif isinstance(message, ToolCallExecutionEvent):
                    # Tool execution results - format with status
                    tool_results = []
                    if hasattr(message, 'content') and message.content:
                        for result in message.content:
                            tool_results.append({
                                "name": result.name,
                                "content": result.content,
                                "is_error": getattr(result, 'is_error', False),
                                "call_id": getattr(result, 'call_id', 'unknown')
                            })
                    
                    activity_data = {
                        "type": "tool_result",
                        "source": getattr(message, 'source', 'agent'),
                        "results": tool_results,
                        "timestamp": str(datetime.now())
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                    )
                    
                elif isinstance(message, ToolCallSummaryMessage):
                    # Tool call summary
                    activity_data = {
                        "type": "tool_summary",
                        "source": getattr(message, 'source', 'agent'),
                        "content": message.content,
                        "timestamp": str(datetime.now())
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                    )
                    
                elif isinstance(message, ThoughtEvent):
                    # Agent thoughts/reasoning
                    activity_data = {
                        "type": "thought",
                        "source": getattr(message, 'source', 'agent'),
                        "content": message.content,
                        "timestamp": str(datetime.now())
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                    )
                    
                elif isinstance(message, TextMessage):
                    # Complete text messages
                    if message.content and message.source != 'user':
                        activity_data = {
                            "type": "message",
                            "source": message.source,
                            "content": message.content,
                            "timestamp": str(datetime.now())
                        }
                        yield StructuredAgentOutput(
                            response_text="",
                            parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                        )
                        
                elif isinstance(message, TaskResult):
                    # Final result - send the complete formatted response
                    final_message = message.messages[-1] if message.messages else None
                    if final_message and final_message.content:
                        # Parse special blocks (optionsblocks and formDefinition) from the final message
                        cleaned_text, special_parts = parse_special_blocks_from_text(final_message.content)
                        
                        # Build the parts list
                        parts = [TextOutputPart(text=cleaned_text)]
                        parts.extend(special_parts)
                        
                        # Send final answer with regular text_output type and any extracted options
                        yield StructuredAgentOutput(
                            response_text=cleaned_text,
                            parts=parts
                        )
                    return
                    
                else:
                    # Handle any other event types
                    activity_data = {
                        "type": "other",
                        "source": getattr(message, 'source', 'unknown'),
                        "content": str(message),
                        "event_type": type(message).__name__,
                        "timestamp": str(datetime.now())
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                    )
                    
            except Exception as e:
                logger.error(f"Error processing streaming message: {e}")
                error_data = {
                    "type": "error",
                    "content": str(e),
                    "timestamp": str(datetime.now())
                }
                yield StructuredAgentOutput(
                    response_text="",
                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(error_data)}")]
                )

    async def get_state(self) -> Dict[str, Any]:
        """Retrieves the serializable state of the agent."""
        return await self.autogen_agent.save_state()

    async def load_state(self, state: Dict[str, Any]):
        """Loads the state into the agent."""
        if state:
            try:
                await self.autogen_agent.load_state(state)
            except Exception as e:
                logger.warning(
                    f"Warning: Could not load agent state for AutoGenBasedAgent due to an error: {e}. Starting fresh.") 