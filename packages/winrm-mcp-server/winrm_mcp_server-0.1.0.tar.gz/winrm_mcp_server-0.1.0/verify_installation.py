#!/usr/bin/env python3
"""Installation verification script for WinRM MCP Server."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def check_package_installed():
    """Check if the package can be imported."""
    try:
        import winrm_mcp_server

        print(f"✅ winrm-mcp-server package found (version {winrm_mcp_server.__version__})")
        return True
    except ImportError:
        print("❌ winrm-mcp-server package not found")
        print("   Install with: pip install winrm-mcp-server")
        return False


def check_dependencies():
    """Check if all dependencies are available."""
    required_packages = ["mcp", "winrm", "pydantic", "pydantic_settings", "loguru"]

    all_available = True
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            print(f"✅ {package} is available")
        else:
            print(f"❌ {package} is missing")
            all_available = False

    return all_available


def test_entry_point():
    """Test if the command-line entry point is available."""
    try:
        # Try running with minimal environment to test the entry point exists
        result = subprocess.run(
            ["winrm-mcp-server"],
            capture_output=True,
            text=True,
            timeout=5,
            env={
                **os.environ,
                "WINRM_MCP_HOSTNAME": "test",
                "WINRM_MCP_USERNAME": "test",
                "WINRM_MCP_PASSWORD": "test",
            },
        )

        # If the command runs (even if it fails due to config), the entry point works
        if result.returncode == 0 or "Starting WinRM MCP Server" in result.stderr or "MCP" in result.stderr:
            print("✅ winrm-mcp-server command is available")
            return True
        else:
            print(f"❌ winrm-mcp-server command failed with return code {result.returncode}")
            if result.stdout:
                print(f"   stdout: {result.stdout[:200]}")
            if result.stderr:
                print(f"   stderr: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        # Timeout might happen if the server starts waiting for MCP input
        print("✅ winrm-mcp-server command is available (timed out waiting for MCP input)")
        return True
    except FileNotFoundError:
        print("❌ winrm-mcp-server command not found in PATH")
        return False
    except Exception as e:
        print(f"❌ winrm-mcp-server command failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("WinRM MCP Server Installation Verification")
    print("=" * 45)

    checks = [check_python_version, check_package_installed, check_dependencies, test_entry_point]

    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()

    if all_passed:
        print("🎉 All checks passed! WinRM MCP Server is ready to use.")
        print("\nNext steps:")
        print("1. Configure your environment variables (see README.md)")
        print("2. Add the server to your VS Code MCP configuration")
        print("3. Test the connection with your target Windows machine")
    else:
        print("❌ Some checks failed. Please resolve the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
