"""Input validation utilities for the Mesh SDK."""

from typing import Any, Dict, TYPE_CHECKING

from .exceptions import AgentNotFoundError, ValidationError

if TYPE_CHECKING:
    from .client import MeshClient
    from .async_client import AsyncMeshClient


def validate_agent_inputs(
    client: "MeshClient", 
    agent_id: str, 
    inputs: Dict[str, Any]
) -> None:
    """Validate input dictionary against agent's input schema.
    
    Args:
        client: Mesh client instance
        agent_id: ID of the agent
        inputs: Input dictionary to validate
        
    Raises:
        AgentNotFoundError: If agent is not found
        ValidationError: If validation fails
    """
    try:
        import jsonschema
    except ImportError:
        # jsonschema not available, skip validation
        return
    
    agents = client.list_all_agents()
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise AgentNotFoundError(agent_id)

    schema = agent.input_schema
    if schema:
        try:
            jsonschema.validate(instance=inputs, schema=schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Invalid inputs for agent {agent_id}: {e.message}") from e


async def validate_agent_inputs_async(
    client: "AsyncMeshClient", 
    agent_id: str, 
    inputs: Dict[str, Any]
) -> None:
    """Async version of validate_agent_inputs.
    
    Args:
        client: Async Mesh client instance
        agent_id: ID of the agent
        inputs: Input dictionary to validate
        
    Raises:
        AgentNotFoundError: If agent is not found
        ValidationError: If validation fails
    """
    try:
        import jsonschema
    except ImportError:
        # jsonschema not available, skip validation
        return
    
    agents = await client.list_all_agents()
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise AgentNotFoundError(agent_id)

    schema = agent.input_schema
    if schema:
        try:
            jsonschema.validate(instance=inputs, schema=schema)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Invalid inputs for agent {agent_id}: {e.message}") from e