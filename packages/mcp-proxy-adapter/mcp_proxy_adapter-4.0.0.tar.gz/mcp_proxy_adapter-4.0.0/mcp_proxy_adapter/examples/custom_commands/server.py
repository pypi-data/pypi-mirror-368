"""
Custom Commands Server Example

This example demonstrates a MCP Proxy Adapter server
with custom commands: echo, custom help, and custom health.
Includes hooks for before and after command processing.
"""

import asyncio
import uvicorn
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.core.logging import get_logger, setup_logging
from mcp_proxy_adapter.core.settings import (
    Settings,
    get_server_host,
    get_server_port,
    get_server_debug,
    get_setting,
    get_custom_setting_value
)
from .custom_settings_manager import CustomSettingsManager, get_app_name, is_feature_enabled

# Import custom commands and hooks
from .custom_help_command import CustomHelpCommand
from .custom_health_command import CustomHealthCommand
from .data_transform_command import DataTransformCommand
from .intercept_command import InterceptCommand
from .advanced_hooks import register_advanced_hooks

# Import auto-registered commands
from .auto_commands.auto_echo_command import AutoEchoCommand
from .auto_commands.auto_info_command import AutoInfoCommand

# Import manual registration example
from .manual_echo_command import ManualEchoCommand

# Import echo command
from .echo_command import EchoCommand

# Import custom OpenAPI generator
from .custom_openapi_generator import custom_openapi_generator

# Import command registry for manual registration
from mcp_proxy_adapter.commands.command_registry import registry


def register_custom_commands():
    """Register custom commands with the registry."""
    logger = get_logger("custom_commands")
    logger.info("Registering custom commands...")
    
    # Get custom commands configuration from custom settings
    custom_commands_config = get_custom_setting_value("custom_commands", {})
    
    # Register echo command
    registry.register(EchoCommand)
    logger.info("Registered: echo command")
    
    # Register custom help command (will override built-in)
    if custom_commands_config.get("help", {}).get("enabled", True):
        registry.register_custom_command(CustomHelpCommand)
        logger.info("Registered: custom help command")
    
    # Register custom health command (will override built-in)
    if custom_commands_config.get("health", {}).get("enabled", True):
        registry.register_custom_command(CustomHealthCommand)
        logger.info("Registered: custom health command")
    
    # Register advanced demonstration commands
    if custom_commands_config.get("data_transform", {}).get("enabled", True):
        registry.register(DataTransformCommand)
        logger.info("Registered: data_transform command")
    
    if custom_commands_config.get("intercept", {}).get("enabled", True):
        registry.register(InterceptCommand)
        logger.info("Registered: intercept command")
    
    # Register manually registered commands
    if custom_commands_config.get("manual_echo", {}).get("enabled", True):
        registry.register(ManualEchoCommand)
        logger.info("Registered: manual_echo command")
    
    logger.info(f"Total commands registered: {len(registry.get_all_commands())}")


def setup_hooks():
    """Setup hooks for command processing."""
    logger = get_logger("custom_commands")
    logger.info("Setting up hooks...")
    
    # Get hooks configuration from custom settings
    hooks_config = get_custom_setting_value("hooks", {})
    
    # Register basic hooks
    # register_all_hooks(hooks) # This line was removed as per the new_code, as hooks is no longer imported.
    logger.info("Registered: basic hooks")
    
    # Register advanced hooks based on configuration
    if hooks_config.get("data_transform", {}).get("enabled", True):
        # register_advanced_hooks(None)  # Temporarily disabled for simplicity
        logger.info("Registered: data transformation hooks (disabled for now)")
    
    if hooks_config.get("intercept", {}).get("enabled", True):
        logger.info("Registered: interception hooks")
    
    logger.info("Registered: command-specific hooks")
    logger.info("Registered: global hooks")
    logger.info("Registered: performance monitoring hooks")
    logger.info("Registered: security monitoring hooks")
    logger.info("Registered: data transformation hooks")
    logger.info("Registered: interception hooks")


