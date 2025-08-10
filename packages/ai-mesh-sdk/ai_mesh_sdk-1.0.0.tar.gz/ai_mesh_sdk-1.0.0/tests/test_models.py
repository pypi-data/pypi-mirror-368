"""Tests for the Pydantic models."""

import pytest
from pydantic import ValidationError

from mesh_sdk.models import (
    Agent,
    AgentType,
    ChatMessage,
    MessageRole,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    StreamingChatCompletionResponse,
    ErrorResponse,
)


class TestAgent:
    """Test Agent model."""

    def test_agent_creation_minimal(self):
        """Test creating an agent with minimal data."""
        agent = Agent(
            id="test-123",
            name="Test Agent",
            type=AgentType.AGENT
        )
        assert agent.id == "test-123"
        assert agent.name == "Test Agent"
        assert agent.type == AgentType.AGENT
        assert agent.description is None
        assert agent.input_schema is None

    def test_agent_creation_full(self):
        """Test creating an agent with all fields."""
        input_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        }
        
        agent = Agent(
            id="test-123",
            name="Test Agent",
            description="A test agent",
            type=AgentType.TOOL,
            input_schema=input_schema,
            example_inputs={"query": "test"}
        )
        
        assert agent.id == "test-123"
        assert agent.name == "Test Agent"
        assert agent.description == "A test agent"
        assert agent.type == AgentType.TOOL
        assert agent.input_schema == input_schema
        assert agent.example_inputs == {"query": "test"}

    def test_agent_type_validation(self):
        """Test agent type validation."""
        # Valid types should work
        for agent_type in [AgentType.LLM, AgentType.AGENT, AgentType.TOOL]:
            agent = Agent(id="test", name="Test", type=agent_type)
            assert agent.type == agent_type

        # Invalid type should raise error
        with pytest.raises(ValidationError):
            Agent(id="test", name="Test", type="INVALID")

    def test_agent_alias_fields(self):
        """Test agent field aliases."""
        # Test inputSchema alias
        agent = Agent(
            id="test",
            name="Test",
            type=AgentType.AGENT,
            inputSchema={"type": "object"}  # Using alias
        )
        assert agent.input_schema == {"type": "object"}
        
        # Test exampleInputs alias
        agent = Agent(
            id="test",
            name="Test", 
            type=AgentType.AGENT,
            exampleInputs={"test": "value"}  # Using alias
        )
        assert agent.example_inputs == {"test": "value"}


class TestChatMessage:
    """Test ChatMessage model."""

    def test_chat_message_creation(self):
        """Test creating a chat message."""
        message = ChatMessage(
            role=MessageRole.USER,
            content="Hello, world!"
        )
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"

    def test_chat_message_role_validation(self):
        """Test chat message role validation."""
        # Valid roles should work
        for role in [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT]:
            message = ChatMessage(role=role, content="Test")
            assert message.role == role

        # Invalid role should raise error
        with pytest.raises(ValidationError):
            ChatMessage(role="invalid", content="Test")

    def test_chat_message_string_conversion(self):
        """Test that enum values are properly converted to strings."""
        message = ChatMessage(role=MessageRole.USER, content="Test")
        message_dict = message.dict()
        assert message_dict["role"] == "user"  # Should be string, not enum


class TestChatCompletionRequest:
    """Test ChatCompletionRequest model."""

    def test_chat_completion_request_minimal(self):
        """Test creating a chat completion request with minimal data."""
        messages = [ChatMessage(role=MessageRole.USER, content="Hello")]
        request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=messages
        )
        assert request.model == "gpt-3.5-turbo"
        assert len(request.messages) == 1
        assert request.stream is False  # Default value

    def test_chat_completion_request_full(self):
        """Test creating a chat completion request with all fields."""
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="You are helpful"),
            ChatMessage(role=MessageRole.USER, content="Hello")
        ]
        
        request = ChatCompletionRequest(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=100,
            stream=True,
            stop=["END"],
            top_p=0.9,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            n=2,
            user="user123",
            logit_bias={"token": 0.5}
        )
        
        assert request.model == "gpt-4"
        assert len(request.messages) == 2
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.stream is True
        assert request.stop == ["END"]
        assert request.top_p == 0.9
        assert request.presence_penalty == 0.1
        assert request.frequency_penalty == 0.1
        assert request.n == 2
        assert request.user == "user123"
        assert request.logit_bias == {"token": 0.5}

    def test_chat_completion_request_validation(self):
        """Test chat completion request validation."""
        messages = [ChatMessage(role=MessageRole.USER, content="Test")]
        
        # Temperature out of range
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=3.0  # > 2.0
            )
        
        # Negative max_tokens
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=-1
            )
        
        # top_p out of range
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                model="gpt-3.5-turbo",
                messages=messages,
                top_p=1.5  # > 1.0
            )


class TestChatCompletionResponse:
    """Test ChatCompletionResponse model."""

    def test_chat_completion_response_creation(self):
        """Test creating a chat completion response."""
        choice = ChatCompletionChoice(
            index=0,
            message=ChatMessage(role=MessageRole.ASSISTANT, content="Hello!"),
            finish_reason="stop"
        )
        
        response = ChatCompletionResponse(
            id="chatcmpl-123",
            object="chat.completion",
            created=1677652288,
            model="gpt-3.5-turbo",
            choices=[choice]
        )
        
        assert response.id == "chatcmpl-123"
        assert response.object == "chat.completion"
        assert response.created == 1677652288
        assert response.model == "gpt-3.5-turbo"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Hello!"


class TestStreamingChatCompletionResponse:
    """Test StreamingChatCompletionResponse model."""

    def test_streaming_response_creation(self):
        """Test creating a streaming chat completion response."""
        from mesh_sdk.models import StreamingChatCompletionChoice, StreamingChatCompletionDelta
        
        delta = StreamingChatCompletionDelta(
            role=MessageRole.ASSISTANT,
            content="Hello"
        )
        
        choice = StreamingChatCompletionChoice(
            index=0,
            delta=delta,
            finish_reason=None
        )
        
        response = StreamingChatCompletionResponse(
            id="chatcmpl-123",
            object="chat.completion.chunk",
            created=1677652288,
            model="gpt-3.5-turbo",
            choices=[choice]
        )
        
        assert response.id == "chatcmpl-123"
        assert response.object == "chat.completion.chunk"
        assert len(response.choices) == 1
        assert response.choices[0].delta.content == "Hello"


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_error_response_creation(self):
        """Test creating an error response."""
        error_data = {
            "error": {
                "message": "Invalid API key",
                "type": "authentication_error",
                "code": "invalid_api_key"
            }
        }
        
        response = ErrorResponse(**error_data)
        
        assert response.message == "Invalid API key"
        assert response.type == "authentication_error"
        assert response.code == "invalid_api_key"

    def test_error_response_minimal(self):
        """Test error response with minimal data."""
        error_data = {
            "error": {
                "message": "Something went wrong"
            }
        }
        
        response = ErrorResponse(**error_data)
        
        assert response.message == "Something went wrong"
        assert response.type is None
        assert response.code is None

    def test_error_response_missing_message(self):
        """Test error response without message."""
        error_data = {
            "error": {
                "type": "unknown_error"
            }
        }
        
        response = ErrorResponse(**error_data)
        
        assert response.message == "Unknown error"
        assert response.type == "unknown_error"