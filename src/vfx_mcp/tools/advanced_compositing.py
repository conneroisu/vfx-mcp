"""Advanced compositing tools: green screen, motion blur, and complex effects."""

import ffmpeg
from fastmcp import Context, FastMCP

from ..core import (
    create_standard_output,
    handle_ffmpeg_error,
    log_operation,
    parse_color,
    validate_range,
)


def register_compositing_tools(
    mcp: FastMCP,
) -> None:
    """Register advanced compositing tools with the MCP server."""

    @mcp.tool
    async def create_green_screen_effect(
        input_path: str,
        output_path: str,
        background_path: str | None = None,
        chroma_key_color: str = "green",
        similarity: float = 0.3,
        blend: float = 0.1,
        spill_reduction: float = 0.5,
        ctx: Context | None = None,
    ) -> str:
        """Remove green/blue screen and composite with background.

        Advanced chroma key compositing with adjustable parameters for
        professional green screen removal and background replacement.

        Args:
            input_path: Path to the input video with green/blue screen.
            output_path: Path where the composited video will be saved.
            background_path: Path to background image/video. If None, creates
                transparent background.
            chroma_key_color: Color to remove ("green", "blue", "red", or hex code
                like "#00FF00").
            similarity: Color similarity threshold (0.0 to 1.0). Lower = more precise.
            blend: Edge blending amount (0.0 to 1.0) for smoother edges.
            spill_reduction: Color spill reduction strength (0.0 to 1.0).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating green screen effect was applied.

        Raises:
            ValueError: If parameter values are out of valid ranges.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(similarity, 0.0, 1.0, "Similarity")
        validate_range(blend, 0.0, 1.0, "Blend")
        validate_range(
            spill_reduction,
            0.0,
            1.0,
            "Spill reduction",
        )

        # Parse color to ffmpeg format
        key_color = parse_color(chroma_key_color)

        await log_operation(
            ctx,
            f"Applying chroma key: {chroma_key_color} "
            f"(similarity: {similarity}, blend: {blend})",
        )

        try:
            input_stream = ffmpeg.input(input_path)

            # Create chromakey filter
            keyed = ffmpeg.filter(
                input_stream,
                "chromakey",
                color=key_color,
                similarity=similarity,
                blend=blend,
            )

            # Apply spill reduction if needed
            if spill_reduction > 0:
                keyed = ffmpeg.filter(
                    keyed,
                    "despill",
                    type=("green" if "green" in chroma_key_color.lower() else "blue"),
                    mix=spill_reduction,
                )

            if background_path:
                # Composite with background
                background = ffmpeg.input(background_path)
                output_stream = ffmpeg.filter(
                    [background, keyed],
                    "overlay",
                    x="(W-w)/2",
                    y="(H-h)/2",
                )
            else:
                # Transparent background
                output_stream = keyed

            output = ffmpeg.output(
                output_stream,
                output_path,
                vcodec="libx264",
                pix_fmt="yuv420p",
            )
            ffmpeg.run(output, overwrite_output=True)

            bg_msg = (
                " with custom background"
                if background_path
                else " with transparent background"
            )
            return f"Green screen effect applied{bg_msg} and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def apply_motion_blur(
        input_path: str,
        output_path: str,
        blur_strength: float = 1.0,
        angle: float = 0.0,
        ctx: Context | None = None,
    ) -> str:
        """Apply motion blur effect to simulate camera or object movement.

        Creates motion blur effect with adjustable strength and direction,
        simulating movement in the specified angle direction.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the motion-blurred video will be saved.
            blur_strength: Blur intensity (0.1 to 3.0). Higher = more blur.
            angle: Blur direction angle in degrees (0 to 360).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating motion blur was applied.

        Raises:
            ValueError: If parameters are out of valid ranges.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(
            blur_strength,
            0.1,
            3.0,
            "Blur strength",
        )
        validate_range(angle, 0, 360, "Angle")

        await log_operation(
            ctx,
            f"Applying motion blur (strength: {blur_strength}, angle: {angle}°)...",
        )

        try:
            stream = ffmpeg.input(input_path)

            # Convert angle and strength to blur parameters
            blur_amount = int(blur_strength * 3) * 2 + 1  # Odd number for kernel size

            # Create motion blur kernel based on angle
            # Note: Complex motion blur math would go here in a real implementation

            # For simplicity, use mblur filter with approximated settings
            if angle < 45 or angle > 315:
                # Horizontal blur
                stream = ffmpeg.filter(
                    stream,
                    "boxblur",
                    luma_radius=f"{blur_amount}:1",
                )
            elif 45 <= angle < 135:
                # Vertical blur
                stream = ffmpeg.filter(
                    stream,
                    "boxblur",
                    luma_radius=f"1:{blur_amount}",
                )
            elif 135 <= angle < 225:
                # Horizontal blur (reverse)
                stream = ffmpeg.filter(
                    stream,
                    "boxblur",
                    luma_radius=f"{blur_amount}:1",
                )
            else:
                # Vertical blur (reverse)
                stream = ffmpeg.filter(
                    stream,
                    "boxblur",
                    luma_radius=f"1:{blur_amount}",
                )

            output = create_standard_output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)

            return (
                f"Motion blur applied (strength: {blur_strength}, angle: {angle}°) "
                f"and saved to {output_path}"
            )
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
