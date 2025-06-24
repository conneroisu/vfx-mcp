---
title: Troubleshooting
description: Common issues and solutions for the VFX MCP Server
---

# Troubleshooting

This guide covers common issues you might encounter while using the VFX MCP Server and provides step-by-step solutions to resolve them.

## 🚨 Installation Issues

### FFmpeg Not Found

**Symptoms**:
- Error: "FFmpeg not found in PATH"
- Tool calls fail with "ffmpeg command not found"

**Solutions**:

1. **Verify FFmpeg Installation**:
   ```bash
   # Check if FFmpeg is installed
   ffmpeg -version
   ffprobe -version
   
   # If not found, install FFmpeg
   # Ubuntu/Debian:
   sudo apt update && sudo apt install ffmpeg
   
   # macOS with Homebrew:
   brew install ffmpeg
   
   # Windows: Download from https://ffmpeg.org/download.html
   ```

2. **Set FFmpeg Path Manually**:
   ```bash
   # Add to your environment
   export FFMPEG_PATH=/usr/bin/ffmpeg
   export FFPROBE_PATH=/usr/bin/ffprobe
   
   # Or in Windows:
   set FFMPEG_PATH=C:\path\to\ffmpeg.exe
   set FFPROBE_PATH=C:\path\to\ffprobe.exe
   ```

3. **Using Nix Development Environment**:
   ```bash
   # Recommended approach - includes FFmpeg automatically
   nix develop
   # FFmpeg paths are set automatically
   ```

### Python Dependencies Issues

**Symptoms**:
- ImportError for required packages
- "Module not found" errors

**Solutions**:

