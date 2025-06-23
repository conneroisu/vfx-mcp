#!/usr/bin/env python3
"""
VFX MCP Server - Video editing server using FastMCP and ffmpeg-python
"""

import json
import os
from pathlib import Path
from typing import Any

import ffmpeg
from fastmcp import Context, FastMCP

# Initialize the MCP server
mcp = FastMCP(
    "vfx-mcp",
    description="Video editing MCP server with ffmpeg-python",
)


# === Basic Video Operations ===


@mcp.tool
async def trim_video(
    input_path: str,
    output_path: str,
    start_time: float,
    duration: float | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Extract a segment from a video.

    Args:
        input_path: Path to input video file
        output_path: Path for output video file
        start_time: Start time in seconds
        duration: Duration in seconds (if not specified, trims to end)
        ctx: MCP context for progress reporting
    """
    if ctx:
        await ctx.info(
            f"Trimming video from {start_time}s"
            + (
                f" for {duration}s"
                if duration
                else " to end"
            )
        )

    try:
        stream = ffmpeg.input(
            input_path, ss=start_time
        )
        if duration:
            stream = ffmpeg.output(
                stream,
                output_path,
                t=duration,
                c="copy",
            )
        else:
            stream = ffmpeg.output(
                stream, output_path, c="copy"
            )

        ffmpeg.run(stream, overwrite_output=True)
        return f"Video trimmed successfully and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def get_video_info(
    video_path: str,
) -> dict[str, Any]:
    """
    Get detailed video metadata.

    Args:
        video_path: Path to video file

    Returns:
        Video metadata including duration, resolution, codec, bitrate, fps, etc.
    """
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next(
            (
                stream
                for stream in probe["streams"]
                if stream["codec_type"] == "video"
            ),
            None,
        )
        audio_stream = next(
            (
                stream
                for stream in probe["streams"]
                if stream["codec_type"] == "audio"
            ),
            None,
        )

        info = {
            "filename": os.path.basename(
                video_path
            ),
            "format": probe["format"][
                "format_name"
            ],
            "duration": float(
                probe["format"]["duration"]
            ),
            "size": int(probe["format"]["size"]),
            "bit_rate": int(
                probe["format"]["bit_rate"]
            ),
        }

        if video_stream:
            info["video"] = {
                "codec": video_stream[
                    "codec_name"
                ],
                "width": video_stream["width"],
                "height": video_stream["height"],
                "fps": eval(
                    video_stream["r_frame_rate"]
                ),
                "bit_rate": video_stream.get(
                    "bit_rate", "N/A"
                ),
            }

        if audio_stream:
            info["audio"] = {
                "codec": audio_stream[
                    "codec_name"
                ],
                "sample_rate": audio_stream[
                    "sample_rate"
                ],
                "channels": audio_stream[
                    "channels"
                ],
                "bit_rate": audio_stream.get(
                    "bit_rate", "N/A"
                ),
            }

        return info
    except ffmpeg.Error as e:
        raise RuntimeError(
            f"Error getting video info: {str(e)}"
        ) from e


@mcp.tool
async def resize_video(
    input_path: str,
    output_path: str,
    width: int | None = None,
    height: int | None = None,
    scale: float | None = None,
    ctx: Context | None = None,
) -> str:
    """
    Change video resolution.

    Args:
        input_path: Path to input video file
        output_path: Path for output video file
        width: Target width (maintains aspect ratio if height not specified)
        height: Target height (maintains aspect ratio if width not specified)
        scale: Scale factor (e.g., 0.5 for half size)
        ctx: MCP context for progress reporting
    """
    if not any([width, height, scale]):
        raise ValueError(
            "Must specify either width, height, or scale"
        )

    if ctx:
        await ctx.info("Resizing video...")

    try:
        stream = ffmpeg.input(input_path)

        if scale:
            stream = ffmpeg.filter(
                stream,
                "scale",
                f"iw*{scale}",
                f"ih*{scale}",
            )
        elif width and height:
            stream = ffmpeg.filter(
                stream, "scale", width, height
            )
        elif width:
            stream = ffmpeg.filter(
                stream, "scale", width, -1
            )
        else:  # height only
            stream = ffmpeg.filter(
                stream, "scale", -1, height
            )

        stream = ffmpeg.output(
            stream, output_path
        )
        ffmpeg.run(stream, overwrite_output=True)

        return f"Video resized and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def concatenate_videos(
    input_paths: list[str],
    output_path: str,
    ctx: Context | None = None,
) -> str:
    """
    Join multiple videos together.

    Args:
        input_paths: List of video file paths to concatenate
        output_path: Path for output video file
        ctx: MCP context for progress reporting
    """
    if len(input_paths) < 2:
        raise ValueError(
            "Need at least 2 videos to concatenate"
        )

    if ctx:
        await ctx.info(
            f"Concatenating {len(input_paths)} videos..."
        )

    try:
        # Create a temporary file list for concat
        list_file = (
            Path(output_path).parent
            / "concat_list.txt"
        )
        with open(list_file, "w") as f:
            for path in input_paths:
                f.write(
                    f"file '{os.path.abspath(path)}'\n"
                )

        stream = ffmpeg.input(
            str(list_file),
            format="concat",
            safe=0,
        )
        stream = ffmpeg.output(
            stream, output_path, c="copy"
        )
        ffmpeg.run(stream, overwrite_output=True)

        # Clean up
        list_file.unlink()

        return f"Videos concatenated and saved to {output_path}"
    except Exception as e:
        if ctx:
            await ctx.error(
                f"Error concatenating videos: {str(e)}"
            )
        raise RuntimeError(
            f"Error concatenating videos: {str(e)}"
        ) from e


# === Resource Handlers ===


@mcp.resource("videos://list")
async def list_videos() -> str:
    """List available video files in the current directory."""
    video_extensions = [
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".webm",
        ".flv",
        ".wmv",
    ]
    videos = []

    for file in Path(".").iterdir():
        if (
            file.is_file()
            and file.suffix.lower()
            in video_extensions
        ):
            videos.append(str(file))

    return json.dumps(
        {"videos": sorted(videos)}, indent=2
    )


@mcp.resource("videos://{filename}/metadata")
async def get_video_metadata(
    filename: str,
) -> str:
    """Get metadata for a specific video file."""
    try:
        info = await get_video_info(filename)
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# === Main Entry Point ===


def main():
    """Run the VFX MCP server."""
    import sys

    # Default to stdio transport
    transport = os.environ.get(
        "MCP_TRANSPORT", "stdio"
    )

    if transport == "stdio":
        print(
            "Starting VFX MCP server on stdio...",
            file=sys.stderr,
        )
        mcp.run()
    elif transport == "sse":
        host = os.environ.get(
            "MCP_HOST", "localhost"
        )
        port = int(
            os.environ.get("MCP_PORT", "8000")
        )
        print(
            f"Starting VFX MCP server on {host}:{port} (SSE)...",
            file=sys.stderr,
        )
        mcp.run(
            transport="sse", host=host, port=port
        )
    else:
        print(
            f"Unknown transport: {transport}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
