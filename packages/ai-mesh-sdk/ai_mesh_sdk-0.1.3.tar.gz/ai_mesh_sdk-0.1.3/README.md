
# AI Mesh SDK

A lightweight Python SDK for discovering and calling agents on the AI Mesh platform.

## Features
- List available agents on the mesh
- Call any agent by ID with custom inputs
- **Input validation** using JSON Schema (when available)
- Convert all Mesh agents into LangChain-compatible tools
- Auto-generated parameter documentation
- Simple authentication with API tokens

## Installation

```bash
pip install ai-mesh-sdk
```

## Quick Start

```python
from mesh_sdk import MeshSDK

# Initialize with your API token
sdk = MeshSDK(token="your-api-token")

# List all available agents
agents = sdk.list_agents()
print(f"Found {len(agents)} agents")

# Call a specific agent
result = sdk.call_agent(
    agent_id="agent-123",
    inputs={"prompt": "Hello, world!"}
)
print(result)

# Use with LangChain
from langchain.agents import initialize_agent, AgentType

tools = sdk.to_langchain_tools()
agent = initialize_agent(
    tools=tools,
    llm=your_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)
```

## API Reference

### MeshSDK(token)
Initialize the SDK with your API token.

**Parameters:**
- `token` (str): Your AI Mesh API token

### list_agents()
Returns a list of all available agents on the mesh.

**Returns:** List[Dict] - Agent metadata including ID, name, and description

### call_agent(agent_id, inputs, validate_inputs=True)
Call a specific agent with provided inputs.

**Parameters:**
- `agent_id` (str): The unique identifier of the agent
- `inputs` (Dict): Input parameters for the agent
- `validate_inputs` (bool): Whether to validate inputs against schema (default: True)

**Returns:** Dict - The agent's response

**Input Validation:**
If an agent has an `inputSchema`, the SDK will automatically validate your inputs:

```python
# This will validate inputs against the agent's schema
result = sdk.call_agent("summarizer", {
    "text": "Long text to summarize...",
    "max_length": 100
})

# Skip validation if needed
result = sdk.call_agent("summarizer", inputs, validate_inputs=False)
```

### to_langchain_tools()
Convert all mesh agents into LangChain Tool objects with automatic input validation.

**Returns:** List[Tool] - LangChain-compatible tools

**Enhanced Tool Descriptions:**
Tools automatically include parameter information from the agent's schema:

```python
tools = sdk.to_langchain_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Output example:
# Summarizer: Summarizes long text into concise summaries
# 
# Parameters: text: string (required), max_length: integer (optional)
```

## Agent Schema Format

For optimal validation, agents should include an `inputSchema` in their metadata:

```json
{
  "id": "summarizer",
  "name": "Text Summarizer", 
  "description": "Summarizes long text into concise summaries",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "The text to summarize"
      },
      "max_length": {
        "type": "integer", 
        "description": "Maximum length of summary",
        "default": 100
      }
    },
    "required": ["text"]
  }
}
```

**Fallback:** If no `inputSchema` is available, the SDK will look for `exampleInputs` and include those in the tool description.

## License

MIT License