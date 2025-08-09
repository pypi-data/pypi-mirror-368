"""
Module for FastAPI application setup.
"""

import json
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from mcp_proxy_adapter.api.handlers import execute_command, handle_json_rpc, handle_batch_json_rpc, get_server_health, get_commands_list
from mcp_proxy_adapter.api.middleware import setup_middleware
from mcp_proxy_adapter.api.schemas import JsonRpcRequest, JsonRpcSuccessResponse, JsonRpcErrorResponse, HealthResponse, CommandListResponse, APIToolDescription
from mcp_proxy_adapter.api.tools import get_tool_description, execute_tool
from mcp_proxy_adapter.config import config
from mcp_proxy_adapter.core.errors import MicroserviceError, NotFoundError
from mcp_proxy_adapter.core.logging import logger, RequestLogger
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.custom_openapi import custom_openapi_with_fallback


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for the FastAPI application. Handles startup and shutdown events.
    """
    # Startup events
    from mcp_proxy_adapter.commands.command_registry import registry
    from mcp_proxy_adapter.commands.help_command import HelpCommand
    from mcp_proxy_adapter.commands.health_command import HealthCommand
    
    # Register built-in commands if they don't exist (user can override them)
    if not registry.command_exists("help"):
        registry.register(HelpCommand)
    
    if not registry.command_exists("health"):
        registry.register(HealthCommand)
    
    # Discover and register additional commands automatically
    registry.discover_commands()
    
    logger.info(f"Application started with {len(registry.get_all_commands())} commands registered")
    
    yield  # Application is running
    
    # Shutdown events
    logger.info("Application shutting down")


def create_app(title: Optional[str] = None, description: Optional[str] = None, version: Optional[str] = None) -> FastAPI:
    """
    Creates and configures FastAPI application.

    Args:
        title: Application title (default: "MCP Proxy Adapter")
        description: Application description (default: "JSON-RPC API for interacting with MCP Proxy")
        version: Application version (default: "1.0.0")

    Returns:
        Configured FastAPI application.
    """
    # Use provided parameters or defaults
    app_title = title or "MCP Proxy Adapter"
    app_description = description or "JSON-RPC API for interacting with MCP Proxy"
    app_version = version or "1.0.0"
    
    # Create application
    app = FastAPI(
        title=app_title,
        description=app_description,
        version=app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify concrete domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup middleware using the new middleware package
    setup_middleware(app)
    
    # Use custom OpenAPI schema
    app.openapi = lambda: custom_openapi_with_fallback(app)
    
    # Explicit endpoint for OpenAPI schema
    @app.get("/openapi.json")
    async def get_openapi_schema():
        """
        Returns optimized OpenAPI schema compatible with MCP-Proxy.
        """
        return custom_openapi_with_fallback(app)

    # JSON-RPC handler
    @app.post("/api/jsonrpc", response_model=Union[JsonRpcSuccessResponse, JsonRpcErrorResponse, List[Union[JsonRpcSuccessResponse, JsonRpcErrorResponse]]])
    async def jsonrpc_endpoint(request: Request, request_data: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(...)):
        """
        Endpoint for handling JSON-RPC requests.
        Supports both single and batch requests.
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        # Create request logger for this endpoint
        req_logger = RequestLogger(__name__, request_id) if request_id else logger
        
        # Check if it's a batch request
        if isinstance(request_data, list):
            # Process batch request
            if len(request_data) == 0:
                # Empty batch request is invalid
                req_logger.warning("Invalid Request: Empty batch request")
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32600,
                            "message": "Invalid Request. Empty batch request"
                        },
                        "id": None
                    }
                )
            return await handle_batch_json_rpc(request_data, request)
        else:
            # Process single request
            return await handle_json_rpc(request_data, request_id)

    # Command execution endpoint (/cmd)
    @app.post("/cmd")
    async def cmd_endpoint(request: Request, command_data: Dict[str, Any] = Body(...)):
        """
        Universal endpoint for executing commands.
        Supports two formats:
        1. CommandRequest:
        {
            "command": "command_name",
            "params": {
                // Command parameters
            }
        }
        
        2. JSON-RPC:
        {
            "jsonrpc": "2.0",
            "method": "command_name",
            "params": {
                // Command parameters
            },
            "id": 123
        }
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        # Create request logger for this endpoint
        req_logger = RequestLogger(__name__, request_id) if request_id else logger
        
        try:
            # Determine request format (CommandRequest or JSON-RPC)
            if "jsonrpc" in command_data and "method" in command_data:
                # JSON-RPC format
                return await handle_json_rpc(command_data, request_id)
            
            # CommandRequest format
            if "command" not in command_data:
                req_logger.warning("Missing required field 'command'")
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": -32600,
                            "message": "Отсутствует обязательное поле 'command'"
                        }
                    }
                )
            
            command_name = command_data["command"]
            params = command_data.get("params", {})
            
            req_logger.info(f"Executing command via /cmd: {command_name}, params: {params}")
            
            # Check if command exists
            if not registry.command_exists(command_name):
                req_logger.warning(f"Command '{command_name}' not found")
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": -32601,
                            "message": f"Команда '{command_name}' не найдена"
                        }
                    }
                )
            
            # Execute command
            try:
                result = await execute_command(command_name, params, request_id)
                return {"result": result}
            except MicroserviceError as e:
                # Handle command execution errors
                req_logger.error(f"Error executing command '{command_name}': {str(e)}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": e.to_dict()
                    }
                )
            except NotFoundError as e:
                # Специальная обработка для help-команды: возвращаем result с пустым commands и error
                if command_name == "help":
                    return {
                        "result": {
                            "success": False,
                            "commands": {},
                            "error": str(e),
                            "note": "To get detailed information about a specific command, call help with parameter: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}"
                        }
                    }
                # Для остальных команд — стандартная ошибка
                return JSONResponse(
                    status_code=200,
                    content={
                        "error": {
                            "code": e.code,
                            "message": str(e)
                        }
                    }
                )
            
        except json.JSONDecodeError:
            req_logger.error("JSON decode error")
            return JSONResponse(
                status_code=200,
                content={
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
            )
        except Exception as e:
            req_logger.exception(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=200,
                content={
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": {"details": str(e)}
                    }
                }
            )

    # Direct command call
    @app.post("/api/command/{command_name}")
    async def command_endpoint(request: Request, command_name: str, params: Dict[str, Any] = Body(default={})):
        """
        Endpoint for direct command call.
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        try:
            result = await execute_command(command_name, params, request_id)
            return result
        except MicroserviceError as e:
            # Convert to proper HTTP status code
            status_code = 400 if e.code < 0 else e.code
            return JSONResponse(
                status_code=status_code,
                content=e.to_dict()
            )

    # Server health check
    @app.get("/health", operation_id="health_check")
    async def health_endpoint():
        """
        Health check endpoint.
        Returns server status and basic information.
        """
        return {
            "status": "ok",
            "model": "mcp-proxy-adapter",
            "version": "1.0.0"
        }
    
    # Graceful shutdown endpoint
    @app.post("/shutdown")
    async def shutdown_endpoint():
        """
        Graceful shutdown endpoint.
        Triggers server shutdown after completing current requests.
        """
        import asyncio
        
        # Schedule shutdown after a short delay to allow response
        async def delayed_shutdown():
            await asyncio.sleep(1)
            # This will trigger the lifespan shutdown event
            import os
            os._exit(0)
        
        # Start shutdown task
        asyncio.create_task(delayed_shutdown())
        
        return {
            "status": "shutting_down",
            "message": "Server shutdown initiated. New requests will be rejected."
        }

    # List of available commands
    @app.get("/api/commands", response_model=CommandListResponse)
    async def commands_list_endpoint():
        """
        Endpoint for getting list of available commands.
        """
        commands = await get_commands_list()
        return {"commands": commands}

    # Get command information by name
    @app.get("/api/commands/{command_name}")
    async def command_info_endpoint(request: Request, command_name: str):
        """
        Endpoint for getting information about a specific command.
        """
        # Get request_id from middleware state
        request_id = getattr(request.state, "request_id", None)
        
        # Create request logger for this endpoint
        req_logger = RequestLogger(__name__, request_id) if request_id else logger
        
        try:
            command_info = registry.get_command_info(command_name)
            return command_info
        except NotFoundError as e:
            req_logger.warning(f"Command '{command_name}' not found")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": 404,
                        "message": f"Command '{command_name}' not found"
                    }
                }
            )

    # Get API tool description
    @app.get("/api/tools/{tool_name}")
    async def tool_description_endpoint(tool_name: str, format: Optional[str] = "json"):
        """
        Получить подробное описание инструмента API.
        
        Возвращает полное описание инструмента API с доступными командами,
        их параметрами и примерами использования. Формат возвращаемых данных
        может быть JSON или Markdown (text).
        
        Args:
            tool_name: Имя инструмента API
            format: Формат вывода (json, text, markdown, html)
        """
        try:
            description = get_tool_description(tool_name, format)
            
            if format.lower() in ["text", "markdown", "html"]:
                if format.lower() == "html":
                    return Response(content=description, media_type="text/html")
                else:
                    return JSONResponse(
                        content={"description": description},
                        media_type="application/json"
                    )
            else:
                return description
                
        except NotFoundError as e:
            logger.warning(f"Tool not found: {tool_name}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": 404,
                        "message": str(e)
                    }
                }
            )
        except Exception as e:
            logger.exception(f"Error generating tool description: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": f"Error generating tool description: {str(e)}"
                    }
                }
            )

    # Execute API tool
    @app.post("/api/tools/{tool_name}")
    async def execute_tool_endpoint(tool_name: str, params: Dict[str, Any] = Body(...)):
        """
        Выполнить инструмент API с указанными параметрами.
        
        Args:
            tool_name: Имя инструмента API
            params: Параметры инструмента
        """
        try:
            result = await execute_tool(tool_name, **params)
            return result
        except NotFoundError as e:
            logger.warning(f"Tool not found: {tool_name}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": 404,
                        "message": str(e)
                    }
                }
            )
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": f"Error executing tool: {str(e)}"
                    }
                }
            )
    
    return app





# Create global application instance
app = create_app()
