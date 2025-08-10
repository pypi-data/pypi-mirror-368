"""Tests for the synchronous client."""

import pytest
from unittest.mock import Mock, patch
import httpx

from mesh_sdk import MeshClient
from mesh_sdk.exceptions import (
    AuthenticationError,
    ValidationError,
    APIError,
    NetworkError,
    TimeoutError,
)
from mesh_sdk.models import Agent, AgentType, ChatMessage, MessageRole


class TestMeshClient:
    """Test cases for MeshClient."""

    def test_client_initialization(self, api_key, base_url):
        """Test client initialization."""
        client = MeshClient(api_key=api_key, base_url=base_url)
        
        assert client.api_key == api_key
        assert client.base_url == base_url
        assert client.timeout == 60.0
        assert client.max_retries == 3

    def test_client_initialization_with_empty_api_key(self):
        """Test client initialization with empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            MeshClient(api_key="")

    def test_context_manager(self, client):
        """Test client as context manager."""
        with client as c:
            assert c is client
        # Client should be closed after exiting context

    @patch('mesh_sdk.client.httpx.Client')
    def test_list_agents(self, mock_httpx_client, client, mock_agent_data, mock_tool_data):
        """Test listing agents."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock responses for tools and agents endpoints
        tools_response = Mock()
        tools_response.is_success = True
        tools_response.json.return_value = [mock_tool_data]
        
        agents_response = Mock()
        agents_response.is_success = True
        agents_response.json.return_value = [mock_agent_data]
        
        mock_client_instance.request.side_effect = [tools_response, agents_response]
        
        # Call the method
        agents = client.list_agents()
        
        # Verify results
        assert len(agents) == 2
        assert all(isinstance(agent, Agent) for agent in agents)
        assert agents[0].id == mock_tool_data["id"]
        assert agents[1].id == mock_agent_data["id"]

    @patch('mesh_sdk.client.httpx.Client')
    def test_list_tools(self, mock_httpx_client, client, mock_tool_data):
        """Test listing tools."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = [mock_tool_data]
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        tools = client.list_tools()
        
        # Verify results
        assert len(tools) == 1
        assert isinstance(tools[0], Agent)
        assert tools[0].id == mock_tool_data["id"]
        assert tools[0].type == AgentType.TOOL

    @patch('mesh_sdk.client.httpx.Client')
    def test_list_llms(self, mock_httpx_client, client, mock_llm_data, mock_agent_data):
        """Test listing LLMs."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock response with mixed agent types
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = [mock_llm_data, mock_agent_data]
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        llms = client.list_llms()
        
        # Verify results - should only return LLMs
        assert len(llms) == 1
        assert isinstance(llms[0], Agent)
        assert llms[0].id == mock_llm_data["id"]
        assert llms[0].type == AgentType.LLM

    @patch('mesh_sdk.client.httpx.Client')
    def test_call_agent(self, mock_httpx_client, client):
        """Test calling an agent."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"data": {"result": "success"}}
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        response = client.call_agent(
            agent_id="test-agent",
            inputs={"query": "test"},
            validate_inputs=False  # Skip validation for this test
        )
        
        # Verify results
        assert response.data["result"] == "success"

    @patch('mesh_sdk.client.httpx.Client')
    def test_chat_completions(self, mock_httpx_client, client, mock_chat_completion_response):
        """Test chat completions."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_chat_completion_response
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        messages = [{"role": "user", "content": "Hello!"}]
        response = client.chat_completions(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        # Verify results
        assert response.id == "chatcmpl-123"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Hello! How can I help you?"

    @patch('mesh_sdk.client.httpx.Client')
    def test_http_error_handling_401(self, mock_httpx_client, client):
        """Test handling of 401 authentication errors."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock 401 response
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.json.return_value = {
            "error": {"message": "Invalid API key"}
        }
        mock_client_instance.request.return_value = mock_response
        
        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.list_tools()

    @patch('mesh_sdk.client.httpx.Client')
    def test_network_error_handling(self, mock_httpx_client, client):
        """Test handling of network errors."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock network error
        mock_client_instance.request.side_effect = httpx.NetworkError("Connection failed")
        
        # Should raise NetworkError
        with pytest.raises(NetworkError, match="Network error"):
            client.list_tools()

    @patch('mesh_sdk.client.httpx.Client')
    def test_timeout_error_handling(self, mock_httpx_client, client):
        """Test handling of timeout errors."""
        # Mock the HTTP client
        mock_client_instance = Mock()
        mock_httpx_client.return_value = mock_client_instance
        client._client = mock_client_instance
        
        # Mock timeout error
        mock_client_instance.request.side_effect = httpx.TimeoutException("Request timed out")
        
        # Should raise TimeoutError
        with pytest.raises(TimeoutError, match="Request timed out"):
            client.list_tools()


class TestChatMessage:
    """Test ChatMessage model."""

    def test_chat_message_creation(self):
        """Test creating a chat message."""
        message = ChatMessage(role=MessageRole.USER, content="Hello!")
        assert message.role == MessageRole.USER
        assert message.content == "Hello!"

    def test_chat_message_validation(self):
        """Test chat message validation."""
        # Invalid role should raise validation error
        with pytest.raises(ValidationError):
            ChatMessage(role="invalid", content="Hello!")


class TestAgent:
    """Test Agent model."""

    def test_agent_creation(self, mock_agent_data):
        """Test creating an agent."""
        agent = Agent(**mock_agent_data)
        assert agent.id == mock_agent_data["id"]
        assert agent.name == mock_agent_data["name"]
        assert agent.type == AgentType.AGENT
        assert agent.input_schema == mock_agent_data["inputSchema"]

    def test_agent_type_validation(self):
        """Test agent type validation."""
        # Invalid type should raise validation error
        with pytest.raises(ValidationError):
            Agent(
                id="test",
                name="Test",
                type="INVALID_TYPE"
            )