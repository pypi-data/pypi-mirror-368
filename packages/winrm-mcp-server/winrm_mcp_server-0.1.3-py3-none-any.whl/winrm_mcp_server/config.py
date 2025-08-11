"""Configuration management for WinRM MCP Server."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WinRMSettings(BaseSettings):
    """Settings for WinRM MCP Server."""

    # Connection parameters (required via environment variables)
    hostname: str = Field(..., description="Target hostname or IP address")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")

    # Default timeout for command execution (5 minutes in seconds)
    command_timeout: int = 300

    # Default WinRM port for HTTP
    default_http_port: int = 5985

    # Default WinRM port for HTTPS
    default_https_port: int = 5986

    # Connection port for WinRM (optional, defaults based on use_https)
    connection_port: Optional[int] = Field(default=None, description="Port to use for WinRM connection")

    # Connection timeout in seconds
    connection_timeout: int = 30

    # Maximum number of retries for transient failures
    max_retries: int = 3

    # Use HTTPS for WinRM connection
    use_https: bool = True

    # Skip SSL certificate verification (use with caution)
    skip_ssl_verification: bool = False

    model_config = SettingsConfigDict(env_prefix="WINRM_MCP_", case_sensitive=False)
