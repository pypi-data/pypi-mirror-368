"""
Basic Server Example

This example demonstrates a minimal MCP Proxy Adapter server
without any additional custom commands.
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
    get_setting
)


def main():
    """Run the basic server example."""
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
    logger = get_logger("basic_server")
    
    # Get settings from configuration
    server_settings = Settings.get_server_settings()
    logging_settings = Settings.get_logging_settings()
    commands_settings = Settings.get_commands_settings()
    custom_settings = Settings.get_custom_setting("custom", {})
    
    # Print server header and description
    print("=" * 80)
    print("🔧 BASIC MCP PROXY ADAPTER SERVER")
    print("=" * 80)
    print("📋 Description:")
    print(f"   {custom_settings.get('description', 'Basic server example')}")
    print()
    print("⚙️  Configuration:")
    print(f"   • Server: {server_settings['host']}:{server_settings['port']}")
    print(f"   • Debug: {server_settings['debug']}")
    print(f"   • Log Level: {logging_settings['level']}")
    print(f"   • Log Directory: {logging_settings['log_dir']}")
    print(f"   • Auto Discovery: {commands_settings['auto_discovery']}")
    print()
    print("🔧 Available Commands:")
    print("   • help - Built-in help command")
    print("   • health - Built-in health command")
    print("   • config - Built-in config command")
    print("   • reload - Built-in reload command")
    print()
    print("🎯 Features:")
    print("   • Standard JSON-RPC API")
    print("   • Built-in command discovery")
    print("   • Basic logging and error handling")
    print("   • OpenAPI schema generation")
    print("   • Configuration-driven settings")
    print("=" * 80)
    print()
    
    logger.info("Starting Basic MCP Proxy Adapter Server...")
    logger.info(f"Server configuration: {server_settings}")
    logger.info(f"Logging configuration: {logging_settings}")
    logger.info(f"Commands configuration: {commands_settings}")
    
    # Create application with settings from configuration
    app = create_app(
        title=custom_settings.get('server_name', 'Basic MCP Proxy Adapter Server'),
        description=custom_settings.get('description', 'Minimal server example with only built-in commands'),
        version="1.0.0"
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