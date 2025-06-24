"""Video effects and filters: speed changes, filters, and thumbnails."""

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
    """Register video effects tools with the MCP server."""

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

        Args:
            input_path: Path to the input video file.
            output_path: Path where the filtered video will be saved.
            filter: Name of the filter to apply.
            strength: Filter intensity (0.1 to 3.0). 1.0 = normal strength.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating filter was applied and video saved.

        Raises:
            ValueError: If filter name or strength is invalid.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_filter_name(filter)
        validate_range(
            strength, 0.1, 3.0, "Filter strength"
        )

        await log_operation(
            ctx,
            f"Applying {filter} filter with strength {strength}",
        )

        try:
            stream = ffmpeg.input(input_path)

            # Apply different filters based on name
            if filter == "blur":
                stream = ffmpeg.filter(
                    stream,
                    "boxblur",
                    luma_radius=strength,
                )
            elif filter == "sharpen":
                stream = ffmpeg.filter(
                    stream,
                    "unsharp",
                    luma_matrix_h_size=5,
                    luma_matrix_v_size=5,
                    luma_amount=strength,
                )
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
                stream = ffmpeg.filter(
                    stream,
                    "curves",
                    vintage=f"0.1*{strength}",
                )
            elif filter == "sepia":
                sepia_strength = min(
                    strength, 1.0
                )
                stream = ffmpeg.filter(
                    stream,
                    "colorchannelmixer",
                    rr=0.393 * sepia_strength,
                    rg=0.769 * sepia_strength,
                    rb=0.189 * sepia_strength,
                )
            elif filter == "grayscale":
                stream = ffmpeg.filter(
                    stream, "hue", s=1 - strength
                )
            elif filter == "hflip":
                stream = ffmpeg.filter(
                    stream, "hflip"
                )
            elif filter.startswith("scale="):
                # Handle scale filter with parameters like scale=640:360
                scale_params = filter.split("=")[
                    1
                ]
                width, height = (
                    scale_params.split(":")
                )
                stream = ffmpeg.filter(
                    stream,
                    "scale",
                    int(width),
                    int(height),
                )

            output = create_standard_output(
                stream, output_path
            )
            ffmpeg.run(
                output, overwrite_output=True
            )
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

        Adjusts video playback speed while maintaining audio pitch. Values greater
        than 1.0 speed up the video, values less than 1.0 slow it down.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the speed-adjusted video will be saved.
            speed: Speed multiplier (0.25 to 4.0). 1.0 = normal speed.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating speed was changed and video saved.

        Raises:
            ValueError: If speed factor is out of valid range.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(
            speed, 0.25, 4.0, "Speed factor"
        )

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
            audio_stream = ffmpeg.filter(
                stream["a"], "atempo", speed
            )

            output = ffmpeg.output(
                video_stream,
                audio_stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
            )
            ffmpeg.run(
                output, overwrite_output=True
            )

            speed_desc = (
                "faster"
                if speed > 1.0
                else "slower"
            )
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
        timestamp: float = 5.0,
        width: int = 320,
        height: int = 240,
        ctx: Context | None = None,
    ) -> str:
        """Generate a thumbnail image from a video.

        Extracts a single frame from the video at the specified timestamp and
        resizes it to create a thumbnail image.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the thumbnail image will be saved.
            timestamp: Time in seconds to extract frame from (0.0 to video duration).
            width: Thumbnail width in pixels (50 to 1920).
            height: Thumbnail height in pixels (50 to 1080).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating thumbnail was generated and saved.

        Raises:
            ValueError: If dimensions are out of valid ranges.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(width, 50, 1920, "Width")
        validate_range(height, 50, 1080, "Height")

        await log_operation(
            ctx,
            f"Generating {width}x{height} thumbnail at {timestamp}s",
        )

        try:
            stream = ffmpeg.input(
                input_path, ss=timestamp
            )
            stream = ffmpeg.filter(
                stream, "scale", width, height
            )
            output = ffmpeg.output(
                stream, output_path, vframes=1
            )
            ffmpeg.run(
                output, overwrite_output=True
            )
            return f"Thumbnail generated and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
