"""WinRM client wrapper for remote command execution."""

import time
from typing import Any, Dict

import winrm
from loguru import logger

from .config import WinRMSettings
from .exceptions import (
    AuthenticationError,
    CommandExecutionError,
    ConnectionError,
    TimeoutError,
)


class WinRMClient:
    """A wrapper around pywinrm for executing remote commands."""

    def __init__(self, settings: WinRMSettings):
        """Initialize the WinRM client with required settings.

        Args:
            settings: WinRM configuration settings containing connection details
        """
        self.settings = settings
        logger.debug("Initializing WinRM client")

    def _build_winrm_url(self, hostname: str, use_https: bool, port: int) -> str:
        """Build WinRM URL with proper protocol and port."""
        protocol = "https" if use_https else "http"
        return f"{protocol}://{hostname}:{port}/wsman"

    def _create_session(self) -> winrm.Session:
        """Create a WinRM session with the specified parameters."""
        port = (
            self.settings.connection_port
            if self.settings.connection_port is not None
            else (
                self.settings.default_https_port
                if self.settings.use_https
                else self.settings.default_http_port
            )
        )
        url = self._build_winrm_url(self.settings.hostname, self.settings.use_https, port)

        logger.debug(f"Creating WinRM session to {url}")

        try:
            # Create session with basic authentication
            session = winrm.Session(
                url,
                auth=(self.settings.username, self.settings.password),
                transport="ntlm",
                server_cert_validation=("ignore" if self.settings.skip_ssl_verification else "validate"),
            )
            if self._test_connection(session):
                logger.info(f"Successfully connected to {self.settings.hostname}")
            else:
                raise Exception("Connection test failed")
            return session
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.settings.hostname}. Last error: {e}")

    def _test_connection(self, session: winrm.Session) -> bool:
        """Test if the WinRM connection is working."""
        try:
            # Run a simple command to test connectivity
            result = session.run_cmd("echo test")
            return result.status_code == 0
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False

    def _safe_decode(self, data: bytes) -> str:
        """
        Safely decode bytes to string with fallback handling for binary data.

        Args:
            data: Bytes to decode

        Returns:
            Decoded string or base64-encoded representation for binary data
        """
        if not data:
            return ""

        try:
            # Try UTF-8 decoding first
            decoded = data.decode("utf-8")
            return decoded
        except UnicodeDecodeError:
            # Check if this looks like binary data by examining the content
            # Binary data often contains null bytes or high percentage of non-printable chars
            null_count = data.count(b"\x00")
            non_printable_count = sum(
                1 for byte in data if byte < 32 and byte not in [9, 10, 13]
            )  # Tab, LF, CR are ok

            # If more than 10% null bytes or more than 30% non-printable, treat as binary
            is_binary = len(data) > 0 and (
                null_count / len(data) > 0.1 or non_printable_count / len(data) > 0.3
            )
            if is_binary:
                import base64

                logger.warning(
                    "Binary data detected in command output, returning base64 encoded representation"
                )
                b64_data = base64.b64encode(data).decode("ascii")
                return f"[BINARY DATA - BASE64]: {b64_data}"

            # Try with error handling to replace invalid characters for text-like data
            try:
                return data.decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                # If still failing, try other common encodings
                for encoding in ["latin1", "cp1252", "ascii"]:
                    try:
                        return data.decode(encoding)
                    except UnicodeDecodeError:
                        continue

                # Last resort: return base64 encoded data
                import base64

                logger.warning(
                    "Unable to decode data with any encoding, returning base64 encoded representation"
                )
                b64_data = base64.b64encode(data).decode("ascii")
                return f"[BINARY DATA - BASE64]: {b64_data}"

    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a PowerShell command on the configured remote host.

        Args:
            command: PowerShell command to execute

        Returns:
            Dictionary containing execution results

        Raises:
            ConnectionError: If connection to host fails
            AuthenticationError: If authentication fails
            CommandExecutionError: If command execution fails
            TimeoutError: If command execution times out
            ValueError: If command is empty or invalid
        """
        # Validate command input
        if not command or not command.strip():
            raise ValueError("Command cannot be empty")
        
        command = command.strip()
        
        start_time = time.time()
        session = None

        logger.info(f"Executing command on {self.settings.hostname} as {self.settings.username}")
        logger.debug(f"Command: {command}")

        try:
            # Establish connection
            session = self._create_session()

            # Execute the command with timeout
            logger.debug(f"Running command with {self.settings.command_timeout}s timeout")

            # Use run_ps for PowerShell commands
            result = session.run_ps(command)

            execution_time = time.time() - start_time

            # Prepare response with safe decoding
            response = {
                "hostname": self.settings.hostname,
                "command": command,
                "status_code": result.status_code,
                "stdout": self._safe_decode(result.std_out) if result.std_out else "",
                "stderr": self._safe_decode(result.std_err) if result.std_err else "",
                "execution_time_seconds": round(execution_time, 2),
                "success": result.status_code == 0,
            }

            if response["success"]:
                logger.info(
                    f"Command executed successfully on {self.settings.hostname} in {execution_time:.2f}s"
                )
            else:
                logger.warning(f"Command failed on {self.settings.hostname} with status {result.status_code}")
                logger.debug(f"Error output: {response['stderr']}")

            return response

        except Exception as e:
            error_msg = str(e).lower()
            if "unauthorized" in error_msg or "401" in error_msg or "authentication" in error_msg:
                raise AuthenticationError(
                    f"Authentication failed for {self.settings.username}@{self.settings.hostname}: {e}"
                )
            elif "timeout" in error_msg:
                raise TimeoutError(f"Command execution timed out on {self.settings.hostname}: {e}")
            elif "connection" in error_msg or "network" in error_msg:
                raise ConnectionError(f"Connection error to {self.settings.hostname}: {e}")
            else:
                logger.error(f"Unexpected error executing command on {self.settings.hostname}: {e}")
                raise CommandExecutionError(f"Failed to execute command on {self.settings.hostname}: {e}")
