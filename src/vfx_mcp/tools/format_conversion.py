"""Format and codec conversion tools."""

import ffmpeg
from fastmcp import Context, FastMCP

from ..core import (
    handle_ffmpeg_error,
    log_operation,
)


def register_format_conversion_tools(
    mcp: FastMCP,
) -> None:
    """Register format conversion tools with the MCP server."""

    @mcp.tool
    async def convert_format(
        input_path: str,
        output_path: str,
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
                output_kwargs["video_bitrate"] = (
                    video_bitrate
                )

            output = ffmpeg.output(
                stream,
                output_path,
                **output_kwargs,
            )
            ffmpeg.run(
                output, overwrite_output=True
            )
            return f"Format converted successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
