---
title: FAQ
description: Frequently asked questions about the VFX MCP Server
---

Find answers to the most common questions about the VFX MCP Server, including setup, usage, and troubleshooting.

## 🚀 General Questions

### What is the VFX MCP Server?

The VFX MCP Server is a professional video editing server that implements the Model Context Protocol (MCP). It provides 35+ video editing tools that can be used by AI assistants like Claude to perform sophisticated video manipulation, effects, and processing tasks through natural language commands.

### What can I do with the VFX MCP Server?

You can perform a wide range of video editing tasks:
- **Basic editing**: Trim, resize, concatenate videos
- **Audio processing**: Extract, mix, and enhance audio
- **Visual effects**: Color grading, motion blur, stabilization
- **Advanced composition**: Picture-in-picture, green screen, particle effects
- **Format conversion**: Convert between video formats
- **Batch processing**: Process multiple videos automatically

### Do I need video editing experience to use this?

No! The server is designed to work with AI assistants, so you can use natural language to describe what you want to accomplish. For example: "Trim the first 30 seconds of this video and make it brighter" or "Create a slideshow from these images with music."

### Is it free to use?

Yes, the VFX MCP Server is open source and free to use. However, you'll need:
- A computer capable of running Python and FFmpeg
- An MCP client (like Claude Desktop) to interact with the server
- Video files to process

---

## 🛠️ Installation and Setup

### What are the system requirements?

**Minimum Requirements**:
- Python 3.9 or higher
- FFmpeg (latest version)
- 4GB RAM
- 2GB available disk space

**Recommended**:
- Python 3.11+
- 8GB+ RAM
- SSD storage
- Multi-core processor

### How do I install FFmpeg?

**Ubuntu/Debian**:
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS**:
```bash
brew install ffmpeg
```

**Windows**:
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

**Using Nix** (recommended):
```bash
nix develop  # Includes FFmpeg automatically
```

### Why use the Nix development environment?

The Nix environment provides:
- ✅ Automatic FFmpeg installation with full codec support
- ✅ Consistent environment across different systems
- ✅ All development tools included
- ✅ No dependency conflicts

### Can I use this without Claude Desktop?

Yes! The server implements the standard MCP protocol and can work with:
- **Claude Desktop** (easiest setup)
- **Custom MCP clients** (Python, JavaScript, etc.)
- **Web applications** (using SSE transport)
- **Direct API calls** (for developers)

---

## 🎬 Usage Questions

### How do I start the server?

```bash
# Navigate to the project directory
cd vfx-mcp

# Using Nix (recommended)
nix develop
uv run python main.py

# Or without Nix
uv sync
uv run python main.py
```

The server will start and wait for MCP client connections.

### How do I connect Claude Desktop?

1. **Edit your Claude Desktop configuration**:
   - macOS: `~/.config/claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add the server configuration**:
   ```json
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

3. **Restart Claude Desktop**

### What video formats are supported?

**Input formats**: MP4, AVI, MOV, MKV, WebM, FLV, 3GP, and more
**Output formats**: MP4, AVI, MOV, MKV, WebM
**Audio formats**: MP3, WAV, AAC, FLAC
**Image formats**: JPG, PNG, BMP, TIFF

The exact list depends on your FFmpeg installation. Use the `get_video_info` tool to check if a specific file is supported.

### Can I process multiple videos at once?

Yes! The server supports:
- **Batch processing**: Process multiple videos with the same settings
- **Concatenation**: Join multiple videos together
- **Concurrent operations**: Process different videos simultaneously

Example with Claude Desktop:
> "Process all MP4 files in my folder: trim the first 30 seconds, apply color grading, and resize to 720p"

### How long does video processing take?

Processing time depends on:
- **Video length and resolution**
- **Complexity of operations**
- **Your computer's performance**
- **Output quality settings**

**Typical times**:
- Trimming (copy mode): Seconds
- Color grading: 1-5x realtime
- Complex effects: 2-10x realtime
- Format conversion: 1-3x realtime

---

## 🔧 Technical Questions

### Where are my processed videos saved?

By default, output videos are saved in the same directory as the input videos. You can:
- **Specify custom output paths** in tool calls
- **Set a working directory** with `VFX_WORK_DIR` environment variable
- **Use absolute paths** for precise control

### How do I improve processing speed?

1. **Use appropriate quality settings**:
   - "low" for previews
   - "medium" for social media
   - "high" for professional output

2. **Leverage copy mode**:
   - Trimming without re-encoding is fastest
   - Use when input/output formats match

3. **Process similar content together**:
   - Batch operations are more efficient
   - Consistent settings reduce overhead

4. **Monitor system resources**:
   ```python
   capabilities = await session.read_resource("tools://capabilities")
   print(capabilities['system_resources'])
   ```

### What's the difference between quality settings?

| Setting | Use Case | Speed | File Size | Quality |
|---------|----------|-------|-----------|---------|
| **low** | Previews, drafts | Fastest | Smallest | Basic |
| **medium** | Social media | Fast | Small | Good |
| **high** | Professional | Moderate | Large | Excellent |
| **ultra** | Archive, master | Slow | Largest | Perfect |

### Can I use custom FFmpeg filters?

Yes! Use the `apply_filter` tool with custom FFmpeg filter strings:

```python
await session.call_tool("apply_filter", {
    "input_path": "input.mp4",
    "output_path": "filtered.mp4",
    "filter_string": "eq=brightness=0.1:contrast=1.2,unsharp=5:5:1.0"
})
```

---

## 🐛 Troubleshooting

### The server won't start. What should I check?

1. **Verify FFmpeg installation**:
   ```bash
   ffmpeg -version
   ```

