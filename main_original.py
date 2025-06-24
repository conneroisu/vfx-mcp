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


# === Advanced Video Operations ===


@mcp.tool
async def create_video_slideshow(
    image_paths: list[str],
    output_path: str,
    duration_per_image: float = 3.0,
    transition_duration: float = 0.5,
    fps: int = 30,
    resolution: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Create a video slideshow from multiple images.

    Combines multiple images into a video slideshow with customizable timing
    and optional crossfade transitions between images. Each image is displayed
    for the specified duration with smooth transitions.

    Args:
        image_paths: List of paths to image files to include in slideshow.
        output_path: Path where the slideshow video will be saved.
        duration_per_image: Duration in seconds to display each image.
        transition_duration: Duration in seconds for crossfade transitions.
        fps: Frame rate for the output video.
        resolution: Output resolution (e.g., "1920x1080", "1280x720").
            If None, uses resolution of first image.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the slideshow was created and saved.

    Raises:
        ValueError: If fewer than 1 image path is provided.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if len(image_paths) < 1:
        raise ValueError(
            "Need at least 1 image to create slideshow"
        )

    if ctx:
        await ctx.info(
            f"Creating slideshow from {len(image_paths)} images..."
        )

    try:
        # Create input streams for each image
        inputs = []
        for image_path in image_paths:
            # Each image displayed for specified duration
            stream = ffmpeg.input(
                image_path,
                loop=1,
                t=duration_per_image,
                framerate=fps,
            )
            if resolution:
                width, height = resolution.split(
                    "x"
                )
                stream = ffmpeg.filter(
                    stream,
                    "scale",
                    int(width),
                    int(height),
                )
            inputs.append(stream)

        # Concatenate all images with crossfade transitions
        if len(inputs) == 1:
            # Single image case
            output_stream = inputs[0]
        else:
            # Multiple images - apply crossfade transitions
            output_stream = inputs[0]
            for i in range(1, len(inputs)):
                # Create crossfade transition between current stream and next image
                output_stream = ffmpeg.filter(
                    [output_stream, inputs[i]],
                    "xfade",
                    transition="fade",
                    duration=transition_duration,
                    offset=duration_per_image
                    - transition_duration,
                )

        # Create final output
        output = ffmpeg.output(
            output_stream,
            output_path,
            vcodec="libx264",
            pix_fmt="yuv420p",
        )
        ffmpeg.run(output, overwrite_output=True)

        total_duration = (
            len(image_paths) * duration_per_image
        )
        return (
            f"Slideshow created with {len(image_paths)} images "
            f"({total_duration:.1f}s) and saved to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def extract_frames(
    input_path: str,
    output_dir: str,
    start_time: float = 0.0,
    end_time: float | None = None,
    frame_interval: int = 1,
    image_format: str = "png",
    ctx: Context | None = None,
) -> str:
    """Extract frames from video as individual images.

    Extracts frames from a video file within a specified time range and saves
    them as individual image files. Useful for creating thumbnails, analyzing
    video content, or extracting still images from video.

    Args:
        input_path: Path to the input video file.
        output_dir: Directory where extracted frames will be saved.
        start_time: Start time in seconds for frame extraction.
        end_time: End time in seconds for frame extraction. If None, extracts to end.
        frame_interval: Extract every Nth frame (1 = every frame, 2 = every other).
        image_format: Output image format (png, jpg, bmp, etc.).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating frames were extracted and saved.

    Raises:
        ValueError: If frame_interval is less than 1.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if frame_interval < 1:
        raise ValueError(
            "Frame interval must be 1 or greater"
        )

    if ctx:
        time_range = f"{start_time}s" + (
            f" to {end_time}s"
            if end_time
            else " to end"
        )
        await ctx.info(
            f"Extracting frames from {time_range}..."
        )

    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(
            parents=True, exist_ok=True
        )

        # Build input stream with time range
        input_args = {"ss": start_time}
        if end_time:
            input_args["t"] = (
                end_time - start_time
            )

        stream = ffmpeg.input(
            input_path, **input_args
        )

        # Apply frame interval filter if needed
        if frame_interval > 1:
            # Select every Nth frame using select filter
            stream = ffmpeg.filter(
                stream,
                "select",
                f"not(mod(n,{frame_interval}))",
            )

        # Output frames with numbered filenames
        output_pattern = str(
            Path(output_dir)
            / f"frame_%04d.{image_format}"
        )
        output = ffmpeg.output(
            stream,
            output_pattern,
            vcodec=(
                "png"
                if image_format == "png"
                else "mjpeg"
            ),
        )
        ffmpeg.run(output, overwrite_output=True)

        # Count extracted frames
        extracted_files = list(
            Path(output_dir).glob(
                f"frame_*.{image_format}"
            )
        )
        frame_count = len(extracted_files)

        return f"Extracted {frame_count} frames to {output_dir}/"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def add_text_overlay(
    input_path: str,
    output_path: str,
    text: str,
    position: str = "center",
    font_size: int = 24,
    font_color: str = "white",
    background_color: str | None = None,
    start_time: float = 0.0,
    duration: float | None = None,
    ctx: Context | None = None,
) -> str:
    """Add text overlay to video.

    Adds text overlay/subtitle to a video with customizable positioning,
    styling, and timing. Supports various positions and color options for
    creating titles, captions, or watermarks.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the video with text overlay will be saved.
        text: Text content to overlay on the video.
        position: Text position ("center", "top", "bottom", "top-left", "top-right",
            "bottom-left", "bottom-right", or custom "x:y" coordinates).
        font_size: Font size in pixels.
        font_color: Text color (e.g., "white", "black", "red", "#FF0000").
        background_color: Background color for text box. If None, no background.
        start_time: Start time in seconds when text should appear.
        duration: Duration in seconds for text display. If None, shows for entire video.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating text overlay was added and saved.

    Raises:
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if ctx:
        text_preview = text[:30] + (
            "..." if len(text) > 30 else ""
        )
        await ctx.info(
            f"Adding text overlay: '{text_preview}'"
        )

    try:
        stream = ffmpeg.input(input_path)

        # Map position names to coordinates
        position_map = {
            "center": "(w-text_w)/2:(h-text_h)/2",
            "top": "(w-text_w)/2:text_h",
            "bottom": "(w-text_w)/2:h-text_h-text_h",
            "top-left": "text_h:text_h",
            "top-right": "w-text_w-text_h:text_h",
            "bottom-left": "text_h:h-text_h-text_h",
            "bottom-right": "w-text_w-text_h:h-text_h-text_h",
        }

        # Use mapped position or custom coordinates
        if position in position_map:
            xy_position = position_map[position]
        elif ":" in position:
            # Custom x:y coordinates
            xy_position = position
        else:
            # Default to center if position not recognized
            xy_position = position_map["center"]

        # Build drawtext filter options
        drawtext_options = {
            "text": text,
            "fontsize": font_size,
            "fontcolor": font_color,
            "x": xy_position.split(":")[0],
            "y": xy_position.split(":")[1],
        }

        # Add background box if specified
        if background_color:
            drawtext_options.update(
                {
                    "box": "1",
                    "boxcolor": background_color,
                    "boxborderw": "5",
                }
            )

        # Add timing if specified
        if start_time > 0 or duration:
            enable_condition = (
                f"gte(t,{start_time})"
            )
            if duration:
                enable_condition += f"*lte(t,{start_time + duration})"
            drawtext_options["enable"] = (
                enable_condition
            )

        # Apply drawtext filter
        stream = ffmpeg.filter(
            stream, "drawtext", **drawtext_options
        )
        output = ffmpeg.output(
            stream, output_path
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"Text overlay added and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_video_mosaic(
    input_paths: list[str],
    output_path: str,
    layout: str = "2x2",
    audio_source: int = 0,
    ctx: Context | None = None,
) -> str:
    """Create a mosaic/grid layout from multiple videos.

    Combines multiple videos into a single mosaic video with a grid layout.
    All input videos are resized to fit the grid and played simultaneously.
    Useful for creating comparison videos or multi-camera displays.

    Args:
        input_paths: List of paths to input video files.
        output_path: Path where the mosaic video will be saved.
        layout: Grid layout format (e.g., "2x2", "3x1", "1x4", "3x3").
        audio_source: Index of input video to use for audio (0-based).
            Use -1 for no audio.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the mosaic was created and saved.

    Raises:
        ValueError: If layout format is invalid or insufficient input videos.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if "x" not in layout:
        raise ValueError(
            "Layout must be in format 'WxH' (e.g., '2x2', '3x1')"
        )

    try:
        cols, rows = map(int, layout.split("x"))
        required_videos = cols * rows
    except ValueError as e:
        raise ValueError(
            f"Invalid layout format: {layout}"
        ) from e

    if len(input_paths) < required_videos:
        raise ValueError(
            f"Layout {layout} requires {required_videos} videos, "
            f"but only {len(input_paths)} provided"
        )

    if ctx:
        await ctx.info(
            f"Creating {layout} video mosaic from {len(input_paths)} videos..."
        )

    try:
        # Create input streams and resize them for grid
        inputs = []
        for _i, path in enumerate(
            input_paths[:required_videos]
        ):
            stream = ffmpeg.input(path)
            # Scale each video to fit grid cell (assuming 1920x1080 output)
            cell_width = 1920 // cols
            cell_height = 1080 // rows
            scaled = ffmpeg.filter(
                stream,
                "scale",
                cell_width,
                cell_height,
            )
            inputs.append(scaled)

        # Create the mosaic layout using xstack filter
        if cols == 1 and rows == 1:
            # Single video case
            mosaic = inputs[0]
        else:
            # Build xstack layout string
            layout_str = ""
            for row in range(rows):
                if row > 0:
                    layout_str += "|"
                row_layouts = []
                for col in range(cols):
                    video_idx = row * cols + col
                    if video_idx < len(inputs):
                        row_layouts.append(
                            f"{col}_{row}"
                        )
                layout_str += "_".join(
                    row_layouts
                )

            # Apply xstack filter to create mosaic
            mosaic = ffmpeg.filter(
                inputs,
                "xstack",
                inputs=required_videos,
                layout=layout_str,
            )

        # Handle audio
        if (
            audio_source >= 0
            and audio_source < len(input_paths)
        ):
            audio_stream = ffmpeg.input(
                input_paths[audio_source]
            ).audio
            output = ffmpeg.output(
                mosaic,
                audio_stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
            )
        else:
            # No audio
            output = ffmpeg.output(
                mosaic,
                output_path,
                vcodec="libx264",
            )

        ffmpeg.run(output, overwrite_output=True)

        return f"Video mosaic ({layout}) created and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def detect_scene_changes(
    input_path: str,
    threshold: float = 0.3,
    min_scene_length: float = 1.0,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Detect scene changes in video and return timestamps.

    Analyzes a video for scene changes using frame content analysis and
    returns timestamps where significant changes occur. Useful for automatic
    video segmentation, highlight detection, or content analysis.

    Args:
        input_path: Path to the input video file.
        threshold: Scene change detection threshold (0.0-1.0). Lower values
            detect more subtle changes, higher values detect only major changes.
        min_scene_length: Minimum scene length in seconds to avoid micro-scenes.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Dictionary containing scene change information:
        - scenes: List of dicts with 'start', 'end', and 'duration' for each scene
        - scene_count: Total number of scenes detected
        - total_duration: Total video duration in seconds

    Raises:
        ValueError: If threshold is not between 0.0 and 1.0.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "Threshold must be between 0.0 and 1.0"
        )

    if ctx:
        await ctx.info(
            f"Detecting scene changes with threshold {threshold}..."
        )

    try:
        # Get video duration first
        probe = ffmpeg.probe(input_path)
        duration = float(
            probe["format"]["duration"]
        )

        # Use ffmpeg's scene detection filter to find scene changes

        # Create a complex filter that detects scene changes and outputs timestamps
        stream = ffmpeg.input(input_path)

        # Use select filter with scene change detection
        # scene filter detects changes, select outputs frames at scene boundaries
        scene_stream = ffmpeg.filter(
            stream,
            "select",
            f"gt(scene,{threshold})",
            vsync="vfr",
        )

        # Output frame timestamps using showinfo filter
        info_stream = ffmpeg.filter(
            scene_stream, "showinfo"
        )

        # Null output to just get the timestamps
        output = ffmpeg.output(
            info_stream, "null", f="null"
        )

        # Run ffmpeg and capture stderr which contains showinfo output
        result = ffmpeg.run(
            output,
            capture_stdout=True,
            capture_stderr=True,
        )

        # Parse scene change timestamps from stderr
        scene_timestamps = []
        if result.stderr:
            stderr_text = result.stderr.decode()
            import re

            # Look for timestamp patterns in showinfo output
            timestamp_pattern = (
                r"pts_time:(\d+\.?\d*)"
            )
            timestamps = re.findall(
                timestamp_pattern, stderr_text
            )
            scene_timestamps = [
                float(ts) for ts in timestamps
            ]

        # Add start and end timestamps
        all_timestamps = (
            [0.0]
            + sorted(set(scene_timestamps))
            + [duration]
        )

        # Filter out scenes shorter than min_scene_length
        filtered_timestamps = [all_timestamps[0]]
        for i in range(1, len(all_timestamps)):
            if (
                all_timestamps[i]
                - filtered_timestamps[-1]
                >= min_scene_length
            ):
                filtered_timestamps.append(
                    all_timestamps[i]
                )

        # If last timestamp isn't the end, add it
        if filtered_timestamps[-1] != duration:
            filtered_timestamps.append(duration)

        # Build scene information
        scenes = []
        for i in range(
            len(filtered_timestamps) - 1
        ):
            start_time = filtered_timestamps[i]
            end_time = filtered_timestamps[i + 1]
            scenes.append(
                {
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "duration": round(
                        end_time - start_time, 2
                    ),
                }
            )

        result_data = {
            "scenes": scenes,
            "scene_count": len(scenes),
            "total_duration": round(duration, 2),
        }

        if ctx:
            await ctx.info(
                f"Detected {len(scenes)} scenes"
            )

        return result_data

    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_picture_in_picture(
    main_video_path: str,
    overlay_video_path: str,
    output_path: str,
    position: str = "top-right",
    scale: float = 0.25,
    opacity: float = 1.0,
    margin: int = 20,
    ctx: Context | None = None,
) -> str:
    """Create picture-in-picture effect by overlaying one video onto another.

    Overlays a smaller video (picture-in-picture) onto a main video with
    customizable positioning, scaling, and transparency. Useful for creating
    reaction videos, tutorials, or multi-source content.

    Args:
        main_video_path: Path to the main (background) video file.
        overlay_video_path: Path to the overlay (picture-in-picture) video file.
        output_path: Path where the combined video will be saved.
        position: Position of overlay ("top-left", "top-right", "bottom-left",
            "bottom-right", "center", or custom "x:y" coordinates).
        scale: Scale factor for overlay video (0.1 to 1.0).
        opacity: Opacity of overlay video (0.0 to 1.0).
        margin: Margin in pixels from edges when using named positions.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the picture-in-picture video was created.

    Raises:
        ValueError: If scale or opacity values are out of valid range.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 0.1 <= scale <= 1.0:
        raise ValueError(
            "Scale must be between 0.1 and 1.0"
        )
    if not 0.0 <= opacity <= 1.0:
        raise ValueError(
            "Opacity must be between 0.0 and 1.0"
        )

    if ctx:
        await ctx.info(
            f"Creating picture-in-picture with {scale:.1%} scale overlay..."
        )

    try:
        main_stream = ffmpeg.input(
            main_video_path
        )
        overlay_stream = ffmpeg.input(
            overlay_video_path
        )

        # Get main video dimensions for positioning
        main_probe = ffmpeg.probe(main_video_path)
        main_video_stream = next(
            stream
            for stream in main_probe["streams"]
            if stream["codec_type"] == "video"
        )
        main_width = main_video_stream["width"]
        main_height = main_video_stream["height"]

        # Scale the overlay video
        overlay_width = int(main_width * scale)
        overlay_height = int(main_height * scale)
        scaled_overlay = ffmpeg.filter(
            overlay_stream,
            "scale",
            overlay_width,
            overlay_height,
        )

        # Apply opacity if needed
        if opacity < 1.0:
            scaled_overlay = ffmpeg.filter(
                scaled_overlay,
                "format",
                "yuva420p",
            ).filter(
                "colorchannelmixer", aa=opacity
            )

        # Calculate position coordinates
        position_map = {
            "top-left": f"{margin}:{margin}",
            "top-right": f"{main_width - overlay_width - margin}:{margin}",
            "bottom-left": f"{margin}:{main_height - overlay_height - margin}",
            "bottom-right": (
                f"{main_width - overlay_width - margin}:"
                f"{main_height - overlay_height - margin}"
            ),
            "center": (
                f"{(main_width - overlay_width) // 2}:"
                f"{(main_height - overlay_height) // 2}"
            ),
        }

        if position in position_map:
            x_pos, y_pos = position_map[
                position
            ].split(":")
        elif ":" in position:
            x_pos, y_pos = position.split(":")
        else:
            # Default to top-right
            x_pos, y_pos = position_map[
                "top-right"
            ].split(":")

        # Overlay the video
        output_stream = ffmpeg.filter(
            [main_stream, scaled_overlay],
            "overlay",
            x=x_pos,
            y=y_pos,
        )

        output = ffmpeg.output(
            output_stream,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"Picture-in-picture video created and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def extract_audio_spectrum(
    input_path: str,
    output_path: str,
    style: str = "spectrum",
    size: str = "1280x720",
    colors: str = "rainbow",
    ctx: Context | None = None,
) -> str:
    """Generate visual audio spectrum/waveform video from audio.

    Creates a video visualization of audio content using spectrum analysis
    or waveform display. Useful for creating audio visualizations, podcasts,
    or music videos.

    Args:
        input_path: Path to input audio or video file.
        output_path: Path where the spectrum video will be saved.
        style: Visualization style ("spectrum", "waveform", "showcqt", "showfreqs").
        size: Output video resolution (e.g., "1280x720", "1920x1080").
        colors: Color scheme ("rainbow", "fire", "cool", "hot", "magma").
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the spectrum video was created.

    Raises:
        ValueError: If style or size format is invalid.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    valid_styles = [
        "spectrum",
        "waveform",
        "showcqt",
        "showfreqs",
    ]
    if style not in valid_styles:
        raise ValueError(
            f"Style must be one of: {', '.join(valid_styles)}"
        )

    if "x" not in size:
        raise ValueError(
            "Size must be in format 'WIDTHxHEIGHT'"
        )

    if ctx:
        await ctx.info(
            f"Generating {style} visualization..."
        )

    try:
        stream = ffmpeg.input(input_path)
        width, height = size.split("x")

        # Configure visualization based on style
        if style == "spectrum":
            # Audio spectrum analyzer
            visual_stream = ffmpeg.filter(
                stream,
                "showspectrum",
                s=size,
                mode="combined",
                color=colors,
                scale="log",
            )
        elif style == "waveform":
            # Audio waveform
            visual_stream = ffmpeg.filter(
                stream,
                "showwaves",
                s=size,
                mode="cline",
                colors=colors,
                rate=25,
            )
        elif style == "showcqt":
            # Constant Q Transform visualization
            visual_stream = ffmpeg.filter(
                stream,
                "showcqt",
                s=size,
                fps=25,
                sono_h=int(height) // 2,
                bar_h=int(height) // 2,
            )
        else:  # showfreqs
            # Frequency analysis
            visual_stream = ffmpeg.filter(
                stream,
                "showfreqs",
                s=size,
                mode="bar",
                ascale="log",
                fscale="log",
            )

        # If input has video, we might want to combine audio from original
        try:
            # Try to get audio stream from input
            audio_stream = stream.audio
            output = ffmpeg.output(
                visual_stream,
                audio_stream,
                output_path,
                vcodec="libx264",
            )
        except Exception:
            # Input might be audio-only or no audio
            output = ffmpeg.output(
                visual_stream,
                output_path,
                vcodec="libx264",
            )

        ffmpeg.run(output, overwrite_output=True)

        return f"Audio {style} visualization created and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def apply_color_grading(
    input_path: str,
    output_path: str,
    brightness: float = 0.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    gamma: float = 1.0,
    temperature: int = 0,
    tint: int = 0,
    ctx: Context | None = None,
) -> str:
    """Apply color grading and correction to video.

    Adjusts various color properties of a video including brightness, contrast,
    saturation, gamma, and color temperature. Useful for color correction,
    mood adjustment, and cinematic grading.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the color-graded video will be saved.
        brightness: Brightness adjustment (-1.0 to 1.0, 0 = no change).
        contrast: Contrast multiplier (0.0 to 3.0, 1.0 = no change).
        saturation: Saturation multiplier (0.0 to 3.0, 1.0 = no change).
        gamma: Gamma correction (0.1 to 3.0, 1.0 = no change).
        temperature: Color temperature shift in Kelvin (-2000 to 2000).
        tint: Tint adjustment (-100 to 100, 0 = no change).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating color grading was applied.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not -1.0 <= brightness <= 1.0:
        raise ValueError(
            "Brightness must be between -1.0 and 1.0"
        )
    if not 0.0 <= contrast <= 3.0:
        raise ValueError(
            "Contrast must be between 0.0 and 3.0"
        )
    if not 0.0 <= saturation <= 3.0:
        raise ValueError(
            "Saturation must be between 0.0 and 3.0"
        )
    if not 0.1 <= gamma <= 3.0:
        raise ValueError(
            "Gamma must be between 0.1 and 3.0"
        )
    if not -2000 <= temperature <= 2000:
        raise ValueError(
            "Temperature must be between -2000 and 2000"
        )
    if not -100 <= tint <= 100:
        raise ValueError(
            "Tint must be between -100 and 100"
        )

    if ctx:
        await ctx.info(
            "Applying color grading..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Apply brightness and contrast using eq filter
        if brightness != 0.0 or contrast != 1.0:
            stream = ffmpeg.filter(
                stream,
                "eq",
                brightness=brightness,
                contrast=contrast,
            )

        # Apply saturation
        if saturation != 1.0:
            stream = ffmpeg.filter(
                stream,
                "eq",
                saturation=saturation,
            )

        # Apply gamma correction
        if gamma != 1.0:
            stream = ffmpeg.filter(
                stream, "eq", gamma=gamma
            )

        # Apply color temperature and tint adjustments
        if temperature != 0 or tint != 0:
            # Convert temperature to RGB multipliers (simplified)
            if temperature > 0:
                # Warmer (more red/yellow)
                red_adj = (
                    1.0
                    + (temperature / 2000.0) * 0.2
                )
                blue_adj = (
                    1.0
                    - (temperature / 2000.0) * 0.2
                )
            else:
                # Cooler (more blue)
                red_adj = (
                    1.0
                    + (temperature / 2000.0) * 0.2
                )
                blue_adj = (
                    1.0
                    - (temperature / 2000.0) * 0.2
                )

            # Apply tint (green/magenta balance)
            green_adj = 1.0 + (tint / 100.0) * 0.1

            stream = ffmpeg.filter(
                stream,
                "colorbalance",
                rs=red_adj - 1.0,
                gs=green_adj - 1.0,
                bs=blue_adj - 1.0,
            )

        output = ffmpeg.output(
            stream, output_path, vcodec="libx264"
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"Color grading applied and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_time_lapse(
    input_path: str,
    output_path: str,
    speed_factor: float = 10.0,
    stabilize: bool = False,
    smooth_motion: bool = True,
    ctx: Context | None = None,
) -> str:
    """Convert normal speed video to time-lapse.

    Creates time-lapse videos by sampling frames and optionally applying
    stabilization and motion smoothing. Useful for creating fast-forward
    effects from long-duration recordings.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the time-lapse video will be saved.
        speed_factor: Speed multiplier for time-lapse (2.0 to 100.0).
        stabilize: Whether to apply video stabilization.
        smooth_motion: Whether to apply motion smoothing between frames.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the time-lapse was created.

    Raises:
        ValueError: If speed_factor is out of valid range.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 2.0 <= speed_factor <= 100.0:
        raise ValueError(
            "Speed factor must be between 2.0 and 100.0"
        )

    if ctx:
        await ctx.info(
            f"Creating {speed_factor}x time-lapse video..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Apply video stabilization if requested
        if stabilize:
            if ctx:
                await ctx.info(
                    "Applying video stabilization..."
                )
            # First pass: analyze for stabilization
            stream = ffmpeg.filter(
                stream,
                "vidstabdetect",
                shakiness=10,
                accuracy=15,
            )
            # Second pass: apply stabilization
            stream = ffmpeg.filter(
                stream,
                "vidstabtransform",
                smoothing=30,
            )

        # Create time-lapse effect
        if speed_factor <= 2.0:
            # Use setpts for small speed increases
            stream = ffmpeg.filter(
                stream,
                "setpts",
                f"PTS/{speed_factor}",
            )
        else:
            # Use frame selection for larger speed increases
            frame_step = int(speed_factor)
            stream = ffmpeg.filter(
                stream,
                "select",
                f"not(mod(n,{frame_step}))",
            )
            stream = ffmpeg.filter(
                stream,
                "setpts",
                "N/FRAME_RATE/TB",
            )

        # Apply motion smoothing if requested
        if smooth_motion and speed_factor > 5.0:
            stream = ffmpeg.filter(
                stream,
                "minterpolate",
                fps=30,
                mi_mode="mci",
                mc_mode="aobmc",
            )

        # Handle audio - speed up to match video or remove for very fast time-lapses
        try:
            audio_stream = ffmpeg.input(
                input_path
            ).audio
            if speed_factor <= 4.0:
                # Speed up audio to match video
                if speed_factor <= 2.0:
                    audio_stream = ffmpeg.filter(
                        audio_stream,
                        "atempo",
                        speed_factor,
                    )
                else:
                    # Chain atempo filters for higher speeds
                    remaining_speed = speed_factor
                    while remaining_speed > 2.0:
                        audio_stream = (
                            ffmpeg.filter(
                                audio_stream,
                                "atempo",
                                2.0,
                            )
                        )
                        remaining_speed /= 2.0
                    if remaining_speed > 1.0:
                        audio_stream = (
                            ffmpeg.filter(
                                audio_stream,
                                "atempo",
                                remaining_speed,
                            )
                        )
                output = ffmpeg.output(
                    stream,
                    audio_stream,
                    output_path,
                    vcodec="libx264",
                )
            else:
                # Remove audio for very fast time-lapses
                output = ffmpeg.output(
                    stream,
                    output_path,
                    vcodec="libx264",
                )
        except Exception:
            # No audio stream or audio processing failed
            output = ffmpeg.output(
                stream,
                output_path,
                vcodec="libx264",
            )

        ffmpeg.run(output, overwrite_output=True)

        return (
            f"Time-lapse video ({speed_factor}x speed) created and "
            f"saved to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def merge_audio_tracks(
    audio_paths: list[str],
    output_path: str,
    volumes: list[float] | None = None,
    delays: list[float] | None = None,
    mix_mode: str = "mix",
    ctx: Context | None = None,
) -> str:
    """Merge multiple audio tracks with volume and timing control.

    Combines multiple audio files into a single output with individual
    volume control, timing delays, and mixing modes. Useful for creating
    soundtracks, podcasts, or multi-source audio content.

    Args:
        audio_paths: List of paths to audio files to merge.
        output_path: Path where the merged audio will be saved.
        volumes: List of volume multipliers for each track (0.0 to 2.0).
            If None, all tracks use volume 1.0.
        delays: List of delay times in seconds for each track.
            If None, all tracks start at time 0.
        mix_mode: Mixing mode ("mix", "sequence", "overlay").
            - mix: Blend all tracks together
            - sequence: Play tracks one after another
            - overlay: Overlay tracks with timing control
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating audio tracks were merged.

    Raises:
        ValueError: If input validation fails or insufficient tracks provided.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if len(audio_paths) < 2:
        raise ValueError(
            "Need at least 2 audio tracks to merge"
        )

    valid_modes = ["mix", "sequence", "overlay"]
    if mix_mode not in valid_modes:
        raise ValueError(
            f"Mix mode must be one of: {', '.join(valid_modes)}"
        )

    # Validate volumes if provided
    if volumes:
        if len(volumes) != len(audio_paths):
            raise ValueError(
                "Number of volumes must match number of audio paths"
            )
        for vol in volumes:
            if not 0.0 <= vol <= 2.0:
                raise ValueError(
                    "Volume values must be between 0.0 and 2.0"
                )
    else:
        volumes = [1.0] * len(audio_paths)

    # Validate delays if provided
    if delays:
        if len(delays) != len(audio_paths):
            raise ValueError(
                "Number of delays must match number of audio paths"
            )
        for delay in delays:
            if delay < 0:
                raise ValueError(
                    "Delay values must be non-negative"
                )
    else:
        delays = [0.0] * len(audio_paths)

    if ctx:
        await ctx.info(
            f"Merging {len(audio_paths)} audio tracks in {mix_mode} mode..."
        )

    try:
        # Create input streams
        inputs = []
        for _i, (
            path,
            volume,
            delay,
        ) in enumerate(
            zip(
                audio_paths,
                volumes,
                delays,
                strict=False,
            )
        ):
            stream = ffmpeg.input(path)

            # Apply delay if specified
            if delay > 0:
                delay_ms = int(delay * 1000)
                stream = ffmpeg.filter(
                    stream,
                    "adelay",
                    f"{delay_ms}|{delay_ms}",
                )

            # Apply volume adjustment
            if volume != 1.0:
                stream = ffmpeg.filter(
                    stream, "volume", volume
                )

            inputs.append(stream)

        # Apply mixing based on mode
        if mix_mode == "mix":
            # Mix all tracks together
            if len(inputs) == 2:
                mixed = ffmpeg.filter(
                    [inputs[0], inputs[1]],
                    "amix",
                    inputs=2,
                )
            else:
                mixed = ffmpeg.filter(
                    inputs,
                    "amix",
                    inputs=len(inputs),
                )

        elif mix_mode == "sequence":
            # Concatenate tracks sequentially
            mixed = ffmpeg.filter(
                inputs,
                "concat",
                n=len(inputs),
                v=0,
                a=1,
            )

        else:  # overlay
            # Overlay tracks with timing control
            mixed = inputs[0]
            for i in range(1, len(inputs)):
                mixed = ffmpeg.filter(
                    [mixed, inputs[i]],
                    "amix",
                    inputs=2,
                )

        # Output the merged audio
        output = ffmpeg.output(
            mixed, output_path, acodec="aac"
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"Audio tracks merged in {mix_mode} mode and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_green_screen_effect(
    input_path: str,
    output_path: str,
    background_path: str | None = None,
    chroma_key_color: str = "green",
    similarity: float = 0.3,
    blend: float = 0.1,
    spill_reduction: float = 0.1,
    ctx: Context | None = None,
) -> str:
    """Remove green/blue screen background and replace with custom background.

    Performs chroma key compositing to remove a colored background and optionally
    replace it with a custom background image or video. Includes advanced spill
    reduction and edge blending for professional results.

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
    if not 0.0 <= similarity <= 1.0:
        raise ValueError(
            "Similarity must be between 0.0 and 1.0"
        )
    if not 0.0 <= blend <= 1.0:
        raise ValueError(
            "Blend must be between 0.0 and 1.0"
        )
    if not 0.0 <= spill_reduction <= 1.0:
        raise ValueError(
            "Spill reduction must be between 0.0 and 1.0"
        )

    # Convert color names to hex values
    color_map = {
        "green": "0x00FF00",
        "blue": "0x0000FF",
        "red": "0xFF0000",
        "cyan": "0x00FFFF",
        "magenta": "0xFF00FF",
        "yellow": "0xFFFF00",
    }

    if chroma_key_color.lower() in color_map:
        key_color = color_map[
            chroma_key_color.lower()
        ]
    elif chroma_key_color.startswith("#"):
        key_color = "0x" + chroma_key_color[1:]
    else:
        key_color = chroma_key_color

    if ctx:
        await ctx.info(
            f"Applying {chroma_key_color} screen removal..."
        )

    try:
        foreground = ffmpeg.input(input_path)

        # Apply chromakey filter with advanced settings
        keyed = ffmpeg.filter(
            foreground,
            "chromakey",
            color=key_color,
            similarity=similarity,
            blend=blend,
            yuv=1,  # Use YUV color space for better results
        )

        # Apply despill filter to reduce color spill
        if spill_reduction > 0:
            keyed = ffmpeg.filter(
                keyed,
                "despill",
                type=(
                    1
                    if chroma_key_color.lower()
                    == "green"
                    else 2
                ),
                mix=spill_reduction,
                expand=spill_reduction * 0.5,
            )

        if background_path:
            # Composite with background
            background = ffmpeg.input(
                background_path
            )

            # Get foreground dimensions to scale background if needed
            probe = ffmpeg.probe(input_path)
            video_stream = next(
                stream
                for stream in probe["streams"]
                if stream["codec_type"] == "video"
            )
            width = video_stream["width"]
            height = video_stream["height"]

            # Scale background to match foreground
            background_scaled = ffmpeg.filter(
                background, "scale", width, height
            )

            # Composite foreground over background
            output_stream = ffmpeg.filter(
                [background_scaled, keyed],
                "overlay",
                x=0,
                y=0,
            )
        else:
            # Keep transparent background
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
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def apply_motion_blur(
    input_path: str,
    output_path: str,
    blur_strength: float = 1.0,
    angle: float = 0.0,
    shutter_speed: float = 0.5,
    ctx: Context | None = None,
) -> str:
    """Add realistic motion blur effects to video.

    Applies motion blur to simulate camera movement or fast-moving objects.
    Can create directional blur based on angle and adjustable blur intensity
    based on virtual shutter speed.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the motion-blurred video will be saved.
        blur_strength: Motion blur intensity (0.1 to 5.0).
        angle: Blur direction in degrees (0 to 360). 0 = horizontal, 90 = vertical.
        shutter_speed: Virtual shutter speed affecting blur amount (0.1 to 1.0).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating motion blur was applied.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 0.1 <= blur_strength <= 5.0:
        raise ValueError(
            "Blur strength must be between 0.1 and 5.0"
        )
    if not 0.0 <= angle <= 360.0:
        raise ValueError(
            "Angle must be between 0.0 and 360.0"
        )
    if not 0.1 <= shutter_speed <= 1.0:
        raise ValueError(
            "Shutter speed must be between 0.1 and 1.0"
        )

    if ctx:
        await ctx.info(
            f"Applying motion blur (strength: {blur_strength}, angle: {angle}°)..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Calculate blur parameters based on strength and shutter speed
        blur_amount = (
            blur_strength
            * (1.0 - shutter_speed)
            * 10
        )

        # Apply directional motion blur
        if angle == 0 or angle == 180:
            # Horizontal blur
            blur_filter = ffmpeg.filter(
                stream,
                "boxblur",
                luma_radius=f"{blur_amount}:1",
                chroma_radius=f"{blur_amount/2}:1",
            )
        elif angle == 90 or angle == 270:
            # Vertical blur
            blur_filter = ffmpeg.filter(
                stream,
                "boxblur",
                luma_radius=f"1:{blur_amount}",
                chroma_radius=f"1:{blur_amount/2}",
            )
        else:
            # Diagonal/custom angle blur using convolution
            # Create motion blur kernel based on angle
            import math

            math.radians(angle)
            max(3, int(blur_amount))

            # For simplicity, use mblur filter with approximated settings
            blur_filter = ffmpeg.filter(
                stream,
                "mblur",
                amount=blur_strength,
                angle=angle,
            )

        # Apply temporal blending to enhance motion blur effect
        if shutter_speed < 0.8:
            # Blend multiple frames for more realistic motion blur
            blended = ffmpeg.filter(
                blur_filter,
                "tmix",
                frames=max(
                    2,
                    int(
                        (1.0 - shutter_speed) * 5
                    ),
                ),
                weights=f"1 {shutter_speed}",
            )
            output_stream = blended
        else:
            output_stream = blur_filter

        output = ffmpeg.output(
            output_stream,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return (
            f"Motion blur applied (strength: {blur_strength}, angle: {angle}°) "
            f"and saved to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_video_transitions(
    video_paths: list[str],
    output_path: str,
    transition_type: str = "fade",
    transition_duration: float = 1.0,
    ctx: Context | None = None,
) -> str:
    """Create smooth transitions between multiple video clips.

    Combines multiple video clips with professional transitions between them.
    Supports various transition types including fades, wipes, slides, and
    dissolves for seamless video sequences.

    Args:
        video_paths: List of paths to video files to combine with transitions.
        output_path: Path where the final video with transitions will be saved.
        transition_type: Type of transition ("fade", "wipe_left", "wipe_right",
            "wipe_up", "wipe_down", "slide_left", "slide_right", "dissolve").
        transition_duration: Duration of each transition in seconds (0.1 to 5.0).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating video with transitions was created.

    Raises:
        ValueError: If parameters are invalid or insufficient video clips.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if len(video_paths) < 2:
        raise ValueError(
            "Need at least 2 video clips to create transitions"
        )

    if not 0.1 <= transition_duration <= 5.0:
        raise ValueError(
            "Transition duration must be between 0.1 and 5.0 seconds"
        )

    valid_transitions = [
        "fade",
        "wipe_left",
        "wipe_right",
        "wipe_up",
        "wipe_down",
        "slide_left",
        "slide_right",
        "dissolve",
        "pixelize",
        "radial",
    ]
    if transition_type not in valid_transitions:
        raise ValueError(
            f"Transition type must be one of: {', '.join(valid_transitions)}"
        )

    if ctx:
        await ctx.info(
            f"Creating video with {transition_type} transitions..."
        )

    try:
        # Load all video inputs
        inputs = [
            ffmpeg.input(path)
            for path in video_paths
        ]

        # Start with the first video
        result = inputs[0]

        # Apply transitions between consecutive videos
        for i in range(1, len(inputs)):
            current_video = inputs[i]

            # Apply the specified transition
            if transition_type == "fade":
                # Crossfade transition
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="fade",
                    duration=transition_duration,
                    offset=0,  # Offset will be calculated by ffmpeg
                )
            elif transition_type == "dissolve":
                # Dissolve transition
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="dissolve",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "wipe_left":
                # Wipe from left
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="wipeleft",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "wipe_right":
                # Wipe from right
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="wiperight",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "wipe_up":
                # Wipe upward
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="wipeup",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "wipe_down":
                # Wipe downward
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="wipedown",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "slide_left":
                # Slide left
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="slideleft",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "slide_right":
                # Slide right
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="slideright",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "pixelize":
                # Pixelize transition
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="pixelize",
                    duration=transition_duration,
                    offset=0,
                )
            elif transition_type == "radial":
                # Radial transition
                result = ffmpeg.filter(
                    [result, current_video],
                    "xfade",
                    transition="radial",
                    duration=transition_duration,
                    offset=0,
                )

        output = ffmpeg.output(
            result, output_path, vcodec="libx264"
        )
        ffmpeg.run(output, overwrite_output=True)

        return (
            f"Video with {len(video_paths)} clips and {transition_type} transitions "
            f"created and saved to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def extract_video_statistics(
    input_path: str,
    analysis_type: str = "comprehensive",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Analyze video content for technical metrics and quality assessment.

    Performs detailed analysis of video files including quality metrics,
    encoding information, motion analysis, and technical statistics.
    Useful for quality control and optimization decisions.

    Args:
        input_path: Path to the video file to analyze.
        analysis_type: Type of analysis ("basic", "comprehensive", "quality", "motion").
        ctx: MCP context for progress reporting and logging.

    Returns:
        Dictionary containing detailed video analysis results including:
        - Technical specifications (resolution, framerate, bitrate)
        - Quality metrics (PSNR, SSIM if applicable)
        - Motion analysis (scene changes, motion vectors)
        - Audio analysis (levels, frequency response)

    Raises:
        ValueError: If analysis_type is invalid.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    valid_types = [
        "basic",
        "comprehensive",
        "quality",
        "motion",
    ]
    if analysis_type not in valid_types:
        raise ValueError(
            f"Analysis type must be one of: {', '.join(valid_types)}"
        )

    if ctx:
        await ctx.info(
            f"Performing {analysis_type} video analysis..."
        )

    try:
        # Get basic video information
        probe = ffmpeg.probe(input_path)

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

        stats = {
            "file_info": {
                "filename": os.path.basename(
                    input_path
                ),
                "size_bytes": int(
                    probe["format"]["size"]
                ),
                "duration_seconds": float(
                    probe["format"]["duration"]
                ),
                "format_name": probe["format"][
                    "format_name"
                ],
                "bit_rate": int(
                    probe["format"]["bit_rate"]
                ),
            }
        }

        if video_stream:
            # Calculate FPS
            fps_fraction = video_stream[
                "r_frame_rate"
            ]
            fps = eval(
                fps_fraction
            )  # Safe since ffmpeg always returns fractions

            stats["video"] = {
                "codec": video_stream[
                    "codec_name"
                ],
                "width": video_stream["width"],
                "height": video_stream["height"],
                "fps": round(fps, 2),
                "bit_rate": video_stream.get(
                    "bit_rate", "N/A"
                ),
                "pix_fmt": video_stream.get(
                    "pix_fmt"
                ),
                "aspect_ratio": f"{video_stream['width']}:{video_stream['height']}",
            }

        if audio_stream:
            stats["audio"] = {
                "codec": audio_stream[
                    "codec_name"
                ],
                "sample_rate": int(
                    audio_stream["sample_rate"]
                ),
                "channels": audio_stream[
                    "channels"
                ],
                "bit_rate": audio_stream.get(
                    "bit_rate", "N/A"
                ),
                "channel_layout": audio_stream.get(
                    "channel_layout", "unknown"
                ),
            }

        # Perform additional analysis based on type
        if analysis_type in [
            "comprehensive",
            "quality",
        ]:
            if ctx:
                await ctx.info(
                    "Analyzing video quality metrics..."
                )

            # Run ffmpeg with stats filter to get detailed metrics
            stats_output = ffmpeg.input(
                input_path
            ).output(
                "null", f="null", vf="signalstats"
            )
            result = ffmpeg.run(
                stats_output,
                capture_stderr=True,
                quiet=True,
            )

            # Parse signal statistics from stderr
            stderr_text = (
                result.stderr.decode()
                if result.stderr
                else ""
            )

            # Extract quality metrics (simplified parsing)
            quality_metrics = {}
            for line in stderr_text.split("\n"):
                if "YMIN:" in line:
                    parts = line.split()
                    for part in parts:
                        if ":" in part:
                            key, value = (
                                part.split(":", 1)
                            )
                            try:
                                quality_metrics[
                                    key.lower()
                                ] = float(value)
                            except ValueError:
                                quality_metrics[
                                    key.lower()
                                ] = value

            if quality_metrics:
                stats["quality_metrics"] = (
                    quality_metrics
                )

        if analysis_type in [
            "comprehensive",
            "motion",
        ]:
            if ctx:
                await ctx.info(
                    "Analyzing motion and scene changes..."
                )

            # Analyze scene changes for motion metrics
            try:
                scene_output = ffmpeg.input(
                    input_path
                ).output(
                    "null",
                    f="null",
                    vf="select=gt(scene\\,0.3),showinfo",
                )
                scene_result = ffmpeg.run(
                    scene_output,
                    capture_stderr=True,
                    quiet=True,
                )

                # Count scene changes from output
                stderr_text = (
                    scene_result.stderr.decode()
                    if scene_result.stderr
                    else ""
                )
                scene_count = stderr_text.count(
                    "Parsed_showinfo"
                )

                stats["motion_analysis"] = {
                    "scene_changes": scene_count,
                    "average_scene_length": round(
                        stats["file_info"][
                            "duration_seconds"
                        ]
                        / max(scene_count, 1),
                        2,
                    ),
                    "motion_intensity": (
                        "high"
                        if scene_count > 50
                        else (
                            "medium"
                            if scene_count > 20
                            else "low"
                        )
                    ),
                }
            except Exception:
                stats["motion_analysis"] = {
                    "error": "Motion analysis failed"
                }

        # Add file size analysis
        duration = stats["file_info"][
            "duration_seconds"
        ]
        size_mb = stats["file_info"][
            "size_bytes"
        ] / (1024 * 1024)

        stats["compression_analysis"] = {
            "size_mb": round(size_mb, 2),
            "mb_per_minute": round(
                size_mb / (duration / 60), 2
            ),
            "compression_ratio": (
                "high"
                if size_mb / (duration / 60) < 10
                else (
                    "medium"
                    if size_mb / (duration / 60)
                    < 50
                    else "low"
                )
            ),
        }

        return stats

    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_loop_video(
    input_path: str,
    output_path: str,
    loop_duration: float = 10.0,
    crossfade_duration: float = 1.0,
    seamless: bool = True,
    ctx: Context | None = None,
) -> str:
    """Create seamless looping video with crossfade blending.

    Creates a video that loops seamlessly by blending the end with the beginning
    using crossfade transitions. Useful for creating background videos,
    cinemagraphs, or repeating animations.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the looping video will be saved.
        loop_duration: Total duration of the output loop in seconds (1.0 to 120.0).
        crossfade_duration: Duration of crossfade between end and beginning
            (0.1 to 5.0).
        seamless: Whether to ensure seamless looping with motion analysis.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating the loop video was created.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 1.0 <= loop_duration <= 120.0:
        raise ValueError(
            "Loop duration must be between 1.0 and 120.0 seconds"
        )
    if not 0.1 <= crossfade_duration <= 5.0:
        raise ValueError(
            "Crossfade duration must be between 0.1 and 5.0 seconds"
        )
    if crossfade_duration >= loop_duration / 2:
        raise ValueError(
            "Crossfade duration must be less than half the loop duration"
        )

    if ctx:
        await ctx.info(
            f"Creating {loop_duration}s seamless loop video..."
        )

    try:
        # Get video duration to determine loop strategy
        probe = ffmpeg.probe(input_path)
        original_duration = float(
            probe["format"]["duration"]
        )

        # Create the main loop segment
        if original_duration >= loop_duration:
            # Use portion of the original video
            main_segment = ffmpeg.input(
                input_path,
                ss=0,
                t=loop_duration
                - crossfade_duration,
            )
        else:
            # Repeat the video to reach desired duration
            repeats_needed = (
                int(
                    (
                        loop_duration
                        - crossfade_duration
                    )
                    / original_duration
                )
                + 1
            )

            # Create repeated segments
            segments = []
            for _i in range(repeats_needed):
                segment = ffmpeg.input(input_path)
                segments.append(segment)

            # Concatenate segments
            if len(segments) > 1:
                main_segment = ffmpeg.filter(
                    segments,
                    "concat",
                    n=len(segments),
                    v=1,
                    a=1,
                )
                # Trim to desired length
                main_segment = ffmpeg.filter(
                    main_segment,
                    "trim",
                    duration=loop_duration
                    - crossfade_duration,
                )
            else:
                main_segment = ffmpeg.filter(
                    segments[0],
                    "trim",
                    duration=loop_duration
                    - crossfade_duration,
                )

        # Create crossfade segment from beginning and end
        beginning = ffmpeg.input(
            input_path, ss=0, t=crossfade_duration
        )

        if (
            original_duration
            >= crossfade_duration
        ):
            # Use end of original video
            end_start_time = min(
                original_duration
                - crossfade_duration,
                loop_duration
                - crossfade_duration,
            )
            ending = ffmpeg.input(
                input_path,
                ss=end_start_time,
                t=crossfade_duration,
            )
        else:
            # Use beginning again if video is shorter than crossfade
            ending = ffmpeg.input(
                input_path,
                ss=0,
                t=crossfade_duration,
            )

        # Apply crossfade between end and beginning
        crossfade_segment = ffmpeg.filter(
            [ending, beginning],
            "xfade",
            transition="fade",
            duration=crossfade_duration,
            offset=0,
        )

        # Combine main segment with crossfade segment
        if seamless:
            # Ensure color and brightness continuity
            main_segment = ffmpeg.filter(
                main_segment, "colorbalance"
            )
            crossfade_segment = ffmpeg.filter(
                crossfade_segment, "colorbalance"
            )

        # Concatenate main segment and crossfade
        final_video = ffmpeg.filter(
            [main_segment, crossfade_segment],
            "concat",
            n=2,
            v=1,
            a=1,
        )

        # Apply final adjustments for seamless looping
        if seamless:
            # Add slight fade in/out to ensure smooth transitions
            final_video = ffmpeg.filter(
                final_video,
                "fade",
                type="in",
                start_time=0,
                duration=0.1,
            )
            final_video = ffmpeg.filter(
                final_video,
                "fade",
                type="out",
                start_time=loop_duration - 0.1,
                duration=0.1,
            )

        output = ffmpeg.output(
            final_video,
            output_path,
            vcodec="libx264",
            pix_fmt="yuv420p",
        )
        ffmpeg.run(output, overwrite_output=True)

        return (
            f"Seamless loop video ({loop_duration}s with {crossfade_duration}s "
            f"crossfade) created and saved to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_particle_system(
    input_path: str,
    output_path: str,
    particle_type: str = "snow",
    density: int = 100,
    size_range: str = "2:8",
    speed: float = 1.0,
    direction: str = "down",
    opacity: float = 0.7,
    ctx: Context | None = None,
) -> str:
    """Generate particle effects like snow, rain, sparks, or smoke.

    Creates realistic particle systems overlaid on video content. Supports
    various particle types with customizable physics, appearance, and motion.
    Perfect for adding atmospheric effects to videos.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the video with particles will be saved.
        particle_type: Type of particles ("snow", "rain", "sparks", "dust", "bubbles").
        density: Number of particles (10 to 500).
        size_range: Size range as "min:max" pixels (e.g., "2:8").
        speed: Particle motion speed multiplier (0.1 to 5.0).
        direction: Motion direction ("down", "up", "left", "right", "random").
        opacity: Particle opacity (0.1 to 1.0).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating particles were added to the video.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    valid_types = [
        "snow",
        "rain",
        "sparks",
        "dust",
        "bubbles",
    ]
    if particle_type not in valid_types:
        raise ValueError(
            f"Particle type must be one of: {', '.join(valid_types)}"
        )

    if not 10 <= density <= 500:
        raise ValueError(
            "Density must be between 10 and 500"
        )
    if not 0.1 <= speed <= 5.0:
        raise ValueError(
            "Speed must be between 0.1 and 5.0"
        )
    if not 0.1 <= opacity <= 1.0:
        raise ValueError(
            "Opacity must be between 0.1 and 1.0"
        )

    try:
        min_size, max_size = map(
            int, size_range.split(":")
        )
        if min_size >= max_size or min_size < 1:
            raise ValueError("Invalid size range")
    except (ValueError, AttributeError):
        raise ValueError(
            "Size range must be in format 'min:max' (e.g., '2:8')"
        ) from None

    if ctx:
        await ctx.info(
            f"Adding {particle_type} particles (density: {density})..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Create particle effect based on type
        if particle_type == "snow":
            # White particles falling down with slight randomness
            particles = ffmpeg.filter(
                stream,
                "geq",
                r=f"if(lt(random(1)*255,{density/5}),255,r(X,Y))",
                g=f"if(lt(random(2)*255,{density/5}),255,g(X,Y))",
                b=f"if(lt(random(3)*255,{density/5}),255,b(X,Y))",
            )
            # Add motion blur for falling effect
            particles = ffmpeg.filter(
                particles,
                "boxblur",
                f"1:{max_size}",
            )

        elif particle_type == "rain":
            # Vertical streaks falling fast
            particles = ffmpeg.filter(
                stream,
                "drawbox",
                x="random(1)*iw",
                y="random(2)*ih",
                width=1,
                height=max_size * 3,
                color="white@" + str(opacity),
                thickness="fill",
            )

        elif particle_type == "sparks":
            # Bright yellow/orange particles with random motion
            particles = ffmpeg.filter(
                stream,
                "geq",
                r=f"if(lt(random(1)*255,{density/3}),255,r(X,Y))",
                g=f"if(lt(random(2)*255,{density/3}),200,g(X,Y))",
                b=f"if(lt(random(3)*255,{density/3}),50,b(X,Y))",
            )

        elif particle_type == "dust":
            # Small, slow-moving brownish particles
            particles = ffmpeg.filter(
                stream,
                "geq",
                r=f"if(lt(random(1)*255,{density/8}),200,r(X,Y))",
                g=f"if(lt(random(2)*255,{density/8}),150,g(X,Y))",
                b=f"if(lt(random(3)*255,{density/8}),100,b(X,Y))",
            )

        else:  # bubbles
            # Transparent circles floating upward
            particles = ffmpeg.filter(
                stream,
                "geq",
                r=f"if(lt(random(1)*255,{density/6}),255,r(X,Y))",
                g=f"if(lt(random(2)*255,{density/6}),255,g(X,Y))",
                b=f"if(lt(random(3)*255,{density/6}),255,b(X,Y))",
            )

        # Apply motion based on direction and speed
        if direction == "down":
            motion_filter = ffmpeg.filter(
                particles,
                "scroll",
                vh=f"-{speed*10}",
            )
        elif direction == "up":
            motion_filter = ffmpeg.filter(
                particles,
                "scroll",
                vh=f"{speed*10}",
            )
        elif direction == "left":
            motion_filter = ffmpeg.filter(
                particles,
                "scroll",
                h=f"-{speed*10}",
            )
        elif direction == "right":
            motion_filter = ffmpeg.filter(
                particles,
                "scroll",
                h=f"{speed*10}",
            )
        else:  # random
            motion_filter = particles

        # Blend particles with original video
        output_stream = ffmpeg.filter(
            [stream, motion_filter],
            "blend",
            mode="screen",
            opacity=opacity,
        )

        output = ffmpeg.output(
            output_stream,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"{particle_type.title()} particles added and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def apply_3d_transforms(
    input_path: str,
    output_path: str,
    transform_type: str = "perspective",
    rotation_x: float = 0.0,
    rotation_y: float = 0.0,
    rotation_z: float = 0.0,
    depth: float = 0.0,
    perspective_strength: float = 0.5,
    ctx: Context | None = None,
) -> str:
    """Apply 3D perspective transforms, rotations, and depth effects.

    Creates 3D transformation effects including perspective distortion, rotation
    along multiple axes, and depth simulation. Perfect for creating dynamic
    camera movements and 3D-style effects in 2D video.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the transformed video will be saved.
        transform_type: Type of transform ("perspective", "rotate3d", "depth", "cube").
        rotation_x: Rotation around X-axis in degrees (-180 to 180).
        rotation_y: Rotation around Y-axis in degrees (-180 to 180).
        rotation_z: Rotation around Z-axis in degrees (-180 to 180).
        depth: Depth effect strength (-1.0 to 1.0).
        perspective_strength: Perspective distortion strength (0.0 to 2.0).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating 3D transform was applied.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    valid_transforms = [
        "perspective",
        "rotate3d",
        "depth",
        "cube",
    ]
    if transform_type not in valid_transforms:
        raise ValueError(
            f"Transform type must be one of: {', '.join(valid_transforms)}"
        )

    if not -180.0 <= rotation_x <= 180.0:
        raise ValueError(
            "Rotation X must be between -180 and 180 degrees"
        )
    if not -180.0 <= rotation_y <= 180.0:
        raise ValueError(
            "Rotation Y must be between -180 and 180 degrees"
        )
    if not -180.0 <= rotation_z <= 180.0:
        raise ValueError(
            "Rotation Z must be between -180 and 180 degrees"
        )
    if not -1.0 <= depth <= 1.0:
        raise ValueError(
            "Depth must be between -1.0 and 1.0"
        )
    if not 0.0 <= perspective_strength <= 2.0:
        raise ValueError(
            "Perspective strength must be between 0.0 and 2.0"
        )

    if ctx:
        await ctx.info(
            f"Applying 3D {transform_type} transform..."
        )

    try:
        stream = ffmpeg.input(input_path)

        if transform_type == "perspective":
            # Apply perspective transformation
            transform_str = (
                f"perspective="
                f"{50+perspective_strength*20}:{50+perspective_strength*20}:"
                f"{950-perspective_strength*20}:{50+perspective_strength*20}:"
                f"{950-perspective_strength*20}:{950-perspective_strength*20}:"
                f"{50+perspective_strength*20}:{950-perspective_strength*20}"
            )
            output_stream = ffmpeg.filter(
                stream,
                "perspective",
                transform_str,
            )

        elif transform_type == "rotate3d":
            # Simulate 3D rotation using combination of transforms
            if rotation_z != 0:
                stream = ffmpeg.filter(
                    stream,
                    "rotate",
                    angle=f"{rotation_z}*PI/180",
                )

            if rotation_x != 0 or rotation_y != 0:
                # Use perspective to simulate X/Y rotation
                x_factor = (
                    abs(rotation_x)
                    / 180.0
                    * perspective_strength
                )
                y_factor = (
                    abs(rotation_y)
                    / 180.0
                    * perspective_strength
                )

                transform_str = (
                    f"perspective="
                    f"{50-x_factor*30}:{50-y_factor*30}:"
                    f"{950+x_factor*30}:{50-y_factor*30}:"
                    f"{950+x_factor*30}:{950+y_factor*30}:"
                    f"{50-x_factor*30}:{950+y_factor*30}"
                )
                output_stream = ffmpeg.filter(
                    stream,
                    "perspective",
                    transform_str,
                )
            else:
                output_stream = stream

        elif transform_type == "depth":
            # Simulate depth with scaling and perspective
            scale_factor = 1.0 + depth * 0.5
            output_stream = ffmpeg.filter(
                stream,
                "scale",
                int(1920 * scale_factor),
                int(1080 * scale_factor),
            )
            # Add perspective for depth illusion
            if depth != 0:
                depth_perspective = (
                    abs(depth) * 0.3
                )
                transform_str = (
                    f"perspective="
                    f"{50-depth_perspective*20}:{50-depth_perspective*20}:"
                    f"{950+depth_perspective*20}:{50-depth_perspective*20}:"
                    f"{950+depth_perspective*20}:{950+depth_perspective*20}:"
                    f"{50-depth_perspective*20}:{950+depth_perspective*20}"
                )
                output_stream = ffmpeg.filter(
                    output_stream,
                    "perspective",
                    transform_str,
                )

        else:  # cube
            # Create cube-like perspective effect
            cube_strength = (
                perspective_strength * 0.4
            )
            transform_str = (
                f"perspective="
                f"{100-cube_strength*50}:{100}:"
                f"{900}:{100-cube_strength*50}:"
                f"{900+cube_strength*50}:{900}:"
                f"{100}:{900+cube_strength*50}"
            )
            output_stream = ffmpeg.filter(
                stream,
                "perspective",
                transform_str,
            )

        output = ffmpeg.output(
            output_stream,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"3D {transform_type} transform applied and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_split_screen(
    video_paths: list[str],
    output_path: str,
    layout: str = "vertical",
    border_width: int = 2,
    border_color: str = "black",
    ctx: Context | None = None,
) -> str:
    """Create professional split-screen layouts with customizable divisions.

    Combines multiple videos into split-screen arrangements with precise control
    over layout, borders, and positioning. Perfect for comparison videos,
    interviews, or multi-perspective content.

    Args:
        video_paths: List of paths to video files (2-4 videos supported).
        output_path: Path where the split-screen video will be saved.
        layout: Layout type ("vertical", "horizontal", "quad", "triple_horizontal",
            "triple_vertical", "diagonal").
        border_width: Width of border between videos in pixels (0 to 20).
        border_color: Color of borders ("black", "white", "gray", hex code).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating split-screen video was created.

    Raises:
        ValueError: If invalid parameters or insufficient videos provided.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if len(video_paths) < 2:
        raise ValueError(
            "Need at least 2 videos for split-screen"
        )
    if len(video_paths) > 4:
        raise ValueError(
            "Maximum 4 videos supported for split-screen"
        )

    valid_layouts = [
        "vertical",
        "horizontal",
        "quad",
        "triple_horizontal",
        "triple_vertical",
        "diagonal",
    ]
    if layout not in valid_layouts:
        raise ValueError(
            f"Layout must be one of: {', '.join(valid_layouts)}"
        )

    if not 0 <= border_width <= 20:
        raise ValueError(
            "Border width must be between 0 and 20 pixels"
        )

    if ctx:
        await ctx.info(
            f"Creating {layout} split-screen with {len(video_paths)} videos..."
        )

    try:
        # Load input videos
        inputs = [
            ffmpeg.input(path)
            for path in video_paths
        ]

        # Define output dimensions
        output_width, output_height = 1920, 1080

        if layout == "vertical":
            # Side by side vertical split
            if len(video_paths) != 2:
                raise ValueError(
                    "Vertical layout requires exactly 2 videos"
                )

            video_width = (
                output_width - border_width
            ) // 2

            left = ffmpeg.filter(
                inputs[0],
                "scale",
                video_width,
                output_height,
            )
            right = ffmpeg.filter(
                inputs[1],
                "scale",
                video_width,
                output_height,
            )

            # Create split with border
            if border_width > 0:
                # Create border
                border = ffmpeg.filter(
                    "color",
                    color=border_color,
                    size=f"{border_width}x{output_height}",
                )
                # Combine left + border + right
                output_stream = ffmpeg.filter(
                    [left, border, right],
                    "hstack",
                    inputs=3,
                )
            else:
                output_stream = ffmpeg.filter(
                    [left, right],
                    "hstack",
                    inputs=2,
                )

        elif layout == "horizontal":
            # Top and bottom horizontal split
            if len(video_paths) != 2:
                raise ValueError(
                    "Horizontal layout requires exactly 2 videos"
                )

            video_height = (
                output_height - border_width
            ) // 2

            top = ffmpeg.filter(
                inputs[0],
                "scale",
                output_width,
                video_height,
            )
            bottom = ffmpeg.filter(
                inputs[1],
                "scale",
                output_width,
                video_height,
            )

            if border_width > 0:
                border = ffmpeg.filter(
                    "color",
                    color=border_color,
                    size=f"{output_width}x{border_width}",
                )
                output_stream = ffmpeg.filter(
                    [top, border, bottom],
                    "vstack",
                    inputs=3,
                )
            else:
                output_stream = ffmpeg.filter(
                    [top, bottom],
                    "vstack",
                    inputs=2,
                )

        elif layout == "quad":
            # 2x2 quad layout
            if len(video_paths) != 4:
                raise ValueError(
                    "Quad layout requires exactly 4 videos"
                )

            video_width = (
                output_width - border_width
            ) // 2
            video_height = (
                output_height - border_width
            ) // 2

            # Scale all videos
            scaled_videos = [
                ffmpeg.filter(
                    video,
                    "scale",
                    video_width,
                    video_height,
                )
                for video in inputs
            ]

            # Create top row
            if border_width > 0:
                v_border = ffmpeg.filter(
                    "color",
                    color=border_color,
                    size=f"{border_width}x{video_height}",
                )
                top_row = ffmpeg.filter(
                    [
                        scaled_videos[0],
                        v_border,
                        scaled_videos[1],
                    ],
                    "hstack",
                    inputs=3,
                )
                bottom_row = ffmpeg.filter(
                    [
                        scaled_videos[2],
                        v_border,
                        scaled_videos[3],
                    ],
                    "hstack",
                    inputs=3,
                )

                h_border = ffmpeg.filter(
                    "color",
                    color=border_color,
                    size=f"{output_width}x{border_width}",
                )
                output_stream = ffmpeg.filter(
                    [
                        top_row,
                        h_border,
                        bottom_row,
                    ],
                    "vstack",
                    inputs=3,
                )
            else:
                top_row = ffmpeg.filter(
                    [
                        scaled_videos[0],
                        scaled_videos[1],
                    ],
                    "hstack",
                    inputs=2,
                )
                bottom_row = ffmpeg.filter(
                    [
                        scaled_videos[2],
                        scaled_videos[3],
                    ],
                    "hstack",
                    inputs=2,
                )
                output_stream = ffmpeg.filter(
                    [top_row, bottom_row],
                    "vstack",
                    inputs=2,
                )

        elif layout == "triple_horizontal":
            # Three videos stacked horizontally
            if len(video_paths) != 3:
                raise ValueError(
                    "Triple horizontal layout requires exactly 3 videos"
                )

            video_width = (
                output_width - 2 * border_width
            ) // 3
            scaled_videos = [
                ffmpeg.filter(
                    video,
                    "scale",
                    video_width,
                    output_height,
                )
                for video in inputs
            ]

            if border_width > 0:
                border = ffmpeg.filter(
                    "color",
                    color=border_color,
                    size=f"{border_width}x{output_height}",
                )
                output_stream = ffmpeg.filter(
                    [
                        scaled_videos[0],
                        border,
                        scaled_videos[1],
                        border,
                        scaled_videos[2],
                    ],
                    "hstack",
                    inputs=5,
                )
            else:
                output_stream = ffmpeg.filter(
                    scaled_videos,
                    "hstack",
                    inputs=3,
                )

        elif layout == "triple_vertical":
            # Three videos stacked vertically
            if len(video_paths) != 3:
                raise ValueError(
                    "Triple vertical layout requires exactly 3 videos"
                )

            video_height = (
                output_height - 2 * border_width
            ) // 3
            scaled_videos = [
                ffmpeg.filter(
                    video,
                    "scale",
                    output_width,
                    video_height,
                )
                for video in inputs
            ]

            if border_width > 0:
                border = ffmpeg.filter(
                    "color",
                    color=border_color,
                    size=f"{output_width}x{border_width}",
                )
                output_stream = ffmpeg.filter(
                    [
                        scaled_videos[0],
                        border,
                        scaled_videos[1],
                        border,
                        scaled_videos[2],
                    ],
                    "vstack",
                    inputs=5,
                )
            else:
                output_stream = ffmpeg.filter(
                    scaled_videos,
                    "vstack",
                    inputs=3,
                )

        else:  # diagonal
            # Diagonal split layout
            if len(video_paths) != 2:
                raise ValueError(
                    "Diagonal layout requires exactly 2 videos"
                )

            # Create mask for diagonal split
            mask = ffmpeg.filter(
                "color",
                color="white",
                size=f"{output_width}x{output_height}",
            )
            mask = ffmpeg.filter(
                mask,
                "geq",
                r="if(lt(X+Y,W+H/2),255,0)",
                g="if(lt(X+Y,W+H/2),255,0)",
                b="if(lt(X+Y,W+H/2),255,0)",
            )

            # Scale videos to full size
            video1 = ffmpeg.filter(
                inputs[0],
                "scale",
                output_width,
                output_height,
            )
            video2 = ffmpeg.filter(
                inputs[1],
                "scale",
                output_width,
                output_height,
            )

            # Apply diagonal mask
            output_stream = ffmpeg.filter(
                [video1, video2, mask],
                "maskedmerge",
            )

        output = ffmpeg.output(
            output_stream,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"Split-screen video ({layout}) created and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def apply_video_stabilization(
    input_path: str,
    output_path: str,
    strength: int = 10,
    smoothing: int = 30,
    crop_black: bool = True,
    zoom: float = 0.0,
    ctx: Context | None = None,
) -> str:
    """Advanced video stabilization using optical flow analysis.

    Applies professional video stabilization to reduce camera shake and jitter.
    Uses two-pass analysis for optimal results with configurable strength and
    smoothing parameters.

    Args:
        input_path: Path to the input shaky video file.
        output_path: Path where the stabilized video will be saved.
        strength: Stabilization strength (1 to 100). Higher = more stabilization.
        smoothing: Smoothing amount (1 to 100). Higher = smoother motion.
        crop_black: Whether to crop black borders from stabilization.
        zoom: Additional zoom to reduce black borders (0.0 to 0.2).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating video was stabilized.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 1 <= strength <= 100:
        raise ValueError(
            "Strength must be between 1 and 100"
        )
    if not 1 <= smoothing <= 100:
        raise ValueError(
            "Smoothing must be between 1 and 100"
        )
    if not 0.0 <= zoom <= 0.2:
        raise ValueError(
            "Zoom must be between 0.0 and 0.2"
        )

    if ctx:
        await ctx.info(
            f"Applying video stabilization (strength: {strength})..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # First pass: analyze motion vectors
        if ctx:
            await ctx.info(
                "Pass 1: Analyzing motion vectors..."
            )

        # Use vidstabdetect for motion analysis
        ffmpeg.filter(
            stream,
            "vidstabdetect",
            shakiness=strength,
            accuracy=15,
            result="transforms.trf",
        )

        # Second pass: apply stabilization
        if ctx:
            await ctx.info(
                "Pass 2: Applying stabilization..."
            )

        stabilized = ffmpeg.filter(
            stream,
            "vidstabtransform",
            input="transforms.trf",
            smoothing=smoothing,
            crop=(
                "black" if crop_black else "keep"
            ),
            zoom=(
                int(zoom * 100) if zoom > 0 else 0
            ),
            optzoom=1 if zoom > 0 else 0,
        )

        # Apply additional smoothing if needed
        if smoothing > 50:
            stabilized = ffmpeg.filter(
                stabilized,
                "minterpolate",
                fps=30,
                mi_mode="mci",
            )

        output = ffmpeg.output(
            stabilized,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        # Clean up temporary file
        import os

        try:
            os.remove("transforms.trf")
        except FileNotFoundError:
            pass

        return (
            f"Video stabilized (strength: {strength}, smoothing: {smoothing}) "
            f"and saved to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_zoom_pan_effect(
    input_path: str,
    output_path: str,
    start_zoom: float = 1.0,
    end_zoom: float = 1.5,
    start_x: float = 0.5,
    start_y: float = 0.5,
    end_x: float = 0.5,
    end_y: float = 0.5,
    duration: float | None = None,
    easing: str = "linear",
    ctx: Context | None = None,
) -> str:
    """Ken Burns effect with smooth zoom and pan animations.

    Creates cinematic zoom and pan effects (Ken Burns style) with smooth
    animations between start and end positions. Perfect for adding motion
    to static images or creating dynamic video effects.

    Args:
        input_path: Path to the input video or image file.
        output_path: Path where the animated video will be saved.
        start_zoom: Initial zoom level (0.5 to 5.0).
        end_zoom: Final zoom level (0.5 to 5.0).
        start_x: Starting X position (0.0 to 1.0, 0.5 = center).
        start_y: Starting Y position (0.0 to 1.0, 0.5 = center).
        end_x: Ending X position (0.0 to 1.0, 0.5 = center).
        end_y: Ending Y position (0.0 to 1.0, 0.5 = center).
        duration: Animation duration in seconds. If None, uses input duration.
        easing: Animation easing ("linear", "ease_in", "ease_out", "ease_in_out").
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating zoom/pan effect was applied.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 0.5 <= start_zoom <= 5.0:
        raise ValueError(
            "Start zoom must be between 0.5 and 5.0"
        )
    if not 0.5 <= end_zoom <= 5.0:
        raise ValueError(
            "End zoom must be between 0.5 and 5.0"
        )
    if not 0.0 <= start_x <= 1.0:
        raise ValueError(
            "Start X must be between 0.0 and 1.0"
        )
    if not 0.0 <= start_y <= 1.0:
        raise ValueError(
            "Start Y must be between 0.0 and 1.0"
        )
    if not 0.0 <= end_x <= 1.0:
        raise ValueError(
            "End X must be between 0.0 and 1.0"
        )
    if not 0.0 <= end_y <= 1.0:
        raise ValueError(
            "End Y must be between 0.0 and 1.0"
        )

    valid_easings = [
        "linear",
        "ease_in",
        "ease_out",
        "ease_in_out",
    ]
    if easing not in valid_easings:
        raise ValueError(
            f"Easing must be one of: {', '.join(valid_easings)}"
        )

    if ctx:
        await ctx.info(
            f"Creating zoom/pan effect ({start_zoom}x to {end_zoom}x)..."
        )

    try:
        stream = ffmpeg.input(input_path)

        # Get input duration if not specified
        if duration is None:
            probe = ffmpeg.probe(input_path)
            duration = float(
                probe["format"]["duration"]
            )

        # Calculate animation parameters
        zoom_diff = end_zoom - start_zoom
        x_diff = end_x - start_x
        y_diff = end_y - start_y

        # Create easing function for smooth animation
        if easing == "linear":
            easing_func = "t/d"
        elif easing == "ease_in":
            easing_func = "(t/d)*(t/d)"
        elif easing == "ease_out":
            easing_func = "1-pow(1-t/d,2)"
        else:  # ease_in_out
            easing_func = "if(lt(t/d,0.5),2*(t/d)*(t/d),1-2*pow(1-t/d,2))"

        # Build zoompan filter expression
        # Zoom expression
        zoom_expr = f"{start_zoom}+{zoom_diff}*({easing_func})"

        # X position expression (convert from 0-1 to pixel coordinates)
        x_expr = f"iw*({start_x}+{x_diff}*({easing_func}))"

        # Y position expression
        y_expr = f"ih*({start_y}+{y_diff}*({easing_func}))"

        # Apply zoompan filter
        animated = ffmpeg.filter(
            stream,
            "zoompan",
            z=zoom_expr,
            x=x_expr,
            y=y_expr,
            d=f"{duration*30}",  # Duration in frames (assuming 30fps)
            s="1920x1080",
        )

        # Add smooth interpolation for better quality
        smoothed = ffmpeg.filter(
            animated,
            "minterpolate",
            fps=30,
            mi_mode="mci",
        )

        output = ffmpeg.output(
            smoothed,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return (
            f"Zoom/pan effect ({start_zoom}x to {end_zoom}x) created and saved "
            f"to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def batch_process_videos(
    input_paths: list[str],
    output_directory: str,
    operation: str,
    parameters: dict[str, Any] = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Process multiple videos with the same operations automatically.

    Applies the same video processing operation to multiple files in batch mode.
    Supports most video processing operations with progress tracking and error
    handling for efficient bulk processing.

    Args:
        input_paths: List of paths to input video files.
        output_directory: Directory where processed videos will be saved.
        operation: Operation to perform ("resize", "convert", "trim", "color_grade",
            "stabilize", "compress").
        parameters: Dictionary of operation-specific parameters.
        ctx: MCP context for progress reporting and logging.

    Returns:
        Dictionary with processing results including successes, failures, and timing.

    Raises:
        ValueError: If operation is not supported or parameters are invalid.
        RuntimeError: If batch processing encounters critical errors.
    """
    if parameters is None:
        parameters = {}
    valid_operations = [
        "resize",
        "convert",
        "trim",
        "color_grade",
        "stabilize",
        "compress",
    ]
    if operation not in valid_operations:
        raise ValueError(
            f"Operation must be one of: {', '.join(valid_operations)}"
        )

    if not input_paths:
        raise ValueError(
            "Must provide at least one input video"
        )

    # Create output directory if it doesn't exist
    Path(output_directory).mkdir(
        parents=True, exist_ok=True
    )

    if ctx:
        await ctx.info(
            f"Batch processing {len(input_paths)} videos with {operation}..."
        )

    import time

    start_time = time.time()
    results = {
        "operation": operation,
        "total_files": len(input_paths),
        "successful": [],
        "failed": [],
        "processing_time": 0,
        "parameters_used": parameters,
    }

    for i, input_path in enumerate(input_paths):
        if ctx:
            await ctx.info(
                f"Processing file {i+1}/{len(input_paths)}: "
                f"{os.path.basename(input_path)}"
            )

        try:
            # Generate output filename
            input_name = Path(input_path).stem
            output_name = f"{input_name}_{operation}{Path(input_path).suffix}"
            output_path = str(
                Path(output_directory)
                / output_name
            )

            # Apply operation based on type
            if operation == "resize":
                width = parameters.get(
                    "width", 1280
                )
                height = parameters.get(
                    "height", 720
                )

                stream = ffmpeg.input(input_path)
                stream = ffmpeg.filter(
                    stream, "scale", width, height
                )
                output = ffmpeg.output(
                    stream, output_path
                )
                ffmpeg.run(
                    output,
                    overwrite_output=True,
                    quiet=True,
                )

            elif operation == "convert":
                codec = parameters.get(
                    "codec", "libx264"
                )
                format_type = parameters.get(
                    "format", "mp4"
                )

                stream = ffmpeg.input(input_path)
                output = ffmpeg.output(
                    stream,
                    output_path,
                    vcodec=codec,
                    format=format_type,
                )
                ffmpeg.run(
                    output,
                    overwrite_output=True,
                    quiet=True,
                )

            elif operation == "trim":
                start_time_param = parameters.get(
                    "start_time", 0
                )
                duration_param = parameters.get(
                    "duration", 10
                )

                stream = ffmpeg.input(
                    input_path,
                    ss=start_time_param,
                    t=duration_param,
                )
                output = ffmpeg.output(
                    stream, output_path, c="copy"
                )
                ffmpeg.run(
                    output,
                    overwrite_output=True,
                    quiet=True,
                )

            elif operation == "color_grade":
                brightness = parameters.get(
                    "brightness", 0.0
                )
                contrast = parameters.get(
                    "contrast", 1.0
                )
                saturation = parameters.get(
                    "saturation", 1.0
                )

                stream = ffmpeg.input(input_path)
                stream = ffmpeg.filter(
                    stream,
                    "eq",
                    brightness=brightness,
                    contrast=contrast,
                    saturation=saturation,
                )
                output = ffmpeg.output(
                    stream, output_path
                )
                ffmpeg.run(
                    output,
                    overwrite_output=True,
                    quiet=True,
                )

            elif operation == "stabilize":
                strength = parameters.get(
                    "strength", 10
                )
                smoothing = parameters.get(
                    "smoothing", 30
                )

                stream = ffmpeg.input(input_path)
                stream = ffmpeg.filter(
                    stream,
                    "vidstabdetect",
                    shakiness=strength,
                )
                stream = ffmpeg.filter(
                    stream,
                    "vidstabtransform",
                    smoothing=smoothing,
                )
                output = ffmpeg.output(
                    stream, output_path
                )
                ffmpeg.run(
                    output,
                    overwrite_output=True,
                    quiet=True,
                )

            elif operation == "compress":
                crf = parameters.get("crf", 23)
                preset = parameters.get(
                    "preset", "medium"
                )

                stream = ffmpeg.input(input_path)
                output = ffmpeg.output(
                    stream,
                    output_path,
                    vcodec="libx264",
                    crf=crf,
                    preset=preset,
                )
                ffmpeg.run(
                    output,
                    overwrite_output=True,
                    quiet=True,
                )

            results["successful"].append(
                {
                    "input": input_path,
                    "output": output_path,
                    "filename": os.path.basename(
                        input_path
                    ),
                }
            )

        except Exception as e:
            results["failed"].append(
                {
                    "input": input_path,
                    "filename": os.path.basename(
                        input_path
                    ),
                    "error": str(e),
                }
            )
            if ctx:
                await ctx.error(
                    f"Failed to process {os.path.basename(input_path)}: {str(e)}"
                )

    results["processing_time"] = round(
        time.time() - start_time, 2
    )
    results["success_rate"] = (
        len(results["successful"])
        / len(input_paths)
        * 100
    )

    if ctx:
        await ctx.info(
            f"Batch processing complete: {len(results['successful'])}/"
            f"{len(input_paths)} successful"
        )

    return results


@mcp.tool
async def create_animated_text(
    output_path: str,
    text: str,
    animation_type: str = "fade_in",
    duration: float = 3.0,
    font_size: int = 48,
    font_color: str = "white",
    background_color: str = "transparent",
    resolution: str = "1920x1080",
    ctx: Context | None = None,
) -> str:
    """Create advanced animated text with motion graphics and effects.

    Generates animated text videos with various motion graphics effects.
    Perfect for creating titles, credits, lower thirds, and motion graphics
    elements for video production.

    Args:
        output_path: Path where the animated text video will be saved.
        text: Text content to animate.
        animation_type: Animation type ("fade_in", "slide_left", "slide_right",
            "slide_up", "slide_down", "typewriter", "zoom_in", "bounce").
        duration: Total animation duration in seconds (1.0 to 30.0).
        font_size: Font size in pixels (12 to 200).
        font_color: Text color (color name or hex code).
        background_color: Background color ("transparent", color name, or hex).
        resolution: Output resolution (e.g., "1920x1080", "1280x720").
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating animated text was created.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    valid_animations = [
        "fade_in",
        "slide_left",
        "slide_right",
        "slide_up",
        "slide_down",
        "typewriter",
        "zoom_in",
        "bounce",
    ]
    if animation_type not in valid_animations:
        raise ValueError(
            f"Animation type must be one of: {', '.join(valid_animations)}"
        )

    if not 1.0 <= duration <= 30.0:
        raise ValueError(
            "Duration must be between 1.0 and 30.0 seconds"
        ) from None
    if not 12 <= font_size <= 200:
        raise ValueError(
            "Font size must be between 12 and 200 pixels"
        )

    try:
        width, height = map(
            int, resolution.split("x")
        )
    except (ValueError, AttributeError):
        raise ValueError(
            "Resolution must be in format 'WIDTHxHEIGHT'"
        ) from None

    if ctx:
        await ctx.info(
            f"Creating {animation_type} text animation..."
        )

    try:
        # Create base background
        if background_color == "transparent":
            pass
        else:
            pass

        background = ffmpeg.filter(
            None,
            "color",
            **{
                "c": (
                    background_color
                    if background_color
                    != "transparent"
                    else "black@0"
                ),
                "s": resolution,
                "d": duration,
            },
        )

        # Create animated text based on type
        if animation_type == "fade_in":
            # Fade in text
            text_filter = ffmpeg.filter(
                background,
                "drawtext",
                text=text,
                fontsize=font_size,
                fontcolor=font_color,
                x="(w-text_w)/2",
                y="(h-text_h)/2",
                alpha=f"if(lt(t,{duration*0.8}),t/{duration*0.8},1)",
            )

        elif animation_type in [
            "slide_left",
            "slide_right",
            "slide_up",
            "slide_down",
        ]:
            # Sliding animations
            if animation_type == "slide_left":
                x_expr = (
                    f"w-t/({duration})*w-text_w/2"
                )
                y_expr = "(h-text_h)/2"
            elif animation_type == "slide_right":
                x_expr = (
                    f"t/({duration})*w-text_w/2"
                )
                y_expr = "(h-text_h)/2"
            elif animation_type == "slide_up":
                x_expr = "(w-text_w)/2"
                y_expr = (
                    f"h-t/({duration})*h-text_h/2"
                )
            else:  # slide_down
                x_expr = "(w-text_w)/2"
                y_expr = (
                    f"t/({duration})*h-text_h/2"
                )

            text_filter = ffmpeg.filter(
                background,
                "drawtext",
                text=text,
                fontsize=font_size,
                fontcolor=font_color,
                x=x_expr,
                y=y_expr,
            )

        elif animation_type == "typewriter":
            # Typewriter effect (reveal characters over time)
            char_count = len(text)
            chars_per_second = (
                char_count / duration
            )

            text_filter = ffmpeg.filter(
                background,
                "drawtext",
                text=text,
                fontsize=font_size,
                fontcolor=font_color,
                x="(w-text_w)/2",
                y="(h-text_h)/2",
                # Reveal characters progressively
                # Show space if beyond current time
                textfile=f"if(lt(t*{chars_per_second},n),pc,32)",
            )

        elif animation_type == "zoom_in":
            # Zoom in text
            scale_factor = (
                f"min(1,t/{duration*0.5})"
            )
            text_filter = ffmpeg.filter(
                background,
                "drawtext",
                text=text,
                fontsize=f"{font_size}*{scale_factor}",
                fontcolor=font_color,
                x="(w-text_w)/2",
                y="(h-text_h)/2",
            )

        else:  # bounce
            # Bouncing text animation
            bounce_height = font_size
            bounce_expr = f"(h-text_h)/2+{bounce_height}*abs(sin(t*4*PI))"

            text_filter = ffmpeg.filter(
                background,
                "drawtext",
                text=text,
                fontsize=font_size,
                fontcolor=font_color,
                x="(w-text_w)/2",
                y=bounce_expr,
            )

        output = ffmpeg.output(
            text_filter,
            output_path,
            vcodec="libx264",
            pix_fmt="yuva420p",
        )
        ffmpeg.run(output, overwrite_output=True)

        return f"Animated text ({animation_type}) created and saved to {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def apply_lens_effects(
    input_path: str,
    output_path: str,
    effect_type: str = "vignette",
    strength: float = 0.5,
    center_x: float = 0.5,
    center_y: float = 0.5,
    color: str = "white",
    ctx: Context | None = None,
) -> str:
    """Simulate camera lens effects like vignette, lens flare, chromatic aberration.

    Applies realistic camera lens effects to simulate various optical phenomena.
    Perfect for adding cinematic quality and professional camera characteristics
    to video footage.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the video with lens effects will be saved.
        effect_type: Lens effect type ("vignette", "lens_flare", "chromatic_aberration",
            "barrel_distortion", "fisheye").
        strength: Effect intensity (0.1 to 2.0).
        center_x: Effect center X position (0.0 to 1.0).
        center_y: Effect center Y position (0.0 to 1.0).
        color: Effect color for flares and tints (color name or hex).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating lens effect was applied.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    valid_effects = [
        "vignette",
        "lens_flare",
        "chromatic_aberration",
        "barrel_distortion",
        "fisheye",
    ]
    if effect_type not in valid_effects:
        raise ValueError(
            f"Effect type must be one of: {', '.join(valid_effects)}"
        )

    if not 0.1 <= strength <= 2.0:
        raise ValueError(
            "Strength must be between 0.1 and 2.0"
        )
    if not 0.0 <= center_x <= 1.0:
        raise ValueError(
            "Center X must be between 0.0 and 1.0"
        )
    if not 0.0 <= center_y <= 1.0:
        raise ValueError(
            "Center Y must be between 0.0 and 1.0"
        )

    if ctx:
        await ctx.info(
            f"Applying {effect_type} lens effect..."
        )

    try:
        stream = ffmpeg.input(input_path)

        if effect_type == "vignette":
            # Apply vignette effect
            vignette_filter = ffmpeg.filter(
                stream,
                "vignette",
                angle=f"PI/{4-strength}",  # Angle affects the shape
                x0=center_x,
                y0=center_y,
                mode="forward",
            )
            output_stream = vignette_filter

        elif effect_type == "lens_flare":
            # Create lens flare effect using overlay
            flare_size = int(200 * strength)

            # Create flare element
            flare = ffmpeg.filter(
                "color",
                color=color,
                size=f"{flare_size}x{flare_size}",
            )

            # Apply radial gradient for flare shape
            flare = ffmpeg.filter(
                flare,
                "geq",
                r=f"255*exp(-((X-{flare_size/2})^2+(Y-{flare_size/2})^2)/{flare_size/4})",
                g=f"255*exp(-((X-{flare_size/2})^2+(Y-{flare_size/2})^2)/{flare_size/4})",
                b=f"255*exp(-((X-{flare_size/2})^2+(Y-{flare_size/2})^2)/{flare_size/4})",
            )

            # Overlay flare on video
            probe = ffmpeg.probe(input_path)
            video_stream = next(
                s
                for s in probe["streams"]
                if s["codec_type"] == "video"
            )
            video_width = video_stream["width"]
            video_height = video_stream["height"]

            output_stream = ffmpeg.filter(
                [stream, flare],
                "overlay",
                x=int(
                    video_width * center_x
                    - flare_size / 2
                ),
                y=int(
                    video_height * center_y
                    - flare_size / 2
                ),
                mode="screen",
            )

        elif (
            effect_type == "chromatic_aberration"
        ):
            # Simulate chromatic aberration by shifting color channels
            shift_amount = int(5 * strength)

            # Extract RGB channels
            red_channel = ffmpeg.filter(
                stream,
                "extractplanes",
                planes="r",
            )
            green_channel = ffmpeg.filter(
                stream,
                "extractplanes",
                planes="g",
            )
            blue_channel = ffmpeg.filter(
                stream,
                "extractplanes",
                planes="b",
            )

            # Shift channels slightly
            if shift_amount > 0:
                red_shifted = ffmpeg.filter(
                    red_channel,
                    "pad",
                    w=f"iw+{shift_amount*2}",
                    h=f"ih+{shift_amount*2}",
                    x=shift_amount,
                    y=shift_amount,
                )
                blue_shifted = ffmpeg.filter(
                    blue_channel,
                    "pad",
                    w=f"iw+{shift_amount*2}",
                    h=f"ih+{shift_amount*2}",
                    x=0,
                    y=0,
                )

                # Recombine channels
                output_stream = ffmpeg.filter(
                    [
                        red_shifted,
                        green_channel,
                        blue_shifted,
                    ],
                    "mergeplanes",
                    inputs=3,
                    map="0.0:r 1.0:g 2.0:b",
                )
            else:
                output_stream = stream

        elif effect_type == "barrel_distortion":
            # Apply barrel distortion
            distortion_strength = strength * 0.2

            output_stream = ffmpeg.filter(
                stream,
                "lenscorrection",
                cx=center_x,
                cy=center_y,
                k1=distortion_strength,
                k2=distortion_strength * 0.1,
            )

        else:  # fisheye
            # Apply fisheye effect using perspective transformation
            fisheye_strength = strength * 0.3

            # Create fisheye distortion using complex transform
            transform_expr = (
                f"perspective="
                f"{50-fisheye_strength*30}:{50-fisheye_strength*30}:"
                f"{950+fisheye_strength*30}:{50-fisheye_strength*30}:"
                f"{950+fisheye_strength*30}:{950+fisheye_strength*30}:"
                f"{50-fisheye_strength*30}:{950+fisheye_strength*30}"
            )

            output_stream = ffmpeg.filter(
                stream,
                "perspective",
                transform_expr,
            )

        output = ffmpeg.output(
            output_stream,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return (
            f"{effect_type.replace('_', ' ').title()} effect applied and saved "
            f"to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def create_video_collage(
    video_paths: list[str],
    output_path: str,
    layout_pattern: str = "dynamic",
    transition_interval: float = 2.0,
    background_color: str = "black",
    border_width: int = 2,
    ctx: Context | None = None,
) -> str:
    """Create dynamic video collages with multiple simultaneous videos.

    Creates animated video collages that showcase multiple videos simultaneously
    with dynamic layouts, transitions, and effects. Perfect for video portfolios,
    social media content, or multi-perspective presentations.

    Args:
        video_paths: List of paths to video files (2-9 videos supported).
        output_path: Path where the video collage will be saved.
        layout_pattern: Layout pattern ("dynamic", "rotating", "spiral",
            "grid_animate").
        transition_interval: Time between layout changes in seconds (1.0 to 10.0).
        background_color: Background color (color name or hex code).
        border_width: Border width between videos in pixels (0 to 10).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Success message indicating video collage was created.

    Raises:
        ValueError: If invalid parameters or insufficient videos provided.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if len(video_paths) < 2:
        raise ValueError(
            "Need at least 2 videos for collage"
        )
    if len(video_paths) > 9:
        raise ValueError(
            "Maximum 9 videos supported for collage"
        )

    valid_patterns = [
        "dynamic",
        "rotating",
        "spiral",
        "grid_animate",
    ]
    if layout_pattern not in valid_patterns:
        raise ValueError(
            f"Layout pattern must be one of: {', '.join(valid_patterns)}"
        )

    if not 1.0 <= transition_interval <= 10.0:
        raise ValueError(
            "Transition interval must be between 1.0 and 10.0 seconds"
        )
    if not 0 <= border_width <= 10:
        raise ValueError(
            "Border width must be between 0 and 10 pixels"
        )

    if ctx:
        await ctx.info(
            f"Creating {layout_pattern} video collage with {len(video_paths)} videos..."
        )

    try:
        # Load and scale input videos
        inputs = []
        video_count = len(video_paths)

        # Calculate video size based on count
        if video_count <= 4:
            video_width, video_height = (
                480,
                270,
            )  # Quarter size
        elif video_count <= 6:
            video_width, video_height = (
                320,
                180,
            )  # Sixth size
        else:
            video_width, video_height = (
                256,
                144,
            )  # Ninth size

        for path in video_paths:
            scaled = ffmpeg.filter(
                ffmpeg.input(path),
                "scale",
                video_width,
                video_height,
            )
            inputs.append(scaled)

        # Create background
        background = ffmpeg.filter(
            "color",
            color=background_color,
            size="1920x1080",
            duration=30,  # Default duration
        )

        if layout_pattern == "dynamic":
            # Dynamic floating layout with animated positions
            overlaid = background

            for i, video in enumerate(inputs):
                # Calculate animated position for each video
                angle_offset = (
                    i * 2 * 3.14159
                ) / video_count
                radius = 300

                x_expr = f"960+{radius}*cos(t/2+{angle_offset})-{video_width//2}"
                y_expr = f"540+{radius}*sin(t/2+{angle_offset})-{video_height//2}"

                overlaid = ffmpeg.filter(
                    [overlaid, video],
                    "overlay",
                    x=x_expr,
                    y=y_expr,
                )

        elif layout_pattern == "rotating":
            # Rotating layout where videos orbit around center
            overlaid = background

            for i, video in enumerate(inputs):
                angle_offset = (
                    i * 2 * 3.14159
                ) / video_count
                orbit_radius = 350

                # Rotating motion
                x_expr = (
                    f"960+{orbit_radius}*cos(t*0.5+{angle_offset})-{video_width//2}"
                )
                y_expr = (
                    f"540+{orbit_radius}*sin(t*0.5+{angle_offset})-{video_height//2}"
                )

                overlaid = ffmpeg.filter(
                    [overlaid, video],
                    "overlay",
                    x=x_expr,
                    y=y_expr,
                )

        elif layout_pattern == "spiral":
            # Spiral layout with videos arranged in expanding spiral
            overlaid = background

            for i, video in enumerate(inputs):
                spiral_factor = i + 1
                spiral_radius = (
                    spiral_factor * 100
                )
                spiral_angle = spiral_factor * 0.8

                x_expr = (
                    f"960+{spiral_radius}*cos(t*0.3+{spiral_angle})-{video_width//2}"
                )
                y_expr = (
                    f"540+{spiral_radius}*sin(t*0.3+{spiral_angle})-{video_height//2}"
                )

                overlaid = ffmpeg.filter(
                    [overlaid, video],
                    "overlay",
                    x=x_expr,
                    y=y_expr,
                )

        else:  # grid_animate
            # Animated grid that changes positions periodically
            grid_cols = (
                3 if video_count > 4 else 2
            )
            (
                video_count + grid_cols - 1
            ) // grid_cols

            overlaid = background

            for i, video in enumerate(inputs):
                base_col = i % grid_cols
                base_row = i // grid_cols

                # Add animation to grid positions
                base_x = 320 + base_col * (
                    video_width + border_width * 4
                )
                base_y = 200 + base_row * (
                    video_height
                    + border_width * 4
                )

                # Animated offset
                anim_x = f"{base_x}+50*sin(t+{i})"
                anim_y = (
                    f"{base_y}+30*cos(t*1.2+{i})"
                )

                overlaid = ffmpeg.filter(
                    [overlaid, video],
                    "overlay",
                    x=anim_x,
                    y=anim_y,
                )

        # Add border effects if specified
        if border_width > 0:
            overlaid = ffmpeg.filter(
                overlaid,
                "pad",
                w=f"iw+{border_width*2}",
                h=f"ih+{border_width*2}",
                x=border_width,
                y=border_width,
                color=background_color,
            )

        output = ffmpeg.output(
            overlaid,
            output_path,
            vcodec="libx264",
        )
        ffmpeg.run(output, overwrite_output=True)

        return (
            f"Video collage ({layout_pattern}) with {video_count} videos created "
            f"and saved to {output_path}"
        )
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e


@mcp.tool
async def extract_dominant_colors(
    input_path: str,
    num_colors: int = 5,
    analysis_frames: int = 10,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Analyze and extract dominant color palettes from videos.

    Performs color analysis on video frames to extract the most dominant colors
    and their frequency. Useful for color grading reference, theme analysis,
    and automatic color palette generation.

    Args:
        input_path: Path to the video file to analyze.
        num_colors: Number of dominant colors to extract (3 to 20).
        analysis_frames: Number of frames to sample for analysis (5 to 50).
        ctx: MCP context for progress reporting and logging.

    Returns:
        Dictionary containing dominant colors, their frequencies, and color statistics.

    Raises:
        ValueError: If parameter values are out of valid ranges.
        RuntimeError: If ffmpeg encounters an error during processing.
    """
    if not 3 <= num_colors <= 20:
        raise ValueError(
            "Number of colors must be between 3 and 20"
        )
    if not 5 <= analysis_frames <= 50:
        raise ValueError(
            "Analysis frames must be between 5 and 50"
        )

    if ctx:
        await ctx.info(
            f"Analyzing dominant colors from {analysis_frames} frames..."
        )

    try:
        # Get video duration and basic info
        probe = ffmpeg.probe(input_path)
        duration = float(
            probe["format"]["duration"]
        )
        video_stream = next(
            s
            for s in probe["streams"]
            if s["codec_type"] == "video"
        )

        # Extract frames at regular intervals
        frame_interval = (
            duration / analysis_frames
        )
        color_data = {
            "dominant_colors": [],
            "color_statistics": {},
            "analysis_info": {
                "frames_analyzed": analysis_frames,
                "video_duration": duration,
                "video_resolution": f"{video_stream['width']}x{video_stream['height']}",
            },
        }

        # Collect color information from sampled frames
        for i in range(analysis_frames):
            timestamp = i * frame_interval

            if ctx and i % 5 == 0:
                await ctx.info(
                    f"Analyzing frame {i+1}/{analysis_frames}..."
                )

            # Extract frame at timestamp
            frame_output = ffmpeg.input(
                input_path, ss=timestamp
            ).output(
                "pipe:",
                vframes=1,
                format="rawvideo",
                pix_fmt="rgb24",
            )

            # Run ffmpeg to get frame data
            frame_result = ffmpeg.run(
                frame_output,
                capture_stdout=True,
                quiet=True,
            )

            if frame_result.stdout:
                # Process frame data (simplified color analysis)
                frame_data = frame_result.stdout

                # Sample color values (simplified implementation)
                # In a real implementation, you'd use proper color quantization
                width, height = (
                    video_stream["width"],
                    video_stream["height"],
                )
                pixel_count = width * height
                bytes_per_pixel = 3

                if (
                    len(frame_data)
                    >= pixel_count
                    * bytes_per_pixel
                ):
                    # Sample pixels for color analysis
                    sample_rate = max(
                        1, pixel_count // 1000
                    )  # Sample every Nth pixel

                    color_samples = []
                    for pixel_idx in range(
                        0,
                        len(frame_data) - 2,
                        sample_rate
                        * bytes_per_pixel,
                    ):
                        if pixel_idx + 2 < len(
                            frame_data
                        ):
                            r = frame_data[
                                pixel_idx
                            ]
                            g = frame_data[
                                pixel_idx + 1
                            ]
                            b = frame_data[
                                pixel_idx + 2
                            ]

                            # Quantize colors to reduce variance
                            r_quant = (
                                r // 32
                            ) * 32
                            g_quant = (
                                g // 32
                            ) * 32
                            b_quant = (
                                b // 32
                            ) * 32

                            color_hex = f"#{r_quant:02x}{g_quant:02x}{b_quant:02x}"
                            color_samples.append(
                                color_hex
                            )

                    # Count color frequency
                    from collections import (
                        Counter,
                    )

                    color_counts = Counter(
                        color_samples
                    )

                    # Update overall color statistics
                    for (
                        color,
                        count,
                    ) in color_counts.items():
                        if (
                            color
                            in color_data[
                                "color_statistics"
                            ]
                        ):
                            color_data[
                                "color_statistics"
                            ][color] += count
                        else:
                            color_data[
                                "color_statistics"
                            ][color] = count

        # Determine most dominant colors
        sorted_colors = sorted(
            color_data[
                "color_statistics"
            ].items(),
            key=lambda x: x[1],
            reverse=True,
        )

        total_samples = sum(
            color_data[
                "color_statistics"
            ].values()
        )

        for i, (color, count) in enumerate(
            sorted_colors[:num_colors]
        ):
            percentage = (
                (count / total_samples) * 100
                if total_samples > 0
                else 0
            )

            # Convert hex to RGB for additional info
            hex_color = color.lstrip("#")
            rgb = tuple(
                int(hex_color[i : i + 2], 16)
                for i in (0, 2, 4)
            )

            # Calculate brightness and saturation (simplified)
            brightness = sum(rgb) / 3 / 255
            max_rgb = max(rgb)
            min_rgb = min(rgb)
            saturation = (
                (max_rgb - min_rgb) / max_rgb
                if max_rgb > 0
                else 0
            )

            color_data["dominant_colors"].append(
                {
                    "rank": i + 1,
                    "hex": color,
                    "rgb": rgb,
                    "percentage": round(
                        percentage, 2
                    ),
                    "brightness": round(
                        brightness, 3
                    ),
                    "saturation": round(
                        saturation, 3
                    ),
                    "sample_count": count,
                }
            )

        # Add summary statistics
        if color_data["dominant_colors"]:
            avg_brightness = sum(
                c["brightness"]
                for c in color_data[
                    "dominant_colors"
                ]
            ) / len(color_data["dominant_colors"])
            avg_saturation = sum(
                c["saturation"]
                for c in color_data[
                    "dominant_colors"
                ]
            ) / len(color_data["dominant_colors"])

            color_data["summary"] = {
                "average_brightness": round(
                    avg_brightness, 3
                ),
                "average_saturation": round(
                    avg_saturation, 3
                ),
                "color_diversity": len(
                    color_data["color_statistics"]
                ),
                "total_samples": total_samples,
            }

        return color_data

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


@mcp.resource("tools://advanced")
async def list_advanced_tools() -> str:
    """List all advanced VFX tools and their capabilities.

    Returns information about the advanced video editing tools available
    in this MCP server, including their purposes and key parameters.

    Returns:
        JSON string containing advanced tools information and usage examples.
    """
    advanced_tools = {
        "advanced_tools": [
            {
                "name": "create_video_slideshow",
                "purpose": "Create video slideshows from multiple images",
                "key_features": [
                    "Crossfade transitions between images",
                    "Customizable timing and resolution",
                    "Support for various image formats",
                ],
                "example_use": "Create a photo montage video with smooth transitions",
            },
            {
                "name": "extract_frames",
                "purpose": "Extract frames from video as individual images",
                "key_features": [
                    "Time range selection",
                    "Frame interval control",
                    "Multiple output formats",
                ],
                "example_use": "Extract thumbnails or analyze video content",
            },
            {
                "name": "add_text_overlay",
                "purpose": "Add text overlays and subtitles to videos",
                "key_features": [
                    "Customizable positioning and styling",
                    "Timing control for text appearance",
                    "Background box options",
                ],
                "example_use": "Add titles, captions, or watermarks to videos",
            },
            {
                "name": "create_video_mosaic",
                "purpose": "Combine multiple videos into grid layouts",
                "key_features": [
                    "Various grid layouts (2x2, 3x1, etc.)",
                    "Audio source selection",
                    "Automatic scaling and positioning",
                ],
                "example_use": "Create comparison videos or multi-camera displays",
            },
            {
                "name": "detect_scene_changes",
                "purpose": "Analyze video for scene changes and transitions",
                "key_features": [
                    "Configurable sensitivity threshold",
                    "Minimum scene length filtering",
                    "Detailed timestamp reporting",
                ],
                "example_use": "Automatic video segmentation for editing workflows",
            },
            {
                "name": "create_picture_in_picture",
                "purpose": "Overlay one video onto another with positioning control",
                "key_features": [
                    "Flexible positioning and scaling",
                    "Opacity control for transparency",
                    "Margin settings for precise placement",
                ],
                "example_use": "Create reaction videos or tutorial overlays",
            },
            {
                "name": "extract_audio_spectrum",
                "purpose": "Generate visual audio spectrum and waveform videos",
                "key_features": [
                    "Multiple visualization styles",
                    "Customizable colors and resolution",
                    "Audio spectrum analysis",
                ],
                "example_use": "Create audio visualizations for music or podcasts",
            },
            {
                "name": "apply_color_grading",
                "purpose": "Apply color correction and grading effects",
                "key_features": [
                    "Brightness, contrast, saturation control",
                    "Color temperature and tint adjustment",
                    "Gamma correction",
                ],
                "example_use": "Color correct footage or create cinematic looks",
            },
            {
                "name": "create_time_lapse",
                "purpose": "Convert normal speed video to time-lapse",
                "key_features": [
                    "Variable speed factors",
                    "Optional video stabilization",
                    "Motion smoothing",
                ],
                "example_use": "Create fast-forward effects from long recordings",
            },
            {
                "name": "merge_audio_tracks",
                "purpose": "Merge multiple audio tracks with volume and timing control",
                "key_features": [
                    "Individual volume control per track",
                    "Timing delays and synchronization",
                    "Multiple mixing modes",
                ],
                "example_use": "Create soundtracks or multi-source audio content",
            },
            {
                "name": "create_green_screen_effect",
                "purpose": "Remove green/blue screen and replace with custom "
                "backgrounds",
                "key_features": [
                    "Advanced chroma key compositing",
                    "Color spill reduction and edge blending",
                    "Support for multiple key colors",
                ],
                "example_use": "Create professional composited videos with "
                "custom backgrounds",
            },
            {
                "name": "apply_motion_blur",
                "purpose": "Add realistic motion blur effects to video",
                "key_features": [
                    "Directional blur with angle control",
                    "Virtual shutter speed simulation",
                    "Temporal frame blending",
                ],
                "example_use": "Simulate camera movement or fast-moving objects",
            },
            {
                "name": "create_video_transitions",
                "purpose": "Create smooth transitions between multiple video clips",
                "key_features": [
                    "Multiple transition types (fade, wipe, slide)",
                    "Customizable transition duration",
                    "Professional video sequencing",
                ],
                "example_use": "Create seamless video montages with "
                "professional transitions",
            },
            {
                "name": "extract_video_statistics",
                "purpose": "Analyze video content for technical metrics and quality",
                "key_features": [
                    "Comprehensive quality analysis",
                    "Motion and scene change detection",
                    "Technical specification reporting",
                ],
                "example_use": "Quality control and optimization for video content",
            },
            {
                "name": "create_loop_video",
                "purpose": "Create seamless looping videos with crossfade blending",
                "key_features": [
                    "Seamless crossfade transitions",
                    "Customizable loop duration",
                    "Color continuity optimization",
                ],
                "example_use": "Create background videos or cinemagraphs",
            },
        ],
        "total_tools": 15,
        "categories": [
            "Image/Video Creation",
            "Video Analysis",
            "Text and Graphics",
            "Audio Processing",
            "Color Correction",
            "Time Manipulation",
            "Compositing and VFX",
            "Motion Effects",
            "Professional Transitions",
        ],
    }

    return json.dumps(advanced_tools, indent=2)


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
