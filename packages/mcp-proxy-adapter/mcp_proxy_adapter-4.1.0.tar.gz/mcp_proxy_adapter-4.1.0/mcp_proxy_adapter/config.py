"""
Module for microservice configuration management.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """
    Configuration management class for the microservice.
    Allows loading settings from configuration file and environment variables.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file. If not specified, "./config.json" is used.
        """
        self.config_path = config_path or "./config.json"
        self.config_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Load configuration from file and environment variables.
        """
        # Set default config values
        self.config_data = {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False,
                "log_level": "INFO"
            },
            "logging": {
                "level": "INFO",
                "file": None,
                "log_dir": "./logs",
                "log_file": "mcp_proxy_adapter.log",
                "error_log_file": "mcp_proxy_adapter_error.log",
                "access_log_file": "mcp_proxy_adapter_access.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "console_output": True,
                "file_output": True
            },
            "commands": {
                "auto_discovery": True,
                "discovery_path": "mcp_proxy_adapter.commands",
                "custom_commands_path": None
            }
        }
        
        # Try to load configuration from file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._update_nested_dict(self.config_data, file_config)
            except Exception as e:
                print(f"Error loading config from {self.config_path}: {e}")
        
        # Load configuration from environment variables
        self._load_env_variables()

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from the specified file.

        Args:
            config_path: Path to configuration file.
        """
        self.config_path = config_path
        self.load_config()

    def _load_env_variables(self) -> None:
        """
        Load configuration from environment variables.
        Environment variables should be in format SERVICE_SECTION_KEY=value.
        For example, SERVICE_SERVER_PORT=8080.
        """
        prefix = "SERVICE_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                parts = key[len(prefix):].lower().split("_", 1)
                if len(parts) == 2:
                    section, param = parts
                    if section not in self.config_data:
                        self.config_data[section] = {}
                    self.config_data[section][param] = self._convert_env_value(value)

    def _convert_env_value(self, value: str) -> Any:
        """
        Convert environment variable value to appropriate type.

        Args:
            value: Value as string

        Returns:
            Converted value
        """
        # Try to convert to appropriate type
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit():
            return int(value)
        else:
            try:
                return float(value)
            except ValueError:
                return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value for key.

        Args:
            key: Configuration key in format "section.param"
            default: Default value if key not found

        Returns:
            Configuration value
        """
        parts = key.split(".")
        
        # Get value from config
        value = self.config_data
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
            
        return value

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary with all configuration values
        """
        return self.config_data.copy()

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value for key.

        Args:
            key: Configuration key in format "section.param"
            value: Configuration value
        """
        parts = key.split(".")
        if len(parts) == 1:
            self.config_data[key] = value
        else:
            section = parts[0]
            param = ".".join(parts[1:])
            
            if section not in self.config_data:
                self.config_data[section] = {}
                
            current = self.config_data[section]
            for part in parts[1:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
                
            current[parts[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file.

        Args:
            path: Path to configuration file. If not specified, self.config_path is used.
        """
        save_path = path or self.config_path
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=2)

    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """
        Update nested dictionary recursively.

        Args:
            d: Dictionary to update
            u: Dictionary with new values

        Returns:
            Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d


# Singleton instance
config = Config()
