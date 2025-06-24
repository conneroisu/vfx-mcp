"""End-to-end tests for basic video operations.

This module provides comprehensive end-to-end testing for basic video editing
tools including trim, resize, concatenate, get_video_info, and image_to_video.
Tests cover realistic workflows and complete operations from input to output validation.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import ffmpeg
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

if TYPE_CHECKING:
    pass


class TestBasicVideoOperationsE2E:
    """End-to-end tests for basic video operations."""

    @pytest.mark.integration
    async def test_complete_video_editing_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test a complete video editing workflow: trim, resize, get info.

        This test simulates a realistic workflow where a user:
        1. Gets video information
        2. Trims the video to a shorter segment
        3. Resizes the trimmed video
        4. Validates the final output
        """
        async with Client(mcp_server) as client:
            # Step 1: Get original video info
            info_result = await client.call_tool(
                "get_video_info",
                {"video_path": str(sample_video)},
            )
            original_info = json.loads(info_result[0].text)

            # Validate original video properties
            assert original_info["video"]["width"] == 1280
            assert original_info["video"]["height"] == 720
            assert 4.9 <= original_info["duration"] <= 5.1

            # Step 2: Trim video (2 seconds starting from 1s)
            trimmed_path = temp_dir / "trimmed.mp4"
            trim_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(trimmed_path),
                    "start_time": 1.0,
                    "duration": 2.0,
                },
            )
            assert trimmed_path.exists()

            # Step 3: Resize trimmed video to half size
            resized_path = temp_dir / "resized.mp4"
            resize_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(trimmed_path),
                    "output_path": str(resized_path),
                    "scale": 0.5,
                },
            )
            assert resized_path.exists()

            # Step 4: Validate final output
            final_info_result = await client.call_tool(
                "get_video_info",
                {"video_path": str(resized_path)},
            )
            final_info = json.loads(final_info_result[0].text)

            # Check final video properties
            assert final_info["video"]["width"] == 640
            assert final_info["video"]["height"] == 360
            assert 1.9 <= final_info["duration"] <= 2.1

    @pytest.mark.integration
    async def test_image_to_video_workflow(self, temp_dir, mcp_server):
        """Test creating video from image and then processing it.

        This test creates a video from a static image, then applies
        basic operations to verify the image-to-video functionality
        works correctly in a complete workflow.
        """
        # Create a simple test image using ffmpeg
        image_path = temp_dir / "test_image.png"
        (
            ffmpeg.input(
                "testsrc=duration=1:size=640x480:rate=1",
                f="lavfi",
            )
            .output(str(image_path), vframes=1)
            .overwrite_output()
            .run(quiet=True)
        )

        async with Client(mcp_server) as client:
            # Step 1: Create video from image
            video_path = temp_dir / "from_image.mp4"
            video_result = await client.call_tool(
                "image_to_video",
                {
                    "image_path": str(image_path),
                    "output_path": str(video_path),
                    "duration": 3.0,
                    "framerate": 24,
                },
            )
            assert video_path.exists()

            # Step 2: Verify video properties
            info_result = await client.call_tool(
                "get_video_info",
                {"video_path": str(video_path)},
            )
            info = json.loads(info_result[0].text)

            assert info["video"]["width"] == 640
            assert info["video"]["height"] == 480
            assert 2.9 <= info["duration"] <= 3.1

            # Step 3: Resize the created video
            resized_path = temp_dir / "image_video_resized.mp4"
            resize_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(video_path),
                    "output_path": str(resized_path),
                    "width": 320,
                },
            )
            assert resized_path.exists()

            # Verify final dimensions
            final_probe = ffmpeg.probe(str(resized_path))
            video_stream = next(
                s for s in final_probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 320
            assert video_stream["height"] == 240  # Maintains aspect ratio

    @pytest.mark.integration
    async def test_multi_video_concatenation_workflow(
        self, sample_videos, temp_dir, mcp_server
    ):
        """Test concatenating multiple videos and processing the result.

        This test concatenates multiple videos, then applies effects
        to the concatenated result to verify the concatenation works
        correctly in a complete workflow.
        """
        async with Client(mcp_server) as client:
            # Step 1: Concatenate multiple videos
            concat_path = temp_dir / "concatenated.mp4"
            concat_result = await client.call_tool(
                "concatenate_videos",
                {
                    "input_paths": [str(v) for v in sample_videos],
                    "output_path": str(concat_path),
                },
            )
            assert concat_path.exists()

            # Step 2: Verify concatenated duration
            probe = ffmpeg.probe(str(concat_path))
            duration = float(probe["format"]["duration"])
            assert 5.9 <= duration <= 6.1  # ~6 seconds total

            # Step 3: Extract a portion from the concatenated video
            excerpt_path = temp_dir / "concat_excerpt.mp4"
            trim_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(concat_path),
                    "output_path": str(excerpt_path),
                    "start_time": 2.0,
                    "duration": 2.0,
                },
            )
            assert excerpt_path.exists()

            # Step 4: Resize the excerpt
            final_path = temp_dir / "concat_final.mp4"
            resize_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(excerpt_path),
                    "output_path": str(final_path),
                    "height": 240,
                },
            )
            assert final_path.exists()

            # Verify final properties
            final_probe = ffmpeg.probe(str(final_path))
            video_stream = next(
                s for s in final_probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["height"] == 240
            assert video_stream["width"] == 320  # Maintains aspect ratio

    @pytest.mark.integration
    async def test_resize_variations_workflow(self, sample_video, temp_dir, mcp_server):
        """Test different resize operations in a workflow.

        This test applies various resize operations to verify all
        resize modes work correctly and maintain video quality.
        """
        async with Client(mcp_server) as client:
            # Test resize by width
            width_path = temp_dir / "resized_width.mp4"
            width_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(width_path),
                    "width": 800,
                },
            )
            assert width_path.exists()

            # Verify width-based resize
            probe = ffmpeg.probe(str(width_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 800
            assert video_stream["height"] == 450  # Maintains aspect ratio

            # Test resize by height
            height_path = temp_dir / "resized_height.mp4"
            height_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(height_path),
                    "height": 400,
                },
            )
            assert height_path.exists()

            # Verify height-based resize
            probe = ffmpeg.probe(str(height_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["height"] == 400
            # Original 1280x720, so 400 height gives width = 1280 * (400/720) = ~711
            expected_width = int(1280 * (400 / 720))
            assert (
                abs(video_stream["width"] - expected_width) <= 1
            )  # Allow 1 pixel difference for rounding

            # Test resize by scale
            scale_path = temp_dir / "resized_scale.mp4"
            scale_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(scale_path),
                    "scale": 1.5,
                },
            )
            assert scale_path.exists()

            # Verify scale-based resize
            probe = ffmpeg.probe(str(scale_path))
            video_stream = next(
                s for s in probe["streams"] if s["codec_type"] == "video"
            )
            assert video_stream["width"] == 1920  # 1280 * 1.5
            assert video_stream["height"] == 1080  # 720 * 1.5

    @pytest.mark.integration
    async def test_trim_variations_workflow(self, sample_video, temp_dir, mcp_server):
        """Test different trim operations in a workflow.

        This test applies various trim operations to verify all
        trim modes work correctly with different parameters.
        """
        async with Client(mcp_server) as client:
            # Test trim with duration
            trim_duration_path = temp_dir / "trim_duration.mp4"
            duration_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(trim_duration_path),
                    "start_time": 0.5,
                    "duration": 1.5,
                },
            )
            assert trim_duration_path.exists()

            # Verify duration
            probe = ffmpeg.probe(str(trim_duration_path))
            duration = float(probe["format"]["duration"])
            assert 1.4 <= duration <= 1.6

            # Test trim to end (no duration specified)
            trim_to_end_path = temp_dir / "trim_to_end.mp4"
            to_end_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(trim_to_end_path),
                    "start_time": 3.0,
                },
            )
            assert trim_to_end_path.exists()

            # Verify remaining duration
            probe = ffmpeg.probe(str(trim_to_end_path))
            duration = float(probe["format"]["duration"])
            assert 1.9 <= duration <= 2.1  # Should be ~2 seconds remaining

            # Test trim from beginning
            trim_beginning_path = temp_dir / "trim_beginning.mp4"
            beginning_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(trim_beginning_path),
                    "start_time": 0.0,
                    "duration": 2.5,
                },
            )
            assert trim_beginning_path.exists()

            # Verify duration
            probe = ffmpeg.probe(str(trim_beginning_path))
            duration = float(probe["format"]["duration"])
            assert 2.4 <= duration <= 2.6

    @pytest.mark.integration
    async def test_error_handling_workflow(self, sample_video, temp_dir, mcp_server):
        """Test error handling in basic video operations.

        This test verifies that basic video operations handle errors
        correctly and provide meaningful error messages.
        """
        async with Client(mcp_server) as client:
            # Test non-existent input file
            with pytest.raises(ToolError):
                await client.call_tool(
                    "trim_video",
                    {
                        "input_path": "nonexistent.mp4",
                        "output_path": str(temp_dir / "output.mp4"),
                        "start_time": 0,
                        "duration": 1,
                    },
                )

            # Test invalid resize parameters (multiple parameters)
            with pytest.raises(ToolError):
                await client.call_tool(
                    "resize_video",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "width": 640,
                        "height": 480,  # Can't specify both width and height
                    },
                )

            # Test resize with invalid scale
            with pytest.raises(ToolError):
                await client.call_tool(
                    "resize_video",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "scale": 15.0,  # Too large
                    },
                )

            # Test concatenation with insufficient videos
            with pytest.raises(ToolError):
                await client.call_tool(
                    "concatenate_videos",
                    {
                        "input_paths": [str(sample_video)],  # Only one video
                        "output_path": str(temp_dir / "output.mp4"),
                    },
                )

            # Test image_to_video with invalid parameters
            with pytest.raises(ToolError):
                await client.call_tool(
                    "image_to_video",
                    {
                        "image_path": str(sample_video),  # Using video as image
                        "output_path": str(temp_dir / "output.mp4"),
                        "duration": -1.0,  # Invalid duration
                    },
                )

            # Test image_to_video with invalid framerate
            with pytest.raises(ToolError):
                await client.call_tool(
                    "image_to_video",
                    {
                        "image_path": "test.jpg",
                        "output_path": str(temp_dir / "output.mp4"),
                        "duration": 1.0,
                        "framerate": 200,  # Too high
                    },
                )

    @pytest.mark.integration
    async def test_metadata_consistency_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test metadata consistency across operations.

        This test verifies that video metadata remains consistent
        and accurate after various operations.
        """
        async with Client(mcp_server) as client:
            # Get original metadata
            original_info_result = await client.call_tool(
                "get_video_info",
                {"video_path": str(sample_video)},
            )
            original_info = json.loads(original_info_result[0].text)

            # Perform trim operation
            trimmed_path = temp_dir / "metadata_trim.mp4"
            await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(trimmed_path),
                    "start_time": 1.0,
                    "duration": 2.0,
                },
            )

            # Check metadata after trim
            trimmed_info_result = await client.call_tool(
                "get_video_info",
                {"video_path": str(trimmed_path)},
            )
            trimmed_info = json.loads(trimmed_info_result[0].text)

            # Dimensions should be unchanged after trim
            assert trimmed_info["video"]["width"] == original_info["video"]["width"]
            assert trimmed_info["video"]["height"] == original_info["video"]["height"]
            # Duration should be ~2 seconds
            assert 1.9 <= trimmed_info["duration"] <= 2.1

            # Perform resize operation
            resized_path = temp_dir / "metadata_resize.mp4"
            await client.call_tool(
                "resize_video",
                {
                    "input_path": str(trimmed_path),
                    "output_path": str(resized_path),
                    "scale": 0.75,
                },
            )

            # Check metadata after resize
            resized_info_result = await client.call_tool(
                "get_video_info",
                {"video_path": str(resized_path)},
            )
            resized_info = json.loads(resized_info_result[0].text)

            # Dimensions should be scaled
            expected_width = int(original_info["video"]["width"] * 0.75)
            expected_height = int(original_info["video"]["height"] * 0.75)
            assert resized_info["video"]["width"] == expected_width
            assert resized_info["video"]["height"] == expected_height
            # Duration should remain the same
            assert abs(resized_info["duration"] - trimmed_info["duration"]) < 0.1
