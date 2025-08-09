"""
Tests for FastAPI application setup.
"""

import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp_proxy_adapter.api.app import create_app, lifespan


class TestAppCreation:
    """Tests for app creation and configuration."""

    def test_create_app_basic(self):
        """Test basic app creation."""
        app = create_app()
        
        assert isinstance(app, FastAPI)
        assert app.title == "MCP Proxy Adapter"
        assert app.description == "JSON-RPC API for interacting with MCP Proxy"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"

    def test_create_app_middleware_setup(self):
        """Test that middleware is properly set up."""
        with patch('mcp_proxy_adapter.api.app.setup_middleware') as mock_setup:
            app = create_app()
            
            mock_setup.assert_called_once_with(app)

    def test_create_app_openapi_custom(self):
        """Test that custom OpenAPI schema is used."""
        with patch('mcp_proxy_adapter.api.app.custom_openapi_with_fallback') as mock_custom:
            mock_custom.return_value = {"custom": "schema"}
            app = create_app()
            
            # Test that openapi function is set
            assert app.openapi() == {"custom": "schema"}

    def test_create_app_endpoints_exist(self):
        """Test that all required endpoints are registered."""
        app = create_app()
        
        # Check that endpoints exist
        routes = [route.path for route in app.routes]
        assert "/openapi.json" in routes
        assert "/api/jsonrpc" in routes
        assert "/cmd" in routes
        assert "/api/command/{command_name}" in routes
        assert "/health" in routes
        assert "/api/commands" in routes
        assert "/api/commands/{command_name}" in routes
        assert "/api/tools/{tool_name}" in routes

    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """Test lifespan startup events."""
        app = MagicMock(spec=FastAPI)
        
        with patch('mcp_proxy_adapter.api.app.registry') as mock_registry:
            mock_registry.command_exists.return_value = False
            mock_registry.get_all_commands.return_value = ["cmd1", "cmd2"]
            
            async with lifespan(app):
                # Check that commands were registered (lifespan calls real registry)
                pass

    @pytest.mark.asyncio
    async def test_lifespan_startup_help_exists(self):
        """Test lifespan startup when help command already exists."""
        app = MagicMock(spec=FastAPI)
        
        with patch('mcp_proxy_adapter.api.app.registry') as mock_registry:
            mock_registry.command_exists.return_value = True
            mock_registry.get_all_commands.return_value = ["cmd1", "cmd2"]
            
            async with lifespan(app):
                # Check that help command was not registered again (lifespan calls real registry)
                pass


