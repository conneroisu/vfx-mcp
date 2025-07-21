"""Comprehensive server verification tests for VFX MCP.

This module provides end-to-end verification tests for the entire VFX MCP server,
ensuring all components work correctly together on this platform. Tests cover
MCP protocol compliance, tool registration, resource endpoints, and cross-platform
compatibility.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

import ffmpeg
import pytest
from fastmcp import Client, FastMCP
from fastmcp.client.transports import FastMCPTransport

if TYPE_CHECKING:
    from typing import NotRequired


class ToolInfo(TypedDict):
    """Type definition for MCP tool information."""
    name: str
    description: str
    inputSchema: dict[str, Any]


class ResourceInfo(TypedDict):
    """Type definition for MCP resource information."""
    uri: str
    name: str
    description: str
    mimeType: NotRequired[str]


class ServerCapabilities(TypedDict):
    """Type definition for MCP server capabilities."""
    tools: dict[str, Any]
    resources: dict[str, Any]
    prompts: dict[str, Any]


class TestServerVerification:
    """Comprehensive verification tests for the VFX MCP server."""

    @pytest.mark.integration
    async def test_server_initialization(self, mcp_server: FastMCP[None]) -> None:
        """Test that the server initializes correctly with all components."""
        assert mcp_server is not None
        assert mcp_server.name == "vfx-mcp"
        
        # Test that server has tools registered
        tools = await mcp_server.get_tools()
        assert len(tools) > 0, "Server should have tools registered"
        
        # Test that server has resources registered
        resources = await mcp_server.get_resources()
        assert len(resources) > 0, "Server should have resources registered"

    @pytest.mark.integration
    async def test_mcp_protocol_compliance(self, mcp_server: FastMCP[None]) -> None:
        """Test MCP protocol compliance and capabilities."""
        # Test using the client context manager
        async with Client(mcp_server) as client:
            # Test list_tools request
            tools = await client.list_tools()
            assert len(tools) > 0
            
            # Verify tool structure
            for tool in tools:
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'input_schema')
                assert isinstance(tool.input_schema, dict)
            
            # Test list_resources request  
            resources = await client.list_resources()
            assert len(resources) > 0
            
            # Verify resource structure
            for resource in resources:
                assert hasattr(resource, 'uri')
                assert hasattr(resource, 'name')
                assert hasattr(resource, 'description')

    @pytest.mark.integration
    async def test_all_tools_registered(self, mcp_server: FastMCP[None]) -> None:
        """Test that all expected video editing tools are registered."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        tools_response = await client.list_tools()
        tools = cast(list[ToolInfo], tools_response["tools"])
        tool_names = {tool["name"] for tool in tools}
        
        # Basic video operations
        expected_basic_tools = {
            "trim_video", "concatenate_videos", "resize_video", "get_video_info"
        }
        
        # Audio processing tools
        expected_audio_tools = {
            "extract_audio", "add_audio", "normalize_audio", "remove_audio"
        }
        
        # Video effects tools
        expected_effects_tools = {
            "apply_filter", "change_speed", "generate_thumbnail", "add_watermark"
        }
        
        # Format conversion tools
        expected_format_tools = {
            "convert_format", "change_codec", "compress_video"
        }
        
        # Check that essential tools are present
        missing_basic = expected_basic_tools - tool_names
        assert not missing_basic, f"Missing basic tools: {missing_basic}"
        
        missing_audio = expected_audio_tools - tool_names
        assert not missing_audio, f"Missing audio tools: {missing_audio}"
        
        # At least some effects and format tools should be present
        assert any(tool in tool_names for tool in expected_effects_tools), \
            "No video effects tools found"
        assert any(tool in tool_names for tool in expected_format_tools), \
            "No format conversion tools found"

    @pytest.mark.integration
    async def test_resource_endpoints(self, mcp_server: FastMCP[None]) -> None:
        """Test that MCP resource endpoints are properly registered."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test list_resources
        resources_response = await client.list_resources()
        resources = cast(list[ResourceInfo], resources_response["resources"])
        resource_uris = {resource["uri"] for resource in resources}
        
        # Check for expected resource endpoints
        assert "videos://list" in resource_uris
        assert any(uri.startswith("videos://") and uri.endswith("/metadata") 
                  for uri in resource_uris)

    @pytest.mark.integration
    async def test_platform_compatibility(self, mcp_server: FastMCP[None]) -> None:
        """Test platform-specific compatibility and requirements."""
        # Test platform detection
        current_platform = platform.system()
        assert current_platform in ["Darwin", "Linux", "Windows"]
        
        # Test FFmpeg availability
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        
        assert ffmpeg_path is not None, "FFmpeg not found in PATH"
        assert ffprobe_path is not None, "FFprobe not found in PATH"
        
        # Test FFmpeg version compatibility
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            assert result.returncode == 0, "FFmpeg version check failed"
            assert "ffmpeg version" in result.stdout.lower()
        except subprocess.TimeoutExpired:
            pytest.fail("FFmpeg version check timed out")
        
        # Test Python version compatibility
        python_version = sys.version_info
        assert python_version >= (3, 13), f"Python 3.13+ required, got {python_version}"

    @pytest.mark.integration
    async def test_end_to_end_workflow(
        self, 
        sample_video: Path, 
        sample_audio: Path, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test complete end-to-end video editing workflow."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test basic video info
        info_response = await client.call_tool(
            "get_video_info",
            {"video_path": str(sample_video)}
        )
        assert info_response["isError"] is False
        video_info = json.loads(info_response["content"][0]["text"])
        assert "duration" in video_info
        assert "width" in video_info
        assert "height" in video_info
        
        # Test video trimming
        trimmed_output = temp_dir / "trimmed.mp4"
        trim_response = await client.call_tool(
            "trim_video",
            {
                "input_path": str(sample_video),
                "output_path": str(trimmed_output),
                "start_time": "0",
                "duration": "2"
            }
        )
        assert trim_response["isError"] is False
        assert trimmed_output.exists()
        
        # Test audio extraction
        audio_output = temp_dir / "extracted_audio.mp3"
        audio_response = await client.call_tool(
            "extract_audio",
            {
                "input_path": str(sample_video),
                "output_path": str(audio_output)
            }
        )
        assert audio_response["isError"] is False
        assert audio_output.exists()
        
        # Test format conversion
        converted_output = temp_dir / "converted.avi"
        convert_response = await client.call_tool(
            "convert_format",
            {
                "input_path": str(sample_video),
                "output_path": str(converted_output),
                "output_format": "avi"
            }
        )
        assert convert_response["isError"] is False
        assert converted_output.exists()
        
        # Test thumbnail generation
        thumbnail_output = temp_dir / "thumbnail.jpg"
        thumb_response = await client.call_tool(
            "generate_thumbnail",
            {
                "input_path": str(sample_video),
                "output_path": str(thumbnail_output),
                "timestamp": "1.0"
            }
        )
        assert thumb_response["isError"] is False
        assert thumbnail_output.exists()

    @pytest.mark.integration
    async def test_error_handling(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test error handling for invalid inputs and edge cases."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test with non-existent input file
        nonexistent_file = temp_dir / "nonexistent.mp4"
        response = await client.call_tool(
            "get_video_info",
            {"video_path": str(nonexistent_file)}
        )
        assert response["isError"] is True
        
        # Test with invalid output path
        invalid_output = Path("/invalid/path/output.mp4")
        response = await client.call_tool(
            "trim_video",
            {
                "input_path": str(nonexistent_file),
                "output_path": str(invalid_output),
                "start_time": "0",
                "duration": "2"
            }
        )
        assert response["isError"] is True
        
        # Test with invalid parameters
        response = await client.call_tool(
            "trim_video",
            {
                "input_path": str(nonexistent_file),
                "output_path": str(temp_dir / "output.mp4"),
                "start_time": "invalid",
                "duration": "2"
            }
        )
        assert response["isError"] is True

    @pytest.mark.slow
    @pytest.mark.integration
    async def test_performance_benchmarks(
        self, 
        sample_video: Path, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test performance benchmarks for common operations."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        import time
        
        # Benchmark video info retrieval
        start_time = time.time()
        info_response = await client.call_tool(
            "get_video_info",
            {"video_path": str(sample_video)}
        )
        info_time = time.time() - start_time
        
        assert info_response["isError"] is False
        assert info_time < 5.0, f"Video info took too long: {info_time}s"
        
        # Benchmark thumbnail generation
        start_time = time.time()
        thumb_response = await client.call_tool(
            "generate_thumbnail",
            {
                "input_path": str(sample_video),
                "output_path": str(temp_dir / "bench_thumb.jpg"),
                "timestamp": "1.0"
            }
        )
        thumb_time = time.time() - start_time
        
        assert thumb_response["isError"] is False
        assert thumb_time < 10.0, f"Thumbnail generation took too long: {thumb_time}s"

    @pytest.mark.integration
    async def test_resource_file_discovery(
        self, 
        sample_video: Path, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test resource endpoints for file discovery."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Change to temp directory for resource discovery
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Create some test video files
            test_files = ["test1.mp4", "test2.avi", "test3.mkv"]
            for filename in test_files:
                # Create dummy video files
                dummy_file = temp_dir / filename
                dummy_file.write_text("dummy video content")
            
            # Test videos://list resource
            list_response = await client.read_resource("videos://list")
            assert list_response["isError"] is False
            
            # The response should contain video file information
            content = list_response["content"][0]["text"]
            assert isinstance(content, str)
            # Content should be JSON with video file list
            try:
                video_list = json.loads(content)
                assert isinstance(video_list, dict)
                assert "videos" in video_list
            except json.JSONDecodeError:
                pytest.fail("Resource response is not valid JSON")
                
        finally:
            os.chdir(original_cwd)

    @pytest.mark.integration
    async def test_concurrent_operations(
        self, 
        sample_videos: list[Path], 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test concurrent video operations."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        import asyncio
        
        # Create multiple concurrent operations
        async def process_video(video_path: Path, index: int) -> bool:
            output_path = temp_dir / f"concurrent_output_{index}.mp4"
            response = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(video_path),
                    "output_path": str(output_path),
                    "start_time": "0",
                    "duration": "1"
                }
            )
            return response["isError"] is False and output_path.exists()
        
        # Run concurrent operations
        tasks = [
            process_video(video, i) 
            for i, video in enumerate(sample_videos)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that all operations completed successfully
        success_count = sum(1 for result in results if result is True)
        assert success_count == len(sample_videos), \
            f"Only {success_count}/{len(sample_videos)} concurrent operations succeeded"

    @pytest.mark.integration  
    async def test_memory_usage(
        self, 
        sample_video: Path, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test memory usage during video operations."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        import gc
        import sys
        
        # Get initial memory usage
        initial_objects = len(gc.get_objects())
        
        # Perform multiple operations
        for i in range(5):
            output_path = temp_dir / f"memory_test_{i}.mp4"
            response = await client.call_tool(
                "trim_video",
                {
                    "input_path": str(sample_video),
                    "output_path": str(output_path),
                    "start_time": "0",
                    "duration": "1"
                }
            )
            assert response["isError"] is False
            
            # Force garbage collection
            gc.collect()
        
        # Check final memory usage
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Memory usage should not increase dramatically
        assert object_increase < 1000, \
            f"Memory usage increased by {object_increase} objects"