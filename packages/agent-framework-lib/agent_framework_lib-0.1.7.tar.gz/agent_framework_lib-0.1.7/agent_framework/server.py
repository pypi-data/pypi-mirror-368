### v0.2.0 ###
import os
import uuid
import importlib
from typing import Dict, Optional, List, Tuple, Any, Type, AsyncGenerator, Union, Literal
import logging # Added logging
import secrets # Ensure secrets is imported for compare_digest
import json # Added json
import asyncio # Added asyncio
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager


from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Query, Depends, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials # Crucial import for Basic Auth and API Key
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.routing import APIRoute
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone

# Configure logging based on environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create logger for this module
logger = logging.getLogger(__name__)

from .agent_interface import AgentInterface, StructuredAgentInput, StructuredAgentOutput, AgentOutputPartUnion, TextOutputPart, JsonOutputPart, MermaidOutputPart, ChartJsOutputPart, TableDataOutputPart, FormDefinitionOutputPart, OptionsBlockOutputPart, ImageUrlInputPart, FileDataInputPart, TextInputPart, AgentInputPartUnion, AgentConfig # Import new models
from .model_config import model_config
from .model_clients import client_factory

# Session storage imports
from .session_storage import (
    SessionStorageInterface, SessionStorageFactory, SessionData,
    history_message_to_message_data, message_data_to_history_message
)
from .autogen_state_manager import (
    agent_instance_to_config, get_agent_identity,
    agent_instance_to_config_async, decompress_state
)
from .agent_provider import AgentManager



# Global variable for agent class (used by convenience function)
_GLOBAL_AGENT_CLASS: Optional[Type[AgentInterface]] = None

# --- Helper Function to Load Agent --- >
def _load_agent_dynamically() -> Type[AgentInterface]:
    """Loads the agent class from global variable or AGENT_CLASS_PATH environment variable."""
    
    # First, check if agent class is set via global variable (convenience function)
    if _GLOBAL_AGENT_CLASS is not None:
        logger.info(f"[Agent Loading] Using agent class from global variable: {_GLOBAL_AGENT_CLASS.__name__}")
        return _GLOBAL_AGENT_CLASS
    
    # Fallback to environment variable method
    # For this session, we will hardcode the streaming agent to demonstrate the new functionality.
    # In a real application, you would set this environment variable to:
    # AGENT_CLASS_PATH="examples.simple_autogen_assistant:StreamingAutoGenAssistant"
    agent_path = "examples.simple_autogen_assistant:StreamingAutoGenAssistant"
    # agent_path = os.environ.get("AGENT_CLASS_PATH")
    if not agent_path:
        raise EnvironmentError(
            "No agent class available. Either:\n"
            "1. Use create_basic_agent_server(MyAgent) from agent_framework, or\n"
            "2. Set AGENT_CLASS_PATH environment variable (format: 'module_name:ClassName'), or\n"
            "3. Create a server.py file that imports the agent_framework.server app\n"
            "\nExample using convenience function:\n"
            "  from agent_framework import create_basic_agent_server\n"
            "  create_basic_agent_server(MyAgent, port=8000)"
        )

    try:
        module_name, class_name = agent_path.split(":")
    except ValueError:
        raise ValueError(f"Invalid AGENT_CLASS_PATH format: '{agent_path}'. Expected format: 'module_name:ClassName'")

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Could not import agent module '{module_name}' from AGENT_CLASS_PATH: {e}")

    try:
        agent_class = getattr(module, class_name)
    except AttributeError:
        raise AttributeError(f"Could not find class '{class_name}' in module '{module_name}'")

    if not issubclass(agent_class, AgentInterface):
        raise TypeError(f"Agent class '{agent_path}' must inherit from AgentInterface")

    logger.info(f"[Agent Loading] Successfully loaded agent class from AGENT_CLASS_PATH: {agent_path}")
    return agent_class
# < --- Helper Function ---

# --- Content Part Models (for request validation) --- >
class TextContentPart(BaseModel):
    type: str = "text"
    text: str

class ImageUrl(BaseModel):
    url: str
    # detail: Optional[str] = "auto" # Optional detail field if needed later

class ImageUrlContentPart(BaseModel):
    type: str = "image_url"
    image_url: ImageUrl

# Type alias for content parts accepted in requests
InputContentPart = Union[TextContentPart, ImageUrlContentPart]
# < --- Content Part Models ---


# --- History Message Model --- >
class HistoryMessage(BaseModel):
    role: str
    text_content: Optional[str] = None # Made optional
    parts: Optional[List[AgentOutputPartUnion]] = None # Field for structured parts
    response_text_main: Optional[str] = None # To store StructuredAgentOutput.response_text
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    interaction_id: str = Field(default_factory=lambda: str(uuid.uuid4())) # Unique ID for each interaction exchange
    processing_time_ms: Optional[float] = None # Processing time for agent responses
    processed_at: Optional[str] = None # When the response was processed
    model_used: Optional[str] = None # AI model used to generate the response
# < --- History Message Model ---


# --- Global Application State ---

# Session storage backend (set during startup)
session_storage: Optional[SessionStorageInterface] = None

# Default user ID for single-user deployments
DEFAULT_USER_ID = "default_user"

# Pydantic model for incoming messages, now uses content list
class MessageRequest(BaseModel):
    # This model directly mirrors StructuredAgentInput for the request body
    query: Optional[str] = None
    parts: List[AgentInputPartUnion] = Field(default_factory=list)
    session_id: Optional[str] = None # session_id from query param will take precedence if both provided
    correlation_id: Optional[str] = None # Optional correlation ID to link sessions across agents

# Pydantic model for the response, includes session_id
class SessionMessageResponse(BaseModel):
    # This model directly mirrors StructuredAgentOutput for the response body
    response_text: Optional[str] = None
    parts: List[AgentOutputPartUnion] = Field(default_factory=list)
    session_id: str
    user_id: str # Include user_id in the response for clarity
    correlation_id: Optional[str] = None # Include correlation_id in response
    interaction_id: str # Include the interaction ID for this exchange
    processing_time_ms: Optional[float] = None # Include processing time if available
    model_used: Optional[str] = None # Include model used to generate the response
    # Agent identity fields
    agent_id: Optional[str] = None # Unique identifier for the agent instance
    agent_type: Optional[str] = None # Agent class name
    agent_metadata: Optional[Dict[str, Any]] = None # Additional agent metadata

class SessionInfo(BaseModel):
    session_id: str
    session_label: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    agent_id: Optional[str] = None
    agent_type: Optional[str] = None
    session_configuration: Optional[Dict[str, Any]] = None
    # Enhanced with agent lifecycle information
    agent_lifecycle: Optional[List[Dict[str, Any]]] = None

