"""Tests for advanced video operations.

This module tests the advanced video editing functions like audio extraction,
filters, speed changes, thumbnail generation, and format conversion. Uses
pytest fixtures for consistent test data and temporary file management.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, cast

import ffmpeg
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

if TYPE_CHECKING:
    from fastmcp import FastMCP


class VideoStreamInfo(TypedDict):
    """Type definition for video stream information."""

    width: int
    height: int
    codec_name: str
    codec_type: str


class AudioStreamInfo(TypedDict):
    """Type definition for audio stream information."""

    codec_name: str
    codec_type: str


class FormatInfo(TypedDict):
    """Type definition for format information."""

    duration: str
    format_name: str


class ProbeData(TypedDict):
    """Type definition for ffmpeg probe data."""

    streams: list[VideoStreamInfo | AudioStreamInfo]
    format: FormatInfo


class TestAudioOperations:
    """Test suite for audio-related video operations."""

    @pytest.mark.unit
    async def test_extract_audio(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test audio extraction functionality.

        This test verifies that extract_audio correctly extracts audio
        from a video file into a separate audio file.
        """
        output_path: Path = temp_dir / "extracted_audio.mp3"

        async with Client(mcp_server) as client:
            # Extract audio as MP3
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            audio_stream = next(
                (s for s in probe_data["streams"] if s["codec_type"] == "audio"),
                None,
            )
            assert audio_stream is not None
            assert cast(AudioStreamInfo, audio_stream)["codec_name"] == "mp3"

    @pytest.mark.unit
    async def test_add_audio_replace(
        self,
        sample_video: Path,
        sample_audio: Path,
        temp_dir: Path,
        mcp_server: FastMCP[None],
    ) -> None:
        """
        Test audio replacement functionality.

        This test verifies that add_audio correctly replaces the audio
        track in a video with a new audio file.
        """
        output_path: Path = temp_dir / "video_with_new_audio.mp4"

        async with Client(mcp_server) as client:
            # Replace audio
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            video_stream = next(
                (s for s in probe_data["streams"] if s["codec_type"] == "video"),
                None,
            )
            audio_stream = next(
                (s for s in probe_data["streams"] if s["codec_type"] == "audio"),
                None,
            )
            assert video_stream is not None
            assert audio_stream is not None


