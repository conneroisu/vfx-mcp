"""
This type stub file was generated by pyright.
"""

import datetime
import httpx
import mcp.types
from pathlib import Path
from typing import Any, Generic, Literal, overload
from mcp import ClientSession
from pydantic import AnyUrl
from fastmcp.client.logging import LogHandler, MessageHandler
from fastmcp.client.progress import ProgressHandler
from fastmcp.client.roots import RootsHandler, RootsList
from fastmcp.client.sampling import SamplingHandler
from fastmcp.server import FastMCP
from fastmcp.utilities.mcp_config import MCPConfig
from fastmcp.utilities.types import MCPContent
from .transports import ClientTransportT, FastMCP1Server, FastMCPTransport, MCPConfigTransport, NodeStdioTransport, PythonStdioTransport, SSETransport, StreamableHttpTransport

__all__ = ["Client", "SessionKwargs", "RootsHandler", "RootsList", "LogHandler", "MessageHandler", "SamplingHandler", "ProgressHandler"]
class Client(Generic[ClientTransportT]):
    """
    MCP client that delegates connection management to a Transport instance.

    The Client class is responsible for MCP protocol logic, while the Transport
    handles connection establishment and management. Client provides methods for
    working with resources, prompts, tools and other MCP capabilities.

    Args:
        transport: Connection source specification, which can be:
            - ClientTransport: Direct transport instance
            - FastMCP: In-process FastMCP server
            - AnyUrl | str: URL to connect to
            - Path: File path for local socket
            - MCPConfig: MCP server configuration
            - dict: Transport configuration
        roots: Optional RootsList or RootsHandler for filesystem access
        sampling_handler: Optional handler for sampling requests
        log_handler: Optional handler for log messages
        message_handler: Optional handler for protocol messages
        progress_handler: Optional handler for progress notifications
        timeout: Optional timeout for requests (seconds or timedelta)
        init_timeout: Optional timeout for initial connection (seconds or timedelta).
            Set to 0 to disable. If None, uses the value in the FastMCP global settings.

    Examples:
        ```python # Connect to FastMCP server client =
        Client("http://localhost:8080")

        async with client:
            # List available resources resources = await client.list_resources()

            # Call a tool result = await client.call_tool("my_tool", {"param":
            "value"})
        ```
    """
    @overload
    def __new__(cls, transport: ClientTransportT, **kwargs: Any) -> Client[ClientTransportT]:
        ...
    
    @overload
    def __new__(cls, transport: AnyUrl, **kwargs) -> Client[SSETransport | StreamableHttpTransport]:
        ...
    
    @overload
    def __new__(cls, transport: FastMCP | FastMCP1Server, **kwargs) -> Client[FastMCPTransport]:
        ...
    
    @overload
    def __new__(cls, transport: Path, **kwargs) -> Client[PythonStdioTransport | NodeStdioTransport]:
        ...
    
    @overload
    def __new__(cls, transport: MCPConfig | dict[str, Any], **kwargs) -> Client[MCPConfigTransport]:
        ...
    
    @overload
    def __new__(cls, transport: str, **kwargs) -> Client[PythonStdioTransport | NodeStdioTransport | SSETransport | StreamableHttpTransport]:
        ...
    
    def __new__(cls, transport, **kwargs) -> Client:
        ...
    
    def __init__(self, transport: ClientTransportT | FastMCP | AnyUrl | Path | MCPConfig | dict[str, Any] | str, roots: RootsList | RootsHandler | None = ..., sampling_handler: SamplingHandler | None = ..., log_handler: LogHandler | None = ..., message_handler: MessageHandler | None = ..., progress_handler: ProgressHandler | None = ..., timeout: datetime.timedelta | float | int | None = ..., init_timeout: datetime.timedelta | float | int | None = ..., client_info: mcp.types.Implementation | None = ..., auth: httpx.Auth | Literal["oauth"] | str | None = ...) -> None:
        ...
    
    @property
    def session(self) -> ClientSession:
        """Get the current active session. Raises RuntimeError if not connected."""
        ...
    
    @property
    def initialize_result(self) -> mcp.types.InitializeResult:
        """Get the result of the initialization request."""
        ...
    
    def set_roots(self, roots: RootsList | RootsHandler) -> None:
        """Set the roots for the client. This does not automatically call `send_roots_list_changed`."""
        ...
    
    def set_sampling_callback(self, sampling_callback: SamplingHandler) -> None:
        """Set the sampling callback for the client."""
        ...
    
    def is_connected(self) -> bool:
        """Check if the client is currently connected."""
        ...
    
    async def __aenter__(self): # -> Self:
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb): # -> None:
        ...
    
    async def close(self): # -> None:
        ...
    
    async def ping(self) -> bool:
        """Send a ping request."""
        ...
    
    async def cancel(self, request_id: str | int, reason: str | None = ...) -> None:
        """Send a cancellation notification for an in-progress request."""
        ...
    
    async def progress(self, progress_token: str | int, progress: float, total: float | None = ..., message: str | None = ...) -> None:
        """Send a progress notification."""
        ...
    
    async def set_logging_level(self, level: mcp.types.LoggingLevel) -> None:
        """Send a logging/setLevel request."""
        ...
    
    async def send_roots_list_changed(self) -> None:
        """Send a roots/list_changed notification."""
        ...
    
    async def list_resources_mcp(self) -> mcp.types.ListResourcesResult:
        """Send a resources/list request and return the complete MCP protocol result.

        Returns:
            mcp.types.ListResourcesResult: The complete response object from the protocol,
                containing the list of resources and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def list_resources(self) -> list[mcp.types.Resource]:
        """Retrieve a list of resources available on the server.

        Returns:
            list[mcp.types.Resource]: A list of Resource objects.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def list_resource_templates_mcp(self) -> mcp.types.ListResourceTemplatesResult:
        """Send a resources/listResourceTemplates request and return the complete MCP protocol result.

        Returns:
            mcp.types.ListResourceTemplatesResult: The complete response object from the protocol,
                containing the list of resource templates and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def list_resource_templates(self) -> list[mcp.types.ResourceTemplate]:
        """Retrieve a list of resource templates available on the server.

        Returns:
            list[mcp.types.ResourceTemplate]: A list of ResourceTemplate objects.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def read_resource_mcp(self, uri: AnyUrl | str) -> mcp.types.ReadResourceResult:
        """Send a resources/read request and return the complete MCP protocol result.

        Args:
            uri (AnyUrl | str): The URI of the resource to read. Can be a string or an AnyUrl object.

        Returns:
            mcp.types.ReadResourceResult: The complete response object from the protocol,
                containing the resource contents and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def read_resource(self, uri: AnyUrl | str) -> list[mcp.types.TextResourceContents | mcp.types.BlobResourceContents]:
        """Read the contents of a resource or resolved template.

        Args:
            uri (AnyUrl | str): The URI of the resource to read. Can be a string or an AnyUrl object.

        Returns:
            list[mcp.types.TextResourceContents | mcp.types.BlobResourceContents]: A list of content
                objects, typically containing either text or binary data.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def list_prompts_mcp(self) -> mcp.types.ListPromptsResult:
        """Send a prompts/list request and return the complete MCP protocol result.

        Returns:
            mcp.types.ListPromptsResult: The complete response object from the protocol,
                containing the list of prompts and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def list_prompts(self) -> list[mcp.types.Prompt]:
        """Retrieve a list of prompts available on the server.

        Returns:
            list[mcp.types.Prompt]: A list of Prompt objects.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def get_prompt_mcp(self, name: str, arguments: dict[str, Any] | None = ...) -> mcp.types.GetPromptResult:
        """Send a prompts/get request and return the complete MCP protocol result.

        Args:
            name (str): The name of the prompt to retrieve.
            arguments (dict[str, Any] | None, optional): Arguments to pass to the prompt. Defaults to None.

        Returns:
            mcp.types.GetPromptResult: The complete response object from the protocol,
                containing the prompt messages and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = ...) -> mcp.types.GetPromptResult:
        """Retrieve a rendered prompt message list from the server.

        Args:
            name (str): The name of the prompt to retrieve.
            arguments (dict[str, Any] | None, optional): Arguments to pass to the prompt. Defaults to None.

        Returns:
            mcp.types.GetPromptResult: The complete response object from the protocol,
                containing the prompt messages and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def complete_mcp(self, ref: mcp.types.ResourceReference | mcp.types.PromptReference, argument: dict[str, str]) -> mcp.types.CompleteResult:
        """Send a completion request and return the complete MCP protocol result.

        Args:
            ref (mcp.types.ResourceReference | mcp.types.PromptReference): The reference to complete.
            argument (dict[str, str]): Arguments to pass to the completion request.

        Returns:
            mcp.types.CompleteResult: The complete response object from the protocol,
                containing the completion and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def complete(self, ref: mcp.types.ResourceReference | mcp.types.PromptReference, argument: dict[str, str]) -> mcp.types.Completion:
        """Send a completion request to the server.

        Args:
            ref (mcp.types.ResourceReference | mcp.types.PromptReference): The reference to complete.
            argument (dict[str, str]): Arguments to pass to the completion request.

        Returns:
            mcp.types.Completion: The completion object.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def list_tools_mcp(self) -> mcp.types.ListToolsResult:
        """Send a tools/list request and return the complete MCP protocol result.

        Returns:
            mcp.types.ListToolsResult: The complete response object from the protocol,
                containing the list of tools and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def list_tools(self) -> list[mcp.types.Tool]:
        """Retrieve a list of tools available on the server.

        Returns:
            list[mcp.types.Tool]: A list of Tool objects.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def call_tool_mcp(self, name: str, arguments: dict[str, Any], progress_handler: ProgressHandler | None = ..., timeout: datetime.timedelta | float | int | None = ...) -> mcp.types.CallToolResult:
        """Send a tools/call request and return the complete MCP protocol result.

        This method returns the raw CallToolResult object, which includes an isError flag
        and other metadata. It does not raise an exception if the tool call results in an error.

        Args:
            name (str): The name of the tool to call.
            arguments (dict[str, Any]): Arguments to pass to the tool.
            timeout (datetime.timedelta | float | int | None, optional): The timeout for the tool call. Defaults to None.
            progress_handler (ProgressHandler | None, optional): The progress handler to use for the tool call. Defaults to None.

        Returns:
            mcp.types.CallToolResult: The complete response object from the protocol,
                containing the tool result and any additional metadata.

        Raises:
            RuntimeError: If called while the client is not connected.
        """
        ...
    
    async def call_tool(self, name: str, arguments: dict[str, Any] | None = ..., timeout: datetime.timedelta | float | int | None = ..., progress_handler: ProgressHandler | None = ...) -> list[MCPContent]:
        """Call a tool on the server.

        Unlike call_tool_mcp, this method raises a ToolError if the tool call results in an error.

        Args:
            name (str): The name of the tool to call.
            arguments (dict[str, Any] | None, optional): Arguments to pass to the tool. Defaults to None.
            timeout (datetime.timedelta | float | int | None, optional): The timeout for the tool call. Defaults to None.
            progress_handler (ProgressHandler | None, optional): The progress handler to use for the tool call. Defaults to None.

        Returns:
            list[mcp.types.TextContent | mcp.types.ImageContent | mcp.types.AudioContent | mcp.types.EmbeddedResource]:
                The content returned by the tool.

        Raises:
            ToolError: If the tool call results in an error.
            RuntimeError: If called while the client is not connected.
        """
        ...
    


