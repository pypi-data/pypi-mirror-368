"""MCP Server implementation for WinRM remote command execution."""

import asyncio
import sys
from typing import Any, Dict, List, Sequence

from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    ServerCapabilities,
    TextContent,
    Tool,
    ToolsCapability,
)
from pydantic import BaseModel, Field

from .config import WinRMSettings
from .exceptions import (
    AuthenticationError,
    CommandExecutionError,
    ConnectionError,
    TimeoutError,
)
from .winrm_client import WinRMClient


class ExecuteCommandRequest(BaseModel):
    """Request model for execute_command tool."""

    command: str = Field(..., description="PowerShell command to execute")


class WinRMMCPServer:
    """MCP Server for WinRM remote command execution."""

    def __init__(self):
        """Initialize the MCP server."""
        # Initialize settings with current environment variables
        # This ensures that environment variables set in mcp.json are properly loaded
        self.settings = WinRMSettings()  # type: ignore

        self.server = Server("winrm-mcp-server")
        self.winrm_client = WinRMClient(settings=self.settings)

        # Configure logging for VS Code MCP output
        logger.remove()  # Remove default handler
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            level="DEBUG",
        )

        logger.info("WinRM MCP Server initializing...")
        logger.debug(
            f"Settings loaded: command_timeout={self.settings.command_timeout}, "
            f"use_https={self.settings.use_https}, "
            f"skip_ssl_verification={self.settings.skip_ssl_verification}"
        )

        # Register tools
        self._register_tools()

        logger.info("WinRM MCP Server initialized successfully")

    def _register_tools(self):
        """Register MCP tools."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="execute_command",
                    description="Execute a PowerShell command on a remote Windows host via WinRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "PowerShell command to execute",
                            }
                        },
                        "required": ["command"],
                    },
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
            """Handle tool calls."""
            if name == "execute_command":
                return await self._execute_command(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _execute_command(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute a PowerShell command on the configured remote host."""
        try:
            # Validate arguments
            request = ExecuteCommandRequest(**arguments)

            logger.info(f"Executing command on {self.settings.hostname}")
            logger.debug(f"User: {self.settings.username}, Command: {request.command}")

            # Execute command (run in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.winrm_client.execute_command, request.command)

            # Format response
            response_text = self._format_command_result(result)

            return [TextContent(type="text", text=response_text)]

        except (
            ConnectionError,
            AuthenticationError,
            CommandExecutionError,
            TimeoutError,
        ) as e:
            logger.error(f"WinRM error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]

    def _format_command_result(self, result: Dict[str, Any]) -> str:
        """Format command execution result for display."""
        lines = [
            f"Command executed on {result['hostname']}",
            (
                f"Status: {'SUCCESS' if result['success'] else 'FAILED'} "
                f"(Exit Code: {result['status_code']})"
            ),
            f"Execution Time: {result['execution_time_seconds']}s",
            "",
        ]

        if result["stdout"]:
            lines.extend(["=== STDOUT ===", result["stdout"].strip(), ""])

        if result["stderr"]:
            lines.extend(["=== STDERR ===", result["stderr"].strip(), ""])

        return "\n".join(lines)

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting WinRM MCP Server...")

        # Initialize server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="winrm-mcp-server",
                    server_version="0.1.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability(listChanged=True)),
                ),
            )


def main():
    """Main entry point."""
    server = WinRMMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
