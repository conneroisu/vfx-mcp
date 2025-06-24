"""Tests for advanced video operations.

This module tests the advanced video editing functions like audio extraction,
filters, speed changes, thumbnail generation, and format conversion. Uses
pytest fixtures for consistent test data and temporary file management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import ffmpeg
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

if TYPE_CHECKING:
    pass


class TestAudioOperations:
    """Test suite for audio-related video operations."""

    @pytest.mark.unit
    async def test_extract_audio(self, sample_video, temp_dir, mcp_server):
        """
        Test audio extraction functionality.

        This test verifies that extract_audio correctly extracts audio
        from a video file into a separate audio file.
        """
        output_path = temp_dir / "extracted_audio.mp3"

        async with Client(mcp_server) as client:
            # Extract audio as MP3
            result = await client.call_tool(
                "extract_audio",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "format": "mp3",
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify it's an audio file by probing it
            probe = ffmpeg.probe(str(output_path))
            audio_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "audio"),
                None,
            )
            assert audio_stream is not None
            assert audio_stream["codec_name"] == "mp3"

    @pytest.mark.unit
    async def test_add_audio_replace(
        self,
        sample_video,
        sample_audio,
        temp_dir,
        mcp_server,
    ):
        """
        Test audio replacement functionality.

        This test verifies that add_audio correctly replaces the audio
        track in a video with a new audio file.
        """
        output_path = temp_dir / "video_with_new_audio.mp4"

        async with Client(mcp_server) as client:
            # Replace audio
            result = await client.call_tool(
                "add_audio",
                {
                    "input_path": str(sample_video),
                    "audio_path": str(sample_audio),
                    "output_path": str(output_path),
                    "replace": True,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify it has both video and audio streams
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "video"),
                None,
            )
            audio_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "audio"),
                None,
            )
            assert video_stream is not None
            assert audio_stream is not None


class TestVideoEffects:
    """Test suite for video effects and filters."""

    @pytest.mark.unit
    async def test_apply_filter_simple(self, sample_video, temp_dir, mcp_server):
        """
        Test applying a simple video filter.

        This test verifies that apply_filter correctly applies a simple
        filter like horizontal flip to a video.
        """
        output_path = temp_dir / "flipped_video.mp4"

        async with Client(mcp_server) as client:
            # Apply horizontal flip filter
            result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "filter": "hflip",
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify it has the same dimensions as original
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 1280
            assert video_stream["height"] == 720

    @pytest.mark.unit
    async def test_apply_filter_with_params(self, sample_video, temp_dir, mcp_server):
        """
        Test applying a filter with parameters.

        This test verifies that apply_filter correctly applies filters
        that require parameters, such as blur with intensity.
        """
        output_path = temp_dir / "blurred_video.mp4"

        async with Client(mcp_server) as client:
            # Apply scale filter with parameter
            result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "filter": "scale=640:360",
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the video was scaled correctly
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 640
            assert video_stream["height"] == 360

    @pytest.mark.unit
    async def test_change_speed_faster(self, sample_video, temp_dir, mcp_server):
        """
        Test speeding up video playback.

        This test verifies that change_speed correctly speeds up video
        playback while maintaining synchronization.
        """
        output_path = temp_dir / "fast_video.mp4"

        async with Client(mcp_server) as client:
            # Double the speed
            result = await client.call_tool(
                "change_speed",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "speed": 2.0,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the video duration is approximately halved
            original_probe = ffmpeg.probe(str(sample_video))
            new_probe = ffmpeg.probe(str(output_path))

            original_duration = float(original_probe["format"]["duration"])
            new_duration = float(new_probe["format"]["duration"])

            # Duration should be approximately half (with some tolerance)
            expected_duration = original_duration / 2.0
            assert abs(new_duration - expected_duration) < 0.5

    @pytest.mark.unit
    async def test_change_speed_slower(self, sample_video, temp_dir, mcp_server):
        """
        Test slowing down video playback.

        This test verifies that change_speed correctly slows down video
        playback while maintaining quality.
        """
        output_path = temp_dir / "slow_video.mp4"

        async with Client(mcp_server) as client:
            # Half the speed
            result = await client.call_tool(
                "change_speed",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "speed": 0.5,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the video duration is approximately doubled
            original_probe = ffmpeg.probe(str(sample_video))
            new_probe = ffmpeg.probe(str(output_path))

            original_duration = float(original_probe["format"]["duration"])
            new_duration = float(new_probe["format"]["duration"])

            # Duration should be approximately double (with some tolerance)
            expected_duration = original_duration * 2.0
            assert abs(new_duration - expected_duration) < 0.5

    @pytest.mark.unit
    async def test_change_speed_error_handling(self, sample_video, mcp_server):
        """
        Test error handling for invalid speed values.

        This test verifies that change_speed properly handles invalid
        speed values like zero or negative numbers.
        """
        async with Client(mcp_server) as client:
            # Try invalid speed (zero)
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "change_speed",
                    {
                        "input_path": str(sample_video),
                        "output_path": "output.mp4",
                        "speed": 0.0,
                    },
                )

            # Verify the error message
            assert "must be greater than 0" in str(exc_info.value).lower()


class TestThumbnailGeneration:
    """Test suite for thumbnail generation."""

    @pytest.mark.unit
    async def test_generate_thumbnail_default(self, sample_video, temp_dir, mcp_server):
        """
        Test thumbnail generation with default settings.

        This test verifies that generate_thumbnail correctly extracts
        a frame from the middle of the video as a thumbnail.
        """
        output_path = temp_dir / "thumbnail.jpg"

        async with Client(mcp_server) as client:
            # Generate thumbnail with default settings
            result = await client.call_tool(
                "generate_thumbnail",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify it's an image file by probing it
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "video"),
                None,
            )
            assert video_stream is not None
            # Should maintain original dimensions
            assert video_stream["width"] == 1280
            assert video_stream["height"] == 720

    @pytest.mark.unit
    async def test_generate_thumbnail_specific_time(
        self, sample_video, temp_dir, mcp_server
    ):
        """
        Test thumbnail generation at a specific timestamp.

        This test verifies that generate_thumbnail correctly extracts
        a frame from a specified time in the video.
        """
        output_path = temp_dir / "thumbnail_2s.png"

        async with Client(mcp_server) as client:
            # Generate thumbnail at 2 seconds
            result = await client.call_tool(
                "generate_thumbnail",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "timestamp": 2.0,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify it's an image file
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream is not None

    @pytest.mark.unit
    async def test_generate_thumbnail_resized(self, sample_video, temp_dir, mcp_server):
        """
        Test thumbnail generation with custom dimensions.

        This test verifies that generate_thumbnail correctly resizes
        the extracted frame to specified dimensions.
        """
        output_path = temp_dir / "thumbnail_small.jpg"

        async with Client(mcp_server) as client:
            # Generate resized thumbnail
            result = await client.call_tool(
                "generate_thumbnail",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "width": 320,
                    "height": 180,
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the image dimensions
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 320
            assert video_stream["height"] == 180


class TestFormatConversion:
    """Test suite for format conversion operations."""

    @pytest.mark.unit
    async def test_convert_format_basic(self, sample_video, temp_dir, mcp_server):
        """
        Test basic format conversion.

        This test verifies that convert_format correctly converts a video
        to a different format while maintaining quality.
        """
        output_path = temp_dir / "converted.avi"

        async with Client(mcp_server) as client:
            # Convert to AVI format
            result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "format": "avi",
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the format was changed
            probe = ffmpeg.probe(str(output_path))
            format_name = probe["format"]["format_name"]
            assert "avi" in format_name.lower()

    @pytest.mark.unit
    async def test_convert_format_with_codecs(self, sample_video, temp_dir, mcp_server):
        """
        Test format conversion with specific codecs.

        This test verifies that convert_format correctly applies
        specific video and audio codecs during conversion.
        """
        output_path = temp_dir / "converted_codecs.mp4"

        async with Client(mcp_server) as client:
            # Convert with specific codecs
            result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "video_codec": "libx264",
                    "audio_codec": "aac",
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the codecs were applied
            probe = ffmpeg.probe(str(output_path))
            video_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "video"),
                None,
            )
            if video_stream:
                assert video_stream["codec_name"] == "h264"

    @pytest.mark.unit
    async def test_convert_format_with_bitrates(
        self, sample_video, temp_dir, mcp_server
    ):
        """
        Test format conversion with custom bitrates.

        This test verifies that convert_format correctly applies
        custom video and audio bitrates during conversion.
        """
        output_path = temp_dir / "converted_bitrates.mp4"

        async with Client(mcp_server) as client:
            # Convert with custom bitrates
            result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "video_bitrate": "500k",
                    "audio_bitrate": "128k",
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify the file was processed (size should be different)
            original_size = sample_video.stat().st_size
            new_size = output_path.stat().st_size
            # With lower bitrate, file should generally be smaller
            assert new_size != original_size


class TestErrorHandling:
    """Test suite for error handling in advanced operations."""

    @pytest.mark.unit
    async def test_extract_audio_nonexistent_file(self, temp_dir, mcp_server):
        """
        Test error handling for non-existent input files.

        This test verifies that audio extraction properly handles
        cases where the input video file doesn't exist.
        """
        output_path = temp_dir / "audio.mp3"

        async with Client(mcp_server) as client:
            # Try to extract audio from non-existent file
            with pytest.raises(ToolError):
                await client.call_tool(
                    "extract_audio",
                    {
                        "input_path": "nonexistent.mp4",
                        "output_path": str(output_path),
                    },
                )

    @pytest.mark.unit
    async def test_apply_filter_invalid_filter(
        self, sample_video, temp_dir, mcp_server
    ):
        """
        Test error handling for invalid filter names.

        This test verifies that filter application properly handles
        cases where an invalid filter name is provided.
        """
        output_path = temp_dir / "filtered.mp4"

        async with Client(mcp_server) as client:
            # Try to apply an invalid filter
            with pytest.raises(ToolError):
                await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "filter": "nonexistent_filter",
                    },
                )
