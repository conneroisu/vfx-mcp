"""FastMCP server setup and tool registration."""

from fastmcp import FastMCP


def create_mcp_server() -> FastMCP:
    """Create and configure the VFX MCP server with all tools registered."""
    mcp = FastMCP("vfx-mcp")

    # Import and register all tool modules
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

    # from ..resources.mcp_endpoints import register_resource_endpoints

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
    # register_resource_endpoints(mcp)  # TODO: Fix resource endpoints

    return mcp
