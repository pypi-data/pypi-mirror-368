"""Pydantic models for the Mesh SDK."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import BaseModel, Field, validator


class AgentType(str, Enum):
    """Types of agents available in the Mesh platform."""
    
    LLM = "LLM"
    AGENT = "AGENT"
    TOOL = "TOOL"


class MessageRole(str, Enum):
    """Valid roles for chat messages."""
    
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """A single chat message."""
    
    role: MessageRole = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")

    class Config:
        use_enum_values = True


class Agent(BaseModel):
    """Represents an agent in the Mesh platform."""
    
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human-readable name of the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    type: Optional[AgentType] = Field(None, description="Type of the agent")
    input_schema: Optional[Dict[str, Any]] = Field(
        None, 
        description="JSON schema for agent inputs",
        alias="inputSchema"
    )
    example_inputs: Optional[Dict[str, Any]] = Field(
        None, 
        description="Example inputs for the agent",
        alias="exampleInputs"
    )
    
    # Additional fields that might be present in API responses
    price_per_token: Optional[float] = Field(
        None,
        description="Price per token for this agent",
        alias="pricePerToken"
    )

    class Config:
        use_enum_values = True
        populate_by_name = True  # Updated for Pydantic v2
        extra = "ignore"  # Ignore extra fields from API


class AgentCall(BaseModel):
    """Request to call an agent."""
    
    agent_id: str = Field(..., description="ID of the agent to call")
    inputs: Union[str, Dict[str, Any]] = Field(..., description="Inputs for the agent")


class ChatCompletionRequest(BaseModel):
    """Request for chat completions."""
    
    model: str = Field(..., description="Model identifier to use")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=2.0, 
        description="Sampling temperature (0-2)"
    )
    max_tokens: Optional[int] = Field(
        None, 
        gt=0, 
        description="Maximum tokens to generate"
    )
    stream: bool = Field(False, description="Whether to stream the response")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    top_p: Optional[float] = Field(
        None, 
        gt=0.0, 
        le=1.0, 
        description="Nucleus sampling parameter"
    )
    presence_penalty: Optional[float] = Field(
        None, 
        ge=-2.0, 
        le=2.0, 
        description="Presence penalty (-2 to 2)"
    )
    frequency_penalty: Optional[float] = Field(
        None, 
        ge=-2.0, 
        le=2.0, 
        description="Frequency penalty (-2 to 2)"
    )
    n: Optional[int] = Field(
        None, 
        gt=0, 
        description="Number of completions to generate"
    )
    user: Optional[str] = Field(None, description="User identifier")
    logit_bias: Optional[Dict[str, float]] = Field(
        None, 
        description="Token bias adjustments"
    )


class ChatCompletionChoice(BaseModel):
    """A single choice from a chat completion."""
    
    index: int = Field(..., description="Index of the choice")
    message: ChatMessage = Field(..., description="The message content")
    finish_reason: Optional[str] = Field(
        None, 
        description="Reason why the generation stopped"
    )


class ChatCompletionUsage(BaseModel):
    """Usage statistics for a chat completion."""
    
    prompt_tokens: int = Field(..., description="Tokens in the prompt")
    completion_tokens: int = Field(..., description="Tokens in the completion")
    total_tokens: int = Field(..., description="Total tokens used")


class ChatCompletionResponse(BaseModel):
    """Response from a chat completion request."""
    
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field(..., description="Object type (chat.completion)")
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="Model used for the completion")
    choices: List[ChatCompletionChoice] = Field(..., description="List of choices")
    usage: Optional[ChatCompletionUsage] = Field(None, description="Usage statistics")


class StreamingChatCompletionDelta(BaseModel):
    """Delta for streaming chat completions."""
    
    role: Optional[MessageRole] = Field(None, description="Role of the message")
    content: Optional[str] = Field(None, description="Content delta")

    class Config:
        use_enum_values = True


class StreamingChatCompletionChoice(BaseModel):
    """A single choice from a streaming chat completion."""
    
    index: int = Field(..., description="Index of the choice")
    delta: StreamingChatCompletionDelta = Field(..., description="Content delta")
    finish_reason: Optional[str] = Field(
        None, 
        description="Reason why the generation stopped"
    )


class StreamingChatCompletionResponse(BaseModel):
    """Response chunk from a streaming chat completion."""
    
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field(..., description="Object type (chat.completion.chunk)")
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="Model used for the completion")
    choices: List[StreamingChatCompletionChoice] = Field(
        ..., 
        description="List of choices"
    )


class ErrorResponse(BaseModel):
    """Error response from the API."""
    
    error: Dict[str, Any] = Field(..., description="Error details")
    
    @property
    def message(self) -> str:
        """Get the error message."""
        return self.error.get("message", "Unknown error")
    
    @property
    def type(self) -> Optional[str]:
        """Get the error type."""
        return self.error.get("type")
    
    @property
    def code(self) -> Optional[str]:
        """Get the error code."""
        return self.error.get("code")


class AgentResponse(BaseModel):
    """Response from calling an agent."""
    
    data: Dict[str, Any] = Field(..., description="Response data from the agent")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata"
    )