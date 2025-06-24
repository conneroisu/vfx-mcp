"""End-to-end tests for video effects and filters.

This module provides comprehensive end-to-end testing for video effects
tools including apply_filter, change_speed, and generate_thumbnail.
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


class TestVideoEffectsE2E:
    """End-to-end tests for video effects and filters."""

    @pytest.mark.integration
    async def test_complete_effects_workflow(self, sample_video, temp_dir, mcp_server):
        """Test applying multiple effects in sequence.

        This test applies multiple video effects in sequence to simulate
        a realistic video editing workflow with various effects.
        """
        async with Client(mcp_server) as client:
            # Step 1: Apply brightness filter
            bright_path = temp_dir / "bright.mp4"
            bright_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(sample_video),
                    "output_path": str(bright_path),
                    "filter": "brightness",
                    "strength": 1.3,
                },
            )
            assert bright_path.exists()

            # Step 2: Apply contrast to the brightened video
            contrast_path = temp_dir / "bright_contrast.mp4"
            contrast_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(bright_path),
                    "output_path": str(contrast_path),
                    "filter": "contrast",
                    "strength": 1.2,
                },
            )
            assert contrast_path.exists()

            # Step 3: Apply saturation boost
            saturated_path = temp_dir / "final_effects.mp4"
            saturation_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(contrast_path),
                    "output_path": str(saturated_path),
                    "filter": "saturation",
                    "strength": 1.4,
                },
            )
            assert saturated_path.exists()

            # Step 4: Generate thumbnail from final result
            thumb_path = temp_dir / "effects_thumb.jpg"
            thumb_result = await client.call_tool(
                "generate_thumbnail",
                {
                    "input_path": str(saturated_path),
                    "output_path": str(thumb_path),
                    "timestamp": 2.5,
                    "width": 480,
                    "height": 270,
                },
            )
            assert thumb_path.exists()

            # Verify thumbnail properties
            thumb_probe = ffmpeg.probe(str(thumb_path))
            thumb_stream = next(
                s for s in thumb_probe["streams"] if s["codec_type"] == "video"
            )
            assert thumb_stream["width"] == 480
            assert thumb_stream["height"] == 270

    @pytest.mark.integration
    async def test_speed_change_workflow(self, sample_video, temp_dir, mcp_server):
        """Test speed change operations and validation.

        This test changes video speed and verifies the duration
        changes correctly, then applies additional processing.
        """
        async with Client(mcp_server) as client:
            # Step 1: Speed up video by 2x
            fast_path = temp_dir / "fast.mp4"
            fast_result = await client.call_tool(
                "change_speed",
                {
                    "input_path": str(sample_video),
                    "output_path": str(fast_path),
                    "speed": 2.0,
                },
            )
            assert fast_path.exists()

            # Verify duration is halved
            original_probe = ffmpeg.probe(str(sample_video))
            fast_probe = ffmpeg.probe(str(fast_path))

            original_duration = float(original_probe["format"]["duration"])
            fast_duration = float(fast_probe["format"]["duration"])

            expected_duration = original_duration / 2.0
            assert abs(fast_duration - expected_duration) < 0.5

            # Step 2: Slow down original video by 0.5x
            slow_path = temp_dir / "slow.mp4"
            slow_result = await client.call_tool(
                "change_speed",
                {
                    "input_path": str(sample_video),
                    "output_path": str(slow_path),
                    "speed": 0.5,
                },
            )
            assert slow_path.exists()

            # Verify duration is doubled
            slow_probe = ffmpeg.probe(str(slow_path))
            slow_duration = float(slow_probe["format"]["duration"])

            expected_slow_duration = original_duration * 2.0
            assert abs(slow_duration - expected_slow_duration) < 0.5

            # Step 3: Generate thumbnails from both speed variants
            for name, video_path in [("fast", fast_path), ("slow", slow_path)]:
                thumb_path = temp_dir / f"{name}_thumb.png"
                thumb_result = await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(video_path),
                        "output_path": str(thumb_path),
                        "timestamp": 1.0,
                    },
                )
                assert thumb_path.exists()

    @pytest.mark.integration
    async def test_filter_combinations_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test combining different filters for creative effects.

        This test applies various filter combinations to create
        different artistic effects and validates the results.
        """
        filters_to_test = [
            ("hflip", 1.0, "flipped.mp4"),
            ("grayscale", 0.8, "bw.mp4"),
            ("sepia", 0.7, "vintage.mp4"),
            ("blur", 1.5, "blurred.mp4"),
            ("sharpen", 1.3, "sharp.mp4"),
        ]

        async with Client(mcp_server) as client:
            for filter_name, strength, output_name in filters_to_test:
                output_path = temp_dir / output_name

                filter_result = await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "filter": filter_name,
                        "strength": strength,
                    },
                )
                assert output_path.exists()

                # Verify video properties are maintained
                probe = ffmpeg.probe(str(output_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720

    @pytest.mark.integration
    async def test_thumbnail_generation_variations(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test thumbnail generation with different parameters.

        This test generates thumbnails with various settings to verify
        all thumbnail generation options work correctly.
        """
        thumbnail_tests = [
            # (timestamp, width, height, filename)
            (1.0, 320, 240, "thumb_small.jpg"),
            (2.5, 640, 360, "thumb_medium.jpg"),
            (4.0, 1280, 720, "thumb_large.jpg"),
            (0.5, 160, 120, "thumb_tiny.png"),
            (3.5, 800, 450, "thumb_custom.jpg"),
        ]

        async with Client(mcp_server) as client:
            for timestamp, width, height, filename in thumbnail_tests:
                output_path = temp_dir / filename

                thumb_result = await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "timestamp": timestamp,
                        "width": width,
                        "height": height,
                    },
                )
                assert output_path.exists()

                # Verify thumbnail dimensions
                probe = ffmpeg.probe(str(output_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )
                assert video_stream["width"] == width
                assert video_stream["height"] == height

    @pytest.mark.integration
    async def test_advanced_filter_workflow(self, sample_video, temp_dir, mcp_server):
        """Test advanced filter operations and parameter handling.

        This test applies filters with specific parameters and verifies
        advanced filter functionality works correctly.
        """
        async with Client(mcp_server) as client:
            # Test scale filter with parameters
            scale_path = temp_dir / "scaled_filter.mp4"
            scale_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(sample_video),
                    "output_path": str(scale_path),
                    "filter": "scale=960:540",
                    "strength": 1.0,  # Not used for scale filter
                },
            )
            assert scale_path.exists()

            # Verify scaling worked
            probe = ffmpeg.probe(str(scale_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 960
            assert video_stream["height"] == 540

            # Test strength variations for blur filter
            strength_tests = [
                (0.5, "blur_light.mp4"),
                (1.0, "blur_normal.mp4"),
                (2.0, "blur_heavy.mp4"),
                (3.0, "blur_extreme.mp4"),
            ]

            for strength, filename in strength_tests:
                output_path = temp_dir / filename

                blur_result = await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "filter": "blur",
                        "strength": strength,
                    },
                )
                assert output_path.exists()

                # Verify video properties maintained
                probe = ffmpeg.probe(str(output_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720

    @pytest.mark.integration
    async def test_effects_with_video_operations_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test effects combined with other video operations.

        This test combines effects with trimming, resizing, and other
        operations to verify the complete pipeline works correctly.
        """
        async with Client(mcp_server) as client:
            # Step 1: Trim video first
            trimmed_path = temp_dir / "trimmed_for_effects.mp4"
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

            # Step 2: Apply effect to trimmed video
            effect_path = temp_dir / "trimmed_with_effect.mp4"
            effect_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(trimmed_path),
                    "output_path": str(effect_path),
                    "filter": "vintage",
                    "strength": 1.2,
                },
            )
            assert effect_path.exists()

            # Step 3: Resize the video with effects
            resized_path = temp_dir / "resized_with_effects.mp4"
            resize_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(effect_path),
                    "output_path": str(resized_path),
                    "scale": 0.75,
                },
            )
            assert resized_path.exists()

            # Step 4: Change speed of the processed video
            speed_path = temp_dir / "final_processed.mp4"
            speed_result = await client.call_tool(
                "change_speed",
                {
                    "input_path": str(resized_path),
                    "output_path": str(speed_path),
                    "speed": 1.5,
                },
            )
            assert speed_path.exists()

            # Step 5: Generate final thumbnail
            final_thumb = temp_dir / "final_thumb.jpg"
            thumb_result = await client.call_tool(
                "generate_thumbnail",
                {
                    "input_path": str(speed_path),
                    "output_path": str(final_thumb),
                    "timestamp": 1.0,
                    "width": 640,
                    "height": 360,
                },
            )
            assert final_thumb.exists()

            # Verify final video properties
            probe = ffmpeg.probe(str(speed_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )

            # Check dimensions (75% of original)
            assert video_stream["width"] == 960  # 1280 * 0.75
            assert video_stream["height"] == 540  # 720 * 0.75

            # Check duration (3s trimmed, then 1.5x speed = ~2s)
            duration = float(probe["format"]["duration"])
            expected_duration = 3.0 / 1.5  # 3 seconds / 1.5x speed
            assert abs(duration - expected_duration) < 0.5

    @pytest.mark.integration
    async def test_speed_change_edge_cases(self, sample_video, temp_dir, mcp_server):
        """Test speed change with edge case values.

        This test verifies that speed changes work correctly at the
        boundaries of acceptable values.
        """
        speed_tests = [
            (0.25, "very_slow.mp4"),  # Minimum speed
            (0.5, "half_speed.mp4"),
            (1.5, "fast.mp4"),
            (2.0, "double_speed.mp4"),
            (3.0, "triple_speed.mp4"),
            (4.0, "very_fast.mp4"),  # Maximum speed
        ]

        async with Client(mcp_server) as client:
            for speed, filename in speed_tests:
                output_path = temp_dir / filename

                speed_result = await client.call_tool(
                    "change_speed",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "speed": speed,
                    },
                )
                assert output_path.exists()

                # Verify duration change
                original_probe = ffmpeg.probe(str(sample_video))
                new_probe = ffmpeg.probe(str(output_path))

                original_duration = float(original_probe["format"]["duration"])
                new_duration = float(new_probe["format"]["duration"])

                expected_duration = original_duration / speed
                assert abs(new_duration - expected_duration) < 0.5

                # Verify video properties maintained
                video_stream = next(
                    s for s in new_probe["streams"] if s["codec_type"] == "video"
                )
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720

    @pytest.mark.integration
    async def test_color_correction_workflow(self, sample_video, temp_dir, mcp_server):
        """Test color correction and grading workflow.

        This test applies various color correction filters to simulate
        a professional color grading workflow.
        """
        color_tests = [
            ("brightness", 1.2, "brighter.mp4"),
            ("contrast", 1.3, "high_contrast.mp4"),
            ("saturation", 1.5, "vibrant.mp4"),
            ("brightness", 0.8, "darker.mp4"),
            ("contrast", 0.7, "low_contrast.mp4"),
            ("saturation", 0.5, "desaturated.mp4"),
        ]

        async with Client(mcp_server) as client:
            for filter_name, strength, filename in color_tests:
                output_path = temp_dir / filename

                color_result = await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "filter": filter_name,
                        "strength": strength,
                    },
                )
                assert output_path.exists()

                # Verify properties maintained
                probe = ffmpeg.probe(str(output_path))
                video_stream = next(
                    s for s in probe["streams"] if s["codec_type"] == "video"
                )
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720

                # Generate thumbnail to visually verify effect
                thumb_path = temp_dir / f"{filename.replace('.mp4', '_thumb.jpg')}"
                thumb_result = await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(output_path),
                        "output_path": str(thumb_path),
                        "timestamp": 2.5,
                        "width": 320,
                        "height": 180,
                    },
                )
                assert thumb_path.exists()

    @pytest.mark.integration
    async def test_artistic_effects_workflow(self, sample_video, temp_dir, mcp_server):
        """Test artistic effects and stylization.

        This test applies artistic effects to create stylized versions
        of the video for creative purposes.
        """
        artistic_effects = [
            ("sepia", 1.0, "vintage_sepia.mp4"),
            ("grayscale", 1.0, "black_white.mp4"),
            ("vintage", 0.8, "retro_look.mp4"),
        ]

        async with Client(mcp_server) as client:
            for effect, strength, filename in artistic_effects:
                output_path = temp_dir / filename

                effect_result = await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "filter": effect,
                        "strength": strength,
                    },
                )
                assert output_path.exists()

                # Create thumbnail for each artistic effect
                thumb_path = temp_dir / f"{effect}_thumb.jpg"
                thumb_result = await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(output_path),
                        "output_path": str(thumb_path),
                        "timestamp": 2.5,
                        "width": 480,
                        "height": 270,
                    },
                )
                assert thumb_path.exists()

                # Verify thumbnail dimensions
                thumb_probe = ffmpeg.probe(str(thumb_path))
                thumb_stream = next(
                    s for s in thumb_probe["streams"] if s["codec_type"] == "video"
                )
                assert thumb_stream["width"] == 480
                assert thumb_stream["height"] == 270

    @pytest.mark.integration
    async def test_effects_error_handling(self, sample_video, temp_dir, mcp_server):
        """Test error handling in video effects operations.

        This test verifies that video effects tools handle errors
        correctly and provide meaningful error messages.
        """
        async with Client(mcp_server) as client:
            # Test invalid filter name
            with pytest.raises(ToolError):
                await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "filter": "nonexistent_filter",
                        "strength": 1.0,
                    },
                )

            # Test invalid speed value (too low)
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "change_speed",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "speed": 0.1,  # Too low
                    },
                )

            # Test invalid speed value (too high)
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "change_speed",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "speed": 10.0,  # Too high
                    },
                )

            # Test invalid speed value (zero)
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "change_speed",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "speed": 0.0,  # Invalid
                    },
                )

            # Test invalid filter strength (too low)
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "filter": "blur",
                        "strength": 0.05,  # Too low
                    },
                )

            # Test invalid filter strength (too high)
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "filter": "blur",
                        "strength": 5.0,  # Too high
                    },
                )

            # Test invalid thumbnail dimensions (too small)
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "thumb.jpg"),
                        "width": 10,  # Too small
                        "height": 10,
                    },
                )

            # Test invalid thumbnail dimensions (too large)
            with pytest.raises((ValueError, RuntimeError)):
                await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "thumb.jpg"),
                        "width": 5000,  # Too large
                        "height": 3000,
                    },
                )

            # Test thumbnail with invalid timestamp (negative)
            with pytest.raises(ToolError):
                await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "thumb.jpg"),
                        "timestamp": -1.0,  # Negative
                    },
                )

            # Test operations on non-existent file
            with pytest.raises(ToolError):
                await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": "nonexistent.mp4",
                        "output_path": str(temp_dir / "output.mp4"),
                        "filter": "blur",
                        "strength": 1.0,
                    },
                )

    @pytest.mark.integration
    async def test_thumbnail_timestamp_handling(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test thumbnail generation with various timestamp values.

        This test verifies that thumbnail generation handles different
        timestamp values correctly, including edge cases.
        """
        # Get video duration first
        probe = ffmpeg.probe(str(sample_video))
        duration = float(probe["format"]["duration"])

        timestamp_tests = [
            (0.0, "thumb_start.jpg"),
            (duration / 2, "thumb_middle.jpg"),
            (duration - 0.5, "thumb_near_end.jpg"),
            (0.1, "thumb_very_start.jpg"),
            (duration - 0.1, "thumb_very_end.jpg"),
        ]

        async with Client(mcp_server) as client:
            for timestamp, filename in timestamp_tests:
                output_path = temp_dir / filename

                thumb_result = await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(output_path),
                        "timestamp": timestamp,
                        "width": 320,
                        "height": 240,
                    },
                )
                assert output_path.exists()

                # Verify thumbnail properties
                thumb_probe = ffmpeg.probe(str(output_path))
                thumb_stream = next(
                    s for s in thumb_probe["streams"] if s["codec_type"] == "video"
                )
                assert thumb_stream["width"] == 320
                assert thumb_stream["height"] == 240
