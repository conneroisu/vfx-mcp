"""VFX MCP Server - Professional video editing tools via Model Context Protocol.

A comprehensive video editing server built on FastMCP framework, providing
professional-grade video processing capabilities through ffmpeg-python bindings.
"""

__version__ = "0.1.0"
__author__ = "VFX MCP Team"

from .core.server import create_mcp_server

__all__ = ["create_mcp_server"]
