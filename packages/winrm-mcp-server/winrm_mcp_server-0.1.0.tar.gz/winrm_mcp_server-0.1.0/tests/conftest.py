"""Test configuration for pytest."""

import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    test_env = {
        "WINRM_MCP_HOSTNAME": "test.host.com",
        "WINRM_MCP_USERNAME": "testuser",
        "WINRM_MCP_PASSWORD": "testpass",
    }

    with patch.dict(os.environ, test_env):
        yield
