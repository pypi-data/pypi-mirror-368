"""
Extended tests for reload commands.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.commands.reload_command import ReloadResult, ReloadCommand
from mcp_proxy_adapter.commands.reload_settings_command import ReloadSettingsResult, ReloadSettingsCommand


class TestReloadResultExtended:
    """Extended tests for ReloadResult class."""
    
    def test_init_with_all_parameters(self):
        """Test ReloadResult initialization with all parameters."""
        result = ReloadResult(
            config_reloaded=True,
            commands_discovered=5,
            custom_commands_preserved=2,
            total_commands=10,
            built_in_commands=8,
            custom_commands=2,
            server_restart_required=True,
            success=True,
            error_message=None
        )
        
        assert result.config_reloaded is True
        assert result.commands_discovered == 5
        assert result.custom_commands_preserved == 2
        assert result.total_commands == 10
        assert result.built_in_commands == 8
        assert result.custom_commands == 2
        assert result.server_restart_required is True
        assert result.success is True
        assert result.error_message is None
    
    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        result = ReloadResult(
            config_reloaded=True,
            commands_discovered=5,
            custom_commands_preserved=2,
            total_commands=10,
            built_in_commands=8,
            custom_commands=2,
            server_restart_required=True,
            success=True,
            error_message=None
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["config_reloaded"] is True
        assert data["commands_discovered"] == 5
        assert data["custom_commands_preserved"] == 2
        assert data["total_commands"] == 10
        assert data["built_in_commands"] == 8
        assert data["custom_commands"] == 2
        assert data["server_restart_required"] is True
        assert data["message"] == "Server restart required to apply configuration changes"
        assert data["error_message"] is None
    
    def test_to_dict_with_minimal_fields(self):
        """Test to_dict method with minimal fields."""
        result = ReloadResult(
            config_reloaded=False,
            commands_discovered=0,
            custom_commands_preserved=0,
            total_commands=0,
            built_in_commands=0,
            custom_commands=0,
            server_restart_required=False,
            success=False,
            error_message="Test error"
        )
        
        data = result.to_dict()
        assert data["success"] is False
        assert data["config_reloaded"] is False
        assert data["commands_discovered"] == 0
        assert data["custom_commands_preserved"] == 0
        assert data["total_commands"] == 0
        assert data["built_in_commands"] == 0
        assert data["custom_commands"] == 0
        assert data["server_restart_required"] is False
        assert data["message"] == "Server restart required to apply configuration changes"
        assert data["error_message"] == "Test error"
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = ReloadResult(
            config_reloaded=True,
            commands_discovered=0,
            custom_commands_preserved=0,
            total_commands=0,
            built_in_commands=0,
            custom_commands=0
        ).get_schema()
        
        assert schema["type"] == "object"
        assert "success" in schema["properties"]
        assert "config_reloaded" in schema["properties"]
        assert "commands_discovered" in schema["properties"]
        assert "custom_commands_preserved" in schema["properties"]
        assert "total_commands" in schema["properties"]
        assert "built_in_commands" in schema["properties"]
        assert "custom_commands" in schema["properties"]
        assert "server_restart_required" in schema["properties"]
        assert "message" in schema["properties"]
        assert "error_message" in schema["properties"]


class TestReloadCommandExtended:
    """Extended tests for ReloadCommand class."""
    
    def test_name_and_description(self):
        """Test command name and description."""
        assert ReloadCommand.name == "reload"
        # ReloadCommand doesn't have result_class attribute
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = ReloadCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "package_path" in schema["properties"]
        assert "force_restart" in schema["properties"]
        assert schema["additionalProperties"] is False
    
    @patch('mcp_proxy_adapter.commands.reload_command.registry')
    async def test_execute_reload_all_components(self, mock_registry):
        """Test reload command execution for all components."""
        mock_registry.reload_config_and_commands.return_value = {
            "config_reloaded": True,
            "commands_discovered": 3,
            "custom_commands_preserved": 1,
            "total_commands": 8,
            "built_in_commands": 7,
            "custom_commands": 1
        }
        
        command = ReloadCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadResult)
        assert result.success is True
        assert result.config_reloaded is True
        assert result.commands_discovered == 3
        assert result.custom_commands_preserved == 1
        assert result.total_commands == 8
        assert result.built_in_commands == 7
        assert result.custom_commands == 1
        assert result.server_restart_required is True
        # ReloadResult doesn't have message attribute directly, it's in to_dict()
        assert result.to_dict()["message"] == "Server restart required to apply configuration changes"
    
    @patch('mcp_proxy_adapter.commands.reload_command.registry')
    async def test_execute_reload_specific_components(self, mock_registry):
        """Test reload command execution for specific components."""
        mock_registry.reload_config_and_commands.return_value = {
            "config_reloaded": True,
            "commands_discovered": 2,
            "custom_commands_preserved": 0,
            "total_commands": 6,
            "built_in_commands": 6,
            "custom_commands": 0
        }
        
        command = ReloadCommand()
        result = await command.execute(components=["config", "commands"])
        
        assert isinstance(result, ReloadResult)
        assert result.success is True
        assert result.config_reloaded is True
        assert result.commands_discovered == 2
        assert result.total_commands == 6
    
    @patch('mcp_proxy_adapter.commands.reload_command.registry')
    async def test_execute_reload_commands_failure(self, mock_registry):
        """Test reload command execution failure."""
        mock_registry.reload_config_and_commands.side_effect = Exception("Reload failed")
        
        command = ReloadCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadResult)
        assert result.success is False
        assert result.config_reloaded is False
        assert result.commands_discovered == 0
        assert result.custom_commands_preserved == 0
        assert result.total_commands == 0
        assert result.built_in_commands == 0
        assert result.custom_commands == 0
        assert result.server_restart_required is False
        assert result.error_message == "Reload failed"
    
    @patch('mcp_proxy_adapter.commands.reload_command.registry')
    async def test_execute_reload_commands_exception(self, mock_registry):
        """Test reload command execution with exception."""
        mock_registry.reload_config_and_commands.side_effect = RuntimeError("Runtime error")
        
        command = ReloadCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadResult)
        assert result.success is False
        assert result.error_message == "Runtime error"
    
    @patch('mcp_proxy_adapter.commands.reload_command.registry')
    async def test_execute_invalid_components(self, mock_registry):
        """Test reload command with invalid components."""
        mock_registry.reload_config_and_commands.return_value = {
            "config_reloaded": True,
            "commands_discovered": 0,
            "custom_commands_preserved": 0,
            "total_commands": 6,
            "built_in_commands": 6,
            "custom_commands": 0
        }
        
        command = ReloadCommand()
        result = await command.execute(components=["invalid_component"])
        
        assert isinstance(result, ReloadResult)
        assert result.success is True  # Should still succeed as invalid components are ignored
    
    @patch('mcp_proxy_adapter.commands.reload_command.registry')
    async def test_execute_no_components_specified(self, mock_registry):
        """Test reload command with no components specified."""
        mock_registry.reload_config_and_commands.return_value = {
            "config_reloaded": True,
            "commands_discovered": 1,
            "custom_commands_preserved": 0,
            "total_commands": 6,
            "built_in_commands": 6,
            "custom_commands": 0
        }
        
        command = ReloadCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadResult)
        assert result.success is True
        assert result.config_reloaded is True
        assert result.commands_discovered == 1
    
    @patch('mcp_proxy_adapter.commands.reload_command.registry')
    async def test_execute_empty_components_list(self, mock_registry):
        """Test reload command with empty components list."""
        mock_registry.reload_config_and_commands.return_value = {
            "config_reloaded": True,
            "commands_discovered": 0,
            "custom_commands_preserved": 0,
            "total_commands": 6,
            "built_in_commands": 6,
            "custom_commands": 0
        }
        
        command = ReloadCommand()
        result = await command.execute(components=[])
        
        assert isinstance(result, ReloadResult)
        assert result.success is True
        assert result.config_reloaded is True


class TestReloadSettingsResultExtended:
    """Extended tests for ReloadSettingsResult class."""
    
    def test_init_with_all_parameters(self):
        """Test ReloadSettingsResult initialization with all parameters."""
        custom_settings = {"app": {"version": "1.0.0"}}
        
        result = ReloadSettingsResult(
            success=True,
            message="Settings reloaded successfully",
            custom_settings=custom_settings,
            error_message=None
        )
        
        assert result.success is True
        assert result.message == "Settings reloaded successfully"
        assert result.custom_settings == custom_settings
        assert result.error_message is None
    
    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        custom_settings = {"app": {"version": "1.0.0"}}
        
        result = ReloadSettingsResult(
            success=True,
            message="Settings reloaded successfully",
            custom_settings=custom_settings,
            error_message=None
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["message"] == "Settings reloaded successfully"
        assert data["custom_settings"] == custom_settings
        assert "error_message" not in data
    
    def test_to_dict_with_error(self):
        """Test to_dict method with error."""
        custom_settings = {"app": {"version": "1.0.0"}}
        
        result = ReloadSettingsResult(
            success=False,
            message="Failed to reload settings",
            custom_settings=custom_settings,
            error_message="Configuration file not found"
        )
        
        data = result.to_dict()
        assert data["success"] is False
        assert data["message"] == "Failed to reload settings"
        assert data["custom_settings"] == custom_settings
        assert data["error_message"] == "Configuration file not found"
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = ReloadSettingsResult(
            success=True,
            message="test",
            custom_settings={}
        ).get_schema()
        
        assert schema["type"] == "object"
        assert "success" in schema["properties"]
        assert "message" in schema["properties"]
        assert "custom_settings" in schema["properties"]
        assert "error_message" in schema["properties"]


class TestReloadSettingsCommandExtended:
    """Extended tests for ReloadSettingsCommand class."""
    
    def test_name_and_description(self):
        """Test command name and description."""
        assert ReloadSettingsCommand.name == "reload_settings"
        assert ReloadSettingsCommand.description == "Reload configuration settings from files and environment variables"
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = ReloadSettingsCommand.get_schema()
        
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert "description" in schema
    
    @patch('mcp_proxy_adapter.commands.reload_settings_command.reload_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_custom_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_logger')
    async def test_execute_reload_settings_success(self, mock_get_logger, mock_get_custom_settings, mock_reload_settings):
        """Test reload settings command execution success."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_custom_settings.return_value = {
            "app": {"version": "1.0.0"},
            "database": {"host": "localhost"}
        }
        
        command = ReloadSettingsCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadSettingsResult)
        assert result.success is True
        assert result.message == "Settings reloaded successfully from configuration files and environment variables"
        assert result.custom_settings == {
            "app": {"version": "1.0.0"},
            "database": {"host": "localhost"}
        }
        assert result.error_message is None
        
        mock_reload_settings.assert_called_once()
        mock_get_custom_settings.assert_called_once()
    
    @patch('mcp_proxy_adapter.commands.reload_settings_command.reload_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_custom_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_logger')
    async def test_execute_reload_settings_failure(self, mock_get_logger, mock_get_custom_settings, mock_reload_settings):
        """Test reload settings command execution failure."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_reload_settings.side_effect = Exception("Configuration file not found")
        mock_get_custom_settings.return_value = {}
        
        command = ReloadSettingsCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadSettingsResult)
        assert result.success is False
        assert result.message == "Failed to reload settings"
        assert result.custom_settings == {}
        assert result.error_message == "Failed to reload settings: Configuration file not found"
    
    @patch('mcp_proxy_adapter.commands.reload_settings_command.reload_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_custom_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_logger')
    async def test_execute_reload_settings_exception(self, mock_get_logger, mock_get_custom_settings, mock_reload_settings):
        """Test reload settings command execution with exception."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_reload_settings.side_effect = RuntimeError("Runtime error")
        mock_get_custom_settings.return_value = {"app": {"version": "1.0.0"}}
        
        command = ReloadSettingsCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadSettingsResult)
        assert result.success is False
        assert result.message == "Failed to reload settings"
        assert result.custom_settings == {"app": {"version": "1.0.0"}}
        assert result.error_message == "Failed to reload settings: Runtime error"
    
    @patch('mcp_proxy_adapter.commands.reload_settings_command.reload_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_custom_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_logger')
    async def test_execute_reload_settings_default_path(self, mock_get_logger, mock_get_custom_settings, mock_reload_settings):
        """Test reload settings command with default path."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_custom_settings.return_value = {}
        
        command = ReloadSettingsCommand()
        result = await command.execute()
        
        assert isinstance(result, ReloadSettingsResult)
        assert result.success is True
        assert result.custom_settings == {}
    
    @patch('mcp_proxy_adapter.commands.reload_settings_command.reload_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_custom_settings')
    @patch('mcp_proxy_adapter.commands.reload_settings_command.get_logger')
    async def test_execute_reload_settings_with_additional_kwargs(self, mock_get_logger, mock_get_custom_settings, mock_reload_settings):
        """Test reload settings command with additional kwargs."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_custom_settings.return_value = {"test": "value"}
        
        command = ReloadSettingsCommand()
        result = await command.execute(force=True, clear_cache=True)
        
        assert isinstance(result, ReloadSettingsResult)
        assert result.success is True
        assert result.custom_settings == {"test": "value"} 