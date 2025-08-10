"""Tests for the asynchronous client."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx

from mesh_sdk import AsyncMeshClient
from mesh_sdk.exceptions import (
    AuthenticationError,
    NetworkError,
    TimeoutError,
)
from mesh_sdk.models import Agent, AgentType


@pytest.mark.asyncio
class TestAsyncMeshClient:
    """Test cases for AsyncMeshClient."""

    async def test_client_initialization(self, api_key, base_url):
        """Test async client initialization."""
        client = AsyncMeshClient(api_key=api_key, base_url=base_url)
        
        assert client.api_key == api_key
        assert client.base_url == base_url
        assert client.timeout == 60.0
        assert client.max_retries == 3

    async def test_context_manager(self, async_client):
        """Test async client as context manager."""
        async with async_client as c:
            assert c is async_client

    @patch('mesh_sdk.async_client.httpx.AsyncClient')
    async def test_list_agents(self, mock_httpx_client, async_client, mock_agent_data, mock_tool_data):
        """Test listing agents asynchronously."""
        # Mock the HTTP client
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value = mock_client_instance
        async_client._client = mock_client_instance
        
        # Mock responses for tools and agents endpoints
        tools_response = Mock()
        tools_response.is_success = True
        tools_response.json.return_value = [mock_tool_data]
        
        agents_response = Mock()
        agents_response.is_success = True
        agents_response.json.return_value = [mock_agent_data]
        
        mock_client_instance.request.side_effect = [tools_response, agents_response]
        
        # Call the method
        agents = await async_client.list_agents()
        
        # Verify results
        assert len(agents) == 2
        assert all(isinstance(agent, Agent) for agent in agents)
        assert agents[0].id == mock_tool_data["id"]
        assert agents[1].id == mock_agent_data["id"]

    @patch('mesh_sdk.async_client.httpx.AsyncClient')
    async def test_list_tools(self, mock_httpx_client, async_client, mock_tool_data):
        """Test listing tools asynchronously."""
        # Mock the HTTP client
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value = mock_client_instance
        async_client._client = mock_client_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = [mock_tool_data]
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        tools = await async_client.list_tools()
        
        # Verify results
        assert len(tools) == 1
        assert isinstance(tools[0], Agent)
        assert tools[0].id == mock_tool_data["id"]
        assert tools[0].type == AgentType.TOOL

    @patch('mesh_sdk.async_client.httpx.AsyncClient')
    async def test_list_llms(self, mock_httpx_client, async_client, mock_llm_data, mock_agent_data):
        """Test listing LLMs asynchronously."""
        # Mock the HTTP client
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value = mock_client_instance
        async_client._client = mock_client_instance
        
        # Mock response with mixed agent types
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = [mock_llm_data, mock_agent_data]
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        llms = await async_client.list_llms()
        
        # Verify results - should only return LLMs
        assert len(llms) == 1
        assert isinstance(llms[0], Agent)
        assert llms[0].id == mock_llm_data["id"]
        assert llms[0].type == AgentType.LLM

    @patch('mesh_sdk.async_client.httpx.AsyncClient')
    async def test_call_agent(self, mock_httpx_client, async_client):
        """Test calling an agent asynchronously."""
        # Mock the HTTP client
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value = mock_client_instance
        async_client._client = mock_client_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"data": {"result": "success"}}
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        response = await async_client.call_agent(
            agent_id="test-agent",
            inputs={"query": "test"},
            validate_inputs=False  # Skip validation for this test
        )
        
        # Verify results
        assert response.data["result"] == "success"

    @patch('mesh_sdk.async_client.httpx.AsyncClient')
    async def test_chat_completions(self, mock_httpx_client, async_client, mock_chat_completion_response):
        """Test chat completions asynchronously."""
        # Mock the HTTP client
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value = mock_client_instance
        async_client._client = mock_client_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_chat_completion_response
        mock_client_instance.request.return_value = mock_response
        
        # Call the method
        messages = [{"role": "user", "content": "Hello!"}]
        response = await async_client.chat_completions(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        # Verify results
        assert response.id == "chatcmpl-123"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Hello! How can I help you?"

    @patch('mesh_sdk.async_client.httpx.AsyncClient')
    async def test_network_error_handling(self, mock_httpx_client, async_client):
        """Test handling of network errors asynchronously."""
        # Mock the HTTP client
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value = mock_client_instance
        async_client._client = mock_client_instance
        
        # Mock network error
        mock_client_instance.request.side_effect = httpx.NetworkError("Connection failed")
        
        # Should raise NetworkError
        with pytest.raises(NetworkError, match="Network error"):
            await async_client.list_tools()

    @patch('mesh_sdk.async_client.httpx.AsyncClient')
    async def test_timeout_error_handling(self, mock_httpx_client, async_client):
        """Test handling of timeout errors asynchronously."""
        # Mock the HTTP client
        mock_client_instance = AsyncMock()
        mock_httpx_client.return_value = mock_client_instance
        async_client._client = mock_client_instance
        
        # Mock timeout error
        mock_client_instance.request.side_effect = httpx.TimeoutException("Request timed out")
        
        # Should raise TimeoutError
        with pytest.raises(TimeoutError, match="Request timed out"):
            await async_client.list_tools()