# --- Lifespan Event Handler --- >
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events using modern lifespan approach."""
    global session_storage
    
    # Startup
    try:
        # Load agent class
        agent_class = _load_agent_dynamically()
        logger.info(f"Startup event: Setting app.state.agent_class to {agent_class.__name__}")
        app.state.agent_class = agent_class
        
        # Initialize session storage
        session_storage = await SessionStorageFactory.create_storage()
        app.state.session_storage = session_storage
        logger.info(f"Session storage initialized: {session_storage.__class__.__name__}")

        # Initialize the AgentManager
        agent_manager = AgentManager(session_storage)
        app.state.agent_manager = agent_manager
        logger.info("AgentManager initialized.")
        
    except (EnvironmentError, ValueError, ImportError, AttributeError, TypeError) as e:
        # Log the specific error and raise a runtime error to prevent startup
        logger.critical(f"CRITICAL STARTUP ERROR: Failed to load agent class - {e}")
        raise RuntimeError(f"Server startup failed: Could not load agent. {e}") from e
    except Exception as e:
        # Catch any other unexpected errors during loading
        logger.critical(f"CRITICAL STARTUP ERROR: An unexpected error occurred during startup - {e}")
        raise RuntimeError(f"Server startup failed: Unexpected error. {e}") from e
    
    yield
    
    # Shutdown
    if session_storage is not None:
        await session_storage.cleanup()
        logger.info("Session storage cleaned up")
# < --- Lifespan Event Handler ---

# Initialize FastAPI app
app = FastAPI(title="Generic Agent Server", lifespan=lifespan)

# --- Authentication Setup ---
logger.debug(f"[AUTH DEBUG] Raw REQUIRE_AUTH env var: {os.environ.get('REQUIRE_AUTH')}")
REQUIRE_AUTH_STR = os.environ.get("REQUIRE_AUTH", "false").lower()
REQUIRE_AUTH = REQUIRE_AUTH_STR == "true"

# Basic Auth Configuration
BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME", "admin")
BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD", "password")

# API Key Authentication Configuration
API_KEYS = os.environ.get("API_KEYS", "").strip()
VALID_API_KEYS = set(key.strip() for key in API_KEYS.split(",") if key.strip()) if API_KEYS else set()

# Admin Mode Password Configuration
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# Initialize security schemes
basic_security = HTTPBasic(auto_error=False)
bearer_security = HTTPBearer(auto_error=False)

logger.debug(f"[AUTH DEBUG] Authentication configured - REQUIRE_AUTH: {REQUIRE_AUTH}")
logger.debug(f"[AUTH DEBUG] Valid API keys configured: {len(VALID_API_KEYS)} keys")
logger.debug("[AUTH DEBUG] Both Basic Auth and API Key authentication available")
logger.info(f"[AUTH] Admin password configured (length: {len(ADMIN_PASSWORD)} chars)")

async def get_current_user(
    basic_credentials: Optional[HTTPBasicCredentials] = Depends(basic_security),
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_security),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Unified authentication function that supports both Basic Auth and API Key authentication.
    Tries API Key first, then falls back to Basic Auth.
    """
    # Re-evaluate all auth settings on each call to respect test fixtures
    require_auth = os.environ.get("REQUIRE_AUTH", "false").lower() == "true"
    basic_auth_username = os.environ.get("BASIC_AUTH_USERNAME", "admin")
    basic_auth_password = os.environ.get("BASIC_AUTH_PASSWORD", "password")
    api_keys_str = os.environ.get("API_KEYS", "").strip()
    valid_api_keys = set(key.strip() for key in api_keys_str.split(",") if key.strip()) if api_keys_str else set()

    logger.debug(f"[AUTH DEBUG] Inside get_current_user. REQUIRE_AUTH is: {require_auth}")

    if not require_auth:
        logger.debug("[AUTH DEBUG] REQUIRE_AUTH is false, bypassing auth check. Returning anonymous user.")
        return "anonymous"

    # Try API Key authentication first (from Bearer token)
    if bearer_credentials and bearer_credentials.credentials:
        api_key = bearer_credentials.credentials
        logger.debug(f"[AUTH DEBUG] Attempting API key authentication with Bearer token")
        if api_key in valid_api_keys:
            logger.debug("[AUTH DEBUG] API key authentication successful (Bearer)")
            return f"api_key_user_{hash(api_key) % 10000}"
        else:
            logger.debug("[AUTH DEBUG] Invalid API key provided via Bearer token")

    # Try API Key authentication from X-API-Key header
    if x_api_key:
        logger.debug(f"[AUTH DEBUG] Attempting API key authentication with X-API-Key header")
        if x_api_key in valid_api_keys:
            logger.debug("[AUTH DEBUG] API key authentication successful (X-API-Key)")
            return f"api_key_user_{hash(x_api_key) % 10000}"
        else:
            logger.debug("[AUTH DEBUG] Invalid API key provided via X-API-Key header")

    # Try Basic Auth authentication
    if basic_credentials:
        logger.debug("[AUTH DEBUG] Attempting basic authentication")
        correct_username = secrets.compare_digest(basic_credentials.username, basic_auth_username)
        correct_password = secrets.compare_digest(basic_credentials.password, basic_auth_password)

        if correct_username and correct_password:
            logger.debug(f"[AUTH DEBUG] Basic auth successful for user: {basic_credentials.username}")
            return basic_credentials.username
        else:
            logger.debug(f"[AUTH DEBUG] Basic auth failed for user: {basic_credentials.username}")

    # If we reach here, authentication failed
    logger.debug("[AUTH DEBUG] All authentication methods failed. Raising 401.")
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Use Basic Auth (username/password) or API Key (Bearer token or X-API-Key header).",
        headers={
            "WWW-Authenticate": "Basic",
            "X-Auth-Methods": "Basic, Bearer, X-API-Key"
        },
    )
# --- End Authentication Setup ---

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Session Management is now handled by AgentManager ---

# --- Message persistence helpers --- >
async def _persist_user_message_to_storage(user_id: str, session_id: str, interaction_id: str, 
                                     user_message: HistoryMessage,
                                     agent_id: Optional[str] = None, agent_type: Optional[str] = None) -> bool:
    """Persist user input to storage."""
    global session_storage
    try:
        user_msg_data = history_message_to_message_data(
            user_message, session_id, user_id, interaction_id, "user_input", 
            agent_id=agent_id, agent_type=agent_type
        )
        success = await session_storage.add_message(user_msg_data)
        if success:
            logger.debug(f"Persisted user message for interaction {interaction_id}")
        return success
    except Exception as e:
        logger.error(f"Error persisting user message for interaction {interaction_id}: {e}")
        return False

async def _persist_agent_response_to_storage(user_id: str, session_id: str, interaction_id: str,
                                            agent_response_obj: StructuredAgentOutput, processing_time_ms: float,
                                            model_used: Optional[str], agent_id: Optional[str], agent_type: Optional[str]) -> None:
    """Persists the agent's response to storage."""
    global session_storage
    try:
        agent_message = HistoryMessage(
            role="assistant",
            parts=agent_response_obj.parts,
            response_text_main=agent_response_obj.response_text,
            interaction_id=interaction_id,
            processing_time_ms=processing_time_ms,
            processed_at=datetime.now(timezone.utc).isoformat(),
            model_used=model_used
        )
        agent_msg_data = history_message_to_message_data(
            agent_message, session_id, user_id, interaction_id, "agent_response",
            agent_id=agent_id, agent_type=agent_type
        )
        await session_storage.add_message(agent_msg_data)
        logger.debug(f"Persisted agent response for interaction {interaction_id}")
    except Exception as e:
        logger.error(f"Error persisting agent response for interaction {interaction_id}: {e}")


# --- Helper to extract text from content for history --- >
def _extract_text_for_history_from_input(agent_input: StructuredAgentInput) -> str:
    """Extracts a primary text representation from StructuredAgentInput for history logging."""
    if agent_input.query:
        return agent_input.query
    # Fallback: concatenate text from TextInputParts if no primary query
    text_from_parts = [p.text for p in agent_input.parts if isinstance(p, TextInputPart)]
    if text_from_parts:
        return "\n".join(text_from_parts)
    # Fallback for non-text inputs if no query or text parts
    if agent_input.parts: # If there are parts but no text ones
        return f"[Structured input with {len(agent_input.parts)} part(s), e.g., {type(agent_input.parts[0]).__name__}]"
    return "[Empty input]".strip()

