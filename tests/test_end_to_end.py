"""End-to-end tests for all VFX MCP tools.

This module provides comprehensive end-to-end testing for all video editing tools
in the VFX MCP server. Tests cover realistic workflows and complete operations
from input to output validation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
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
    async def test_image_to_video_workflow(
        self, temp_dir, mcp_server
    ):
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
                s for s in final_probe["streams"]
                if s["codec_type"] == "video"
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
                s for s in final_probe["streams"]
                if s["codec_type"] == "video"
            )
            assert video_stream["height"] == 240
            assert video_stream["width"] == 320  # Maintains aspect ratio


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
                s for s in audio_probe["streams"]
                if s["codec_type"] == "audio"
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
            ("mp3", "libmp3lame", "192k"),
            ("wav", "pcm_s16le", None),
            ("aac", "aac", "128k"),
            ("ogg", "libvorbis", "256k"),
        ]
        
        async with Client(mcp_server) as client:
            for format_name, expected_codec, bitrate in formats_to_test:
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
                    s for s in probe["streams"]
                    if s["codec_type"] == "audio"
                )
                
                # Check codec (some formats have different probe names)
                if format_name == "mp3":
                    assert audio_stream["codec_name"] == "mp3"
                elif format_name == "aac":
                    assert audio_stream["codec_name"] == "aac"
                elif format_name == "ogg":
                    assert audio_stream["codec_name"] == "vorbis"


class TestVideoEffectsE2E:
    """End-to-end tests for video effects and filters."""

    @pytest.mark.integration
    async def test_complete_effects_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
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
                s for s in thumb_probe["streams"]
                if s["codec_type"] == "video"
            )
            assert thumb_stream["width"] == 480
            assert thumb_stream["height"] == 270

    @pytest.mark.integration
    async def test_speed_change_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
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
                    s for s in probe["streams"]
                    if s["codec_type"] == "video"
                )
                assert video_stream["width"] == 1280
                assert video_stream["height"] == 720


class TestFormatConversionE2E:
    """End-to-end tests for format conversion operations."""

    @pytest.mark.integration
    async def test_format_conversion_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
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
                s for s in probe["streams"]
                if s["codec_type"] == "video"
            )
            audio_stream = next(
                s for s in probe["streams"]
                if s["codec_type"] == "audio"
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


class TestMCPResourcesE2E:
    """End-to-end tests for MCP resource endpoints."""

    @pytest.mark.integration
    async def test_resources_with_video_operations(
        self, sample_videos, temp_dir, mcp_server
    ):
        """Test MCP resources in combination with video operations.
        
        This test uses MCP resources to discover videos and then
        processes them using the discovered information.
        """
        # Change to temp directory for resource discovery
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            async with Client(mcp_server) as client:
                # Step 1: List videos using resource endpoint
                list_result = await client.read_resource("videos://list")
                video_list = json.loads(list_result[0].text)
                
                assert "videos" in video_list
                assert len(video_list["videos"]) == len(sample_videos)
                
                # Step 2: Get metadata for each video using resources
                video_metadata = []
                for video_filename in video_list["videos"]:
                    metadata_result = await client.read_resource(
                        f"videos://{video_filename}/metadata"
                    )
                    metadata = json.loads(metadata_result[0].text)
                    video_metadata.append(metadata)
                
                # Verify metadata structure
                for metadata in video_metadata:
                    assert "filename" in metadata
                    assert "duration" in metadata
                    assert "video" in metadata
                    assert metadata["video"]["width"] == 640
                    assert metadata["video"]["height"] == 480
                
                # Step 3: Process videos based on discovered metadata
                for i, metadata in enumerate(video_metadata):
                    if metadata["duration"] >= 1.5:  # Only process longer videos
                        video_path = temp_dir / metadata["filename"]
                        output_path = temp_dir / f"processed_{i}.mp4"
                        
                        # Trim based on duration
                        trim_duration = min(1.0, metadata["duration"] - 0.5)
                        trim_result = await client.call_tool(
                            "trim_video",
                            {
                                "input_path": str(video_path),
                                "output_path": str(output_path),
                                "start_time": 0.5,
                                "duration": trim_duration,
                            },
                        )
                        assert output_path.exists()
                
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_error_handling(
        self, temp_dir, mcp_server
    ):
        """Test error handling for MCP resources.
        
        This test verifies that resource endpoints handle errors correctly
        when files don't exist or directories are empty.
        """
        # Create empty directory
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        original_cwd = os.getcwd()
        os.chdir(empty_dir)
        
        try:
            async with Client(mcp_server) as client:
                # Test listing videos in empty directory
                list_result = await client.read_resource("videos://list")
                video_list = json.loads(list_result[0].text)
                
                assert "videos" in video_list
                assert len(video_list["videos"]) == 0
                
                # Test metadata for non-existent file
                with pytest.raises(Exception):  # Should raise an error
                    await client.read_resource(
                        "videos://nonexistent.mp4/metadata"
                    )
                
        finally:
            os.chdir(original_cwd)


class TestErrorHandlingE2E:
    """End-to-end tests for error handling across all tools."""

    @pytest.mark.integration
    async def test_invalid_input_handling(
        self, temp_dir, mcp_server
    ):
        """Test error handling for various invalid inputs.
        
        This test verifies that all tools handle invalid inputs gracefully
        and provide meaningful error messages.
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
            
            # Test invalid speed value
            with pytest.raises(Exception):
                await client.call_tool(
                    "change_speed",
                    {
                        "input_path": "test.mp4",
                        "output_path": "output.mp4",
                        "speed": 0,  # Invalid speed
                    },
                )
            
            # Test invalid filter
            with pytest.raises(ToolError):
                await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": "test.mp4",
                        "output_path": "output.mp4",
                        "filter": "invalid_filter_name",
                    },
                )
            
            # Test invalid audio format
            with pytest.raises(Exception):
                await client.call_tool(
                    "extract_audio",
                    {
                        "input_path": "test.mp4",
                        "output_path": "output.xyz",
                        "format": "invalid_format",
                    },
                )

    @pytest.mark.integration
    async def test_parameter_validation_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test parameter validation across different tools.
        
        This test verifies that parameter validation works correctly
        and provides helpful error messages for edge cases.
        """
        async with Client(mcp_server) as client:
            # Test resize with invalid scale
            with pytest.raises(Exception):
                await client.call_tool(
                    "resize_video",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "scale": 15.0,  # Too large
                    },
                )
            
            # Test resize with conflicting parameters
            with pytest.raises(Exception):
                await client.call_tool(
                    "resize_video",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "output.mp4"),
                        "width": 640,
                        "height": 480,  # Both width and height provided
                    },
                )
            
            # Test thumbnail with invalid dimensions
            with pytest.raises(Exception):
                await client.call_tool(
                    "generate_thumbnail",
                    {
                        "input_path": str(sample_video),
                        "output_path": str(temp_dir / "thumb.jpg"),
                        "width": 10,  # Too small
                        "height": 10,
                    },
                )
            
            # Test audio volume out of range
            with pytest.raises(Exception):
                await client.call_tool(
                    "add_audio",
                    {
                        "video_path": str(sample_video),
                        "audio_path": str(sample_video),  # Using video as audio for test
                        "output_path": str(temp_dir / "output.mp4"),
                        "audio_volume": 5.0,  # Too high
                    },
                )


class TestPerformanceE2E:
    """End-to-end performance tests for demanding operations."""

    @pytest.mark.slow
    @pytest.mark.integration
    async def test_large_file_processing_workflow(
        self, temp_dir, mcp_server
    ):
        """Test processing larger files to verify performance and stability.
        
        This test creates a longer video and processes it to ensure
        the tools can handle more demanding operations.
        """
        # Create a longer test video (30 seconds)
        long_video_path = temp_dir / "long_video.mp4"
        (
            ffmpeg.input(
                "testsrc=duration=30:size=1920x1080:rate=30",
                f="lavfi",
            )
            .output(
                str(long_video_path),
                vcodec="libx264",
                preset="ultrafast",
                **{"f": "mp4"},
            )
            .overwrite_output()
            .run(quiet=True)
        )
        
        async with Client(mcp_server) as client:
            # Step 1: Trim a segment from the long video
            segment_path = temp_dir / "segment.mp4"
            trim_result = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(long_video_path),
                    "output_path": str(segment_path),
                    "start_time": 10.0,
                    "duration": 5.0,
                },
            )
            assert segment_path.exists()
            
            # Step 2: Resize to smaller resolution
            resized_path = temp_dir / "resized_hd.mp4"
            resize_result = await client.call_tool(
                "resize_video",
                {
                    "input_path": str(segment_path),
                    "output_path": str(resized_path),
                    "width": 1280,
                },
            )
            assert resized_path.exists()
            
            # Step 3: Apply effects
            effects_path = temp_dir / "effects_hd.mp4"
            effects_result = await client.call_tool(
                "apply_filter",
                {
                    "input_path": str(resized_path),
                    "output_path": str(effects_path),
                    "filter": "contrast",
                    "strength": 1.2,
                },
            )
            assert effects_path.exists()
            
            # Step 4: Convert format
            final_path = temp_dir / "final_hd.mp4"
            convert_result = await client.call_tool(
                "convert_format",
                {
                    "input_path": str(effects_path),
                    "output_path": str(final_path),
                    "video_codec": "libx265",
                    "video_bitrate": "2M",
                    "audio_bitrate": "128k",
                },
            )
            assert final_path.exists()
            
            # Verify final output quality
            probe = ffmpeg.probe(str(final_path))
            video_stream = next(
                s for s in probe["streams"]
                if s["codec_type"] == "video"
            )
            assert video_stream["codec_name"] == "hevc"
            assert video_stream["width"] == 1280
            assert video_stream["height"] == 720

    @pytest.mark.slow
    @pytest.mark.integration
    async def test_batch_operations_workflow(
        self, temp_dir, mcp_server
    ):
        """Test batch processing multiple videos efficiently.
        
        This test processes multiple videos in sequence to verify
        the system can handle batch operations reliably.
        """
        # Create multiple test videos
        test_videos = []
        for i in range(5):
            video_path = temp_dir / f"batch_video_{i}.mp4"
            (
                ffmpeg.input(
                    f"testsrc=duration=3:size=640x480:rate=24",
                    f="lavfi",
                )
                .output(
                    str(video_path),
                    vcodec="libx264",
                    preset="ultrafast",
                    **{"f": "mp4"},
                )
                .overwrite_output()
                .run(quiet=True)
            )
            test_videos.append(video_path)
        
        async with Client(mcp_server) as client:
            processed_videos = []
            
            # Process each video
            for i, video_path in enumerate(test_videos):
                # Trim each video
                trimmed_path = temp_dir / f"trimmed_{i}.mp4"
                trim_result = await client.call_tool(
                    "trim_video",
                    {
                        "input_path": str(video_path),
                        "output_path": str(trimmed_path),
                        "start_time": 0.5,
                        "duration": 2.0,
                    },
                )
                assert trimmed_path.exists()
                
                # Apply different effects to each
                effects = ["brightness", "contrast", "saturation", "blur", "sharpen"]
                effect_path = temp_dir / f"effect_{i}.mp4"
                effect_result = await client.call_tool(
                    "apply_filter",
                    {
                        "input_path": str(trimmed_path),
                        "output_path": str(effect_path),
                        "filter": effects[i],
                        "strength": 1.2,
                    },
                )
                assert effect_path.exists()
                processed_videos.append(effect_path)
            
            # Concatenate all processed videos
            final_concat_path = temp_dir / "batch_final.mp4"
            concat_result = await client.call_tool(
                "concatenate_videos",
                {
                    "input_paths": [str(v) for v in processed_videos],
                    "output_path": str(final_concat_path),
                },
            )
            assert final_concat_path.exists()
            
            # Verify final concatenated video
            probe = ffmpeg.probe(str(final_concat_path))
            duration = float(probe["format"]["duration"])
            assert 9.5 <= duration <= 10.5  # ~10 seconds total (5 videos * 2s each)