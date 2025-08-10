# WinRM MCP Server

A Model Context Protocol (MCP) server that enables AI agents to execute PowerShell commands on remote Windows machines via WinRM.

[![PyPI version](https://badge.fury.io/py/winrm-mcp-server.svg)](https://badge.fury.io/py/winrm-mcp-server)
[![Python Version](https://img.shields.io/pypi/pyversions/winrm-mcp-server.svg)](https://pypi.org/project/winrm-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/antonvano-microsoft/winrm-mcp-server/workflows/CI/badge.svg)](https://github.com/antonvano-microsoft/winrm-mcp-server/actions)

## Features

- **Remote Command Execution**: Execute PowerShell commands on remote Windows hosts
- **Secure Authentication**: Uses username/password authentication with support for both HTTP and HTTPS
- **Error Handling**: Comprehensive error handling with semantic separation of error types
- **Timeout Management**: Configurable command timeouts (default: 5 minutes)
- **Comprehensive Logging**: Detailed logging compatible with VS Code's MCP Server output
- **Connection Flexibility**: Automatically tries HTTPS first, falls back to HTTP if needed

## Installation

### From PyPI (Recommended)

```bash
pip install winrm-mcp-server
```

### From Source

1. Clone this repository
2. Install dependencies using `uv`:

```bash
cd winrm-mcp-server
uv sync
```

## Configuration

The server can be configured via VS Code's MCP configuration. Add the following to your VS Code settings or MCP configuration file:

### Using the installed package

```json
{
  "mcpServers": {
    "winrm-mcp-server": {
      "command": "winrm-mcp-server",
      "env": {
        "WINRM_MCP_HOSTNAME": "remote.host.com",
        "WINRM_MCP_USERNAME": "username",
        "WINRM_MCP_PASSWORD": "secret"
      }
    }
  }
}
```

### Using from source

```json
{
  "mcpServers": {
    "winrm-mcp-server": {
      "command": "python",
      "args": ["run_server.py"],
      "cwd": "/path/to/winrm-mcp-server",
      "env": {
        "WINRM_MCP_HOSTNAME": "remote.host.com",
        "WINRM_MCP_USERNAME": "username",
        "WINRM_MCP_PASSWORD": "secret"
      }
    }
  }
}
```

### Environment Variables

You can customize the server behavior using environment variables:

**Required Variables:**

- `WINRM_MCP_HOSTNAME`: Target Windows hostname or IP address (required)
- `WINRM_MCP_USERNAME`: Username for authentication (required)
- `WINRM_MCP_PASSWORD`: Password for authentication (required)

**Optional Variables:**

- `WINRM_MCP_COMMAND_TIMEOUT`: Command execution timeout in seconds (default: 300)
- `WINRM_MCP_CONNECTION_PORT`: Connection port to use (default: 5985 for HTTP, 5986 for HTTPS)
- `WINRM_MCP_CONNECTION_TIMEOUT`: Connection timeout in seconds (default: 30)
- `WINRM_MCP_USE_HTTPS`: Prefer HTTPS over HTTP (default: true)
- `WINRM_MCP_SKIP_SSL_VERIFICATION`: Skip SSL certificate verification (default: false)
- `WINRM_MCP_MAX_RETRIES`: Maximum retries for transient failures (default: 3)

## Usage

The server exposes a single tool: `execute_command`

### Parameters

- `command`: PowerShell command to execute

### Example

```json
{
  "tool": "execute_command",
  "arguments": {
    "command": "Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Select-Object -First 10"
  }
}
```

## Security Considerations

- Credentials are handled securely and not logged
- Supports both HTTP and HTTPS WinRM connections
- SSL certificate validation can be configured
- Command input is validated to prevent injection attacks

## Requirements

### Target Windows Machines

The target Windows machines must have WinRM enabled and configured:

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Configure WinRM for HTTP (if needed)
winrm quickconfig

# Configure WinRM for HTTPS (recommended)
# (Requires SSL certificate configuration)
```

### Network Requirements

- WinRM HTTP port (default: 5985) or HTTPS port (default: 5986) must be accessible
- Windows Firewall rules must allow WinRM traffic

## Error Types

The server provides semantic error separation:

- **ConnectionError**: Network connectivity issues
- **AuthenticationError**: Invalid credentials or authentication failures
- **CommandExecutionError**: Command execution failures
- **TimeoutError**: Command execution timeouts

## Development

### Setting up the development environment

```bash
git clone https://github.com/antonvano-microsoft/winrm-mcp-server.git
cd winrm-mcp-server
uv sync --dev
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
```

### Type Checking

```bash
uv run mypy .
```

### Building and Publishing

To build the package:

```bash
uv build
```

To publish to PyPI (maintainers only):

```bash
uv publish
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate and follow the existing code style.

## License

MIT License - see LICENSE file for details.
