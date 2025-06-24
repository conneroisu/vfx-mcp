---
title: MCP Integration
description: How to integrate the VFX MCP Server with Claude Desktop and other MCP clients
---

# MCP Integration

Learn how to connect the VFX MCP Server with various MCP clients, including Claude Desktop, custom applications, and development tools.

## 🔌 What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard that enables AI assistants to securely connect to external data sources and tools. The VFX MCP Server implements this protocol to provide video editing capabilities to AI assistants.

### Key Benefits

- 🎯 **Natural Language Interface**: Control video editing with conversational commands
- 🔒 **Secure Communication**: Standardized protocol with built-in security
- 🔄 **Real-time Updates**: Streaming progress updates for long operations
- 🛠️ **Tool Discovery**: Automatic discovery of available video editing tools
- 📊 **Resource Access**: File discovery and metadata endpoints

## 🖥️ Claude Desktop Integration

### Configuration

Add the VFX MCP Server to your Claude Desktop configuration:

#### macOS/Linux
Edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vfx-server": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/vfx-mcp",
      "env": {
        "VFX_WORK_DIR": "/path/to/your/videos"
      }
    }
  }
}
```

#### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vfx-server": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "C:\\path\\to\\vfx-mcp",
      "env": {
        "VFX_WORK_DIR": "C:\\path\\to\\your\\videos"
      }
    }
  }
}
```

#### Using Nix Development Environment

If you're using the Nix development environment:

```json
{
  "mcpServers": {
    "vfx-server": {
      "command": "nix",
      "args": ["develop", "--command", "uv", "run", "python", "main.py"],
      "cwd": "/path/to/vfx-mcp"
    }
  }
}
```

### Testing the Connection

1. **Restart Claude Desktop** after updating the configuration
2. **Start a new conversation** and ask Claude about video editing capabilities
3. **Test with a simple command**:

> "What video editing tools do you have available?"

Claude should respond with information about the 35+ video editing tools provided by the server.

### Example Conversations

#### Basic Video Editing
> **You:** "I have a video called 'presentation.mp4' that's 10 minutes long. Can you trim it to just the first 5 minutes and create a thumbnail?"

> **Claude:** I'll help you trim your presentation video and create a thumbnail. Let me start by getting information about the video, then trim it to 5 minutes and generate a thumbnail.

*Claude will automatically use the MCP tools to complete these tasks.*

#### Advanced Editing
> **You:** "I need to create a professional-looking video from these three clips: intro.mp4, main_content.mp4, and outro.mp4. Can you concatenate them, add some color grading, and create a slideshow preview?"

*Claude will use multiple tools in sequence to complete this complex workflow.*

## 💻 Custom MCP Clients

### Python Client Example

```python
# vfx_client.py
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class VFXClient:
    def __init__(self, server_path: str):
        self.server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", "main.py"],
            cwd=server_path
        )
    
    async def connect(self):
        """Connect to the VFX MCP Server"""
        self.connection = stdio_client(self.server_params)
        self.read, self.write = await self.connection.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.initialize()
        
    async def disconnect(self):
        """Disconnect from the server"""
        await self.connection.__aexit__(None, None, None)
    
    async def list_video_tools(self):
        """Get all available video editing tools"""
        tools = await self.session.list_tools()
        return [tool.name for tool in tools.tools]
    
    async def get_video_info(self, video_path: str):
        """Get information about a video file"""
        result = await self.session.call_tool(
            "get_video_info", 
            {"video_path": video_path}
        )
        return json.loads(result.content[0].text)
    
    async def trim_video(self, input_path: str, output_path: str, 
                        start_time: float, duration: float = None):
        """Trim a video to specified duration"""
        args = {
            "input_path": input_path,
            "output_path": output_path, 
            "start_time": start_time
        }
        if duration:
            args["duration"] = duration
            
        result = await self.session.call_tool("trim_video", args)
        return result.content[0].text

# Usage example
async def main():
    client = VFXClient("/path/to/vfx-mcp")
    await client.connect()
    
    try:
        # List available tools
        tools = await client.list_video_tools()
        print(f"Available tools: {', '.join(tools)}")
        
        # Get video information
        info = await client.get_video_info("sample.mp4")
        print(f"Video duration: {info['duration']} seconds")
        
        # Trim video
        result = await client.trim_video(
            "sample.mp4", 
            "trimmed.mp4", 
            start_time=10.0, 
            duration=30.0
        )
        print(f"Trim result: {result}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript/Node.js Client

```javascript
// vfx-client.js
const { spawn } = require('child_process');
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

class VFXClient {
    constructor(serverPath) {
        this.serverPath = serverPath;
    }
    
