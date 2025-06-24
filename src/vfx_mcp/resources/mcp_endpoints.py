"""MCP resource endpoints for tool discovery and video metadata."""

import json
from pathlib import Path

from fastmcp import FastMCP

from ..core import get_video_metadata


def register_resource_endpoints(
    mcp: FastMCP,
) -> None:
    """Register MCP resource endpoints with the server."""

    @mcp.resource("file://videos/list/{format}")
    async def list_videos_resource(uri: str, format: str = "json") -> str:
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
                        video_files.append(
                            {
                                "name": file_path.name,
                                "path": str(file_path),
                                "size": file_path.stat().st_size,
                            }
                        )

        return json.dumps(
            {
                "videos": video_files[:100],  # Limit to first 100 files
                "total_found": len(video_files),
            },
            indent=2,
        )

    @mcp.resource("file://video/metadata/{path}")
    async def video_metadata_resource(uri: str, path: str) -> str:
        """Get detailed metadata for a specific video file."""
        # Extract file path from URI
        if "path=" in uri:
            file_path = uri.split("path=")[1]
            try:
                metadata = get_video_metadata(file_path)
                return json.dumps(metadata, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        else:
            return json.dumps(
                {
                    "error": "No file path provided. Use: file://video/metadata?path=/path/to/video.mp4"
                },
                indent=2,
            )

    @mcp.resource("file://tools/advanced/{category}")
    async def advanced_tools_resource(uri: str, category: str = "all") -> str:
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
