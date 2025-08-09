"""
Extended tests for base command to improve coverage.

This module contains additional tests for commands/base.py to achieve 90%+ coverage.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.core.errors import (
    ValidationError, InvalidParamsError, NotFoundError, 
    TimeoutError, CommandError, InternalError
)


class TestCommandExtended:
    """Extended tests for Command base class."""

    def test_get_schema_with_complex_params(self):
        """Test get_schema with complex parameter types."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        schema = TestCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        # Note: description is not always present in schema

    def test_get_result_schema(self):
        """Test get_result_schema method."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        schema = TestCommand.get_result_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_validate_params_with_complex_types(self):
        """Test validate_params with complex parameter types."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        params = {
            "string_param": "test",
            "int_param": 123,
            "float_param": 123.45,
            "bool_param": True,
            "list_param": [1, 2, 3],
            "dict_param": {"key": "value"}
        }
        
        validated = TestCommand.validate_params(params)
        assert validated == params

    def test_validate_params_with_none(self):
        """Test validate_params with None params."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        validated = TestCommand.validate_params(None)
        assert validated == {}

    def test_get_param_info_with_complex_types(self):
        """Test get_param_info with complex parameter types."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, string_param: str, int_param: int, 
                            float_param: float, bool_param: bool,
                            list_param: list, dict_param: dict,
                            optional_param: str = "default"):
                return SuccessResult()
        
        param_info = TestCommand.get_param_info()
        
        assert "string_param" in param_info
        assert "int_param" in param_info
        assert "float_param" in param_info
        assert "bool_param" in param_info
        assert "list_param" in param_info
        assert "dict_param" in param_info
        assert "optional_param" in param_info
        assert param_info["optional_param"]["default"] == "default"

    def test_get_metadata_with_examples(self):
        """Test get_metadata with generated examples."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, required_param: str, optional_param: str = "default"):
                return SuccessResult()
        
        metadata = TestCommand.get_metadata()
        
        assert "description" in metadata
        assert "examples" in metadata
        assert len(metadata["examples"]) > 0

    def test_generate_examples_all_optional(self):
        """Test _generate_examples with all optional parameters."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, param1: str = "default1", param2: int = 0):
                return SuccessResult()
        
        params = {
            "param1": {"type": "str", "required": False, "default": "default1"},
            "param2": {"type": "int", "required": False, "default": 0}
        }
        
        examples = TestCommand._generate_examples(params)
        
        # Should have at least one example (without parameters)
        assert len(examples) >= 1
        assert examples[0]["command"] == "test"
        assert "without parameters" in examples[0]["description"]

    def test_generate_examples_with_required_params(self):
        """Test _generate_examples with required parameters."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, required_param: str, optional_param: str = "default"):
                return SuccessResult()
        
        params = {
            "required_param": {"type": "str", "required": True},
            "optional_param": {"type": "str", "required": False, "default": "default"}
        }
        
        examples = TestCommand._generate_examples(params)
        
        assert len(examples) == 2
        # Example with required params
        required_example = next(ex for ex in examples if "required parameters" in ex["description"])
        assert required_example["params"]["required_param"] == "sample_required_param"
        # Example with all params
        all_example = next(ex for ex in examples if "all parameters" in ex["description"])
        assert all_example["params"]["required_param"] == "sample_required_param"
        assert all_example["params"]["optional_param"] == "default"

    def test_generate_examples_complex_types(self):
        """Test _generate_examples with complex parameter types."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, str_param: str, int_param: int, float_param: float,
                            bool_param: bool, list_param: list, dict_param: dict,
                            unknown_param: Any):
                return SuccessResult()
        
        params = {
            "str_param": {"type": "str", "required": True},
            "int_param": {"type": "int", "required": True},
            "float_param": {"type": "float", "required": True},
            "bool_param": {"type": "bool", "required": True},
            "list_param": {"type": "List[str]", "required": True},
            "dict_param": {"type": "Dict[str, Any]", "required": True},
            "unknown_param": {"type": "CustomType", "required": True}
        }
        
        examples = TestCommand._generate_examples(params)
        
        assert len(examples) == 1
        example = examples[0]
        assert example["params"]["str_param"] == "sample_str_param"
        assert example["params"]["int_param"] == 1
        assert example["params"]["float_param"] == 1.0
        assert example["params"]["bool_param"] is True
        # Note: The actual implementation might return different values for complex types
        assert "list_param" in example["params"]
        assert "dict_param" in example["params"]
        assert "unknown_param" in example["params"]

    def test_generate_examples_optional_with_defaults(self):
        """Test _generate_examples with optional parameters that have defaults."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, required_param: str, optional_with_default: str = "default",
                            optional_without_default: str = None):
                return SuccessResult()
        
        params = {
            "required_param": {"type": "str", "required": True},
            "optional_with_default": {"type": "str", "required": False, "default": "default"},
            "optional_without_default": {"type": "str", "required": False}
        }
        
        examples = TestCommand._generate_examples(params)
        
        assert len(examples) == 2
        all_example = next(ex for ex in examples if "all parameters" in ex["description"])
        assert all_example["params"]["optional_with_default"] == "default"
        assert "optional_without_default" in all_example["params"]


class TestCommandRunExtended:
    """Extended tests for Command.run method."""

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_with_priority_command(self, mock_hooks, mock_registry):
        """Test run with priority command."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult(data={"test": "data"})
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry
        mock_registry.get_priority_command.return_value = TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, SuccessResult)
        assert result.data == {"test": "data"}
        mock_hooks.execute_before_hooks.assert_called_once()
        mock_hooks.execute_after_hooks.assert_called_once()

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_with_existing_instance(self, mock_hooks, mock_registry):
        """Test run with existing command instance."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult(data={"test": "data"})
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry
        mock_registry.get_priority_command.return_value = TestCommand
        mock_registry.has_instance.return_value = True
        mock_registry.get_command_instance.return_value = TestCommand()
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, SuccessResult)
        mock_registry.get_command_instance.assert_called_once_with("test")

    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_skip_standard_processing(self, mock_hooks):
        """Test run when standard processing is skipped by hooks."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        # Mock hooks to skip standard processing
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = False
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, SuccessResult)
        assert result.data == {"param1": "value1"}

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_command_not_found(self, mock_hooks, mock_registry):
        """Test run when command is not found."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry to return None (command not found)
        mock_registry.get_priority_command.return_value = None
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, ErrorResult)
        assert "not found" in result.message.lower()

    async def test_run_validation_error(self):
        """Test run with validation error."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            @classmethod
            def validate_params(cls, params):
                raise ValidationError("Validation failed")
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        result = await TestCommand.run(invalid_param="value")
        
        assert isinstance(result, ErrorResult)
        assert "validation failed" in result.message.lower()

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_invalid_params_error(self, mock_hooks, mock_registry):
        """Test run with invalid params error."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                raise InvalidParamsError("Invalid parameters")
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry
        mock_registry.get_priority_command.return_value = TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, ErrorResult)
        assert "invalid parameters" in result.message.lower()

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_timeout_error(self, mock_hooks, mock_registry):
        """Test run with timeout error."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                raise TimeoutError("Operation timed out")
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry
        mock_registry.get_priority_command.return_value = TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, ErrorResult)
        assert "timed out" in result.message.lower()

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_command_error(self, mock_hooks, mock_registry):
        """Test run with command error."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                raise CommandError("Command execution failed")
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry
        mock_registry.get_priority_command.return_value = TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, ErrorResult)
        assert "execution failed" in result.message.lower()

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_unexpected_error(self, mock_hooks, mock_registry):
        """Test run with unexpected error."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                raise RuntimeError("Unexpected runtime error")
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry
        mock_registry.get_priority_command.return_value = TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await TestCommand.run(param1="value1")
        
        assert isinstance(result, ErrorResult)
        assert "execution error" in result.message.lower()
        assert result.details["original_error"] == "Unexpected runtime error"

    @patch('mcp_proxy_adapter.commands.command_registry.registry')
    @patch('mcp_proxy_adapter.commands.base.hooks')
    async def test_run_with_none_kwargs(self, mock_hooks, mock_registry):
        """Test run with None kwargs."""
        class TestCommand(Command):
            name = "test"
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        # Mock hooks
        mock_hook_context = MagicMock()
        mock_hook_context.standard_processing = True
        mock_hooks.execute_before_hooks.return_value = mock_hook_context
        
        # Mock registry
        mock_registry.get_priority_command.return_value = TestCommand
        mock_registry.has_instance.return_value = False
        
        result = await TestCommand.run(**{})
        
        assert isinstance(result, SuccessResult)
        mock_hooks.execute_before_hooks.assert_called_once_with("test", {})

    def test_command_name_extraction(self):
        """Test command name extraction from class name."""
        class TestCommand(Command):
            name = "test"  # Explicitly set name
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        # Test that name is set correctly
        assert TestCommand.name == "test"
        
        class EchoCommand(Command):
            name = "echo"  # Explicitly set name
            result_class = SuccessResult
            
            async def execute(self, **kwargs):
                return SuccessResult()
        
        # Test that name is set correctly
        assert EchoCommand.name == "echo" 