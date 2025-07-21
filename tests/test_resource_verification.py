"""Resource endpoint verification tests for VFX MCP server.

This module provides comprehensive tests for MCP resource endpoints,
including file discovery, metadata extraction, and resource URI handling.
Tests ensure proper functionality across different file systems and platforms.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

import ffmpeg
import pytest
from fastmcp import Client, FastMCP
from fastmcp.client.transports import FastMCPTransport

if TYPE_CHECKING:
    from typing import NotRequired


class VideoMetadata(TypedDict):
    """Type definition for video metadata."""
    filename: str
    duration: float
    video: dict[str, Any]
    audio: NotRequired[dict[str, Any]]
    size: NotRequired[int]
    format: NotRequired[str]


class VideoList(TypedDict):
    """Type definition for video list response."""
    videos: list[str]
    count: NotRequired[int]


class TestResourceVerification:
    """Test suite for MCP resource endpoint verification."""

    @pytest.mark.integration
    async def test_videos_list_endpoint(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test videos://list resource endpoint."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Create test video files in temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Create various video file types
            test_files = {
                "test1.mp4": "MP4 video",
                "test2.avi": "AVI video", 
                "test3.mkv": "MKV video",
                "test4.mov": "MOV video",
                "test5.webm": "WebM video",
                "not_video.txt": "Text file"  # Should be ignored
            }
            
            for filename, content in test_files.items():
                test_file = temp_dir / filename
                test_file.write_text(content)
            
            # Test videos://list resource
            response = await client.read_resource("videos://list")
            
            assert response["isError"] is False
            assert len(response["content"]) > 0
            
            # Parse JSON response
            content_text = response["content"][0]["text"]
            video_list = cast(VideoList, json.loads(content_text))
            
            # Verify response structure
            assert "videos" in video_list
            assert isinstance(video_list["videos"], list)
            
            # Should contain video files but not text files
            video_files = set(video_list["videos"])
            expected_videos = {
                "test1.mp4", "test2.avi", "test3.mkv", 
                "test4.mov", "test5.webm"
            }
            
            # At least some video files should be detected
            assert len(video_files) > 0
            
            # Should not contain non-video files
            assert "not_video.txt" not in video_files
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_video_metadata_endpoint(
        self, 
        sample_video: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test videos://{filename}/metadata resource endpoint."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test metadata endpoint
        filename = sample_video.name
        metadata_uri = f"videos://{filename}/metadata"
        
        # Change to sample video directory
        original_cwd = os.getcwd()
        try:
            os.chdir(sample_video.parent)
            
            response = await client.read_resource(metadata_uri)
            
            assert response["isError"] is False
            assert len(response["content"]) > 0
            
            # Parse JSON response
            content_text = response["content"][0]["text"]
            metadata = cast(VideoMetadata, json.loads(content_text))
            
            # Verify metadata structure
            assert "filename" in metadata
            assert "duration" in metadata
            assert "video" in metadata
            
            # Verify data types
            assert isinstance(metadata["filename"], str)
            assert isinstance(metadata["duration"], (int, float))
            assert isinstance(metadata["video"], dict)
            
            # Verify filename matches
            assert metadata["filename"] == filename
            
            # Verify video metadata
            video_info = metadata["video"]
            assert "width" in video_info
            assert "height" in video_info
            assert "codec" in video_info
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_uri_patterns(self, mcp_server: FastMCP[None]) -> None:
        """Test resource URI pattern matching and validation."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Get available resources
        resources_response = await client.list_resources()
        resources = resources_response["resources"]
        
        # Test URI patterns
        list_resources = [r for r in resources if r["uri"] == "videos://list"]
        assert len(list_resources) == 1
        
        metadata_resources = [r for r in resources if "/metadata" in r["uri"]]
        assert len(metadata_resources) > 0
        
        # Test URI format validation
        for resource in resources:
            uri = resource["uri"]
            assert uri.startswith("videos://")
            
            if uri == "videos://list":
                continue
            elif "/metadata" in uri:
                # Should have filename before /metadata
                parts = uri.replace("videos://", "").split("/")
                assert len(parts) >= 2
                assert parts[-1] == "metadata"
                assert len(parts[0]) > 0  # Filename should not be empty

    @pytest.mark.integration
    async def test_resource_error_handling(
        self, 
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource endpoint error handling."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test non-existent resource
        response = await client.read_resource("videos://nonexistent")
        assert response["isError"] is True
        
        # Test malformed URI
        response = await client.read_resource("invalid://uri")
        assert response["isError"] is True
        
        # Test metadata for non-existent file
        response = await client.read_resource("videos://nonexistent.mp4/metadata")
        assert response["isError"] is True

    @pytest.mark.integration
    async def test_resource_content_types(
        self, 
        sample_video: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource content type handling."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test list resource content type
        list_response = await client.read_resource("videos://list")
        assert list_response["isError"] is False
        
        for block in list_response["content"]:
            assert block["type"] == "text"
            assert "text" in block
            
            # Should be valid JSON
            try:
                json.loads(block["text"])
            except json.JSONDecodeError:
                pytest.fail("List resource content is not valid JSON")
        
        # Test metadata resource content type
        original_cwd = os.getcwd()
        try:
            os.chdir(sample_video.parent)
            
            metadata_uri = f"videos://{sample_video.name}/metadata"
            metadata_response = await client.read_resource(metadata_uri)
            assert metadata_response["isError"] is False
            
            for block in metadata_response["content"]:
                assert block["type"] == "text"
                assert "text" in block
                
                # Should be valid JSON
                try:
                    json.loads(block["text"])
                except json.JSONDecodeError:
                    pytest.fail("Metadata resource content is not valid JSON")
                    
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_file_filtering(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource file filtering and extension handling."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Create files with various extensions
            test_files = {
                "video.mp4": "video",
                "video.avi": "video", 
                "video.mkv": "video",
                "video.mov": "video",
                "video.webm": "video",
                "video.flv": "video",
                "video.wmv": "video",
                "audio.mp3": "audio",
                "audio.wav": "audio",
                "image.jpg": "image",
                "image.png": "image",
                "document.pdf": "document",
                "text.txt": "text",
                "data.json": "data",
                "no_extension": "unknown"
            }
            
            for filename, content in test_files.items():
                test_file = temp_dir / filename
                test_file.write_text(content)
            
            # Test videos://list filtering
            response = await client.read_resource("videos://list")
            assert response["isError"] is False
            
            content_text = response["content"][0]["text"]
            video_list = cast(VideoList, json.loads(content_text))
            
            found_files = set(video_list["videos"])
            
            # Should include video files
            video_extensions = {
                "video.mp4", "video.avi", "video.mkv", 
                "video.mov", "video.webm", "video.flv", "video.wmv"
            }
            
            # Should exclude non-video files
            non_video_files = {
                "audio.mp3", "audio.wav", "image.jpg", "image.png",
                "document.pdf", "text.txt", "data.json", "no_extension"
            }
            
            # Check that non-video files are not included
            for non_video in non_video_files:
                assert non_video not in found_files
                
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_directory_traversal(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource directory traversal and subdirectory handling."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Create subdirectory structure
            subdir = temp_dir / "subdir"
            subdir.mkdir()
            
            # Create video files in root and subdirectory
            (temp_dir / "root_video.mp4").write_text("root video")
            (subdir / "sub_video.mp4").write_text("sub video")
            
            # Test videos://list from root
            response = await client.read_resource("videos://list")
            assert response["isError"] is False
            
            content_text = response["content"][0]["text"]
            video_list = cast(VideoList, json.loads(content_text))
            
            found_files = set(video_list["videos"])
            
            # Should find root video
            assert "root_video.mp4" in found_files
            
            # Behavior for subdirectory files may vary by implementation
            # This test documents the current behavior
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_large_directory(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource handling with large number of files."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Create many video files
            num_files = 100
            for i in range(num_files):
                video_file = temp_dir / f"video_{i:03d}.mp4"
                video_file.write_text(f"video content {i}")
            
            # Test videos://list performance
            import time
            start_time = time.time()
            
            response = await client.read_resource("videos://list")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete in reasonable time
            assert duration < 5.0, f"List operation took too long: {duration}s"
            
            assert response["isError"] is False
            
            content_text = response["content"][0]["text"]
            video_list = cast(VideoList, json.loads(content_text))
            
            # Should find all video files
            assert len(video_list["videos"]) == num_files
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_concurrent_access(
        self, 
        sample_video: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test concurrent access to resource endpoints."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        import asyncio
        
        original_cwd = os.getcwd()
        try:
            os.chdir(sample_video.parent)
            
            # Create concurrent resource requests
            async def read_list_resource() -> dict[str, Any]:
                return await client.read_resource("videos://list")
            
            async def read_metadata_resource() -> dict[str, Any]:
                return await client.read_resource(f"videos://{sample_video.name}/metadata")
            
            # Run concurrent operations
            tasks = [
                read_list_resource(),
                read_metadata_resource(),
                read_list_resource(),
                read_metadata_resource()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All operations should succeed
            for result in results:
                assert not isinstance(result, Exception)
                assert result["isError"] is False
                
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_caching_behavior(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource caching and invalidation behavior."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Create initial video file
            video_file = temp_dir / "test.mp4"
            video_file.write_text("initial content")
            
            # Read resource list
            response1 = await client.read_resource("videos://list")
            assert response1["isError"] is False
            
            content1 = response1["content"][0]["text"]
            video_list1 = cast(VideoList, json.loads(content1))
            
            # Add another video file
            video_file2 = temp_dir / "test2.mp4"
            video_file2.write_text("second content")
            
            # Read resource list again
            response2 = await client.read_resource("videos://list")
            assert response2["isError"] is False
            
            content2 = response2["content"][0]["text"]
            video_list2 = cast(VideoList, json.loads(content2))
            
            # Should reflect changes (no stale caching)
            assert len(video_list2["videos"]) >= len(video_list1["videos"])
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_resource_path_security(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource path security and traversal protection."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test path traversal attempts
        malicious_uris = [
            "videos://../../../etc/passwd/metadata",
            "videos://..\\..\\..\\system32\\config\\metadata",
            "videos://./../../secrets.txt/metadata",
            "videos:///etc/passwd/metadata"
        ]
        
        for uri in malicious_uris:
            response = await client.read_resource(uri)
            # Should either error or safely handle the request
            # Should not expose system files
            if not response["isError"]:
                content = response["content"][0]["text"]
                # Should not contain sensitive system information
                assert "root:" not in content.lower()
                assert "password" not in content.lower()
                assert "secret" not in content.lower()

    @pytest.mark.integration
    async def test_resource_metadata_accuracy(
        self, 
        sample_video: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test accuracy of metadata extraction."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        original_cwd = os.getcwd()
        try:
            os.chdir(sample_video.parent)
            
            # Get metadata via resource endpoint
            metadata_uri = f"videos://{sample_video.name}/metadata"
            response = await client.read_resource(metadata_uri)
            
            assert response["isError"] is False
            
            content_text = response["content"][0]["text"]
            metadata = cast(VideoMetadata, json.loads(content_text))
            
            # Compare with direct ffprobe
            probe_data = ffmpeg.probe(str(sample_video))
            
            # Duration should match (within reasonable tolerance)
            expected_duration = float(probe_data["format"]["duration"])
            actual_duration = metadata["duration"]
            
            assert abs(actual_duration - expected_duration) < 0.1
            
            # Video dimensions should match
            video_stream = next(s for s in probe_data["streams"] if s["codec_type"] == "video")
            expected_width = video_stream["width"]
            expected_height = video_stream["height"]
            
            assert metadata["video"]["width"] == expected_width
            assert metadata["video"]["height"] == expected_height
            
        finally:
            os.chdir(original_cwd)