2. **Check Python version**:
   ```bash
   python --version  # Should be 3.9+
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Check working directory**:
   ```bash
   cd /path/to/vfx-mcp
   ls main.py  # Should exist
   ```

### Claude Desktop says "Server failed to start"

**Common causes and solutions**:

1. **Wrong file paths**: Use absolute paths in configuration
2. **Missing dependencies**: Run `uv sync` in the project directory
3. **Permission issues**: Ensure the directory is readable
4. **Configuration errors**: Validate JSON syntax

**Test the server independently**:
```bash
cd /path/to/vfx-mcp
uv run python main.py
# Should start without errors
```

### Video processing fails with FFmpeg errors

1. **Check input file**:
   ```python
   info = await session.call_tool("get_video_info", {
       "video_path": "problem_video.mp4"
   })
   ```

2. **Verify disk space**:
   ```bash
   df -h .
   ```

3. **Try format conversion**:
   ```python
   await session.call_tool("convert_format", {
       "input_path": "problem_video.avi",
       "output_path": "converted.mp4",
       "video_codec": "libx264",
       "audio_codec": "aac"
   })
   ```

### Processing is very slow

1. **Lower quality settings**:
   ```python
   # Use "medium" instead of "ultra" quality
   ```

2. **Check system resources**:
   ```python
   capabilities = await session.read_resource("tools://capabilities")
   resources = capabilities['system_resources']
   print(f"CPU: {resources['cpu_usage']}%")
   print(f"Memory: {resources['memory_usage']}%")
   ```

3. **Process smaller segments**:
   ```python
   # Split large videos into smaller chunks
   ```

### How do I enable debug logging?

```bash
export VFX_LOG_LEVEL=DEBUG
uv run python main.py 2>&1 | tee debug.log
```

This will show detailed information about what the server is doing.

---

## 💡 Tips and Best Practices

### How should I organize my video files?

**Recommended structure**:
```
video_projects/
├── input/          # Source videos
├── output/         # Processed videos  
├── temp/           # Temporary files
└── assets/         # Images, audio, etc.
```

**Set working directory**:
```bash
export VFX_WORK_DIR=/path/to/video_projects
```

### What's the best workflow for beginners?

1. **Start simple**: Trim and resize videos first
2. **Use get_video_info**: Always check video properties before processing
3. **Test with short clips**: Don't start with 2-hour videos
4. **Save incrementally**: Process in steps rather than one complex operation

**Example beginner workflow**:
> "I have a 10-minute video called 'presentation.mp4'. Can you show me its properties, then trim the first 5 minutes and resize it to 720p?"

### How do I create professional-looking videos?

1. **Use consistent color grading**:
   ```python
   # Apply professional color correction
   await session.call_tool("apply_color_grading", {
       "input_path": "raw_footage.mp4",
       "output_path": "graded.mp4",
       "contrast": 1.1,
       "saturation": 0.9,
       "shadows": 0.05
   })
   ```

2. **Add smooth transitions**:
   ```python
   await session.call_tool("concatenate_videos", {
       "input_paths": ["clip1.mp4", "clip2.mp4"],
       "output_path": "smooth_edit.mp4",
       "transition_duration": 1.0
   })
   ```

3. **Stabilize shaky footage**:
   ```python
   await session.call_tool("apply_video_stabilization", {
       "input_path": "shaky.mp4",
       "output_path": "stable.mp4",
       "smoothing": 10.0
   })
   ```

### Can I automate repetitive tasks?

Absolutely! Example automation:

> "I have 20 videos that need the same processing: trim to 60 seconds, apply bright color grading, and resize to 1080p. Can you process them all?"

The server will automatically process all videos with consistent settings.

---

## 🔮 Advanced Usage

### Can I integrate this into my own application?

Yes! The server provides:
- **MCP protocol support**: Standard interface for integration
- **SSE transport**: For web applications
- **Python API**: Direct integration with Python apps
- **Resource endpoints**: File discovery and metadata

### Is GPU acceleration supported?

Currently, the server uses CPU-based FFmpeg processing. GPU acceleration may be added in future versions depending on your FFmpeg build and hardware.

### Can I extend the server with custom tools?

The server is designed to be extensible. You can:
- **Fork the repository**: Add your own tools
- **Submit feature requests**: Suggest new tools for the main project
- **Use custom filters**: Apply any FFmpeg filter through `apply_filter`

### How do I contribute to the project?

- **Report bugs**: Use GitHub issues
- **Suggest features**: Describe your use case
- **Submit pull requests**: Follow the contribution guidelines
- **Share examples**: Show what you've created

---

## 📚 Learning Resources

### Where can I learn more about video editing concepts?

- **FFmpeg documentation**: [ffmpeg.org](https://ffmpeg.org/documentation.html)
- **Color grading basics**: Search for "video color grading tutorials"
- **Video formats**: Understanding codecs and containers
- **Audio processing**: Learn about sample rates, bitrates, and formats

### How do I get better at using AI for video editing?

1. **Be specific**: "Trim 30 seconds" vs "make it shorter"
2. **Describe your goal**: "for Instagram post" vs "process this video"
3. **Ask for explanations**: "Why did you choose those settings?"
4. **Experiment**: Try different approaches and compare results

### Where can I find example videos to practice with?

- **Create test content**: Use your phone to record short clips
- **Free stock footage**: Pixabay, Pexels (check licenses)
- **Generate test videos**: The server can create sample content
- **Use the examples**: Check the documentation examples

---

**Still have questions?** Check the [troubleshooting guide](/support/troubleshooting/) or [file an issue](https://github.com/conneroisu/vfx-mcp/issues) on GitHub.