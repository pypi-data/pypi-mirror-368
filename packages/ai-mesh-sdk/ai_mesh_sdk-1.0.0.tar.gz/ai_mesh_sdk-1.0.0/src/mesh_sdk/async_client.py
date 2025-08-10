"""Async client for the Mesh SDK."""

import json
import logging
from typing import Any, AsyncIterator, Dict, List, Union

import httpx
from tenacity import (
    AsyncRetrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .client import BaseMeshClient
from .exceptions import (
    InvalidResponseError,
    NetworkError,
    TimeoutError,
)
from .models import (
    Agent,
    AgentCall,
    AgentResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    StreamingChatCompletionResponse,
)

logger = logging.getLogger(__name__)


class AsyncMeshClient(BaseMeshClient):
    """Asynchronous client for the Mesh API."""

    def __init__(self, **kwargs) -> None:
        """Initialize the async client."""
        super().__init__(**kwargs)
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._headers,
        )

    async def __aenter__(self) -> "AsyncMeshClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the async client."""
        await self._client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make an async HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type((NetworkError, TimeoutError)),
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        ):
            with attempt:
                try:
                    logger.debug(f"Making async {method} request to {url}")
                    response = await self._client.request(method, url, **kwargs)
                    
                    if not response.is_success:
                        self._handle_http_error(response)
                        
                    return response
                    
                except httpx.TimeoutException as e:
                    logger.error(f"Request timeout: {e}")
                    raise TimeoutError(f"Request timed out: {e}") from e
                except httpx.NetworkError as e:
                    logger.error(f"Network error: {e}")
                    raise NetworkError(f"Network error: {e}") from e

    async def list_agents(self) -> List[Agent]:
        """List agents and tools suitable for LangChain Tools integration.
        
        Returns:
            List of AGENT and TOOL type agents (excluding LLMs)
        """
        # Get tools and agents separately for backward compatibility
        tools_response, agents_response = await asyncio.gather(
            self._make_request("GET", "/public/tools"),
            self._make_request("GET", "/public/agents")
        )
        
        try:
            tools_data = tools_response.json()
            agents_data = agents_response.json()
            combined_data = tools_data + agents_data
            
            return [Agent(**item) for item in combined_data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    async def list_tools(self) -> List[Agent]:
        """List only TOOL type agents."""
        response = await self._make_request("GET", "/public/tools")
        
        try:
            data = response.json()
            return [Agent(**item) for item in data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    async def list_workflow_agents(self) -> List[Agent]:
        """List only AGENT type agents (workflows/autonomous agents)."""
        response = await self._make_request("GET", "/public/agents")
        
        try:
            data = response.json()
            return [Agent(**item) for item in data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    async def list_all_agents(self) -> List[Agent]:
        """List all agent types (LLM + AGENT + TOOL)."""
        response = await self._make_request("GET", "/public/all")
        
        try:
            data = response.json()
            return [Agent(**item) for item in data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    async def list_llms(self) -> List[Agent]:
        """List only LLM type agents for use with chat_completions."""
        all_agents = await self.list_all_agents()
        return [agent for agent in all_agents if agent.type and agent.type.value == "LLM"]

    async def call_agent(
        self,
        agent_id: str,
        inputs: Union[str, Dict[str, Any]],
        validate_inputs: bool = True,
    ) -> AgentResponse:
        """Call a Mesh agent asynchronously.
        
        Args:
            agent_id: ID of the agent to call
            inputs: Inputs for the agent
            validate_inputs: Whether to validate inputs against schema
            
        Returns:
            Agent response
        """
        if validate_inputs and isinstance(inputs, dict):
            await self._validate_agent_inputs(agent_id, inputs)

        agent_call = AgentCall(agent_id=agent_id, inputs=inputs)
        
        payload = {
            "agentId": agent_call.agent_id,
            "inputs": agent_call.inputs,
        }

        logger.debug(f"Calling agent {agent_id} with inputs: {inputs}")
        response = await self._make_request("POST", "/gateway/call", json=payload)

        try:
            data = response.json()
            return AgentResponse(data=data.get("data", {}))
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    async def chat_completions(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletionResponse, AsyncIterator[StreamingChatCompletionResponse]]:
        """Create a chat completion asynchronously.
        
        Args:
            model: Model identifier
            messages: List of messages
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response or async streaming iterator
        """
        # Convert dict messages to ChatMessage objects for validation
        from .models import ChatMessage
        chat_messages = [ChatMessage(**msg) for msg in messages]
        
        request = ChatCompletionRequest(
            model=model,
            messages=chat_messages,
            stream=stream,
            **kwargs
        )

        payload = request.dict(exclude_none=True)
        # Convert back to dict format for API
        payload["messages"] = [msg.dict() for msg in chat_messages]

        if stream:
            return self._stream_chat_completions(payload)
        else:
            response = await self._make_request(
                "POST", 
                "/v1/chat/completions", 
                json=payload
            )
            
            try:
                data = response.json()
                return ChatCompletionResponse(**data)
            except (json.JSONDecodeError, ValueError) as e:
                raise InvalidResponseError(f"Invalid response format: {e}") from e

    async def _stream_chat_completions(
        self, 
        payload: Dict[str, Any]
    ) -> AsyncIterator[StreamingChatCompletionResponse]:
        """Stream chat completion responses asynchronously."""
        url = f"{self.base_url}/v1/chat/completions"
        
        async with self._client.stream(
            "POST", 
            url, 
            json=payload,
            headers=self._headers
        ) as response:
            if not response.is_success:
                self._handle_http_error(response)
                
            async for line in response.aiter_lines():
                if line and line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        yield StreamingChatCompletionResponse(**data)
                    except (json.JSONDecodeError, ValueError):
                        continue

    async def _validate_agent_inputs(
        self, 
        agent_id: str, 
        inputs: Dict[str, Any]
    ) -> None:
        """Validate input dictionary against agent's input schema."""
        from .validation import validate_agent_inputs_async
        await validate_agent_inputs_async(self, agent_id, inputs)


# Import asyncio at the end to avoid circular imports
import asyncio