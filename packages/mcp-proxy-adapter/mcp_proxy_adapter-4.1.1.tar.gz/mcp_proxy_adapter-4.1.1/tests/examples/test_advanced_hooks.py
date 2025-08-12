"""
Tests for advanced hooks example.

This module tests the advanced hooks functionality including:
- Data transformation hooks
- Interception hooks
- Conditional transformation hooks
- Smart interception hooks
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from mcp_proxy_adapter.examples.custom_commands import advanced_hooks
from mcp_proxy_adapter.commands.hooks import HookContext, HookType
from mcp_proxy_adapter.commands.result import CommandResult


class TestDataTransformHooks:
    """Test data transformation hooks."""

    def test_data_transform_before_hook_with_string_data(self):
        """Test data_transform_before_hook with string data."""
        context = HookContext(
            command_name="data_transform",
            params={"data": {"name": "test", "value": "hello"}},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.data_transform_before_hook(context)
        
        assert context.params["data"]["pre_name_post"] == "ENHANCED_test_PROCESSED"
        assert context.params["data"]["pre_value_post"] == "ENHANCED_hello_PROCESSED"
        assert context.params["data"]["_hook_modified"] is True
        assert context.params["data_modified"] is True

    def test_data_transform_before_hook_with_numeric_data(self):
        """Test data_transform_before_hook with numeric data."""
        context = HookContext(
            command_name="data_transform",
            params={"data": {"count": 5, "price": 10.5}},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.data_transform_before_hook(context)
        
        assert context.params["data"]["doubled_count"] == 10
        assert context.params["data"]["doubled_price"] == 21.0
        assert context.params["data"]["_hook_modified"] is True

    def test_data_transform_before_hook_with_mixed_data(self):
        """Test data_transform_before_hook with mixed data types."""
        context = HookContext(
            command_name="data_transform",
            params={"data": {"name": "test", "count": 3, "active": True}},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.data_transform_before_hook(context)
        
        assert context.params["data"]["pre_name_post"] == "ENHANCED_test_PROCESSED"
        assert context.params["data"]["doubled_count"] == 6
        assert context.params["data"]["doubled_active"] == 2
        assert context.params["data"]["_hook_modified"] is True

    def test_data_transform_after_hook_with_result(self):
        """Test data_transform_after_hook with result."""
        # Create mock result with transformed_data
        mock_result = MagicMock()
        mock_result.transformed_data = {"name": "test", "value": "hello"}
        
        context = HookContext(
            command_name="data_transform",
            params={},
            result=mock_result,
            hook_type=HookType.AFTER_EXECUTION
        )
        
        advanced_hooks.data_transform_after_hook(context)
        
        assert context.result.transformed_data["formatted_name"] == "✨ test ✨"
        assert context.result.transformed_data["formatted_value"] == "✨ hello ✨"
        assert context.result.transformed_data["_formatted_by_hook"] is True

    def test_data_transform_after_hook_without_result(self):
        """Test data_transform_after_hook without result."""
        context = HookContext(
            command_name="data_transform",
            params={},
            result=None,
            hook_type=HookType.AFTER_EXECUTION
        )
        
        # Should not raise any exception
        advanced_hooks.data_transform_after_hook(context)


class TestInterceptHooks:
    """Test interception hooks."""

    @patch('mcp_proxy_adapter.examples.custom_commands.intercept_command.InterceptResult')
    def test_intercept_before_hook_bypass_flag_zero(self, mock_intercept_result):
        """Test intercept_before_hook with bypass_flag = 0."""
        mock_result = MagicMock()
        mock_intercept_result.return_value = mock_result
        
        context = HookContext(
            command_name="intercept",
            params={"bypass_flag": 0, "message": "test"},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.intercept_before_hook(context)
        
        assert context.result == mock_result
        assert context.standard_processing is False
        mock_intercept_result.assert_called_once()

    def test_intercept_before_hook_bypass_flag_non_zero(self):
        """Test intercept_before_hook with bypass_flag != 0."""
        context = HookContext(
            command_name="intercept",
            params={"bypass_flag": 1, "message": "test"},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.intercept_before_hook(context)
        
        assert context.standard_processing is True
        assert context.params["hook_processed"] is True

    def test_intercept_after_hook_with_standard_processing(self):
        """Test intercept_after_hook with standard processing."""
        mock_result = MagicMock()
        mock_result.hook_data = {}
        
        context = HookContext(
            command_name="intercept",
            params={},
            result=mock_result,
            standard_processing=True,
            hook_type=HookType.AFTER_EXECUTION
        )
        
        advanced_hooks.intercept_after_hook(context)
        
        assert context.result.hook_data["after_hook_processed"] is True
        assert "after_hook_time" in context.result.hook_data

    def test_intercept_after_hook_without_standard_processing(self):
        """Test intercept_after_hook without standard processing."""
        mock_result = MagicMock()
        mock_result.hook_data = {}
        
        context = HookContext(
            command_name="intercept",
            params={},
            result=mock_result,
            standard_processing=False,
            hook_type=HookType.AFTER_EXECUTION
        )
        
        advanced_hooks.intercept_after_hook(context)
        
        assert context.result.hook_data["after_hook_processed"] is True
        assert "after_hook_time" in context.result.hook_data


class TestConditionalTransformHook:
    """Test conditional transformation hook."""

    def test_conditional_transform_hook_before_with_special_data(self):
        """Test conditional_transform_hook before with special data."""
        context = HookContext(
            command_name="data_transform",
            params={"data": {"message": "special content"}, "transform_type": "default"},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.conditional_transform_hook(context)
        
        assert context.params["transform_type"] == "uppercase"
        assert context.params["_special_enhancement"] is True

    def test_conditional_transform_hook_before_with_test_data(self):
        """Test conditional_transform_hook before with test data."""
        context = HookContext(
            command_name="data_transform",
            params={"data": {"message": "test content"}, "transform_type": "default"},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.conditional_transform_hook(context)
        
        assert context.params["transform_type"] == "reverse"
        assert context.params["_test_mode"] is True

    def test_conditional_transform_hook_before_with_normal_data(self):
        """Test conditional_transform_hook before with normal data."""
        context = HookContext(
            command_name="data_transform",
            params={"data": {"message": "normal content"}, "transform_type": "default"},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.conditional_transform_hook(context)
        
        assert context.params["transform_type"] == "default"
        assert "_special_enhancement" not in context.params
        assert "_test_mode" not in context.params

    def test_conditional_transform_hook_after_with_result(self):
        """Test conditional_transform_hook after with result."""
        mock_result = MagicMock()
        mock_result.processing_info = {}
        
        context = HookContext(
            command_name="data_transform",
            params={},
            result=mock_result,
            hook_type=HookType.AFTER_EXECUTION
        )
        
        advanced_hooks.conditional_transform_hook(context)
        
        assert context.result.processing_info["conditional_processed"] is True
        assert "conditional_time" in context.result.processing_info


class TestSmartInterceptHook:
    """Test smart interception hook."""

    @patch('mcp_proxy_adapter.examples.custom_commands.intercept_command.InterceptResult')
    def test_smart_intercept_hook_before_blocked_action(self, mock_intercept_result):
        """Test smart_intercept_hook before with blocked action."""
        mock_result = MagicMock()
        mock_intercept_result.return_value = mock_result
        
        context = HookContext(
            command_name="intercept",
            params={"action": "blocked", "bypass_flag": 1},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.smart_intercept_hook(context)
        
        assert context.result == mock_result
        assert context.standard_processing is False
        mock_intercept_result.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.intercept_command.InterceptResult')
    def test_smart_intercept_hook_before_bypass_flag_zero(self, mock_intercept_result):
        """Test smart_intercept_hook before with bypass_flag = 0."""
        mock_result = MagicMock()
        mock_intercept_result.return_value = mock_result
        
        context = HookContext(
            command_name="intercept",
            params={"action": "allowed", "bypass_flag": 0},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.smart_intercept_hook(context)
        
        assert context.result == mock_result
        assert context.standard_processing is False
        mock_intercept_result.assert_called_once()

    def test_smart_intercept_hook_before_allowed_action(self):
        """Test smart_intercept_hook before with allowed action."""
        context = HookContext(
            command_name="intercept",
            params={"action": "allowed", "bypass_flag": 1},
            hook_type=HookType.BEFORE_EXECUTION
        )
        
        advanced_hooks.smart_intercept_hook(context)
        
        assert context.result is None
        assert context.standard_processing is True


class TestRegisterAdvancedHooks:
    """Test register_advanced_hooks function."""

    def test_register_advanced_hooks(self):
        """Test register_advanced_hooks function."""
        mock_hooks_manager = MagicMock()
        
        advanced_hooks.register_advanced_hooks(mock_hooks_manager)
        
        # Verify all hooks are registered
        assert mock_hooks_manager.register_before_hook.call_count == 2
        assert mock_hooks_manager.register_after_hook.call_count == 2
        assert mock_hooks_manager.register_global_before_hook.call_count == 2
        assert mock_hooks_manager.register_global_after_hook.call_count == 1 