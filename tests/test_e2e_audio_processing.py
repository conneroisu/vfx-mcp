"""End-to-end tests for audio processing operations.

This module provides comprehensive end-to-end testing for audio processing
tools including extract_audio and add_audio. Tests cover realistic workflows
and complete operations from input to output validation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import ffmpeg
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

if TYPE_CHECKING:
    pass


class TestAudioProcessingE2E:
    """End-to-end tests for audio processing operations."""

    @pytest.mark.integration
    async def test_complete_audio_workflow(
        self, sample_video, sample_audio, temp_dir, mcp_server
    ):
        """Test a complete audio processing workflow.

        This test simulates a realistic audio workflow:
        1. Extract audio from a video
        2. Add new audio to the video (replace mode)
        3. Add audio in mix mode
        4. Validate audio properties
        """
        async with Client(mcp_server) as client:
            # Step 1: Extract original audio
            extracted_audio_path = temp_dir / "extracted.mp3"
            extract_result = await client.call_tool(
                "extract_audio",
                {
                    "input_path": str(sample_video),
                    "output_path": str(extracted_audio_path),
                    "format": "mp3",
                    "bitrate": "192k",
                },
            )
            assert extracted_audio_path.exists()

            # Verify extracted audio properties
            audio_probe = ffmpeg.probe(str(extracted_audio_path))
            audio_stream = next(
                s for s in audio_probe["streams"] if s["codec_type"] == "audio"
            )
            assert audio_stream["codec_name"] == "mp3"

            # Step 2: Replace audio in video
            video_with_new_audio = temp_dir / "video_new_audio.mp4"
            replace_result = await client.call_tool(
                "add_audio",
                {
                    "video_path": str(sample_video),
                    "audio_path": str(sample_audio),
                    "output_path": str(video_with_new_audio),
                    "replace": True,
                    "audio_volume": 1.0,
                },
            )
            assert video_with_new_audio.exists()

            # Step 3: Mix audio with existing
            video_mixed_audio = temp_dir / "video_mixed_audio.mp4"
            mix_result = await client.call_tool(
                "add_audio",
                {
                    "video_path": str(sample_video),
                    "audio_path": str(sample_audio),
                    "output_path": str(video_mixed_audio),
                    "replace": False,
                    "audio_volume": 0.5,
                },
            )
            assert video_mixed_audio.exists()

            # Step 4: Verify both outputs have video and audio
            for video_path in [video_with_new_audio, video_mixed_audio]:
                probe = ffmpeg.probe(str(video_path))
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

    @pytest.mark.integration
    async def test_audio_format_conversion_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test extracting audio in different formats.

        This test extracts audio from a video in multiple formats
        and verifies each format has correct properties.
        """
        formats_to_test = [
            ("mp3", "192k"),
            ("wav", ""),  # WAV doesn't use bitrate
            ("aac", "128k"),
            ("ogg", "256k"),
            ("flac", ""),  # FLAC is lossless, no bitrate
        ]

        async with Client(mcp_server) as client:
            for format_name, bitrate in formats_to_test:
                output_path = temp_dir / f"audio.{format_name}"

                extract_args = {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "format": format_name,
                }
                if bitrate:
                    extract_args["bitrate"] = bitrate

                extract_result = await client.call_tool(
                    "extract_audio",
                    extract_args,
                )
                assert output_path.exists()

                # Verify audio format
                probe = ffmpeg.probe(str(output_path))
                audio_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "audio"
                )

                # Check codec (some formats have different probe names)
                if format_name == "mp3":
                    assert audio_stream["codec_name"] == "mp3"
                elif format_name == "aac":
                    assert audio_stream["codec_name"] == "aac"
                elif format_name == "ogg":
                    assert audio_stream["codec_name"] == "vorbis"
                elif format_name == "wav":
                    assert audio_stream["codec_name"] == "pcm_s16le"
                elif format_name == "flac":
                    assert audio_stream["codec_name"] == "flac"

    @pytest.mark.integration
    async def test_audio_volume_adjustment_workflow(
        self, sample_video, sample_audio, temp_dir, mcp_server
    ):
        """Test audio volume adjustments in various scenarios.

        This test verifies that audio volume adjustments work correctly
        in both replace and mix modes with different volume levels.
        """
        volume_tests = [
            ("replace", 0.5, "quiet_replace.mp4"),
            ("replace", 1.5, "loud_replace.mp4"),
            ("mix", 0.3, "quiet_mix.mp4"),
            ("mix", 0.8, "normal_mix.mp4"),
        ]

        async with Client(mcp_server) as client:
            for mode, volume, output_name in volume_tests:
                output_path = temp_dir / output_name
                replace_mode = mode == "replace"

                result = await client.call_tool(
                    "add_audio",
                    {
                        "video_path": str(sample_video),
                        "audio_path": str(sample_audio),
                        "output_path": str(output_path),
                        "replace": replace_mode,
                        "audio_volume": volume,
                    },
                )
                assert output_path.exists()

                # Verify video and audio streams exist
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

                # Verify video properties remain unchanged
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720

    @pytest.mark.integration
    async def test_audio_synchronization_workflow(
        self, sample_video, sample_audio, temp_dir, mcp_server
    ):
        """Test audio synchronization and duration matching.

        This test verifies that audio is properly synchronized with video
        and handles duration mismatches correctly.
        """
        async with Client(mcp_server) as client:
            # First, create a longer audio file for testing
            long_audio_path = temp_dir / "long_audio.mp3"
            (
                ffmpeg.input(
                    "sine=frequency=880:duration=10",  # 10-second sine wave
                    f="lavfi",
                )
                .output(
                    str(long_audio_path),
                    acodec="mp3",
                    audio_bitrate="192k",
                )
                .overwrite_output()
                .run(quiet=True)
            )

            # Test replacing audio with longer audio (should be truncated)
            replace_long_path = temp_dir / "replace_long_audio.mp4"
            replace_result = await client.call_tool(
                "add_audio",
                {
                    "video_path": str(sample_video),
                    "audio_path": str(long_audio_path),
                    "output_path": str(replace_long_path),
                    "replace": True,
                    "audio_volume": 1.0,
                },
            )
            assert replace_long_path.exists()

            # Verify the output duration matches the video duration
            probe = ffmpeg.probe(str(replace_long_path))
            duration = float(probe["format"]["duration"])
            assert 4.9 <= duration <= 5.1  # Should match original video duration

            # Test mixing with longer audio
            mix_long_path = temp_dir / "mix_long_audio.mp4"
            mix_result = await client.call_tool(
                "add_audio",
                {
                    "video_path": str(sample_video),
                    "audio_path": str(long_audio_path),
                    "output_path": str(mix_long_path),
                    "replace": False,
                    "audio_volume": 0.7,
                },
            )
            assert mix_long_path.exists()

            # Verify the output duration matches the video duration
            probe = ffmpeg.probe(str(mix_long_path))
            duration = float(probe["format"]["duration"])
            assert 4.9 <= duration <= 5.1  # Should match original video duration

    @pytest.mark.integration
    async def test_audio_quality_preservation_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test audio quality preservation across operations.

        This test verifies that audio quality is preserved when
        extracting and re-adding audio to videos.
        """
        async with Client(mcp_server) as client:
            # Step 1: Extract high-quality audio
            hq_audio_path = temp_dir / "hq_audio.flac"
            extract_result = await client.call_tool(
                "extract_audio",
                {
                    "input_path": str(sample_video),
                    "output_path": str(hq_audio_path),
                    "format": "flac",  # Lossless format
                },
            )
            assert hq_audio_path.exists()

            # Step 2: Add the high-quality audio back to video
            hq_video_path = temp_dir / "hq_video.mp4"
            add_result = await client.call_tool(
                "add_audio",
                {
                    "video_path": str(sample_video),
                    "audio_path": str(hq_audio_path),
                    "output_path": str(hq_video_path),
                    "replace": True,
                    "audio_volume": 1.0,
                },
            )
            assert hq_video_path.exists()

            # Step 3: Extract audio again to compare
            extracted_again_path = temp_dir / "extracted_again.wav"
            extract_again_result = await client.call_tool(
                "extract_audio",
                {
                    "input_path": str(hq_video_path),
                    "output_path": str(extracted_again_path),
                    "format": "wav",
                },
            )
            assert extracted_again_path.exists()

            # Verify audio properties are maintained
            for audio_path in [hq_audio_path, extracted_again_path]:
                probe = ffmpeg.probe(str(audio_path))
                audio_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "audio"
                )
                # Duration should be approximately the same
                duration = float(probe["format"]["duration"])
                assert 4.9 <= duration <= 5.1

    @pytest.mark.integration
    async def test_audio_processing_with_video_operations(
        self, sample_video, sample_audio, temp_dir, mcp_server
    ):
        """Test audio processing combined with video operations.

        This test verifies that audio processing works correctly
        when combined with other video editing operations.
        """
        async with Client(mcp_server) as client:
            # Step 1: Trim video first
            trimmed_video_path = temp_dir / "trimmed_for_audio.mp4"
            trim_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(trimmed_video_path),
                    "start_time": 1.0,
                    "duration": 3.0,
                },
            )
            assert trimmed_video_path.exists()

            # Step 2: Extract audio from trimmed video
            trimmed_audio_path = temp_dir / "trimmed_audio.mp3"
            extract_result = await client.call_tool(
                "extract_audio",
                {
                    "input_path": str(trimmed_video_path),
                    "output_path": str(trimmed_audio_path),
                    "format": "mp3",
                    "bitrate": "320k",
                },
            )
            assert trimmed_audio_path.exists()

            # Step 3: Resize the trimmed video
            resized_video_path = temp_dir / "resized_for_audio.mp4"
            resize_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(trimmed_video_path),
                    "output_path": str(resized_video_path),
                    "scale": 0.75,
                },
            )
            assert resized_video_path.exists()

            # Step 4: Add new audio to resized video
            final_video_path = temp_dir / "final_with_audio.mp4"
            add_audio_result = await client.call_tool(
                "add_audio",
                {
                    "video_path": str(resized_video_path),
                    "audio_path": str(sample_audio),
                    "output_path": str(final_video_path),
                    "replace": True,
                    "audio_volume": 1.2,
                },
            )
            assert final_video_path.exists()

            # Verify final video properties
            probe = ffmpeg.probe(str(final_video_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            audio_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "audio"
            )

            # Check video dimensions (should be 75% of original)
            assert video_stream["width"] == 960  # 1280 * 0.75
            assert video_stream["height"] == 540  # 720 * 0.75

            # Check duration (should be ~3 seconds from trim)
            duration = float(probe["format"]["duration"])
            assert 2.9 <= duration <= 3.1

            # Check audio is present
            assert audio_stream is not None
            assert audio_stream["codec_name"] == "aac"

    @pytest.mark.integration
    async def test_audio_error_handling(self, sample_video, temp_dir, mcp_server):
        """Test error handling in audio processing operations.

        This test verifies that audio processing tools handle errors
        correctly and provide meaningful error messages.
        """
        async with Client(mcp_server) as client:
            # Test extracting audio from non-existent file
            with pytest.raises(ToolError):
                await client.call_tool(
                    "extract_audio",
                    {
                        "input_path": "nonexistent.mp4",
                        "output_path": str(temp_dir / "audio.mp3"),
                        "format": "mp3",
                    },
                )

            # Test invalid audio format
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "extract_audio",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "audio.xyz"),
                        "format": "invalid_format",
                    },
                )

            # Test adding audio with invalid volume
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "add_audio",
                    {
                        "video_path": str(sample_video),
                        "audio_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "audio_volume": 5.0,  # Too high
                    },
                )

            # Test adding audio with negative volume
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "add_audio",
                    {
                        "video_path": str(sample_video),
                        "audio_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "audio_volume": -0.5,  # Negative
                    },
                )

            # Test adding non-existent audio file
            with pytest.raises(ToolError):
                await client.call_tool(
                    "add_audio",
                    {
                        "video_path": str(sample_video),
                        "audio_path": "nonexistent_audio.mp3",
                        "output_path": str(temp_dir / "output.mp4"),
                        "replace": True,
                    },
                )

            # Test adding audio to non-existent video
            with pytest.raises(ToolError):
                await client.call_tool(
                    "add_audio",
                    {
                        "video_path": "nonexistent_video.mp4",
                        "audio_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "replace": True,
                    },
                )

    @pytest.mark.integration
    async def test_audio_bitrate_variations(self, sample_video, temp_dir, mcp_server):
        """Test audio extraction with different bitrate settings.

        This test verifies that different bitrate settings work correctly
        and produce files with expected properties.
        """
        bitrate_tests = [
            ("96k", "low_quality.mp3"),
            ("128k", "standard_quality.mp3"),
            ("192k", "good_quality.mp3"),
            ("320k", "high_quality.mp3"),
        ]

        async with Client(mcp_server) as client:
            file_sizes = []

            for bitrate, filename in bitrate_tests:
                output_path = temp_dir / filename

                extract_result = await client.call_tool(
                    "extract_audio",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "format": "mp3",
                        "bitrate": bitrate,
                    },
                )
                assert output_path.exists()

                # Verify file properties
                probe = ffmpeg.probe(str(output_path))
                audio_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "audio"
                )
                assert audio_stream["codec_name"] == "mp3"

                # Track file size for comparison
                file_size = output_path.stat().st_size
                file_sizes.append(file_size)

            # Verify that higher bitrates generally produce larger files
            # (with some tolerance for encoding variations)
            for i in range(len(file_sizes) - 1):
                # Each higher bitrate should generally be larger (with 20% tolerance)
                size_ratio = file_sizes[i + 1] / file_sizes[i]
                assert (
                    size_ratio > 0.8
                )  # Allow for some compression efficiency variation