def _extract_text_for_history_from_output(agent_output: StructuredAgentOutput) -> str:
    """Extracts the primary text response from StructuredAgentOutput for history logging."""
    if agent_output.response_text is not None:
        return agent_output.response_text
    # Fallback: If no primary response_text, find the first TextOutputPart
    for part in agent_output.parts:
        if isinstance(part, TextOutputPart):
            return part.text
    if agent_output.parts: # If parts exist but no text ones
        return f"[Structured response with {len(agent_output.parts)} part(s), e.g., {type(agent_output.parts[0]).__name__}]"
    return "[Empty or non-text response]".strip()
# < --- Helper --- >


@app.post("/message", response_model=SessionMessageResponse)
async def handle_message_endpoint(request: Request, msg_request_body: MessageRequest, user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user session"), current_user: str = Depends(get_current_user)):
    """
    Handles incoming messages using the session storage backend.
    """
    global session_storage
    logger.info(f"[SERVER PRE-PROCESS] Parsed msg_request_body: {msg_request_body}")
    agent_class_to_use: Type[AgentInterface] = request.app.state.agent_class
    agent_manager: AgentManager = request.app.state.agent_manager

    # Determine session_id: query param > body.session_id > new UUID
    session_id_from_query = request.query_params.get("session_id")
    effective_session_id = session_id_from_query or msg_request_body.session_id or str(uuid.uuid4())
    
    # Construct StructuredAgentInput from the request body
    query_from_request = msg_request_body.query
    if query_from_request is None:
        query_from_request = ""
    
    agent_input = StructuredAgentInput(
        query=query_from_request, 
        parts=msg_request_body.parts
    )
    logger.info(f"[SERVER LOG] Received agent_input: query='{agent_input.query}' (Original msg_request_body.query: '{msg_request_body.query}'), parts={agent_input.parts}")

    # Ensure session metadata exists (create if needed for sessions created through messaging)
    existing_session = await session_storage.load_session(user_id, effective_session_id)
    if not existing_session:
        # Create minimal session metadata for sessions created through messaging
        session_data = SessionData(
            session_id=effective_session_id,
            user_id=user_id,
            agent_instance_config={},
            correlation_id=msg_request_body.correlation_id,
            metadata={"status": "active"}  # Ensure new sessions are marked as active
        )
        await session_storage.save_session(user_id, effective_session_id, session_data)
        logger.info(f"Created session metadata for messaging session {effective_session_id}")
    else:
        # Check if session is closed (prevent messaging)
        if existing_session.metadata and existing_session.metadata.get("status") == "closed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot send message to closed session {effective_session_id}"
            )

    # Use AgentManager to get a ready-to-use agent instance (proxy)
    agent_instance = await agent_manager.get_agent(effective_session_id, agent_class_to_use, user_id)

    # Generate an interaction ID for this exchange
    interaction_id = str(uuid.uuid4())
    
    # Create and persist the user message
    user_text_for_history = _extract_text_for_history_from_input(agent_input)
    user_message = HistoryMessage(role="user", text_content=user_text_for_history, interaction_id=interaction_id)
    
    # Get agent identity from the agent instance managed by AgentManager
    # The AgentManager already ensures agent identity, so we can extract it from the agent instance
    from .autogen_state_manager import ensure_agent_identity
    agent_identity = ensure_agent_identity(agent_instance)
    await _persist_user_message_to_storage(user_id, effective_session_id, interaction_id, user_message, 
                                         agent_identity.agent_id, agent_identity.agent_type)

    try:
        # Capture start time for processing measurement
        start_time = datetime.now(timezone.utc)
        
        # Handle the message using the agent proxy.
        # State saving is now automatic within this call.
        agent_response_obj: StructuredAgentOutput = await agent_instance.handle_message(effective_session_id, agent_input)

        # Capture end time and calculate processing duration
        end_time = datetime.now(timezone.utc)
        processing_time_ms = (end_time - start_time).total_seconds() * 1000

        # Get the current model used for this response
        model_used = await agent_instance.get_current_model(effective_session_id)

        # Persist the agent response to storage
        await _persist_agent_response_to_storage(
            user_id, effective_session_id, interaction_id,
            agent_response_obj, processing_time_ms, model_used, agent_identity.agent_id, agent_identity.agent_type
        )

        # Create response
        response = SessionMessageResponse(
            response_text=agent_response_obj.response_text,
            parts=agent_response_obj.parts,
            session_id=effective_session_id,
            user_id=user_id,
            correlation_id=msg_request_body.correlation_id,
            interaction_id=interaction_id,
            processing_time_ms=processing_time_ms,
            model_used=model_used,
            # Agent identity fields
            agent_id=agent_identity.agent_id,
            agent_type=agent_identity.agent_type,
            agent_metadata=agent_identity.to_dict()
        )

        logger.info(f"[SERVER RESPONSE] Final response: session_id={effective_session_id}, response_text='{response.response_text[:100] if response.response_text else ''}...', num_parts={len(response.parts)}")
        return response

    except Exception as e:
        logger.error(f"Error processing message for session {effective_session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# --- NEW STREAMING ENDPOINT --- >

from fastapi import Body

@app.post("/stream")
async def handle_stream_endpoint(
    request: Request,
    session_id: Optional[str] = None,
    msg_request_body: MessageRequest = Body(...),
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user session"),
    current_user: str = Depends(get_current_user)
):
    """
    Handles streaming messages using the session storage backend.
    Available at:
      - POST /sessions/{session_id}/stream (session_id in path, user_id as query)
      - POST /stream?session_id=...&user_id=... (both as query)
    """
    global session_storage

    # Support both /sessions/{session_id}/stream and /stream?session_id=...
    # If session_id is not provided as a path parameter, try to get it from query/body
    if session_id is None:
        # Try to get from query params (for /stream?session_id=...)
        session_id = request.query_params.get("session_id")
        if not session_id:
            # Try to get from body (if present)
            session_id = getattr(msg_request_body, "session_id", None)
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required as a path or query parameter.")

    logger.info(f"[STREAM PRE-PROCESS] Session: {session_id}, User: {user_id}")
    agent_class_to_use: Type[AgentInterface] = request.app.state.agent_class
    agent_manager: AgentManager = request.app.state.agent_manager

    # Construct StructuredAgentInput from the request body
    query_from_request = msg_request_body.query
    if query_from_request is None:
        query_from_request = ""
    
    agent_input = StructuredAgentInput(
        query=query_from_request, 
        parts=msg_request_body.parts
    )
    logger.info(f"[STREAM LOG] Received agent_input: query='{agent_input.query}', parts={agent_input.parts}")

    # Ensure session metadata exists (create if needed for sessions created through streaming)
    existing_session = await session_storage.load_session(user_id, session_id)
    if not existing_session:
        # Create minimal session metadata for sessions created through streaming
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            agent_instance_config={},
            correlation_id=msg_request_body.correlation_id,
            metadata={"status": "active"}  # Ensure new sessions are marked as active
        )
        await session_storage.save_session(user_id, session_id, session_data)
        logger.info(f"Created session metadata for streaming session {session_id}")
    else:
        # Check if session is closed (prevent streaming)
        if existing_session.metadata and existing_session.metadata.get("status") == "closed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot send message to closed session {session_id}"
            )

    # Use AgentManager to get a ready-to-use agent instance (proxy)
    agent_instance = await agent_manager.get_agent(session_id, agent_class_to_use, user_id)

    # Generate an interaction ID for this exchange
    interaction_id = str(uuid.uuid4())
    
    # Create and persist the user message
    user_text_for_history = _extract_text_for_history_from_input(agent_input)
    user_message = HistoryMessage(role="user", text_content=user_text_for_history, interaction_id=interaction_id)
    
    # Get agent identity from the agent instance managed by AgentManager
    from .autogen_state_manager import ensure_agent_identity
    agent_identity = ensure_agent_identity(agent_instance)
    await _persist_user_message_to_storage(user_id, session_id, interaction_id, user_message, 
                                         agent_identity.agent_id, agent_identity.agent_type)

    async def stream_generator():
        final_agent_response = None
        try:
            start_time = datetime.now(timezone.utc)
            
            # The handle_message_stream call on the proxy will now stream and save state automatically
            response_stream = agent_instance.handle_message_stream(session_id, agent_input)
            
            async for output_chunk in response_stream:
                try:
                    # For each yielded StructuredAgentOutput, create a SessionMessageResponse
                    # and send it over SSE.
                    final_agent_response = output_chunk # Keep track of the latest state
                    chunk_response = SessionMessageResponse(
                        response_text=output_chunk.response_text,
                        parts=output_chunk.parts,
                        session_id=session_id,
                        user_id=user_id,
                        correlation_id=msg_request_body.correlation_id,
                        interaction_id=interaction_id,
                        # Agent identity fields
                        agent_id=agent_identity.agent_id,
                        agent_type=agent_identity.agent_type,
                        agent_metadata=agent_identity.to_dict()
                    )
                    # Use explicit JSON serialization to avoid encoding issues
                    json_data = json.dumps(chunk_response.model_dump(), ensure_ascii=False, separators=(',', ':'))
                    # Encode to bytes then decode to ensure proper UTF-8 handling
                    data_line = f"data: {json_data}\n\n"
                    yield data_line.encode('utf-8').decode('utf-8')
                    
                except Exception as chunk_error:
                    logger.error(f"Error processing chunk in stream: {chunk_error}", exc_info=True)
                    # Send error for this chunk but continue streaming
                    error_chunk = {"error": f"Chunk processing error: {str(chunk_error)}"}
                    error_line = f"data: {json.dumps(error_chunk, ensure_ascii=False, separators=(',', ':'))}\n\n"
                    yield error_line.encode('utf-8').decode('utf-8')

            # The stream is finished, now handle final persistence of the complete response
            end_time = datetime.now(timezone.utc)
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            model_used = await agent_instance.get_current_model(session_id)

            if final_agent_response:
                # Persist the final agent response summary
                await _persist_agent_response_to_storage(
                    user_id, session_id, interaction_id,
                    final_agent_response, processing_time_ms, model_used,
                    agent_identity.agent_id, agent_identity.agent_type
                )
            
            # Send a final "done" message
            done_message = {"status": "done", "session_id": session_id, "interaction_id": interaction_id}
            done_line = f"data: {json.dumps(done_message, ensure_ascii=False, separators=(',', ':'))}\n\n"
            yield done_line.encode('utf-8').decode('utf-8')

        except Exception as e:
            logger.error(f"Error during streaming for session {session_id}: {e}", exc_info=True)
            error_payload = {"error": "An error occurred during processing."}
            error_line = f"data: {json.dumps(error_payload, ensure_ascii=False, separators=(',', ':'))}\n\n"
            yield error_line.encode('utf-8').decode('utf-8')

    return StreamingResponse(
        stream_generator(), 
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )



