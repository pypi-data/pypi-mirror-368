# Mesh SDK

[![PyPI version](https://badge.fury.io/py/ai-mesh-sdk.svg)](https://badge.fury.io/py/ai-mesh-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/ai-mesh-sdk.svg)](https://pypi.org/project/ai-mesh-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/your-org/mesh-sdk/actions/workflows/test.yml/badge.svg)](https://github.com/your-org/mesh-sdk/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Professional Python SDK for the Mesh AI Platform. Easily integrate AI agents, tools, and LLMs into your Python applications with both synchronous and asynchronous support.

## Features

- 🚀 **Easy to use**: Simple, intuitive API design
- ⚡ **Async support**: Full async/await support for high-performance applications  
- 🛡️ **Type safe**: Comprehensive type hints with Pydantic models
- 🔄 **Retry logic**: Built-in exponential backoff for robust API calls
- 📝 **Comprehensive logging**: Detailed logging for debugging and monitoring
- 🧪 **Well tested**: Extensive test suite with >95% coverage
- 🔌 **LangChain integration**: Optional integration with LangChain framework
- 🎯 **Multiple agent types**: Support for LLMs, autonomous agents, and tools

## Installation

### Basic Installation

```bash
pip install ai-mesh-sdk
```

### With Optional Dependencies

```bash
# With LangChain integration
pip install ai-mesh-sdk[langchain]

# For development
pip install ai-mesh-sdk[dev]

# All optional dependencies
pip install ai-mesh-sdk[langchain,dev]
```

## Quick Start

### Synchronous Client

```python
import os
from mesh_sdk import MeshClient

# Initialize the client
client = MeshClient(api_key=os.getenv("MESH_API_KEY"))

# List available agents
agents = client.list_agents()
print(f"Found {len(agents)} agents")

# Call an agent
response = client.call_agent(
    agent_id="your-agent-id", 
    inputs={"query": "What is the weather today?"}
)
print(response.data)

# Chat completions (OpenAI-compatible)
messages = [{"role": "user", "content": "Hello!"}]
response = client.chat_completions(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.7
)
print(response.choices[0].message.content)
```

### Asynchronous Client

```python
import asyncio
from mesh_sdk import AsyncMeshClient

async def main():
    # Initialize async client
    async with AsyncMeshClient(api_key=os.getenv("MESH_API_KEY")) as client:
        
        # List agents asynchronously
        agents = await client.list_agents()
        print(f"Found {len(agents)} agents")
        
        # Call agent asynchronously  
        response = await client.call_agent(
            agent_id="your-agent-id",
            inputs={"query": "Analyze this data"}
        )
        print(response.data)
        
        # Async chat completions
        messages = [{"role": "user", "content": "Hello!"}]
        response = await client.chat_completions(
            model="gpt-4",
            messages=messages
        )
        print(response.choices[0].message.content)

# Run the async function
asyncio.run(main())
```

### Streaming Responses

```python
# Streaming chat completions
messages = [{"role": "user", "content": "Tell me a story"}]

for chunk in client.chat_completions(
    model="gpt-3.5-turbo",
    messages=messages,
    stream=True
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Agent Types

The Mesh platform supports three types of agents:

### 1. LLMs (Large Language Models)
Direct access to language models via OpenAI-compatible chat completions:

```python
# List available LLMs
llms = client.list_llms()

# Use with chat completions
response = client.chat_completions(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 2. Tools
Specialized functions that perform specific tasks:

```python
# List available tools
tools = client.list_tools()

# Call a tool
response = client.call_agent(
    agent_id="search-tool-123",
    inputs={"query": "Python programming", "max_results": 10}
)
```

### 3. Autonomous Agents
Complex workflows that can use multiple tools and make decisions:

```python
# List workflow agents
workflows = client.list_workflow_agents()

# Execute a workflow
response = client.call_agent(
    agent_id="data-analysis-workflow-456", 
    inputs={"dataset_url": "https://example.com/data.csv"}
)
```

## LangChain Integration

Mesh SDK provides seamless integration with LangChain:

```python
from mesh_sdk import MeshClient
from mesh_sdk.integrations.langchain import to_langchain_tools

# Initialize client
client = MeshClient(api_key="your-api-key")

# Convert Mesh agents to LangChain tools
tools = to_langchain_tools(client)

# Use with LangChain agents
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

# Get a prompt template
prompt = hub.pull("hwchase17/react")

# Create LangChain agent (you'll need a separate LLM)
agent = create_react_agent(your_llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Execute
response = agent_executor.invoke({
    "input": "Search for information about climate change"
})
```

## Configuration

### Environment Variables

```bash
export MESH_API_KEY="your-api-key-here"
export MESH_BASE_URL="https://api.meshcore.ai"  # Optional, defaults to official API
```

### Client Configuration

```python
from mesh_sdk import MeshClient

client = MeshClient(
    api_key="your-api-key",
    base_url="https://api.meshcore.ai",  # Custom API endpoint
    timeout=60.0,  # Request timeout in seconds
    max_retries=3,  # Max retries for failed requests
    retry_delay=1.0  # Base delay between retries
)
```

## Error Handling

The SDK provides specific exceptions for different error scenarios:

```python
from mesh_sdk import MeshClient
from mesh_sdk.exceptions import (
    AuthenticationError,
    AuthorizationError, 
    RateLimitError,
    ValidationError,
    APIError,
    NetworkError,
    TimeoutError
)

client = MeshClient(api_key="your-api-key")

try:
    agents = client.list_agents()
except AuthenticationError:
    print("Invalid API key")
except AuthorizationError:
    print("Access denied")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid input: {e}")
except NetworkError:
    print("Network connection failed")
except TimeoutError:
    print("Request timed out")
except APIError as e:
    print(f"API error: {e}")
```

## Logging

The SDK uses Python's standard logging module:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('mesh_sdk')
logger.setLevel(logging.INFO)
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/your-org/mesh-sdk.git
cd mesh-sdk
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mesh_sdk --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code  
ruff src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Examples

See the [examples/](examples/) directory for complete example applications:

- [Basic Usage](examples/basic_usage.py) - Simple synchronous example
- [Async Usage](examples/async_usage.py) - Asynchronous client example  
- [LangChain Integration](examples/langchain_integration.py) - Using with LangChain
- [Error Handling](examples/error_handling.py) - Comprehensive error handling
- [Streaming](examples/streaming.py) - Streaming responses

## API Reference

### MeshClient

The main synchronous client for the Mesh API.

#### Methods

- `list_agents()` → `List[Agent]` - List all agents and tools (excluding LLMs)
- `list_tools()` → `List[Agent]` - List only tools
- `list_workflow_agents()` → `List[Agent]` - List only workflow agents
- `list_all_agents()` → `List[Agent]` - List all agent types including LLMs
- `list_llms()` → `List[Agent]` - List only LLMs
- `call_agent(agent_id, inputs, validate_inputs=True)` → `AgentResponse` - Call an agent
- `chat_completions(model, messages, **kwargs)` → `ChatCompletionResponse` - Create chat completion

### AsyncMeshClient

Asynchronous version of MeshClient with the same methods as async functions.

### Models

- `Agent` - Represents an agent, tool, or LLM
- `ChatMessage` - Individual chat message
- `ChatCompletionRequest` - Request for chat completions
- `ChatCompletionResponse` - Response from chat completions
- `AgentResponse` - Response from agent calls

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run code quality tools (`black`, `ruff`, `mypy`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://mesh-sdk.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/your-org/mesh-sdk/issues)  
- 💬 [Discussions](https://github.com/your-org/mesh-sdk/discussions)
- 📧 [Email Support](mailto:support@meshcore.ai)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

Made with ❤️ by the Mesh AI Team