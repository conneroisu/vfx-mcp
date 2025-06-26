"""Type stubs for fastmcp library.

This module provides type definitions for the fastmcp library to ensure
full type safety in test code.
"""

from typing import Any, Generic, TypeVar, Protocol
from collections.abc import AsyncContextManager, Mapping, Sequence

__all__ = ["FastMCP", "Client", "TextContent", "Context"]

T = TypeVar("T")


class TextContent:
    """Text content returned from tool calls."""

    text: str


class Context(Protocol):
    """Context for MCP operations."""

    async def info(self, message: str) -> None: ...
    async def error(self, message: str) -> None: ...


class FastMCP(Generic[T]):
    """FastMCP server class."""

    def __init__(self, name: str) -> None: ...
    def run(self) -> None: ...
    def tool(self, func: Any) -> Any: ...
    def resource(self, path: str) -> Any: ...


class Client:
    """MCP client for interacting with servers."""

    def __init__(self, server: FastMCP[Any]) -> None: ...

    async def __aenter__(self) -> Client: ...

    async def __aexit__(self, *args: object) -> None: ...

    async def call_tool(
        self, tool_name: str, arguments: Mapping[str, Any]
    ) -> list[TextContent]: ...

    async def read_resource(self, resource_uri: str) -> list[TextContent]: ...