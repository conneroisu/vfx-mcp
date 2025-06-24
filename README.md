# vfx-mcp 🎬

A powerful video editing MCP (Model Context Protocol) server built with FastMCP and ffmpeg-python. This server allows LLMs to perform video editing operations through a standardized interface, enabling AI-powered video manipulation and processing workflows.

## Features

### Core Video Operations
- **Trimming & Cutting**: Extract specific segments from videos
- **Concatenation**: Join multiple videos together
- **Format Conversion**: Transcode between different video formats
- **Resolution & Quality**: Resize, change bitrate, adjust quality
- **Audio Processing**: Extract, replace, or mix audio tracks
- **Effects & Filters**: Apply ffmpeg filters and effects
- **Analysis**: Get video metadata, generate thumbnails
- **Advanced Operations**: Speed changes, reverse playback, loops

### MCP Capabilities
- **Tools**: Execute video editing operations
- **Resources**: Access and manage video files
- **Context**: Progress reporting for long operations
- **Streaming**: Support for both file-based and streaming workflows

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/conneroisu/vfx-mcp.git
cd vfx-mcp

# Install dependencies with uv
uv sync

# Run the server
uv run python main.py
```

### Using Nix

```bash
# Enter the development shell
nix develop

# Run the server
python main.py
```

### System Requirements

- Python 3.13+
- FFmpeg (installed automatically with Nix, or install manually)
- uv package manager (for non-Nix installation)

## Quick Start

### Basic Usage

```python
# Connect to the VFX MCP server
from fastmcp import Client

async with Client("python main.py") as client:
    # Trim a video
    result = await client.call_tool("trim_video", {
        "input_path": "input.mp4",
        "output_path": "trimmed.mp4",
        "start_time": 10.0,
        "duration": 30.0
    })
    
    # Get video information
    info = await client.call_tool("get_video_info", {
        "video_path": "input.mp4"
    })
    print(info)
```

### CLI Usage with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "vfx": {
      "command": "uv",
      "args": ["run", "python", "/path/to/vfx-mcp/main.py"],
      "cwd": "/path/to/vfx-mcp"
    }
  }
}
```

## API Reference

### Video Processing Tools

#### `trim_video`
Extract a segment from a video.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path for output video file
- `start_time` (float): Start time in seconds
- `duration` (float, optional): Duration in seconds (if not specified, trims to end)

#### `concatenate_videos`
Join multiple videos together.

**Parameters:**
- `input_paths` (list[str]): List of video file paths to concatenate
- `output_path` (str): Path for output video file
- `transition` (str, optional): Transition type between videos

#### `convert_format`
Convert video to different format or codec.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path for output video file
- `format` (str, optional): Output format (mp4, avi, mov, webm, etc.)
- `codec` (str, optional): Video codec (h264, h265, vp9, etc.)
- `audio_codec` (str, optional): Audio codec (aac, mp3, opus, etc.)

#### `resize_video`
Change video resolution.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path for output video file
- `width` (int, optional): Target width (maintains aspect ratio if height not specified)
- `height` (int, optional): Target height (maintains aspect ratio if width not specified)
- `scale` (float, optional): Scale factor (e.g., 0.5 for half size)

#### `extract_audio`
Extract audio track from video.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path for output audio file
- `format` (str, optional): Audio format (mp3, wav, aac, etc.)

#### `add_audio`
Add or replace audio track in video.

**Parameters:**
- `video_path` (str): Path to input video file
- `audio_path` (str): Path to audio file
- `output_path` (str): Path for output video file
- `replace` (bool, optional): Replace existing audio (default: true)

#### `apply_filter`
Apply ffmpeg filter to video.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path for output video file
- `filter` (str): FFmpeg filter string (e.g., "blur=10", "hflip", "reverse")

#### `change_speed`
Adjust video playback speed.

**Parameters:**
- `input_path` (str): Path to input video file
- `output_path` (str): Path for output video file
- `speed` (float): Speed multiplier (e.g., 2.0 for double speed, 0.5 for half speed)

#### `generate_thumbnail`
Extract frame as image thumbnail.

**Parameters:**
- `video_path` (str): Path to input video file
- `output_path` (str): Path for output image file
- `timestamp` (float, optional): Time in seconds (default: middle of video)

#### `get_video_info`
Get detailed video metadata.

**Parameters:**
- `video_path` (str): Path to video file

**Returns:**
- Video metadata including duration, resolution, codec, bitrate, fps, etc.

### Resource Endpoints

#### `videos://list`
List available video files in the workspace.

#### `videos://{filename}/metadata`
Get metadata for a specific video file.

#### `videos://workspace/info`
Get workspace information and available storage.

## Examples

### Create a Video Montage