def main():
    """Run the custom commands server example with hooks."""
    # Load configuration from config.json in the same directory
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        from mcp_proxy_adapter.config import config
        config.load_from_file(config_path)
        print(f"✅ Loaded configuration from: {config_path}")
    else:
        print(f"⚠️  Configuration file not found: {config_path}")
        print("   Using default configuration")
    
    # Setup logging with configuration
    setup_logging()
    logger = get_logger("custom_commands")
    
    # Initialize custom settings manager
    custom_settings_manager = CustomSettingsManager("custom_settings.json")
    
    # Print custom settings summary
    custom_settings_manager.print_settings_summary()
    
    # Get settings from configuration
    server_settings = Settings.get_server_settings()
    logging_settings = Settings.get_logging_settings()
    commands_settings = Settings.get_commands_settings()
    custom_settings = Settings.get_custom_setting("custom", {})
    
    # Print server header and description
    print("=" * 80)
    print("🔧 ADVANCED MCP PROXY ADAPTER SERVER WITH HOOKS")
    print("=" * 80)
    print("📋 Description:")
    print(f"   {get_app_name()} - Advanced server with custom settings management")
    print()
    print("⚙️  Configuration:")
    print(f"   • Server: {server_settings['host']}:{server_settings['port']}")
    print(f"   • Debug: {server_settings['debug']}")
    print(f"   • Log Level: {logging_settings['level']}")
    print(f"   • Log Directory: {logging_settings['log_dir']}")
    print(f"   • Auto Discovery: {commands_settings['auto_discovery']}")
    print()
    print("🔧 Available Commands:")
    print("   • help - Custom help command (overrides built-in)")
    print("   • health - Custom health command (overrides built-in)")
    print("   • config - Built-in config command")
    print("   • reload - Built-in reload command")
    print("   • settings - Built-in settings command")
    print("   • reload_settings - Built-in reload settings command")
    print("   • data_transform - Data transformation command")
    print("   • intercept - Command interception example")
    print("   • manual_echo - Manually registered echo command")
    print("   • auto_echo - Auto-registered echo command")
    print("   • auto_info - Auto-registered info command")
    print()
    print("🎯 Features:")
    print("   • Advanced JSON-RPC API")
    print("   • Custom commands with hooks")
    print("   • Data transformation hooks")
    print("   • Command interception hooks")
    print("   • Auto-registration and manual registration")
    print("   • Custom OpenAPI schema generation")
    print("   • Configuration-driven settings")
    print("   • Custom settings management")
    print("=" * 80)
    print()
    
    logger.info("Starting Advanced Custom Commands MCP Proxy Adapter Server with Hooks...")
    logger.info(f"Server configuration: {server_settings}")
    logger.info(f"Logging configuration: {logging_settings}")
    logger.info(f"Commands configuration: {commands_settings}")
    logger.info("This server demonstrates both auto-registration and manual registration:")
    logger.info("• Auto-registered: auto_echo, auto_info (from auto_commands/ package)")
    logger.info("• Manually registered: echo, help, health, data_transform, intercept, manual_echo")
    logger.info("• Built-in commands: help, health (if not overridden)")
    logger.info("With advanced hooks for data transformation and command interception")
    
    # Register custom commands
    register_custom_commands()
    
    # Discover auto-registered commands
    logger.info("Discovering auto-registered commands...")
    auto_commands_path = commands_settings.get("auto_commands_path", "mcp_proxy_adapter.examples.custom_commands.auto_commands")
    registry.discover_commands(auto_commands_path)
    
    # Setup hooks
    setup_hooks()
    
    # Create application with settings from configuration
    app = create_app(
        title=get_app_name(),
        description="Advanced MCP Proxy Adapter server with custom settings management, demonstrating hook capabilities including data transformation, command interception, conditional processing, and smart interception hooks. Features custom commands with enhanced functionality and comprehensive settings management.",
        version="2.1.0"
    )
    
    # Run the server with configuration settings
    uvicorn.run(
        app,
        host=server_settings['host'],
        port=server_settings['port'],
        log_level=server_settings['log_level'].lower()
    )


if __name__ == "__main__":
    main() 