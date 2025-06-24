---
title: Tools Overview
description: Complete overview of all 35+ video editing tools available in the VFX MCP Server
---

# Tools Overview

The VFX MCP Server provides **35+ professional video editing tools** organized into logical categories. Each tool is designed for specific video manipulation tasks and can be used individually or combined for complex workflows.

## 🎯 Tool Categories

<div class="tool-category-grid">
  <div class="tool-category-card">
    <h3>Basic Operations <span class="tool-count">4 tools</span></h3>
    <p>Essential video manipulation functions for common editing tasks.</p>
    <ul>
      <li><code>trim_video</code> - Extract video segments</li>
      <li><code>get_video_info</code> - Retrieve video metadata</li>
      <li><code>resize_video</code> - Change video resolution</li>
      <li><code>concatenate_videos</code> - Join multiple videos</li>
    </ul>
    <a href="/tools/basic-operations/">View Details →</a>
  </div>
  
  <div class="tool-category-card">
    <h3>Audio Processing <span class="tool-count">4 tools</span></h3>
    <p>Complete audio manipulation and visualization capabilities.</p>
    <ul>
      <li><code>extract_audio</code> - Extract audio tracks</li>
      <li><code>add_audio</code> - Add or replace audio</li>
      <li><code>extract_audio_spectrum</code> - Audio visualization</li>
      <li><code>merge_audio_tracks</code> - Merge multiple audio tracks</li>
    </ul>
    <a href="/tools/audio-processing/">View Details →</a>
  </div>
  
  <div class="tool-category-card">
    <h3>Effects & Filters <span class="tool-count">5 tools</span></h3>
    <p>Professional-grade enhancement and visual effects.</p>
    <ul>
      <li><code>apply_filter</code> - Custom FFmpeg filters</li>
      <li><code>change_speed</code> - Speed adjustment</li>
      <li><code>apply_color_grading</code> - Color correction</li>
      <li><code>apply_motion_blur</code> - Motion blur effects</li>
      <li><code>apply_video_stabilization</code> - Stabilization</li>
    </ul>
    <a href="/tools/effects-filters/">View Details →</a>
  </div>
  
  <div class="tool-category-card">
    <h3>Format Conversion <span class="tool-count">2 tools</span></h3>
    <p>File format and media conversion utilities.</p>
    <ul>
      <li><code>generate_thumbnail</code> - Extract video frames</li>
      <li><code>convert_format</code> - Format conversion</li>
    </ul>
    <a href="/tools/format-conversion/">View Details →</a>
  </div>
  
  <div class="tool-category-card">
    <h3>Advanced Operations <span class="tool-count">10 tools</span></h3>
    <p>Sophisticated video production and composition tools.</p>
    <ul>
      <li><code>create_video_slideshow</code> - Image slideshows</li>
      <li><code>create_video_mosaic</code> - Multi-video layouts</li>
      <li><code>create_picture_in_picture</code> - PiP overlays</li>
      <li><code>create_time_lapse</code> - Time-lapse effects</li>
      <li><code>create_video_transitions</code> - Smooth transitions</li>
      <li>+ 5 more advanced tools</li>
    </ul>
    <a href="/tools/advanced-operations/">View Details →</a>
  </div>
  
  <div class="tool-category-card">
    <h3>Analysis & Extraction <span class="tool-count">4 tools</span></h3>
    <p>Video analysis and content extraction capabilities.</p>
    <ul>
      <li><code>extract_frames</code> - Frame extraction</li>
      <li><code>detect_scene_changes</code> - Scene detection</li>
      <li><code>extract_video_statistics</code> - Technical analysis</li>
      <li><code>extract_dominant_colors</code> - Color analysis</li>
    </ul>
    <a href="/tools/analysis-extraction/">View Details →</a>
  </div>
  
  <div class="tool-category-card">
    <h3>Text & Graphics <span class="tool-count">2 tools</span></h3>
    <p>Text overlay and animation capabilities.</p>
    <ul>
      <li><code>add_text_overlay</code> - Text overlays</li>
      <li><code>create_animated_text</code> - Animated text</li>
    </ul>
    <a href="/tools/text-graphics/">View Details →</a>
  </div>
  
  <div class="tool-category-card">
    <h3>Specialized Effects <span class="tool-count">4 tools</span></h3>
    <p>Professional VFX and cinematic effects.</p>
    <ul>
      <li><code>create_green_screen_effect</code> - Chroma key</li>
      <li><code>create_particle_system</code> - Particle effects</li>
      <li><code>apply_3d_transforms</code> - 3D transforms</li>
      <li><code>apply_lens_effects</code> - Lens simulation</li>
    </ul>
    <a href="/tools/specialized-effects/">View Details →</a>
  </div>
