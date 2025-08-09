"""
Module for command execution hooks.

This module provides a hook system that allows intercepting command execution
before and after the actual command runs.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from mcp_proxy_adapter.core.logging import logger


class HookType(Enum):
    """Types of hooks."""
    BEFORE_EXECUTION = "before_execution"
    AFTER_EXECUTION = "after_execution"


@dataclass
class HookContext:
    """Context passed to hook functions."""
    command_name: str
    params: Dict[str, Any]
    hook_type: HookType
    standard_processing: bool = True
    result: Optional[Any] = None


class CommandHooks:
    """
    Manages command execution hooks.
    """
    
    def __init__(self):
        """Initialize hooks manager."""
        self._before_hooks: Dict[str, List[Callable]] = {}
        self._after_hooks: Dict[str, List[Callable]] = {}
        self._global_before_hooks: List[Callable] = []
        self._global_after_hooks: List[Callable] = []
    
    def register_before_hook(self, command_name: str, hook: Callable[[HookContext], None]) -> None:
        """
        Register a hook to be executed before command execution.
        
        Args:
            command_name: Name of the command to hook into
            hook: Hook function that takes HookContext as parameter
        """
        if command_name not in self._before_hooks:
            self._before_hooks[command_name] = []
        self._before_hooks[command_name].append(hook)
        logger.debug(f"Registered before hook for command: {command_name}")
    
    def register_after_hook(self, command_name: str, hook: Callable[[HookContext], None]) -> None:
        """
        Register a hook to be executed after command execution.
        
        Args:
            command_name: Name of the command to hook into
            hook: Hook function that takes HookContext as parameter
        """
        if command_name not in self._after_hooks:
            self._after_hooks[command_name] = []
        self._after_hooks[command_name].append(hook)
        logger.debug(f"Registered after hook for command: {command_name}")
    
    def register_global_before_hook(self, hook: Callable[[HookContext], None]) -> None:
        """
        Register a global hook to be executed before any command.
        
        Args:
            hook: Hook function that takes HookContext as parameter
        """
        self._global_before_hooks.append(hook)
        logger.debug("Registered global before hook")
    
    def register_global_after_hook(self, hook: Callable[[HookContext], None]) -> None:
        """
        Register a global hook to be executed after any command.
        
        Args:
            hook: Hook function that takes HookContext as parameter
        """
        self._global_after_hooks.append(hook)
        logger.debug("Registered global after hook")
    
    def unregister_before_hook(self, command_name: str, hook: Callable[[HookContext], None]) -> None:
        """
        Unregister a before hook for a specific command.
        
        Args:
            command_name: Name of the command
            hook: Hook function to unregister
        """
        if command_name in self._before_hooks:
            try:
                self._before_hooks[command_name].remove(hook)
                logger.debug(f"Unregistered before hook for command: {command_name}")
                # Remove the command key if no hooks remain
                if not self._before_hooks[command_name]:
                    del self._before_hooks[command_name]
            except ValueError:
                logger.warning(f"Hook not found for command: {command_name}")
    
    def unregister_after_hook(self, command_name: str, hook: Callable[[HookContext], None]) -> None:
        """
        Unregister an after hook for a specific command.
        
        Args:
            command_name: Name of the command
            hook: Hook function to unregister
        """
        if command_name in self._after_hooks:
            try:
                self._after_hooks[command_name].remove(hook)
                logger.debug(f"Unregistered after hook for command: {command_name}")
                # Remove the command key if no hooks remain
                if not self._after_hooks[command_name]:
                    del self._after_hooks[command_name]
            except ValueError:
                logger.warning(f"Hook not found for command: {command_name}")
    
    def unregister_global_before_hook(self, hook: Callable[[HookContext], None]) -> None:
        """
        Unregister a global before hook.
        
        Args:
            hook: Hook function to unregister
        """
        try:
            self._global_before_hooks.remove(hook)
            logger.debug("Unregistered global before hook")
        except ValueError:
            logger.warning("Global before hook not found")
    
    def unregister_global_after_hook(self, hook: Callable[[HookContext], None]) -> None:
        """
        Unregister a global after hook.
        
        Args:
            hook: Hook function to unregister
        """
        try:
            self._global_after_hooks.remove(hook)
            logger.debug("Unregistered global after hook")
        except ValueError:
            logger.warning("Global after hook not found")
    
    def execute_before_hooks(self, command_name: str, params: Dict[str, Any]) -> HookContext:
        """
        Execute all before hooks for a command.
        
        Args:
            command_name: Name of the command
            params: Command parameters
            
        Returns:
            HookContext with execution results
        """
        context = HookContext(
            command_name=command_name,
            params=params,
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        # Execute global before hooks
        for hook in self._global_before_hooks:
            try:
                hook(context)
            except Exception as e:
                logger.error(f"Error in global before hook for command {command_name}: {e}")
        
        # Execute command-specific before hooks
        if command_name in self._before_hooks:
            for hook in self._before_hooks[command_name]:
                try:
                    hook(context)
                except Exception as e:
                    logger.error(f"Error in before hook for command {command_name}: {e}")
        
        return context
    
    def execute_after_hooks(self, command_name: str, params: Dict[str, Any], result: Any) -> HookContext:
        """
        Execute all after hooks for a command.
        
        Args:
            command_name: Name of the command
            params: Command parameters
            result: Command execution result
            
        Returns:
            HookContext with execution results
        """
        context = HookContext(
            command_name=command_name,
            params=params,
            hook_type=HookType.AFTER_EXECUTION,
            result=result
        )
        
        # Execute command-specific after hooks
        if command_name in self._after_hooks:
            for hook in self._after_hooks[command_name]:
                try:
                    hook(context)
                except Exception as e:
                    logger.error(f"Error in after hook for command {command_name}: {e}")
        
        # Execute global after hooks
        for hook in self._global_after_hooks:
            try:
                hook(context)
            except Exception as e:
                logger.error(f"Error in global after hook for command {command_name}: {e}")
        
        return context
    
    def clear_hooks(self, command_name: Optional[str] = None) -> None:
        """
        Clear all hooks or hooks for a specific command.
        
        Args:
            command_name: If provided, clear hooks only for this command.
                          If None, clear all hooks.
        """
        if command_name is None:
            # Clear all hooks
            self._before_hooks.clear()
            self._after_hooks.clear()
            self._global_before_hooks.clear()
            self._global_after_hooks.clear()
            logger.debug("Cleared all hooks")
        else:
            # Clear hooks for specific command
            if command_name in self._before_hooks:
                del self._before_hooks[command_name]
            if command_name in self._after_hooks:
                del self._after_hooks[command_name]
            logger.debug(f"Cleared hooks for command: {command_name}")
    
    def get_hook_info(self) -> Dict[str, Any]:
        """
        Get information about registered hooks.
        
        Returns:
            Dictionary with hook information
        """
        return {
            "before_hooks": {cmd: len(hooks) for cmd, hooks in self._before_hooks.items()},
            "after_hooks": {cmd: len(hooks) for cmd, hooks in self._after_hooks.items()},
            "global_before_hooks": len(self._global_before_hooks),
            "global_after_hooks": len(self._global_after_hooks)
        }


# Global hooks instance
hooks = CommandHooks() 