"""
LlamaIndex-Based Agent Base Class

This base class factors out boilerplate for LlamaIndex agents:
- Session/config handling
- State management via subclass-provided context (serialize/deserialize)
- Non-streaming and streaming message processing
- Streaming event formatting aligned with modern UI expectations

Note: This base does NOT construct any concrete LlamaIndex agent.
Subclasses must implement build_agent() and provide Context and stream runner.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List, AsyncGenerator, Tuple
import json
from datetime import datetime
import logging
import os

from .agent_interface import (
    AgentInterface,
    StructuredAgentInput,
    StructuredAgentOutput,
    TextOutputPart,
    TextOutputStreamPart,
)
from .utils.special_blocks import parse_special_blocks_from_text

logger = logging.getLogger(__name__)


class LlamaIndexBasedAgent(AgentInterface):
    """
    Abstract base for LlamaIndex agents.

    Subclasses must provide:
    - get_agent_prompt() -> str
    - get_agent_tools() -> List[callable]
    - async build_agent(model_name: str, system_prompt: str) -> None
    - create_fresh_context() -> Any
    - serialize_context(ctx: Any) -> Dict[str, Any]
    - deserialize_context(state: Dict[str, Any]) -> Any
    - run_agent_stream(query: str, ctx: Any) -> Any  # returns handler with stream_events() and awaitable for final
    """

    def __init__(self):
        # Session-configurable settings
        self._session_system_prompt: str = self.get_agent_prompt()
        self._session_model_config: Dict[str, Any] = {}
        self._session_model_name: Optional[str] = None

        # Subclass-managed runtime
        self._agent_built: bool = False
        self._state_ctx: Optional[Any] = None

        # Build the agent via subclass hook
        self._ensure_agent_built()

    # ----- Abstract hooks to implement in subclass -----
    def get_agent_prompt(self) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def get_agent_tools(self) -> List[callable]:  # pragma: no cover - abstract
        raise NotImplementedError

    async def build_agent(self, model_name: str, system_prompt: str) -> None:  # pragma: no cover - abstract
        raise NotImplementedError

    def create_fresh_context(self) -> Any:  # pragma: no cover - abstract
        raise NotImplementedError

    def serialize_context(self, ctx: Any) -> Dict[str, Any]:  # pragma: no cover - abstract
        raise NotImplementedError

    def deserialize_context(self, state: Dict[str, Any]) -> Any:  # pragma: no cover - abstract
        raise NotImplementedError

    def run_agent_stream(self, query: str, ctx: Any) -> Any:  # pragma: no cover - abstract
        raise NotImplementedError

    # ----- Internal helpers -----
    def _resolve_model_name(self) -> str:
        candidate = self._session_model_name or os.getenv("OPENAI_API_MODEL")
        if not candidate or candidate.lower().startswith("gpt-5"):
            return "gpt-4o-mini"
        return candidate

    def _ensure_agent_built(self):
        if not self._agent_built:
            # Synchronous wrapper calling async build in a lazy fashion is not ideal;
            # but AgentManager invokes configure_session before first use. We'll rely on build being awaited there.
            # For safety, we expose an async ensure in configure_session.
            pass

    async def _async_ensure_agent_built(self):
        if not self._agent_built:
            await self.build_agent(self._resolve_model_name(), self._session_system_prompt)
            self._agent_built = True

    # ----- AgentInterface -----
    async def configure_session(self, session_configuration: Dict[str, Any]) -> None:
        logger.info(f"LlamaIndexBasedAgent: Configuring session: {session_configuration}")
        if "system_prompt" in session_configuration:
            self._session_system_prompt = session_configuration["system_prompt"]
        if "model_config" in session_configuration:
            self._session_model_config = session_configuration["model_config"]
        if "model_name" in session_configuration:
            self._session_model_name = session_configuration["model_name"]

        # Rebuild agent with new params
        self._agent_built = False
        await self._async_ensure_agent_built()

    async def get_system_prompt(self) -> Optional[str]:
        return self._session_system_prompt

    async def get_current_model(self, session_id: str) -> Optional[str]:
        return self._resolve_model_name()

    async def get_metadata(self) -> Dict[str, Any]:
        tools = self.get_agent_tools()
        tool_list = [
            {
                "name": getattr(t, "__name__", str(t)),
                "description": getattr(t, "__doc__", "Agent tool"),
                "type": "static",
            }
            for t in tools
        ]
        return {
            "name": "LlamaIndex Agent",
            "description": "Agent powered by LlamaIndex with streaming and tool support.",
            "capabilities": {
                "streaming": True,
                "tool_use": True,
                "reasoning": True,
                "multimodal": False,
            },
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text", "structured"],
            "tools": tool_list,
            "tool_summary": {
                "total_tools": len(tools),
                "static_tools": len(tools),
            },
            "framework": "LlamaIndex",
        }

    async def handle_message(self, session_id: str, agent_input: StructuredAgentInput) -> StructuredAgentOutput:
        if not agent_input.query:
            return StructuredAgentOutput(response_text="Input query cannot be empty.", parts=[])

        await self._async_ensure_agent_built()

        # Context reuse
        ctx = self._state_ctx or self.create_fresh_context()

        # Use streaming runner but await the final result
        handler = self.run_agent_stream(agent_input.query, ctx)
        final_response = await handler
        response_text = str(final_response)

        # Save context for future
        self._state_ctx = ctx

        cleaned, parts = parse_special_blocks_from_text(response_text)
        return StructuredAgentOutput(response_text=cleaned, parts=[TextOutputPart(text=cleaned), *parts])

    async def handle_message_stream(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> AsyncGenerator[StructuredAgentOutput, None]:
        if not agent_input.query:
            yield StructuredAgentOutput(response_text="Input query cannot be empty.", parts=[])
            return

        await self._async_ensure_agent_built()

        ctx = self._state_ctx or self.create_fresh_context()
        handler = self.run_agent_stream(agent_input.query, ctx)

        agent_loop_started_emitted = False

        async for event in handler.stream_events():
            # Token deltas
            if getattr(event, "__class__", type("", (), {})).__name__ == "AgentStream":
                chunk = getattr(event, "delta", "")
                if chunk:
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_CHUNK__{chunk}")],
                    )
                continue

            # Tool results (emit request first so UI shows arguments)
            if getattr(event, "__class__", type("", (), {})).__name__ == "ToolCallResult":
                try:
                    tool_name = getattr(event, "tool_name", "unknown_tool")
                    tool_kwargs = getattr(event, "tool_kwargs", {})
                    call_id = getattr(event, "call_id", "unknown")
                    tool_request = {
                        "type": "tool_request",
                        "source": "llamaindex_agent",
                        "tools": [
                            {"name": tool_name, "arguments": tool_kwargs, "id": call_id}
                        ],
                        "timestamp": str(datetime.now()),
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(tool_request)}")],
                    )
                except Exception:
                    pass

                tool_output = str(getattr(event, "tool_output", ""))
                tool_result = {
                    "type": "tool_result",
                    "source": "llamaindex_agent",
                    "results": [
                        {
                            "name": tool_name,
                            "content": tool_output,
                            "is_error": False,
                            "call_id": call_id,
                        }
                    ],
                    "timestamp": str(datetime.now()),
                }
                yield StructuredAgentOutput(
                    response_text="",
                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(tool_result)}")],
                )
                agent_loop_started_emitted = False
                continue

            # AgentOutput or lifecycle noise suppression and loop marker
            event_type = type(event).__name__
            if event_type in {"AgentOutput"}:
                continue
            if event_type in {"AgentInput", "InputEvent"}:
                if not agent_loop_started_emitted:
                    loop_activity = {
                        "type": "message",
                        "source": "agent",
                        "content": "Agent loop started",
                        "timestamp": str(datetime.now()),
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(loop_activity)}")],
                    )
                    agent_loop_started_emitted = True
                continue
            if event_type in {"StopEvent", "StartEvent"}:
                continue

            # Fallback: concise other event
            try:
                event_str = str(event)
                if len(event_str) > 800 or "ChatMessage(" in event_str or "tool_kwargs=" in event_str:
                    other = {
                        "type": "other",
                        "source": "llamaindex_agent",
                        "content": event_type,
                        "event_type": event_type,
                        "timestamp": str(datetime.now()),
                    }
                else:
                    other = {
                        "type": "other",
                        "source": "llamaindex_agent",
                        "content": event_str,
                        "event_type": event_type,
                        "timestamp": str(datetime.now()),
                    }
                yield StructuredAgentOutput(
                    response_text="",
                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(other)}")],
                )
            except Exception as e:
                err = {
                    "type": "error",
                    "content": f"Failed to serialize event: {e}",
                    "timestamp": str(datetime.now()),
                }
                yield StructuredAgentOutput(
                    response_text="",
                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(err)}")],
                )

        # Final result
        final_response = await handler
        self._state_ctx = ctx
        final_text = str(final_response)
        cleaned, parts = parse_special_blocks_from_text(final_text)
        yield StructuredAgentOutput(
            response_text=cleaned,
            parts=[TextOutputPart(text=cleaned), *parts],
        )

    async def get_state(self) -> Dict[str, Any]:
        if self._state_ctx is None:
            return {}
        try:
            return self.serialize_context(self._state_ctx)
        finally:
            # One-time retrieval pattern to keep consistent with existing examples
            self._state_ctx = None

    async def load_state(self, state: Dict[str, Any]):
        # Ensure the concrete agent exists before creating or deserializing context
        await self._async_ensure_agent_built()
        if state:
            try:
                self._state_ctx = self.deserialize_context(state)
            except Exception as e:
                logger.error(f"Failed to load context state: {e}. Starting fresh.")
                self._state_ctx = self.create_fresh_context()
        else:
            self._state_ctx = self.create_fresh_context()