@app.get("/sessions", response_model=List[str])
async def list_sessions_endpoint(request: Request, user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user whose sessions to list"), current_user: str = Depends(get_current_user)):
    """Lists all active session IDs for a given user_id, filtered by current agent type."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Get current agent type from the server's agent class
        from .autogen_state_manager import get_agent_identity
        temp_agent = request.app.state.agent_class()
        _, current_agent_type = get_agent_identity(temp_agent)
        
        # Use agent-filtered session retrieval instead of all user sessions
        user_sessions = await session_storage.get_user_sessions_by_agent(user_id, agent_type=current_agent_type)
        return user_sessions
    except Exception as e:
        logger.error(f"Error listing sessions for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve user sessions")

@app.get("/sessions/info", response_model=List[SessionInfo])
async def list_sessions_with_info_endpoint(
    request: Request,
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user whose sessions to list"),
    agent_id: Optional[str] = Query(None, description="Filter by specific agent ID"),
    agent_type: Optional[str] = Query(None, description="Filter by specific agent type"),
    current_user: str = Depends(get_current_user)
):
    """Lists all sessions for a user with detailed information including labels, with optional agent filtering."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # If no agent_type filter is provided, use current agent's type
        if not agent_type and not agent_id:
            from .autogen_state_manager import get_agent_identity
            temp_agent = request.app.state.agent_class()
            _, current_agent_type = get_agent_identity(temp_agent)
            agent_type = current_agent_type
        
        # Use SessionStorage to get all sessions with info for the user
        sessions_info = await session_storage.list_user_sessions_with_info(user_id)
        
        # Apply agent filters
        if agent_id or agent_type:
            filtered_sessions = []
            for session in sessions_info:
                # Check agent_id filter
                if agent_id and session.get('agent_id') != agent_id:
                    continue
                # Check agent_type filter  
                if agent_type and session.get('agent_type') != agent_type:
                    continue
                filtered_sessions.append(session)
            sessions_info = filtered_sessions
        
        return sessions_info
    except Exception as e:
        logger.error(f"Error listing sessions with info for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve user sessions with info")

@app.get("/sessions/by-correlation/{correlation_id}")
async def get_sessions_by_correlation_endpoint(correlation_id: str, current_user: str = Depends(get_current_user)):
    """Retrieves all session IDs across all users that share the same correlation_id."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Note: Cross-user correlation search is not yet implemented in the storage interface
        # For now, we'll return a placeholder response
        # TODO: Implement correlation search methods in SessionStorageInterface
        return {
            "message": "Cross-user correlation search not yet implemented. Please contact the system administrator.",
            "correlation_id": correlation_id,
            "sessions": []
        }
    except Exception as e:
        logger.error(f"Error searching for correlation {correlation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to search for correlated sessions")

@app.get("/users", response_model=List[str])
async def list_users_endpoint(current_user: str = Depends(get_current_user)):
    """Lists all user IDs who have at least one session. Admin-only endpoint."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Get all users who have sessions
        users_with_sessions = await session_storage.list_all_users_with_sessions()
        # Remove 'admin' from the list as requested - admin should not be displayed as a user
        filtered_users = [user for user in users_with_sessions if user != 'admin']
        return filtered_users
    except Exception as e:
        logger.error(f"Error listing users with sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@app.get("/sessions/{session_id}/history", response_model=List[HistoryMessage])
async def get_history_endpoint(session_id: str, user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user owning the session"), current_user: str = Depends(get_current_user)):
    """Retrieves the message history for a specific session_id owned by user_id."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    # Check if session exists
    session_data = await session_storage.load_session(user_id, session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Load conversation history from message storage
    message_data_list = await session_storage.get_conversation_history(session_id)
    
    # Convert MessageData back to HistoryMessage objects
    history = []
    for msg_data in message_data_list:
        history_msg = message_data_to_history_message(msg_data, HistoryMessage)
        history.append(history_msg)
    
    return history

@app.get("/metadata")
async def get_metadata_endpoint(request: Request, current_user: str = Depends(get_current_user)):
    """Gets the agent's metadata card using the loaded agent class from app.state."""
    # Access the agent_class from app.state, which was set during startup
    agent_class_to_use: Type[AgentInterface] = request.app.state.agent_class
    try:
        # Create a temporary instance of the loaded agent class to get metadata
        temp_agent = agent_class_to_use()
        metadata = await temp_agent.get_metadata()
        return metadata
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving metadata")

@app.get("/system-prompt")
async def get_system_prompt_endpoint(request: Request, current_user: str = Depends(get_current_user)):
    """Gets the agent's default system prompt using the loaded agent class from app.state."""
    # Access the agent_class from app.state, which was set during startup
    agent_class_to_use: Type[AgentInterface] = request.app.state.agent_class
    try:
        # Create a temporary instance of the loaded agent class to get system prompt
        temp_agent = agent_class_to_use()
        system_prompt = await temp_agent.get_system_prompt()
        
        if system_prompt is None:
            # Return 404 if no system prompt is configured
            raise HTTPException(status_code=404, detail="No default system prompt configured for this agent")
        
        return {"system_prompt": system_prompt}
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Error retrieving system prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving system prompt")

@app.get("/config/models")
async def get_model_configuration(current_user: str = Depends(get_current_user)) -> Dict[str, Any]:
    """Get model configuration information including supported models and providers."""
    try:
        config_status = model_config.validate_configuration()
        model_list = model_config.get_model_list()
        supported_providers = client_factory.get_supported_providers()
        
        return {
            "default_model": model_config.default_model,
            "configuration_status": config_status,
            "supported_models": model_list,
            "supported_providers": supported_providers,
            "fallback_provider": model_config.fallback_provider.value
        }
    except Exception as e:
        logger.error(f"Error retrieving model configuration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving model configuration")


@app.post("/admin/authenticate")
async def authenticate_admin_endpoint(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """
    Validates admin password for accessing admin features.
    This is a secondary authentication layer on top of the base auth.
    """
    try:
        password = request.get("password", "")
        if not password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        # Use secrets.compare_digest for timing-safe comparison
        if secrets.compare_digest(password, ADMIN_PASSWORD):
            return {"success": True, "message": "Admin authentication successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid admin password")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during admin authentication: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root(current_user: str = Depends(get_current_user)):
    return {"message": "Agent server is running. Visit /docs for API documentation or /testapp for a test interface."}

# --- New Endpoint for Help/Listing --- >
# --- Agent-focused API endpoints --- >

@app.get("/agents", summary="List all agent types and their usage statistics")
async def list_agents_endpoint(current_user: str = Depends(get_current_user)) -> Dict[str, Any]:
    """Get all agent types and their usage statistics."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        usage_stats = await session_storage.get_agent_usage_statistics()
        return {
            "success": True,
            "data": usage_stats
        }
    except Exception as e:
        logger.error(f"Error retrieving agent statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving agent statistics")

@app.get("/agents/{agent_type}/sessions", summary="Get sessions for a specific agent type")
async def list_agent_type_sessions_endpoint(
    agent_type: str, 
    user_id: Optional[str] = Query(None, description="Filter by specific user"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List all sessions for a specific agent type, optionally filtered by user."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        if user_id:
            # Get sessions for specific user and agent type
            sessions = await session_storage.get_user_sessions_by_agent(user_id, agent_type=agent_type)
        else:
            # Get all sessions for agent type
            sessions = await session_storage.list_sessions_by_agent_type(agent_type)
        
        return {
            "success": True,
            "agent_type": agent_type,
            "user_id": user_id,
            "session_count": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"Error retrieving sessions for agent type {agent_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error retrieving sessions for agent type {agent_type}")

@app.get("/agents/{agent_id}/lifecycle", summary="Get lifecycle events for a specific agent")
async def get_agent_lifecycle_endpoint(
    agent_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get lifecycle events for a specific agent instance."""
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        lifecycle_events = await session_storage.get_agent_lifecycle_events(agent_id)
        
        # Convert AgentLifecycleData objects to dictionaries for JSON response
        events_data = []
        for event in lifecycle_events:
            event_dict = {
                "lifecycle_id": event.lifecycle_id,
                "agent_id": event.agent_id,
                "agent_type": event.agent_type,
                "event_type": event.event_type,
                "session_id": event.session_id,
                "user_id": event.user_id,
                "timestamp": event.timestamp,
                "metadata": event.metadata
            }
            events_data.append(event_dict)
        
        return {
            "success": True,
            "agent_id": agent_id,
            "event_count": len(events_data),
            "events": events_data
        }
    except Exception as e:
        logger.error(f"Error retrieving lifecycle events for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error retrieving lifecycle events for agent {agent_id}")

@app.get("/endpoints", summary="List available API endpoints")
async def list_api_endpoints(request: Request, current_user: str = Depends(get_current_user)):
    """
    Retrieves a list of all available API endpoints in the application,
    excluding WebSocket routes and static file mounts if desired.
    """
    route_list = []
    excluded_paths = {"/openapi.json", "/docs", "/redoc", "/endpoints", "/testapp"} # Exclude testapp too

    for route in request.app.routes:
        if isinstance(route, APIRoute) and route.path not in excluded_paths:
            endpoint_info = {
                "path": route.path,
                "methods": list(route.methods),
                "summary": route.summary or "", # Use defined summary if available
                "description": route.endpoint.__doc__.strip() if route.endpoint.__doc__ else "No description.",
                "parameters": [],
                "request_body": None
            }

            # Extract Path and Query Parameters (from Pydantic models if available)
            # Note: This gives basic info; more complex dependencies might not be fully captured.
            if hasattr(route, 'dependant') and route.dependant:
                if route.dependant.path_params:
                    for param in route.dependant.path_params:
                        endpoint_info["parameters"].append({
                            "name": param.name,
                            "in": "path",
                            "required": True,
                            "type": str(param.type_.__name__) if hasattr(param.type_, '__name__') else str(param.type_)
                        })
                if route.dependant.query_params:
                    for param in route.dependant.query_params:
                         endpoint_info["parameters"].append({
                            "name": param.name,
                            "in": "query",
                            "required": param.required,
                            "type": str(param.type_.__name__) if hasattr(param.type_, '__name__') else str(param.type_)
                        })

                # Extract Request Body Info
                if route.dependant.body_params:
                    # Assuming one body param for simplicity, often the case
                    body_param = route.dependant.body_params[0]
                    body_model = body_param.type_
                    if hasattr(body_model, '__name__'):
                         endpoint_info["request_body"] = {
                             "model": body_model.__name__,
                             "required": body_param.required,
                             # Potentially list fields of the model here if needed
                         }
                    else:
                        endpoint_info["request_body"] = {"type": str(body_model), "required": body_param.required }

            route_list.append(endpoint_info)

    return route_list
# < --- New Endpoint --- >

# --- New Endpoint to Serve Test App --- >
@app.get("/testapp", response_class=FileResponse, summary="Serve the HTML test application")
async def get_test_app(current_user: str = Depends(get_current_user)):
    """
    Serves the static HTML test application.
    Ensure 'testapp.html' is in the same directory as this server script or provide the correct path.
    """
    file_path = os.path.join(os.path.dirname(__file__), "test_app.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="test_app.html not found")
    return FileResponse(file_path)

@app.get("/ui", response_class=FileResponse, summary="Serve the modern UI application")
async def get_modern_ui(current_user: str = Depends(get_current_user)):
    """
    Serves the modern HTML UI application based on HTMX, Alpine.js, and BaseCoat UI.
    This is the new UI that coexists with the existing testapp until migration is complete.
    """
    file_path = os.path.join(os.path.dirname(__file__), "modern_ui.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="modern_ui.html not found")
    return FileResponse(file_path)

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    """
    Serves a simple favicon or returns 204 No Content.
    This prevents 404 errors in browser requests.
    """
    # Check if a favicon file exists
    favicon_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        # Return proper 204 No Content with explicit headers
        from fastapi.responses import Response
        return Response(status_code=204, headers={"Content-Length": "0"})

# Mount the React build directory using absolute path (if it exists)
react_build_path = os.path.join(os.path.dirname(__file__), "front", "chat", "dist")
if os.path.exists(react_build_path):
    app.mount("/static", StaticFiles(directory=react_build_path), name="static")
    logger.info(f"Mounted static files from: {react_build_path}")
else:
    logger.warning(f"React build directory not found: {react_build_path}. Static files not mounted.")

# --- Server Startup Helper Function --- >
def start_server(agent_class_to_serve: Type[AgentInterface],
                   host: str = "0.0.0.0",
                   port: int = 8000,
                   reload: bool = True):
    """Configures and starts the Uvicorn server."""
    # This function might not be directly used if AGENT_CLASS_PATH is set for startup,
    # but kept for potential direct calls or future use.
    # global _AGENT_CLASS_TO_SERVE # Removed global as startup event handles it
    logger.info(f"Agent class passed to start_server (may be overridden by env var): {agent_class_to_serve.__name__}")

    # Read host, port, and reload from environment variables, using provided function args as defaults
    host = os.getenv("AGENT_HOST", host)
    port = int(os.getenv("AGENT_PORT", str(port)))
    # Default reload to True if AGENT_RELOAD is not explicitly set to 'false'
    reload_env = os.getenv("AGENT_RELOAD", "true").lower()
    reload = reload_env != "false"

    logger.info(f"Attempting to start Generic Agent Server (Agent loaded via AGENT_CLASS_PATH on startup)")
    logger.info(f"Listening on {host}:{port} - Reload: {reload}")

    # Run the Uvicorn server - needs import string for reload
    # When reload is enabled, we need the full module path
    if reload:
        # For reload mode, use the full module path
        app_import_string = "agent_framework.server:app"
    else:
        # For non-reload mode, can use the app directly
        app_import_string = app
    
    logger.info(f"Using import string: {app_import_string}")

    uvicorn.run(app_import_string, host=host, port=port, reload=reload)
# < --- Server Startup Helper Function --- >

# --- Internal Helper for Dynamic Loading (used only in server.py's __main__) --- >
def _load_agent_dynamically_internal() -> Type[AgentInterface]:
    # This function is problematic because it tries to load the agent *before* uvicorn potentially reloads.
    # The environment variable AGENT_CLASS_PATH set *before* running `python server.py`
    # combined with the startup event is the robust way.
    # Keeping this block but noting its potential issues if AGENT_CLASS_PATH isn't pre-set.
    agent_path = os.environ.get("AGENT_CLASS_PATH")
    if agent_path:
        logger.info(f"server.py __main__: Attempting to load agent from AGENT_CLASS_PATH: {agent_path}")
        try:
            return _load_agent_dynamically() # Use the main loader
        except Exception as e:
            logger.error(f"Fatal Error in __main__: Could not load agent from AGENT_CLASS_PATH='{agent_path}'. {e}")
            raise SystemExit(e)
    else:
        # Fallback to old environment variables if AGENT_CLASS_PATH is not set (less recommended)
        logger.warning("Warning: AGENT_CLASS_PATH not set. Falling back to AGENT_MODULE/AGENT_CLASS (might not work reliably with reload).")
        agent_module_name = os.getenv("AGENT_MODULE", "agent") # Default module
        agent_class_name = os.getenv("AGENT_CLASS", "PersonalAssistantAgent") # Default class
        logger.info(f"server.py __main__: Attempting fallback load {agent_module_name}.{agent_class_name}")
        try:
            module = importlib.import_module(agent_module_name)
            agent_class = getattr(module, agent_class_name)
            if not issubclass(agent_class, AgentInterface):
                raise TypeError(f"{agent_class_name} does not implement AgentInterface")
            # Manually set the environment variable so the startup event can find it
            # This is a workaround for running `python server.py` without pre-setting AGENT_CLASS_PATH
            os.environ["AGENT_CLASS_PATH"] = f"{agent_module_name}:{agent_class_name}"
            logger.info(f"Set AGENT_CLASS_PATH environment variable to '{os.environ['AGENT_CLASS_PATH']}' for startup event.")
            return agent_class
        except Exception as e:
            logger.error(f"Fatal Error in __main__: Could not load agent using fallback AGENT_MODULE/AGENT_CLASS. {e}")
            raise SystemExit(e)
# < --- Internal Helper --- >

# --- Server Startup Main Block --- >
if __name__ == "__main__":
    # When running server.py directly, ensure AGENT_CLASS_PATH is available for the startup event.
    # The helper above tries to load it or set it based on older env vars.
    loaded_agent_class_for_start_server = _load_agent_dynamically_internal()
    # Call start_server. The actual agent used will be determined by the startup event
    # using the AGENT_CLASS_PATH environment variable.
    start_server(loaded_agent_class_for_start_server)
# < --- Server Startup Main Block --- >

# --- Session Workflow Endpoints (New) --- >

# Define new models for session initialization and feedback
class SessionInitRequest(BaseModel):
    user_id: str
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    configuration: Dict[str, Any] = Field(..., description="Session configuration")

class SessionInitResponse(BaseModel):
    user_id: str
    correlation_id: Optional[str] = None
    session_id: str
    data: Optional[Dict[str, Any]] = None
    configuration: Dict[str, Any]
    # Agent identity fields
    agent_id: Optional[str] = None
    agent_type: Optional[str] = None

class SessionEndRequest(BaseModel):
    session_id: str

class MessageFeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    feedback: Literal["up", "down"]

class SessionFlagRequest(BaseModel):
    session_id: str
    flag_message: str

class SessionLabelUpdateRequest(BaseModel):
    session_id: str
    label: str = Field(..., max_length=100, description="Session label (max 100 characters)")


def _template_system_prompt(base_prompt: str, data: Any) -> str:
    """
    Template a system prompt with data using advanced string replacement.
    Supports:
    - {{data}} for the entire data object
    - {{data.key}} for accessing dictionary keys with data prefix
    - {{data.key.subkey}} for nested access with data prefix
    - {{key}} for direct access without data prefix
    - {{key.subkey}} for nested access without data prefix
    """
    if not data or not base_prompt:
        return base_prompt or ""
    
    import re
    
    if isinstance(data, str):
        # Simple case: replace {{data}} with the string
        templated = base_prompt.replace("{{data}}", data)
        # Also replace any {{key}} if data is just a string value
        return templated
    elif isinstance(data, dict):
        # Complex case: support multiple template patterns
        templated = base_prompt
        
        # Replace {{data}} with the entire JSON object
        templated = templated.replace("{{data}}", json.dumps(data, indent=2))
        
        # Handle nested access like {{data.key}} or {{data.key.subkey}}
        data_pattern = r'\{\{data\.([^}]+)\}\}'
        data_matches = re.findall(data_pattern, templated)
        
        for match in data_matches:
            keys = match.split('.')
            value = data
            try:
                for key in keys:
                    if isinstance(value, dict):
                        value = value[key]
                    else:
                        # Can't traverse further
                        break
                templated = templated.replace(f"{{{{data.{match}}}}}", str(value))
            except (KeyError, TypeError, AttributeError):
                # Leave placeholder if key doesn't exist
                logger.warning(f"Template key 'data.{match}' not found in data")
                pass
        
        # Handle direct access like {{key}} or {{key.subkey}} (without data prefix)
        direct_pattern = r'\{\{(?!data\.)([^}]+)\}\}'
        direct_matches = re.findall(direct_pattern, templated)
        
        for match in direct_matches:
            keys = match.split('.')
            value = data
            try:
                for key in keys:
                    if isinstance(value, dict):
                        value = value[key]
                    else:
                        # Can't traverse further
                        break
                templated = templated.replace(f"{{{{{match}}}}}", str(value))
            except (KeyError, TypeError, AttributeError):
                # Leave placeholder if key doesn't exist
                logger.warning(f"Template key '{match}' not found in data")
                pass
        
        return templated
    else:
        # For other types (list, etc.), convert to string and replace {{data}}
        return base_prompt.replace("{{data}}", json.dumps(data) if isinstance(data, (list, tuple)) else str(data))

@app.post("/init", response_model=SessionInitResponse)
async def init_session_endpoint(
    init_request: SessionInitRequest,
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """
    Initialize a new session for a user using SessionStorage with agent identity tracking.
    """
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Use provided session_id or generate new one
        session_id = init_request.session_id or str(uuid.uuid4())
        
        # Check if session already exists
        existing_session = await session_storage.load_session(init_request.user_id, session_id)
        if existing_session:
            raise HTTPException(
                status_code=409, 
                detail=f"Session {session_id} already exists for user {init_request.user_id}"
            )
        
        # Get agent class and manager
        agent_class_to_use: Type[AgentInterface] = request.app.state.agent_class
        agent_manager: AgentManager = request.app.state.agent_manager
        
        # Create temporary agent instance to get agent identity
        temp_agent = agent_class_to_use()
        from .autogen_state_manager import ensure_agent_identity
        agent_identity = ensure_agent_identity(temp_agent)
        
        logger.info(f"Capturing agent identity for session {session_id}: {agent_identity.agent_id} ({agent_identity.agent_type})")
        
        # Process the configuration - apply templating to system prompt if data is provided
        processed_configuration = init_request.configuration.copy()
        
        if init_request.data and "system_prompt" in processed_configuration:
            original_prompt = processed_configuration["system_prompt"]
            templated_prompt = _template_system_prompt(original_prompt, init_request.data)
            processed_configuration["system_prompt"] = templated_prompt
            
            logger.info(f"Applied templating to system prompt for session {session_id}")
            logger.debug(f"Original prompt: {original_prompt}")
            logger.debug(f"Templated prompt: {templated_prompt}")
            logger.debug(f"Template data: {init_request.data}")
        
        # Create SessionData object with agent identity and configuration
        session_data = SessionData(
            session_id=session_id,
            user_id=init_request.user_id,
            agent_instance_config={},  # Will be populated by AgentManager
            correlation_id=init_request.correlation_id,
            session_configuration=processed_configuration,  # Store processed configuration
            # Agent identity fields
            agent_id=agent_identity.agent_id,
            agent_type=agent_identity.agent_type,
            metadata={
                "data": init_request.data,
                "status": "active",
                "original_configuration": init_request.configuration,  # Store original for reference
                "agent_identity": agent_identity.to_dict()  # Store complete agent identity
            }
        )
        
        # Save session to storage
        success = await session_storage.save_session(init_request.user_id, session_id, session_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to initialize session")
        
        logger.info(f"Successfully initialized session {session_id} for user {init_request.user_id} with agent {agent_identity.agent_id}")
        
        return SessionInitResponse(
            user_id=init_request.user_id,
            correlation_id=init_request.correlation_id,
            session_id=session_id,
            data=init_request.data,
            configuration=processed_configuration,  # Return the templated configuration
            # Agent identity fields
            agent_id=agent_identity.agent_id,
            agent_type=agent_identity.agent_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to initialize session: {e}")

@app.post("/end")
async def end_session_endpoint(
    request: SessionEndRequest,
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user who owns the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Ends a session by updating its status in SessionStorage.
    """
    global session_storage
    session_id = request.session_id
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Load the session for the specified user
        session_data = await session_storage.load_session(user_id, session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Update session status to closed
        if session_data.metadata is None:
            session_data.metadata = {}
        session_data.metadata["status"] = "closed"
        session_data.metadata["closed_at"] = datetime.now(timezone.utc).isoformat()
        
        await session_storage.save_session(user_id, session_id, session_data)
        
        logger.info(f"Session {session_id} has been closed for user {user_id}")
        return {"message": f"Session {session_id} has been successfully closed", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to end session: {e}")

@app.post("/feedback/message")
async def submit_message_feedback_endpoint(
    request: MessageFeedbackRequest,
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user who owns the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Submit feedback for a specific message. Stores feedback in session metadata.
    Includes validation for session status, message existence, and duplicate feedback handling.
    """
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Find the session that contains this message
        session_data = await session_storage.load_session(user_id, request.session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
        
        # Check if session is closed (prevent editing)
        if session_data.metadata and session_data.metadata.get("status") == "closed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot submit feedback for closed session {request.session_id}"
            )
        
        # Validate that the message exists in this session
        # Note: The GUI sends interaction_id as message_id, so we need to search by interaction_id
        message_history = await session_storage.get_conversation_history(request.session_id)
        message_exists = any(msg.interaction_id == request.message_id for msg in message_history)
        if not message_exists:
            raise HTTPException(
                status_code=404, 
                detail=f"Message with interaction ID {request.message_id} not found in session {request.session_id}"
            )
        
        # Initialize feedback structure if needed
        if session_data.metadata is None:
            session_data.metadata = {}
        if "feedback" not in session_data.metadata:
            session_data.metadata["feedback"] = {}
        if "messages" not in session_data.metadata["feedback"]:
            session_data.metadata["feedback"]["messages"] = {}
        
        # Check for existing feedback (for duplicate prevention)
        existing_feedback = session_data.metadata["feedback"]["messages"].get(request.message_id)
        feedback_changed = existing_feedback != request.feedback
        
        # Store/update feedback
        session_data.metadata["feedback"]["messages"][request.message_id] = request.feedback
        session_data.metadata["feedback"]["messages"][f"{request.message_id}_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Save updated session data
        await session_storage.save_session(user_id, request.session_id, session_data)
        
        # Create response message
        if existing_feedback is None:
            status_message = f"Feedback '{request.feedback}' recorded for message {request.message_id}"
            logger.info(f"New feedback '{request.feedback}' submitted for message {request.message_id} in session {request.session_id}")
        elif feedback_changed:
            status_message = f"Feedback updated from '{existing_feedback}' to '{request.feedback}' for message {request.message_id}"
            logger.info(f"Feedback changed from '{existing_feedback}' to '{request.feedback}' for message {request.message_id} in session {request.session_id}")
        else:
            status_message = f"Feedback '{request.feedback}' confirmed for message {request.message_id} (no change)"
            logger.info(f"Duplicate feedback '{request.feedback}' submitted for message {request.message_id} in session {request.session_id}")
        
        return {
            "status": "success",
            "message": status_message,
            "session_id": request.session_id,
            "message_id": request.message_id,
            "feedback": request.feedback,
            "previous_feedback": existing_feedback,
            "feedback_changed": feedback_changed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting message feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {e}")

@app.post("/feedback/flag")
@app.put("/feedback/flag")
async def submit_session_flag_endpoint(
    request: SessionFlagRequest,
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user who owns the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Submit or update session-level flag. Editable while session is open.
    """
    global session_storage
    session_id = request.session_id
    flag_message = request.flag_message
    
    # Check if session exists
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Find the session
        session_data = await session_storage.load_session(user_id, session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Check if session is closed (prevent editing)
        if session_data.metadata and session_data.metadata.get("status") == "closed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit flag for closed session {session_id}"
            )
        
        # Store previous flag for comparison
        if session_data.metadata is None:
            session_data.metadata = {}
        previous_flag = session_data.metadata.get("flag_message")
        
        # Store/update session flag
        session_data.metadata["flag_message"] = flag_message
        session_data.metadata["flag_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        await session_storage.save_session(user_id, session_id, session_data)
        
        # Create response message
        if previous_flag is None:
            status_message = "Session flag created"
            logger.info(f"New session flag created for {session_id}")
        elif previous_flag != flag_message:
            status_message = "Session flag updated"
            logger.info(f"Session flag updated for {session_id}")
        else:
            status_message = "Session flag confirmed (no change)"
            logger.info(f"Duplicate session flag submitted for {session_id}")
        
        return {
            "status": "success", 
            "message": status_message,
            "session_id": session_id,
            "flag_message": flag_message,
            "previous_flag": previous_flag,
            "flag_changed": previous_flag != flag_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session flag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update session flag: {e}")

@app.put("/session/{session_id}/label", response_model=SessionInfo)
async def update_session_label_endpoint(
    session_id: str,
    label_request: SessionLabelUpdateRequest,
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user who owns the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Update the label of a specific session.
    """
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Load the session for the specified user to check if it exists
        session_data = await session_storage.load_session(user_id, session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Check if session is closed (prevent editing)
        if session_data.metadata and session_data.metadata.get("status") == "closed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update label for closed session {session_id}"
            )
        
        # Use the dedicated update_session_label method
        success = await session_storage.update_session_label(user_id, session_id, label_request.label)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update session label in storage")
        
        # Load the updated session data to return
        updated_session_data = await session_storage.load_session(user_id, session_id)
        if not updated_session_data:
            raise HTTPException(status_code=500, detail="Failed to load updated session data")
        
        logger.info(f"Session label updated for {session_id}")
        return updated_session_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session label: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update session label: {e}")

# < --- Feedback Retrieval Endpoints --- >

@app.get("/feedback/session/{session_id}")
async def get_session_feedback_endpoint(
    session_id: str,
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user who owns the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieve all feedback data for a session (flag message and message feedback).
    """
    global session_storage
    # Check if session exists
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Load session data
        session_data = await session_storage.load_session(user_id, session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Extract feedback data from SessionData object
        metadata = session_data.metadata or {}
        feedback_data = {
            "session_id": session_id,
            "user_id": user_id,
            "session_status": metadata.get("status", "active"),
            "flag_message": metadata.get("flag_message"),
            "flag_timestamp": metadata.get("flag_timestamp"),
            "message_feedback": metadata.get("feedback", {}).get("messages", {})
        }
        
        return feedback_data
        
    except Exception as e:
        logger.error(f"Error retrieving session feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session feedback: {e}")

@app.get("/feedback/message/{message_id}")
async def get_message_feedback_endpoint(
    message_id: str,
    session_id: str = Query(..., description="Session ID required to locate message feedback"),
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user who owns the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieve feedback for a specific message within a session.
    """
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Load session data to find the message feedback
        session_data = await session_storage.load_session(user_id, session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Extract message feedback from SessionData object
        metadata = session_data.metadata or {}
        message_feedback_data = metadata.get("feedback", {}).get("messages", {}).get(message_id)
        feedback_timestamp = metadata.get("feedback", {}).get("messages", {}).get(f"{message_id}_timestamp")
        
        return {
            "message_id": message_id,
            "session_id": session_id,
            "user_id": user_id,
            "feedback": message_feedback_data,
            "feedback_timestamp": feedback_timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving message feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve message feedback: {e}")

# < --- Session Status Endpoints --- >

@app.get("/session/{session_id}/status")
async def get_session_status_endpoint(
    session_id: str,
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user who owns the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Get the status of a specific session (active, closed, or not found).
    """
    global session_storage
    
    if not session_storage:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    try:
        # Check for session existence and get its status
        session_data = await session_storage.load_session(user_id, session_id)
        
        if session_data:
            # Session exists, check its actual status from metadata
            status = "active"  # Default status for sessions without explicit status
            if session_data.metadata:
                status = session_data.metadata.get("status", "active")
            
            return {
                "session_id": session_id,
                "user_id": user_id,
                "status": status,
                "created_at": session_data.created_at,
                "updated_at": session_data.updated_at,
                "closed_at": session_data.metadata.get("closed_at") if session_data.metadata else None
            }
        else:
            return {
                "session_id": session_id,
                "user_id": user_id,
                "status": "not_found"
            }
        
    except Exception as e:
        logger.error(f"Error checking session status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to check session status: {e}")

# < --- Session Workflow Endpoints --- >

@app.get("/sessions/{session_id}/response-times")
async def get_session_response_times_endpoint(
    session_id: str, 
    user_id: str = Query(DEFAULT_USER_ID, description="Identifier for the user owning the session"),
    current_user: str = Depends(get_current_user)
):
    """
    Get response times for all agent responses in a session.
    Calculates the time delta between user input and agent response messages.
    """
    if session_storage is None:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    # Check if session exists and belongs to user
    session_data = await session_storage.get_session(session_id)
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_data.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    # Get response times (only works with MongoDB storage)
    if hasattr(session_storage, 'get_response_times_for_session'):
        response_times = await session_storage.get_response_times_for_session(session_id)
        return {
            "session_id": session_id,
            "user_id": user_id,
            "response_times": response_times,
            "total_responses": len(response_times),
            "average_response_time_ms": sum(rt.get("response_time_ms", 0) for rt in response_times) / len(response_times) if response_times else 0
        }
    else:
        raise HTTPException(status_code=501, detail="Response time calculation only available with MongoDB storage")

@app.get("/interactions/{interaction_id}/response-time")
async def get_interaction_response_time_endpoint(
    interaction_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get response time for a specific interaction (user input + agent response pair).
    """
    if session_storage is None:
        raise HTTPException(status_code=500, detail="Session storage not available")
    
    # Get response time (only works with MongoDB storage)
    if hasattr(session_storage, 'get_response_times_for_interaction'):
        response_time_data = await session_storage.get_response_times_for_interaction(interaction_id)
        if not response_time_data:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        return response_time_data
    else:
        raise HTTPException(status_code=501, detail="Response time calculation only available with MongoDB storage")



