"""
A LlamaIndex FunctionAgent integrated into the AgentFramework.
"""
from typing import Any, Dict, Optional, List, AsyncGenerator
import asyncio
import json
import re
import logging
import os
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from agent_framework.agent_interface import (
    AgentInterface,
    StructuredAgentInput,
    StructuredAgentOutput,
    TextOutputPart,
    TextOutputStreamPart,
    OptionsBlockOutputPart,
    FormDefinitionOutputPart,
)
from agent_framework.model_config import model_config
from agent_framework import create_basic_agent_server

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- LlamaIndex Imports ---
try:
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.llms.openai import OpenAI
    from llama_index.core.llms.llm import BaseLLM
    from llama_index.core.workflow import Context
    from llama_index.core.agent.workflow import AgentStream, ToolCallResult, AgentOutput
except ImportError:
    raise ImportError(
        "LlamaIndex dependencies are not installed. Please run 'pip install llama-index' to install the required packages."
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


AGENT_PROMPT = '''
You are an assistant helping with a user's requests.

You can generate markdown, mermaid diagrams, charts and code blocks, forms and optionsblocks. 
ALWAYS include option blocks in your answer especially when asking the user to select an option or continue with the conversation!!! 
ALWAYS include options blocks (OK, No Thanks) when saying something like:  Let me know if you want to ... 

NEVER propose to export data, charts or tables or generate pdf files. You are not capable YET.

**Crucial for Display: Formatting Charts and Tables**
To ensure charts are displayed correctly as interactive graphics, you MUST format your chart output using a fenced code block explicitly marked as `chart`. The content of this block must be a JSON object with **EXACTLY** the following top-level structure:
```json
{
  "type": "chartjs",
  "chartConfig": { /* Your actual Chart.js configuration object goes here */ }
}
```
Inside the `chartConfig` object, you will then specify the Chart.js `type` (e.g., `bar`, `line`), `data`, and `options`.

**CRITICAL: NO JAVASCRIPT FUNCTIONS ALLOWED**
The `chartConfig` must be PURE JSON - NO JavaScript functions, callbacks, or executable code are allowed. This means:
- NO `function(context) { ... }` in tooltip callbacks
- NO `function(value, index, values) { ... }` in formatting callbacks
- NO arrow functions like `(ctx) => { ... }`
- NO executable JavaScript code of any kind

If you need to present a form to the user to gather structured information,
you MUST format your entire response as a single JSON string. 
This JSON object should contain a top-level key `"formDefinition"`, and its value should be an object describing the form.

If you need to ask a single question with a small, fixed set of answers, you can present these as clickable options to the user.
Use the ```optionsblock``` for this. The user's selection (the 'value' of the chosen option) will be sent back as their next message.
Format this block as a JSON object with the following structure:
- `question` (string, optional): The question text displayed to the user above the options.
- `options` (array of objects): Each object represents a clickable option.
  - `text` (string): The text displayed on the button for the user.
  - `value` (string): The actual value that will be sent back to you if this option is chosen.
- `id` (string, optional): A unique identifier for this set of options.

ALWAYS generate the optionsblock as the last thing in your response!!!! YOU MUST DO THIS!!!
'''


class LlamaIndexAgent(AgentInterface):
    """
    A LlamaIndex FunctionAgent integrated into the AgentFramework.
    """
    
    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract one number from another."""
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers together."""
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divide one number by another."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    def __init__(self):
        # Store configuration that can be overridden per session
        self._session_system_prompt = AGENT_PROMPT
        self._session_model_config = {}
        self._session_model_name = None
        self._state = None
        
        # Initialize LlamaIndex agent
        self._create_llamaindex_agent()
        
        # State management will be handled per-session via contexts

    def _resolve_model_name(self) -> str:
        """Resolve a valid OpenAI model name for LlamaIndex streaming."""
        # Priority: explicitly set session model -> env var -> safe default
        candidate = self._session_model_name or os.getenv("OPENAI_API_MODEL")
        # Guard against invalid placeholders (e.g., gpt-5-mini) by falling back
        if not candidate:
            return "gpt-5-mini"
        return candidate

    def _create_llamaindex_agent(self):
        """Create the LlamaIndex FunctionAgent with current configuration."""
        # Get tools
        tools = [self.add, self.subtract, self.multiply, self.divide]
        
        # Create LLM
        model_name = self._resolve_model_name()
        llm = OpenAI(model=model_name)
        
        # Create the agent
        self.llamaindex_agent = FunctionAgent(
            tools=tools,
            llm=llm,
            system_prompt=self._session_system_prompt,
            #memory=self._conversation_memory,
            verbose=True
        )
        
        logger.info(f"LlamaIndex agent created with {len(tools)} tools and model {model_name}")

    async def configure_session(self, session_configuration: Dict[str, Any]) -> None:
        """
        Configure the agent with session-level settings.
        Called by AgentManager after agent creation but before state loading.
        """
        logger.info(f"LlamaIndexAgent: Configuring session with: {session_configuration}")
        
        # Extract session-level configuration
        if "system_prompt" in session_configuration:
            self._session_system_prompt = session_configuration["system_prompt"]
            logger.info(f"LlamaIndexAgent: Set system prompt to: {self._session_system_prompt[:100]}...")
        
        if "model_config" in session_configuration:
            self._session_model_config = session_configuration["model_config"]
            logger.info(f"LlamaIndexAgent: Set model config to: {self._session_model_config}")
        
        if "model_name" in session_configuration:
            self._session_model_name = session_configuration["model_name"]
            logger.info(f"LlamaIndexAgent: Set model name to: {self._session_model_name}")
        
        # Recreate the agent with new configuration
        self._create_llamaindex_agent()
        
        logger.info("LlamaIndexAgent: Agent reconfigured with session settings")

    async def get_system_prompt(self) -> Optional[str]:
        """Return the current system prompt for this session."""
        return self._session_system_prompt

    async def get_current_model(self, session_id: str) -> Optional[str]:
        """Return the current model name for this session."""
        return self._session_model_name

    async def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata about the agent."""
        tool_list = [
            {
                "name": "add",
                "description": "Add two numbers together",
                "parameters": ["a: float", "b: float"],
                "type": "static"
            },
            {
                "name": "subtract", 
                "description": "Subtract one number from another",
                "parameters": ["a: float", "b: float"],
                "type": "static"
            },
            {
                "name": "multiply",
                "description": "Multiply two numbers together", 
                "parameters": ["a: float", "b: float"],
                "type": "static"
            },
            {
                "name": "divide",
                "description": "Divide one number by another",
                "parameters": ["a: float", "b: float"],
                "type": "static"
            }
        ]
        
        return {
            "name": "LlamaIndex Function Agent",
            "description": "An agent that uses LlamaIndex FunctionAgent with mathematical tools.",
            "welcome_message": "Hello! I'm a LlamaIndex-powered agent that can help with mathematical calculations and general assistance.",
            "capabilities": {
                "streaming": True,  # LlamaIndex agents now support streaming
                "tool_use": True,
                "reasoning": True,
                "multimodal": False,
                "llamaindex_integration": True
            },
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text", "structured"],
            "tools": tool_list,
            "tool_summary": {
                "total_tools": len(tool_list),
                "static_tools": len(tool_list),
                "llamaindex_tools": len(tool_list)
            },
            "framework": "LlamaIndex",
            "agent_type": "FunctionAgent"
        }

    async def handle_message(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> StructuredAgentOutput:
        """
        Handles a user message in non-streaming mode.
        """
        logger.info(f"Handling message for session {session_id}")
        if not agent_input.query:
            return StructuredAgentOutput(
                response_text="Input query cannot be empty.", parts=[]
            )

        try:
                      
            # Run the LlamaIndex agent
            from llama_index.core.workflow import JsonSerializer
            
            
            if(self._state is not None):
                ctx = self._state
                logger.info("STATE USED IN HANDLE_MESSAGE: FROM LOCAL VARIABLE")
            else:
                ctx = Context(self.llamaindex_agent)
                logger.info("STATE USED IN HANDLE_MESSAGE: FROM INITIALIZED")
            
            response = await self.llamaindex_agent.run(user_msg=agent_input.query, ctx=ctx)
            response_text = str(response)
            
            #save context as state for next interaction
            self._state=ctx

            # Parse special blocks (optionsblocks and formDefinition) from the response
            cleaned_text, special_parts = parse_special_blocks_from_text(response_text)
            
            # Build the parts list
            parts = [TextOutputPart(text=cleaned_text)]
            parts.extend(special_parts)

            return StructuredAgentOutput(
                response_text=cleaned_text,
                parts=parts,
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_message = f"Sorry, I encountered an error: {str(e)}"
            return StructuredAgentOutput(
                response_text=error_message,
                parts=[TextOutputPart(text=error_message)],
            )

    async def handle_message_stream(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> AsyncGenerator[StructuredAgentOutput, None]:
        """
        Handles a user message by yielding responses as they are generated.
        Uses LlamaIndex's streaming capability.
        """
        logger.info(f"Handling streaming message for session {session_id}")
        if not agent_input.query:
            yield StructuredAgentOutput(
                response_text="Input query cannot be empty.", parts=[]
            )
            return

        try:
            from llama_index.core.workflow import JsonSerializer
            
  
            
            if(self._state is not None):
                ctx = self._state
                logger.info("STATE USED IN HANDLE_MESSAGE: FROM LOCAL VARIABLE")
            else:
                ctx = Context(self.llamaindex_agent)
                logger.info("STATE USED IN HANDLE_MESSAGE: FROM INITIALIZED")
            
            # Run the LlamaIndex agent with streaming
            handler = self.llamaindex_agent.run(user_msg=agent_input.query, ctx=ctx)
            
            accumulated_text = ""
            agent_loop_started_emitted = False
            
            # Stream events from LlamaIndex
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    # Stream text tokens
                    chunk_text = event.delta
                    if chunk_text:
                        accumulated_text += chunk_text
                        yield StructuredAgentOutput(
                            response_text="",
                            parts=[TextOutputStreamPart(text=f"__STREAM_CHUNK__{chunk_text}")]
                        )
                        
                elif isinstance(event, ToolCallResult):
                    # First emit a proper tool_request activity so UI shows arguments
                    try:
                        tool_request = {
                            "type": "tool_request",
                            "source": "llamaindex_agent",
                            "tools": [
                                {
                                    "name": getattr(event, "tool_name", "unknown_tool"),
                                    "arguments": getattr(event, "tool_kwargs", {}),
                                    "id": getattr(event, "call_id", "unknown")
                                }
                            ],
                            "timestamp": str(datetime.now())
                        }
                        yield StructuredAgentOutput(
                            response_text="",
                            parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(tool_request)}")]
                        )
                    except Exception:
                        pass

                    # Then emit the tool_result activity with output
                    tool_results = [
                        {
                            "name": getattr(event, "tool_name", "unknown_tool"),
                            "content": str(getattr(event, "tool_output", "")),
                            "is_error": False,
                            "call_id": getattr(event, "call_id", "unknown")
                        }
                    ]
                    activity_data = {
                        "type": "tool_result",
                        "source": "llamaindex_agent",
                        "results": tool_results,
                        "timestamp": str(datetime.now())
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                    )
                    # Reset loop-start flag after a concrete action
                    agent_loop_started_emitted = False
                elif isinstance(event, AgentOutput):
                    # Suppress verbose AgentOutput events; final message is handled below
                    continue
                else:
                    # Filter out internal/super-verbose events that confuse the UI
                    try:
                        event_type_name = type(event).__name__
                        # Replace AgentInput with a single friendly loop-start message (debounced)
                        if event_type_name in {"AgentInput", "InputEvent"}:
                            if not agent_loop_started_emitted:
                                loop_activity = {
                                    "type": "message",
                                    "source": "agent",
                                    "content": "Agent loop started",
                                    "timestamp": str(datetime.now())
                                }
                                yield StructuredAgentOutput(
                                    response_text="",
                                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(loop_activity)}")]
                                )
                                agent_loop_started_emitted = True
                            continue

                        if event_type_name in {"StopEvent", "StartEvent"}:
                            # Ignore framework lifecycle events
                            continue
                        # Avoid dumping giant raw inputs or internal representations
                        event_str = str(event) if not isinstance(event, dict) else json.dumps(event)
                        # Drop low-level tool_name debug events; we already emit combined tool_result above
                        if "tool_name=" in event_str or "tool_kwargs=" in event_str:
                            continue
                        if len(event_str) > 800 or "ChatMessage(" in event_str:
                            # Emit only a concise marker instead of the full payload
                            concise = {
                                "type": "other",
                                "source": "llamaindex_agent",
                                "content": f"{event_type_name}",
                                "event_type": event_type_name,
                                "timestamp": str(datetime.now())
                            }
                            yield StructuredAgentOutput(
                                response_text="",
                                parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(concise)}")]
                            )
                        else:
                            activity_data = {
                                "type": "other",
                                "source": "llamaindex_agent",
                                "content": event_str,
                                "event_type": event_type_name,
                                "timestamp": str(datetime.now())
                            }
                            yield StructuredAgentOutput(
                                response_text="",
                                parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                            )
                    except Exception as e:
                        err = {
                            "type": "error",
                            "content": f"Failed to serialize event: {e}",
                            "timestamp": str(datetime.now())
                        }
                        yield StructuredAgentOutput(
                            response_text="",
                            parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(err)}")]
                        )
            
            # Get the final response
            response = await handler
            final_response_text = str(response)
            self._state=ctx
            
            # Parse special blocks from the final response
            cleaned_text, special_parts = parse_special_blocks_from_text(final_response_text)
            
            # Build the parts list
            parts = [TextOutputPart(text=cleaned_text)]
            parts.extend(special_parts)
            
            # Send final answer
            yield StructuredAgentOutput(
                response_text=cleaned_text,
                parts=parts
            )
                    
        except Exception as e:
            logger.error(f"Error processing streaming message: {e}")
            error_message = f"Sorry, I encountered an error: {str(e)}"
            yield StructuredAgentOutput(
                response_text=error_message,
                parts=[TextOutputPart(text=error_message)],
            )

    async def get_state(self) -> Dict[str, Any]:
        """Retrieves the serializable state of the agent."""
        from llama_index.core.workflow import JsonSerializer
        state_dict = None
        if self._state is not None:
            state_dict = self._state.to_dict(serializer=JsonSerializer())
            logger.info("STATE RETRIEVAL: FROM self._state")
            self._state=None
        else:
            state_dict = Context(self.llamaindex_agent).to_dict(serializer=JsonSerializer())
            logger.info("STATE RETRIEVAL: INITIALIZED CONTEXT")
        return state_dict

    async def load_state(self, state: Dict[str, Any]):
        """Loads the state into the agent."""
        from llama_index.core.workflow import JsonSerializer
        if state:
            try:
                 #logger.info(f"STATE LOADING. Memeory content: {state}")
                 self._state= Context.from_dict(self.llamaindex_agent, state, serializer=JsonSerializer())
                 logger.info("STATE LOADING: FROM PERSISTENCE LAYER")
            except Exception as e:
                logger.error(f"STATE LOADING: ERROR: {e}. Starting fresh.")
                ctx = Context(self.llamaindex_agent)
                self._state=ctx.to_dict(serializer=JsonSerializer())

def main():
    """Main function to start the LlamaIndex agent server."""
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Error: No OPENAI_API_KEY found!")
        logger.error("Please set OPENAI_API_KEY environment variable")
        return
    
    # Get port from environment variable or use 8000 as default
    try:
        port = int(os.getenv("AGENT_PORT", "8000"))
    except ValueError:
        logger.warning("Invalid AGENT_PORT specified. Defaulting to 8000.")
        port = 8000

    logger.info("Starting LlamaIndex Agent Server...")
    logger.info(f"Model: {os.getenv('OPENAI_API_MODEL', 'gpt-4o-mini')}")
    logger.info(f"Access at: http://localhost:{port}/testapp")
    
    create_basic_agent_server(
        agent_class=LlamaIndexAgent,
        host="0.0.0.0", 
        port=port,
        reload=False
    )


if __name__ == "__main__":
    main()