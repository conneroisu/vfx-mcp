---
title: Resource Endpoints
description: MCP resource endpoints for file discovery and metadata access
---

# Resource Endpoints

The VFX MCP Server provides several resource endpoints that enable clients to discover available video files, access metadata, and explore server capabilities. These endpoints follow the MCP resource protocol for standardized data access.

## 📁 Available Resources

### `videos://list`
Lists all video files in the current working directory with basic metadata.

**URI Pattern**: `videos://list`

**Response Format**:
```json
{
  "videos": [
    {
      "name": "sample.mp4",
      "path": "/path/to/sample.mp4",
      "size": "15.2 MB",
      "duration": 45.3,
      "resolution": "1920x1080",
      "format": "mp4",
      "created": "2024-01-15T10:30:00Z",
      "modified": "2024-01-15T10:35:00Z"
    },
    {
      "name": "presentation.avi",
      "path": "/path/to/presentation.avi", 
      "size": "120.5 MB",
      "duration": 180.0,
      "resolution": "1280x720",
      "format": "avi",
      "created": "2024-01-14T15:20:00Z",
      "modified": "2024-01-14T15:25:00Z"
    }
  ],
  "total_count": 2,
  "total_size": "135.7 MB",
  "supported_formats": ["mp4", "avi", "mov", "mkv", "webm"],
  "working_directory": "/path/to/videos"
}
```

**Example Usage**:
```python
# Using MCP client
resources = await session.list_resources()
video_list = await session.read_resource("videos://list")

print(f"Found {video_list['total_count']} videos")
for video in video_list['videos']:
    print(f"- {video['name']}: {video['duration']}s, {video['resolution']}")
```

**Use Cases**:
- **File Discovery**: Find all video files in the workspace
- **Batch Processing**: Get list of files for batch operations
- **Workspace Management**: Monitor file changes and additions
- **Quality Assessment**: Quick overview of video properties

---

### `videos://{filename}/metadata`
Returns detailed metadata for a specific video file.

**URI Pattern**: `videos://{filename}/metadata`

**Parameters**:
- `{filename}`: Name of the video file (with or without extension)

**Response Format**:
```json
{
  "file_info": {
    "name": "sample.mp4",
    "path": "/path/to/sample.mp4",
    "size": 15728640,
    "size_human": "15.2 MB",
    "created": "2024-01-15T10:30:00Z",
    "modified": "2024-01-15T10:35:00Z",
    "permissions": "rw-r--r--"
  },
  "video_properties": {
    "format": "mp4",
    "duration": 45.3,
    "width": 1920,
    "height": 1080,
    "aspect_ratio": "16:9",
    "fps": 30.0,
    "frame_count": 1359,
    "video_codec": "h264",
    "video_bitrate": 2500000,
    "color_space": "yuv420p",
    "pixel_format": "yuv420p"
  },
  "audio_properties": {
    "has_audio": true,
    "audio_codec": "aac",
    "audio_bitrate": 128000,
    "sample_rate": 44100,
    "channels": 2,
    "channel_layout": "stereo"
  },
  "technical_info": {
    "container": "mov,mp4,m4a,3gp,3g2,mj2",
    "overall_bitrate": 2628000,
    "is_variable_bitrate": false,
    "has_b_frames": true,
    "gop_size": 250,
    "encoding_profile": "High",
    "encoding_level": "4.0"
  },
  "quality_metrics": {
    "estimated_quality": "high",
    "compression_ratio": 0.15,
    "bits_per_pixel": 0.12,
    "audio_quality": "good"
  }
}
```

**Example Usage**:
```python
# Get detailed metadata for specific video
metadata = await session.read_resource("videos://sample.mp4/metadata")

# Extract key information
video_props = metadata['video_properties']
audio_props = metadata['audio_properties']

print(f"Video: {video_props['width']}x{video_props['height']} @ {video_props['fps']}fps")
print(f"Duration: {video_props['duration']} seconds")
print(f"Audio: {audio_props['channels']} channels @ {audio_props['sample_rate']}Hz")

# Check if suitable for processing
if video_props['video_codec'] == 'h264' and audio_props['has_audio']:
    print("✅ Ready for processing")
else:
    print("⚠️ May need format conversion")
```

