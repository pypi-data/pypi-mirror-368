"""
Tests for command hooks system.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any

from mcp_proxy_adapter.commands.hooks import hooks, HookContext, HookType
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult


class TestCommand(Command):
    """Test command for hook testing."""
    
    name = "test"
    
    async def execute(self, **kwargs) -> SuccessResult:
        """Execute test command."""
        return SuccessResult(data={"message": "Test executed", "params": kwargs})


class TestHooks:
    """Tests for command hooks system."""

    def setup_method(self):
        """Set up test method."""
        # Clear all hooks before each test
        hooks.clear_hooks()

    def test_hook_context_creation(self):
        """Test HookContext creation."""
        context = HookContext(
            command_name="test",
            params={"param1": "value1"},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        assert context.command_name == "test"
        assert context.params == {"param1": "value1"}
        assert context.hook_type == HookType.BEFORE_EXECUTION
        assert context.standard_processing is True
        assert context.result is None

    def test_register_before_hook(self):
        """Test registering before hook."""
        def before_hook(context: HookContext):
            context.standard_processing = False
        
        hooks.register_before_hook("test", before_hook)
        
        # Check that hook was registered
        hook_info = hooks.get_hook_info()
        assert "test" in hook_info["before_hooks"]
        assert hook_info["before_hooks"]["test"] == 1

    def test_register_after_hook(self):
        """Test registering after hook."""
        def after_hook(context: HookContext):
            pass
        
        hooks.register_after_hook("test", after_hook)
        
        # Check that hook was registered
        hook_info = hooks.get_hook_info()
        assert "test" in hook_info["after_hooks"]
        assert hook_info["after_hooks"]["test"] == 1

    def test_register_global_before_hook(self):
        """Test registering global before hook."""
        def global_before_hook(context: HookContext):
            pass
        
        hooks.register_global_before_hook(global_before_hook)
        
        # Check that hook was registered
        hook_info = hooks.get_hook_info()
        assert hook_info["global_before_hooks"] == 1

    def test_register_global_after_hook(self):
        """Test registering global after hook."""
        def global_after_hook(context: HookContext):
            pass
        
        hooks.register_global_after_hook(global_after_hook)
        
        # Check that hook was registered
        hook_info = hooks.get_hook_info()
        assert hook_info["global_after_hooks"] == 1

    def test_execute_before_hooks(self):
        """Test executing before hooks."""
        hook_called = False
        hook_context = None
        
        def before_hook(context: HookContext):
            nonlocal hook_called, hook_context
            hook_called = True
            hook_context = context
            context.standard_processing = False
        
        hooks.register_before_hook("test", before_hook)
        
        params = {"param1": "value1"}
        context = hooks.execute_before_hooks("test", params)
        
        assert hook_called
        assert hook_context is not None
        assert hook_context.command_name == "test"
        assert hook_context.params == params
        assert hook_context.hook_type == HookType.BEFORE_EXECUTION
        assert hook_context.standard_processing is False

    def test_execute_after_hooks(self):
        """Test executing after hooks."""
        hook_called = False
        hook_context = None
        
        def after_hook(context: HookContext):
            nonlocal hook_called, hook_context
            hook_called = True
            hook_context = context
        
        hooks.register_after_hook("test", after_hook)
        
        params = {"param1": "value1"}
        result = SuccessResult(data={"test": "result"})
        context = hooks.execute_after_hooks("test", params, result)
        
        assert hook_called
        assert hook_context is not None
        assert hook_context.command_name == "test"
        assert hook_context.params == params
        assert hook_context.hook_type == HookType.AFTER_EXECUTION
        assert hook_context.result == result

    def test_execute_global_hooks(self):
        """Test executing global hooks."""
        global_before_called = False
        global_after_called = False
        
        def global_before_hook(context: HookContext):
            nonlocal global_before_called
            global_before_called = True
        
        def global_after_hook(context: HookContext):
            nonlocal global_after_called
            global_after_called = True
        
        hooks.register_global_before_hook(global_before_hook)
        hooks.register_global_after_hook(global_after_hook)
        
        params = {"param1": "value1"}
        
        # Execute before hooks
        context = hooks.execute_before_hooks("test", params)
        assert global_before_called
        
        # Execute after hooks
        result = SuccessResult(data={"test": "result"})
        context = hooks.execute_after_hooks("test", params, result)
        assert global_after_called

    def test_hook_error_handling(self, caplog):
        """Test hook error handling."""
        def error_hook(context: HookContext):
            raise Exception("Hook error")
        
        hooks.register_before_hook("test", error_hook)
        
        # Execute hooks - should not raise exception
        hooks.execute_before_hooks("test", {})
        
        # Verify error was logged
        assert "Error in before hook for command test: Hook error" in caplog.text

    def test_unregister_hooks(self):
        """Test unregistering hooks."""
        def test_hook(context: HookContext):
            pass
        
        # Register hooks
        hooks.register_before_hook("test", test_hook)
        hooks.register_after_hook("test", test_hook)
        hooks.register_global_before_hook(test_hook)
        hooks.register_global_after_hook(test_hook)
        
        # Unregister hooks
        hooks.unregister_before_hook("test", test_hook)
        hooks.unregister_after_hook("test", test_hook)
        hooks.unregister_global_before_hook(test_hook)
        hooks.unregister_global_after_hook(test_hook)
        
        # Check that hooks were unregistered
        hook_info = hooks.get_hook_info()
        # After unregistering, the command should not be in the hooks dict
        assert "test" not in hook_info["before_hooks"]
        assert "test" not in hook_info["after_hooks"]
        assert hook_info["global_before_hooks"] == 0
        assert hook_info["global_after_hooks"] == 0

    def test_clear_hooks(self):
        """Test clearing hooks."""
        def test_hook(context: HookContext):
            pass
        
        # Register hooks
        hooks.register_before_hook("test1", test_hook)
        hooks.register_after_hook("test2", test_hook)
        hooks.register_global_before_hook(test_hook)
        hooks.register_global_after_hook(test_hook)
        
        # Clear all hooks
        hooks.clear_hooks()
        
        # Check that all hooks were cleared
        hook_info = hooks.get_hook_info()
        assert hook_info["before_hooks"] == {}
        assert hook_info["after_hooks"] == {}
        assert hook_info["global_before_hooks"] == 0
        assert hook_info["global_after_hooks"] == 0

    def test_clear_specific_command_hooks(self):
        """Test clearing hooks for specific command."""
        def test_hook(context: HookContext):
            pass
        
        # Register hooks for multiple commands
        hooks.register_before_hook("test1", test_hook)
        hooks.register_after_hook("test1", test_hook)
        hooks.register_before_hook("test2", test_hook)
        hooks.register_after_hook("test2", test_hook)
        
        # Clear hooks for test1 only
        hooks.clear_hooks("test1")
        
        # Check that only test1 hooks were cleared
        hook_info = hooks.get_hook_info()
        assert "test1" not in hook_info["before_hooks"]
        assert "test1" not in hook_info["after_hooks"]
        assert "test2" in hook_info["before_hooks"]
        assert "test2" in hook_info["after_hooks"]

    @pytest.mark.asyncio
    async def test_command_with_hooks(self):
        """Test command execution with hooks."""
        hook_called = False
        standard_processing = True
        
        def before_hook(context: HookContext):
            nonlocal hook_called, standard_processing
            hook_called = True
            context.standard_processing = standard_processing
        
        hooks.register_before_hook("test", before_hook)
        
        # Register the test command
        from mcp_proxy_adapter.commands.command_registry import registry
        registry.register(TestCommand)
        
        # Test with standard processing enabled
        standard_processing = True
        result = await TestCommand.run(param1="value1")
        
        assert hook_called
        assert isinstance(result, SuccessResult)
        assert result.data["message"] == "Test executed"
        
        # Test with standard processing disabled
        hook_called = False
        standard_processing = False
        result = await TestCommand.run(param1="value1")
        
        assert hook_called
        assert isinstance(result, SuccessResult)
        assert result.data == {"param1": "value1"}  # Should return params as result

    @pytest.mark.asyncio
    async def test_command_with_after_hook(self):
        """Test command execution with after hook."""
        after_hook_called = False
        
        def after_hook(context: HookContext):
            nonlocal after_hook_called
            after_hook_called = True
            # Modify the result
            if isinstance(context.result, SuccessResult):
                context.result.data["modified"] = True
        
        hooks.register_after_hook("test", after_hook)
        
        # Register the test command
        from mcp_proxy_adapter.commands.command_registry import registry
        registry.register(TestCommand)
        
        result = await TestCommand.run(param1="value1")
        
        assert after_hook_called
        assert isinstance(result, SuccessResult)
        assert result.data["modified"] is True

    def test_multiple_hooks_same_command(self):
        """Test multiple hooks for the same command."""
        hook1_called = False
        hook2_called = False
        
        def hook1(context: HookContext):
            nonlocal hook1_called
            hook1_called = True
        
        def hook2(context: HookContext):
            nonlocal hook2_called
            hook2_called = True
            context.standard_processing = False
        
        hooks.register_before_hook("test", hook1)
        hooks.register_before_hook("test", hook2)
        
        params = {"param1": "value1"}
        context = hooks.execute_before_hooks("test", params)
        
        assert hook1_called
        assert hook2_called
        assert context.standard_processing is False  # Last hook wins 