#!/usr/bin/env python3
"""VFX MCP Server - Video editing server using FastMCP and ffmpeg-python.

This module provides a comprehensive video editing server built on the FastMCP
framework. It offers tools for basic video operations (trimming, resizing,
concatenation) and advanced features (audio processing, effects, format
conversion) using ffmpeg-python bindings.

Typical usage example:
    $ uv run python main.py
    # Server starts and listens for MCP requests via stdio transport
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vfx_mcp import create_mcp_server  # noqa: E402

# Initialize the MCP server (exposed for testing)
mcp = create_mcp_server()

# Run the server when called directly
if __name__ == "__main__":
    mcp.run()
