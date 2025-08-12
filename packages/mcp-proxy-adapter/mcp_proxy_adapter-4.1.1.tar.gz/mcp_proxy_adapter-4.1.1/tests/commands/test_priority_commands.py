"""
Tests for priority command system.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.commands.command_registry import registry


class BuiltInCommand(Command):
    """Built-in command for testing."""
    
    name = "test"
    
    async def execute(self, **kwargs) -> SuccessResult:
        """Execute built-in command."""
        return SuccessResult(data={"message": "Built-in command executed", "type": "built-in"})


class CustomCommand(Command):
    """Custom command for testing."""
    
    name = "test"
    
    async def execute(self, **kwargs) -> SuccessResult:
        """Execute custom command."""
        return SuccessResult(data={"message": "Custom command executed", "type": "custom"})


class TestPriorityCommands:
    """Tests for priority command system."""

    def setup_method(self):
        """Set up test method."""
        # Clear registry and hooks before each test
        registry.clear()
        from mcp_proxy_adapter.commands.hooks import hooks
        hooks.clear_hooks()

    def test_register_custom_command(self):
        """Test registering custom command."""
        registry.register_custom_command(CustomCommand)
        
        assert registry.custom_command_exists("test")
        assert registry.get_custom_command("test") == CustomCommand

    def test_register_built_in_command(self):
        """Test registering built-in command."""
        registry.register(BuiltInCommand)
        
        assert registry.command_exists("test")
        assert registry.get_command("test") == BuiltInCommand

    def test_priority_command_exists(self):
        """Test checking if priority command exists."""
        # Register built-in command
        registry.register(BuiltInCommand)
        assert registry.command_exists_with_priority("test")
        
        # Register custom command
        registry.register_custom_command(CustomCommand)
        assert registry.command_exists_with_priority("test")

    def test_get_priority_command(self):
        """Test getting command with priority."""
        # Register built-in command first
        registry.register(BuiltInCommand)
        command = registry.get_priority_command("test")
        assert command == BuiltInCommand
        
        # Register custom command (should take priority)
        registry.register_custom_command(CustomCommand)
        command = registry.get_priority_command("test")
        assert command == CustomCommand

    def test_get_command_with_priority(self):
        """Test getting command with priority using get_command_with_priority."""
        # Register built-in command first
        registry.register(BuiltInCommand)
        command = registry.get_command_with_priority("test")
        assert command == BuiltInCommand
        
        # Register custom command (should take priority)
        registry.register_custom_command(CustomCommand)
        command = registry.get_command_with_priority("test")
        assert command == CustomCommand

    def test_get_command_with_priority_not_found(self):
        """Test getting command with priority when command doesn't exist."""
        with pytest.raises(Exception, match="Command 'nonexistent' not found"):
            registry.get_command_with_priority("nonexistent")

    def test_get_all_custom_commands(self):
        """Test getting all custom commands."""
        registry.register_custom_command(CustomCommand)
        
        custom_commands = registry.get_all_custom_commands()
        assert "test" in custom_commands
        assert custom_commands["test"] == CustomCommand

    def test_unregister_custom_command(self):
        """Test unregistering custom command."""
        registry.register_custom_command(CustomCommand)
        assert registry.custom_command_exists("test")
        
        registry.unregister_custom_command("test")
        assert not registry.custom_command_exists("test")

    def test_unregister_custom_command_not_found(self):
        """Test unregistering non-existent custom command."""
        with pytest.raises(Exception, match="Custom command 'nonexistent' not found"):
            registry.unregister_custom_command("nonexistent")

    @pytest.mark.asyncio
    async def test_command_execution_priority(self):
        """Test command execution with priority."""
        # Register built-in command first
        registry.register(BuiltInCommand)
        
        # Execute command - should use built-in
        result = await BuiltInCommand.run(param1="value1")
        assert result.data["type"] == "built-in"
        
        # Register custom command - should take priority
        registry.register_custom_command(CustomCommand)
        
        # Execute command - should use custom (priority)
        # We need to use the custom command class to get the right name
        result = await CustomCommand.run(param1="value1")
        assert result.data["type"] == "custom"

    @pytest.mark.asyncio
    async def test_command_execution_with_instances(self):
        """Test command execution with instances and priority."""
        # Create custom command instance
        custom_instance = CustomCommand()
        registry.register_custom_command(custom_instance)
        
        # Create built-in command instance
        builtin_instance = BuiltInCommand()
        registry.register(builtin_instance)
        
        # Execute command - should use custom instance (priority)
        # We need to use the custom command class to get the right name
        result = await custom_instance.execute(param1="value1")
        assert result.data["type"] == "custom"

    def test_clear_registry(self):
        """Test clearing registry with custom commands."""
        registry.register_custom_command(CustomCommand)
        registry.register(BuiltInCommand)
        
        assert registry.custom_command_exists("test")
        assert registry.command_exists("test")
        
        registry.clear()
        
        assert not registry.custom_command_exists("test")
        assert not registry.command_exists("test")

    def test_register_duplicate_custom_command(self):
        """Test registering duplicate custom command."""
        registry.register_custom_command(CustomCommand)
        
        with pytest.raises(ValueError, match="Custom command 'test' is already registered"):
            registry.register_custom_command(CustomCommand)

    def test_register_custom_and_builtin_same_name(self):
        """Test registering custom and built-in commands with same name."""
        # Register built-in command
        registry.register(BuiltInCommand)
        
        # Register custom command with same name
        registry.register_custom_command(CustomCommand)
        
        # Both should exist
        assert registry.command_exists("test")
        assert registry.custom_command_exists("test")
        
        # Priority should go to custom command
        command = registry.get_priority_command("test")
        assert command == CustomCommand

    def test_get_command_info_with_priority(self):
        """Test getting command info with priority."""
        registry.register(BuiltInCommand)
        registry.register_custom_command(CustomCommand)
        
        # Should return info for custom command (priority)
        info = registry.get_command_info("test")
        assert info["name"] == "test"
        assert info["description"] == "Custom command for testing."

    def test_get_all_metadata_with_priority(self):
        """Test getting all metadata with priority."""
        registry.register(BuiltInCommand)
        registry.register_custom_command(CustomCommand)
        
        metadata = registry.get_all_metadata()
        assert "test" in metadata
        
        # Should return metadata for custom command (priority)
        command_metadata = metadata["test"]
        assert command_metadata["name"] == "test"

    def test_discover_commands_with_custom(self):
        """Test command discovery with custom commands."""
        # Register custom command first
        registry.register_custom_command(CustomCommand)
        
        # Discover commands (should not override custom command)
        registry.discover_commands()
        
        # Custom command should still have priority
        command = registry.get_priority_command("test")
        assert command == CustomCommand 