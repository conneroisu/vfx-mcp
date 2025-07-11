"""
This type stub file was generated by pyright.
"""

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from mcp import LoggingLevel
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.shared.context import RequestContext
from mcp.types import ModelPreferences, Root, SamplingMessage
from pydantic.networks import AnyUrl
from starlette.requests import Request
from fastmcp.server.server import FastMCP
from fastmcp.utilities.types import MCPContent

logger = ...
_current_context: ContextVar[Context | None] = ...
@contextmanager
def set_context(context: Context) -> Generator[Context, None, None]:
    ...

@dataclass
class Context:
    """Context object providing access to MCP capabilities.

    This provides a cleaner interface to MCP's RequestContext functionality.
    It gets injected into tool and resource functions that request it via type hints.

    To use context in a tool function, add a parameter with the Context type annotation:

    ```python
    @server.tool
    def my_tool(x: int, ctx: Context) -> str:
        # Log messages to the client
        ctx.info(f"Processing {x}")
        ctx.debug("Debug info")
        ctx.warning("Warning message")
        ctx.error("Error message")

        # Report progress
        ctx.report_progress(50, 100, "Processing")

        # Access resources
        data = ctx.read_resource("resource://data")

        # Get request info
        request_id = ctx.request_id
        client_id = ctx.client_id

        return str(x)
    ```

    The context parameter name can be anything as long as it's annotated with Context.
    The context is optional - tools that don't need it can omit the parameter.

    """
    def __init__(self, fastmcp: FastMCP) -> None:
        ...
    
    def __enter__(self) -> Context:
        """Enter the context manager and set this context as the current context."""
        ...
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager and reset the most recent token."""
        ...
    
    @property
    def request_context(self) -> RequestContext:
        """Access to the underlying request context.

        If called outside of a request context, this will raise a ValueError.
        """
        ...
    
    async def report_progress(self, progress: float, total: float | None = ..., message: str | None = ...) -> None:
        """Report progress for the current operation.

        Args:
            progress: Current progress value e.g. 24
            total: Optional total value e.g. 100
        """
        ...
    
    async def read_resource(self, uri: str | AnyUrl) -> list[ReadResourceContents]:
        """Read a resource by URI.

        Args:
            uri: Resource URI to read

        Returns:
            The resource content as either text or bytes
        """
        ...
    
    async def log(self, message: str, level: LoggingLevel | None = ..., logger_name: str | None = ...) -> None:
        """Send a log message to the client.

        Args:
            message: Log message
            level: Optional log level. One of "debug", "info", "notice", "warning", "error", "critical",
                "alert", or "emergency". Default is "info".
            logger_name: Optional logger name
        """
        ...
    
    @property
    def client_id(self) -> str | None:
        """Get the client ID if available."""
        ...
    
    @property
    def request_id(self) -> str:
        """Get the unique ID for this request."""
        ...
    
    @property
    def session_id(self) -> str | None:
        """Get the MCP session ID for HTTP transports.

        Returns the session ID that can be used as a key for session-based
        data storage (e.g., Redis) to share data between tool calls within
        the same client session.

        Returns:
            The session ID for HTTP transports (SSE, StreamableHTTP), or None
            for stdio and in-memory transports which don't use session IDs.

        Example:
            ```python
            @server.tool
            def store_data(data: dict, ctx: Context) -> str:
                if session_id := ctx.session_id:
                    redis_client.set(f"session:{session_id}:data", json.dumps(data))
                    return f"Data stored for session {session_id}"
                return "No session ID available (stdio/memory transport)"
            ```
        """
        ...
    
    @property
    def session(self):
        """Access to the underlying session for advanced usage."""
        ...
    
    async def debug(self, message: str, logger_name: str | None = ...) -> None:
        """Send a debug log message."""
        ...
    
    async def info(self, message: str, logger_name: str | None = ...) -> None:
        """Send an info log message."""
        ...
    
    async def warning(self, message: str, logger_name: str | None = ...) -> None:
        """Send a warning log message."""
        ...
    
    async def error(self, message: str, logger_name: str | None = ...) -> None:
        """Send an error log message."""
        ...
    
    async def list_roots(self) -> list[Root]:
        """List the roots available to the server, as indicated by the client."""
        ...
    
    async def sample(self, messages: str | list[str | SamplingMessage], system_prompt: str | None = ..., temperature: float | None = ..., max_tokens: int | None = ..., model_preferences: ModelPreferences | str | list[str] | None = ...) -> MCPContent:
        """
        Send a sampling request to the client and await the response.

        Call this method at any time to have the server request an LLM
        completion from the client. The client must be appropriately configured,
        or the request will error.
        """
        ...
    
    def get_http_request(self) -> Request:
        """Get the active starlette request."""
        ...
    


