"""
Unit tests for configuration module.
"""

import json
import os
import tempfile
from typing import Generator

import pytest

from mcp_proxy_adapter.config import Config


@pytest.fixture
def temp_config_file() -> Generator[str, None, None]:
    """
    Creates temporary configuration file for tests.
    
    Returns:
        Path to temporary configuration file.
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=".json")
    
    # Write test configuration
    test_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 8000
        },
        "logging": {
            "level": "DEBUG",
            "file": "test.log"
        },
        "test_section": {
            "test_key": "test_value",
            "nested": {
                "key1": "value1",
                "key2": 42
            }
        }
    }
    
    with os.fdopen(fd, "w") as f:
        json.dump(test_config, f)
    
    yield path
    
    # Remove temporary file after tests
    os.unlink(path)


@pytest.mark.unit
def test_config_load_from_file(temp_config_file: str):
    """
    Test loading configuration from file.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    config = Config(temp_config_file)
    
    # Check loaded values
    assert config.get("server.host") == "127.0.0.1"
    assert config.get("server.port") == 8000
    assert config.get("logging.level") == "DEBUG"
    assert config.get("logging.file") == "test.log"
    assert config.get("test_section.test_key") == "test_value"


@pytest.mark.unit
def test_config_get_nested_values(temp_config_file: str):
    """
    Test getting nested values from configuration.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    config = Config(temp_config_file)
    
    # Get nested values
    assert config.get("test_section.nested.key1") == "value1"
    assert config.get("test_section.nested.key2") == 42


@pytest.mark.unit
def test_config_get_with_default(temp_config_file: str):
    """
    Test getting configuration values with default.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    config = Config(temp_config_file)
    
    # Get non-existent values with defaults
    assert config.get("non_existent", default="default") == "default"
    assert config.get("server.non_existent", default=123) == 123
    assert config.get("test_section.nested.non_existent", default=False) is False


@pytest.mark.unit
def test_config_get_without_default(temp_config_file: str):
    """
    Test getting non-existent configuration values without default.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    config = Config(temp_config_file)
    
    # Get non-existent values without defaults
    assert config.get("non_existent") is None
    assert config.get("server.non_existent") is None
    assert config.get("test_section.nested.non_existent") is None


@pytest.mark.unit
def test_config_set_value(temp_config_file: str):
    """
    Test setting configuration values.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    config = Config(temp_config_file)
    
    # Set values
    config.set("server.host", "localhost")
    config.set("logging.level", "INFO")
    config.set("new_section.new_key", "new_value")
    
    # Check set values
    assert config.get("server.host") == "localhost"
    assert config.get("logging.level") == "INFO"
    assert config.get("new_section.new_key") == "new_value"


@pytest.mark.unit
def test_config_save_and_load(temp_config_file: str):
    """
    Test saving and loading configuration.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    # Create and modify configuration
    config1 = Config(temp_config_file)
    config1.set("server.host", "localhost")
    config1.set("new_section.new_key", "new_value")
    
    # Save configuration
    config1.save()
    
    # Load configuration again
    config2 = Config(temp_config_file)
    
    # Check values
    assert config2.get("server.host") == "localhost"
    assert config2.get("new_section.new_key") == "new_value"


@pytest.mark.unit
def test_config_load_updated_file(temp_config_file: str):
    """
    Test loading updated configuration from file.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    # Load configuration
    config = Config(temp_config_file)
    original_host = config.get("server.host")
    
    # Modify file directly
    with open(temp_config_file, "r+") as f:
        data = json.load(f)
        data["server"]["host"] = "new_host"
        f.seek(0)
        f.truncate()
        json.dump(data, f)
    
    # Create new config instance to load updated file
    updated_config = Config(temp_config_file)
    
    # Check that value was updated
    assert updated_config.get("server.host") == "new_host"
    assert updated_config.get("server.host") != original_host


@pytest.mark.unit
def test_config_access_nested_sections(temp_config_file: str):
    """
    Test accessing nested configuration sections directly.
    
    Args:
        temp_config_file: Path to temporary configuration file.
    """
    config = Config(temp_config_file)
    
    # Get parent key then access nested keys
    server = config.get("server")
    logging = config.get("logging")
    test_section = config.get("test_section")
    
    # Check sections
    assert isinstance(server, dict)
    assert isinstance(logging, dict)
    assert isinstance(test_section, dict)
    
    assert server["host"] == "127.0.0.1"
    assert server["port"] == 8000
    assert logging["level"] == "DEBUG"
    assert logging["file"] == "test.log"
    assert test_section["test_key"] == "test_value"
    assert test_section["nested"]["key1"] == "value1" 