"""Format and codec conversion tools.

This module provides comprehensive video and audio format conversion capabilities
with support for various containers, codecs, and quality settings. Enables
conversion between different video formats while maintaining quality control.

Supported formats:
    - mp4: MPEG-4 container (widely compatible)
    - avi: Audio Video Interleave (legacy support)
    - mkv: Matroska container (open source, feature-rich)
    - webm: WebM container (web optimized)

Common codec combinations:
    - H.264 + AAC: Best compatibility (mp4, mkv)
    - H.265 + AAC: Higher compression (mp4, mkv)
    - VP9 + Vorbis: Open source (webm, mkv)

Example:
    Convert to high-quality H.265:

        await convert_format(
            input_path="input.avi",
            output_path="output.mp4",
            format="mp4",
            video_codec="libx265",
            video_bitrate="2M"
        )
"""

import ffmpeg
from fastmcp import Context, FastMCP

from ..core import (
    handle_ffmpeg_error,
    log_operation,
)


def register_format_conversion_tools(
    mcp: FastMCP,
) -> None:
    """Register format conversion tools with the MCP server.

    Adds video and audio format conversion capabilities with support for
    various containers, codecs, and quality settings to the FastMCP server.

    Args:
        mcp: The FastMCP server instance to register tools with.

    Returns:
        None
    """

    @mcp.tool
    async def convert_format(
        input_path: str,
        output_path: str,
        format: str | None = None,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        video_bitrate: str | None = None,
        audio_bitrate: str = "128k",
        ctx: Context | None = None,
    ) -> str:
        """Convert video format and adjust encoding settings.

        Converts a video file to a different format with customizable codec
        and bitrate settings for both video and audio streams.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the converted video will be saved.
            format: Target format ("mp4", "avi", "mkv", "webm"). If specified,
                   auto-selects appropriate codecs.
            video_codec: Video codec ("libx264", "libx265", "libvpx-vp9", etc.).
            audio_codec: Audio codec ("aac", "mp3", "libvorbis", etc.).
            video_bitrate: Video bitrate (e.g., "1M", "2.5M"). If None, auto.
            audio_bitrate: Audio bitrate (e.g., "128k", "192k", "320k").
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating format was converted and video saved.

        Raises:
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        # Auto-select codecs based on format if specified
        if format:
            format_codecs = {
                "mp4": {"video": "libx264", "audio": "aac"},
                "avi": {"video": "libx264", "audio": "mp3"},
                "mkv": {"video": "libx264", "audio": "aac"},
                "webm": {"video": "libvpx-vp9", "audio": "libvorbis"},
                "mov": {"video": "libx264", "audio": "aac"},
            }

            if format.lower() in format_codecs:
                selected = format_codecs[format.lower()]
                video_codec = selected["video"]
                audio_codec = selected["audio"]

        await log_operation(
            ctx,
            f"Converting format: {video_codec}/{audio_codec} "
            f"(vbr: {video_bitrate or 'auto'}, abr: {audio_bitrate})",
        )

        try:
            stream = ffmpeg.input(input_path)

            output_kwargs = {
                "vcodec": video_codec,
                "acodec": audio_codec,
                "audio_bitrate": audio_bitrate,
            }

            if video_bitrate:
                output_kwargs["video_bitrate"] = video_bitrate

            output = ffmpeg.output(
                stream,
                output_path,
                **output_kwargs,
            )
            ffmpeg.run(output, overwrite_output=True)
            return f"Format converted successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
