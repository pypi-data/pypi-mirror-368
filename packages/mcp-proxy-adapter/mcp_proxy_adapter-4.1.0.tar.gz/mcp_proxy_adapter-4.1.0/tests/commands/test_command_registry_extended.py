"""
Extended tests for command registry functionality.

This module contains additional tests for command_registry.py
to improve code coverage to 90%+.
"""

import pytest
import os
import importlib
import pkgutil
import inspect
from unittest.mock import patch, MagicMock, mock_open
from typing import Dict, Any, Type

from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.core.errors import NotFoundError


class TestCommandRegistryExtended:
    """Extended tests for CommandRegistry class."""

    def test_register_with_invalid_type(self):
        """Test register with invalid command type."""
        registry = CommandRegistry()
        
        with pytest.raises(ValueError, match="Invalid command type"):
            registry.register("invalid_command")

    def test_register_with_command_instance(self):
        """Test register with command instance."""
        class MockCommand(Command):
            name = "mock"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        command_instance = MockCommand()
        
        registry.register(command_instance)
        
        assert registry.command_exists("mock")
        assert registry.has_instance("mock")
        assert registry.get_command_instance("mock") == command_instance

    def test_register_with_command_class_no_name(self):
        """Test register with command class that has no name attribute."""
        class MockCommand(Command):
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        
        registry.register(MockCommand)
        
        # Should use class name without "command" suffix
        assert registry.command_exists("mock")

    def test_register_with_command_class_ending_command(self):
        """Test register with command class ending with 'command'."""
        class TestCommand(Command):
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        
        registry.register(TestCommand)
        
        # Should remove "command" suffix
        assert registry.command_exists("test")

    def test_register_duplicate_command(self):
        """Test register with duplicate command name."""
        class MockCommand(Command):
            name = "mock"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(MockCommand)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(MockCommand)

    def test_unregister_nonexistent_command(self):
        """Test unregister with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError, match="not found"):
            registry.unregister("nonexistent")

    def test_unregister_command_with_instance(self):
        """Test unregister command that has an instance."""
        class MockCommand(Command):
            name = "mock"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        command_instance = MockCommand()
        registry.register(command_instance)
        
        # Verify instance exists
        assert registry.has_instance("mock")
        
        # Unregister
        registry.unregister("mock")
        
        # Verify both command and instance are removed
        assert not registry.command_exists("mock")
        assert not registry.has_instance("mock")

    def test_get_command_nonexistent(self):
        """Test get_command with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError, match="not found"):
            registry.get_command("nonexistent")

    def test_get_command_instance_nonexistent(self):
        """Test get_command_instance with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError, match="not found"):
            registry.get_command_instance("nonexistent")

    def test_get_command_instance_creates_new(self):
        """Test get_command_instance creates new instance."""
        class MockCommand(Command):
            name = "mock"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(MockCommand)
        
        # No instance should exist initially
        assert not registry.has_instance("mock")
        
        # Get instance should create new one
        instance = registry.get_command_instance("mock")
        assert isinstance(instance, MockCommand)
        
        # Note: get_command_instance creates new instance but doesn't store it
        # So has_instance will still return False
        assert not registry.has_instance("mock")

    def test_get_command_info_nonexistent(self):
        """Test get_command_info with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError):
            info = registry.get_command_info("nonexistent")

    def test_get_command_metadata_nonexistent(self):
        """Test get_command_metadata with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError):
            metadata = registry.get_command_metadata("nonexistent")

    @patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module')
    @patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules')
    def test_discover_commands_import_error(self, mock_iter_modules, mock_import_module):
        """Test discover_commands with import error."""
        mock_import_module.side_effect = ImportError("Module not found")
        
        registry = CommandRegistry()
        registry.discover_commands("invalid.package")
        
        # Should handle error gracefully
        assert len(registry.get_all_commands()) == 0

    @patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module')
    @patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules')
    def test_discover_commands_module_error(self, mock_iter_modules, mock_import_module):
        """Test discover_commands with module loading error."""
        # Setup mocks
        mock_package = MagicMock()
        mock_package.__file__ = "/path/to/package"
        mock_import_module.return_value = mock_package
        
        mock_iter_modules.return_value = [("", "test_command", False)]
        
        # Mock module import to raise error
        with patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module') as mock_module_import:
            mock_module_import.side_effect = [mock_package, Exception("Module error")]
            
            registry = CommandRegistry()
            registry.discover_commands("test.package")
            
            # Should handle error gracefully
            assert len(registry.get_all_commands()) == 0

    @patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module')
    @patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules')
    def test_discover_commands_with_subpackages(self, mock_iter_modules, mock_import_module):
        """Test discover_commands with subpackages."""
        # Setup mocks
        mock_package = MagicMock()
        mock_package.__file__ = "/path/to/package"
        mock_import_module.return_value = mock_package
        
        # Mock subpackage
        mock_iter_modules.return_value = [("", "subpackage", True)]
        
        registry = CommandRegistry()
        
        # The current implementation doesn't recursively call discover_commands for subpackages
        # It just processes the current package level
        registry.discover_commands("test.package")
        
        # Verify that the method was called with the original package path
        # The implementation should handle subpackages internally
        assert mock_import_module.called

    @patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module')
    @patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules')
    def test_discover_commands_already_registered(self, mock_iter_modules, mock_import_module):
        """Test discover_commands with already registered command."""
        # Setup mocks
        mock_package = MagicMock()
        mock_package.__file__ = "/path/to/package"
        mock_import_module.return_value = mock_package
        
        mock_iter_modules.return_value = [("", "test_command", False)]
        
        class MockCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        # Mock module with command
        mock_module = MagicMock()
        mock_module.MockCommand = MockCommand
        
        with patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module') as mock_module_import:
            mock_module_import.side_effect = [mock_package, mock_module]
            
            with patch('mcp_proxy_adapter.commands.command_registry.inspect.getmembers') as mock_getmembers:
                mock_getmembers.return_value = [("MockCommand", MockCommand)]
                
                registry = CommandRegistry()
                registry.register(MockCommand)  # Register first
                
                # Try to discover again
                registry.discover_commands("test.package")
                
                # Should skip already registered command
                assert len(registry.get_all_commands()) == 1

    def test_register_custom_command_with_invalid_type(self):
        """Test register_custom_command with invalid type."""
        registry = CommandRegistry()
        
        with pytest.raises(ValueError, match="Invalid command type"):
            registry.register_custom_command("invalid_command")

    def test_register_custom_command_duplicate(self):
        """Test register_custom_command with duplicate name."""
        class MockCommand(Command):
            name = "mock"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register_custom_command(MockCommand)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register_custom_command(MockCommand)

    def test_unregister_custom_command_nonexistent(self):
        """Test unregister_custom_command with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError, match="not found"):
            registry.unregister_custom_command("nonexistent")

    def test_get_custom_command_nonexistent(self):
        """Test get_custom_command with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError, match="not found"):
            registry.get_custom_command("nonexistent")

    def test_get_priority_command_custom_first(self):
        """Test get_priority_command returns custom command first."""
        class BuiltInCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        class CustomCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(BuiltInCommand)
        registry.register_custom_command(CustomCommand)
        
        # Should return custom command
        command_class = registry.get_priority_command("test")
        assert command_class == CustomCommand

    def test_get_priority_command_builtin_fallback(self):
        """Test get_priority_command falls back to built-in command."""
        class BuiltInCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(BuiltInCommand)
        
        # Should return built-in command
        command_class = registry.get_priority_command("test")
        assert command_class == BuiltInCommand

    def test_get_priority_command_nonexistent(self):
        """Test get_priority_command with nonexistent command."""
        registry = CommandRegistry()
        
        command_class = registry.get_priority_command("nonexistent")
        assert command_class is None

    def test_command_exists_with_priority_custom(self):
        """Test command_exists_with_priority with custom command."""
        class CustomCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register_custom_command(CustomCommand)
        
        assert registry.command_exists_with_priority("test")

    def test_command_exists_with_priority_builtin(self):
        """Test command_exists_with_priority with built-in command."""
        class BuiltInCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(BuiltInCommand)
        
        assert registry.command_exists_with_priority("test")

    def test_command_exists_with_priority_nonexistent(self):
        """Test command_exists_with_priority with nonexistent command."""
        registry = CommandRegistry()
        
        assert not registry.command_exists_with_priority("nonexistent")

    def test_get_command_with_priority_custom(self):
        """Test get_command_with_priority returns custom command first."""
        class BuiltInCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        class CustomCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(BuiltInCommand)
        registry.register_custom_command(CustomCommand)
        
        # Should return custom command
        command_class = registry.get_command_with_priority("test")
        assert command_class == CustomCommand

    def test_get_command_with_priority_nonexistent(self):
        """Test get_command_with_priority with nonexistent command."""
        registry = CommandRegistry()
        
        with pytest.raises(NotFoundError, match="not found"):
            registry.get_command_with_priority("nonexistent")

    def test_clear_removes_all_commands(self):
        """Test clear removes all commands and instances."""
        class MockCommand(Command):
            name = "mock"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        command_instance = MockCommand()
        registry.register(command_instance)
        registry.register_custom_command(MockCommand)
        
        # Verify commands exist
        assert registry.command_exists("mock")
        assert registry.custom_command_exists("mock")
        assert registry.has_instance("mock")
        
        # Clear
        registry.clear()
        
        # Verify all removed
        assert not registry.command_exists("mock")
        assert not registry.custom_command_exists("mock")
        assert not registry.has_instance("mock")

    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.core.logging.setup_logging')
    def test_reload_config_and_commands_success(self, mock_setup_logging, mock_config):
        """Test reload_config_and_commands with success."""
        class MockCommand(Command):
            name = "mock"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(MockCommand)
        
        # Setup mocks
        mock_config.load_config.return_value = None
        
        # Execute
        registry.reload_config_and_commands()
        
        # Verify
        mock_config.load_config.assert_called_once()
        mock_setup_logging.assert_called_once()

    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.core.logging.setup_logging')
    def test_reload_config_and_commands_config_error(self, mock_setup_logging, mock_config):
        """Test reload_config_and_commands with config error."""
        registry = CommandRegistry()
        
        # Setup mocks to raise error
        mock_config.load_config.side_effect = Exception("Config error")
        
        # Execute - should handle error gracefully
        registry.reload_config_and_commands()
        
        # Verify
        mock_config.load_config.assert_called_once()
        mock_setup_logging.assert_called_once()

    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.core.logging.setup_logging')
    def test_reload_config_and_commands_discovery_error(self, mock_setup_logging, mock_config):
        """Test reload_config_and_commands with discovery error."""
        registry = CommandRegistry()
        
        # Setup mocks
        mock_config.load_config.return_value = None
        
        with patch.object(registry, 'discover_commands') as mock_discover:
            mock_discover.side_effect = Exception("Discovery error")
            
            # Execute - should handle error gracefully
            registry.reload_config_and_commands()
            
            # Verify
            mock_config.load_config.assert_called_once()
            mock_setup_logging.assert_called_once()
            mock_discover.assert_called_once()

    def test_get_all_commands_info_priority_order(self):
        """Test get_all_commands_info returns commands in priority order."""
        class BuiltInCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        class CustomCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        registry = CommandRegistry()
        registry.register(BuiltInCommand)
        registry.register_custom_command(CustomCommand)
        
        commands_info = registry.get_all_commands_info()
        
        # Custom command should override built-in command
        assert "test" in commands_info
        assert len(commands_info) == 1  # Only one entry for "test" 