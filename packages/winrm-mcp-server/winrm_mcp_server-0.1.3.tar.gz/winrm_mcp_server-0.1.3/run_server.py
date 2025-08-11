#!/usr/bin/env python3
"""Startup script for WinRM MCP Server."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to src directory so relative imports work
os.chdir(src_path)

# Import and run the main function from server.py
from winrm_mcp_server.server import main

if __name__ == "__main__":
    asyncio.run(main())
