"""FastMCP server setup and tool registration.

This module creates and configures the VFX MCP server with comprehensive
video editing capabilities. Registers all available tool modules and
resource endpoints to provide a complete video processing API.

The server provides:
    - Basic video operations (trim, resize, concatenate)
    - Advanced video effects (filters, speed changes)
    - Audio processing (extraction, mixing, enhancement)
    - Format conversion (codecs, containers)
    - Compositing and automation tools
    - MCP resource endpoints for file discovery

Example:
    Create and start the server:

        server = create_mcp_server()
        # Server is ready to handle MCP requests
"""

from fastmcp import FastMCP


def create_mcp_server() -> FastMCP:
    """Create and configure the VFX MCP server with all tools registered.

    Initializes a FastMCP server instance and registers all available video
    editing tools and resource endpoints. The resulting server provides a
    comprehensive API for video processing operations.

    Returns:
        FastMCP: Configured server instance with all tools registered.

    Example:
        server = create_mcp_server()
        # Server ready to handle video editing requests
    """
    mcp = FastMCP("vfx-mcp")

    # Import and register all tool modules
    from ..resources.mcp_endpoints import register_resource_endpoints
    from ..tools.advanced_compositing import (
        register_compositing_tools,
    )
    from ..tools.audio_processing import (
        register_audio_tools,
    )
    from ..tools.basic_video_ops import (
        register_basic_video_tools,
    )
    from ..tools.batch_automation import (
        register_automation_tools,
    )
    from ..tools.format_conversion import (
        register_format_conversion_tools,
    )
    from ..tools.text_animation import (
        register_animation_tools,
    )
    from ..tools.video_analysis import (
        register_analysis_tools,
    )
    from ..tools.video_effects import (
        register_video_effects_tools,
    )
    from ..tools.video_transitions import (
        register_transition_tools,
    )

    # Register all tool categories
    register_basic_video_tools(mcp)
    register_audio_tools(mcp)
    register_video_effects_tools(mcp)
    register_format_conversion_tools(mcp)
    register_compositing_tools(mcp)
    register_transition_tools(mcp)
    register_animation_tools(mcp)
    register_automation_tools(mcp)
    register_analysis_tools(mcp)
    register_resource_endpoints(mcp)

    return mcp
