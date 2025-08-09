"""
Middleware package for API.
This package contains middleware components for request processing.
"""

from fastapi import FastAPI

from mcp_proxy_adapter.core.logging import logger
from .base import BaseMiddleware
from .logging import LoggingMiddleware
from .error_handling import ErrorHandlingMiddleware
from .auth import AuthMiddleware
from .rate_limit import RateLimitMiddleware
from .performance import PerformanceMiddleware

def setup_middleware(app: FastAPI) -> None:
    """
    Sets up middleware for application.

    Args:
        app: FastAPI application instance.
    """
    # Add error handling middleware first (last to execute)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add rate limiting middleware if configured
    from mcp_proxy_adapter.config import config
    if config.get("rate_limit_enabled", False):
        app.add_middleware(
            RateLimitMiddleware,
            rate_limit=config.get("rate_limit", 100),
            time_window=config.get("rate_limit_window", 60)
        )
    
    # Добавляем authentication middleware с явным указанием auth_enabled
    auth_enabled = config.get("auth_enabled", False)
    app.add_middleware(
        AuthMiddleware,
        api_keys=config.get("api_keys", {}),
        auth_enabled=auth_enabled
    )

    # Add performance middleware
    app.add_middleware(PerformanceMiddleware)
    
    logger.info(f"Middleware setup completed. Auth enabled: {auth_enabled}") 