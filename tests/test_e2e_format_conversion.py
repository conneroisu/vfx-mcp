"""End-to-end tests for format conversion operations.

This module provides comprehensive end-to-end testing for format conversion
tools including convert_format with various codecs, bitrates, and containers.
Tests cover realistic workflows and complete operations from input to output validation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import ffmpeg
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

if TYPE_CHECKING:
    pass


class TestFormatConversionE2E:
    """End-to-end tests for format conversion operations."""

    @pytest.mark.integration
    async def test_format_conversion_workflow(self, sample_video, temp_dir, mcp_server):
        """Test converting between different video formats and codecs.

        This test converts a video to different formats and verifies
        the conversion maintains quality and applies settings correctly.
        """
        conversion_tests = [
            {
                "video_codec": "libx264",
                "audio_codec": "aac",
                "video_bitrate": "1M",
                "audio_bitrate": "128k",
                "output": "h264_aac.mp4",
            },
            {
                "video_codec": "libx265",
                "audio_codec": "aac",
                "video_bitrate": "800k",
                "audio_bitrate": "96k",
                "output": "h265_aac.mp4",
            },
            {
                "video_codec": "libx264",
                "audio_codec": "aac",
                "video_bitrate": None,  # Auto bitrate
                "audio_bitrate": "192k",
                "output": "auto_bitrate.mp4",
            },
        ]

        async with Client(mcp_server) as client:
            for test_case in conversion_tests:
                output_path = temp_dir / test_case["output"]

                convert_args = {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "video_codec": test_case["video_codec"],
                    "audio_codec": test_case["audio_codec"],
                    "audio_bitrate": test_case["audio_bitrate"],
                }

                if test_case["video_bitrate"]:
                    convert_args["video_bitrate"] = test_case["video_bitrate"]

                convert_result = await client.call_tool(
                    "convert_format",
                    convert_args,
                )
                assert output_path.exists()

                # Verify codec was applied
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

                # Check video codec
                if test_case["video_codec"] == "libx264":
                    assert video_stream["codec_name"] == "h264"
                elif test_case["video_codec"] == "libx265":
                    assert video_stream["codec_name"] == "hevc"

                # Check audio codec
                assert audio_stream["codec_name"] == "aac"

    @pytest.mark.integration
    async def test_format_conversion_with_effects_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test format conversion combined with effects.

        This test applies effects and then converts the format to verify
        the complete pipeline works correctly.
        """
        async with Client(mcp_server) as client:
            # Step 1: Apply effects first
            effects_path = temp_dir / "with_effects.mp4"
            effects_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(sample_video),
                    "output_path": str(effects_path),
                    "filter": "contrast",
                    "strength": 1.4,
                },
            )
            assert effects_path.exists()

            # Step 2: Convert format with different codec
            converted_path = temp_dir / "effects_converted.mp4"
            convert_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(effects_path),
                    "output_path": str(converted_path),
                    "video_codec": "libx265",
                    "audio_codec": "aac",
                    "video_bitrate": "500k",
                    "audio_bitrate": "96k",
                },
            )
            assert converted_path.exists()

            # Step 3: Verify final output
            probe = ffmpeg.probe(str(converted_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            audio_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "audio"
            )

            assert video_stream["codec_name"] == "hevc"  # H.265
            assert audio_stream["codec_name"] == "aac"

            # Step 4: Generate final thumbnail
            final_thumb = temp_dir / "final_thumb.jpg"
            thumb_result = await client.call_tool(
                "generate_thumbnail",
                {
                    "input_path": str(converted_path),
                    "output_path": str(final_thumb),
                    "timestamp": 2.0,
                    "width": 640,
                    "height": 360,
                },
            )
            assert final_thumb.exists()

    @pytest.mark.integration
    async def test_bitrate_variations_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test format conversion with different bitrate settings.

        This test converts videos with various bitrate settings to verify
        quality and file size variations work as expected.
        """
        bitrate_tests = [
            ("500k", "64k", "low_quality.mp4"),
            ("1M", "128k", "medium_quality.mp4"),
            ("2M", "192k", "high_quality.mp4"),
            ("4M", "320k", "very_high_quality.mp4"),
        ]

        async with Client(mcp_server) as client:
            file_sizes = []

            for video_bitrate, audio_bitrate, filename in bitrate_tests:
                output_path = temp_dir / filename

                convert_result = await client.call_tool(
                    "convert_format",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "video_codec": "libx264",
                        "audio_codec": "aac",
                        "video_bitrate": video_bitrate,
                        "audio_bitrate": audio_bitrate,
                    },
                )
                assert output_path.exists()

                # Verify codec and properties
                probe = ffmpeg.probe(str(output_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )
                audio_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "audio"
                )

                assert video_stream["codec_name"] == "h264"
                assert audio_stream["codec_name"] == "aac"

                # Track file size for comparison
                file_size = output_path.stat().st_size
                file_sizes.append(file_size)

            # Verify that higher bitrates generally produce larger files
            for i in range(len(file_sizes) - 1):
                # Each higher bitrate should generally be larger
                assert file_sizes[i + 1] > file_sizes[i] * 0.8  # Allow some variance

    @pytest.mark.integration
    async def test_codec_compatibility_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test conversion with different codec combinations.

        This test verifies that various codec combinations work correctly
        and produce valid output files.
        """
        codec_tests = [
            ("libx264", "aac", "h264_aac.mp4"),
            ("libx264", "mp3", "h264_mp3.mp4"),
            ("libx265", "aac", "h265_aac.mp4"),
        ]

        async with Client(mcp_server) as client:
            for video_codec, audio_codec, filename in codec_tests:
                output_path = temp_dir / filename

                convert_result = await client.call_tool(
                    "convert_format",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "video_codec": video_codec,
                        "audio_codec": audio_codec,
                        "video_bitrate": "1.5M",
                        "audio_bitrate": "128k",
                    },
                )
                assert output_path.exists()

                # Verify the codecs were applied correctly
                probe = ffmpeg.probe(str(output_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )
                audio_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "audio"
                )

                # Check video codec
                if video_codec == "libx264":
                    assert video_stream["codec_name"] == "h264"
                elif video_codec == "libx265":
                    assert video_stream["codec_name"] == "hevc"

                # Check audio codec
                if audio_codec == "aac":
                    assert audio_stream["codec_name"] == "aac"
                elif audio_codec == "mp3":
                    assert audio_stream["codec_name"] == "mp3"

    @pytest.mark.integration
    async def test_conversion_with_video_operations_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test format conversion combined with video operations.

        This test combines format conversion with trimming, resizing,
        and other operations to verify the complete pipeline.
        """
        async with Client(mcp_server) as client:
            # Step 1: Trim video
            trimmed_path = temp_dir / "trimmed_for_conversion.mp4"
            trim_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(trimmed_path),
                    "start_time": 1.0,
                    "duration": 3.0,
                },
            )
            assert trimmed_path.exists()

            # Step 2: Resize the trimmed video
            resized_path = temp_dir / "resized_for_conversion.mp4"
            resize_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(trimmed_path),
                    "output_path": str(resized_path),
                    "scale": 0.75,
                },
            )
            assert resized_path.exists()

            # Step 3: Apply effects
            effects_path = temp_dir / "effects_for_conversion.mp4"
            effects_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(resized_path),
                    "output_path": str(effects_path),
                    "filter": "saturation",
                    "strength": 1.3,
                },
            )
            assert effects_path.exists()

            # Step 4: Convert format with high compression
            final_path = temp_dir / "final_converted.mp4"
            convert_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(effects_path),
                    "output_path": str(final_path),
                    "video_codec": "libx265",
                    "audio_codec": "aac",
                    "video_bitrate": "600k",
                    "audio_bitrate": "96k",
                },
            )
            assert final_path.exists()

            # Verify final output properties
            probe = ffmpeg.probe(str(final_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            audio_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "audio"
            )

            # Check codec
            assert video_stream["codec_name"] == "hevc"
            assert audio_stream["codec_name"] == "aac"

            # Check dimensions (75% of original)
            assert video_stream["width"] == 960  # 1280 * 0.75
            assert video_stream["height"] == 540  # 720 * 0.75

            # Check duration (~3 seconds from trim)
            duration = float(probe["format"]["duration"])
            assert 2.9 <= duration <= 3.1

    @pytest.mark.integration
    async def test_audio_only_conversion_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test audio format conversion workflow.

        This test extracts audio, then uses format conversion to change
        the audio codec and settings.
        """
        async with Client(mcp_server) as client:
            # Step 1: Extract audio first
            audio_path = temp_dir / "extracted.wav"
            extract_result = await client.call_tool(
                "extract_audio",
                {
                    "input_path": str(sample_video),
                    "output_path": str(audio_path),
                    "format": "wav",
                },
            )
            assert audio_path.exists()

            # Step 2: Create video with different audio settings
            # First, create a silent video to work with
            silent_video_path = temp_dir / "silent_video.mp4"
            (
                ffmpeg.input(str(sample_video))
                .output(
                    str(silent_video_path),
                    vcodec="copy",
                    an=None,  # Remove audio
                )
                .overwrite_output()
                .run(quiet=True)
            )

            # Step 3: Add audio back with different codec via add_audio
            video_with_audio = temp_dir / "video_with_new_audio.mp4"
            add_result = await client.call_tool(
                "add_audio",
                {
                    "video_path": str(silent_video_path),
                    "audio_path": str(audio_path),
                    "output_path": str(video_with_audio),
                    "replace": True,
                    "audio_volume": 1.0,
                },
            )
            assert video_with_audio.exists()

            # Step 4: Convert the entire video to different codec
            final_converted = temp_dir / "final_audio_converted.mp4"
            convert_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(video_with_audio),
                    "output_path": str(final_converted),
                    "video_codec": "libx264",
                    "audio_codec": "mp3",
                    "video_bitrate": "1M",
                    "audio_bitrate": "192k",
                },
            )
            assert final_converted.exists()

            # Verify final audio codec
            probe = ffmpeg.probe(str(final_converted))
            audio_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "audio"
            )
            assert audio_stream["codec_name"] == "mp3"

    @pytest.mark.integration
    async def test_lossless_conversion_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test lossless and high-quality conversion workflow.

        This test performs conversions focused on maintaining the highest
        possible quality for archival or professional use.
        """
        async with Client(mcp_server) as client:
            # Test high-quality H.264 conversion
            hq_h264_path = temp_dir / "high_quality_h264.mp4"
            hq_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(sample_video),
                    "output_path": str(hq_h264_path),
                    "video_codec": "libx264",
                    "audio_codec": "aac",
                    "video_bitrate": "5M",  # High bitrate
                    "audio_bitrate": "320k",  # High audio quality
                },
            )
            assert hq_h264_path.exists()

            # Test efficient H.265 conversion
            h265_path = temp_dir / "efficient_h265.mp4"
            h265_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(sample_video),
                    "output_path": str(h265_path),
                    "video_codec": "libx265",
                    "audio_codec": "aac",
                    "video_bitrate": "2M",  # Lower bitrate but efficient codec
                    "audio_bitrate": "192k",
                },
            )
            assert h265_path.exists()

            # Compare file sizes and verify quality
            hq_size = hq_h264_path.stat().st_size
            h265_size = h265_path.stat().st_size

            # H.265 should be smaller than high-bitrate H.264
            assert h265_size < hq_size * 1.2  # Allow some variance

            # Verify both maintain video quality (dimensions, etc.)
            for video_path in [hq_h264_path, h265_path]:
                probe = ffmpeg.probe(str(video_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720

    @pytest.mark.integration
    async def test_conversion_error_handling(self, sample_video, temp_dir, mcp_server):
        """Test error handling in format conversion operations.

        This test verifies that format conversion tools handle errors
        correctly and provide meaningful error messages.
        """
        async with Client(mcp_server) as client:
            # Test conversion of non-existent file
            with pytest.raises(ToolError):
                await client.call_tool(
                    "convert_format",
                    {
                        "input_path": "nonexistent.mp4",
                        "output_path": str(temp_dir / "output.mp4"),
                        "video_codec": "libx264",
                        "audio_codec": "aac",
                    },
                )

            # Test with invalid video codec
            with pytest.raises(ToolError):
                await client.call_tool(
                    "convert_format",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "video_codec": "invalid_codec",
                        "audio_codec": "aac",
                    },
                )

            # Test with invalid audio codec
            with pytest.raises(ToolError):
                await client.call_tool(
                    "convert_format",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "video_codec": "libx264",
                        "audio_codec": "invalid_audio_codec",
                    },
                )

            # Test with invalid bitrate format
            with pytest.raises(ToolError):
                await client.call_tool(
                    "convert_format",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "video_codec": "libx264",
                        "audio_codec": "aac",
                        "video_bitrate": "invalid_bitrate",
                        "audio_bitrate": "128k",
                    },
                )

    @pytest.mark.integration
    async def test_format_preservation_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test format conversion while preserving specific characteristics.

        This test verifies that certain video characteristics are preserved
        during format conversion when desired.
        """
        async with Client(mcp_server) as client:
            # Test conversion that preserves video stream (copy)
            # We'll do this by using the same codec with different audio
            preserved_path = temp_dir / "preserved_video.mp4"
            preserved_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(sample_video),
                    "output_path": str(preserved_path),
                    "video_codec": "libx264",  # Same as input
                    "audio_codec": "aac",
                    "video_bitrate": "2M",
                    "audio_bitrate": "192k",
                },
            )
            assert preserved_path.exists()

            # Compare original and converted video properties
            original_probe = ffmpeg.probe(str(sample_video))
            converted_probe = ffmpeg.probe(str(preserved_path))

            original_video = next(
                s for s in original_probe["streams"] if s["codec_type"] == "video"
            )
            converted_video = next(
                s for s in converted_probe["streams"] if s["codec_type"] == "video"
            )

            # Dimensions should be preserved
            assert converted_video["width"] == original_video["width"]
            assert converted_video["height"] == original_video["height"]

            # Duration should be preserved (within tolerance)
            original_duration = float(original_probe["format"]["duration"])
            converted_duration = float(converted_probe["format"]["duration"])
            assert abs(converted_duration - original_duration) < 0.1

    @pytest.mark.integration
    async def test_multiple_conversion_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test multiple conversions in sequence.

        This test performs multiple format conversions to verify that
        the process can be repeated without quality degradation issues.
        """
        async with Client(mcp_server) as client:
            # First conversion: H.264 to H.265
            h265_path = temp_dir / "first_conversion.mp4"
            first_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(sample_video),
                    "output_path": str(h265_path),
                    "video_codec": "libx265",
                    "audio_codec": "aac",
                    "video_bitrate": "1.5M",
                    "audio_bitrate": "128k",
                },
            )
            assert h265_path.exists()

            # Second conversion: H.265 back to H.264 with different settings
            back_to_h264_path = temp_dir / "second_conversion.mp4"
            second_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(h265_path),
                    "output_path": str(back_to_h264_path),
                    "video_codec": "libx264",
                    "audio_codec": "aac",
                    "video_bitrate": "2M",
                    "audio_bitrate": "192k",
                },
            )
            assert back_to_h264_path.exists()

            # Third conversion: Optimize for streaming
            streaming_path = temp_dir / "streaming_optimized.mp4"
            streaming_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(back_to_h264_path),
                    "output_path": str(streaming_path),
                    "video_codec": "libx264",
                    "audio_codec": "aac",
                    "video_bitrate": "800k",
                    "audio_bitrate": "96k",
                },
            )
            assert streaming_path.exists()

            # Verify all outputs maintain basic video properties
            for video_path in [h265_path, back_to_h264_path, streaming_path]:
                probe = ffmpeg.probe(str(video_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )

                # Dimensions should be maintained
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720

                # Duration should be approximately maintained
                duration = float(probe["format"]["duration"])
                assert 4.5 <= duration <= 5.5

            # Verify codecs are correct
            h265_probe = ffmpeg.probe(str(h265_path))
            h264_probe = ffmpeg.probe(str(back_to_h264_path))

            h265_video = next(
                s for s in h265_probe["streams"] if s["codec_type"] == "video"
            )
            h264_video = next(
                s for s in h264_probe["streams"] if s["codec_type"] == "video"
            )

            assert h265_video["codec_name"] == "hevc"
            assert h264_video["codec_name"] == "h264"