class TestVideoEffects:
    """Test suite for video effects and filters."""

    @pytest.mark.unit
    async def test_apply_filter_simple(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test applying a simple video filter.

        This test verifies that apply_filter correctly applies a simple
        filter like horizontal flip to a video.
        """
        output_path: Path = temp_dir / "flipped_video.mp4"

        async with Client(mcp_server) as client:
            # Apply horizontal flip filter
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            video_stream = next(
                s for s in probe_data["streams"] if s["codec_type"] == "video"
            )
            assert cast(VideoStreamInfo, video_stream)["width"] == 1280
            assert cast(VideoStreamInfo, video_stream)["height"] == 720

    @pytest.mark.unit
    async def test_apply_filter_with_params(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test applying a filter with parameters.

        This test verifies that apply_filter correctly applies filters
        that require parameters, such as blur with intensity.
        """
        output_path: Path = temp_dir / "blurred_video.mp4"

        async with Client(mcp_server) as client:
            # Apply scale filter with parameter
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            video_stream = next(
                s for s in probe_data["streams"] if s["codec_type"] == "video"
            )
            assert cast(VideoStreamInfo, video_stream)["width"] == 640
            assert cast(VideoStreamInfo, video_stream)["height"] == 360

    @pytest.mark.unit
    async def test_change_speed_faster(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test speeding up video playback.

        This test verifies that change_speed correctly speeds up video
        playback while maintaining synchronization.
        """
        output_path: Path = temp_dir / "fast_video.mp4"

        async with Client(mcp_server) as client:
            # Double the speed
            await client.call_tool(
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
            original_probe_result = ffmpeg.probe(str(sample_video))
            new_probe_result = ffmpeg.probe(str(output_path))

            original_probe = cast(ProbeData, original_probe_result)
            new_probe = cast(ProbeData, new_probe_result)

            original_duration = float(original_probe["format"]["duration"])
            new_duration = float(new_probe["format"]["duration"])

            # Duration should be approximately half (with some tolerance)
            expected_duration = original_duration / 2.0
            assert abs(new_duration - expected_duration) < 0.5

    @pytest.mark.unit
    async def test_change_speed_slower(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test slowing down video playback.

        This test verifies that change_speed correctly slows down video
        playback while maintaining quality.
        """
        output_path: Path = temp_dir / "slow_video.mp4"

        async with Client(mcp_server) as client:
            # Half the speed
            await client.call_tool(
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
            original_probe_result = ffmpeg.probe(str(sample_video))
            new_probe_result = ffmpeg.probe(str(output_path))

            original_probe = cast(ProbeData, original_probe_result)
            new_probe = cast(ProbeData, new_probe_result)

            original_duration = float(original_probe["format"]["duration"])
            new_duration = float(new_probe["format"]["duration"])

            # Duration should be approximately double (with some tolerance)
            expected_duration = original_duration * 2.0
            assert abs(new_duration - expected_duration) < 0.5

    @pytest.mark.unit
    async def test_change_speed_error_handling(
        self, sample_video: Path, mcp_server: FastMCP[None]
    ) -> None:
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
    async def test_generate_thumbnail_default(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test thumbnail generation with default settings.

        This test verifies that generate_thumbnail correctly extracts
        a frame from the middle of the video as a thumbnail.
        """
        output_path: Path = temp_dir / "thumbnail.jpg"

        async with Client(mcp_server) as client:
            # Generate thumbnail with default settings
            await client.call_tool(
                "generate_thumbnail",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                },
            )

            # Verify the output file exists
            assert output_path.exists()

            # Verify it's an image file by probing it
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            video_stream = next(
                (s for s in probe_data["streams"] if s["codec_type"] == "video"),
                None,
            )
            assert video_stream is not None
            # Should maintain original dimensions
            assert cast(VideoStreamInfo, video_stream)["width"] == 1280
            assert cast(VideoStreamInfo, video_stream)["height"] == 720

    @pytest.mark.unit
    async def test_generate_thumbnail_specific_time(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test thumbnail generation at a specific timestamp.

        This test verifies that generate_thumbnail correctly extracts
        a frame from a specified time in the video.
        """
        output_path: Path = temp_dir / "thumbnail_2s.png"

        async with Client(mcp_server) as client:
            # Generate thumbnail at 2 seconds
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            video_stream = next(
                s for s in probe_data["streams"] if s["codec_type"] == "video"
            )
            assert video_stream is not None

    @pytest.mark.unit
    async def test_generate_thumbnail_resized(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test thumbnail generation with custom dimensions.

        This test verifies that generate_thumbnail correctly resizes
        the extracted frame to specified dimensions.
        """
        output_path: Path = temp_dir / "thumbnail_small.jpg"

        async with Client(mcp_server) as client:
            # Generate resized thumbnail
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            video_stream = next(
                s for s in probe_data["streams"] if s["codec_type"] == "video"
            )
            assert cast(VideoStreamInfo, video_stream)["width"] == 320
            assert cast(VideoStreamInfo, video_stream)["height"] == 180


class TestFormatConversion:
    """Test suite for format conversion operations."""

    @pytest.mark.unit
    async def test_convert_format_basic(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test basic format conversion.

        This test verifies that convert_format correctly converts a video
        to a different format while maintaining quality.
        """
        output_path: Path = temp_dir / "converted.avi"

        async with Client(mcp_server) as client:
            # Convert to AVI format
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            format_name = probe_data["format"]["format_name"]
            assert "avi" in format_name.lower()

    @pytest.mark.unit
    async def test_convert_format_with_codecs(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test format conversion with specific codecs.

        This test verifies that convert_format correctly applies
        specific video and audio codecs during conversion.
        """
        output_path: Path = temp_dir / "converted_codecs.mp4"

        async with Client(mcp_server) as client:
            # Convert with specific codecs
            await client.call_tool(
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
            probe_result = ffmpeg.probe(str(output_path))
            probe_data = cast(ProbeData, probe_result)
            video_stream = next(
                (s for s in probe_data["streams"] if s["codec_type"] == "video"),
                None,
            )
            if video_stream:
                assert cast(VideoStreamInfo, video_stream)["codec_name"] == "h264"

    @pytest.mark.unit
    async def test_convert_format_with_bitrates(
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test format conversion with custom bitrates.

        This test verifies that convert_format correctly applies
        custom video and audio bitrates during conversion.
        """
        output_path: Path = temp_dir / "converted_bitrates.mp4"

        async with Client(mcp_server) as client:
            # Convert with custom bitrates
            await client.call_tool(
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
    async def test_extract_audio_nonexistent_file(
        self, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test error handling for non-existent input files.

        This test verifies that audio extraction properly handles
        cases where the input video file doesn't exist.
        """
        output_path: Path = temp_dir / "audio.mp3"

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
        self, sample_video: Path, temp_dir: Path, mcp_server: FastMCP[None]
    ) -> None:
        """
        Test error handling for invalid filter names.

        This test verifies that filter application properly handles
        cases where an invalid filter name is provided.
        """
        output_path: Path = temp_dir / "filtered.mp4"

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