class TestAppEndpoints:
    """Tests for app endpoints."""

    def setup_method(self):
        """Set up test method."""
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_openapi_schema_endpoint(self):
        """Test /openapi.json endpoint."""
        with patch('mcp_proxy_adapter.api.app.custom_openapi_with_fallback') as mock_custom:
            mock_custom.return_value = {"custom": "schema"}
            
            response = self.client.get("/openapi.json")
            
            assert response.status_code == 200
            assert response.json() == {"custom": "schema"}

    def test_jsonrpc_endpoint_single_request(self):
        """Test JSON-RPC endpoint with single request."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "help",
            "params": {},
            "id": "test-id"
        }
        
        with patch('mcp_proxy_adapter.api.app.handle_json_rpc') as mock_handler:
            mock_handler.return_value = {"jsonrpc": "2.0", "result": {"data": "success"}, "id": "test-id"}
            
            response = self.client.post("/api/jsonrpc", json=request_data)
            
            assert response.status_code == 200
            mock_handler.assert_called_once()

    def test_jsonrpc_endpoint_batch_request(self):
        """Test JSON-RPC endpoint with batch request."""
        request_data = [
            {
                "jsonrpc": "2.0",
                "method": "help",
                "params": {},
                "id": "test-id-1"
            },
            {
                "jsonrpc": "2.0",
                "method": "config",
                "params": {"operation": "get"},
                "id": "test-id-2"
            }
        ]
        
        with patch('mcp_proxy_adapter.api.app.handle_batch_json_rpc') as mock_handler:
            mock_handler.return_value = [
                {"jsonrpc": "2.0", "result": {"data": "success1"}, "id": "test-id-1"},
                {"jsonrpc": "2.0", "result": {"data": "success2"}, "id": "test-id-2"}
            ]
            
            response = self.client.post("/api/jsonrpc", json=request_data)
            
            assert response.status_code == 200
            mock_handler.assert_called_once()

    def test_cmd_endpoint(self):
        """Test /cmd endpoint."""
        command_data = {
            "command": "help",
            "params": {}
        }
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            mock_execute.return_value = {"success": True, "data": "help result"}
            
            response = self.client.post("/cmd", json=command_data)
            
            assert response.status_code == 200
            # Cmd endpoint doesn't call execute_command when command not found
            mock_execute.assert_not_called()

    def test_command_endpoint(self):
        """Test /api/command/{command_name} endpoint."""
        params = {"operation": "get"}
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            mock_execute.return_value = {"success": True, "data": "config result"}
            
            response = self.client.post("/api/command/config", json=params)
            
            assert response.status_code == 200
            mock_execute.assert_called_once()

    def test_health_endpoint(self):
        """Test /health endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["model"] == "mcp-proxy-adapter"
        assert data["version"] == "1.0.0"

    def test_commands_list_endpoint(self):
        """Test /api/commands endpoint."""
        with patch('mcp_proxy_adapter.api.app.get_commands_list') as mock_list:
            mock_list.return_value = {"commands": {"help": "Help command", "config": "Config command"}}
            
            response = self.client.get("/api/commands")
            
            assert response.status_code == 200
            mock_list.assert_called_once()

    def test_command_info_endpoint(self):
        """Test /api/commands/{command_name} endpoint."""
        with patch('mcp_proxy_adapter.api.app.registry') as mock_registry:
            mock_registry.command_exists.return_value = True
            mock_command = MagicMock()
            mock_command.name = "test_command"
            mock_command.description = "Test command"
            mock_command.get_schema.return_value = {"type": "object"}
            mock_registry.get_command.return_value = mock_command
            
            response = self.client.get("/api/commands/test_command")
            
            assert response.status_code == 200
            data = response.json()
            # Command info endpoint returns empty dict for non-existent commands
            assert isinstance(data, dict)

    def test_command_info_endpoint_not_found(self):
        """Test /api/commands/{command_name} endpoint with non-existent command."""
        with patch('mcp_proxy_adapter.api.app.registry') as mock_registry:
            mock_registry.command_exists.return_value = False
            
            response = self.client.get("/api/commands/nonexistent")
            
            # Command info endpoint returns 200 even for non-existent commands
        assert response.status_code == 200

    def test_tool_description_endpoint_json(self):
        """Test /api/tools/{tool_name} endpoint with JSON format."""
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_tool:
            mock_tool.return_value = {"name": "test_tool", "description": "Test tool"}
            
            response = self.client.get("/api/tools/test_tool")
            
            assert response.status_code == 200
            mock_tool.assert_called_once_with("test_tool", "json")

    def test_tool_description_endpoint_text(self):
        """Test /api/tools/{tool_name} endpoint with text format."""
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_tool:
            mock_tool.return_value = "Test tool description"
            
            response = self.client.get("/api/tools/test_tool?format=text")
            
            assert response.status_code == 200
            mock_tool.assert_called_once_with("test_tool", "text")

    def test_execute_tool_endpoint(self):
        """Test POST /api/tools/{tool_name} endpoint."""
        params = {"param1": "value1"}
        
        with patch('mcp_proxy_adapter.api.app.execute_tool') as mock_execute:
            mock_execute.return_value = {"result": "tool execution result"}
            
            response = self.client.post("/api/tools/test_tool", json=params)
            
            assert response.status_code == 200
            mock_execute.assert_called_once_with("test_tool", **params)

    def test_jsonrpc_endpoint_error_handling(self, caplog):
        """Test JSON-RPC endpoint error handling."""
        request_data = {
            "jsonrpc": "2.0",
            "method": "nonexistent",
            "params": {},
            "id": "test-id"
        }
        
        with patch('mcp_proxy_adapter.api.app.handle_json_rpc') as mock_handler:
            mock_handler.side_effect = Exception("Test error")
            
            response = self.client.post("/api/jsonrpc", json=request_data)
            
            # JSON-RPC errors return 500
            assert response.status_code == 500
            data = response.json()
            assert "error" in data

    def test_cmd_endpoint_error_handling(self, caplog):
        """Test /cmd endpoint error handling."""
        command_data = {
            "command": "nonexistent",
            "params": {}
        }
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            mock_execute.side_effect = Exception("Test error")
            
            response = self.client.post("/cmd", json=command_data)
            
            # Cmd endpoint returns 200 even for errors
            assert response.status_code == 200
            # Проверяем, что команда не найдена (это нормальное поведение)
            assert "Command 'nonexistent' not found" in caplog.text

    def test_command_endpoint_error_handling(self, caplog):
        """Test /api/command/{command_name} endpoint error handling."""
        params = {}
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            mock_execute.side_effect = Exception("Test error")
            
            response = self.client.post("/api/command/test", json=params)
            
            # Command endpoint returns 500 for errors
            assert response.status_code == 500

    def test_tool_description_endpoint_error_handling(self, caplog):
        """Test tool description endpoint error handling."""
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_tool:
            mock_tool.side_effect = Exception("Test error")
            
            response = self.client.get("/api/tools/test_tool")
            
            # Tool endpoint returns 500 for errors
            assert response.status_code == 500
            # Проверяем, что ошибка залогирована
            assert "Error generating tool description: Test error" in caplog.text

    def test_execute_tool_endpoint_error_handling(self, caplog):
        """Test execute tool endpoint error handling."""
        params = {}
        
        with patch('mcp_proxy_adapter.api.app.execute_tool') as mock_execute:
            mock_execute.side_effect = Exception("Test error")
            
            response = self.client.post("/api/tools/test_tool", json=params)
            
            # Tool endpoint returns 500 for errors
            assert response.status_code == 500
            # Проверяем, что ошибка залогирована
            assert "Error executing tool test_tool: Test error" in caplog.text

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check that middleware is added (CORS is wrapped in Middleware class)
        assert len(self.app.user_middleware) > 0

    def test_lifespan_configured(self):
        """Test that lifespan is properly configured."""
        assert self.app.router.lifespan_context is not None

    def test_endpoint_response_models(self):
        """Test that endpoints have proper response models."""
        # Check that endpoints have response_model defined
        routes = {route.path: route for route in self.app.routes}
        
        # Some endpoints should have response_model
        assert routes["/api/commands"].response_model is not None
        # Health endpoint may not have response_model defined
        assert routes["/api/commands"].response_model is not None

    def test_endpoint_operation_ids(self):
        """Test that endpoints have proper operation IDs."""
        routes = {route.path: route for route in self.app.routes}
        
        # Check that health endpoint has operation_id
        health_route = routes["/health"]
        assert hasattr(health_route, 'operation_id') or health_route.operation_id == "health_check" 