"""
A simple example of an Autogen AssistantAgent integrated into the AgentFramework.
"""
from typing import Any, Dict, Optional, List, Tuple, AsyncGenerator
import asyncio

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
from agent_framework.model_clients import ModelClientFactory
from agent_framework import create_basic_agent_server
import logging
import os
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__) # Explicitly get logger
logger.setLevel(logging.INFO) # <--- EXPLICITLY SET LOGGER LEVEL TO DEBUG

# --- Autogen Imports ---
# Note: Ensure you have run 'pip install autogen-agentchat'
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
except ImportError:
    raise ImportError(
        "AutoGen dependencies are not installed. Please run 'pip install autogen-agentchat~=0.4.5' to install the required packages."
    )
    
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
# --- End Autogen Imports ---

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



AGENT_PROMPT='''
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
        
        Instead, use only Chart.js's built-in configuration options that accept simple values:
        - For tooltips: Use Chart.js default formatting or simple string templates
        - For labels: Use static strings or Chart.js built-in formatters
        - For colors: Use static color arrays or predefined color schemes
        
        **Valid Chart.js Options (JSON-only):**
        ```json
        "options": {
          "responsive": true,
          "maintainAspectRatio": false,
          "plugins": {
            "title": {
              "display": true,
              "text": "Your Chart Title"
            },
            "legend": {
              "display": true,
              "position": "top"
            }
          },
          "scales": {
            "y": {
              "beginAtZero": true,
              "title": {
                "display": true,
                "text": "Y Axis Label"
              }
            },
            "x": {
              "title": {
                "display": true,
                "text": "X Axis Label"
              }
            }
          }
        }
        ```

        Example of a complete ````chart ```` block:
        ```chart
        {
          "type": "chartjs",
          "chartConfig": {
            "type": "bar",
            "data": {
              "labels": ["Mon", "Tue", "Wed"],
              "datasets": [{
                "label": "Sales",
                "data": [120, 150, 100],
                "backgroundColor": ["rgba(255, 99, 132, 0.6)", "rgba(54, 162, 235, 0.6)", "rgba(255, 206, 86, 0.6)"],
                "borderColor": ["rgba(255, 99, 132, 1)", "rgba(54, 162, 235, 1)", "rgba(255, 206, 86, 1)"],
                "borderWidth": 1
              }]
            },
            "options": {
              "responsive": true,
              "plugins": {
                "title": {
                  "display": true,
                  "text": "Weekly Sales Data"
                }
              }
            }
          }
        }
        ```

        **When generating `chartConfig` for Chart.js, you MUST use only the following core supported chart types within the `chartConfig.type` field: `bar`, `line`, `pie`, `doughnut`, `polarArea`, `radar`, `scatter`, or `bubble`.**
        **Do NOT use any other chart types, especially complex ones like `heatmap`, `treemap`, `sankey`, `matrix`, `wordCloud`, `gantt`, or any other type not explicitly listed as supported, as they typically require plugins not available in the environment.**
        For data that represents counts across two categories (which might seem like a heatmap), a `bar` chart (e.g., a grouped or stacked bar chart) is a more appropriate choice for standard Chart.js.

        **Never** output chart data as plain JSON, or within a code block marked as `json` or any other type if you intend for it to be a graphical chart. Only use the ````chart ```` block.
        
        Similarly, to ensure tables are displayed correctly as formatted tables (not just code), you MUST format your table output using a fenced code block explicitly marked as `tabledata`. The content of this block must be the JSON structure for headers and rows as shown.
        Example:
        ```tabledata
        {
          "caption": "Your Table Title",
          "headers": ["Column 1", "Column 2"],
          "rows": [
            ["Data1A", "Data1B"],
            ["Data2A", "Data2B"]
          ]
        }
        ```
        **Never** output table data intended for graphical display within a code block marked as `json` or any other type. Only use the ````tabledata ```` block.

        If you need to present a form to the user to gather structured information,
        you MUST format your entire response as a single JSON string. 
        This JSON object should contain a top-level key `"formDefinition"`, and its value should be an object describing the form. 

        The `formDefinition` object should have the following structure:
        - `title` (optional string): A title for the form.
        - `description` (optional string): A short description displayed above the form fields.
        - `fields` (array of objects): Each object represents a field in the form.
        - `submitButton` (optional object): Customizes the submit button.

        Each `field` object in the `fields` array must have:
        - `name` (string): A unique identifier for the field (used for data submission).
        - `label` (string): Text label displayed to the user for this field.
        - `fieldType` (string): Type of the input field. Supported types include:
            - `"text"`: Single-line text input.
            - `"number"`: Input for numerical values.
            - `"email"`: Input for email addresses.
            - `"password"`: Password input field (masked).
            - `"textarea"`: Multi-line text input.
            - `"select"`: Dropdown list.
            - `"checkbox"`: A single checkbox.
            - `"radio"`: Radio buttons (group by `name`).
            - `"date"`: Date picker.
        - `placeholder` (optional string): Placeholder text within the input field.
        - `required` (optional boolean): Set to `true` if the field is mandatory.
        - `defaultValue` (optional string/boolean/number): A default value for the field.

        Type-specific properties for fields:
        - For `fieldType: "number"`:
            - `min` (optional number): Minimum allowed value.
            - `max` (optional number): Maximum allowed value.
            - `step` (optional number): Increment step.
        - For `fieldType: "textarea"`:
            - `rows` (optional number): Number of visible text lines.
        - For `fieldType: "select"` or `"radio"`:
            - `options` (array of objects): Each option object must have:
                - `value` (string): The actual value submitted if this option is chosen.
                - `text` (string): The display text for the option.

        For `fieldType: "radio"`, all radio buttons intended to be part of the same group MUST share the same `name` attribute.

        The `submitButton` object (optional) can have:
        - `text` (string): Text for the submit button (e.g., "Submit", "Send").
        - `id` (optional string): A custom ID for the submit button element.

        Example of a form definition:
        ```json
        {
          "formDefinition": {
            "title": "User Feedback Form",
            "description": "Please provide your valuable feedback.",
            "fields": [
              {
                "name": "user_email",
                "label": "Your Email:",
                "fieldType": "email",
                "placeholder": "name@example.com",
                "required": true
              },
              {
                "name": "rating",
                "label": "Overall Rating:",
                "fieldType": "select",
                "options": [
                  {"value": "5", "text": "Excellent"},
                  {"value": "4", "text": "Good"},
                  {"value": "3", "text": "Average"},
                  {"value": "2", "text": "Fair"},
                  {"value": "1", "text": "Poor"}
                ],
                "required": true
              },
              {
                "name": "comments",
                "label": "Additional Comments:",
                "fieldType": "textarea",
                "rows": 4,
                "placeholder": "Let us know your thoughts..."
              },
              {
                "name": "subscribe_newsletter",
                "label": "Subscribe to our newsletter",
                "fieldType": "checkbox",
                "defaultValue": true
              }
            ],
            "submitButton": {
              "text": "Send Feedback"
            }
          }
        }
        ```

        If you are NOT generating a form, respond with a normal text string (or markdown, etc.) as usual.
        Only use the `formDefinition` JSON structure when you intend to present a fillable form to the user.

        If you need to ask a single question with a small, fixed set of answers, you can present these as clickable options to the user.
        Use the ```optionsblock``` for this. The user's selection (the 'value' of the chosen option) will be sent back as their next message.
        Format this block as a JSON object with the following structure:
        - `question` (string, optional): The question text displayed to the user above the options.
        - `options` (array of objects): Each object represents a clickable option.
          - `text` (string): The text displayed on the button for the user.
          - `value` (string): The actual value that will be sent back to you if this option is chosen. This is what your system should process.
        - `id` (string, optional): A unique identifier for this set of options (e.g., for context or logging).

        **CRITICAL JSON VALIDITY NOTE**: All JSON generated for `optionsblock` (and `formDefinition`) MUST be strictly valid. A common error is including a trailing comma after the last item in an array or the last property in an object. For example, in an `options` array, the last option object should NOT be followed by a comma.

        Example of an optionsblock:
        ```optionsblock
        {
          "question": "Which topic are you interested in?",
          "options": [
            {"text": "Weather Updates", "value": "get_weather"},
            {"text": "Stock Prices", "value": "get_stocks"},
            {"text": "General Knowledge", "value": "ask_general_knowledge"}
          ],
          "id": "topic_selection_dialog_001"
        }
        ```
        This is an alternative to using a full formDefinition for simple, single-question scenarios.
        Do NOT use this if multiple inputs are needed or if free-form text is expected.
        
        ALWAYS generate the optionsblock as the last thing in your response!!!! YOU MUST DO THIS!!!
'''


