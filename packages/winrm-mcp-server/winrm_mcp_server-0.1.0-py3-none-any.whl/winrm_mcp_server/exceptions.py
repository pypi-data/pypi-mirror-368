"""Exceptions for WinRM MCP Server."""


class WinRMError(Exception):
    """Base exception for WinRM-related errors."""

    pass


class ConnectionError(WinRMError):
    """Raised when connection to remote host fails."""

    pass


class AuthenticationError(WinRMError):
    """Raised when authentication fails."""

    pass


class CommandExecutionError(WinRMError):
    """Raised when command execution fails."""

    pass


class TimeoutError(WinRMError):
    """Raised when command execution times out."""

    pass
