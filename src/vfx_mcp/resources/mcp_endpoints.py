"""MCP resource endpoints for tool discovery and video metadata."""

import json
from pathlib import Path

from fastmcp import FastMCP

from ..core import get_video_metadata


def register_resource_endpoints(
    mcp: FastMCP,
) -> None:
    """Register MCP resource endpoints with the server."""

    @mcp.resource("videos://list")
    async def list_videos_resource() -> str:
        """List available video files in common directories."""
        video_extensions = {
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".wmv",
            ".flv",
            ".webm",
        }
        video_files = []

        # Search common video directories
        search_paths = [
            Path.cwd(),
            Path.home() / "Videos",
            Path.home() / "Movies",
            Path.home() / "Desktop",
        ]

        for search_path in search_paths:
            if search_path.exists():
                for file_path in search_path.rglob("*"):
                    if (
                        file_path.is_file()
                        and file_path.suffix.lower() in video_extensions
                    ):
                        video_files.append(file_path.name)

        return json.dumps(
            {
                "videos": video_files[:100],  # Limit to first 100 files
                "total_found": len(video_files),
            },
            indent=2,
        )

    @mcp.resource("videos://{filename}/metadata")
    async def video_metadata_resource(filename: str) -> str:
        """Get detailed metadata for a specific video file."""
        try:
            metadata = get_video_metadata(filename)
            return json.dumps(metadata, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    @mcp.resource("tools://advanced/{category}")
    async def advanced_tools_resource(category: str = "all") -> str:
        """List advanced VFX tools with descriptions and capabilities."""
        advanced_tools = [
            {
                "name": "create_video_slideshow",
                "purpose": "Create slideshow videos from image sequences",
                "key_features": [
                    "Customizable transition effects",
                    "Audio track synchronization",
                    "Variable image duration timing",
                    "Ken Burns pan/zoom effects",
                ],
                "example_use": "Transform photo albums into dynamic video "
                "presentations",
            },
            {
                "name": "create_green_screen_effect",
                "purpose": "Remove green/blue screen and replace with custom "
                "backgrounds",
                "key_features": [
                    "Advanced chroma key compositing",
                    "Adjustable similarity and blend parameters",
                    "Color spill reduction",
                    "Support for multiple key colors",
                ],
                "example_use": "Create professional composited videos with "
                "custom backgrounds",
            },
            # Add more tools as needed
        ]

        return json.dumps(
            {
                "advanced_tools": advanced_tools,
                "total_tools": len(advanced_tools),
                "categories": [
                    "compositing",
                    "effects",
                    "analysis",
                    "automation",
                ],
            },
            indent=2,
        )
