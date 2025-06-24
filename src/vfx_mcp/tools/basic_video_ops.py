"""Basic video editing operations: trim, resize, concatenate, and info.

This module provides fundamental video editing tools for trimming segments,
resizing videos, concatenating multiple files, and retrieving video metadata.
All operations use FFmpeg for processing and include comprehensive error handling.

Example:
    Register tools with MCP server:

        mcp = FastMCP('video-editor')
        register_basic_video_tools(mcp)
"""

from typing import Any

import ffmpeg
from fastmcp import Context, FastMCP

from ..core import (
    create_standard_output,
    get_video_metadata,
    handle_ffmpeg_error,
    log_operation,
    validate_range,
)


def register_basic_video_tools(
    mcp: FastMCP,
) -> None:
    """Register basic video editing tools with the MCP server.

    Adds fundamental video editing operations including trim, resize,
    concatenate, get_video_info, and image_to_video functions to the
    provided FastMCP server instance.

    Args:
        mcp: The FastMCP server instance to register tools with.

    Returns:
        None
    """

    @mcp.tool
    async def trim_video(
        input_path: str,
        output_path: str,
        start_time: float,
        duration: float | None = None,
        ctx: Context | None = None,
    ) -> str:
        """Extract a segment from a video.

        Extracts a portion of a video file starting at the specified time.
        If duration is not provided, extracts from start_time to the end of the video.
        Uses copy mode for fast processing without re-encoding.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the trimmed video will be saved.
            start_time: Start time in seconds from which to begin extraction.
            duration: Duration in seconds to extract. If None, extracts to end.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating the video was trimmed and saved.

        Raises:
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        await log_operation(
            ctx,
            f"Trimming video from {start_time}s"
            + (f" for {duration}s" if duration else " to end"),
        )

        try:
            stream = ffmpeg.input(input_path, ss=start_time)
            if duration:
                stream = ffmpeg.output(
                    stream,
                    output_path,
                    t=duration,
                    c="copy",
                )
            else:
                stream = ffmpeg.output(stream, output_path, c="copy")

            ffmpeg.run(stream, overwrite_output=True)
            return f"Video trimmed successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def get_video_info(
        video_path: str,
    ) -> dict[str, Any]:
        """Get detailed video metadata.

        Analyzes a video file and extracts comprehensive metadata including
        format information, video stream properties, and audio stream properties.
        Uses ffmpeg.probe() to gather the information.

        Args:
            video_path: Path to the video file to analyze.

        Returns:
            A dictionary containing video metadata with detailed information
            about format, video stream, and audio stream properties.

        Raises:
            RuntimeError: If ffmpeg encounters an error during analysis.
        """
        return get_video_metadata(video_path)

    @mcp.tool
    async def resize_video(
        input_path: str,
        output_path: str,
        width: int | None = None,
        height: int | None = None,
        scale: float | None = None,
        ctx: Context | None = None,
    ) -> str:
        """Resize a video to specified dimensions or scale factor.

        Resizes a video using one of three methods: specific width (maintaining
        aspect ratio), specific height (maintaining aspect ratio), or uniform
        scaling by a factor. Exactly one parameter must be provided.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the resized video will be saved.
            width: Target width in pixels. Height will be calculated automatically.
            height: Target height in pixels. Width will be calculated automatically.
            scale: Scaling factor (0.1 to 10.0). 1.0 = original size.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating the video was resized and saved.

        Raises:
            ValueError: If parameter constraints are not met.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        param_count = sum(x is not None for x in [width, height, scale])
        if param_count != 1:
            raise ValueError("Provide exactly one: width, height, or scale")

        try:
            stream = ffmpeg.input(input_path)

            if scale:
                validate_range(
                    scale,
                    0.1,
                    10.0,
                    "Scale factor",
                )
                stream = ffmpeg.filter(
                    stream,
                    "scale",
                    f"iw*{scale}",
                    f"ih*{scale}",
                )
                await log_operation(
                    ctx,
                    f"Resizing video by {scale}x",
                )
            elif width:
                stream = ffmpeg.filter(stream, "scale", width, -1)
                await log_operation(
                    ctx,
                    f"Resizing video to width {width}px",
                )
            else:  # height
                stream = ffmpeg.filter(stream, "scale", -1, height)
                await log_operation(
                    ctx,
                    f"Resizing video to height {height}px",
                )

            output = create_standard_output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"Video resized and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def concatenate_videos(
        input_paths: list[str],
        output_path: str,
        ctx: Context | None = None,
    ) -> str:
        """Concatenate multiple videos into a single video.

        Joins multiple video files into one continuous video. All input videos
        should have the same resolution, frame rate, and codec for best results.
        Videos with different properties will be automatically converted.

        Args:
            input_paths: List of paths to video files to concatenate (min 2).
            output_path: Path where the concatenated video will be saved.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating videos were concatenated and saved.

        Raises:
            ValueError: If fewer than 2 videos are provided.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        if len(input_paths) < 2:
            raise ValueError("At least 2 videos required for concatenation")

        await log_operation(
            ctx,
            f"Concatenating {len(input_paths)} videos",
        )

        try:
            inputs = [ffmpeg.input(path) for path in input_paths]
            # Concatenate without specifying stream counts - let ffmpeg auto-detect
            stream = ffmpeg.concat(*inputs)
            output = create_standard_output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"Videos concatenated successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def image_to_video(
        image_path: str,
        output_path: str,
        duration: float,
        framerate: int = 30,
        ctx: Context | None = None,
    ) -> str:
        """Create a video from a static image for a specified duration.

        Converts a static image into a video by displaying the image for the
        specified duration. The output will be a video file with the given
        framerate showing the same image throughout.

        Args:
            image_path: Path to the input image file (supports common formats).
            output_path: Path where the video will be saved.
            duration: Duration of the video in seconds.
            framerate: Framerate of the output video (default: 30 fps).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating the video was created and saved.

        Raises:
            ValueError: If duration is not positive or framerate is invalid.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        if duration <= 0:
            raise ValueError("Duration must be positive")

        if framerate <= 0 or framerate > 120:
            raise ValueError("Framerate must be between 1 and 120 fps")

        await log_operation(
            ctx,
            f"Creating {duration}s video from image at {framerate} fps",
        )

        try:
            stream = ffmpeg.input(
                image_path,
                loop=1,
                t=duration,
                framerate=framerate,
            )
            output = create_standard_output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"Video created successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
