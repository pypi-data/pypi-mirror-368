"""
Reload command for configuration and command discovery.

This command allows reloading configuration and rediscovering commands
without restarting the server.
"""

from typing import Any, Dict, Optional

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.logging import logger


class ReloadResult:
    """
    Result of reload operation.
    """
    
    def __init__(
        self,
        config_reloaded: bool,
        commands_discovered: int,
        custom_commands_preserved: int,
        total_commands: int,
        built_in_commands: int,
        custom_commands: int,
        server_restart_required: bool = True,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Initialize reload result.
        
        Args:
            config_reloaded: Whether configuration was reloaded successfully
            commands_discovered: Number of commands discovered
            custom_commands_preserved: Number of custom commands preserved
            total_commands: Total number of commands after reload
            built_in_commands: Number of built-in commands
            custom_commands: Number of custom commands
            server_restart_required: Whether server restart is required
            success: Whether reload was successful
            error_message: Error message if reload failed
        """
        self.config_reloaded = config_reloaded
        self.commands_discovered = commands_discovered
        self.custom_commands_preserved = custom_commands_preserved
        self.total_commands = total_commands
        self.built_in_commands = built_in_commands
        self.custom_commands = custom_commands
        self.server_restart_required = server_restart_required
        self.success = success
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dictionary representation of the result.
        """
        return {
            "success": self.success,
            "config_reloaded": self.config_reloaded,
            "commands_discovered": self.commands_discovered,
            "custom_commands_preserved": self.custom_commands_preserved,
            "total_commands": self.total_commands,
            "built_in_commands": self.built_in_commands,
            "custom_commands": self.custom_commands,
            "server_restart_required": self.server_restart_required,
            "message": "Server restart required to apply configuration changes",
            "error_message": self.error_message
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for the result.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether reload was successful"
                },
                "config_reloaded": {
                    "type": "boolean",
                    "description": "Whether configuration was reloaded successfully"
                },
                "commands_discovered": {
                    "type": "integer",
                    "description": "Number of commands discovered"
                },
                "custom_commands_preserved": {
                    "type": "integer",
                    "description": "Number of custom commands preserved"
                },
                "total_commands": {
                    "type": "integer",
                    "description": "Total number of commands after reload"
                },
                "built_in_commands": {
                    "type": "integer",
                    "description": "Number of built-in commands"
                },
                "custom_commands": {
                    "type": "integer",
                    "description": "Number of custom commands"
                },
                "server_restart_required": {
                    "type": "boolean",
                    "description": "Whether server restart is required to apply changes"
                },
                "message": {
                    "type": "string",
                    "description": "Information message about the reload operation"
                },
                "error_message": {
                    "type": ["string", "null"],
                    "description": "Error message if reload failed"
                }
            },
            "required": [
                "success", "config_reloaded", "commands_discovered",
                "custom_commands_preserved", "total_commands",
                "built_in_commands", "custom_commands", "server_restart_required"
            ]
        }


class ReloadCommand(Command):
    """
    Command for reloading configuration and rediscovering commands.
    Note: This command will trigger a server restart to apply configuration changes.
    """
    
    name = "reload"
    
    async def execute(self, **params) -> ReloadResult:
        """
        Execute reload command.
        
        Args:
            **params: Command parameters (currently unused)
            
        Returns:
            ReloadResult with reload information
        """
        try:
            logger.info("🔄 Starting configuration and commands reload...")
            
            # Perform reload
            reload_info = registry.reload_config_and_commands()
            
            # Create result
            result = ReloadResult(
                config_reloaded=reload_info.get("config_reloaded", False),
                commands_discovered=reload_info.get("commands_discovered", 0),
                custom_commands_preserved=reload_info.get("custom_commands_preserved", 0),
                total_commands=reload_info.get("total_commands", 0),
                built_in_commands=reload_info.get("built_in_commands", 0),
                custom_commands=reload_info.get("custom_commands", 0),
                server_restart_required=True,
                success=True
            )
            
            logger.info(f"✅ Reload completed successfully: {result.to_dict()}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Reload failed: {str(e)}")
            return ReloadResult(
                config_reloaded=False,
                commands_discovered=0,
                custom_commands_preserved=0,
                total_commands=0,
                built_in_commands=0,
                custom_commands=0,
                server_restart_required=False,
                success=False,
                error_message=str(e)
            )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "package_path": {
                    "type": "string",
                    "description": "Path to package with commands to discover",
                    "default": "mcp_proxy_adapter.commands"
                },
                "force_restart": {
                    "type": "boolean",
                    "description": "Force server restart to apply configuration changes",
                    "default": True
                }
            },
            "additionalProperties": False
        } 