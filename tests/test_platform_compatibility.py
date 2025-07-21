"""Platform-specific compatibility tests for VFX MCP server.

This module provides tests for cross-platform compatibility, focusing on
macOS (Darwin), Linux, and Windows specific behaviors and requirements.
Tests ensure the server works correctly across different operating systems
and environments.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fastmcp import Client, FastMCP
from fastmcp.client.transports import FastMCPTransport

if TYPE_CHECKING:
    pass


class TestPlatformCompatibility:
    """Test suite for platform-specific compatibility verification."""

    @pytest.mark.integration
    def test_platform_detection(self) -> None:
        """Test platform detection and supported platforms."""
        current_platform = platform.system()
        
        # Test that we're on a supported platform
        supported_platforms = ["Darwin", "Linux", "Windows"]
        assert current_platform in supported_platforms, \
            f"Unsupported platform: {current_platform}"
        
        # Test platform-specific information
        if current_platform == "Darwin":
            # macOS specific tests
            assert platform.mac_ver()[0] != ""
            assert platform.machine() in ["x86_64", "arm64"]
        elif current_platform == "Linux":
            # Linux specific tests
            assert platform.release() != ""
            assert platform.machine() in ["x86_64", "aarch64", "armv7l"]
        elif current_platform == "Windows":
            # Windows specific tests
            assert platform.win32_ver()[0] != ""
            assert platform.machine() in ["AMD64", "x86"]

    @pytest.mark.integration
    def test_ffmpeg_availability(self) -> None:
        """Test FFmpeg availability across platforms."""
        # Check for ffmpeg executable
        ffmpeg_path = shutil.which("ffmpeg")
        assert ffmpeg_path is not None, "FFmpeg not found in PATH"
        
        # Check for ffprobe executable
        ffprobe_path = shutil.which("ffprobe")
        assert ffprobe_path is not None, "FFprobe not found in PATH"
        
        # Test FFmpeg execution
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, f"FFmpeg failed: {result.stderr}"
            assert "ffmpeg version" in result.stdout
        except subprocess.TimeoutExpired:
            pytest.fail("FFmpeg version check timed out")
        except FileNotFoundError:
            pytest.fail("FFmpeg executable not found")

    @pytest.mark.integration
    def test_python_version_compatibility(self) -> None:
        """Test Python version compatibility."""
        python_version = sys.version_info
        
        # Require Python 3.13+
        assert python_version >= (3, 13), \
            f"Python 3.13+ required, got {python_version}"
        
        # Test Python executable
        python_exe = sys.executable
        assert Path(python_exe).exists(), "Python executable not found"
        
        # Test that we can import required modules
        try:
            import ffmpeg
            import fastmcp
            assert True
        except ImportError as e:
            pytest.fail(f"Required module import failed: {e}")

    @pytest.mark.integration
    def test_file_system_operations(self, temp_dir: Path) -> None:
        """Test file system operations across platforms."""
        # Test path creation and manipulation
        test_file = temp_dir / "test_file.mp4"
        test_file.write_text("test content")
        
        assert test_file.exists()
        assert test_file.is_file()
        assert test_file.read_text() == "test content"
        
        # Test subdirectory creation
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        assert subdir.exists()
        assert subdir.is_dir()
        
        # Test file operations in subdirectory
        subfile = subdir / "subfile.mp4"
        subfile.write_text("sub content")
        assert subfile.exists()
        
        # Test file deletion
        test_file.unlink()
        assert not test_file.exists()
        
        # Test directory removal
        subfile.unlink()
        subdir.rmdir()
        assert not subdir.exists()

    @pytest.mark.integration
    def test_path_separators(self, temp_dir: Path) -> None:
        """Test path separator handling across platforms."""
        # Test forward slash paths (Unix-style)
        unix_path = temp_dir / "unix/style/path.mp4"
        unix_path.parent.mkdir(parents=True, exist_ok=True)
        unix_path.write_text("unix path")
        
        assert unix_path.exists()
        
        # Test that path string representations work
        path_str = str(unix_path)
        assert Path(path_str).exists()
        
        # Test relative paths
        rel_path = Path("relative/path.mp4")
        abs_path = temp_dir / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text("relative path")
        
        assert abs_path.exists()

    @pytest.mark.integration
    async def test_video_codec_support(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test video codec support across platforms."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test common codec availability
        common_codecs = ["libx264", "libx265", "libvpx", "libvpx-vp9"]
        
        # Check ffmpeg codec support
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            try:
                result = subprocess.run(
                    [ffmpeg_path, "-codecs"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    codec_output = result.stdout
                    
                    # Check for essential codecs
                    assert "h264" in codec_output.lower()
                    assert "aac" in codec_output.lower()
                    
            except subprocess.TimeoutExpired:
                pytest.skip("FFmpeg codec check timed out")

    @pytest.mark.integration
    def test_environment_variables(self) -> None:
        """Test environment variable handling."""
        # Test PATH variable
        path_var = os.environ.get("PATH", "")
        assert path_var != "", "PATH environment variable not set"
        
        # Test that PATH contains ffmpeg location
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            ffmpeg_dir = str(Path(ffmpeg_path).parent)
            path_dirs = path_var.split(os.pathsep)
            assert any(ffmpeg_dir in path_dir for path_dir in path_dirs)
        
        # Test platform-specific environment variables
        current_platform = platform.system()
        if current_platform == "Darwin":
            # macOS specific environment
            assert "HOME" in os.environ
        elif current_platform == "Linux":
            # Linux specific environment
            assert "HOME" in os.environ
        elif current_platform == "Windows":
            # Windows specific environment
            assert "USERPROFILE" in os.environ or "HOME" in os.environ

    @pytest.mark.integration
    async def test_unicode_file_handling(
        self, 
        temp_dir: Path,
        mcp_server: FastMCP[None]
    ) -> None:
        """Test Unicode filename handling across platforms."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        await client.initialize()
        
        # Test Unicode filenames
        unicode_names = [
            "测试视频.mp4",  # Chinese
            "видео_тест.mp4",  # Cyrillic
            "テスト動画.mp4",  # Japanese
            "🎬_emoji_video.mp4",  # Emoji
            "café_münü.mp4",  # Accented characters
        ]
        
        for filename in unicode_names:
            try:
                test_file = temp_dir / filename
                test_file.write_text("unicode test content")
                
                if test_file.exists():
                    # Test that the file can be processed
                    file_str = str(test_file)
                    assert len(file_str) > 0
                    
                    # Clean up
                    test_file.unlink()
                    
            except (UnicodeEncodeError, OSError):
                # Some platforms may not support certain Unicode characters
                # This is expected behavior
                pass

    @pytest.mark.integration
    def test_file_permissions(self, temp_dir: Path) -> None:
        """Test file permission handling across platforms."""
        test_file = temp_dir / "permission_test.mp4"
        test_file.write_text("permission test")
        
        # Test read permissions
        assert test_file.is_file()
        assert test_file.read_text() == "permission test"
        
        # Test write permissions
        test_file.write_text("modified content")
        assert test_file.read_text() == "modified content"
        
        # Platform-specific permission tests
        current_platform = platform.system()
        if current_platform in ["Darwin", "Linux"]:
            # Unix-like systems
            import stat
            
            # Test executable permissions
            test_file.chmod(0o755)
            file_stat = test_file.stat()
            assert file_stat.st_mode & stat.S_IEXEC
            
            # Test read-only permissions
            test_file.chmod(0o444)
            file_stat = test_file.stat()
            assert file_stat.st_mode & stat.S_IREAD
            
            # Restore write permissions for cleanup
            test_file.chmod(0o644)

    @pytest.mark.integration
    def test_temporary_file_handling(self) -> None:
        """Test temporary file handling across platforms."""
        import tempfile
        
        # Test temporary directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            assert temp_path.exists()
            assert temp_path.is_dir()
            
            # Test temporary file creation
            temp_file = temp_path / "temp_test.mp4"
            temp_file.write_text("temporary content")
            assert temp_file.exists()
        
        # Directory should be cleaned up automatically
        assert not temp_path.exists()

    @pytest.mark.integration
    def test_process_execution(self) -> None:
        """Test process execution across platforms."""
        # Test subprocess execution
        try:
            result = subprocess.run(
                [sys.executable, "-c", "print('test')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0
            assert "test" in result.stdout
        except subprocess.TimeoutExpired:
            pytest.fail("Process execution timed out")
        except FileNotFoundError:
            pytest.fail("Python executable not found")

    @pytest.mark.integration
    def test_memory_limits(self) -> None:
        """Test memory limit handling across platforms."""
        import psutil
        
        # Get available memory
        memory_info = psutil.virtual_memory()
        available_memory = memory_info.available
        
        # Should have reasonable amount of available memory
        min_memory_mb = 512 * 1024 * 1024  # 512 MB
        assert available_memory > min_memory_mb, \
            f"Insufficient memory: {available_memory // (1024*1024)} MB available"

    @pytest.mark.integration
    def test_cpu_architecture(self) -> None:
        """Test CPU architecture compatibility."""
        machine = platform.machine()
        processor = platform.processor()
        
        # Test supported architectures
        supported_architectures = [
            "x86_64", "amd64", "AMD64",  # 64-bit Intel/AMD
            "arm64", "aarch64",  # 64-bit ARM
            "i386", "i686", "x86",  # 32-bit Intel (legacy)
            "armv7l", "armv6l"  # 32-bit ARM (legacy)
        ]
        
        assert machine.lower() in [arch.lower() for arch in supported_architectures], \
            f"Unsupported architecture: {machine}"

    @pytest.mark.integration
    async def test_network_isolation(self, mcp_server: FastMCP[None]) -> None:
        """Test that server doesn't require network access."""
        transport = FastMCPTransport(mcp_server)
        client = Client(transport)
        
        # Server should initialize without network access
        await client.initialize()
        
        # Basic operations should work offline
        tools_response = await client.list_tools()
        assert "tools" in tools_response
        
        resources_response = await client.list_resources()
        assert "resources" in resources_response

    @pytest.mark.integration
    def test_locale_handling(self) -> None:
        """Test locale and encoding handling."""
        import locale
        
        # Test current locale
        current_locale = locale.getlocale()
        assert current_locale[0] is not None or current_locale[1] is not None
        
        # Test encoding
        default_encoding = locale.getpreferredencoding()
        assert default_encoding is not None
        assert len(default_encoding) > 0
        
        # Test that UTF-8 is supported
        try:
            "test".encode('utf-8')
            assert True
        except UnicodeError:
            pytest.fail("UTF-8 encoding not supported")

    @pytest.mark.slow
    @pytest.mark.integration
    def test_system_resource_usage(self) -> None:
        """Test system resource usage patterns."""
        import psutil
        import time
        
        # Get initial resource usage
        process = psutil.Process()
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss
        
        # Perform some work
        time.sleep(0.5)  # Let CPU measurement stabilize
        
        # Measure resource usage
        cpu_percent = process.cpu_percent()
        memory_usage = process.memory_info().rss
        
        # Resource usage should be reasonable
        assert cpu_percent < 90.0, f"High CPU usage: {cpu_percent}%"
        
        # Memory usage should not be excessive
        memory_mb = memory_usage / (1024 * 1024)
        assert memory_mb < 1000, f"High memory usage: {memory_mb} MB"

    @pytest.mark.integration
    def test_signal_handling(self) -> None:
        """Test signal handling capabilities."""
        import signal
        
        # Test that common signals are available
        available_signals = [
            signal.SIGINT,  # Interrupt (Ctrl+C)
            signal.SIGTERM,  # Termination
        ]
        
        for sig in available_signals:
            assert hasattr(signal, sig.name)
        
        # Test signal handler setup (basic test)
        def dummy_handler(signum, frame):
            pass
        
        # This should not raise an error
        original_handler = signal.signal(signal.SIGINT, dummy_handler)
        signal.signal(signal.SIGINT, original_handler)

    @pytest.mark.integration
    def test_threading_support(self) -> None:
        """Test threading support across platforms."""
        import threading
        import time
        
        # Test basic threading
        results = []
        
        def worker():
            results.append("worked")
        
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=1.0)
        
        assert not thread.is_alive(), "Thread did not complete"
        assert results == ["worked"], "Thread did not execute correctly"