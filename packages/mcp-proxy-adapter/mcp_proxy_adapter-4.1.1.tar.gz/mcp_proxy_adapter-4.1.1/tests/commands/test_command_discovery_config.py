"""
Tests for command discovery with configuration.
"""

import pytest
from unittest.mock import patch, MagicMock
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult


class TestCommand(Command):
    """Test command for testing discovery."""
    
    name = "test"
    
    def execute(self) -> CommandResult:
        return CommandResult(success=True, data={"test": "ok"})
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {}


class TestCommandDiscoveryConfig:
    """Test command discovery with configuration."""
    
    def test_discover_commands_uses_config_when_no_path_provided(self):
        """Test that discover_commands uses config when no path is provided."""
        registry = CommandRegistry()
        
        # Mock config to return custom path
        mock_config = MagicMock()
        mock_config.get.return_value = "custom.commands"
        
        with patch('mcp_proxy_adapter.config.config', mock_config):
            with patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module') as mock_import:
                # Mock successful module import
                mock_module = MagicMock()
                mock_module.__file__ = "/path/to/custom/commands/__init__.py"
                mock_import.return_value = mock_module
                
                # Mock pkgutil to return no modules
                with patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules') as mock_iter:
                    mock_iter.return_value = []
                    
                    # Call discover_commands without path
                    result = registry.discover_commands()
                    
                    # Verify config was called with correct key
                    mock_config.get.assert_called_once_with("commands.discovery_path", "mcp_proxy_adapter.commands")
                    
                    # Verify import was called with custom path
                    mock_import.assert_any_call("custom.commands")
    
    def test_discover_commands_falls_back_to_default_on_config_error(self):
        """Test that discover_commands falls back to default when config fails."""
        registry = CommandRegistry()
        
        # Mock config to raise exception
        with patch('mcp_proxy_adapter.config.config') as mock_config:
            mock_config.get.side_effect = Exception("Config error")
            
            with patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module') as mock_import:
                # Mock successful module import
                mock_module = MagicMock()
                mock_module.__file__ = "/path/to/default/commands/__init__.py"
                mock_import.return_value = mock_module
                
                # Mock pkgutil to return no modules
                with patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules') as mock_iter:
                    mock_iter.return_value = []
                    
                    # Call discover_commands without path
                    result = registry.discover_commands()
                    
                    # Verify import was called with default path
                    mock_import.assert_any_call("mcp_proxy_adapter.commands")
    
    def test_discover_commands_uses_provided_path_over_config(self):
        """Test that discover_commands uses provided path over config."""
        registry = CommandRegistry()
        
        # Mock config to return custom path
        mock_config = MagicMock()
        mock_config.get.return_value = "custom.commands"
        
        with patch('mcp_proxy_adapter.config.config', mock_config):
            with patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module') as mock_import:
                # Mock successful module import
                mock_module = MagicMock()
                mock_module.__file__ = "/path/to/provided/commands/__init__.py"
                mock_import.return_value = mock_module
                
                # Mock pkgutil to return no modules
                with patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules') as mock_iter:
                    mock_iter.return_value = []
                    
                    # Call discover_commands with explicit path
                    result = registry.discover_commands("provided.commands")
                    
                    # Verify config was NOT called
                    mock_config.get.assert_not_called()
                    
                    # Verify import was called with provided path
                    mock_import.assert_any_call("provided.commands")
    
    def test_reload_config_and_commands_uses_config(self):
        """Test that reload_config_and_commands uses config for discovery."""
        registry = CommandRegistry()
        
        # Mock config to return custom path
        mock_config = MagicMock()
        mock_config.get.return_value = "custom.commands"
        
        with patch('mcp_proxy_adapter.config.config', mock_config):
            with patch('mcp_proxy_adapter.commands.command_registry.importlib.import_module') as mock_import:
                # Mock successful module import
                mock_module = MagicMock()
                mock_module.__file__ = "/path/to/custom/commands/__init__.py"
                mock_import.return_value = mock_module
                
                # Mock pkgutil to return no modules
                with patch('mcp_proxy_adapter.commands.command_registry.pkgutil.iter_modules') as mock_iter:
                    mock_iter.return_value = []
                    
                    # Mock config reload
                    with patch('mcp_proxy_adapter.config.config.load_config'):
                        with patch('mcp_proxy_adapter.core.logging.setup_logging'):
                            # Call reload_config_and_commands without path
                            result = registry.reload_config_and_commands()
                            
                            # Verify config was called with correct key
                            mock_config.get.assert_called_with("commands.discovery_path", "mcp_proxy_adapter.commands")
                            
                            # Verify import was called with custom path
                            mock_import.assert_any_call("custom.commands") 