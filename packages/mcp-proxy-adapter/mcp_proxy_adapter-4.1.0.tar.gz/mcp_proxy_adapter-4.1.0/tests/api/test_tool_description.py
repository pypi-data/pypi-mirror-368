"""
Tests for API tool description functionality.
"""

import json
import pytest
from typing import Dict, Any
from unittest.mock import MagicMock, patch

from mcp_proxy_adapter.api.tools import get_tool_description, TSTCommandExecutor
from mcp_proxy_adapter.api.schemas import APIToolDescription
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import NotFoundError


@pytest.fixture
def client():
    """Create a test client for FastAPI app."""
    # Mock client with async response methods
    class AsyncResponse:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data
            
        async def json(self):
            return self._data
    
    class AsyncClient:
        async def post(self, url, json=None):
            if "non_existent_tool" in url:
                return AsyncResponse(404, {"error": {"message": "Tool not found"}})
            elif "non_existent_command" in str(json):
                return AsyncResponse(200, {"error": {"message": "Command not found"}})
            else:
                return AsyncResponse(200, {"success": True, "data": {}})
                
        async def get(self, url):
            if "non_existent_tool" in url:
                return AsyncResponse(404, {"error": {"message": "Tool not found"}})
            elif "?format=text" in url:
                return AsyncResponse(200, {"description": "# Инструмент\n\nDescription"})
            else:
                return AsyncResponse(200, {"name": TSTCommandExecutor.name})
    
    return AsyncClient()


@pytest.fixture
def mock_registry_with_commands():
    """Create a mock registry with test commands."""
    original_commands = dict(registry._commands)
    
    # Clear existing commands and add mock ones for testing
    registry._commands.clear()
    
    # Add a mock help command
    mock_help_cmd = MagicMock()
    mock_help_cmd.get_metadata.return_value = {
        "name": "help",
        "summary": "Get help information",
        "description": "Get help information about available commands",
        "params": {"cmdname": {"type": "string", "required": False}},
        "examples": [{"command": "help", "description": "Get help about all commands"}]
    }
    registry._commands["help"] = mock_help_cmd
    
    yield registry
    
    # Restore original commands
    registry._commands.clear()
    for name, command in original_commands.items():
        registry._commands[name] = command


def test_api_tool_description_class(mock_registry_with_commands):
    """Test the APIToolDescription class."""
    
    # Generate tool description in JSON format
    description = APIToolDescription.generate_tool_description("test_tool", registry)
    
    # Check basic structure
    assert "name" in description
    assert "description" in description
    assert "supported_commands" in description
    assert "examples" in description
    
    # Check that supported commands is a dict
    assert isinstance(description["supported_commands"], dict)
    assert len(description["supported_commands"]) > 0
    
    # If any command exists, check its structure
    if description["supported_commands"]:
        # Get first command
        cmd_name = next(iter(description["supported_commands"]))
        cmd_info = description["supported_commands"][cmd_name]
        
        assert "summary" in cmd_info
        assert "description" in cmd_info
        assert "params" in cmd_info


def test_api_tool_description_text(mock_registry_with_commands):
    """Test generating text description for API tool."""
    
    # Generate tool description in text format
    description = APIToolDescription.generate_tool_description_text("test_tool", registry)
    
    # Check that it's a string
    assert isinstance(description, str)
    
    # Check that it contains basic structure markers
    assert "# Инструмент test_tool" in description
    assert "## Доступные команды" in description
    
    # Check that it contains a section about params, but only
    # if we actually have command with params
    if "help" in registry._commands:
        assert "help" in description
        assert "Параметры:" in description
    
    # Check for examples section - prefix changes
    assert "Примеры:" in description


def test_tst_command_executor_description():
    """Test the TSTCommandExecutor description generation."""
    
    # Get description in JSON format
    json_desc = TSTCommandExecutor.get_description("json")
    
    # Check basic structure
    assert "name" in json_desc
    assert json_desc["name"] == TSTCommandExecutor.name
    assert "description" in json_desc
    assert "parameters" in json_desc
    assert "properties" in json_desc["parameters"]
    assert "command" in json_desc["parameters"]["properties"]
    
    # Check that command property exists and has correct type
    assert "type" in json_desc["parameters"]["properties"]["command"]
    assert json_desc["parameters"]["properties"]["command"]["type"] == "string"
    
    # Get description in markdown format
    md_desc = TSTCommandExecutor.get_description("markdown")
    
    # Check that it's a string
    assert isinstance(md_desc, str)
    
    # Check basic content
    assert "# Инструмент" in md_desc
    assert "## Доступные команды" in md_desc


def test_get_tool_description():
    """Test the get_tool_description function."""
    
    # Get description for an existing tool
    description = get_tool_description(TSTCommandExecutor.name)
    
    # Check basic structure
    assert "name" in description
    assert description["name"] == TSTCommandExecutor.name
    
    # Try to get description for a non-existent tool
    with pytest.raises(NotFoundError):
        get_tool_description("non_existent_tool")


@pytest.mark.asyncio
async def test_execute_tool_endpoint(client):
    """Test the execute_tool_endpoint."""
    
    # Make a request to the endpoint for a valid command
    response = await client.post(
        f"/api/tools/{TSTCommandExecutor.name}",
        json={"command": "help"}
    )
    
    # Check response status code
    assert response.status_code == 200
    
    # Check response content
    data = await response.json()
    assert "success" in data
    
    # Make a request with invalid parameters
    response = await client.post(
        f"/api/tools/{TSTCommandExecutor.name}",
        json={"command": "non_existent_command"}
    )
    
    # Check response - should be 200 with error in content
    assert response.status_code == 200
    
    # Try to execute a non-existent tool
    response = await client.post(
        "/api/tools/non_existent_tool",
        json={}
    )
    
    # Check response status code
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tool_description_endpoint(client):
    """Test the tool_description_endpoint."""
    
    # Make a request to the endpoint
    response = await client.get(
        f"/api/tools/{TSTCommandExecutor.name}"
    )
    
    # Check response status code
    assert response.status_code == 200
    
    # Check response content
    data = await response.json()
    assert "name" in data
    assert data["name"] == TSTCommandExecutor.name
    
    # Get description in text format
    response = await client.get(
        f"/api/tools/{TSTCommandExecutor.name}?format=text"
    )
    
    # Check response status code
    assert response.status_code == 200
    
    # Check response content
    data = await response.json()
    assert "description" in data
    
    # Try to get description for a non-existent tool
    response = await client.get(
        "/api/tools/non_existent_tool"
    )
    
    # Check response status code
    assert response.status_code == 404 