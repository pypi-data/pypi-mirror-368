"""Main client for the Mesh SDK."""

import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    InvalidResponseError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)
from .models import (
    Agent,
    AgentCall,
    AgentResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
    StreamingChatCompletionResponse,
)

logger = logging.getLogger(__name__)


class BaseMeshClient:
    """Base class for Mesh clients."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.meshcore.ai",
        timeout: float = 60.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize the client.
        
        Args:
            api_key: Your Mesh API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay between retries in seconds
        """
        if not api_key:
            raise ValueError("API key is required and cannot be empty")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "User-Agent": f"mesh-sdk-python/{self._get_version()}",
        }

    def _get_version(self) -> str:
        """Get the SDK version."""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"

    def _handle_http_error(self, response: httpx.Response) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        try:
            error_data = response.json()
            error_response = ErrorResponse(**error_data)
            message = error_response.message
        except (json.JSONDecodeError, ValueError):
            message = f"HTTP {response.status_code}: {response.text}"
            
        if response.status_code == 401:
            raise AuthenticationError(
                message, 
                status_code=response.status_code,
                response_body=response.text
            )
        elif response.status_code == 403:
            raise AuthorizationError(
                message,
                status_code=response.status_code, 
                response_body=response.text
            )
        elif response.status_code == 429:
            retry_after = None
            if "retry-after" in response.headers:
                try:
                    retry_after = int(response.headers["retry-after"])
                except ValueError:
                    pass
            raise RateLimitError(
                message,
                status_code=response.status_code,
                response_body=response.text,
                retry_after=retry_after,
            )
        elif response.status_code >= 500:
            raise APIError(
                f"Server error: {message}",
                status_code=response.status_code,
                response_body=response.text,
            )
        else:
            raise APIError(
                message,
                status_code=response.status_code,
                response_body=response.text,
            )


class MeshClient(BaseMeshClient):
    """Synchronous client for the Mesh API."""

    def __init__(self, **kwargs) -> None:
        """Initialize the synchronous client."""
        super().__init__(**kwargs)
        self._client = httpx.Client(
            timeout=self.timeout,
            headers=self._headers,
        )

    def __enter__(self) -> "MeshClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    @retry(
        retry=retry_if_exception_type((NetworkError, APIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make an HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            response = self._client.request(method, url, **kwargs)
            
            if not response.is_success:
                self._handle_http_error(response)
                
            return response
            
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise NetworkError(f"Network error: {e}") from e

    def list_agents(self) -> List[Agent]:
        """List agents and tools suitable for LangChain Tools integration.
        
        Returns:
            List of AGENT and TOOL type agents (excluding LLMs)
        """
        # Get tools and agents separately for backward compatibility
        tools_response = self._make_request("GET", "/public/tools")
        agents_response = self._make_request("GET", "/public/agents")
        
        try:
            tools_data = tools_response.json()
            agents_data = agents_response.json()
            combined_data = tools_data + agents_data
            
            return [Agent(**item) for item in combined_data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    def list_tools(self) -> List[Agent]:
        """List only TOOL type agents."""
        response = self._make_request("GET", "/public/tools")
        
        try:
            data = response.json()
            return [Agent(**item) for item in data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    def list_workflow_agents(self) -> List[Agent]:
        """List only AGENT type agents (workflows/autonomous agents)."""
        response = self._make_request("GET", "/public/agents")
        
        try:
            data = response.json()
            return [Agent(**item) for item in data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    def list_all_agents(self) -> List[Agent]:
        """List all agent types (LLM + AGENT + TOOL)."""
        response = self._make_request("GET", "/public/all")
        
        try:
            data = response.json()
            return [Agent(**item) for item in data]
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    def list_llms(self) -> List[Agent]:
        """List only LLM type agents for use with chat_completions."""
        all_agents = self.list_all_agents()
        return [agent for agent in all_agents if agent.type and agent.type.value == "LLM"]

    def call_agent(
        self,
        agent_id: str,
        inputs: Union[str, Dict[str, Any]],
        validate_inputs: bool = True,
    ) -> AgentResponse:
        """Call a Mesh agent.
        
        Args:
            agent_id: ID of the agent to call
            inputs: Inputs for the agent
            validate_inputs: Whether to validate inputs against schema
            
        Returns:
            Agent response
        """
        if validate_inputs and isinstance(inputs, dict):
            self._validate_agent_inputs(agent_id, inputs)

        agent_call = AgentCall(agent_id=agent_id, inputs=inputs)
        
        payload = {
            "agentId": agent_call.agent_id,
            "inputs": agent_call.inputs,
        }

        logger.debug(f"Calling agent {agent_id} with inputs: {inputs}")
        response = self._make_request("POST", "/gateway/call", json=payload)

        try:
            data = response.json()
            return AgentResponse(data=data.get("data", {}))
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidResponseError(f"Invalid response format: {e}") from e

    def chat_completions(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletionResponse, Iterator[StreamingChatCompletionResponse]]:
        """Create a chat completion.
        
        Args:
            model: Model identifier
            messages: List of messages
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response or streaming iterator
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
            response = self._make_request(
                "POST", 
                "/v1/chat/completions", 
                json=payload
            )
            
            try:
                data = response.json()
                return ChatCompletionResponse(**data)
            except (json.JSONDecodeError, ValueError) as e:
                raise InvalidResponseError(f"Invalid response format: {e}") from e

    def _stream_chat_completions(
        self, 
        payload: Dict[str, Any]
    ) -> Iterator[StreamingChatCompletionResponse]:
        """Stream chat completion responses."""
        url = f"{self.base_url}/v1/chat/completions"
        
        with self._client.stream(
            "POST", 
            url, 
            json=payload,
            headers=self._headers
        ) as response:
            if not response.is_success:
                self._handle_http_error(response)
                
            for line in response.iter_lines():
                if line and line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        yield StreamingChatCompletionResponse(**data)
                    except (json.JSONDecodeError, ValueError):
                        continue

    def _validate_agent_inputs(
        self, 
        agent_id: str, 
        inputs: Dict[str, Any]
    ) -> None:
        """Validate input dictionary against agent's input schema."""
        from .validation import validate_agent_inputs
        validate_agent_inputs(self, agent_id, inputs)