1. **Reinstall Dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync --force-reinstall
   
   # Using pip
   pip install --force-reinstall -r requirements.txt
   ```

2. **Check Python Version**:
   ```bash
   # Verify Python 3.9+
   python --version
   
   # Use specific version if needed
   python3.9 -m pip install -r requirements.txt
   ```

3. **Virtual Environment Issues**:
   ```bash
   # Create fresh virtual environment
   python -m venv vfx_env
   source vfx_env/bin/activate  # Linux/macOS
   # or
   vfx_env\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   ```

---

## 🔌 MCP Connection Issues

### Server Won't Start

**Symptoms**:
- Server exits immediately
- "Connection refused" errors
- No response to MCP client connections

**Solutions**:

1. **Check Server Logs**:
   ```bash
   # Run server with debug logging
   export VFX_LOG_LEVEL=DEBUG
   uv run python main.py
   
   # Look for specific error messages
   ```

2. **Verify Working Directory**:
   ```bash
   # Ensure you're in the correct directory
   cd /path/to/vfx-mcp
   ls main.py  # Should exist
   
   # Check permissions
   ls -la main.py
   ```

3. **Port Conflicts** (for SSE transport):
   ```bash
   # Check if port is in use
   netstat -an | grep 8000
   
   # Use different port
   export MCP_PORT=8001
   ```

### Claude Desktop Connection Failed

**Symptoms**:
- Claude Desktop shows "Server failed to start"
- Tools not available in Claude Desktop

**Solutions**:

1. **Verify Configuration File**:
   ```json
   // ~/.config/claude/claude_desktop_config.json
   {
     "mcpServers": {
       "vfx-server": {
         "command": "uv",
         "args": ["run", "python", "main.py"],
         "cwd": "/absolute/path/to/vfx-mcp"
       }
     }
   }
   ```

2. **Check Absolute Paths**:
   ```bash
   # Use absolute paths, not relative
   pwd  # Get current directory
   # Use this full path in configuration
   ```

3. **Test Server Independently**:
   ```bash
   # Test server startup
   cd /path/to/vfx-mcp
   uv run python main.py
   # Should start without errors
   ```

4. **Restart Claude Desktop**:
   - Quit Claude Desktop completely
   - Wait 10 seconds
   - Restart Claude Desktop
   - Try again

---

## 🎬 Video Processing Issues

### Tool Execution Failures

**Symptoms**:
- "FFmpeg error" messages
- Tool calls timeout
- Corrupted output files

**Solutions**:

1. **Verify Input Files**:
   ```python
   # Check if input file exists and is accessible
   import os
   print(os.path.exists("input_video.mp4"))
   print(os.access("input_video.mp4", os.R_OK))
   
   # Check file format
   info = await session.call_tool("get_video_info", {
       "video_path": "input_video.mp4"
   })
   print(info)
   ```

2. **Check Disk Space**:
   ```bash
   # Verify sufficient disk space
   df -h .
   
   # Clean up temporary files
   rm -f temp_*.mp4
   ```

3. **File Permissions**:
   ```bash
   # Fix file permissions
   chmod 644 input_video.mp4
   chmod 755 output_directory/
   ```

### Codec and Format Issues

**Symptoms**:
- "Unsupported codec" errors
- Format conversion failures
- Audio/video sync issues

**Solutions**:

1. **Check Supported Formats**:
   ```python
   # Get server capabilities
   capabilities = await session.read_resource("tools://capabilities")
   print("Supported input formats:", capabilities['format_support']['input_formats'])
   print("Supported output formats:", capabilities['format_support']['output_formats'])
   ```

2. **Convert Problematic Files**:
   ```bash
   # Convert to standard format first
   ffmpeg -i problematic_video.avi -c:v libx264 -c:a aac standard_video.mp4
   ```

3. **Use Format Conversion Tool**:
   ```python
   # Convert using VFX MCP Server
   await session.call_tool("convert_format", {
       "input_path": "input.avi",
       "output_path": "output.mp4",
       "video_codec": "libx264",
       "audio_codec": "aac"
   })
   ```

### Performance Issues

**Symptoms**:
- Slow processing
- High CPU/memory usage
- Operations timing out

**Solutions**:

1. **Optimize Quality Settings**:
   ```python
   # Use lower quality for faster processing
   await session.call_tool("resize_video", {
       "input_path": "large_video.mp4",
       "output_path": "resized.mp4",
       "width": 1280,
       "height": 720,
       "quality": "medium"  # Instead of "ultra"
   })
   ```

2. **Process in Smaller Chunks**:
   ```python
   # Split large videos into smaller segments
   duration = 600  # 10 minutes
   for i in range(0, int(total_duration), duration):
       await session.call_tool("trim_video", {
           "input_path": "large_video.mp4",
           "output_path": f"chunk_{i}.mp4",
           "start_time": i,
           "duration": duration
       })
   ```

3. **Monitor System Resources**:
   ```python
   # Check server capabilities
   capabilities = await session.read_resource("tools://capabilities")
   resources = capabilities['system_resources']
   
   if resources['cpu_usage'] > 80:
       print("High CPU usage - consider reducing concurrent operations")
   if resources['memory_usage'] > 90:
       print("High memory usage - restart server if needed")
   ```

---

## 📁 File and Path Issues

### File Not Found Errors

**Symptoms**:
- "No such file or directory"
- Path resolution failures

**Solutions**:

1. **Use Absolute Paths**:
   ```python
   # Instead of relative paths
   import os
   absolute_path = os.path.abspath("relative_video.mp4")
   
   await session.call_tool("trim_video", {
       "input_path": absolute_path,
       "output_path": os.path.abspath("output.mp4"),
       "start_time": 0,
       "duration": 30
   })
   ```

2. **Check Working Directory**:
   ```bash
   # Verify current working directory
   pwd
   ls *.mp4  # List video files
   
   # Or set working directory
   export VFX_WORK_DIR=/path/to/videos
   ```

3. **List Available Files**:
   ```python
   # Use resource endpoint to see available files
   video_list = await session.read_resource("videos://list")
   print("Available videos:")
   for video in video_list['videos']:
       print(f"- {video['name']}")
   ```

### Output Directory Issues

**Symptoms**:
- "Permission denied" when writing output
- Output files not created

**Solutions**:

1. **Create Output Directory**:
   ```bash
   # Ensure output directory exists
   mkdir -p output_videos
   chmod 755 output_videos
   ```

2. **Check Write Permissions**:
   ```bash
   # Test write permissions
   touch test_output.txt
   rm test_output.txt  # Should work without errors
   ```

3. **Use Temporary Directory**:
   ```python
   import tempfile
   import os
   
   # Use system temporary directory
   temp_dir = tempfile.gettempdir()
   output_path = os.path.join(temp_dir, "output.mp4")
   ```

---

## 🔧 Configuration Issues

### Environment Variables

**Symptoms**:
- Server uses wrong settings
- Paths not resolved correctly

**Solutions**:

1. **Check Environment Variables**:
   ```bash
   # List VFX-related environment variables
   env | grep VFX
   env | grep MCP
   env | grep FFMPEG
   ```

2. **Set Required Variables**:
   ```bash
   # Set essential environment variables
   export VFX_WORK_DIR=/path/to/videos
   export MCP_TRANSPORT=stdio
   export VFX_LOG_LEVEL=INFO
   ```

3. **Create Environment File**:
   ```bash
   # Create .env file in project directory
   cat > .env << EOF
   VFX_WORK_DIR=/path/to/videos
   MCP_TRANSPORT=stdio
   FFMPEG_PATH=/usr/bin/ffmpeg
   FFPROBE_PATH=/usr/bin/ffprobe
   EOF
   ```

### Server Configuration

**Symptoms**:
- Wrong transport mode
- Server binding to wrong address/port

**Solutions**:

1. **Verify Transport Configuration**:
   ```python
   # Check current transport mode
   import os
   transport = os.getenv('MCP_TRANSPORT', 'stdio')
   print(f"Transport mode: {transport}")
   
   # For Claude Desktop, use stdio
   os.environ['MCP_TRANSPORT'] = 'stdio'
   
   # For web applications, use sse
   os.environ['MCP_TRANSPORT'] = 'sse'
   os.environ['MCP_HOST'] = 'localhost'
   os.environ['MCP_PORT'] = '8000'
   ```

---

## 🧪 Testing and Debugging

### Enable Debug Mode

```bash
# Enable comprehensive logging
export VFX_LOG_LEVEL=DEBUG
uv run python main.py 2>&1 | tee debug.log
```

### Test Individual Tools

```python
# Test basic connectivity
async def test_basic_functionality():
    try:
        # Test video info tool
        info = await session.call_tool("get_video_info", {
            "video_path": "test_video.mp4"
        })
        print("✅ get_video_info works")
        
        # Test simple trim
        result = await session.call_tool("trim_video", {
            "input_path": "test_video.mp4",
            "output_path": "test_output.mp4",
            "start_time": 0,
            "duration": 5
        })
        print("✅ trim_video works")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
