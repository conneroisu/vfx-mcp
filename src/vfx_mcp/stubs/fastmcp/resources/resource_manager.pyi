"""
This type stub file was generated by pyright.
"""

from collections.abc import Callable
from typing import Any, TYPE_CHECKING
from pydantic import AnyUrl
from fastmcp.resources.resource import Resource
from fastmcp.resources.template import ResourceTemplate
from fastmcp.settings import DuplicateBehavior
from fastmcp.server.server import MountedServer

"""Resource manager functionality."""
if TYPE_CHECKING:
    ...
logger = ...
class ResourceManager:
    """Manages FastMCP resources."""
    def __init__(self, duplicate_behavior: DuplicateBehavior | None = ..., mask_error_details: bool | None = ...) -> None:
        """Initialize the ResourceManager.

        Args:
            duplicate_behavior: How to handle duplicate resources
                (warn, error, replace, ignore)
            mask_error_details: Whether to mask error details from exceptions
                other than ResourceError
        """
        ...
    
    def mount(self, server: MountedServer) -> None:
        """Adds a mounted server as a source for resources and templates."""
        ...
    
    async def get_resources(self) -> dict[str, Resource]:
        """Get all registered resources, keyed by URI."""
        ...
    
    async def get_resource_templates(self) -> dict[str, ResourceTemplate]:
        """Get all registered templates, keyed by URI template."""
        ...
    
    async def list_resources(self) -> list[Resource]:
        """
        Lists all resources, applying protocol filtering.
        """
        ...
    
    async def list_resource_templates(self) -> list[ResourceTemplate]:
        """
        Lists all templates, applying protocol filtering.
        """
        ...
    
    def add_resource_or_template_from_fn(self, fn: Callable[..., Any], uri: str, name: str | None = ..., description: str | None = ..., mime_type: str | None = ..., tags: set[str] | None = ...) -> Resource | ResourceTemplate:
        """Add a resource or template to the manager from a function.

        Args:
            fn: The function to register as a resource or template
            uri: The URI for the resource or template
            name: Optional name for the resource or template
            description: Optional description of the resource or template
            mime_type: Optional MIME type for the resource or template
            tags: Optional set of tags for categorizing the resource or template

        Returns:
            The added resource or template. If a resource or template with the same URI already exists,
            returns the existing resource or template.
        """
        ...
    
    def add_resource_from_fn(self, fn: Callable[..., Any], uri: str, name: str | None = ..., description: str | None = ..., mime_type: str | None = ..., tags: set[str] | None = ...) -> Resource:
        """Add a resource to the manager from a function.

        Args:
            fn: The function to register as a resource
            uri: The URI for the resource
            name: Optional name for the resource
            description: Optional description of the resource
            mime_type: Optional MIME type for the resource
            tags: Optional set of tags for categorizing the resource

        Returns:
            The added resource. If a resource with the same URI already exists,
            returns the existing resource.
        """
        ...
    
    def add_resource(self, resource: Resource) -> Resource:
        """Add a resource to the manager.

        Args:
            resource: A Resource instance to add. The resource's .key attribute
                will be used as the storage key. To overwrite it, call
                Resource.with_key() before calling this method.
        """
        ...
    
    def add_template_from_fn(self, fn: Callable[..., Any], uri_template: str, name: str | None = ..., description: str | None = ..., mime_type: str | None = ..., tags: set[str] | None = ...) -> ResourceTemplate:
        """Create a template from a function."""
        ...
    
    def add_template(self, template: ResourceTemplate) -> ResourceTemplate:
        """Add a template to the manager.

        Args:
            template: A ResourceTemplate instance to add. The template's .key attribute
                will be used as the storage key. To overwrite it, call
                ResourceTemplate.with_key() before calling this method.

        Returns:
            The added template. If a template with the same URI already exists,
            returns the existing template.
        """
        ...
    
    async def has_resource(self, uri: AnyUrl | str) -> bool:
        """Check if a resource exists."""
        ...
    
    async def get_resource(self, uri: AnyUrl | str) -> Resource:
        """Get resource by URI, checking concrete resources first, then templates.

        Args:
            uri: The URI of the resource to get

        Raises:
            NotFoundError: If no resource or template matching the URI is found.
        """
        ...
    
    async def read_resource(self, uri: AnyUrl | str) -> str | bytes:
        """
        Internal API for servers: Finds and reads a resource, respecting the
        filtered protocol path.
        """
        ...
    


