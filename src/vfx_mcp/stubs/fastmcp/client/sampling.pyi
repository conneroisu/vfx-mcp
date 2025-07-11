"""
This type stub file was generated by pyright.
"""

from collections.abc import Awaitable, Callable
from typing import TypeAlias
from mcp import ClientSession, CreateMessageResult
from mcp.client.session import SamplingFnT
from mcp.shared.context import LifespanContextT, RequestContext
from mcp.types import CreateMessageRequestParams as SamplingParams, SamplingMessage

__all__ = ["SamplingMessage", "SamplingParams", "SamplingHandler"]
SamplingHandler: TypeAlias = Callable[[list[SamplingMessage], SamplingParams, RequestContext[ClientSession, LifespanContextT]], str | CreateMessageResult | Awaitable[str | CreateMessageResult],]
def create_sampling_callback(sampling_handler: SamplingHandler) -> SamplingFnT:
    ...

