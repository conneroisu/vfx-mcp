---
title: Quick Start
description: Get started with the VFX MCP Server in minutes
---

Get up and running with the VFX MCP Server and start editing videos with AI assistance in just a few minutes.

## 🎬 Your First Video Edit

Let's walk through a complete example of starting the server and performing basic video operations.

### 1. Start the Server

```bash
# Navigate to the project directory
cd vfx-mcp

# Start the MCP server
uv run python main.py
```

The server will start and wait for MCP client connections. You should see output like:

```
FastMCP Server starting...
Server ready for MCP connections on stdio transport
Waiting for client connections...
```

### 2. Test with Sample Videos

First, let's create some test content:

```bash
# Create a test directory
mkdir test_videos
cd test_videos

# Generate a sample video (if you have FFmpeg available directly)
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 \
       -f lavfi -i sine=frequency=1000:duration=10 \
       -c:v libx264 -c:a aac sample_input.mp4
```

### 3. Connect with an MCP Client

The server is designed to work with MCP clients. Here are a few ways to interact with it:

#### Option A: Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "vfx-server": {
      "command": "uv",
      "args": ["run", "python", "/path/to/vfx-mcp/main.py"],
      "cwd": "/path/to/vfx-mcp"
    }
  }
}
```

#### Option B: Direct MCP Client

```python
# example_client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "main.py"],
        cwd="/path/to/vfx-mcp"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")
            
            # Get video info
            result = await session.call_tool(
                "get_video_info",
                {"video_path": "test_videos/sample_input.mp4"}
            )
            print(f"Video info: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🛠️ Common First Tasks

### Get Video Information

```python
# Through MCP client
result = await session.call_tool("get_video_info", {
    "video_path": "sample_input.mp4"
})
```

**Expected output:**
```json
{
  "format": "mp4",
  "duration": 10.0,
  "width": 1280,
  "height": 720,
  "fps": 30.0,
  "video_codec": "h264",
  "audio_codec": "aac",
  "file_size": "1.2 MB"
}
```

### Trim a Video

```python
# Extract first 5 seconds
result = await session.call_tool("trim_video", {
    "input_path": "sample_input.mp4",
    "output_path": "trimmed_output.mp4",
    "start_time": 0,
    "duration": 5
})
```

### Resize Video

```python
# Resize to 720p
result = await session.call_tool("resize_video", {
    "input_path": "sample_input.mp4", 
    "output_path": "resized_720p.mp4",
    "width": 1280,
    "height": 720
})
```

### Extract Audio

```python
# Extract audio track
result = await session.call_tool("extract_audio", {
    "input_path": "sample_input.mp4",
    "output_path": "extracted_audio.mp3"
})
```

### Generate Thumbnail

```python
# Create thumbnail at 5 second mark
result = await session.call_tool("generate_thumbnail", {
    "input_path": "sample_input.mp4",
    "output_path": "thumbnail.jpg",
    "timestamp": 5.0
})
```

## 🎯 Interactive Examples

### Using Natural Language (with Claude Desktop)

Once connected to Claude Desktop, you can use natural language commands:

> **You:** "I have a video called 'vacation.mp4'. Can you trim the first 30 seconds and resize it to 720p?"

> **Claude:** I'll help you trim and resize your video. Let me start by getting information about the video, then trim the first 30 seconds and resize it to 720p.

*Claude will then use the MCP tools to:*
1. Call `get_video_info` to analyze the video
2. Call `trim_video` to extract seconds 0-30  
3. Call `resize_video` to convert to 720p
4. Provide status updates throughout the process

### Batch Processing Example

> **You:** "I have several videos in my folder. Can you create thumbnails for all of them?"

*Claude will:*
1. Use `videos://list` resource to find all video files
2. Loop through each video using `generate_thumbnail`
3. Provide progress updates and final summary

## 🔍 Exploring Available Tools

### List All Tools

```python
# Get all available tools
tools = await session.list_tools()
for tool in tools.tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
    print("---")
```

### Discover Resources

```python
# List video files in current directory
resources = await session.list_resources()
video_list = await session.read_resource("videos://list")
print(f"Available videos: {video_list}")
```

### Check Tool Categories

The server provides tools in these categories:

- **Basic Operations**: `trim_video`, `resize_video`, `concatenate_videos`, `get_video_info`
- **Audio Processing**: `extract_audio`, `add_audio`, `extract_audio_spectrum`, `merge_audio_tracks`
- **Effects & Filters**: `apply_filter`, `change_speed`, `apply_color_grading`, `apply_motion_blur`
- **Advanced Operations**: `create_video_slideshow`, `create_video_mosaic`, `create_picture_in_picture`
- **Analysis Tools**: `extract_frames`, `detect_scene_changes`, `extract_video_statistics`
- **Text Overlays**: `add_text_overlay`, `create_animated_text`
- **VFX**: `create_green_screen_effect`, `create_particle_system`, `apply_3d_transforms`

## 🚨 Important Notes

### File Paths
- Use absolute paths or paths relative to the server's working directory
- Ensure output directories exist before running operations
- The server processes files in the directory where it's started

### Performance Tips
- For large videos, operations may take time - the server provides progress updates
- Use appropriate codecs and settings for your use case
- Consider disk space when processing multiple large files

### Error Handling
- The server provides detailed error messages for troubleshooting
- Check FFmpeg installation if you encounter codec issues
- Verify file permissions for input and output locations

## 🎉 Success!

You're now ready to start using the VFX MCP Server! Here's what you can do next:

### Immediate Next Steps
1. **[Explore Tool Categories](/tools/overview/)** - See all 35+ available tools
2. **[MCP Integration Guide](/getting-started/mcp-integration/)** - Set up with Claude Desktop
3. **[Common Workflows](/guides/common-workflows/)** - Learn typical video editing patterns

### Advanced Usage
1. **[Batch Processing Guide](/guides/batch-processing/)** - Process multiple videos efficiently
2. **[VFX and Compositing](/guides/vfx-compositing/)** - Create professional visual effects
3. **[API Reference](/api/tool-signatures/)** - Detailed tool documentation

---

**Questions?** Check out our [FAQ](/support/faq/) or [Troubleshooting Guide](/support/troubleshooting/) for help!