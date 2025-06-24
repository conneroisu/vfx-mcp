---
title: Installation
description: How to install and set up the VFX MCP Server
---

Get the VFX MCP Server up and running in just a few steps. This guide covers multiple installation methods to suit your development environment.

## 🚀 Quick Start

### Option 1: Nix Development Environment (Recommended)

The project includes a comprehensive Nix flake that provides all necessary dependencies:

```bash
# Clone the repository
git clone https://github.com/conneroisu/vfx-mcp.git
cd vfx-mcp

# Enter the Nix development environment
nix develop

# Install Python dependencies
uv sync

# Run the server
uv run python main.py
```

### Option 2: Manual Installation

If you prefer not to use Nix, you can install dependencies manually:

```bash
# Clone the repository  
git clone https://github.com/conneroisu/vfx-mcp.git
cd vfx-mcp

# Install FFmpeg (required for video processing)
# On Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# On macOS with Homebrew:
brew install ffmpeg

# On Windows:
# Download from https://ffmpeg.org/download.html

# Install Python dependencies with uv
pip install uv
uv sync

# Or with pip directly
pip install -r requirements.txt
```

## 📋 Requirements

### System Requirements

- **Python**: 3.9 or higher
- **FFmpeg**: Latest version (with full codec support)
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 4GB RAM minimum (8GB recommended for large videos)
- **Storage**: Sufficient space for input/output video files

### Python Dependencies

The server uses these key packages:

- **FastMCP**: Model Context Protocol server framework
- **ffmpeg-python**: Python bindings for FFmpeg
- **Pillow**: Image processing for thumbnails and frames
- **pytest**: Testing framework (development only)

## 🔧 Environment Setup

### Environment Variables

The server can be configured using these environment variables:

```bash
# MCP Transport Configuration
export MCP_TRANSPORT=stdio          # or 'sse'
export MCP_HOST=localhost          # for SSE transport
export MCP_PORT=8000               # for SSE transport

# FFmpeg Configuration (auto-detected in Nix)
export FFMPEG_PATH=/usr/bin/ffmpeg
export FFPROBE_PATH=/usr/bin/ffprobe

# Working Directory (where videos are processed)
export VFX_WORK_DIR=/path/to/videos
```

### Nix Environment Benefits

Using the Nix development environment provides:

- **FFmpeg with full codec support** (`ffmpeg-full`)
- **Automatic path configuration** for FFmpeg tools
- **Development tools** (ruff, black, basedpyright)
- **Consistent environment** across different systems
- **Hot reloading** with Air for development

Available commands in the Nix shell:

```bash
dx       # Edit flake.nix
tests    # Run all tests
run      # Run with hot reloading
format   # Format code
lint     # Run linting
```

## ✅ Verification

### Test Your Installation

1. **Verify FFmpeg is available:**
   ```bash
   ffmpeg -version
   ffprobe -version
   ```

2. **Test the MCP server:**
   ```bash
   # Run the server (should start without errors)
   uv run python main.py
   
   # The server will wait for MCP client connections
   # Press Ctrl+C to stop
   ```

3. **Run the test suite:**
   ```bash
   pytest
   
   # Run specific test categories
   pytest -m unit        # Fast unit tests
   pytest -m integration # Integration tests
   pytest -m "not slow"  # Skip performance tests
   ```

### Sample Test

Create a simple test to verify everything works:

```python
# test_installation.py
import subprocess
import sys

def test_ffmpeg_available():
    """Test that FFmpeg is available"""
    result = subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'ffmpeg version' in result.stdout

def test_server_imports():
    """Test that the server can be imported"""
    try:
        import main
        print("✅ Server imports successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_ffmpeg_available()
    test_server_imports()
    print("🎉 Installation verified!")
```

Run the test:
```bash
python test_installation.py
```

## 🔍 Troubleshooting

### Common Issues

**FFmpeg not found:**
```bash
# Check if FFmpeg is in PATH
which ffmpeg
ffmpeg -version

# If not installed, see installation instructions above
```

**Python version issues:**
```bash
# Check Python version
python --version

# Use specific Python version if needed
python3.9 -m pip install uv
```

**Permission errors:**
```bash
# On Linux/macOS, ensure FFmpeg has execute permissions
chmod +x /usr/bin/ffmpeg
chmod +x /usr/bin/ffprobe
```

**Import errors:**
```bash
# Ensure you're in the project directory
cd vfx-mcp

# Reinstall dependencies
uv sync --force-reinstall
```

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](/support/troubleshooting/)
2. Review the [FAQ](/support/faq/)
3. File an issue on [GitHub](https://github.com/conneroisu/vfx-mcp/issues)

## 🎯 Next Steps

Once installation is complete:

1. **[Quick Start Guide](/getting-started/quick-start/)** - Run your first video editing commands
2. **[MCP Integration](/getting-started/mcp-integration/)** - Connect to Claude Desktop or other MCP clients  
3. **[Tool Overview](/tools/overview/)** - Explore all available video editing tools
4. **[Common Workflows](/guides/common-workflows/)** - Learn typical video editing tasks

---

**Ready to start editing videos with AI?** Continue to the [Quick Start Guide →](/getting-started/quick-start/)