"""
Integration tests for Dependency Injection.

These tests verify the end-to-end functionality of Dependency Injection
across all components of the system.
"""

import pytest
from fastapi.testclient import TestClient

from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.commands import Command, SuccessResult, registry, container


# Test services and commands
class DatabaseMockService:
    """Mock database service for testing."""
    
    def __init__(self):
        """Initialize the mock DB service."""
        self.data = {}
        self.connection_count = 0
        
    def connect(self):
        """Simulate connecting to a database."""
        self.connection_count += 1
        return True
        
    def get_data(self, key):
        """Get data by key."""
        return self.data.get(key)
        
    def set_data(self, key, value):
        """Set data by key."""
        self.data[key] = value
        return True


class LoggingService:
    """Mock logging service for testing."""
    
    def __init__(self):
        """Initialize the mock logging service."""
        self.logs = []
        
    def log(self, message):
        """Log a message."""
        self.logs.append(message)
        return True


class DataCommandResult(SuccessResult):
    """Result for data commands."""
    
    def __init__(self, operation, key, value=None):
        """Initialize with operation details."""
        data = {
            "operation": operation,
            "key": key
        }
        if value is not None:
            data["value"] = value
            
        super().__init__(data=data)


class GetDataCommand(Command):
    """Command to get data from DB."""
    
    name = "get_data"
    result_class = DataCommandResult
    
    def __init__(self, db_service: DatabaseMockService, log_service: LoggingService):
        """Initialize with DB and logging services."""
        self.db = db_service
        self.logger = log_service
        
    async def execute(self, key: str) -> DataCommandResult:
        """Execute the command."""
        self.logger.log(f"Getting data for key: {key}")
        value = self.db.get_data(key)
        return DataCommandResult("get", key, value)


class SetDataCommand(Command):
    """Command to set data in DB."""
    
    name = "set_data"
    result_class = DataCommandResult
    
    def __init__(self, db_service: DatabaseMockService, log_service: LoggingService):
        """Initialize with DB and logging services."""
        self.db = db_service
        self.logger = log_service
        
    async def execute(self, key: str, value: str) -> DataCommandResult:
        """Execute the command."""
        self.logger.log(f"Setting data for key: {key}, value: {value}")
        self.db.set_data(key, value)
        return DataCommandResult("set", key, value)


@pytest.fixture
def di_test_app():
    """Create a test app with DI configured."""
    # Clear any existing registrations
    registry.clear()
    container.clear()
    
    # Create and register services
    db_service = DatabaseMockService()
    log_service = LoggingService()
    
    container.register("db_service", db_service)
    container.register("log_service", log_service)
    
    # Create and register commands with dependencies
    get_command = GetDataCommand(db_service, log_service)
    set_command = SetDataCommand(db_service, log_service)
    
    registry.register(get_command)
    registry.register(set_command)
    
    # Create app
    app = create_app()
    client = TestClient(app)
    
    # Return both client and services for assertions
    return {
        "client": client,
        "db_service": db_service,
        "log_service": log_service
    }


class TestDependencyInjectionIntegration:
    """Integration tests for Dependency Injection."""
    
    def test_set_and_get_data_via_jsonrpc(self, di_test_app):
        """Test setting and getting data through the JSON-RPC API."""
        client = di_test_app["client"]
        log_service = di_test_app["log_service"]
        
        # Set data
        set_response = client.post(
            "/api/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "set_data",
                "params": {"key": "test_key", "value": "test_value"},
                "id": 1
            }
        )
        
        # Check set response
        assert set_response.status_code == 200
        set_result = set_response.json()
        assert set_result["result"]["success"] is True
        assert set_result["result"]["data"]["operation"] == "set"
        assert set_result["result"]["data"]["key"] == "test_key"
        assert set_result["result"]["data"]["value"] == "test_value"
        
        # Get data
        get_response = client.post(
            "/api/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "get_data",
                "params": {"key": "test_key"},
                "id": 2
            }
        )
        
        # Check get response
        assert get_response.status_code == 200
        get_result = get_response.json()
        assert get_result["result"]["success"] is True
        assert get_result["result"]["data"]["operation"] == "get"
        assert get_result["result"]["data"]["key"] == "test_key"
        assert get_result["result"]["data"]["value"] == "test_value"
        
        # Check logs were created by the logging service
        assert len(log_service.logs) == 2
        assert "Setting data for key: test_key" in log_service.logs[0]
        assert "Getting data for key: test_key" in log_service.logs[1]
    
    def test_same_instance_used_across_requests(self, di_test_app):
        """Test that the same service instances are used across requests."""
        client = di_test_app["client"]
        db_service = di_test_app["db_service"]
        
        # Set data in multiple requests
        keys = ["key1", "key2", "key3"]
        for i, key in enumerate(keys):
            client.post(
                "/api/jsonrpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "set_data",
                    "params": {"key": key, "value": f"value{i}"},
                    "id": i
                }
            )
        
        # Check that all data was stored in the same DB instance
        assert db_service.data["key1"] == "value0"
        assert db_service.data["key2"] == "value1"
        assert db_service.data["key3"] == "value2"
        
        # Get data for all keys in one batch request
        batch_request = []
        for i, key in enumerate(keys):
            batch_request.append({
                "jsonrpc": "2.0",
                "method": "get_data",
                "params": {"key": key},
                "id": i + 10
            })
            
        batch_response = client.post("/api/jsonrpc", json=batch_request)
        batch_results = batch_response.json()
        
        # Check all results use the same DB instance
        assert batch_results[0]["result"]["data"]["value"] == "value0"
        assert batch_results[1]["result"]["data"]["value"] == "value1"
        assert batch_results[2]["result"]["data"]["value"] == "value2" 