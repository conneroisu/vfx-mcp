"""Audio processing tools: extraction, mixing, and enhancement."""

import ffmpeg
from fastmcp import Context, FastMCP

from ..core import (
    handle_ffmpeg_error,
    log_operation,
    validate_range,
)


def register_audio_tools(mcp: FastMCP) -> None:
    """Register audio processing tools with the MCP server."""

    @mcp.tool
    async def extract_audio(
        input_path: str,
        output_path: str,
        format: str = "mp3",
        bitrate: str = "192k",
        ctx: Context | None = None,
    ) -> str:
        """Extract audio from a video file.

        Extracts the audio track from a video file and saves it as a separate
        audio file. Supports various output formats and quality settings.

        Args:
            input_path: Path to the input video file.
            output_path: Path where the extracted audio will be saved.
            format: Output audio format ("mp3", "wav", "aac", "flac", "ogg").
            bitrate: Audio bitrate (e.g., "128k", "192k", "320k").
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating audio was extracted and saved.

        Raises:
            ValueError: If format is not supported.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        supported_formats = [
            "mp3",
            "wav",
            "aac",
            "flac",
            "ogg",
        ]
        if format not in supported_formats:
            raise ValueError(f"Format must be one of: {', '.join(supported_formats)}")

        await log_operation(
            ctx,
            f"Extracting audio as {format} at {bitrate}",
        )

        try:
            stream = ffmpeg.input(input_path)
            if format == "wav":
                output = ffmpeg.output(
                    stream,
                    output_path,
                    acodec="pcm_s16le",
                )
            else:
                codec_map = {
                    "mp3": "libmp3lame",
                    "aac": "aac",
                    "flac": "flac",
                    "ogg": "libvorbis",
                }
                output = ffmpeg.output(
                    stream,
                    output_path,
                    acodec=codec_map[format],
                    audio_bitrate=bitrate,
                )

            ffmpeg.run(output, overwrite_output=True)
            return f"Audio extracted successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def add_audio(
        video_path: str,
        audio_path: str,
        output_path: str,
        replace: bool = True,
        audio_volume: float = 1.0,
        ctx: Context | None = None,
    ) -> str:
        """Add or replace audio in a video file.

        Combines a video file with an audio file. Can either replace the existing
        audio track or mix the new audio with the existing audio.

        Args:
            video_path: Path to the input video file.
            audio_path: Path to the audio file to add.
            output_path: Path where the output video will be saved.
            replace: Whether to replace existing audio (True) or mix (False).
            audio_volume: Volume level for the new audio (0.0 to 2.0).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating audio was added and video saved.

        Raises:
            ValueError: If parameters are out of valid ranges.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(audio_volume, 0.0, 2.0, "Audio volume")

        mode = "replace" if replace else "mix"
        await log_operation(
            ctx,
            f"Adding audio to video (mode: {mode}, volume: {audio_volume})",
        )

        try:
            video_input = ffmpeg.input(video_path)
            audio_input = ffmpeg.input(audio_path)

            if replace:
                # Replace existing audio
                if audio_volume != 1.0:
                    audio_input = ffmpeg.filter(
                        audio_input,
                        "volume",
                        audio_volume,
                    )
                output = ffmpeg.output(
                    video_input,
                    audio_input,
                    output_path,
                    vcodec="copy",
                    acodec="aac",
                    shortest=None,
                )
            else:  # mix
                # Mix with existing audio
                if audio_volume != 1.0:
                    audio_input = ffmpeg.filter(
                        audio_input,
                        "volume",
                        audio_volume,
                    )

                mixed_audio = ffmpeg.filter(
                    [video_input, audio_input],
                    "amix",
                    inputs=2,
                    duration="shortest",
                )
                output = ffmpeg.output(
                    video_input,
                    mixed_audio,
                    output_path,
                    vcodec="copy",
                    acodec="aac",
                )

            ffmpeg.run(output, overwrite_output=True)
            return f"Audio {mode}d successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
