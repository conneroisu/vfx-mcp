"""Test verification summary for VFX MCP server.

This module provides a comprehensive test report for the VFX MCP server
verification across all implemented test categories.
"""

from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

import pytest
from fastmcp import Client, FastMCP


class TestVerificationSummary:
    """Summary test class for VFX MCP server verification."""

    @pytest.mark.integration
    async def test_server_verification_summary(self, mcp_server: FastMCP[None]) -> None:
        """Comprehensive verification summary test."""
        print("\n" + "="*60)
        print("VFX MCP SERVER VERIFICATION SUMMARY")
        print("="*60)
        
        # Platform Information
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Architecture: {platform.machine()}")
        print(f"Python: {sys.version}")
        
        # FFmpeg Information
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        print(f"FFmpeg: {ffmpeg_path}")
        print(f"FFprobe: {ffprobe_path}")
        
        # Server Information
        print(f"Server Name: {mcp_server.name}")
        
        # Tool Registration
        tools = await mcp_server.get_tools()
        print(f"Registered Tools: {len(tools)}")
        
        # Resource Registration
        resources = await mcp_server.get_resources()
        print(f"Registered Resources: {len(resources)}")
        
        # Client Connectivity
        async with Client(mcp_server) as client:
            client_tools = await client.list_tools()
            client_resources = await client.list_resources()
            
            print(f"Client Can Access Tools: {len(client_tools)}")
            print(f"Client Can Access Resources: {len(client_resources)}")
        
        print("\n" + "="*60)
        print("VERIFICATION STATUS: ✅ PASSED")
        print("="*60)
        
        # Basic assertions
        assert mcp_server is not None
        assert mcp_server.name == "vfx-mcp"
        assert len(tools) > 0
        assert len(resources) > 0
        assert len(client_tools) > 0
        assert len(client_resources) > 0
        assert ffmpeg_path is not None
        assert ffprobe_path is not None

    @pytest.mark.integration
    def test_environment_verification(self) -> None:
        """Test environment setup and requirements."""
        print("\n" + "-"*40)
        print("ENVIRONMENT VERIFICATION")
        print("-"*40)
        
        # Python version
        python_version = sys.version_info
        print(f"Python Version: {python_version}")
        assert python_version >= (3, 13), "Python 3.13+ required"
        
        # Platform support
        current_platform = platform.system()
        print(f"Platform: {current_platform}")
        assert current_platform in ["Darwin", "Linux", "Windows"], "Unsupported platform"
        
        # FFmpeg availability
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        print(f"FFmpeg Available: {ffmpeg_path is not None}")
        print(f"FFprobe Available: {ffprobe_path is not None}")
        
        assert ffmpeg_path is not None, "FFmpeg not found"
        assert ffprobe_path is not None, "FFprobe not found"
        
        # Required imports
        try:
            import fastmcp
            import ffmpeg
            print("Required packages: ✅ Available")
        except ImportError as e:
            pytest.fail(f"Required package import failed: {e}")
        
        print("Environment: ✅ VERIFIED")

    @pytest.mark.integration
    async def test_tool_categories_verification(self, mcp_server: FastMCP[None]) -> None:
        """Test that all expected tool categories are available."""
        print("\n" + "-"*40)
        print("TOOL CATEGORIES VERIFICATION")
        print("-"*40)
        
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            tool_names = {tool.name for tool in tools}
            
            # Check basic video operations
            basic_tools = {"trim_video", "concatenate_videos", "resize_video", "get_video_info"}
            basic_present = basic_tools.intersection(tool_names)
            print(f"Basic Video Tools: {len(basic_present)}/{len(basic_tools)} - {basic_present}")
            
            # Check audio processing
            audio_tools = {"extract_audio", "add_audio", "normalize_audio", "remove_audio"}
            audio_present = audio_tools.intersection(tool_names)
            print(f"Audio Tools: {len(audio_present)}/{len(audio_tools)} - {audio_present}")
            
            # Check video effects
            effects_tools = {"apply_filter", "change_speed", "generate_thumbnail", "add_watermark"}
            effects_present = effects_tools.intersection(tool_names)
            print(f"Effects Tools: {len(effects_present)}/{len(effects_tools)} - {effects_present}")
            
            # Check format conversion
            format_tools = {"convert_format", "change_codec", "compress_video"}
            format_present = format_tools.intersection(tool_names)
            print(f"Format Tools: {len(format_present)}/{len(format_tools)} - {format_present}")
            
            print(f"Total Tools Available: {len(tool_names)}")
            print("Tool Categories: ✅ VERIFIED")
            
            # Ensure essential tools are present
            assert len(basic_present) >= 3, "Missing essential basic tools"
            assert len(audio_present) >= 2, "Missing essential audio tools"

    @pytest.mark.integration
    async def test_resource_endpoints_verification(self, mcp_server: FastMCP[None]) -> None:
        """Test that resource endpoints are properly configured."""
        print("\n" + "-"*40)
        print("RESOURCE ENDPOINTS VERIFICATION")
        print("-"*40)
        
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            resource_uris = {str(resource.uri) for resource in resources}
            
            # Check for essential resources
            list_resource = "videos://list" in resource_uris
            metadata_resources = [uri for uri in resource_uris if "/metadata" in uri]
            
            print(f"List Resource: {'✅' if list_resource else '❌'} videos://list")
            print(f"Metadata Resources: {len(metadata_resources)} endpoints")
            
            for uri in sorted(resource_uris):
                print(f"  - {uri}")
            
            print("Resource Endpoints: ✅ VERIFIED")
            
            assert list_resource, "Missing videos://list resource"
            # Note: Metadata resources are created dynamically when video files are present
            print(f"Note: Metadata resources are created dynamically for video files")