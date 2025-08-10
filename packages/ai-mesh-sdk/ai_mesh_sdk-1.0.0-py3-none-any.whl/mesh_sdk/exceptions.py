"""Custom exceptions for the Mesh SDK."""

from typing import Any, Dict, Optional


class MeshSDKError(Exception):
    """Base exception class for all Mesh SDK errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the exception.
        
        Args:
            message: The error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class AuthenticationError(MeshSDKError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs) -> None:
        super().__init__(message, **kwargs)


class AuthorizationError(MeshSDKError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed", **kwargs) -> None:
        super().__init__(message, **kwargs)


class APIError(MeshSDKError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the API error.
        
        Args:
            message: The error message
            status_code: HTTP status code
            response_body: Raw response body
            **kwargs: Additional details
        """
        details = kwargs.get("details", {})
        if status_code is not None:
            details["status_code"] = status_code
        if response_body is not None:
            details["response_body"] = response_body
        kwargs["details"] = details
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_body = response_body


class ValidationError(MeshSDKError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed", **kwargs) -> None:
        super().__init__(message, **kwargs)


class ConfigurationError(MeshSDKError):
    """Raised when there's a configuration issue."""

    def __init__(self, message: str = "Configuration error", **kwargs) -> None:
        super().__init__(message, **kwargs)


class NetworkError(MeshSDKError):
    """Raised when there's a network-related issue."""

    def __init__(self, message: str = "Network error", **kwargs) -> None:
        super().__init__(message, **kwargs)


class TimeoutError(MeshSDKError):
    """Raised when a request times out."""

    def __init__(self, message: str = "Request timed out", **kwargs) -> None:
        super().__init__(message, **kwargs)


class AgentNotFoundError(MeshSDKError):
    """Raised when an agent is not found."""

    def __init__(self, agent_id: str, **kwargs) -> None:
        message = f"Agent not found: {agent_id}"
        super().__init__(message, **kwargs)
        self.agent_id = agent_id


class InvalidResponseError(MeshSDKError):
    """Raised when the API returns an invalid response."""

    def __init__(self, message: str = "Invalid API response", **kwargs) -> None:
        super().__init__(message, **kwargs)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ) -> None:
        if retry_after is not None:
            details = kwargs.get("details", {})
            details["retry_after"] = retry_after
            kwargs["details"] = details
        super().__init__(message, **kwargs)
        self.retry_after = retry_after