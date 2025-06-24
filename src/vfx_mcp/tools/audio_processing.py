"""Audio processing tools: extraction, mixing, and enhancement.

This module provides comprehensive audio processing capabilities including
audio extraction from video files, audio mixing, volume adjustment, and
fade effects. Supports multiple audio formats with quality control.

Supported audio formats:
    - mp3: MPEG Audio Layer III (lossy)
    - wav: Waveform Audio File Format (lossless)
    - aac: Advanced Audio Coding (lossy)
    - ogg: Ogg Vorbis (lossy, open source)
    - flac: Free Lossless Audio Codec (lossless)

Example:
    Extract high-quality audio from video:

        await extract_audio(
            input_path="video.mp4",
            output_path="audio.flac",
            format="flac"
        )
"""

import ffmpeg
from fastmcp import Context, FastMCP

from ..core import (
    handle_ffmpeg_error,
    log_operation,
    validate_range,
)


def register_audio_tools(mcp: FastMCP) -> None:
    """Register audio processing tools with the MCP server.

    Adds comprehensive audio manipulation capabilities including extraction,
    mixing, volume adjustment, and fade effects to the FastMCP server.

    Args:
        mcp: The FastMCP server instance to register tools with.

    Returns:
        None
    """

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
        audio file. Supports various output formats with intelligent codec selection
        and quality-based encoding for optimal results.

        Format-specific behavior:
            - wav: Uses PCM encoding (bitrate ignored, lossless)
            - mp3: Uses libmp3lame encoder with specified bitrate
            - aac: Uses AAC encoder with specified bitrate
            - flac: Uses FLAC encoder (bitrate ignored, lossless)
            - ogg: Uses libvorbis with quality-based encoding

        Args:
            input_path: Path to the input video file.
            output_path: Path where the extracted audio will be saved.
            format: Output audio format. Supported: "mp3", "wav", "aac", "flac", "ogg".
            bitrate: Audio bitrate (e.g., "128k", "192k", "320k").
                    Ignored for lossless formats (wav, flac).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating audio was extracted and saved.

        Raises:
            ValueError: If format is not supported.
            RuntimeError: If ffmpeg encounters an error during processing.

        Example:
            Extract high-quality MP3 audio:

                result = await extract_audio(
                    input_path="movie.mp4",
                    output_path="soundtrack.mp3",
                    format="mp3",
                    bitrate="320k"
                )
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

            # Extract only the audio stream
            audio_stream = stream['a']

            if format == "wav":
                output = ffmpeg.output(
                    audio_stream,
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

                output_kwargs = {
                    "acodec": codec_map[format],
                }

                # Handle bitrate differently for different formats
                if format == "ogg":
                    # libvorbis uses quality-based encoding (VBR) by default
                    # Use -q:a instead of bitrate for better compatibility
                    if bitrate:
                        # Convert bitrate to approximate quality level
                        bitrate_num = int(bitrate.rstrip('k'))
                        if bitrate_num <= 96:
                            output_kwargs["qscale:a"] = 0  # ~64kbps
                        elif bitrate_num <= 128:
                            output_kwargs["qscale:a"] = 2  # ~96kbps
                        elif bitrate_num <= 192:
                            output_kwargs["qscale:a"] = 4  # ~128kbps
                        elif bitrate_num <= 256:
                            output_kwargs["qscale:a"] = 6  # ~192kbps
                        else:
                            output_kwargs["qscale:a"] = 8  # ~256kbps+
                elif format not in ["flac"] and bitrate:
                    output_kwargs["audio_bitrate"] = bitrate

                output = ffmpeg.output(
                    audio_stream,
                    output_path,
                    **output_kwargs,
                )

            ffmpeg.run(output, overwrite_output=True)
            return f"Audio extracted successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def add_audio(
        input_path: str,
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
            input_path: Path to the input video file.
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
            video_input = ffmpeg.input(input_path)
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

    @mcp.tool
    async def adjust_audio_volume(
        input_path: str,
        output_path: str,
        volume: float,
        ctx: Context | None = None,
    ) -> str:
        """Adjust the volume level of an audio file.

        Changes the audio volume by a specified factor. Can be used to make
        audio louder or quieter without changing other properties.

        Args:
            input_path: Path to the input audio/video file.
            output_path: Path where the adjusted audio/video will be saved.
            volume: Volume adjustment factor (0.0 to 3.0). 1.0 = no change.
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating volume was adjusted and file saved.

        Raises:
            ValueError: If volume is out of valid range.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(volume, 0.0, 3.0, "Volume")

        await log_operation(
            ctx,
            f"Adjusting audio volume to {volume}x",
        )

        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, "volume", volume)
            output = ffmpeg.output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"Audio volume adjusted to {volume}x and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def mix_audio(
        audio1_path: str,
        audio2_path: str,
        output_path: str,
        audio1_volume: float = 1.0,
        audio2_volume: float = 1.0,
        ctx: Context | None = None,
    ) -> str:
        """Mix two audio files together.

        Combines two audio tracks into a single output file with adjustable
        volume levels for each input.

        Args:
            audio1_path: Path to the first audio file.
            audio2_path: Path to the second audio file.
            output_path: Path where the mixed audio will be saved.
            audio1_volume: Volume level for first audio (0.0 to 2.0).
            audio2_volume: Volume level for second audio (0.0 to 2.0).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating audio files were mixed and saved.

        Raises:
            ValueError: If volume levels are out of valid range.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(audio1_volume, 0.0, 2.0, "Audio1 volume")
        validate_range(audio2_volume, 0.0, 2.0, "Audio2 volume")

        await log_operation(
            ctx,
            f"Mixing audio files (vol1: {audio1_volume}, vol2: {audio2_volume})",
        )

        try:
            audio1 = ffmpeg.input(audio1_path)
            audio2 = ffmpeg.input(audio2_path)

            # Apply volume adjustments if needed
            if audio1_volume != 1.0:
                audio1 = ffmpeg.filter(audio1, "volume", audio1_volume)
            if audio2_volume != 1.0:
                audio2 = ffmpeg.filter(audio2, "volume", audio2_volume)

            # Mix the audio tracks
            mixed_audio = ffmpeg.filter(
                [audio1, audio2],
                "amix",
                inputs=2,
                duration="longest",
            )
            output = ffmpeg.output(mixed_audio, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"Audio files mixed successfully and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def audio_fade_in(
        input_path: str,
        output_path: str,
        duration: float,
        ctx: Context | None = None,
    ) -> str:
        """Apply a fade-in effect to audio.

        Gradually increases the audio volume from silence to full volume
        over the specified duration at the beginning of the audio.

        Args:
            input_path: Path to the input audio/video file.
            output_path: Path where the fade-in audio/video will be saved.
            duration: Duration of fade-in effect in seconds (0.1 to 10.0).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating fade-in was applied and file saved.

        Raises:
            ValueError: If duration is out of valid range.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(duration, 0.1, 10.0, "Fade duration")

        await log_operation(
            ctx,
            f"Applying {duration}s fade-in effect",
        )

        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, "afade", type="in", duration=duration)
            output = ffmpeg.output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"Fade-in effect applied ({duration}s) and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)

    @mcp.tool
    async def audio_fade_out(
        input_path: str,
        output_path: str,
        duration: float,
        ctx: Context | None = None,
    ) -> str:
        """Apply a fade-out effect to audio.

        Gradually decreases the audio volume from full volume to silence
        over the specified duration at the end of the audio.

        Args:
            input_path: Path to the input audio/video file.
            output_path: Path where the fade-out audio/video will be saved.
            duration: Duration of fade-out effect in seconds (0.1 to 10.0).
            ctx: MCP context for progress reporting and logging.

        Returns:
            Success message indicating fade-out was applied and file saved.

        Raises:
            ValueError: If duration is out of valid range.
            RuntimeError: If ffmpeg encounters an error during processing.
        """
        validate_range(duration, 0.1, 10.0, "Fade duration")

        await log_operation(
            ctx,
            f"Applying {duration}s fade-out effect",
        )

        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, "afade", type="out", duration=duration)
            output = ffmpeg.output(stream, output_path)
            ffmpeg.run(output, overwrite_output=True)
            return f"Fade-out effect applied ({duration}s) and saved to {output_path}"
        except ffmpeg.Error as e:
            await handle_ffmpeg_error(e, ctx)