```python
async with Client("python main.py") as client:
    # 1. Trim clips from source videos
    clips = []
    for i, (video, start, duration) in enumerate([
        ("vacation.mp4", 30, 5),
        ("birthday.mp4", 120, 8),
        ("concert.mp4", 45, 6)
    ]):
        clip_path = f"clip_{i}.mp4"
        await client.call_tool("trim_video", {
            "input_path": video,
            "output_path": clip_path,
            "start_time": start,
            "duration": duration
        })
        clips.append(clip_path)
    
    # 2. Concatenate clips
    await client.call_tool("concatenate_videos", {
        "input_paths": clips,
        "output_path": "montage.mp4",
        "transition": "fade"
    })
    
    # 3. Add background music
    await client.call_tool("add_audio", {
        "video_path": "montage.mp4",
        "audio_path": "background_music.mp3",
        "output_path": "final_montage.mp4"
    })
```

### Process Video for Web

```python
async with Client("python main.py") as client:
    # Convert to web-friendly format with optimized settings
    await client.call_tool("convert_format", {
        "input_path": "raw_video.mov",
        "output_path": "web_video.mp4",
        "format": "mp4",
        "codec": "h264",
        "audio_codec": "aac"
    })
    
    # Create multiple resolutions
    for width in [1920, 1280, 854]:
        await client.call_tool("resize_video", {
            "input_path": "web_video.mp4",
            "output_path": f"web_video_{width}.mp4",
            "width": width
        })
    
    # Generate thumbnail
    await client.call_tool("generate_thumbnail", {
        "video_path": "web_video.mp4",
        "output_path": "thumbnail.jpg"
    })
```

## Architecture

### Project Structure

```
vfx-mcp/
├── README.md              # This file
├── flake.nix             # Nix development environment
├── pyproject.toml        # Python project configuration
├── uv.lock              # Locked dependencies
├── main.py              # MCP server entry point
├── src/
│   ├── __init__.py
│   ├── server.py        # FastMCP server configuration
│   ├── tools/           # Video editing tool implementations
│   │   ├── __init__.py
│   │   ├── basic.py     # Basic operations (trim, concat, etc.)
│   │   ├── transform.py # Transformations (resize, rotate, etc.)
│   │   ├── audio.py     # Audio processing tools
│   │   └── effects.py   # Filters and effects
│   ├── resources/       # MCP resource handlers
│   │   └── videos.py    # Video file management
│   └── utils/           # Utility functions
│       ├── ffmpeg.py    # FFmpeg wrapper utilities
│       └── progress.py  # Progress reporting helpers
└── examples/            # Example usage scripts
    ├── montage.py       # Create video montage
    ├── web_process.py   # Process for web
    └── batch_convert.py # Batch conversion
```

### Key Components

1. **FastMCP Server**: Central server handling MCP protocol communication
2. **Tool Modules**: Organized by functionality (basic, transform, audio, effects)
3. **FFmpeg Integration**: Using ffmpeg-python for robust video processing
4. **Progress Reporting**: Real-time progress updates for long operations
5. **Error Handling**: Comprehensive error handling for ffmpeg operations

## Development

### Setting Up Development Environment

#### With Nix (Recommended for consistent environment)

```bash
# Enter development shell with all dependencies
nix develop

# Run tests
pytest

# Run linting
ruff check .

# Format code
ruff format .
```

#### With uv

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

### Adding New Tools

1. Create a new function in the appropriate module under `src/tools/`
2. Use the `@mcp.tool` decorator
3. Add proper type hints and docstring
4. Implement error handling

Example:

```python
@mcp.tool
async def rotate_video(
    input_path: str,
    output_path: str,
    angle: int,
    ctx: Context
) -> str:
    """Rotate video by specified angle (90, 180, 270 degrees)."""
    if angle not in [90, 180, 270]:
        raise ValueError("Angle must be 90, 180, or 270 degrees")
    
    await ctx.info(f"Rotating video by {angle} degrees...")
    
    # Implementation using ffmpeg-python
    stream = ffmpeg.input(input_path)
    stream = ffmpeg.filter(stream, 'rotate', angle=math.radians(angle))
    stream = ffmpeg.output(stream, output_path)
    
    await run_ffmpeg_with_progress(stream, ctx)
    return f"Video rotated and saved to {output_path}"
```

### Testing

Run the test suite:

```bash
# All tests
pytest

# Specific test file
pytest tests/test_basic_tools.py

# With coverage
pytest --cov=src
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-tool`)
3. Make your changes and add tests
4. Run linting and tests
5. Commit your changes (`git commit -m 'Add amazing tool'`)
6. Push to the branch (`git push origin feature/amazing-tool`)
7. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) - The fast, Pythonic MCP framework
- Powered by [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) - Python bindings for FFmpeg
- Uses [Model Context Protocol](https://modelcontextprotocol.io) - Standard for LLM integrations
