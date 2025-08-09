"""
Tests for custom commands server example.

This module tests the custom commands server functionality including:
- Command registration
- Hook setup
- Main function execution
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestRegisterCustomCommands:
    """Test register_custom_commands function."""

    @patch('mcp_proxy_adapter.examples.custom_commands.server.registry')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    def test_register_custom_commands_all_enabled(self, mock_get_logger, mock_get_setting, mock_registry):
        """Test register_custom_commands with all commands enabled."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock custom settings to enable all commands
        mock_get_setting.return_value = {
            "help": {"enabled": True},
            "health": {"enabled": True},
            "data_transform": {"enabled": True},
            "intercept": {"enabled": True},
            "manual_echo": {"enabled": True}
        }
        
        mock_registry.get_all_commands.return_value = ["cmd1", "cmd2", "cmd3"]
        
        from mcp_proxy_adapter.examples.custom_commands.server import register_custom_commands
        
        register_custom_commands()
        
        # Verify all commands are registered
        assert mock_registry.register_custom_command.call_count == 2  # help and health
        assert mock_registry.register.call_count == 3  # data_transform, intercept, manual_echo
        assert mock_logger.info.call_count >= 6  # Multiple log messages

    @patch('mcp_proxy_adapter.examples.custom_commands.server.registry')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    def test_register_custom_commands_all_disabled(self, mock_get_logger, mock_get_setting, mock_registry):
        """Test register_custom_commands with all commands disabled."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock custom settings to disable all commands
        mock_get_setting.return_value = {
            "help": {"enabled": False},
            "health": {"enabled": False},
            "data_transform": {"enabled": False},
            "intercept": {"enabled": False},
            "manual_echo": {"enabled": False}
        }
        
        mock_registry.get_all_commands.return_value = ["cmd1"]
        
        from mcp_proxy_adapter.examples.custom_commands.server import register_custom_commands
        
        register_custom_commands()
        
        # Verify no commands are registered
        assert mock_registry.register_custom_command.call_count == 0
        assert mock_registry.register.call_count == 0
        assert mock_logger.info.call_count >= 2  # At least echo and total commands logs


class TestSetupHooks:
    """Test setup_hooks function."""

    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    def test_setup_hooks_all_enabled(self, mock_get_logger, mock_get_setting):
        """Test setup_hooks with all hooks enabled."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock hooks configuration to enable all hooks
        mock_get_setting.return_value = {
            "data_transform": {"enabled": True},
            "intercept": {"enabled": True}
        }
        
        from mcp_proxy_adapter.examples.custom_commands.server import setup_hooks
        
        setup_hooks()
        
        # Verify all log messages are called
        assert mock_logger.info.call_count >= 8  # Multiple log messages

    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    def test_setup_hooks_all_disabled(self, mock_get_logger, mock_get_setting):
        """Test setup_hooks with all hooks disabled."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock hooks configuration to disable all hooks
        mock_get_setting.return_value = {
            "data_transform": {"enabled": False},
            "intercept": {"enabled": False}
        }
        
        from mcp_proxy_adapter.examples.custom_commands.server import setup_hooks
        
        setup_hooks()
        
        # Verify log messages are still called
        assert mock_logger.info.call_count >= 6  # Multiple log messages


class TestMainFunction:
    """Test main function."""

    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.register_custom_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('builtins.print')
    def test_main_with_config_file(self, mock_print, mock_exists, mock_config, mock_settings, 
                                  mock_custom_settings_manager, mock_setup_logging, mock_get_logger,
                                  mock_register_commands, mock_setup_hooks, mock_create_app, mock_uvicorn_run):
        """Test main function with config file."""
        mock_exists.return_value = True
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            'host': 'localhost',
            'port': 8000,
            'debug': True,
            'log_level': 'INFO'
        }
        mock_settings.get_logging_settings.return_value = {
            'level': 'INFO',
            'log_dir': '/logs'
        }
        mock_settings.get_commands_settings.return_value = {
            'auto_discovery': True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock custom settings manager
        mock_custom_settings_manager_instance = MagicMock()
        mock_custom_settings_manager.return_value = mock_custom_settings_manager_instance
        
        # Mock app
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        main()
        
        # Verify all functions are called
        mock_config.load_from_file.assert_called_once()
        mock_setup_logging.assert_called_once()
        mock_custom_settings_manager.assert_called_once_with("custom_settings.json")
        mock_custom_settings_manager_instance.print_settings_summary.assert_called_once()
        mock_register_commands.assert_called_once()
        mock_setup_hooks.assert_called_once()
        mock_create_app.assert_called_once()
        mock_uvicorn_run.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.register_custom_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('builtins.print')
    def test_main_without_config_file(self, mock_print, mock_exists, mock_config, mock_settings,
                                     mock_custom_settings_manager, mock_setup_logging, mock_get_logger,
                                     mock_register_commands, mock_setup_hooks, mock_create_app, mock_uvicorn_run):
        """Test main function without config file."""
        mock_exists.return_value = False
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            'host': 'localhost',
            'port': 8000,
            'debug': True,
            'log_level': 'INFO'
        }
        mock_settings.get_logging_settings.return_value = {
            'level': 'INFO',
            'log_dir': '/logs'
        }
        mock_settings.get_commands_settings.return_value = {
            'auto_discovery': True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock custom settings manager
        mock_custom_settings_manager_instance = MagicMock()
        mock_custom_settings_manager.return_value = mock_custom_settings_manager_instance
        
        # Mock app
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        main()
        
        # Verify config.load_from_file is not called
        mock_config.load_from_file.assert_not_called()
        # Verify other functions are still called
        mock_setup_logging.assert_called_once()
        mock_custom_settings_manager.assert_called_once_with("custom_settings.json")
        mock_register_commands.assert_called_once()
        mock_setup_hooks.assert_called_once()
        mock_create_app.assert_called_once()
        mock_uvicorn_run.assert_called_once()


class TestServerImports:
    """Test server imports and module structure."""

    def test_server_module_imports(self):
        """Test that server module can be imported."""
        try:
            from mcp_proxy_adapter.examples.custom_commands import server
            assert server is not None
        except ImportError as e:
            pytest.fail(f"Failed to import server module: {e}")

    def test_server_functions_exist(self):
        """Test that server functions exist."""
        from mcp_proxy_adapter.examples.custom_commands import server
        
        assert hasattr(server, 'register_custom_commands')
        assert hasattr(server, 'setup_hooks')
        assert hasattr(server, 'main')
        assert callable(server.register_custom_commands)
        assert callable(server.setup_hooks)
        assert callable(server.main) 