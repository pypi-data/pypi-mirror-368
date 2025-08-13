# Agent Framework Architecture

## 1. Overview

This document outlines the architecture of the Agent Framework, designed to provide a robust, scalable, and extensible platform for serving conversational agents.

The primary architectural goal is the **Separation of Concerns**. Specifically, we aim to completely decouple the web server layer from the implementation details of any specific agent framework (e.g., Microsoft AutoGen). The server should not know how an agent manages its internal memory or state; its only job is to handle web requests and interact with a generic `AgentInterface`.

This design allows for easy extension to support other agent frameworks (like LangChain, etc.) in the future without modifying the core server logic.

### Key Architectural Improvements

**🎯 AutoGen Boilerplate Extraction**: The framework now provides `AutoGenBasedAgent`, a comprehensive base class that eliminates 95% of boilerplate code when creating AutoGen-based agents. Developers can now focus on agent-specific logic rather than AutoGen integration details.

**🔄 Rapid Agent Development**: Creating new AutoGen agents now requires implementing only 4 abstract methods instead of copying 970+ lines of boilerplate code.

## 2. Core Components

The architecture is composed of several key components, each with a single, well-defined responsibility.

| Component                    | Responsibility                                                                                                                                                                                                                  |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Server (FastAPI)**   | Handles HTTP requests, manages the web layer, and orchestrates high-level workflows by interacting with the `AgentManager`.                                                                                                   |
| **AgentManager**       | The "wrapper" or provider. Manages the lifecycle of agents, including creation, state loading, and wrapping them in a proxy. It is the single point of contact for the server.                                                  |
| **_ManagedAgentProxy** | An object that implements the `AgentInterface` and wraps the real agent. It transparently adds automatic state-saving behavior after a message is handled.                                                                    |
| **AutoGenBasedAgent**  | **NEW**: Base class for AutoGen agents. Handles all AutoGen boilerplate including integration, MCP tools, session management, streaming, and state persistence. Concrete agents inherit from this class.                    |
| **RealAgent**          | The concrete agent implementation (e.g., ExampleAutoGenAgent). For AutoGen agents, inherits from `AutoGenBasedAgent` and implements only 4 abstract methods. Contains the core conversational logic.                       |
| **SessionStorage**     | The persistence layer. Manages the storage of two distinct data types: session metadata and agent state, linked by a `session_id`.                                                                                            |
| **AutoGen State Mgr**  | A helper module used by `AutoGenBasedAgent` to handle the specifics of serializing, compressing, and managing AutoGen's unique state format. Now integrated into the base class.                                           |

## 3. Key Architectural Decisions & Principles

### a. True Decoupling via an Agent Manager

The server does not create agent instances or load their state directly. Instead, it delegates this entire responsibility to the `AgentManager`. This manager is the only component that understands how to assemble a fully functional agent, abstracting away all complexity from the server.

### b. The Proxy Pattern for Transparent State Management

A critical requirement was that state should be persisted automatically after an agent responds, without the server needing to explicitly trigger a "save" operation. We achieve this using the **Proxy Pattern**.

- The `AgentManager` does not return the `RealAgent` to the server. It returns a `_ManagedAgentProxy` instead.
- This proxy *looks and feels* exactly like a real agent because it implements the same `AgentInterface`.
- When the server calls `handle_message()` on the proxy, the proxy first passes the call to the `RealAgent`.
- Once the `RealAgent` returns a response, the proxy automatically calls the agent's `get_state()` method and instructs the `SessionStorage` to persist the new state.

This makes state saving an invisible, automatic side-effect of handling a message, dramatically simplifying the server logic.

### c. Separation of Agent State from Session Metadata

Based on your insight, an agent's internal state (its memory, configuration, etc.) is a fundamentally different concern from the session's metadata (user ID, timestamps, correlation ID).

This architecture formalizes that separation. The `SessionStorage` interface has distinct methods and underlying collections/tables for:

1. `save_session()` / `load_session()`: For lightweight session metadata.
2. `save_agent_state()` / `load_agent_state()`: For the potentially large and complex agent state "blob".

This ensures the system is more organized, scalable, and easier to debug.

### d. Interface-Driven Design for Extensibility

The `AgentInterface` is the core contract that enables the entire system's flexibility. Any future agent, regardless of its underlying framework, can be integrated into the system by simply:

1. Implementing the `AgentInterface`.
2. Providing the logic for its own state management within the `get_state()` and `load_state()` methods.

The server, `AgentManager`, and `SessionStorage` layers will require no changes.

### e. AutoGen Base Class Architecture

**🎯 Boilerplate Elimination**: The `AutoGenBasedAgent` base class encapsulates all AutoGen-specific boilerplate:

