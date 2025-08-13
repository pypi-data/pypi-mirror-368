# Agent Framework Library Examples

This directory contains examples demonstrating how to use the `agent-framework-lib` to build various types of conversational AI agents.

Generated on: 2024-12-19 21:45:00 CET

## Prerequisites

### Install UV (Recommended)
UV is a fast Python package installer and resolver that provides better dependency management:

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Alternative: Traditional Python Setup
If you prefer not to use UV, you can use traditional pip with the provided `requirements.txt`.

### Git Repository Access Methods

The Agent Framework can be installed from GitHub using two methods:

**HTTPS Access** (recommended for most users):
- Works with public repositories or private repositories with authentication
- Format: `git+https://github.com/username/repo.git`
- Example: `pip install git+https://github.com/Cinco-AI/AgentFramework.git`

**SSH Access** (recommended for developers with SSH keys):
- Requires SSH key pair configured in GitHub settings
- Format: `git+ssh://git@github.com:username/repo.git`
- Example: `pip install git+ssh://git@github.com/Cinco-AI/AgentFramework.git`

## Quick Start

### Option 1: Using UV (Recommended)

1. **Navigate to the examples directory:**
   ```bash
   cd examples/
   ```

2. **Install dependencies:**
   ```bash
   # Initialize and sync dependencies from pyproject.toml
   uv sync
   
   # Install the agent framework from parent directory
   uv add --editable ../
   ```

3. **Set up environment variables** (for AI-powered examples):
   ```bash
   # Copy the template
   cp env.example .env
   
   # Edit .env and add your API keys
   # See the .env file for all available configuration options
   ```

4. **Run examples:**
   ```bash
   # Run the simple agent
   uv run simple_agent.py
   
   # Run the AI agent (requires API keys)
   uv run autogen_agent_example.py
   ```

### Option 2: Using Traditional pip

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e ../  # Install agent framework from parent
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run examples:**
   ```bash
   python simple_agent.py
   python autogen_agent_example.py
   ```

## Examples

### 1. Simple Agent (`simple_agent.py`)

A basic agent that demonstrates the minimal implementation required to create a conversational agent.

**Features**:
- Simple text responses
- Session management
- Basic conversation handling
- No external AI dependencies

**Run with UV:**
```bash
uv run simple_agent.py
```

**Server starts on:** `http://localhost:8000`

**Test**:
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello!"}'
```

### 2. AutoGen AI Agent (`autogen_agent_example.py`)

An AI-powered agent using the AutoGen framework with actual language models.

**Features**:
- Real AI responses using LLMs
- Multi-provider support (OpenAI, Gemini)
- Context-aware conversations
- Streaming responses
- Session persistence

**Run with UV:**
```bash
uv run autogen_agent_example.py
```

**Server starts on:** `http://localhost:8001`

**Test**:
```bash
curl -X POST http://localhost:8001/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain quantum computing in simple terms"}'
```

## Development Workflow with UV

### Managing Dependencies

```bash
# Add a new dependency
uv add fastapi

# Add a development dependency
uv add --dev pytest

# Add optional dependencies
uv add --optional gemini google-generativeai

# Update all dependencies
uv lock --upgrade

# Install dependencies in different environments
uv sync --extra dev          # Install with dev dependencies
uv sync --extra gemini       # Install with Gemini support
uv sync --extra all          # Install everything
```

### Running Scripts and Commands

```bash
# Run Python scripts
uv run simple_agent.py
uv run autogen_agent_example.py

# Run development tools
uv run black .               # Format code
uv run pytest               # Run tests
uv run mypy .               # Type checking

# Run with specific Python version
uv run --python 3.12 simple_agent.py
```

### Virtual Environment Management

```bash
# UV automatically manages virtual environments, but you can also:

# Create a virtual environment manually
uv venv

# Activate the virtual environment
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

# Install packages in active environment
uv pip install package-name
```

## Usage Patterns

### Basic Agent Implementation

