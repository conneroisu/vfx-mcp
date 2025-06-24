"""End-to-end tests for MCP resource endpoints.

This module provides comprehensive end-to-end testing for MCP resource
endpoints including videos://list and videos://{filename}/metadata.
Tests cover realistic workflows combining resource discovery with video operations.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

import ffmpeg
import pytest
from fastmcp import Client

if TYPE_CHECKING:
    pass


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
    async def test_resource_discovery_workflow(self, temp_dir, mcp_server):
        """Test comprehensive resource discovery and processing workflow.

        This test creates multiple videos with different properties,
        discovers them via resources, and processes them based on metadata.
        """
        # Create videos with different properties
        video_specs = [
            {"name": "short.mp4", "duration": 2, "size": "320x240"},
            {"name": "medium.mp4", "duration": 5, "size": "640x480"},
            {"name": "long.mp4", "duration": 8, "size": "1280x720"},
        ]

        created_videos = []
        for spec in video_specs:
            video_path = temp_dir / spec["name"]
            (
                ffmpeg.input(
                    f"testsrc=duration={spec['duration']}:size={spec['size']}:rate=24",
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
            created_videos.append(video_path)

        # Change to temp directory for resource discovery
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            async with Client(mcp_server) as client:
                # Step 1: Discover all videos
                list_result = await client.read_resource("videos://list")
                video_list = json.loads(list_result[0].text)

                assert "videos" in video_list
                assert len(video_list["videos"]) == len(video_specs)

                # Step 2: Analyze each video and categorize
                short_videos = []
                medium_videos = []
                long_videos = []

                for video_filename in video_list["videos"]:
                    metadata_result = await client.read_resource(
                        f"videos://{video_filename}/metadata"
                    )
                    metadata = json.loads(metadata_result[0].text)

                    if metadata["duration"] < 3:
                        short_videos.append((video_filename, metadata))
                    elif metadata["duration"] < 6:
                        medium_videos.append((video_filename, metadata))
                    else:
                        long_videos.append((video_filename, metadata))

                # Step 3: Process videos based on category
                # Short videos: generate thumbnails only
                for filename, metadata in short_videos:
                    thumb_path = temp_dir / f"{filename}_thumb.jpg"
                    thumb_result = await client.call_tool(
                        "generate_thumbnail",
                        {
                            "input_path": filename,
                            "output_path": str(thumb_path),
                            "timestamp": metadata["duration"] / 2,
                            "width": 160,
                            "height": 120,
                        },
                    )
                    assert thumb_path.exists()

                # Medium videos: trim and resize
                for filename, _metadata in medium_videos:
                    trimmed_path = temp_dir / f"trimmed_{filename}"
                    trim_result = await client.call_tool(
                        "trim_video",
                        {
                            "input_path": filename,
                            "output_path": str(trimmed_path),
                            "start_time": 1.0,
                            "duration": 3.0,
                        },
                    )
                    assert trimmed_path.exists()

                    resized_path = temp_dir / f"resized_{filename}"
                    resize_result = await client.call_tool(
                        "resize_video",
                        {
                            "input_path": str(trimmed_path),
                            "output_path": str(resized_path),
                            "scale": 0.5,
                        },
                    )
                    assert resized_path.exists()

                # Long videos: full processing pipeline
                for filename, _metadata in long_videos:
                    # Trim to manageable length
                    trimmed_path = temp_dir / f"processed_{filename}"
                    trim_result = await client.call_tool(
                        "trim_video",
                        {
                            "input_path": filename,
                            "output_path": str(trimmed_path),
                            "start_time": 2.0,
                            "duration": 4.0,
                        },
                    )
                    assert trimmed_path.exists()

                    # Apply effects
                    effects_path = temp_dir / f"effects_{filename}"
                    effects_result = await client.call_tool(
                        "apply_filter",
                        {
                            "input_path": str(trimmed_path),
                            "output_path": str(effects_path),
                            "filter": "contrast",
                            "strength": 1.2,
                        },
                    )
                    assert effects_path.exists()

                    # Convert format for optimization
                    final_path = temp_dir / f"final_{filename}"
                    convert_result = await client.call_tool(
                        "convert_format",
                        {
                            "input_path": str(effects_path),
                            "output_path": str(final_path),
                            "video_codec": "libx265",
                            "audio_codec": "aac",
                            "video_bitrate": "800k",
                            "audio_bitrate": "96k",
                        },
                    )
                    assert final_path.exists()

        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_metadata_driven_processing(self, temp_dir, mcp_server):
        """Test processing videos based on their metadata properties.

        This test discovers video metadata and makes processing decisions
        based on video properties like resolution, duration, and codec.
        """
        # Create videos with different properties for testing
        test_videos = [
            {
                "name": "hd_video.mp4",
                "duration": 4,
                "size": "1920x1080",
                "rate": 30,
            },
            {
                "name": "sd_video.mp4",
                "duration": 6,
                "size": "640x480",
                "rate": 24,
            },
            {
                "name": "square_video.mp4",
                "duration": 3,
                "size": "720x720",
                "rate": 25,
            },
        ]

        for spec in test_videos:
            video_path = temp_dir / spec["name"]
            (
                ffmpeg.input(
                    f"testsrc=duration={spec['duration']}:size={spec['size']}:rate={spec['rate']}",
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

        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            async with Client(mcp_server) as client:
                # Discover and analyze all videos
                list_result = await client.read_resource("videos://list")
                video_list = json.loads(list_result[0].text)

                for video_filename in video_list["videos"]:
                    metadata_result = await client.read_resource(
                        f"videos://{video_filename}/metadata"
                    )
                    metadata = json.loads(metadata_result[0].text)

                    width = metadata["video"]["width"]
                    height = metadata["video"]["height"]
                    duration = metadata["duration"]

                    # Decision logic based on metadata
                    if width >= 1920:  # High resolution
                        # Compress for web delivery
                        compressed_path = temp_dir / f"web_{video_filename}"
                        compress_result = await client.call_tool(
                            "convert_format",
                            {
                                "input_path": video_filename,
                                "output_path": str(compressed_path),
                                "video_codec": "libx264",
                                "audio_codec": "aac",
                                "video_bitrate": "1M",
                                "audio_bitrate": "128k",
                            },
                        )
                        assert compressed_path.exists()

                        # Generate high-quality thumbnail
                        thumb_path = temp_dir / f"hq_{video_filename}_thumb.jpg"
                        thumb_result = await client.call_tool(
                            "generate_thumbnail",
                            {
                                "input_path": video_filename,
                                "output_path": str(thumb_path),
                                "timestamp": duration / 2,
                                "width": 1280,
                                "height": 720,
                            },
                        )
                        assert thumb_path.exists()

                    elif width == height:  # Square format
                        # Optimize for social media
                        social_path = temp_dir / f"social_{video_filename}"
                        social_result = await client.call_tool(
                            "resize_video",
                            {
                                "input_path": video_filename,
                                "output_path": str(social_path),
                                "width": 480,
                            },
                        )
                        assert social_path.exists()

                        # Apply trendy effects
                        effects_path = temp_dir / f"trendy_{video_filename}"
                        effects_result = await client.call_tool(
                            "apply_filter",
                            {
                                "input_path": str(social_path),
                                "output_path": str(effects_path),
                                "filter": "saturation",
                                "strength": 1.4,
                            },
                        )
                        assert effects_path.exists()

                    else:  # Standard format
                        # Standard processing
                        if duration > 5:
                            # Trim longer videos
                            trimmed_path = temp_dir / f"trimmed_{video_filename}"
                            trim_result = await client.call_tool(
                                "trim_video",
                                {
                                    "input_path": video_filename,
                                    "output_path": str(trimmed_path),
                                    "start_time": 1.0,
                                    "duration": 4.0,
                                },
                            )
                            assert trimmed_path.exists()

                        # Standard thumbnail
                        std_thumb_path = temp_dir / f"std_{video_filename}_thumb.jpg"
                        std_thumb_result = await client.call_tool(
                            "generate_thumbnail",
                            {
                                "input_path": video_filename,
                                "output_path": str(std_thumb_path),
                                "timestamp": min(duration / 2, 2.0),
                                "width": 320,
                                "height": 240,
                            },
                        )
                        assert std_thumb_path.exists()

        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_batch_processing_via_resources(self, temp_dir, mcp_server):
        """Test batch processing of videos discovered via resources.

        This test simulates a batch processing scenario where multiple
        videos are processed automatically based on resource discovery.
        """
        # Create a batch of videos to process
        batch_count = 6
        batch_videos = []

        for i in range(batch_count):
            video_path = temp_dir / f"batch_{i:02d}.mp4"
            duration = 2 + (i * 0.5)  # Varying durations
            size = ["320x240", "640x480", "1280x720"][i % 3]  # Varying sizes

            (
                ffmpeg.input(
                    f"testsrc=duration={duration}:size={size}:rate=24",
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
            batch_videos.append(video_path)

        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            async with Client(mcp_server) as client:
                # Step 1: Discover all videos
                list_result = await client.read_resource("videos://list")
                video_list = json.loads(list_result[0].text)

                # Filter for batch videos only
                batch_filenames = [
                    f for f in video_list["videos"] if f.startswith("batch_")
                ]

                # Step 2: Process each video in the batch
                processed_videos = []
                thumbnails = []

                for video_filename in batch_filenames:
                    # Get metadata
                    metadata_result = await client.read_resource(
                        f"videos://{video_filename}/metadata"
                    )
                    metadata = json.loads(metadata_result[0].text)

                    # Standard processing pipeline
                    # 1. Trim to consistent length
                    trimmed_path = temp_dir / f"proc_{video_filename}"
                    trim_duration = min(2.0, metadata["duration"] - 0.2)

                    trim_result = await client.call_tool(
                        "trim_video",
                        {
                            "input_path": video_filename,
                            "output_path": str(trimmed_path),
                            "start_time": 0.1,
                            "duration": trim_duration,
                        },
                    )
                    assert trimmed_path.exists()

                    # 2. Normalize resolution
                    normalized_path = temp_dir / f"norm_{video_filename}"
                    normalize_result = await client.call_tool(
                        "resize_video",
                        {
                            "input_path": str(trimmed_path),
                            "output_path": str(normalized_path),
                            "width": 640,
                        },
                    )
                    assert normalized_path.exists()

                    # 3. Apply consistent effects
                    enhanced_path = temp_dir / f"enh_{video_filename}"
                    enhance_result = await client.call_tool(
                        "apply_filter",
                        {
                            "input_path": str(normalized_path),
                            "output_path": str(enhanced_path),
                            "filter": "brightness",
                            "strength": 1.1,
                        },
                    )
                    assert enhanced_path.exists()
                    processed_videos.append(enhanced_path)

                    # 4. Generate thumbnail
                    thumb_path = (
                        temp_dir / f"thumb_{video_filename.replace('.mp4', '.jpg')}"
                    )
                    thumb_result = await client.call_tool(
                        "generate_thumbnail",
                        {
                            "input_path": str(enhanced_path),
                            "output_path": str(thumb_path),
                            "timestamp": 1.0,
                            "width": 160,
                            "height": 120,
                        },
                    )
                    assert thumb_path.exists()
                    thumbnails.append(thumb_path)

                # Step 3: Concatenate all processed videos
                if len(processed_videos) > 1:
                    final_concat_path = temp_dir / "batch_final.mp4"
                    concat_result = await client.call_tool(
                        "concatenate_videos",
                        {
                            "input_paths": [str(v) for v in processed_videos],
                            "output_path": str(final_concat_path),
                        },
                    )
                    assert final_concat_path.exists()

                    # Verify final video duration
                    probe = ffmpeg.probe(str(final_concat_path))
                    total_duration = float(probe["format"]["duration"])
                    expected_duration = len(processed_videos) * 2.0  # ~2s each
                    assert abs(total_duration - expected_duration) < 1.0

                # Verify all processing completed
                assert len(processed_videos) == len(batch_filenames)
                assert len(thumbnails) == len(batch_filenames)

        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_error_handling(self, temp_dir, mcp_server):
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
                with pytest.raises((FileNotFoundError, RuntimeError)):
                    await client.read_resource("videos://nonexistent.mp4/metadata")

        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_consistency_workflow(
        self, sample_video, temp_dir, mcp_server
    ):
        """Test resource consistency with file operations.

        This test verifies that resource endpoints return consistent
        information with direct file operations and tool results.
        """
        # Copy sample video to temp directory
        test_video = temp_dir / "test_consistency.mp4"
        (
            ffmpeg.input(str(sample_video))
            .output(str(test_video), c="copy")
            .overwrite_output()
            .run(quiet=True)
        )

        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            async with Client(mcp_server) as client:
                # Get metadata via resource endpoint
                resource_result = await client.read_resource(
                    f"videos://{test_video.name}/metadata"
                )
                resource_metadata = json.loads(resource_result[0].text)

                # Get metadata via tool
                tool_result = await client.call_tool(
                    "get_video_info",
                    {"video_path": test_video.name},
                )
                tool_metadata = json.loads(tool_result[0].text)

                # Compare metadata consistency
                assert resource_metadata["filename"] == tool_metadata["filename"]
                assert (
                    abs(resource_metadata["duration"] - tool_metadata["duration"]) < 0.1
                )
                assert (
                    resource_metadata["video"]["width"]
                    == tool_metadata["video"]["width"]
                )
                assert (
                    resource_metadata["video"]["height"]
                    == tool_metadata["video"]["height"]
                )
                assert (
                    resource_metadata["video"]["codec"]
                    == tool_metadata["video"]["codec"]
                )

                # If audio exists, compare audio properties
                if "audio" in resource_metadata and "audio" in tool_metadata:
                    assert (
                        resource_metadata["audio"]["codec"]
                        == tool_metadata["audio"]["codec"]
                    )

                # Test video listing consistency
                list_result = await client.read_resource("videos://list")
                video_list = json.loads(list_result[0].text)

                assert test_video.name in video_list["videos"]

                # Perform video operation and verify metadata updates are consistent
                processed_video = temp_dir / "processed_consistency.mp4"
                process_result = await client.call_tool(
                    "resize_video",
                    {
                        "input_path": test_video.name,
                        "output_path": str(processed_video),
                        "scale": 0.75,
                    },
                )
                assert processed_video.exists()

                # Check that new file appears in listing
                updated_list_result = await client.read_resource("videos://list")
                updated_video_list = json.loads(updated_list_result[0].text)

                assert processed_video.name in updated_video_list["videos"]

                # Check processed video metadata
                processed_metadata_result = await client.read_resource(
                    f"videos://{processed_video.name}/metadata"
                )
                processed_metadata = json.loads(processed_metadata_result[0].text)

                # Verify dimensions changed correctly
                expected_width = int(resource_metadata["video"]["width"] * 0.75)
                expected_height = int(resource_metadata["video"]["height"] * 0.75)

                assert processed_metadata["video"]["width"] == expected_width
                assert processed_metadata["video"]["height"] == expected_height

        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_large_directory_resource_handling(self, temp_dir, mcp_server):
        """Test resource handling with many video files.

        This test verifies that resource endpoints can handle directories
        with many video files efficiently.
        """
        # Create many small video files
        video_count = 20
        created_videos = []

        for i in range(video_count):
            video_path = temp_dir / f"many_{i:03d}.mp4"
            duration = 1 + (i % 3)  # 1-3 second videos

            (
                ffmpeg.input(
                    f"testsrc=duration={duration}:size=320x240:rate=24",
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
            created_videos.append(video_path)

        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            async with Client(mcp_server) as client:
                # Test listing all videos
                list_result = await client.read_resource("videos://list")
                video_list = json.loads(list_result[0].text)

                # Should find all created videos
                many_videos = [v for v in video_list["videos"] if v.startswith("many_")]
                assert len(many_videos) == video_count

                # Test getting metadata for several videos
                metadata_samples = many_videos[:5]  # Test first 5

                for video_filename in metadata_samples:
                    metadata_result = await client.read_resource(
                        f"videos://{video_filename}/metadata"
                    )
                    metadata = json.loads(metadata_result[0].text)

                    assert "filename" in metadata
                    assert "duration" in metadata
                    assert "video" in metadata
                    assert metadata["video"]["width"] == 320
                    assert metadata["video"]["height"] == 240

                # Test batch processing a subset
                processing_subset = many_videos[::4]  # Every 4th video

                for video_filename in processing_subset:
                    thumb_path = (
                        temp_dir
                        / f"batch_thumb_{video_filename.replace('.mp4', '.jpg')}"
                    )
                    thumb_result = await client.call_tool(
                        "generate_thumbnail",
                        {
                            "input_path": video_filename,
                            "output_path": str(thumb_path),
                            "timestamp": 0.5,
                            "width": 80,
                            "height": 60,
                        },
                    )
                    assert thumb_path.exists()

        finally:
            os.chdir(original_cwd)
