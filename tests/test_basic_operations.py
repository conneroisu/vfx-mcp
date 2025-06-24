"""Tests for basic video operations.

This module tests the core video editing functions like trim, concatenate,
resize, and get_video_info. Uses pytest fixtures for consistent test data
and temporary file management.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import ffmpeg
import pytest
from fastmcp import Client

if TYPE_CHECKING:
    pass


class TestBasicOperations:
    """Test suite for basic video operations."""

    @pytest.mark.unit
    async def test_get_video_info(self, sample_video, mcp_server):
        """
        Test getting video metadata.

        This test verifies that get_video_info returns correct metadata
        for a test video including duration, resolution, codecs, etc.
        """
        # Use the MCP client to test the server
        async with Client(mcp_server) as client:
            # Call the get_video_info tool
            result = await client.call_tool(
                "get_video_info",
                {"video_path": str(sample_video)},
            )

            # Parse the result
            info = json.loads(result[0].text)

            # Verify the metadata structure
            assert "filename" in info
            assert "format" in info
            assert "duration" in info
            assert "video" in info
            # Audio may or may not be present depending on test video generation

            # Verify video properties
            assert info["video"]["width"] == 1280
            assert info["video"]["height"] == 720
            assert info["video"]["codec"] == "h264"

            # Verify duration is approximately 5 seconds
            assert 4.9 <= info["duration"] <= 5.1

    @pytest.mark.unit
    async def test_trim_video(self, sample_video, temp_dir, mcp_server):
        """
        Test video trimming functionality.

        This test verifies that trim_video correctly extracts a segment
        from a video with the specified start time and duration.
        """
        output_path = temp_dir / "trimmed.mp4"

        async with Client(mcp_server) as client:
            # Trim from 1s to 3s (2 second duration)
            result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "start_time": 1.0,
                    "duration": 2.0,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the trimmed video duration
            probe = ffmpeg.probe(str(output_path))
            duration = float(probe["format"]["duration"])
            assert 1.9 <= duration <= 2.2  # Allow small variance for ffmpeg processing

    @pytest.mark.unit
    async def test_trim_video_to_end(self, sample_video, temp_dir, mcp_server):
        """
        Test trimming video from start time to end.

        This test verifies that trim_video works correctly when no
        duration is specified (should trim from start_time to end).
        """
        output_path = temp_dir / "trimmed_to_end.mp4"

        async with Client(mcp_server) as client:
            # Trim from 3s to end
            result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "start_time": 3.0,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the trimmed video duration (should be ~2 seconds)
            probe = ffmpeg.probe(str(output_path))
            duration = float(probe["format"]["duration"])
            assert 1.9 <= duration <= 2.1

    @pytest.mark.unit
    async def test_resize_video_by_width(self, sample_video, temp_dir, mcp_server):
        """
        Test resizing video by width (maintaining aspect ratio).

        This test verifies that resize_video correctly scales a video
        to a target width while maintaining the aspect ratio.
        """
        output_path = temp_dir / "resized_width.mp4"

        async with Client(mcp_server) as client:
            # Resize to 640px width (should result in 640x360)
            result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "width": 640,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the video dimensions
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 640
            assert video_stream["height"] == 360  # Maintains 16:9 aspect ratio

    @pytest.mark.unit
    async def test_resize_video_by_scale(self, sample_video, temp_dir, mcp_server):
        """
        Test resizing video by scale factor.

        This test verifies that resize_video correctly scales a video
        by a given factor (e.g., 0.5 for half size).
        """
        output_path = temp_dir / "resized_scale.mp4"

        async with Client(mcp_server) as client:
            # Scale to 50% (should result in 640x360)
            result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "scale": 0.5,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the video dimensions
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 640
            assert video_stream["height"] == 360

    @pytest.mark.unit
    async def test_concatenate_videos(self, sample_videos, temp_dir, mcp_server):
        """
        Test concatenating multiple videos.

        This test verifies that concatenate_videos correctly joins
        multiple video files into a single output file.
        """
        output_path = temp_dir / "concatenated.mp4"

        async with Client(mcp_server) as client:
            # Concatenate the three 2-second videos
            result = await client.call_tool(
                "concatenate_videos",
                {
                    "input_paths": [str(v) for v in sample_videos],
                    "output_path": str(output_path),
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the concatenated video duration (should be ~6 seconds)
            probe = ffmpeg.probe(str(output_path))
            duration = float(probe["format"]["duration"])
            assert 5.9 <= duration <= 6.1

    @pytest.mark.unit
    async def test_concatenate_videos_error_handling(self, sample_video, mcp_server):
        """
        Test error handling for concatenate_videos.

        This test verifies that concatenate_videos properly handles
        invalid inputs like too few videos.
        """
        async with Client(mcp_server) as client:
            # Try to concatenate only one video (should fail)
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "concatenate_videos",
                    {
                        "input_paths": [str(sample_video)],
                        "output_path": "output.mp4",
                    },
                )

            # Verify the error message
            assert "at least 2 videos" in str(exc_info.value).lower()


class TestResourceEndpoints:
    """Test suite for MCP resource endpoints."""

    @pytest.mark.unit
    async def test_list_videos_resource(self, sample_videos, mcp_server):
        """
        Test the videos://list resource endpoint.

        This test verifies that the list endpoint correctly returns
        all video files in the current directory.
        """
        # Change to the temp directory containing the test videos
        import os

        original_cwd = os.getcwd()
        temp_dir = sample_videos[0].parent
        os.chdir(temp_dir)

        try:
            async with Client(mcp_server) as client:
                # Read the videos list resource
                result = await client.read_resource("videos://list")

                # Parse the JSON response
                data = json.loads(result[0].text)

                # Verify the structure
                assert "videos" in data
                assert isinstance(data["videos"], list)

                # Verify our test videos are listed
                video_names = [Path(v).name for v in data["videos"]]
                for test_video in sample_videos:
                    assert test_video.name in video_names
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    @pytest.mark.unit
    async def test_video_metadata_resource(self, sample_video, mcp_server):
        """
        Test the videos://{filename}/metadata resource endpoint.

        This test verifies that the metadata endpoint returns correct
        information for a specific video file.
        """
        # Change to the temp directory containing the test video
        import os

        original_cwd = os.getcwd()
        temp_dir = sample_video.parent
        os.chdir(temp_dir)

        try:
            async with Client(mcp_server) as client:
                # Read metadata for the test video
                result = await client.read_resource(
                    f"videos://{sample_video.name}/metadata"
                )

                # Parse the JSON response
                metadata = json.loads(result[0].text)

                # Verify it matches get_video_info output
                assert "filename" in metadata
                assert metadata["filename"] == sample_video.name
                assert "duration" in metadata
                assert "video" in metadata
                assert metadata["video"]["width"] == 1280
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