    async connect() {
        // Spawn the server process
        this.serverProcess = spawn('uv', ['run', 'python', 'main.py'], {
            cwd: this.serverPath,
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        // Create MCP client with stdio transport
        const transport = new StdioTransport({
            readable: this.serverProcess.stdout,
            writable: this.serverProcess.stdin
        });
        
        this.client = new Client({
            name: "vfx-client",
            version: "1.0.0"
        }, {
            capabilities: {}
        });
        
        await this.client.connect(transport);
    }
    
    async listTools() {
        const result = await this.client.listTools();
        return result.tools.map(tool => tool.name);
    }
    
    async getVideoInfo(videoPath) {
        const result = await this.client.callTool({
            name: "get_video_info",
            arguments: { video_path: videoPath }
        });
        return JSON.parse(result.content[0].text);
    }
    
    async disconnect() {
        await this.client.close();
        this.serverProcess.kill();
    }
}

// Usage
async function main() {
    const client = new VFXClient('/path/to/vfx-mcp');
    await client.connect();
    
    try {
        const tools = await client.listTools();
        console.log('Available tools:', tools);
        
        const info = await client.getVideoInfo('sample.mp4');
        console.log('Video info:', info);
    } finally {
        await client.disconnect();
    }
}

main().catch(console.error);
```

## 🌐 Web Application Integration

### Server-Sent Events (SSE) Transport

For web applications, you can use SSE transport instead of stdio:

```python
# Run server with SSE transport
import os
os.environ['MCP_TRANSPORT'] = 'sse'
os.environ['MCP_HOST'] = 'localhost'
os.environ['MCP_PORT'] = '8000'

# Start server
uv run python main.py
```

### Web Client Example

```javascript
// web-client.js
class VFXWebClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async callTool(toolName, args) {
        const response = await fetch(`${this.baseUrl}/tools/${toolName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(args)
        });
        
        if (!response.ok) {
            throw new Error(`Tool call failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async getVideoInfo(videoPath) {
        return await this.callTool('get_video_info', { video_path: videoPath });
    }
    
    async trimVideo(inputPath, outputPath, startTime, duration) {
        return await this.callTool('trim_video', {
            input_path: inputPath,
            output_path: outputPath,
            start_time: startTime,
            duration: duration
        });
    }
}

// Usage in web application
const client = new VFXWebClient();

document.getElementById('process-video').addEventListener('click', async () => {
    try {
        const info = await client.getVideoInfo('input.mp4');
        console.log('Video info:', info);
        
        const result = await client.trimVideo('input.mp4', 'output.mp4', 0, 30);
        console.log('Trim result:', result);
    } catch (error) {
        console.error('Error:', error);
    }
});
```

## 🔧 Configuration Options

### Environment Variables

```bash
# Transport Configuration
export MCP_TRANSPORT=stdio          # 'stdio' or 'sse'
export MCP_HOST=localhost          # for SSE transport
export MCP_PORT=8000               # for SSE transport

# Working Directory
export VFX_WORK_DIR=/path/to/videos

# FFmpeg Paths (usually auto-detected)
export FFMPEG_PATH=/usr/bin/ffmpeg
export FFPROBE_PATH=/usr/bin/ffprobe

# Logging
export VFX_LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
```

### Server Configuration File

Create `vfx_config.json` in the server directory:

```json
{
  "transport": {
    "type": "stdio",
    "host": "localhost", 
    "port": 8000
  },
  "video": {
    "work_directory": "/path/to/videos",
    "max_file_size": "1GB",
    "supported_formats": ["mp4", "avi", "mov", "mkv"],
    "default_codec": "libx264"
  },
  "ffmpeg": {
    "path": "/usr/bin/ffmpeg",
    "probe_path": "/usr/bin/ffprobe",
    "threads": 4
  }
}
```

## ✅ Testing Your Integration

### Validation Checklist

1. **Server Starts**: The server starts without errors
2. **Client Connects**: Your MCP client can connect successfully  
3. **Tools Listed**: Client can retrieve list of available tools
4. **Tool Execution**: Can execute basic tools like `get_video_info`
5. **File Access**: Server can access video files in the work directory
6. **Error Handling**: Graceful error handling for invalid inputs

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export VFX_LOG_LEVEL=DEBUG
uv run python main.py
```

### Test Script

```python
# test_integration.py
import asyncio
import sys
from your_mcp_client import VFXClient

async def test_integration():
    client = VFXClient("/path/to/vfx-mcp")
    
    try:
        await client.connect()
        
        # Test 1: List tools
        tools = await client.list_video_tools()
        assert len(tools) > 30, f"Expected 30+ tools, got {len(tools)}"
        print("✅ Tool listing works")
        
        # Test 2: Basic tool execution (if test video exists)
        try:
            info = await client.get_video_info("test.mp4")
            print("✅ Tool execution works")
        except Exception as e:
            print(f"⚠️  Tool execution test skipped: {e}")
        
        print("🎉 Integration test passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        sys.exit(1)
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_integration())
```

## 📚 Next Steps

Now that you have MCP integration working:

1. **[Explore Tools](/tools/overview/)** - Learn about all 35+ available tools
2. **[Common Workflows](/guides/common-workflows/)** - Typical video editing patterns
3. **[API Reference](/api/tool-signatures/)** - Detailed tool documentation
4. **[Examples](/examples/basic-editing/)** - Practical usage examples

---

**Need help?** Check the [Troubleshooting Guide](/support/troubleshooting/) or [FAQ](/support/faq/) for common integration issues.