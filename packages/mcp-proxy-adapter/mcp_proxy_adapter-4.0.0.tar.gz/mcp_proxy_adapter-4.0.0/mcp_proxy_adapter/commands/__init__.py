"""
Commands module initialization file.
"""

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.command_registry import registry, CommandRegistry
from mcp_proxy_adapter.commands.dependency_container import container, DependencyContainer
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult, ErrorResult

# Automatically discover and register commands
registry.discover_commands()

__all__ = [
    "Command",
    "CommandResult",
    "SuccessResult", 
    "ErrorResult",
    "registry",
    "CommandRegistry",
    "container",
    "DependencyContainer"
]