- **AutoGen Integration**: Complete setup and lifecycle management
- **MCP Tools**: Integration with Model Context Protocol tools  
- **Session Management**: Configuration, state saving/loading
- **Streaming Support**: Real-time message streaming with proper event handling
- **Special Block Parsing**: Forms, option blocks, charts, tables
- **Error Handling**: Robust error handling and logging

**🔧 Simple Agent Development**: Concrete AutoGen agents now only need to implement:

```python
class MyAgent(AutoGenBasedAgent):
    def get_agent_prompt(self) -> str:
        """Return the system prompt for this agent."""
        
    def get_agent_tools(self) -> List[callable]:
        """Return list of tool functions for this agent."""
        
    def get_agent_metadata(self) -> Dict[str, Any]:
        """Return agent-specific metadata."""
        
    def create_autogen_agent(self, tools, model_client, system_message):
        """Create and configure your AutoGen agent type."""
```

**📈 Development Impact**:
- **Before**: 970+ lines of boilerplate per agent
- **After**: 40-60 lines for a complete agent
- **Time Reduction**: From 2-3 hours to 10-15 minutes per agent
- **Flexibility**: Full control over AutoGen agent type (AssistantAgent, GroupChatManager, etc.)

## 4. Workflows & Sequence Diagram

The following diagram illustrates how the components interact across the main API workflows.

```mermaid
sequenceDiagram
    participant User as User/Client
    participant Server as Server (FastAPI)
    participant AgentManager as AgentManager
    participant _ManagedAgentProxy as AgentProxy
    participant AutoGenBasedAgent as Base Class
    participant RealAgent as Concrete Agent
    participant SessionStorage as SessionStorage
    participant AutoGenStateManager as AutoGen State Mgr

    Note over User, AutoGenStateManager: Workflow 1: Full Session (/init -> /message -> /end)

    User->>+Server: POST /init (config)
    Note over Server,AgentManager: Server creates AgentManager at startup. The manager has access to SessionStorage.
    Server->>AgentManager: init_session(user_id, config)
    AgentManager->>SessionStorage: save_session(session_metadata)
    AgentManager->>SessionStorage: save_agent_state(session_id, empty_state)
    Server-->>-User: 200 OK (session_id)

    User->>+Server: POST /message (session_id, input)
    Server->>AgentManager: get_agent(session_id, agent_class)
    AgentManager->>SessionStorage: load_agent_state(session_id)
    SessionStorage-->>AgentManager: returns stored_state
    AgentManager->>RealAgent: new ConcreteAgent() extends AutoGenBasedAgent
    Note right of RealAgent: Concrete agent implements only get_agent_prompt(), get_agent_tools(), get_agent_metadata(), create_autogen_agent()
    AgentManager->>AutoGenBasedAgent: load_state(stored_state)
    Note right of AutoGenBasedAgent: Base class handles all AutoGen integration, MCP tools, state management
    AutoGenBasedAgent->>AutoGenStateManager: decompress_state(...)
    AgentManager->>_ManagedAgentProxy: new _ManagedAgentProxy(concrete_agent)
    Note over AgentManager,_ManagedAgentProxy: Proxy implements AgentInterface, hiding the real agent from the server.
    AgentManager-->>Server: returns proxy_instance

    Server->>_ManagedAgentProxy: handle_message(input)
    _ManagedAgentProxy->>AutoGenBasedAgent: handle_message(input)
    Note right of AutoGenBasedAgent: Base class handles streaming, event processing, tool execution
    AutoGenBasedAgent->>RealAgent: get_agent_prompt(), get_agent_tools()
    RealAgent-->>AutoGenBasedAgent: returns agent-specific configuration
    AutoGenBasedAgent-->>_ManagedAgentProxy: returns response
    Note over _ManagedAgentProxy,AutoGenBasedAgent: Automatic State Persistence (Proxy Pattern)
    _ManagedAgentProxy->>AutoGenBasedAgent: get_state()
    AutoGenBasedAgent->>AutoGenStateManager: compress_state(...)
    AutoGenBasedAgent-->>_ManagedAgentProxy: returns new_state
    _ManagedAgentProxy->>SessionStorage: save_agent_state(session_id, new_state)
    _ManagedAgentProxy-->>Server: returns response
    Server-->>-User: 200 OK (response)

    User->>+Server: POST /end (session_id)
    Server->>AgentManager: end_session(session_id)
    AgentManager->>SessionStorage: update_session_status('closed')
    Server-->>-User: 200 OK

    Note over User, AutoGenStateManager: Workflow 2: Stateless Endpoints (e.g., /metadata)

    User->>+Server: GET /metadata
    Note over Server,RealAgent: This flow is stateless and doesn't need the AgentManager or persistence.
    Server->>RealAgent: new RealAgent() (temporary instance)
    Server->>RealAgent: get_metadata()
    RealAgent-->>Server: returns metadata
    Server-->>-User: 200 OK (metadata)
```
