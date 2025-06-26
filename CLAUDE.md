# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a video editing MCP (Model Context Protocol) server built with FastMCP and ffmpeg-python. The server enables LLMs to perform professional video editing operations through a standardized interface, providing AI-powered video manipulation and processing workflows.

**🎉 Now available on PyPI!** Install with `pip install vfx-mcp` - https://pypi.org/project/vfx-mcp/

## Key Commands

### Development and Testing

```bash
# Install from PyPI (recommended)
pip install vfx-mcp

# Run the MCP server
vfx-mcp

# Or for development:
# Enter Nix development environment (includes all dependencies)
nix develop

# Install Python dependencies (if not using Nix)
uv sync

# Run the MCP server
uv run python main.py

# Run tests
pytest
# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run with coverage
pytest --cov=src

# Format code
ruff format .

# Run linting
ruff check .

# Type checking (if available)
mypy main.py src/
```

### Nix Environment Commands

When in the Nix development shell, additional commands are available:

```bash
dx       # Edit flake.nix
tests    # Run all tests (wrapper command)
run      # Run with hot reloading using air
```

## Architecture

### Core Design Patterns

**Single-File Architecture**: All video editing tools are implemented in `main.py` as decorated functions using FastMCP's `@mcp.tool` pattern. This monolithic approach keeps the codebase simple and focused.

**Tool Categories**:
- **Basic Operations**: `trim_video`, `concatenate_videos`, `resize_video`, `get_video_info`
- **Audio Processing**: `extract_audio`, `add_audio` (replace or mix modes)
- **Effects & Filters**: `apply_filter`, `change_speed`, `generate_thumbnail`
- **Format Conversion**: `convert_format` with codec and bitrate control

**Resource Endpoints**: MCP resources for file discovery and metadata:
- `videos://list` - Lists available video files in workspace
- `videos://{filename}/metadata` - Returns detailed video metadata as JSON

### FFmpeg Integration

All video operations use `ffmpeg-python` for robust video processing:
- **Error Handling**: Comprehensive error catching with stderr decoding
- **Progress Reporting**: Optional MCP context for operation status updates
- **Efficiency**: Uses copy mode for operations that don't require re-encoding
- **Compatibility**: Handles various formats, codecs, and parameters

### Testing Infrastructure

**Fixtures** (`tests/conftest.py`):
- `sample_video`: Generates 5-second H.264/AAC test video with color bars and 440Hz tone
- `sample_videos`: Creates multiple test videos with different patterns for concatenation tests
- `sample_audio`: Generates 3-second MP3 audio file for audio processing tests
- `temp_dir`: Managed temporary directory for test file isolation

**Test Categories**:
- `@pytest.mark.unit` - Fast unit tests for individual functions
- `@pytest.mark.integration` - Tests involving actual video processing
- `@pytest.mark.slow` - Performance tests that may take longer to execute

### Development Environment

**Nix Flake Setup**: Provides consistent development environment with:
- Python 3.13 with uv package manager
- FFmpeg with full codec support (`ffmpeg-full`)
- Development tools (ruff, black, basedpyright)
- Optional multimedia tools (imagemagick, sox)

**Environment Variables**:
- `FFMPEG_PATH` and `FFPROBE_PATH` - Automatically set in Nix environment
- `MCP_TRANSPORT` - Server transport mode ('stdio' or 'sse')
- `MCP_HOST` and `MCP_PORT` - SSE transport configuration

## Common Patterns

### Adding New Video Tools

1. Create async function with `@mcp.tool` decorator
2. Include comprehensive type hints and docstring
3. Use optional `ctx: Context` parameter for progress reporting
4. Implement proper error handling with ffmpeg.Error catching
5. Add corresponding tests in appropriate test file

Example pattern:
```python
@mcp.tool
async def new_operation(
    input_path: str,
    output_path: str,
    parameter: type,
    ctx: Context | None = None,
) -> str:
    """Operation description."""
    if ctx:
        await ctx.info("Starting operation...")
    
    try:
        stream = ffmpeg.input(input_path)
        # Apply transformations
        stream = ffmpeg.output(stream, output_path)
        ffmpeg.run(stream, overwrite_output=True)
        return f"Operation completed: {output_path}"
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise RuntimeError(error_msg) from e
```

### Speed Optimization Considerations

- For trimming operations, use `c="copy"` to avoid re-encoding
- Chain multiple atempo filters for speeds > 2.0x (ffmpeg limitation)
- Use appropriate presets (`ultrafast` for testing, `medium` for production)
- Consider file size vs quality tradeoffs when setting bitrates

### MCP Client Integration

Server supports both stdio and SSE transports for different integration scenarios:
- **Claude Desktop**: Uses stdio transport with `vfx-mcp` (PyPI) or `uv run python main.py` (dev)
- **Web Applications**: Can use SSE transport with host/port configuration
- **Direct API**: FastMCP client library for programmatic access

**PyPI Installation**: The server is now available as a pip package at https://pypi.org/project/vfx-mcp/ making it easy to install and distribute across different environments.