```

### System Information

```python
# Gather system information for debugging
async def collect_debug_info():
    import platform
    import sys
    
    print("System Information:")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    
    # Server capabilities
    try:
        capabilities = await session.read_resource("tools://capabilities")
        print(f"Server version: {capabilities['server_info']['version']}")
        print(f"FFmpeg version: {capabilities['ffmpeg_info']['version']}")
        print(f"Available encoders: {capabilities['ffmpeg_info']['encoders']}")
    except Exception as e:
        print(f"Could not get server capabilities: {e}")
```

## 🆘 Getting Help

### Before Seeking Help

1. **Check this troubleshooting guide**
2. **Review the [FAQ](/support/faq/)**
3. **Enable debug logging** and capture the output
4. **Test with a simple video file** to isolate the issue

### Reporting Issues

When reporting issues, please include:

1. **System Information**:
   - Operating system and version
   - Python version
   - FFmpeg version
   - VFX MCP Server version

2. **Error Details**:
   - Full error message
   - Debug logs
   - Steps to reproduce

3. **Configuration**:
   - Environment variables
   - MCP client configuration
   - Working directory structure

### Community Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/conneroisu/vfx-mcp/issues)
- **FAQ**: Check [common questions](/support/faq/)
- **Performance Guide**: See [optimization tips](/support/performance/)

---

## 🔄 Recovery Procedures

### Clean Installation

If all else fails, perform a clean installation:

```bash
# 1. Remove existing installation
rm -rf vfx-mcp/

# 2. Fresh clone
git clone https://github.com/conneroisu/vfx-mcp.git
cd vfx-mcp

# 3. Clean Python environment
python -m venv fresh_env
source fresh_env/bin/activate

# 4. Install dependencies
uv sync

# 5. Test installation
uv run python main.py
```

### Reset Configuration

```bash
# Remove configuration files
rm -f ~/.config/claude/claude_desktop_config.json
rm -f .env

# Recreate with minimal configuration
mkdir -p ~/.config/claude
cat > ~/.config/claude/claude_desktop_config.json << EOF
{
  "mcpServers": {
    "vfx-server": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "$(pwd)"
    }
  }
}
EOF
```

---

**Still having issues?** Check our [FAQ](/support/faq/) or [file an issue](https://github.com/conneroisu/vfx-mcp/issues) with detailed information about your problem.