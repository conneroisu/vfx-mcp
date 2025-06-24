---
title: Basic Operations
description: Essential video editing tools for fundamental operations
---

The basic operations provide the foundation for all video editing workflows. These four essential tools handle the most common video manipulation tasks with optimized performance and comprehensive error handling.

## 🎬 Available Tools

### `trim_video`
Extract specific segments from video files with precise timing control.

<div class="tool-signature">

```python
trim_video(
    input_path: str,
    output_path: str, 
    start_time: float,
    duration: float = None,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the trimmed output video</td></tr>
<tr><td>start_time</td><td>float</td><td>Start time in seconds</td></tr>
<tr><td>duration</td><td>float</td><td>Duration in seconds (optional, trims to end if not specified)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Extract first 30 seconds
result = await session.call_tool("trim_video", {
    "input_path": "long_video.mp4",
    "output_path": "intro.mp4",
    "start_time": 0,
    "duration": 30
})

# Extract middle section (30s to 90s)
result = await session.call_tool("trim_video", {
    "input_path": "presentation.mp4", 
    "output_path": "main_content.mp4",
    "start_time": 30,
    "duration": 60
})

# Trim from 2 minutes to end
result = await session.call_tool("trim_video", {
    "input_path": "meeting.mp4",
    "output_path": "discussion.mp4", 
    "start_time": 120
    # No duration = trim to end
})
```

**Performance Notes:**
- Uses FFmpeg copy mode when possible (no re-encoding)
- Very fast for supported formats (H.264, H.265)
- Automatically preserves audio synchronization

---

### `get_video_info`
Retrieve comprehensive metadata about video files.

<div class="tool-signature">

```python
get_video_info(
    video_path: str,
    ctx: Context = None
) -> dict
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>video_path</td><td>str</td><td>Path to the video file to analyze</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Returns:**
```json
{
  "format": "mp4",
  "duration": 125.5,
  "width": 1920,
  "height": 1080, 
  "fps": 30.0,
  "video_codec": "h264",
  "audio_codec": "aac",
  "bitrate": 5000000,
  "file_size": "78.5 MB",
  "has_audio": true,
  "creation_time": "2024-01-15T10:30:00Z"
}
```

**Example Usage:**
```python
# Get basic video information
info = await session.call_tool("get_video_info", {
    "video_path": "sample.mp4"
})

print(f"Duration: {info['duration']} seconds")
print(f"Resolution: {info['width']}x{info['height']}")
print(f"Codec: {info['video_codec']}")
print(f"File size: {info['file_size']}")

# Check if video has audio before processing
if info['has_audio']:
    # Process with audio considerations
    pass
else:
    # Video-only processing
    pass
