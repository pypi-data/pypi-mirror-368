# Configuration

This guide describes how to configure the MCP Proxy service.

## Configuration File

The MCP Proxy service is configured using a JSON configuration file. By default, it looks for a file named `config.json` in the current directory.

You can specify a different configuration file using the `--config` command-line option:

```bash
mcp-proxy --config /path/to/config.json
```

## Configuration Options

Here's a list of available configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| host | string | "0.0.0.0" | The host to bind the service to |
| port | number | 8000 | The port to listen on |
| log_level | string | "INFO" | The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| log_file | string | null | Path to the log file (if null, logs to stdout) |
| log_rotation_type | string | "size" | The log rotation type ("size" or "time") |
| log_max_bytes | number | 10485760 | The maximum log file size in bytes (if rotation_type is "size") |
| log_backup_count | number | 5 | The number of backup log files to keep |
| cors_origins | array | ["*"] | A list of allowed CORS origins |
| api_keys | array | [] | A list of valid API keys (if empty, authentication is disabled) |

## Example Configuration

Here's an example configuration file:

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "log_level": "INFO",
  "log_file": "logs/mcp_proxy.log",
  "log_rotation_type": "size",
  "log_max_bytes": 10485760,
  "log_backup_count": 5,
  "cors_origins": ["*"],
  "api_keys": ["your-api-key-here"]
}
```

## Environment Variables

You can also configure the service using environment variables. Environment variables take precedence over the configuration file.

The environment variable format is `MCP_UPPERCASE_OPTION_NAME`. For example, to set the port:

```bash
export MCP_PORT=8000
```

## Testing the Configuration

To verify your configuration, you can run the service with the `--validate-config` option:

```bash
mcp-proxy --config /path/to/config.json --validate-config
```

This will validate the configuration file and exit without starting the service. 