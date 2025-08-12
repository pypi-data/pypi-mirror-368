"""
Reload Settings Command

This command allows reloading configuration settings from files and environment variables.
"""

from typing import Dict, Any
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.core.settings import reload_settings, get_custom_settings
from mcp_proxy_adapter.core.logging import get_logger


class ReloadSettingsResult:
    """
    Result class for reload settings command.
    """
    
    def __init__(
        self,
        success: bool,
        message: str,
        custom_settings: Dict[str, Any] = None,
        error_message: str = None
    ):
        self.success = success
        self.message = message
        self.custom_settings = custom_settings or {}
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
            "custom_settings": self.custom_settings
        }
        if self.error_message:
            result["error_message"] = self.error_message
        return result
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for the result."""
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the operation was successful"
                },
                "message": {
                    "type": "string",
                    "description": "Operation result message"
                },
                "custom_settings": {
                    "type": "object",
                    "description": "Current custom settings after reload",
                    "additionalProperties": True
                },
                "error_message": {
                    "type": "string",
                    "description": "Error message if operation failed"
                }
            },
            "required": ["success", "message", "custom_settings"]
        }


class ReloadSettingsCommand(Command):
    """
    Command to reload configuration settings.
    """
    
    name = "reload_settings"
    description = "Reload configuration settings from files and environment variables"
    
    async def execute(self, **params) -> ReloadSettingsResult:
        """
        Execute the reload settings command.
        
        Args:
            **params: Command parameters (not used)
            
        Returns:
            ReloadSettingsResult with operation status
        """
        logger = get_logger("reload_settings_command")
        
        try:
            logger.info("🔄 Starting settings reload...")
            
            # Reload configuration from files and environment variables
            reload_settings()
            
            # Get current custom settings
            custom_settings = get_custom_settings()
            
            logger.info("✅ Settings reloaded successfully")
            logger.info(f"📋 Current custom settings: {custom_settings}")
            
            return ReloadSettingsResult(
                success=True,
                message="Settings reloaded successfully from configuration files and environment variables",
                custom_settings=custom_settings
            )
            
        except Exception as e:
            error_msg = f"Failed to reload settings: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            return ReloadSettingsResult(
                success=False,
                message="Failed to reload settings",
                custom_settings=get_custom_settings(),
                error_message=error_msg
            )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for the command parameters."""
        return {
            "type": "object",
            "description": "Reload configuration settings from files and environment variables",
            "properties": {},
            "additionalProperties": False
        } 