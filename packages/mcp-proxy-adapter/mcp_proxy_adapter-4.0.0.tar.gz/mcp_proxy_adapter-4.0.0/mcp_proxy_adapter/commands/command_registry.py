"""
Module for registering and managing commands.

Example: Registering a command instance (for dependency injection)
---------------------------------------------------------------

.. code-block:: python

    from mcp_proxy_adapter.commands.command_registry import registry
    from my_commands import MyCommand
    
    # Suppose MyCommand requires a service dependency
    service = MyService()
    my_command_instance = MyCommand(service=service)
    registry.register(my_command_instance)

    # Now, when the command is executed, the same instance (with dependencies) will be used
"""

import importlib
import inspect
import os
import pkgutil
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.core.errors import NotFoundError
from mcp_proxy_adapter.core.logging import logger

T = TypeVar("T", bound=Command)


class CommandRegistry:
    """
    Registry for registering and finding commands.
    """
    
    def __init__(self):
        """
        Initialize command registry.
        """
        self._commands: Dict[str, Type[Command]] = {}
        self._instances: Dict[str, Command] = {}
        self._custom_commands: Dict[str, Type[Command]] = {}  # Custom commands with priority
    
    def register(self, command: Union[Type[Command], Command]) -> None:
        """
        Registers command class or instance in the registry.

        Args:
            command: Command class or instance to register.

        Raises:
            ValueError: If command with the same name is already registered.
        """
        # Determine if this is a class or an instance
        if isinstance(command, type) and issubclass(command, Command):
            command_class = command
            command_instance = None
        elif isinstance(command, Command):
            command_class = command.__class__
            command_instance = command
        else:
            raise ValueError(f"Invalid command type: {type(command)}. Expected Command class or instance.")
            
        # Get command name
        if not hasattr(command_class, "name") or not command_class.name:
            # Use class name if name attribute is not set
            command_name = command_class.__name__.lower()
            if command_name.endswith("command"):
                command_name = command_name[:-7]  # Remove "command" suffix
        else:
            command_name = command_class.name
            
        if command_name in self._commands:
            logger.debug(f"Command '{command_name}' is already registered, skipping")
            raise ValueError(f"Command '{command_name}' is already registered")
            
        logger.debug(f"Registering command: {command_name}")
        self._commands[command_name] = command_class
        
        # Store instance if provided
        if command_instance:
            logger.debug(f"Storing instance for command: {command_name}")
            self._instances[command_name] = command_instance
    
    def unregister(self, command_name: str) -> None:
        """
        Removes command from registry.

        Args:
            command_name: Command name to remove.

        Raises:
            NotFoundError: If command is not found.
        """
        if command_name not in self._commands:
            raise NotFoundError(f"Command '{command_name}' not found")
            
        logger.debug(f"Unregistering command: {command_name}")
        del self._commands[command_name]
        
        # Remove instance if exists
        if command_name in self._instances:
            del self._instances[command_name]
    
    def command_exists(self, command_name: str) -> bool:
        """
        Checks if command exists in registry.

        Args:
            command_name: Command name to check.

        Returns:
            True if command exists, False otherwise.
        """
        return command_name in self._commands
    
    def get_command(self, command_name: str) -> Type[Command]:
        """
        Gets command class by name.

        Args:
            command_name: Command name.

        Returns:
            Command class.

        Raises:
            NotFoundError: If command is not found.
        """
        if command_name not in self._commands:
            raise NotFoundError(f"Command '{command_name}' not found")
            
        return self._commands[command_name]
        
    def get_command_instance(self, command_name: str) -> Command:
        """
        Gets command instance by name. If instance doesn't exist, creates new one.
        
        Args:
            command_name: Command name
            
        Returns:
            Command instance
            
        Raises:
            NotFoundError: If command is not found
        """
        if command_name not in self._commands:
            raise NotFoundError(f"Command '{command_name}' not found")
            
        # Return existing instance if available
        if command_name in self._instances:
            return self._instances[command_name]
            
        # Otherwise create new instance without dependencies
        # (this will raise error if command requires dependencies)
        try:
            command_class = self._commands[command_name]
            return command_class()
        except Exception as e:
            logger.error(f"Failed to create instance of '{command_name}': {e}")
            raise ValueError(f"Command '{command_name}' requires dependencies but was registered as class. Register an instance instead.") from e
    
    def has_instance(self, command_name: str) -> bool:
        """
        Checks if command instance exists in registry.
        
        Args:
            command_name: Command name
            
        Returns:
            True if command instance exists, False otherwise
        """
        return command_name in self._instances
    
    def get_all_commands(self) -> Dict[str, Type[Command]]:
        """
        Returns all registered commands.

        Returns:
            Dictionary with command names and their classes.
        """
        return dict(self._commands)
    
    def get_command_info(self, command_name: str) -> Dict[str, Any]:
        """
        Gets information about a command.

        Args:
            command_name: Command name.

        Returns:
            Dictionary with command information.

        Raises:
            NotFoundError: If command is not found.
        """
        command_class = self.get_command_with_priority(command_name)
        
        return {
            "name": command_name,
            "description": command_class.__doc__ or "",
            "params": command_class.get_param_info(),
            "schema": command_class.get_schema(),
            "result_schema": command_class.get_result_schema()
        }
    
    def get_command_metadata(self, command_name: str) -> Dict[str, Any]:
        """
        Get complete metadata for a command.
        
        Args:
            command_name: Command name
            
        Returns:
            Dict with command metadata
            
        Raises:
            NotFoundError: If command is not found
        """
        command_class = self.get_command_with_priority(command_name)
        return command_class.get_metadata()
    
    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all registered commands.
        
        Returns:
            Dict with command names as keys and metadata as values
        """
        metadata = {}
        # Add custom commands first (they have priority)
        for name, command_class in self._custom_commands.items():
            metadata[name] = command_class.get_metadata()
        # Add built-in commands (custom commands will override if same name)
        for name, command_class in self._commands.items():
            if name not in self._custom_commands:  # Only add if not overridden by custom
                metadata[name] = command_class.get_metadata()
        return metadata
    
    def get_all_commands_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Gets information about all registered commands.

        Returns:
            Dictionary with information about all commands.
        """
        commands_info = {}
        # Add custom commands first (they have priority)
        for name in self._custom_commands:
            commands_info[name] = self.get_command_info(name)
        # Add built-in commands (custom commands will override if same name)
        for name in self._commands:
            if name not in self._custom_commands:  # Only add if not overridden by custom
                commands_info[name] = self.get_command_info(name)
        return commands_info
    
    def discover_commands(self, package_path: str = "mcp_proxy_adapter.commands") -> None:
        """
        Automatically discovers and registers commands in the specified package.

        Args:
            package_path: Path to package with commands.
        """
        logger.info(f"Discovering commands in package: {package_path}")
        
        try:
            package = importlib.import_module(package_path)
            package_dir = os.path.dirname(package.__file__ or "")
            
            for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
                if is_pkg:
                    # Recursively traverse subpackages
                    self.discover_commands(f"{package_path}.{module_name}")
                elif module_name.endswith("_command"):
                    # Import only command modules
                    module_path = f"{package_path}.{module_name}"
                    logger.debug(f"Found command module: {module_path}")
                    
                    try:
                        module = importlib.import_module(module_path)
                        
                        # Find all command classes in the module
                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, Command) and 
                                obj != Command and
                                not inspect.isabstract(obj)):
                                
                                # Get command name before registration
                                command_name = obj.name if hasattr(obj, "name") and obj.name else obj.__name__.lower()
                                if command_name.endswith("command"):
                                    command_name = command_name[:-7]  # Remove "command" suffix
                                
                                # Register the command only if it doesn't exist
                                if not self.command_exists(command_name):
                                    self.register(cast(Type[Command], obj))
                                else:
                                    logger.debug(f"Command '{command_name}' is already registered, skipping")
                    except ValueError as e:
                        # Skip already registered commands
                        logger.debug(f"Skipping command registration: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error loading command module {module_path}: {e}")
        except Exception as e:
            logger.error(f"Error discovering commands: {e}")
            
    def register_custom_command(self, command: Union[Type[Command], Command]) -> None:
        """
        Register a custom command with priority over built-in commands.
        
        Args:
            command: Command class or instance to register.
            
        Raises:
            ValueError: If command with the same name is already registered.
        """
        # Determine if this is a class or an instance
        if isinstance(command, type) and issubclass(command, Command):
            command_class = command
            command_instance = None
        elif isinstance(command, Command):
            command_class = command.__class__
            command_instance = command
        else:
            raise ValueError(f"Invalid command type: {type(command)}. Expected Command class or instance.")
            
        # Get command name
        if not hasattr(command_class, "name") or not command_class.name:
            # Use class name if name attribute is not set
            command_name = command_class.__name__.lower()
            if command_name.endswith("command"):
                command_name = command_name[:-7]  # Remove "command" suffix
        else:
            command_name = command_class.name
            
        if command_name in self._custom_commands:
            logger.debug(f"Custom command '{command_name}' is already registered, skipping")
            raise ValueError(f"Custom command '{command_name}' is already registered")
            
        logger.debug(f"Registering custom command: {command_name}")
        self._custom_commands[command_name] = command_class
        
        # Store instance if provided
        if command_instance:
            logger.debug(f"Storing custom instance for command: {command_name}")
            self._instances[command_name] = command_instance
    
    def unregister_custom_command(self, command_name: str) -> None:
        """
        Remove custom command from registry.
        
        Args:
            command_name: Command name to remove.
            
        Raises:
            NotFoundError: If command is not found.
        """
        if command_name not in self._custom_commands:
            raise NotFoundError(f"Custom command '{command_name}' not found")
            
        logger.debug(f"Unregistering custom command: {command_name}")
        del self._custom_commands[command_name]
        
        # Also remove from instances if present
        if command_name in self._instances:
            del self._instances[command_name]
    
    def custom_command_exists(self, command_name: str) -> bool:
        """
        Check if custom command exists.
        
        Args:
            command_name: Command name to check.
            
        Returns:
            True if custom command exists, False otherwise.
        """
        return command_name in self._custom_commands
    
    def get_custom_command(self, command_name: str) -> Type[Command]:
        """
        Get custom command class.
        
        Args:
            command_name: Command name.
            
        Returns:
            Command class.
            
        Raises:
            NotFoundError: If command is not found.
        """
        if command_name not in self._custom_commands:
            raise NotFoundError(f"Custom command '{command_name}' not found")
        return self._custom_commands[command_name]
    
    def get_all_custom_commands(self) -> Dict[str, Type[Command]]:
        """
        Get all custom commands.
        
        Returns:
            Dictionary with custom command names as keys and classes as values.
        """
        return self._custom_commands.copy()
    
    def get_priority_command(self, command_name: str) -> Optional[Type[Command]]:
        """
        Get command with priority (custom commands first, then built-in).
        
        Args:
            command_name: Command name.
            
        Returns:
            Command class if found, None otherwise.
        """
        # First check custom commands
        if command_name in self._custom_commands:
            return self._custom_commands[command_name]
        
        # Then check built-in commands
        if command_name in self._commands:
            return self._commands[command_name]
        
        return None
    
    def command_exists_with_priority(self, command_name: str) -> bool:
        """
        Check if command exists (custom or built-in).
        
        Args:
            command_name: Command name to check.
            
        Returns:
            True if command exists, False otherwise.
        """
        return (command_name in self._custom_commands or 
                command_name in self._commands)
    
    def get_command_with_priority(self, command_name: str) -> Type[Command]:
        """
        Get command with priority (custom commands first, then built-in).
        
        Args:
            command_name: Command name.
            
        Returns:
            Command class.
            
        Raises:
            NotFoundError: If command is not found.
        """
        # First check custom commands
        if command_name in self._custom_commands:
            return self._custom_commands[command_name]
        
        # Then check built-in commands
        if command_name in self._commands:
            return self._commands[command_name]
        
        raise NotFoundError(f"Command '{command_name}' not found")
    
    def clear(self) -> None:
        """
        Clear all registered commands.
        """
        logger.debug("Clearing all registered commands")
        self._commands.clear()
        self._instances.clear()
        self._custom_commands.clear()
    
    def reload_config_and_commands(self, package_path: str = "mcp_proxy_adapter.commands") -> Dict[str, Any]:
        """
        Reload configuration and rediscover commands.
        
        Args:
            package_path: Path to package with commands.
            
        Returns:
            Dictionary with reload information including:
            - config_reloaded: Whether config was reloaded
            - commands_discovered: Number of commands discovered
            - custom_commands_preserved: Number of custom commands preserved
            - total_commands: Total number of commands after reload
        """
        logger.info("🔄 Starting configuration and commands reload...")
        
        # Store current custom commands
        custom_commands_backup = self._custom_commands.copy()
        
        # Reload configuration
        try:
            from mcp_proxy_adapter.config import config
            config.load_config()
            config_reloaded = True
            logger.info("✅ Configuration reloaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to reload configuration: {e}")
            config_reloaded = False
        
        # Reinitialize logging with new configuration
        try:
            from mcp_proxy_adapter.core.logging import setup_logging
            setup_logging()
            logger.info("✅ Logging reinitialized with new configuration")
        except Exception as e:
            logger.error(f"❌ Failed to reinitialize logging: {e}")
        
        # Clear all commands except custom ones
        self._commands.clear()
        self._instances.clear()
        
        # Restore custom commands
        self._custom_commands = custom_commands_backup
        custom_commands_preserved = len(custom_commands_backup)
        
        # Rediscover commands
        try:
            commands_discovered = self.discover_commands(package_path)
            logger.info(f"✅ Rediscovered {commands_discovered} commands")
        except Exception as e:
            logger.error(f"❌ Failed to rediscover commands: {e}")
            commands_discovered = 0
        
        # Get final counts
        total_commands = len(self._commands)
        built_in_commands = total_commands - custom_commands_preserved
        custom_commands = custom_commands_preserved
        
        result = {
            "config_reloaded": config_reloaded,
            "commands_discovered": commands_discovered,
            "custom_commands_preserved": custom_commands_preserved,
            "total_commands": total_commands,
            "built_in_commands": built_in_commands,
            "custom_commands": custom_commands
        }
        
        logger.info(f"🔄 Reload completed: {result}")
        return result


# Global command registry instance
registry = CommandRegistry()