```python
from agent_framework import AgentInterface, StructuredAgentInput, StructuredAgentOutput

class MyAgent(AgentInterface):
    async def get_metadata(self):
        return {"name": "My Agent", "version": "1.0.0"}
    
    async def handle_message(self, session_id: str, agent_input: StructuredAgentInput):
        return StructuredAgentOutput(response_text="Hello from my agent!")
```

### AI-Powered Agent Implementation

```python
from agent_framework import AutoGenAgentBase, client_factory
from autogen_agentchat.agents import AssistantAgent

class MyAIAgent(AutoGenAgentBase):
    def _setup_agent_components(self):
        model_name = "gpt-4"
        model_client = client_factory.create_client(model_name)
        return None, model_client
    
    async def _create_autogen_agent_instance(self, session_id, workbench, server_params, model_client, system_prompt=None, agent_config=None):
        return AssistantAgent(
            name="AI_Assistant", 
            model_client=model_client,
            system_message=system_prompt or "You are a helpful assistant."
        )
```

### Starting the Server

```python
from agent_framework import create_basic_agent_server

# Quick start with convenience function
create_basic_agent_server(MyAgent, port=8000)

# Or with more control
from agent_framework import start_server
start_server(MyAgent, host="0.0.0.0", port=8000, reload=True)
```

## Testing the Examples

### Using the Web Interface

Navigate to `http://localhost:PORT/testapp` to access the built-in web interface for testing.

### Using cURL

```bash
# Basic message
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"query": "Your message here"}'

# With session management
curl -X POST http://localhost:8000/message?session_id=test123 \
  -H "Content-Type: application/json" \
  -d '{"query": "Continue our conversation"}'

# Get agent metadata
curl http://localhost:8000/metadata

# Get available endpoints
curl http://localhost:8000/endpoints
```

### Using Python Requests

```python
import requests

# Send a message
response = requests.post(
    "http://localhost:8000/message",
    json={"query": "Hello, agent!"}
)
print(response.json())
```

### Using the Python HTTP Client

```python
import httpx
import asyncio

async def test_agent():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/message",
            json={"query": "Hello, agent!"}
        )
        print(response.json())

asyncio.run(test_agent())
```

## Configuration

### Environment Variables

Create a `.env` file in this directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
DEFAULT_MODEL=gpt-4

# Gemini Configuration (alternative)
GEMINI_API_KEY=your-gemini-api-key-here
DEFAULT_MODEL=gemini-1.5-pro

# Database Configuration
MONGODB_URI=mongodb://localhost:27017

# Authentication (optional)
REQUIRE_AUTH=false
API_KEYS=key1,key2,key3

# Server Configuration
AGENT_HOST=0.0.0.0
AGENT_PORT=8000
AGENT_RELOAD=true
```

### Agent Configuration

```python
from agent_framework import AgentConfig

# Configure agent behavior per session
agent_config = AgentConfig(
    temperature=0.8,
    max_tokens=1000,
    model_selection="gpt-4-turbo"
)

# Pass in message request
response = requests.post(
    "http://localhost:8000/message",
    json={
        "query": "Your message",
        "agent_config": agent_config.dict()
    }
)
```

## Project Structure

```
examples/
├── pyproject.toml          # UV/pip dependencies and project config
├── requirements.txt        # Fallback pip requirements
├── README.md              # This file
├── simple_agent.py        # Basic agent example
├── autogen_agent_example.py # AI-powered agent example
└── .env                   # Environment variables (create this)
```

## Next Steps

1. **Extend the examples** with your own agent logic
2. **Experiment with different models** by changing `DEFAULT_MODEL`
3. **Add custom tools and capabilities** to your agents
4. **Deploy your agents** using the production deployment guide
5. **Contribute back** improvements and new examples

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in the example scripts
2. **Missing API keys**: Ensure your `.env` file has the correct API keys
3. **Dependency conflicts**: Use `uv sync` to resolve dependencies properly
4. **Import errors**: Make sure you've installed the agent framework with `uv add --editable ../`

### Getting Help

- Check the main documentation: `../docs/`
- Review the API documentation: `http://localhost:PORT/docs`
- Test your setup with: `http://localhost:PORT/testapp` 