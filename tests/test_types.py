"""Type definitions for test utilities.

This module provides type definitions and protocols for test code to ensure
full type safety when working with external libraries that may have incomplete
type annotations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import AsyncContextManager, Mapping

    from fastmcp import FastMCP, TextContent


@runtime_checkable
class CallToolResult(Protocol):
    """Protocol for tool call results."""

    text: str


@runtime_checkable
class MCPClient(Protocol):
    """Protocol defining the interface for MCP clients."""

    async def call_tool(
        self, tool_name: str, arguments: Mapping[str, Any]
    ) -> list[TextContent]:
        """Call a tool with the given arguments."""
        ...

    async def read_resource(self, resource_uri: str) -> list[TextContent]:
        """Read a resource by URI."""
        ...


@runtime_checkable
class MCPClientContextManager(Protocol):
    """Protocol for MCP client context managers."""

    def __init__(self, server: FastMCP[None]) -> None:
        """Initialize with server."""
        ...

    def __aenter__(self) -> AsyncContextManager[MCPClient]:
        """Async enter."""
        ...

    async def __aexit__(self, *args: object) -> None:
        """Async exit."""
        ...