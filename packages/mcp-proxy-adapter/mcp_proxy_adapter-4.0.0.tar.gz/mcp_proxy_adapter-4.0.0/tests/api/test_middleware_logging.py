"""
Tests for logging middleware module.
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.logging import LoggingMiddleware


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware class."""

    def setup_method(self):
        """Set up test method."""
        self.mock_app = MagicMock()
        self.middleware = LoggingMiddleware(self.mock_app)

    @pytest.mark.asyncio
    async def test_dispatch_successful_request(self):
        """Test dispatch with successful request."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        # Mock request body
        request.body = AsyncMock(return_value=json.dumps({"test": "data"}).encode())
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        assert "X-Request-ID" in result.headers
        assert "X-Process-Time" in result.headers
        assert request.state.request_id is not None

    @pytest.mark.asyncio
    async def test_dispatch_get_request(self):
        """Test dispatch with GET request (no body logging)."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        assert "X-Request-ID" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_head_request(self):
        """Test dispatch with HEAD request (no body logging)."""
        request = MagicMock(spec=Request)
        request.method = "HEAD"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        assert "X-Request-ID" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_with_sensitive_data(self):
        """Test dispatch with sensitive data in request body."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Request body with sensitive data
        sensitive_data = {
            "params": {
                "username": "test_user",
                "password": "secret_password",
                "token": "secret_token",
                "api_key": "secret_key"
            }
        }
        request.body = AsyncMock(return_value=json.dumps(sensitive_data).encode())
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        # Sensitive data should be masked in logs

    @pytest.mark.asyncio
    async def test_dispatch_with_non_json_body(self):
        """Test dispatch with non-JSON request body."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Non-JSON body
        request.body = AsyncMock(return_value=b"plain text body")
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_dispatch_with_empty_body(self):
        """Test dispatch with empty request body."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Empty body
        request.body = AsyncMock(return_value=b"")
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_dispatch_with_body_reading_error(self, caplog):
        """Test dispatch with error reading request body."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Mock request body to raise an exception
        request.body = AsyncMock(side_effect=Exception("Body reading error"))
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        assert "Error reading request body: Body reading error" in caplog.text

    @pytest.mark.asyncio
    async def test_dispatch_with_json_decode_error(self):
        """Test dispatch with JSON decode error."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Mock request body with invalid JSON
        request.body = AsyncMock(return_value=b"invalid json")
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_dispatch_with_body_logging_error(self, caplog):
        """Test dispatch with error during body logging."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Mock request body
        request.body = AsyncMock(return_value=b'{"test": "data"}')
        
        # Mock json.loads to raise an exception
        with patch('json.loads', side_effect=Exception("JSON processing error")):
            response = JSONResponse(content={"success": True})
            call_next = AsyncMock(return_value=response)
            
            result = await self.middleware.dispatch(request, call_next)
            
            assert result == response
            assert "Error logging request body: JSON processing error" in caplog.text

    @pytest.mark.asyncio
    async def test_dispatch_with_exception(self, caplog):
        """Test dispatch with exception during processing."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Mock request body
        request.body = AsyncMock(return_value=b'{"test": "data"}')
        
        # Mock call_next to raise an exception
        call_next = AsyncMock(side_effect=Exception("Processing error"))
        
        # Should raise the exception
        with pytest.raises(Exception, match="Processing error"):
            await self.middleware.dispatch(request, call_next)
        
        # Verify error was logged
        assert "Request failed: POST http://testserver/api/test | Error: Processing error" in caplog.text

    @pytest.mark.asyncio
    async def test_dispatch_with_unknown_client(self):
        """Test dispatch with unknown client."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client = None  # Unknown client
        request.state = MagicMock()
        
        # Mock request.body to return bytes
        request.body = AsyncMock(return_value=b'{"test": "data"}')
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_dispatch_with_nested_sensitive_data(self):
        """Test dispatch with nested sensitive data in params."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Request body with nested sensitive data
        nested_data = {
            "params": {
                "user": {
                    "username": "test_user",
                    "password": "secret_password"
                },
                "config": {
                    "api_key": "secret_key"
                }
            }
        }
        request.body = AsyncMock(return_value=json.dumps(nested_data).encode())
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_dispatch_with_non_dict_params(self):
        """Test dispatch with non-dict params in request body."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Request body with non-dict params
        data = {
            "params": "not_a_dict"
        }
        request.body = AsyncMock(return_value=json.dumps(data).encode())
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_dispatch_without_params(self):
        """Test dispatch with request body without params."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Request body without params
        data = {
            "command": "test",
            "data": "test_data"
        }
        request.body = AsyncMock(return_value=json.dumps(data).encode())
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response

    @pytest.mark.asyncio
    async def test_dispatch_with_non_dict_body(self):
        """Test dispatch with non-dict JSON body."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = "http://testserver/api/test"
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        
        # Non-dict JSON body
        request.body = AsyncMock(return_value=json.dumps(["array", "data"]).encode())
        
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response 