"""
This type stub file was generated by pyright.
"""

from pathlib import Path
from pydantic import ValidationInfo
from fastmcp.resources.resource import Resource

"""Concrete resource implementations."""
logger = ...
class TextResource(Resource):
    """A resource that reads from a string."""
    text: str = ...
    async def read(self) -> str:
        """Read the text content."""
        ...
    


class BinaryResource(Resource):
    """A resource that reads from bytes."""
    data: bytes = ...
    async def read(self) -> bytes:
        """Read the binary content."""
        ...
    


class FileResource(Resource):
    """A resource that reads from a file.

    Set is_binary=True to read file as binary data instead of text.
    """
    path: Path = ...
    is_binary: bool = ...
    mime_type: str = ...
    @pydantic.field_validator("path")
    @classmethod
    def validate_absolute_path(cls, path: Path) -> Path:
        """Ensure path is absolute."""
        ...
    
    @pydantic.field_validator("is_binary")
    @classmethod
    def set_binary_from_mime_type(cls, is_binary: bool, info: ValidationInfo) -> bool:
        """Set is_binary based on mime_type if not explicitly set."""
        ...
    
    async def read(self) -> str | bytes:
        """Read the file content."""
        ...
    


class HttpResource(Resource):
    """A resource that reads from an HTTP endpoint."""
    url: str = ...
    mime_type: str = ...
    async def read(self) -> str | bytes:
        """Read the HTTP content."""
        ...
    


class DirectoryResource(Resource):
    """A resource that lists files in a directory."""
    path: Path = ...
    recursive: bool = ...
    pattern: str | None = ...
    mime_type: str = ...
    @pydantic.field_validator("path")
    @classmethod
    def validate_absolute_path(cls, path: Path) -> Path:
        """Ensure path is absolute."""
        ...
    
    def list_files(self) -> list[Path]:
        """List files in the directory."""
        ...
    
    async def read(self) -> str:
        """Read the directory listing."""
        ...
    


