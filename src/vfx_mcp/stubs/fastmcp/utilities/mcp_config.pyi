"""
This type stub file was generated by pyright.
"""

import httpx
from typing import Annotated, Any, Literal, TYPE_CHECKING
from pydantic import AnyUrl, Field
from fastmcp.utilities.types import FastMCPBaseModel
from fastmcp.client.transports import SSETransport, StdioTransport, StreamableHttpTransport

if TYPE_CHECKING:
    ...
def infer_transport_type_from_url(url: str | AnyUrl) -> Literal["http", "sse"]:
    """
    Infer the appropriate transport type from the given URL.
    """
    ...

class StdioMCPServer(FastMCPBaseModel):
    command: str
    args: list[str] = ...
    env: dict[str, Any] = ...
    cwd: str | None = ...
    transport: Literal["stdio"] = ...
    def to_transport(self) -> StdioTransport:
        ...
    


class RemoteMCPServer(FastMCPBaseModel):
    url: str
    headers: dict[str, str] = ...
    transport: Literal["http", "streamable-http", "sse"] | None = ...
    auth: Annotated[str | Literal["oauth"] | httpx.Auth | None, Field(description='Either a string representing a Bearer token, the literal "oauth" to use OAuth authentication, or an httpx.Auth instance for custom authentication.'),] = ...
    model_config = ...
    def to_transport(self) -> StreamableHttpTransport | SSETransport:
        ...
    


class MCPConfig(FastMCPBaseModel):
    mcpServers: dict[str, StdioMCPServer | RemoteMCPServer]
    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> MCPConfig:
        ...
    


