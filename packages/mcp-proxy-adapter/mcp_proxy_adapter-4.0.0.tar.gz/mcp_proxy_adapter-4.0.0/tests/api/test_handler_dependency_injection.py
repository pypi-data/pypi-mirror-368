"""
Tests for Dependency Injection integration with API handlers.
"""

import pytest
from unittest.mock import MagicMock, patch

from mcp_proxy_adapter.api import handlers
from mcp_proxy_adapter.commands import Command, SuccessResult
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.dependency_container import DependencyContainer
from mcp_proxy_adapter.commands.result import CommandResult


# Тестовые классы для проверки интеграции с API
class MockService:
    """Test service to be injected."""
    
    def get_value(self):
        """Return a test value."""
        return "api_service_value"


class MockCommandResult(SuccessResult):
    """Test command result."""
    
    def __init__(self, value):
        """Initialize with a value."""
        super().__init__(data={"value": value})


class APITestCommand(Command):
    """Test command that requires a dependency for API testing."""
    
    name = "api_test_command"
    result_class = MockCommandResult
    
    def __init__(self, service: MockService):
        """Initialize with a service dependency."""
        self.service = service
        
    async def execute(self, param1: str = "default") -> CommandResult:
        """Execute command using the service."""
        value = f"{self.service.get_value()}_{param1}"
        return MockCommandResult(value)


@pytest.fixture
def registry():
    """Create a command registry with test commands."""
    registry = CommandRegistry()
    
    # Create and register service 
    service = MockService()
    
    # Create command with dependency
    command = APITestCommand(service)
    
    # Register command instance
    registry.register(command)
    
    return registry


class TestAPIHandlersDependencyInjection:
    """Tests for DI integration with API handlers."""
    
    @pytest.mark.asyncio
    async def test_execute_command_with_di(self, registry):
        """Test execute_command function with dependency injected commands."""
        # Configure parameters
        command_name = "api_test_command"
        params = {"param1": "custom_param"}
        
        # Execute command through handler
        with patch("mcp_proxy_adapter.api.handlers.registry", registry), \
             patch("mcp_proxy_adapter.commands.command_registry.registry", registry):
            result = await handlers.execute_command(command_name, params)
        
        # Check result
        assert result["data"]["value"] == "api_service_value_custom_param"
    
    @pytest.mark.asyncio
    async def test_handle_json_rpc_with_di(self, registry):
        """Test JSON-RPC handler with dependency injected commands."""
        # Configure request data
        request_data = {
            "jsonrpc": "2.0",
            "method": "api_test_command",
            "params": {"param1": "json_rpc_param"},
            "id": 123
        }
        
        # Execute through JSON-RPC handler
        with patch("mcp_proxy_adapter.api.handlers.registry", registry), \
             patch("mcp_proxy_adapter.commands.command_registry.registry", registry):
            response = await handlers.handle_json_rpc(request_data)
        
        # Verify response
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 123
        assert response["result"]["data"]["value"] == "api_service_value_json_rpc_param"
    
    @pytest.mark.asyncio
    async def test_batch_json_rpc_with_di(self, registry):
        """Test batch JSON-RPC with dependency injected commands."""
        # Configure batch requests
        batch_requests = [
            {
                "jsonrpc": "2.0",
                "method": "api_test_command",
                "params": {"param1": "batch1"},
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "api_test_command",
                "params": {"param1": "batch2"},
                "id": 2
            }
        ]
        
        # Execute batch
        with patch("mcp_proxy_adapter.api.handlers.registry", registry), \
             patch("mcp_proxy_adapter.commands.command_registry.registry", registry):
            responses = await handlers.handle_batch_json_rpc(batch_requests)
        
        # Verify responses
        assert len(responses) == 2
        assert responses[0]["result"]["data"]["value"] == "api_service_value_batch1"
        assert responses[1]["result"]["data"]["value"] == "api_service_value_batch2" 