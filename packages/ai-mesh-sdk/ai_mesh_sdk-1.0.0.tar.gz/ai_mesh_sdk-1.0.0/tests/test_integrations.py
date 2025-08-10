"""Tests for integrations."""

import pytest
from unittest.mock import Mock, patch

from mesh_sdk.integrations.langchain import to_langchain_tools, _format_schema_description
from mesh_sdk.models import Agent, AgentType


class TestLangChainIntegration:
    """Test LangChain integration."""

    @patch('mesh_sdk.integrations.langchain.LANGCHAIN_AVAILABLE', True)
    def test_to_langchain_tools_import_error(self):
        """Test handling when LangChain is not available."""
        # Mock that LangChain is not available
        with patch('mesh_sdk.integrations.langchain.LANGCHAIN_AVAILABLE', False):
            mock_client = Mock()
            
            with pytest.raises(ImportError, match="LangChain is not installed"):
                to_langchain_tools(mock_client)

    @patch('mesh_sdk.integrations.langchain.LANGCHAIN_AVAILABLE', True)
    @patch('mesh_sdk.integrations.langchain.Tool')
    def test_to_langchain_tools_success(self, mock_tool_class):
        """Test successful conversion to LangChain tools."""
        # Mock client and agents
        mock_client = Mock()
        mock_agent = Agent(
            id="test-agent",
            name="Test Agent",
            description="A test agent",
            type=AgentType.AGENT,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        )
        mock_client.list_agents.return_value = [mock_agent]
        mock_client.call_agent.return_value = Mock(data={"result": "success"})
        
        # Mock Tool class
        mock_tool_instance = Mock()
        mock_tool_class.return_value = mock_tool_instance
        
        # Call the function
        tools = to_langchain_tools(mock_client)
        
        # Verify results
        assert len(tools) == 1
        assert tools[0] == mock_tool_instance
        
        # Verify Tool was called with correct arguments
        mock_tool_class.assert_called_once()
        call_args = mock_tool_class.call_args
        assert call_args[1]["name"] == "Test_Agent"  # Spaces replaced with underscores
        assert "A test agent" in call_args[1]["description"]
        assert callable(call_args[1]["func"])

    def test_format_schema_description_with_schema(self):
        """Test formatting schema description with input schema."""
        agent = Agent(
            id="test",
            name="Test",
            type=AgentType.AGENT,
            description="Test agent",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["query"]
            }
        )
        
        description = _format_schema_description(agent)
        
        assert "Test agent" in description
        assert "Parameters:" in description
        assert "query: string (required)" in description
        assert "limit: integer (optional)" in description

    def test_format_schema_description_with_examples(self):
        """Test formatting schema description with example inputs."""
        agent = Agent(
            id="test",
            name="Test",
            type=AgentType.AGENT,
            description="Test agent",
            example_inputs={"query": "example query"}
        )
        
        description = _format_schema_description(agent)
        
        assert "Test agent" in description
        assert "Example inputs:" in description
        assert "{'query': 'example query'}" in description

    def test_format_schema_description_minimal(self):
        """Test formatting schema description with minimal data."""
        agent = Agent(
            id="test",
            name="Test",
            type=AgentType.AGENT
        )
        
        description = _format_schema_description(agent)
        
        # Should return empty string since no description is provided
        assert description == ""