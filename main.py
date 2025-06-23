#!/usr/bin/env python3
"""VFX MCP Server - Video editing server using FastMCP and ffmpeg-python.

This module provides a comprehensive video editing server built on the FastMCP
framework. It offers tools for basic video operations (trimming, resizing,
concatenation) and advanced features (audio processing, effects, format
conversion) using ffmpeg-python bindings.

Typical usage example:
    $ uv run python main.py
    # Server starts and listens for MCP requests via stdio transport
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import ffmpeg
from fastmcp import Context, FastMCP

# Initialize the MCP server
mcp = FastMCP("vfx-mcp")


# === Basic Video Operations ===


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
    """Get detailed video metadata.

    Analyzes a video file and extracts comprehensive metadata including
    format information, video stream properties, and audio stream properties.
    Uses ffmpeg.probe() to gather the information.

    Args:
        video_path: Path to the video file to analyze.

    Returns:
        A dictionary containing video metadata with the following structure:
        - filename: Base filename of the video
        - format: Container format name
        - duration: Video duration in seconds
        - size: File size in bytes
        - bit_rate: Overall bitrate
        - video: Dict with codec, width, height, fps, bit_rate
        - audio: Dict with codec, sample_rate, channels, bit_rate (if present)

    Raises:
        RuntimeError: If ffmpeg cannot read or analyze the video file.
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
            # Calculate FPS from fractional frame rate string (e.g., "30/1" -> 30.0)
            # eval() is safe here as r_frame_rate is always a fraction from ffmpeg
            fps_fraction: str = video_stream[
                "r_frame_rate"
            ]
            fps: float = eval(
                fps_fraction
            )  # pylint: disable=eval-used

            info["video"] = {
                "codec": video_stream[
                    "codec_name"
                ],
                "width": video_stream["width"],
                "height": video_stream["height"],
                "fps": fps,
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
    """Change video resolution.

    Resizes a video using ffmpeg's scale filter. Can resize by specifying
    exact dimensions, one dimension (maintaining aspect ratio), or a scale
    factor. At least one parameter must be specified.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the resized video will be saved.
        width: Target width in pixels. If height not specified, maintains
            aspect ratio using -1.
        height: Target height in pixels. If width not specified, maintains
            aspect ratio using -1.
        scale: Scale factor (e.g., 0.5 for half size, 2.0 for double size).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the video was resized and saved.

    Raises:
        ValueError: If no resize parameters are specified.
        RuntimeError: If ffmpeg encounters an error during processing.
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
    """Join multiple videos together.

    Concatenates multiple video files into a single output file using ffmpeg's
    concat demuxer. Videos should have the same codec and parameters for best
    results. Creates a temporary file list for the concat operation.

    Args:
        input_paths: List of paths to video files to concatenate in order.
        output_path: Path where the concatenated video will be saved.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the videos were concatenated and saved.

    Raises:
        ValueError: If fewer than 2 video paths are provided.
        RuntimeError: If ffmpeg encounters an error during processing.
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


@mcp.tool
async def extract_audio(
    input_path: str,
    output_path: str,
    format: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Extract audio track from video.

    Extracts the audio stream from a video file and saves it as a separate
    audio file. The output format can be explicitly specified or auto-detected
    from the output file extension.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the extracted audio will be saved.
        format: Audio codec to use (mp3, wav, aac, etc.). If None, ffmpeg
            auto-detects from the output file extension.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the audio was extracted and saved.

    Raises:
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if ctx:
        await ctx.info(
            f"Extracting audio from {input_path}..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Extract only audio
        stream = stream.audio

        # Apply format if specified, otherwise let ffmpeg auto-detect from extension
        if format:
            stream = ffmpeg.output(
                stream, output_path, acodec=format
            )
        else:
            stream = ffmpeg.output(
                stream, output_path
            )

        ffmpeg.run(stream, overwrite_output=True)
        return f"Audio extracted and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def add_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    replace: bool = True,
    ctx: Context | None = None,
) -> str:
    """Add or replace audio track in video.

    Combines a video stream with an audio stream. Can either replace the
    existing audio track or mix the new audio with the existing audio.
    The video stream is copied without re-encoding for efficiency.

    Args:
        video_path: Path to the input video file.
        audio_path: Path to the audio file to add.
        output_path: Path where the output video will be saved.
        replace: If True, replaces existing audio. If False, mixes new audio
            with existing audio using the amix filter.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the audio was added/replaced and saved.

    Raises:
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if ctx:
        action = (
            "Replacing" if replace else "Mixing"
        )
        await ctx.info(
            f"{action} audio in video..."
        )

    try:
        video_stream = ffmpeg.input(video_path)
        audio_stream = ffmpeg.input(audio_path)

        if replace:
            # Replace audio: use video stream without audio and new audio
            output = ffmpeg.output(
                video_stream.video,
                audio_stream.audio,
                output_path,
                vcodec="copy",  # Copy video stream as-is
                acodec="aac",  # Re-encode audio to ensure compatibility
            )
        else:
            # Mix audio: combine existing and new audio
            mixed_audio = ffmpeg.filter(
                [
                    video_stream.audio,
                    audio_stream.audio,
                ],
                "amix",
            )
            output = ffmpeg.output(
                video_stream.video,
                mixed_audio,
                output_path,
                vcodec="copy",
                acodec="aac",
            )

        ffmpeg.run(output, overwrite_output=True)
        action = (
            "replaced" if replace else "mixed"
        )
        return f"Audio {action} and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def apply_filter(
    input_path: str,
    output_path: str,
    filter: str,
    ctx: Context | None = None,
) -> str:
    """Apply ffmpeg filter to video.

    Applies any ffmpeg video filter to the input video. Supports both simple
    filters (e.g., 'hflip') and filters with parameters (e.g., 'blur=10:5').
    Parameters are automatically parsed and passed to the filter.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the filtered video will be saved.
        filter: FFmpeg filter string. Examples:
            - 'hflip' (horizontal flip)
            - 'vflip' (vertical flip)
            - 'blur=10' (blur with radius 10)
            - 'scale=640:480' (resize to 640x480)
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the filter was applied and saved.

    Raises:
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if ctx:
        await ctx.info(
            f"Applying filter '{filter}' to video..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Apply the filter to video stream
        if "=" in filter:
            # Filter with parameters (e.g., "blur=10:5" or "scale=640:480")
            filter_name, params = filter.split(
                "=", 1
            )
            # Split parameters by colon and pass as separate arguments
            param_list: list[str] = params.split(
                ":"
            )
            stream = stream.video.filter(
                filter_name, *param_list
            )
        else:
            # Simple filter without parameters (e.g., "hflip", "vflip")
            stream = ffmpeg.filter(stream, filter)

        stream = ffmpeg.output(
            stream, output_path
        )
        ffmpeg.run(stream, overwrite_output=True)

        return f"Filter '{filter}' applied and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def change_speed(
    input_path: str,
    output_path: str,
    speed: float,
    ctx: Context | None = None,
) -> str:
    """Adjust video playback speed.

    Changes the playback speed of a video by adjusting both video and audio
    streams. Uses setpts filter for video and atempo filter for audio.
    For speeds > 2.0, chains multiple atempo filters since each has a 2.0 limit.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the speed-adjusted video will be saved.
        speed: Speed multiplier. Values > 1.0 increase speed, values < 1.0
            decrease speed. Must be greater than 0.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the speed was changed and saved.

    Raises:
        ValueError: If speed is less than or equal to 0.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if speed <= 0:
        raise ValueError(
            "Speed must be greater than 0"
        )

    if ctx:
        await ctx.info(
            f"Changing video speed to {speed}x..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Apply speed changes to both video and audio streams
        # setpts adjusts presentation timestamps for video speed
        video = ffmpeg.filter(
            stream.video, "setpts", f"PTS/{speed}"
        )

        # atempo filter has a maximum speed multiplier of 2.0
        if speed <= 2.0:
            audio = ffmpeg.filter(
                stream.audio, "atempo", speed
            )
        else:
            # For speeds > 2.0, chain multiple atempo filters
            # Example: 4x speed = 2x atempo + 2x atempo
            audio = stream.audio
            remaining_speed: float = speed

            # Apply 2.0x atempo filters until remaining speed <= 2.0
            while remaining_speed > 2.0:
                audio = ffmpeg.filter(
                    audio, "atempo", 2.0
                )
                remaining_speed /= 2.0

            # Apply final atempo filter for the remainder
            if remaining_speed > 1.0:
                audio = ffmpeg.filter(
                    audio,
                    "atempo",
                    remaining_speed,
                )

        if audio:
            output = ffmpeg.output(
                video, audio, output_path
            )
        else:
            # No audio processing (e.g., for very high speeds or audio-less video)
            output = ffmpeg.output(
                video, output_path
            )

        ffmpeg.run(output, overwrite_output=True)

        return f"Video speed changed to {speed}x and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def generate_thumbnail(
    video_path: str,
    output_path: str,
    timestamp: float | None = None,
    width: int | None = None,
    height: int | None = None,
    ctx: Context | None = None,
) -> str:
    """Extract frame as image thumbnail.

    Extracts a single frame from a video at a specified timestamp and saves
    it as an image. If no timestamp is provided, extracts from the middle
    of the video. Optional resizing can be applied to the extracted frame.

    Args:
        video_path: Path to the input video file.
        output_path: Path where the thumbnail image will be saved.
        timestamp: Time in seconds from which to extract the frame.
            If None, uses the middle of the video.
        width: Target width for the thumbnail. If only width is specified,
            height is calculated to maintain aspect ratio.
        height: Target height for the thumbnail. If only height is specified,
            width is calculated to maintain aspect ratio.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the thumbnail was generated and saved.

    Raises:
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if ctx:
        time_desc = (
            f"at {timestamp}s"
            if timestamp is not None
            else "from middle"
        )
        await ctx.info(
            f"Generating thumbnail {time_desc}..."
        )

    try:
        # Get video duration if timestamp not specified
        if timestamp is None:
            probe = ffmpeg.probe(video_path)
            duration = float(
                probe["format"]["duration"]
            )
            timestamp = (
                duration / 2
            )  # Middle of video

        stream = ffmpeg.input(
            video_path, ss=timestamp
        )

        # Apply resizing if specified
        if width or height:
            if width and height:
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

        # Output single frame
        stream = ffmpeg.output(
            stream, output_path, vframes=1
        )
        ffmpeg.run(stream, overwrite_output=True)

        return f"Thumbnail generated at {timestamp:.2f}s and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def convert_format(
    input_path: str,
    output_path: str,
    format: str | None = None,
    video_codec: str | None = None,
    audio_codec: str | None = None,
    video_bitrate: str | None = None,
    audio_bitrate: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Convert video to different format or codec.

    Converts a video file to a different container format and/or codec with
    optional bitrate control. Provides comprehensive format conversion
    capabilities for optimizing videos for different use cases.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the converted video will be saved.
        format: Output container format (mp4, avi, mov, webm, etc.).
            If None, ffmpeg auto-detects from output file extension.
        video_codec: Video codec to use (h264, h265, vp9, etc.).
        audio_codec: Audio codec to use (aac, mp3, opus, etc.).
        video_bitrate: Video bitrate (e.g., '1000k', '2M', '500k').
        audio_bitrate: Audio bitrate (e.g., '128k', '192k', '320k').
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the video was converted and saved.

    Raises:
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if ctx:
        await ctx.info(
            "Converting video format..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Build output arguments
        output_args = {}

        if format:
            output_args["f"] = format
        if video_codec:
            output_args["vcodec"] = video_codec
        if audio_codec:
            output_args["acodec"] = audio_codec
        if video_bitrate:
            output_args["video_bitrate"] = (
                video_bitrate
            )
        if audio_bitrate:
            output_args["audio_bitrate"] = (
                audio_bitrate
            )

        # Create output with specified arguments
        output = ffmpeg.output(
            stream, output_path, **output_args
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"Video converted and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


# === Resource Handlers ===


@mcp.resource("videos://list")
async def list_videos() -> str:
    """List available video files in the current directory.

    Scans the current working directory for video files with common extensions
    and returns them as a JSON-formatted list. Useful for discovering available
    videos before processing.

    Returns:
        JSON string containing a dictionary with 'videos' key mapping to a
        sorted list of video file paths.
    """
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
    """Get metadata for a specific video file.

    Retrieves comprehensive metadata for a video file and returns it as JSON.
    This is a resource endpoint version of the get_video_info tool.

    Args:
        filename: Name or path of the video file to analyze.

    Returns:
        JSON string containing video metadata including format, duration,
        resolution, codecs, and other technical information. Returns error
        information if the file cannot be processed.
    """
    try:
        # Call the underlying function implementation
        probe = ffmpeg.probe(filename)
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
                filename
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
            # Calculate FPS from fractional frame rate string (e.g., "30/1" -> 30.0)
            # eval() is safe here as r_frame_rate is always a fraction from ffmpeg
            fps_fraction: str = video_stream[
                "r_frame_rate"
            ]
            fps: float = eval(
                fps_fraction
            )  # pylint: disable=eval-used

            info["video"] = {
                "codec": video_stream[
                    "codec_name"
                ],
                "width": video_stream["width"],
                "height": video_stream["height"],
                "fps": fps,
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

        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# === Main Entry Point ===


def main() -> None:
    """Run the VFX MCP server.

    Starts the VFX MCP server with the specified transport method. The transport
    is determined by the MCP_TRANSPORT environment variable, defaulting to 'stdio'.
    Supports both stdio (for direct MCP communication) and SSE (Server-Sent Events)
    transports.

    Environment Variables:
        MCP_TRANSPORT: Transport method ('stdio' or 'sse'). Defaults to 'stdio'.
        MCP_HOST: Host for SSE transport. Defaults to 'localhost'.
        MCP_PORT: Port for SSE transport. Defaults to '8000'.

    Raises:
        SystemExit: If an unknown transport method is specified.
    """
    # Default to stdio transport for direct MCP communication
    transport: str = os.environ.get(
        "MCP_TRANSPORT", "stdio"
    )

    if transport == "stdio":
        print(
            "Starting VFX MCP server on stdio...",
            file=sys.stderr,
        )
        mcp.run()
    elif transport == "sse":
        host: str = os.environ.get(
            "MCP_HOST", "localhost"
        )
        port: int = int(
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
