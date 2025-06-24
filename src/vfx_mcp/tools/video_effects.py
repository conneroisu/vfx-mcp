"""Video effects and filters: speed changes, filters, and thumbnails.

This module provides advanced video manipulation tools including visual filters,
speed changes, and thumbnail generation. Supports a wide range of effects from
basic color adjustments to artistic filters like sepia, blur, and sharpening.

Supported filters:
    - brightness: Adjust video brightness (0.0-2.0)
    - contrast: Adjust video contrast (0.0-2.0)
    - saturation: Adjust color saturation (0.0-2.0)
    - hflip: Flip video horizontally
    - grayscale: Convert to grayscale
    - sepia: Apply sepia tone effect
    - blur: Apply gaussian blur
    - sharpen: Apply unsharp mask sharpening
    - vintage: Apply vintage color grading
    - scale: Resize video with specific dimensions

Example:
    Apply a blur effect to a video:

        await apply_filter(
            input_path="input.mp4",
            output_path="blurred.mp4",
            filter="blur",
            strength=1.5
        )
"""

import ffmpeg
from fastmcp import Context, FastMCP

from ..core import (
    create_standard_output,
    handle_ffmpeg_error,
    log_operation,
    validate_filter_name,
    validate_range,
)


def register_video_effects_tools(
    mcp: FastMCP,
) -> None:
    """Register video effects tools with the MCP server.

    Adds advanced video manipulation capabilities including visual filters,
    speed changes, and thumbnail generation to the provided FastMCP server.

    Args:
        mcp: The FastMCP server instance to register tools with.

    Returns:
        None
    """

    @mcp.tool
    async def apply_filter(
        input_path: str,
        output_path: str,
        filter: str,
        strength: float = 1.0,
        ctx: Context | None = None,
    ) -> str:
        """Apply visual effects filter to a video.

        Applies various visual filters to enhance or stylize video content.
        Filter strength can be adjusted to control the intensity of the effect.

        Available filters:
            - brightness: Brightens or darkens the video (0.1-3.0)
            - contrast: Adjusts contrast levels (0.1-3.0)
            - saturation: Controls color saturation (0.1-3.0)
            - hflip: Horizontally flips the video (strength ignored)
            - grayscale: Converts to grayscale based on strength (0.0-1.0)
            - sepia: Applies sepia tone effect (0.1-1.0)
            - blur: Applies gaussian blur (strength controls radius)
            - sharpen: Applies unsharp mask sharpening (0.1-3.0)
            - vintage: Applies vintage color grading
            - scale=WxH: Resizes to specific dimensions

        Args:
            input_path: Path to the input video file.
            output_path: Path where the filtered video will be saved.
            filter: Name of the filter to apply. See available filters above.
            strength: Filter intensity (0.1 to 3.0). 1.0 = normal strength.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating filter was applied and video saved.

        Raises:
            ValueError: If filter name or strength is invalid.
            RuntimeError: If ffmpeg encounters an error during processing.

        Example:
            Apply a moderate blur effect:

                result = await apply_filter(
                    input_path="input.mp4",
                    output_path="blurred.mp4",
                    filter="blur",
                    strength=1.5
                )
        """
        validate_filter_name(filter)
        validate_range(strength, 0.1, 3.0, "Filter strength")

        await log_operation(
            ctx,
            f"Applying {filter} filter with strength {strength}",
        )

        try:
            stream = ffmpeg.input(input_path)

            # Apply different filters based on name
            if filter == "blur":
                # Apply gaussian blur with strength controlling the blur radius
                blur_radius = max(0.5, min(strength * 5, 10))  # Scale strength
                stream = ffmpeg.filter(stream, "gblur", sigma=blur_radius)
            elif filter == "brightness":
                stream = ffmpeg.filter(
                    stream,
                    "eq",
                    brightness=strength - 1,
                )
            elif filter == "contrast":
                stream = ffmpeg.filter(
                    stream,
                    "eq",
                    contrast=strength,
                )
            elif filter == "saturation":
                stream = ffmpeg.filter(
                    stream,
                    "eq",
                    saturation=strength,
                )
            elif filter == "vintage":
                # Apply vintage effect using color correction
                stream = ffmpeg.filter(
                    stream,
                    "eq",
                    brightness=0.1 * strength,
                    contrast=1.2 * strength,
                    saturation=0.7 * strength,
                )
            elif filter == "sepia":
                sepia_strength = min(strength, 1.0)
                stream = ffmpeg.filter(
                    stream,
                    "colorchannelmixer",
                    rr=0.393 * sepia_strength,
                    rg=0.769 * sepia_strength,
                    rb=0.189 * sepia_strength,
                )
            elif filter == "grayscale":
                stream = ffmpeg.filter(stream, "hue", s=1 - strength)
            elif filter == "hflip":
                stream = ffmpeg.filter(stream, "hflip")
            elif filter == "sharpen":
                # Apply unsharp mask for sharpening with strength controlling amount
                sharpen_amount = max(0.1, min(strength, 3.0))  # Scale strength
                stream = ffmpeg.filter(
                    stream,
                    "unsharp",
                    luma_msize_x=5,
                    luma_msize_y=5,
                    luma_amount=sharpen_amount,
                )
            elif filter.startswith("scale="):
                # Handle scale filter with parameters like scale=640:360
                scale_params = filter.split("=")[1]
                width, height = scale_params.split(":")
                stream = ffmpeg.filter(
                    stream,
                    "scale",
                    int(width),
                    int(height),
                )

            output = create_standard_output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"{filter.title()} filter applied and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def change_speed(
        input_path: str,
        output_path: str,
        speed: float,
        ctx: Context | None = None,
    ) -> str:
        """Change the playback speed of a video.

        Adjusts video playback speed while maintaining audio synchronization.
        Values greater than 1.0 speed up the video, values less than 1.0 slow it down.

        The function handles FFmpeg's atempo filter limitations (0.5-2.0 range) by
        automatically chaining multiple atempo filters for extreme speed changes.
        This ensures smooth audio processing at any speed within the supported range.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the speed-adjusted video will be saved.
            speed: Speed multiplier (0.1 to 10.0). Examples:
                - 0.5 = half speed (slow motion)
                - 1.0 = normal speed (no change)
                - 2.0 = double speed (fast forward)
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating speed was changed and video saved.

        Raises:
            ValueError: If speed factor is out of valid range or zero/negative.
            RuntimeError: If ffmpeg encounters an error during processing.

        Example:
            Create slow motion at half speed:

                result = await change_speed(
                    input_path="normal.mp4",
                    output_path="slow_motion.mp4",
                    speed=0.5
                )
        """
        # Custom validation for speed - must be positive
        if speed <= 0:
            raise ValueError("Speed factor must be greater than 0")

        validate_range(speed, 0.1, 10.0, "Speed factor")

        await log_operation(
            ctx,
            f"Changing video speed by {speed}x",
        )

        try:
            stream = ffmpeg.input(input_path)

            # Apply speed change to video and audio
            video_stream = ffmpeg.filter(
                stream["v"],
                "setpts",
                f"PTS/{speed}",
            )

            # Handle atempo filter limitations (0.5-2.0 range)
            # For speeds outside this range, chain multiple atempo filters
            audio_stream = stream["a"]
            current_speed = speed

            while current_speed > 2.0:
                audio_stream = ffmpeg.filter(audio_stream, "atempo", 2.0)
                current_speed /= 2.0

            while current_speed < 0.5:
                audio_stream = ffmpeg.filter(audio_stream, "atempo", 0.5)
                current_speed /= 0.5

            if current_speed != 1.0:
                audio_stream = ffmpeg.filter(audio_stream, "atempo", current_speed)

            output = ffmpeg.output(
                video_stream,
                audio_stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
            )
            ffmpeg.run(output, overwrite_output=True)

            speed_desc = "faster" if speed > 1.0 else "slower"
            return (
                f"Video speed changed {speed_desc} ({speed}x) and saved to "
                f"{output_path}"
            )
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def generate_thumbnail(
        input_path: str,
        output_path: str,
        timestamp: float = 2.5,
        width: int | None = None,
        height: int | None = None,
        ctx: Context | None = None,
    ) -> str:
        """Generate a thumbnail image from a video.

        Extracts a single frame from the video at the specified timestamp and
        resizes it to create a thumbnail image.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the thumbnail image will be saved.
            timestamp: Time in seconds to extract frame from (0.0 to video duration).
            width: Thumbnail width in pixels (50 to 1920). If None, uses original width.
            height: Thumbnail height in pixels (50 to 1080). If None, uses original.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating thumbnail was generated and saved.

        Raises:
            ValueError: If dimensions are out of valid ranges.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        if width is not None:
            validate_range(width, 50, 1920, "Width")
        if height is not None:
            validate_range(height, 50, 1080, "Height")

        size_desc = (
            "original size"
            if width is None and height is None
            else f"{width or 'auto'}x{height or 'auto'}"
        )
        await log_operation(
            ctx,
            f"Generating {size_desc} thumbnail at {timestamp}s",
        )

        try:
            stream = ffmpeg.input(input_path, ss=timestamp)

            # Only apply scaling if dimensions are specified
            if width is not None or height is not None:
                # Use -1 for auto-scaling when one dimension is not specified
                scale_width = width if width is not None else -1
                scale_height = height if height is not None else -1
                stream = ffmpeg.filter(stream, "scale", scale_width, scale_height)

            output = ffmpeg.output(stream, output_path, vframes=1)
            ffmpeg.run(output, overwrite_output=True)
            return f"Thumbnail generated and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