**Use Cases**:
- **Pre-processing Analysis**: Check video compatibility before operations
- **Quality Assessment**: Evaluate video technical properties
- **Workflow Planning**: Determine optimal processing parameters
- **Format Validation**: Verify codec and container support

---

### `tools://advanced`
Provides information about advanced tool capabilities, usage patterns, and best practices.

**URI Pattern**: `tools://advanced`

**Response Format**:
```json
{
  "categories": {
    "basic_operations": {
      "tools": ["trim_video", "get_video_info", "resize_video", "concatenate_videos"],
      "description": "Essential video manipulation functions",
      "use_cases": ["editing", "format_conversion", "basic_processing"]
    },
    "audio_processing": {
      "tools": ["extract_audio", "add_audio", "extract_audio_spectrum", "merge_audio_tracks"],
      "description": "Audio manipulation and visualization",
      "use_cases": ["podcast_production", "music_videos", "audio_cleanup"]
    },
    "effects_filters": {
      "tools": ["apply_filter", "change_speed", "apply_color_grading", "apply_motion_blur", "apply_video_stabilization"],
      "description": "Professional enhancement and effects",
      "use_cases": ["color_correction", "stabilization", "creative_effects"]
    }
  },
  "workflow_patterns": {
    "basic_editing": {
      "steps": ["get_video_info", "trim_video", "resize_video"],
      "description": "Simple video editing workflow"
    },
    "professional_grading": {
      "steps": ["get_video_info", "apply_color_grading", "apply_filter"],
      "description": "Professional color grading pipeline"
    },
    "podcast_production": {
      "steps": ["extract_audio", "merge_audio_tracks", "add_audio"],
      "description": "Complete podcast production workflow"
    }
  },
  "performance_tips": {
    "optimization": [
      "Use copy mode for trimming when possible",
      "Batch similar operations together",
      "Choose appropriate quality settings for use case"
    ],
    "quality_settings": {
      "preview": "medium",
      "final_output": "high",
      "archive": "ultra"
    }
  },
  "format_support": {
    "input_formats": ["mp4", "avi", "mov", "mkv", "webm", "flv", "3gp"],
    "output_formats": ["mp4", "avi", "mov", "mkv", "webm"],
    "audio_formats": ["mp3", "wav", "aac", "flac"],
    "image_formats": ["jpg", "png", "bmp", "tiff"]
  }
}
```

**Example Usage**:
```python
# Get advanced tool information
advanced_info = await session.read_resource("tools://advanced")

# Find tools for specific use case
audio_tools = advanced_info['categories']['audio_processing']['tools']
print(f"Audio tools available: {', '.join(audio_tools)}")

# Get workflow recommendations
workflows = advanced_info['workflow_patterns']
for workflow_name, workflow_info in workflows.items():
    print(f"{workflow_name}: {workflow_info['description']}")
    print(f"  Steps: {' → '.join(workflow_info['steps'])}")
```

---

### `tools://capabilities`
Provides real-time information about server capabilities and system status.

**URI Pattern**: `tools://capabilities`

**Response Format**:
```json
{
  "server_info": {
    "version": "1.0.0",
    "mcp_version": "0.4.0",
    "python_version": "3.11.0",
    "platform": "linux",
    "uptime": "2h 15m 30s"
  },
  "ffmpeg_info": {
    "version": "4.4.2",
    "path": "/usr/bin/ffmpeg",
    "encoders": ["libx264", "libx265", "libvpx-vp9", "aac", "mp3"],
    "decoders": ["h264", "hevc", "vp9", "aac", "mp3", "flac"],
    "filters": ["scale", "crop", "overlay", "colorbalance", "eq"]
  },
  "system_resources": {
    "cpu_usage": 25.3,
    "memory_usage": 67.8,
    "disk_space_free": "150.2 GB",
    "temp_directory": "/tmp/vfx_mcp_temp"
  },
  "feature_flags": {
    "gpu_acceleration": false,
    "hardware_encoding": true,
    "batch_processing": true,
    "progress_reporting": true
  },
  "limits": {
    "max_file_size": "5GB",
    "max_resolution": "7680x4320",
    "concurrent_operations": 4,
    "temp_storage_limit": "10GB"
  }
}
```