class StreamingAutoGenAssistant(AgentInterface):
    """
    An Autogen AssistantAgent that supports streaming, integrated into the AgentFramework.
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
            return a / b

    def __init__(self):
        # Store configuration that can be overridden per session
        self._session_system_prompt = AGENT_PROMPT
        self._session_model_config = {}
        self._session_model_name = None
        
        # Initialize MCP tools
        self._mcp_tools = None
        self._tools_initialization_task = None
        
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
        
        # Start MCP tools initialization in background
        self._tools_initialization_task = asyncio.create_task(self._initialize_tools())

    async def _initialize_tools(self):
        """Initialize the MCP tools for the agent."""
        if self._mcp_tools is None:
            try:
                logger.info("Initializing MCP tools...")
                
                python_server_params = StdioServerParams(
                    command='deno',
                    args=[
                        'run',
                        '-N',
                        '-R=node_modules',
                        '-W=node_modules',
                        '--node-modules-dir=auto',
                        'jsr:@pydantic/mcp-run-python',
                        'stdio',
                    ],
                    read_timeout_seconds=120
                )

                # athena_server_params = StdioServerParams(
                #     command="npx",
                #     args=['-y', '@lishenxydlgzs/aws-athena-mcp'],
                #     env={
                #         "OUTPUT_S3_PATH": os.getenv("OUTPUT_S3_PATH", "xxx"),
                #         "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
                #         "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "xxx"),
                #         "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", "xxx"),
                #         "ATHENA_WORKGROUP": os.getenv("ATHENA_WORKGROUP", "primary")
                #     },
                #     read_timeout_seconds=120,
                # )

                python_tools = await mcp_server_tools(python_server_params)
                #athena_tools = await mcp_server_tools(athena_server_params)
                self._mcp_tools = python_tools #+ athena_tools
                
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
        if self._tools_initialization_task and not self._tools_initialization_task.done():
            logger.info("Waiting for MCP tools initialization to complete...")
            try:
                await self._tools_initialization_task
            except Exception as e:
                logger.error(f"Error during tools initialization: {e}")
        elif self._mcp_tools is None:
            # If initialization never started, start it now
            await self._initialize_tools()

    def _create_autogen_agent(self):
        """Create the AutoGen agent with current configuration."""
        # Combine static methods with MCP tools
        all_tools = [self.add, self.subtract, self.multiply, self.divide]
        
        # Add MCP tools if they're available
        if self._mcp_tools:
            all_tools.extend(self._mcp_tools)
            logger.info(f"Agent created with {len(all_tools)} tools total ({len(self._mcp_tools)}  tools )")
        else:
            logger.info(f"Agent created with {len(all_tools)} static tools only (MCP tools not yet initialized)")
        
        self.autogen_agent = AssistantAgent(
            name="streaming_assistant",
            model_client=self.model_client,
            system_message=self._session_system_prompt,
            max_tool_iterations=250,
            reflect_on_tool_use=True,
            tools=all_tools,
            model_client_stream=True
        )

    async def configure_session(self, session_configuration: Dict[str, Any]) -> None:
        """
        Configure the agent with session-level settings.
        Called by AgentManager after agent creation but before state loading.
        """
        logger.info(f"StreamingAutoGenAssistant: Configuring session with: {session_configuration}")
        
        # Extract session-level configuration
        if "system_prompt" in session_configuration:
            self._session_system_prompt = session_configuration["system_prompt"]
            logger.info(f"StreamingAutoGenAssistant: Set system prompt to: {self._session_system_prompt[:100]}...")
        
        if "model_config" in session_configuration:
            self._session_model_config = session_configuration["model_config"]
            logger.info(f"StreamingAutoGenAssistant: Set model config to: {self._session_model_config}")
        
        if "model_name" in session_configuration:
            self._session_model_name = session_configuration["model_name"]
            logger.info(f"StreamingAutoGenAssistant: Set model name to: {self._session_model_name}")
            
            # If a different model is specified, recreate the model client
            if self._session_model_name:
                try:
                    factory = ModelClientFactory()
                    # Create client with specific model if supported
                    self.model_client = factory.create_client()
                    logger.info(f"StreamingAutoGenAssistant: Updated model client for model: {self._session_model_name}")
                except Exception as e:
                    logger.warning(f"StreamingAutoGenAssistant: Failed to update model client: {e}")
        
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
        
        logger.info("StreamingAutoGenAssistant: Agent reconfigured with session settings")

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
        
        total_tools = 4  # Static methods
        mcp_tool_count = len(self._mcp_tools) if self._mcp_tools else 0
        total_tools += mcp_tool_count
        
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
        
        # Add MCP tools to metadata
        if self._mcp_tools:
            for tool in self._mcp_tools:
                tool_list.append({
                    "name": getattr(tool, 'name', str(tool)),
                    "description": getattr(tool, 'description', 'MCP tool'),
                    "type": "mcp"
                })
        
        return {
            "name": "Streaming AutoGen Assistant",
            "description": "An agent that streams responses using Autogen AssistantAgent with both static methods and MCP tools.",
            "welcome_message": "Hello! I'm an example agent that demonstrates AutoGen integration with mathematical tools and MCP support.",
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
                "static_tools": 4,
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

    async def streaming_formatting_output(agent, task):
    # Your existing team setup
      
      current_streaming = {}  # Track streaming content per agent
      
      final_answer = None
      message_count = 0
      
      async for item in agent.run_stream(task=task):
      
          if isinstance(item, TaskResult):
              # Final answer
              final_answer = item.messages[-1].content
              print(f"\n✅ Final Answer: {final_answer}")
              return final_answer
              
          elif isinstance(item, ModelClientStreamingChunkEvent):
              # Handle streaming tokens on same line
              source = item.source
              
              if source not in current_streaming:
                  # First chunk from this agent
                  message_count += 1
                  current_streaming[source] = ""
                  print(f"\n[{message_count}] {source}: ", end="", flush=True)
              
              # Add chunk to same line
              current_streaming[source] += item.content
              print(item.content, end="", flush=True)
              
          elif isinstance(item, TextMessage):
              # Complete text message
              message_count += 1
              print(f"\n[{message_count}] {item.source}: {item.content}")
              # Clear streaming state for this source
              if item.source in current_streaming:
                  del current_streaming[item.source]
                  
          elif isinstance(item, ToolCallRequestEvent):
              # Show tool calls
              message_count += 1
              print(f"\n[{message_count}] 🔧 {item.source} calling tools:")
              for call in item.content:
                  print(f"   → {call.name}({call.arguments})")
                  
          elif isinstance(item, ToolCallExecutionEvent):
              # Show tool results
              message_count += 1
              print(f"\n[{message_count}] ⚙️ Tool results:")
              for result in item.content:
                  status = "✅" if not result.is_error else "❌"
                  print(f"   {status} {result.name}: {result.content}")
                  
          elif isinstance(item, ToolCallSummaryMessage):
              # Show tool summary
              message_count += 1
              print(f"\n[{message_count}] 📋 {item.source}: {item.content}")
          
          elif isinstance(item, ThoughtEvent):
              # Show tool summary
              message_count += 1
              print(f"\n[{message_count}] 📋 {item.source}: {item.content}")
              
          else:
              # Handle any other events
              message_count += 1
              content = getattr(item, 'content', str(item))
              print(f"\n[{message_count}] 📝 {item.source}: {content}")
      return final_answer  # This is what your client receives

    async def handle_message(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> StructuredAgentOutput:
        """
        Handles a user message in non-streaming mode.
        This is required by the interface, but for this agent, we recommend using the stream endpoint.
        """
        logger.info(f"Handling non streaming message")
        if not agent_input.query:
            return StructuredAgentOutput(
                response_text="Input query cannot be empty.", parts=[]
            )

        # Ensure tools are ready before processing
        await self._ensure_tools_ready()

        task_result = await self.autogen_agent.run(task=agent_input.query)
        print(f"\n\n\n=====TASK RESULT======: {task_result} \n\n\n")
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

        response_stream = self.autogen_agent.run_stream(
            task=agent_input.query,
           # model_client_stream=True,  # Enable token streaming from the model
        )

        accumulated_text = ""
        #from autogen_core.messages import TextMessage
        
        async for message in response_stream:
            try:
                # Handle different AutoGen event types with proper formatting
                if hasattr(message, 'type') and message.type == "ModelClientStreamingChunkEvent":
                    # Streaming text tokens
                    chunk_text = message.content
                    if chunk_text:
                        accumulated_text += chunk_text
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
                print(
                    f"Warning: Could not load agent state for StreamingAutoGenAssistant due to an error: {e}. Starting fresh.")
                pass


def main():
    """Main function to start the thinking agent server."""
    
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        logger.error("Error: No API keys found!")
        logger.error("Please set either OPENAI_API_KEY or GEMINI_API_KEY")
        return
    
    # Get port from environment variable or use 8000 as default
    try:
        port = int(os.getenv("AGENT_PORT", "8000"))
    except ValueError:
        logger.warning("Invalid AGENT_PORT specified. Defaulting to 8000.")
        port = 8000

    logger.info("Starting Agentserver...")
    logger.info(f"Model: {os.getenv('OPENAI_API_MODEL', model_config.default_model)}")
    logger.info(f"Access at: http://localhost:{port}/testapp")
    
    create_basic_agent_server(
        agent_class=StreamingAutoGenAssistant,
        host="0.0.0.0", 
        port=port,
        reload=False
    )


if __name__ == "__main__":
    main()