```

**Use Cases:**
- **Pre-processing validation**: Check video compatibility
- **Workflow planning**: Determine processing requirements
- **Quality assessment**: Analyze video specifications
- **File organization**: Sort videos by properties

---

### `resize_video`
Change video resolution with multiple sizing options and quality control.

<div class="tool-signature">

```python
resize_video(
    input_path: str,
    output_path: str,
    width: int = None,
    height: int = None, 
    scale_factor: float = None,
    maintain_aspect: bool = True,
    quality: str = "medium",
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the resized output video</td></tr>
<tr><td>width</td><td>int</td><td>Target width in pixels (optional)</td></tr>
<tr><td>height</td><td>int</td><td>Target height in pixels (optional)</td></tr>
<tr><td>scale_factor</td><td>float</td><td>Scaling factor (e.g., 0.5 for half size)</td></tr>
<tr><td>maintain_aspect</td><td>bool</td><td>Whether to maintain aspect ratio (default: true)</td></tr>
<tr><td>quality</td><td>str</td><td>Encoding quality: "low", "medium", "high", "ultra"</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Resize to specific dimensions (maintaining aspect ratio)
result = await session.call_tool("resize_video", {
    "input_path": "4k_video.mp4",
    "output_path": "1080p_video.mp4", 
    "width": 1920,
    "height": 1080,
    "quality": "high"
})

# Scale by factor
result = await session.call_tool("resize_video", {
    "input_path": "large_video.mp4",
    "output_path": "compressed.mp4",
    "scale_factor": 0.5,
    "quality": "medium"
})

# Set width only (auto-calculate height)
result = await session.call_tool("resize_video", {
    "input_path": "portrait.mp4",
    "output_path": "web_optimized.mp4",
    "width": 1280,
    "maintain_aspect": True
})
```

**Common Resolutions:**
- **4K**: 3840x2160
- **1080p**: 1920x1080  
- **720p**: 1280x720
- **480p**: 854x480
- **360p**: 640x360

**Quality Settings:**
- **ultra**: Highest quality, larger file size
- **high**: High quality, good for final output
- **medium**: Balanced quality/size (default)
- **low**: Smaller files, lower quality

---

### `concatenate_videos`
Join multiple video files into a single output file with seamless transitions.

<div class="tool-signature">

```python
concatenate_videos(
    input_paths: list[str],
    output_path: str,
    transition_duration: float = 0.0,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_paths</td><td>list[str]</td><td>List of video file paths to concatenate</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the concatenated output video</td></tr>
<tr><td>transition_duration</td><td>float</td><td>Crossfade transition duration in seconds (default: 0)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Simple concatenation without transitions
result = await session.call_tool("concatenate_videos", {
    "input_paths": [
        "intro.mp4", 
        "main_content.mp4",
        "outro.mp4"
    ],
    "output_path": "complete_video.mp4"
})

# Concatenation with crossfade transitions
result = await session.call_tool("concatenate_videos", {
    "input_paths": [
        "scene1.mp4",
        "scene2.mp4", 
        "scene3.mp4"
    ],
    "output_path": "smooth_movie.mp4",
    "transition_duration": 1.0  # 1 second crossfades
})

# Concatenate with different resolutions (auto-normalized)
result = await session.call_tool("concatenate_videos", {
    "input_paths": [
        "mobile_clip.mp4",    # 720p
        "camera_clip.mp4",    # 1080p  
        "drone_clip.mp4"      # 4K
    ],
    "output_path": "mixed_sources.mp4"
})
```

**Important Notes:**
- **Format compatibility**: All videos should have compatible formats
- **Resolution handling**: Videos with different resolutions are automatically normalized
- **Audio synchronization**: Audio tracks are properly aligned
- **Order matters**: Videos are concatenated in the order provided

## 🔧 Advanced Usage Patterns

### Batch Processing
```python
# Process multiple videos with basic operations
video_files = ["clip1.mp4", "clip2.mp4", "clip3.mp4"]

for i, video in enumerate(video_files):
    # Get info for each video
    info = await session.call_tool("get_video_info", {
        "video_path": video
    })
    
    # Trim to first minute
    await session.call_tool("trim_video", {
        "input_path": video,
        "output_path": f"trimmed_{i}.mp4",
        "start_time": 0,
        "duration": 60
    })
    
    # Resize to 720p
    await session.call_tool("resize_video", {
        "input_path": f"trimmed_{i}.mp4", 
        "output_path": f"final_{i}.mp4",
        "width": 1280,
        "height": 720
    })
```

### Quality Control Workflow
```python
# Analyze video before processing
info = await session.call_tool("get_video_info", {
    "video_path": "source.mp4"
})

# Determine processing strategy based on properties
if info['width'] > 1920:
    # Downscale 4K content
    resize_params = {"width": 1920, "height": 1080, "quality": "high"}
elif info['bitrate'] > 10000000:
    # High bitrate optimization
    resize_params = {"scale_factor": 1.0, "quality": "medium"}
else:
    # Keep original quality
    resize_params = {"scale_factor": 1.0, "quality": "ultra"}

await session.call_tool("resize_video", {
    "input_path": "source.mp4",
    "output_path": "optimized.mp4",
    **resize_params
})
```

## 📊 Performance Considerations

### Optimization Tips

1. **Use copy mode when possible**:
   - Trimming without re-encoding is fastest
   - Same codec/container = optimal performance

2. **Batch similar operations**:
   - Group resizing operations
   - Process videos with similar properties together

3. **Choose appropriate quality settings**:
   - "medium" for most use cases
   - "high" for final output
   - "low" for previews and drafts

4. **Monitor file sizes**:
   - Check output sizes with `get_video_info`
   - Adjust quality settings as needed

### Error Handling

All basic operations include comprehensive error handling:

```python
try:
    result = await session.call_tool("trim_video", {
        "input_path": "missing_file.mp4",
        "output_path": "output.mp4", 
        "start_time": 0,
        "duration": 30
    })
except Exception as e:
    if "No such file" in str(e):
        print("Input file not found")
    elif "Invalid time" in str(e):
        print("Start time or duration invalid")
    else:
        print(f"Unexpected error: {e}")
```

## 🎯 Next Steps

Now that you understand the basic operations, explore more advanced capabilities:

- **[Audio Processing](/tools/audio-processing/)** - Extract, mix, and enhance audio
- **[Effects & Filters](/tools/effects-filters/)** - Apply professional enhancements
- **[Advanced Operations](/tools/advanced-operations/)** - Complex video composition
- **[Common Workflows](/guides/common-workflows/)** - Typical editing patterns

---

**Need help with a specific basic operation?** Check our [FAQ](/support/faq/) or [examples section](/examples/basic-editing/).