**Example Usage**:
```python
# Check server capabilities
capabilities = await session.read_resource("tools://capabilities")

# Verify FFmpeg availability
ffmpeg_info = capabilities['ffmpeg_info']
if 'libx264' in ffmpeg_info['encoders']:
    print("✅ H.264 encoding supported")

# Check system resources
resources = capabilities['system_resources']
if resources['cpu_usage'] > 80:
    print("⚠️ High CPU usage, consider reducing concurrent operations")

# Validate file size limits
max_size = capabilities['limits']['max_file_size']
print(f"Maximum file size: {max_size}")
```

## 🔧 Resource Usage Patterns

### Batch File Processing
```python
async def process_all_videos():
    # Get list of all videos
    video_list = await session.read_resource("videos://list")
    
    for video in video_list['videos']:
        # Get detailed metadata
        metadata = await session.read_resource(f"videos://{video['name']}/metadata")
        
        # Process based on properties
        video_props = metadata['video_properties']
        if video_props['width'] > 1920:
            # Downscale 4K videos
            await session.call_tool("resize_video", {
                "input_path": video['name'],
                "output_path": f"processed_{video['name']}",
                "width": 1920,
                "height": 1080
            })
```

### Workspace Monitoring
```python
async def monitor_workspace():
    # Get current video list
    current_videos = await session.read_resource("videos://list")
    
    # Check capabilities
    capabilities = await session.read_resource("tools://capabilities")
    max_size = capabilities['limits']['max_file_size']
    
    # Validate each video
    for video in current_videos['videos']:
        if video['size'] > max_size:
            print(f"⚠️ {video['name']} exceeds size limit")
        
        # Check metadata for quality issues
        metadata = await session.read_resource(f"videos://{video['name']}/metadata")
        quality = metadata['quality_metrics']['estimated_quality']
        if quality == 'low':
            print(f"⚠️ {video['name']} has low quality")
```

### Workflow Optimization
```python
async def optimize_workflow(video_name: str):
    # Get video metadata
    metadata = await session.read_resource(f"videos://{video_name}/metadata")
    
    # Get advanced tool info
    advanced_info = await session.read_resource("tools://advanced")
    
    # Determine optimal workflow based on video properties
    video_props = metadata['video_properties']
    
    if video_props['duration'] > 300:  # 5+ minutes
        workflow = advanced_info['workflow_patterns']['basic_editing']
    else:
        workflow = advanced_info['workflow_patterns']['professional_grading']
    
    print(f"Recommended workflow: {workflow['description']}")
    return workflow['steps']
```

## 📊 Performance Considerations

### Resource Caching
Resources are cached for performance:
- **`videos://list`**: Cached for 30 seconds
- **`videos://{filename}/metadata`**: Cached for 5 minutes
- **`tools://capabilities`**: Updated in real-time

### Rate Limiting
- Maximum 10 resource requests per second
- Metadata requests are more expensive than list requests
- Use batch patterns when possible

### Error Handling
```python
try:
    video_list = await session.read_resource("videos://list")
except Exception as e:
    if "not found" in str(e):
        print("No videos found in working directory")
    elif "permission" in str(e):
        print("Permission denied accessing video directory")
    else:
        print(f"Unexpected error: {e}")
```

## 🎯 Next Steps

Learn more about using resources effectively:

- **[Tool Signatures](/api/tool-signatures/)** - Complete API reference
- **[Common Workflows](/guides/common-workflows/)** - Practical usage examples
- **[Batch Processing](/guides/batch-processing/)** - Efficient batch operations
- **[Performance Tips](/support/performance/)** - Optimization techniques

---

**Questions about resources?** Check our [FAQ](/support/faq/) or explore the [troubleshooting guide](/support/troubleshooting/).