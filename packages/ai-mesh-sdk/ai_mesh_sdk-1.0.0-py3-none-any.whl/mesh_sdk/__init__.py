"""Mesh SDK - Professional Python SDK for Mesh AI Platform."""

__version__ = "1.0.0"

from .client import MeshClient
from .async_client import AsyncMeshClient
from .models import (
    Agent,
    AgentType,
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    MessageRole,
    StreamingChatCompletionResponse,
)
from .exceptions import (
    MeshSDKError,
    APIError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    ConfigurationError,
    NetworkError,
    TimeoutError,
    AgentNotFoundError,
    InvalidResponseError,
    RateLimitError,
)

__all__ = [
    "__version__",
    # Clients
    "MeshClient",
    "AsyncMeshClient",
    # Models
    "Agent",
    "AgentType",
    "ChatMessage",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "MessageRole",
    "StreamingChatCompletionResponse",
    # Exceptions
    "MeshSDKError",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "ConfigurationError",
    "NetworkError",
    "TimeoutError",
    "AgentNotFoundError",
    "InvalidResponseError",
    "RateLimitError",
]

# Convenience alias for backward compatibility
MeshSDK = MeshClient