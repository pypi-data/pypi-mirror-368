"""LangChain integration for the Mesh SDK."""

from typing import Any, Dict, List, TYPE_CHECKING

try:
    from langchain.agents import Tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

if TYPE_CHECKING:
    from ..client import MeshClient


def to_langchain_tools(client: "MeshClient") -> List["Tool"]:
    """Convert Mesh agents to LangChain Tools.
    
    This method fetches both AGENT and TOOL types (excluding LLMs)
    and converts them to LangChain Tool objects for use in agents.
    
    Args:
        client: Mesh client instance
        
    Returns:
        List of LangChain Tool objects for agents and tools
        
    Raises:
        ImportError: If LangChain is not installed
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain is not installed. Install it with: pip install mesh-sdk[langchain]"
        )
    
    tools = []
    agents = client.list_agents()

    for agent in agents:
        agent_id = agent.id
        name = agent.name.replace(" ", "_")
        description = _format_schema_description(agent)
        schema = agent.input_schema

        def make_tool_func(aid=agent_id, input_schema=schema):
            def tool_fn(query=None, **kwargs):
                # If only a query is passed and nothing else, use it as raw string input
                if query is not None and not kwargs:
                    inputs = query
                else:
                    inputs = dict(kwargs)
                    if query is not None:
                        inputs["query"] = query

                if isinstance(inputs, dict) and input_schema:
                    try:
                        import jsonschema
                        jsonschema.validate(instance=inputs, schema=input_schema)
                    except ImportError:
                        # jsonschema not available, skip validation
                        pass
                    except jsonschema.ValidationError as e:
                        raise ValueError(f"Invalid inputs: {e.message}") from e

                response = client.call_agent(aid, inputs, validate_inputs=False)
                return response.data
            return tool_fn

        tools.append(Tool(
            name=name,
            func=make_tool_func(),
            description=description
        ))

    return tools


def _format_schema_description(agent) -> str:
    """Generate a tool description with parameter info from schema."""
    description = agent.description or ""
    schema = agent.input_schema or {}
    
    if schema and "properties" in schema:
        required = schema.get("required", [])
        param_descriptions = [
            f"{name}: {prop.get('type', 'any')}{' (required)' if name in required else ' (optional)'}"
            for name, prop in schema["properties"].items()
        ]
        description += f"\n\nParameters: {', '.join(param_descriptions)}"
    elif agent.example_inputs:
        description += f"\n\nExample inputs: {agent.example_inputs}"
        
    return description