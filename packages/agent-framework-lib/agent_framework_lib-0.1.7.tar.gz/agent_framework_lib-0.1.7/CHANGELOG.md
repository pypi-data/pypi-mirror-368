# Changelog

All notable changes to the Agent Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.7 - 2025-08-12

Updated:
* llamaindex based agent with llamaindex base code


## 0.1.6 - 2025-07-21

Updated:

* refactoring on how to create a new autogen agent
* different fixes at endpoint level and ui

## 0.1.5 - 2025-07-17

Updated:

* different fixes at ui level (including admin view)
* make sure that sessions are persisted per agent type and user id

## 0.1.4 - 2025-07-13

Updated

* Different features to stabilize the new modern ui

## 0.1.1 - 2025-07-12

Added

* A new more modern ui interface accessible at /ui
* A new endpoint to server the new ui interface

## [0.1.0][0.1.0] - 2025-01-XX

### Added

- Initial release of Agent Framework
- **Core Framework Features:**

  - Abstract `AgentInterface` for building custom agents
  - FastAPI-based server with automatic session management
  - Multi-provider AI model support (OpenAI, Gemini)
  - Automatic model routing and configuration
  - Session-based conversation handling with persistence
  - Streaming response support
  - Multi-modal input support (text, images, files)
- **Session Management:**

  - Memory-based and MongoDB session storage backends
  - Automatic agent state persistence using proxy pattern
  - Session workflow with init/end endpoints
  - Correlation ID support for linking sessions across agents
  - Session metadata and configuration management
- **Agent Features:**

  - AutoGen-based base agent implementation
  - System prompt configuration and templating
  - Dynamic agent configuration (temperature, tokens, etc.)
  - Media detection in agent responses
  - Multi-agent conversation support
  - MCP (Model Context Protocol) integration
- **Authentication & Security:**

  - Basic authentication support
  - API key authentication
  - Configurable authentication requirements
- **User Experience:**

  - Built-in web test interface (`/testapp`)
  - User feedback system (thumbs up/down, session flags)
  - Comprehensive API documentation
  - Response time tracking and analytics
  - Real-time streaming endpoints
- **Library Usage:**

  - Convenience function `create_basic_agent_server()` for easy setup
  - Pip installable from GitHub repositories
  - Extensive examples and documentation
- **Developer Tools:**

  - Comprehensive test suite with fixtures
  - Debug logging with configurable levels
  - Model configuration validation endpoints
  - MongoDB integration with automatic indexing
  - Docker support and examples

### Dependencies

- fastapi>=0.115.12
- autogen-agentchat>=0.6.4
- autogen-core>=0.6.4
- autogen-ext[mcp,openai]>=0.6.4
- uvicorn>=0.34.2
- pymongo>=4.10.1
- motor>=3.6.0
- And other supporting libraries

### Requirements

- Python 3.10 or higher
- Optional: MongoDB for persistent session storage
- API keys for OpenAI and/or Gemini models

[Unreleased]: https://github.com/Cinco-AI/AgentFramework/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Cinco-AI/AgentFramework/releases/tag/v0.1.0
