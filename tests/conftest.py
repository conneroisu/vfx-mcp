"""
Pytest configuration and fixtures for VFX MCP tests.

This module provides shared fixtures and configuration for all tests.
"""

import shutil
import tempfile
from pathlib import Path

import ffmpeg
import pytest


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test files.

    This fixture creates a temporary directory that is automatically
    cleaned up after the test completes.

    Yields:
        Path: Path to the temporary directory
    """
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup after test
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_video(temp_dir):
    """
    Create a sample test video using ffmpeg.

    This fixture generates a simple test video with color bars
    and a test tone for use in tests.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to the generated test video
    """
    output_path = temp_dir / "test_video.mp4"

    # Generate a 5-second test video with color bars and sine wave audio
    # Using lavfi (libavfilter) virtual input device
    (
        ffmpeg.input(
            "testsrc=duration=5:size=1280x720:rate=30",
            f="lavfi",
        )
        .output(
            str(output_path),
            vcodec="libx264",
            acodec="aac",
            audio_bitrate="128k",
            # Add a sine wave test tone
            **{"f": "mp4"},
        )
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


@pytest.fixture
def sample_videos(temp_dir):
    """
    Create multiple sample test videos.

    This fixture generates three test videos with different patterns
    for testing concatenation and batch operations.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        list[Path]: List of paths to generated test videos
    """
    videos = []
    patterns = [
        "testsrc",
        "testsrc2",
        "rgbtestsrc",
    ]

    for i, pattern in enumerate(patterns):
        output_path = (
            temp_dir / f"test_video_{i}.mp4"
        )

        # Generate 2-second test videos with different patterns
        (
            ffmpeg.input(
                f"{pattern}=duration=2:size=640x480:rate=24",
                f="lavfi",
            )
            .output(
                str(output_path),
                vcodec="libx264",
                preset="ultrafast",
                **{"f": "mp4"},
            )
            .overwrite_output()
            .run(quiet=True)
        )

        videos.append(output_path)

    return videos


@pytest.fixture
def sample_audio(temp_dir):
    """
    Create a sample audio file.

    This fixture generates a test audio file with a sine wave tone.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to the generated audio file
    """
    output_path = temp_dir / "test_audio.mp3"

    # Generate a 3-second 440Hz sine wave (A4 note)
    (
        ffmpeg.input(
            "sine=frequency=440:duration=3",
            f="lavfi",
        )
        .output(
            str(output_path),
            acodec="mp3",
            audio_bitrate="192k",
        )
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


@pytest.fixture
def mcp_server():
    """
    Create an MCP server instance for testing.

    This fixture provides a configured FastMCP server instance
    that can be used for testing MCP functionality.

    Returns:
        FastMCP: Configured MCP server instance
    """
    # Import here to avoid circular imports
    from main import mcp

    return mcp


# Pytest configuration options
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests",
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests",
    )