</div>

## 🔧 Common Tool Patterns

### Input/Output Pattern
All tools follow a consistent pattern:
```python
tool_name(
    input_path: str,        # Source video file
    output_path: str,       # Destination file
    # Tool-specific parameters...
    ctx: Context = None     # Optional progress reporting
)
```

### Progress Reporting
Tools support optional context for progress updates:
```python
await session.call_tool("trim_video", {
    "input_path": "long_video.mp4",
    "output_path": "trimmed.mp4", 
    "start_time": 0,
    "duration": 60
    # Progress updates will be streamed back
})
```

### Error Handling
All tools provide comprehensive error handling:
- **Input validation**: File existence and format checks
- **FFmpeg errors**: Detailed error messages with suggestions
- **Resource management**: Automatic cleanup of temporary files

## 📊 Resource Endpoints

In addition to tools, the server provides resource endpoints for file discovery:

### `videos://list`
Lists all video files in the current working directory:
```json
{
  "videos": [
    {
      "name": "sample.mp4",
      "size": "15.2 MB", 
      "duration": 45.3,
      "resolution": "1920x1080"
    }
  ]
}
```

### `videos://{filename}/metadata`
Returns detailed metadata for a specific video:
```json
{
  "format": "mp4",
  "duration": 45.3,
  "width": 1920,
  "height": 1080,
  "fps": 30.0,
  "video_codec": "h264",
  "audio_codec": "aac",
  "bitrate": 2500000,
  "file_size": "15.2 MB"
}
```

### `tools://advanced`
Provides information about advanced tool capabilities and usage patterns.

## 🎬 Tool Usage Philosophy

### Single Responsibility
Each tool has a focused purpose:
- **Basic tools** handle fundamental operations
- **Advanced tools** combine multiple operations
- **Analysis tools** extract information without modification

### Composability
Tools are designed to work together:
```python
# Extract → Process → Combine workflow
extract_frames("video.mp4", "frames/")
# Process frames individually
create_video_slideshow("frames/", "processed.mp4")
```

### Performance Optimization
- **Copy mode**: Tools use FFmpeg copy when possible (no re-encoding)
- **Chunked processing**: Large files are processed in manageable chunks
- **Concurrent operations**: Multi-threaded processing where applicable

## 🚀 Getting Started with Tools

### 1. Basic Video Info
```python
# Always start by understanding your video
info = await session.call_tool("get_video_info", {
    "video_path": "input.mp4"
})
```

### 2. Simple Edits
```python
# Trim to essential content
result = await session.call_tool("trim_video", {
    "input_path": "input.mp4",
    "output_path": "trimmed.mp4",
    "start_time": 10,
    "duration": 60
})
```

### 3. Enhancement
```python
# Apply color grading for better visuals
result = await session.call_tool("apply_color_grading", {
    "input_path": "trimmed.mp4",
    "output_path": "enhanced.mp4",
    "brightness": 0.1,
    "contrast": 1.2,
    "saturation": 1.1
})
```

### 4. Advanced Composition
```python
# Create picture-in-picture effect
result = await session.call_tool("create_picture_in_picture", {
    "main_video": "enhanced.mp4",
    "overlay_video": "webcam.mp4", 
    "output_path": "final.mp4",
    "position": "top-right",
    "scale": 0.3
})
```

## 📚 Next Steps

Ready to dive deeper? Explore the detailed documentation for each tool category:

<div class="feature-grid">
  <div class="feature-item">
    <h4><a href="/tools/basic-operations/">Basic Operations</a></h4>
    <p>Start with essential video editing functions</p>
  </div>
  
  <div class="feature-item">
    <h4><a href="/tools/advanced-operations/">Advanced Operations</a></h4>
    <p>Complex video composition and effects</p>
  </div>
  
  <div class="feature-item">
    <h4><a href="/guides/common-workflows/">Common Workflows</a></h4>
    <p>Learn typical video editing patterns</p>
  </div>
  
  <div class="feature-item">
    <h4><a href="/api/tool-signatures/">API Reference</a></h4>
    <p>Complete technical documentation</p>
  </div>
</div>

---

**Questions about specific tools?** Each category page includes detailed examples, parameter references, and use case scenarios.