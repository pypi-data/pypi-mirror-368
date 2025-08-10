"""Tests for the WinRM MCP Server."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from winrm_mcp_server.config import WinRMSettings
from winrm_mcp_server.exceptions import AuthenticationError, ConnectionError
from winrm_mcp_server.winrm_client import WinRMClient


class TestWinRMSettings:
    """Tests for WinRM settings configuration."""

    def test_default_settings(self):
        """Test default settings values."""
        with patch.dict(
            "os.environ",
            {
                "WINRM_MCP_HOSTNAME": "test.host.com",
                "WINRM_MCP_USERNAME": "testuser",
                "WINRM_MCP_PASSWORD": "testpass",
            },
        ):
            settings = WinRMSettings() # type: ignore

            assert settings.hostname == "test.host.com"
            assert settings.username == "testuser"
            assert settings.password == "testpass"
            assert settings.command_timeout == 300
            assert settings.connection_timeout == 30
            assert settings.use_https is True
            assert settings.skip_ssl_verification is False
            assert settings.max_retries == 3

    def test_custom_settings(self):
        """Test custom settings values."""
        with patch.dict(
            "os.environ",
            {
                "WINRM_MCP_HOSTNAME": "custom.host.com",
                "WINRM_MCP_USERNAME": "customuser",
                "WINRM_MCP_PASSWORD": "custompass",
                "WINRM_MCP_COMMAND_TIMEOUT": "600",
                "WINRM_MCP_CONNECTION_TIMEOUT": "60",
                "WINRM_MCP_USE_HTTPS": "false",
                "WINRM_MCP_SKIP_SSL_VERIFICATION": "true",
                "WINRM_MCP_MAX_RETRIES": "5",
            },
        ):
            settings = WinRMSettings()

            assert settings.hostname == "custom.host.com"
            assert settings.username == "customuser"
            assert settings.password == "custompass"
            assert settings.command_timeout == 600
            assert settings.connection_timeout == 60
            assert settings.use_https is False
            assert settings.skip_ssl_verification is True
            assert settings.max_retries == 5


class TestWinRMClient:
    """Tests for the WinRM client."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        with patch.dict(
            "os.environ",
            {
                "WINRM_MCP_HOSTNAME": "test.host.com",
                "WINRM_MCP_USERNAME": "testuser",
                "WINRM_MCP_PASSWORD": "testpass",
            },
        ):
            return WinRMSettings()

    @pytest.fixture
    def winrm_client(self, mock_settings):
        """Create a WinRM client instance for testing."""
        return WinRMClient(settings=mock_settings)

    def test_client_initialization(self, winrm_client, mock_settings):
        """Test client initialization."""
        assert winrm_client.settings == mock_settings

    @patch("winrm_mcp_server.winrm_client.winrm.Session")
    def test_execute_command_success(self, mock_session_class, winrm_client):
        """Test successful command execution."""
        # Mock the Session class and its methods
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock the connection test
        mock_test_result = MagicMock()
        mock_test_result.status_code = 0
        mock_session.run_cmd.return_value = mock_test_result
        
        # Mock successful PowerShell command execution
        mock_result = MagicMock()
        mock_result.status_code = 0
        mock_result.std_out = b"Test output"
        mock_result.std_err = b""
        mock_session.run_ps.return_value = mock_result

        result = winrm_client.execute_command("Get-Process")

        assert result["status_code"] == 0
        assert result["stdout"] == "Test output"
        assert result["stderr"] == ""
        assert result["success"] is True
        mock_session.run_ps.assert_called_once_with("Get-Process")

    @patch("winrm_mcp_server.winrm_client.winrm.Session")
    def test_execute_command_with_error(self, mock_session_class, winrm_client):
        """Test command execution with error output."""
        # Mock the Session class and its methods
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock the connection test
        mock_test_result = MagicMock()
        mock_test_result.status_code = 0
        mock_session.run_cmd.return_value = mock_test_result

        # Mock command execution with error
        mock_result = MagicMock()
        mock_result.status_code = 1
        mock_result.std_out = b""
        mock_result.std_err = b"Command failed"
        mock_session.run_ps.return_value = mock_result

        result = winrm_client.execute_command("Invalid-Command")

        assert result["status_code"] == 1
        assert result["stdout"] == ""
        assert result["stderr"] == "Command failed"
        assert result["success"] is False

    def test_command_validation(self, winrm_client):
        """Test command validation."""
        # Test that empty commands raise ValueError
        with pytest.raises(ValueError, match="Command cannot be empty"):
            winrm_client.execute_command("")

        # Test that whitespace-only commands raise ValueError  
        with pytest.raises(ValueError, match="Command cannot be empty"):
            winrm_client.execute_command("   ")
