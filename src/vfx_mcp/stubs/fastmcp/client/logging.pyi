"""
This type stub file was generated by pyright.
"""

from collections.abc import Awaitable, Callable
from typing import TypeAlias
from mcp.client.session import LoggingFnT, MessageHandlerFnT
from mcp.types import LoggingMessageNotificationParams

logger = ...
LogMessage: TypeAlias = LoggingMessageNotificationParams
LogHandler: TypeAlias = Callable[[LogMessage], Awaitable[None]]
MessageHandler: TypeAlias = MessageHandlerFnT
async def default_log_handler(message: LogMessage) -> None:
    ...

def create_log_callback(handler: LogHandler | None = ...) -> LoggingFnT:
    ...

