"""
Slim LlamaIndex agent built on LlamaIndexBasedAgent base.
Keeps only agent-specific logic: tools, prompt, agent/context wiring.
"""
from typing import Any, Dict, List, Optional, AsyncGenerator
import os
import logging

from agent_framework import (
    create_basic_agent_server,
)
from agent_framework.llamaindex_based_agent import LlamaIndexBasedAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# LlamaIndex imports kept local to this example
try:
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.llms.openai import OpenAI
    from llama_index.core.workflow import Context
    from llama_index.core.workflow import JsonSerializer
except ImportError:
    raise ImportError(
        "LlamaIndex dependencies are not installed. Please run 'pip install llama-index'"
    )


AGENT_PROMPT = """
You are an assistant helping with a user's requests.
You can use provided tools to do computations. Stream responses and show tool calls.
""".strip()


class SlimLlamaIndexAgent(LlamaIndexBasedAgent):
    # ---- Tools ----
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

    # ---- Base hooks ----
    def get_agent_prompt(self) -> str:
        return AGENT_PROMPT

    def get_agent_tools(self) -> List[callable]:
        return [self.add, self.subtract, self.multiply, self.divide]

    async def build_agent(self, model_name: str, system_prompt: str) -> None:
        # Create LLM and FunctionAgent (subclass owns this choice)
        llm = OpenAI(model=model_name)
        self._li_agent = FunctionAgent(
            tools=self.get_agent_tools(),
            llm=llm,
            system_prompt=system_prompt,
            verbose=True,
        )

    def create_fresh_context(self) -> Any:
        return Context(self._li_agent)

    def serialize_context(self, ctx: Any) -> Dict[str, Any]:
        return ctx.to_dict(serializer=JsonSerializer())

    def deserialize_context(self, state: Dict[str, Any]) -> Any:
        return Context.from_dict(self._li_agent, state, serializer=JsonSerializer())

    def run_agent_stream(self, query: str, ctx: Any) -> Any:
        return self._li_agent.run(user_msg=query, ctx=ctx)


def main():
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Error: No OPENAI_API_KEY found!")
        return

    try:
        port = int(os.getenv("AGENT_PORT", "8000"))
    except ValueError:
        port = 8000

    logger.info("Starting Slim LlamaIndex Agent Server...")
    logger.info(f"Model: {os.getenv('OPENAI_API_MODEL', 'gpt-4o-mini')}")
    logger.info(f"Access at: http://localhost:{port}/ui")

    create_basic_agent_server(
        agent_class=SlimLlamaIndexAgent,
        host="0.0.0.0",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
