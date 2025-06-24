"""Common utilities and helper functions for VFX operations."""

from pathlib import Path
from typing import Any

import ffmpeg
from fastmcp import Context


async def handle_ffmpeg_error(e: ffmpeg.Error, ctx: Context | None = None) -> None:
    """Standard error handling for ffmpeg operations."""
    stderr_msg = ""
    if e.stderr:
        try:
            stderr_msg = e.stderr.decode("utf-8")
        except Exception:
            stderr_msg = str(e.stderr)

    stdout_msg = ""
    if e.stdout:
        try:
            stdout_msg = e.stdout.decode("utf-8")
        except Exception:
            stdout_msg = str(e.stdout)

    error_msg = f"FFmpeg error: {stderr_msg or stdout_msg or str(e)}"
    if ctx:
        await ctx.error(error_msg)
    raise RuntimeError(error_msg) from e


async def log_operation(ctx: Context | None, message: str) -> None:
    """Log operation info if context is available."""
    if ctx:
        await ctx.info(message)


def get_video_metadata(
    video_path: str,
) -> dict[str, Any]:
    """Extract comprehensive video metadata using ffmpeg probe."""
    try:
        probe = ffmpeg.probe(video_path)
        format_info = probe.get("format", {})

        # Find video and audio streams
        video_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"),
            None,
        )
        audio_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "audio"),
            None,
        )

        metadata = {
            "filename": Path(format_info.get("filename", "")).name,
            "format": format_info.get("format_name", ""),
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bitrate": int(format_info.get("bit_rate", 0)),
        }

        if video_stream:
            metadata["video"] = {
                "codec": video_stream.get("codec_name", ""),
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                "aspect_ratio": video_stream.get("display_aspect_ratio", ""),
                "pixel_format": video_stream.get("pix_fmt", ""),
            }

        if audio_stream:
            metadata["audio"] = {
                "codec": audio_stream.get("codec_name", ""),
                "channels": int(audio_stream.get("channels", 0)),
                "sample_rate": int(audio_stream.get("sample_rate", 0)),
                "bitrate": int(audio_stream.get("bit_rate", 0)),
            }

        return metadata

    except ffmpeg.Error as e:
        raise RuntimeError(f"Error analyzing video: {e}") from e


def create_standard_output(stream, output_path: str, **kwargs) -> Any:
    """Create ffmpeg output with standard encoding settings."""
    default_settings = {
        "vcodec": "libx264",
        "acodec": "aac",
        "pix_fmt": "yuv420p",
    }
    default_settings.update(kwargs)
    return ffmpeg.output(stream, output_path, **default_settings)


COLOR_MAP = {
    "green": "0x00FF00",
    "blue": "0x0000FF",
    "red": "0xFF0000",
    "cyan": "0x00FFFF",
    "magenta": "0xFF00FF",
    "yellow": "0xFFFF00",
    "white": "0xFFFFFF",
    "black": "0x000000",
    "gray": "0x808080",
    "orange": "0xFFA500",
    "purple": "0x800080",
    "pink": "0xFFC0CB",
}


def parse_color(color: str) -> str:
    """Parse color name or hex code to ffmpeg-compatible format."""
    if color.lower() in COLOR_MAP:
        return COLOR_MAP[color.lower()]
    elif color.startswith("#"):
        return "0x" + color[1:]
    elif color.startswith("0x"):
        return color
    else:
        raise ValueError(f"Invalid color format: {color}")


def parse_resolution(
    resolution: str,
) -> tuple[int, int]:
    """Parse resolution string to (width, height) tuple."""
    try:
        width, height = map(int, resolution.split("x"))
        return width, height
    except (ValueError, AttributeError):
        raise ValueError("Resolution must be in format 'WIDTHxHEIGHT'") from None


def parse_size_range(
    size_range: str,
) -> tuple[float, float]:
    """Parse size range string to (min_size, max_size) tuple."""
    try:
        min_size, max_size = map(float, size_range.split(":"))
        if min_size >= max_size:
            raise ValueError("Invalid size range")
        return min_size, max_size
    except (ValueError, AttributeError):
        raise ValueError(
            "Size range must be in format 'min:max' (e.g., '2:8')"
        ) from None
