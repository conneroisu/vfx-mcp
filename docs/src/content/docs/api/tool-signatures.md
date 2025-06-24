---
title: Tool Signatures
description: Complete API reference for all VFX MCP Server tools with function signatures and parameters
---

This page provides the complete API reference for all 35+ tools available in the VFX MCP Server. Each tool signature includes parameters, types, default values, and return types.

## 🏷️ Type Definitions

### Common Types
```python
Context = Optional[MCP Context object for progress reporting]
PathStr = str  # File path (absolute or relative to working directory)
QualityLevel = Literal["low", "medium", "high", "ultra"]
VideoFormat = Literal["mp4", "avi", "mov", "mkv", "webm"]
AudioFormat = Literal["mp3", "wav", "aac", "flac"]
```

---

## 📹 Basic Operations

### `trim_video`
Extract specific segments from video files.

```python
def trim_video(
    input_path: PathStr,
    output_path: PathStr,
    start_time: float,
    duration: Optional[float] = None,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output trimmed video path
- `start_time`: Start time in seconds
- `duration`: Duration in seconds (optional, trims to end if not specified)
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `get_video_info`
Retrieve comprehensive video metadata.

```python
def get_video_info(
    video_path: PathStr,
    ctx: Context = None
) -> Dict[str, Any]
```

**Parameters:**
- `video_path`: Path to video file to analyze
- `ctx`: Optional progress reporting context

**Returns:** Dictionary with video metadata:
```python
{
    "format": str,
    "duration": float,
    "width": int,
    "height": int,
    "fps": float,
    "video_codec": str,
    "audio_codec": str,
    "bitrate": int,
    "file_size": str,
    "has_audio": bool
}
```

---

### `resize_video`
Change video resolution with quality control.

```python
def resize_video(
    input_path: PathStr,
    output_path: PathStr,
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale_factor: Optional[float] = None,
    maintain_aspect: bool = True,
    quality: QualityLevel = "medium",
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output resized video path
- `width`: Target width in pixels (optional)
- `height`: Target height in pixels (optional)
- `scale_factor`: Scaling factor (e.g., 0.5 for half size)
- `maintain_aspect`: Whether to maintain aspect ratio
- `quality`: Encoding quality level
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `concatenate_videos`
Join multiple video files seamlessly.

```python
def concatenate_videos(
    input_paths: List[PathStr],
    output_path: PathStr,
    transition_duration: float = 0.0,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_paths`: List of video file paths to concatenate
- `output_path`: Output concatenated video path
- `transition_duration`: Crossfade transition duration in seconds
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

## 🎵 Audio Processing

### `extract_audio`
Extract audio tracks from video files.

```python
def extract_audio(
    input_path: PathStr,
    output_path: PathStr,
    format: AudioFormat = "mp3",
    quality: QualityLevel = "medium",
    sample_rate: Optional[int] = None,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output audio file path
- `format`: Output audio format
- `quality`: Audio quality level
- `sample_rate`: Target sample rate in Hz (optional)
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `add_audio`
Add or replace audio tracks in videos.

```python
def add_audio(
    video_path: PathStr,
    audio_path: PathStr,
    output_path: PathStr,
    mode: Literal["replace", "mix"] = "replace",
    volume: float = 1.0,
    audio_offset: float = 0.0,
    fade_in: float = 0.0,
    fade_out: float = 0.0,
    ctx: Context = None
) -> str
```

**Parameters:**
- `video_path`: Source video file path
- `audio_path`: Audio file to add
- `output_path`: Output video with new audio
- `mode`: "replace" or "mix" audio mode
- `volume`: Volume multiplier (1.0 = original)
- `audio_offset`: Audio delay in seconds
- `fade_in`: Fade-in duration in seconds
- `fade_out`: Fade-out duration in seconds
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `extract_audio_spectrum`
Generate visual audio spectrum videos.

```python
def extract_audio_spectrum(
    input_path: PathStr,
    output_path: PathStr,
    visualization_type: Literal["spectrum", "waveform", "bars", "circle"] = "spectrum",
    width: int = 1920,
    height: int = 1080,
    color_scheme: Literal["rainbow", "fire", "cool", "mono"] = "rainbow",
    sensitivity: float = 1.0,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video or audio file path
- `output_path`: Output visualization video path
- `visualization_type`: Type of audio visualization
- `width`: Output video width in pixels
- `height`: Output video height in pixels
- `color_scheme`: Color scheme for visualization
- `sensitivity`: Audio sensitivity multiplier
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `merge_audio_tracks`
Merge multiple audio tracks with timing control.

```python
def merge_audio_tracks(
    input_paths: List[PathStr],
    output_path: PathStr,
    volumes: Optional[List[float]] = None,
    delays: Optional[List[float]] = None,
    crossfade_duration: float = 0.0,
    output_format: AudioFormat = "mp3",
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_paths`: List of audio file paths to merge
- `output_path`: Output merged audio file path
- `volumes`: Volume levels for each track (defaults to 1.0)
- `delays`: Delay in seconds for each track (defaults to 0.0)
- `crossfade_duration`: Crossfade duration between tracks
- `output_format`: Output audio format
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

## 🎨 Effects & Filters

### `apply_filter`
Apply custom FFmpeg filters.

```python
def apply_filter(
    input_path: PathStr,
    output_path: PathStr,
    filter_string: str,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output filtered video path
- `filter_string`: FFmpeg filter expression
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `change_speed`
Adjust video playback speed.

```python
def change_speed(
    input_path: PathStr,
    output_path: PathStr,
    speed_factor: float,
    preserve_audio: bool = True,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output speed-adjusted video path
- `speed_factor`: Speed multiplier (0.5 = half speed, 2.0 = double speed)
- `preserve_audio`: Whether to maintain audio pitch
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `apply_color_grading`
Professional color correction and grading.

```python
def apply_color_grading(
    input_path: PathStr,
    output_path: PathStr,
    brightness: float = 0.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    gamma: float = 1.0,
    temperature: float = 0.0,
    tint: float = 0.0,
    shadows: float = 0.0,
    highlights: float = 0.0,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output color-graded video path
- `brightness`: Brightness adjustment (-1.0 to 1.0)
- `contrast`: Contrast multiplier (0.0 to 3.0)
- `saturation`: Saturation multiplier (0.0 to 3.0)
- `gamma`: Gamma correction (0.1 to 3.0)
- `temperature`: Color temperature (-1.0 warm to 1.0 cool)
- `tint`: Green/magenta tint (-1.0 to 1.0)
- `shadows`: Shadow adjustment (-1.0 to 1.0)
- `highlights`: Highlight adjustment (-1.0 to 1.0)
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `apply_motion_blur`
Add realistic motion blur effects.

```python
def apply_motion_blur(
    input_path: PathStr,
    output_path: PathStr,
    angle: float = 0.0,
    distance: float = 5.0,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output motion-blurred video path
- `angle`: Blur direction in degrees (0-360)
- `distance`: Blur distance in pixels
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `apply_video_stabilization`
Advanced video stabilization.

```python
def apply_video_stabilization(
    input_path: PathStr,
    output_path: PathStr,
    smoothing: float = 10.0,
    crop_black: bool = True,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source shaky video file path
- `output_path`: Output stabilized video path
- `smoothing`: Smoothing strength (1.0 to 100.0)
- `crop_black`: Whether to crop black borders
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

## 🔄 Format Conversion

### `generate_thumbnail`
Extract video frames as image thumbnails.

```python
def generate_thumbnail(
    input_path: PathStr,
    output_path: PathStr,
    timestamp: float = 0.0,
    width: Optional[int] = None,
    height: Optional[int] = None,
    format: Literal["jpg", "png", "bmp"] = "jpg",
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output thumbnail image path
- `timestamp`: Time in seconds to extract frame
- `width`: Thumbnail width in pixels (optional)
- `height`: Thumbnail height in pixels (optional)
- `format`: Output image format
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `convert_format`
Convert between video formats.

```python
def convert_format(
    input_path: PathStr,
    output_path: PathStr,
    video_codec: Optional[str] = None,
    audio_codec: Optional[str] = None,
    bitrate: Optional[str] = None,
    quality: QualityLevel = "medium",
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output converted video path
- `video_codec`: Target video codec (e.g., "libx264", "libx265")
- `audio_codec`: Target audio codec (e.g., "aac", "mp3")
- `bitrate`: Target bitrate (e.g., "2M", "500k")
- `quality`: Encoding quality level
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

## 🎬 Advanced Operations

### `create_video_slideshow`
Generate slideshows from images.

```python
def create_video_slideshow(
    image_folder: PathStr,
    output_path: PathStr,
    duration_per_image: float = 3.0,
    transition_duration: float = 1.0,
    fps: int = 30,
    resolution: str = "1920x1080",
    ctx: Context = None
) -> str
```

**Parameters:**
- `image_folder`: Directory containing images
- `output_path`: Output slideshow video path
- `duration_per_image`: Display time per image in seconds
- `transition_duration`: Transition duration between images
- `fps`: Frame rate of output video
- `resolution`: Output resolution (e.g., "1920x1080")
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `create_video_mosaic`
Create multi-video grid layouts.

```python
def create_video_mosaic(
    input_paths: List[PathStr],
    output_path: PathStr,
    layout: str = "2x2",
    width: int = 1920,
    height: int = 1080,
    border_width: int = 2,
    border_color: str = "black",
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_paths`: List of video file paths for mosaic
- `output_path`: Output mosaic video path
- `layout`: Grid layout (e.g., "2x2", "3x1", "4x2")
- `width`: Output video width
- `height`: Output video height
- `border_width`: Border width between videos in pixels
- `border_color`: Border color name or hex code
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `create_picture_in_picture`
Create picture-in-picture overlays.

```python
def create_picture_in_picture(
    main_video: PathStr,
    overlay_video: PathStr,
    output_path: PathStr,
    position: str = "top-right",
    scale: float = 0.25,
    opacity: float = 1.0,
    x_offset: int = 10,
    y_offset: int = 10,
    ctx: Context = None
) -> str
```

**Parameters:**
- `main_video`: Main background video path
- `overlay_video`: Overlay video path
- `output_path`: Output picture-in-picture video path
- `position`: Overlay position ("top-left", "top-right", "bottom-left", "bottom-right", "center")
- `scale`: Overlay scale factor (0.1 to 1.0)
- `opacity`: Overlay opacity (0.0 to 1.0)
- `x_offset`: Horizontal offset from position in pixels
- `y_offset`: Vertical offset from position in pixels
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

## 📊 Analysis & Extraction

### `extract_frames`
Extract individual frames as images.

```python
def extract_frames(
    input_path: PathStr,
    output_directory: PathStr,
    interval: float = 1.0,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    format: Literal["jpg", "png", "bmp"] = "jpg",
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_directory`: Directory to save extracted frames
- `interval`: Time interval between frames in seconds
- `start_time`: Start time for extraction in seconds
- `end_time`: End time for extraction in seconds (optional)
- `format`: Output image format
- `ctx`: Optional progress reporting context

**Returns:** Success message with frame count and directory

---

### `detect_scene_changes`
Automatic scene change detection.

```python
def detect_scene_changes(
    input_path: PathStr,
    sensitivity: float = 0.3,
    min_scene_duration: float = 1.0,
    output_format: Literal["json", "csv", "txt"] = "json",
    ctx: Context = None
) -> Dict[str, Any]
```

**Parameters:**
- `input_path`: Source video file path
- `sensitivity`: Detection sensitivity (0.1 to 1.0)
- `min_scene_duration`: Minimum scene duration in seconds
- `output_format`: Format for scene data export
- `ctx`: Optional progress reporting context

**Returns:** Dictionary with scene change timestamps and metadata

---

### `extract_video_statistics`
Comprehensive technical analysis.

```python
def extract_video_statistics(
    input_path: PathStr,
    include_quality_metrics: bool = True,
    include_motion_analysis: bool = False,
    ctx: Context = None
) -> Dict[str, Any]
```

**Parameters:**
- `input_path`: Source video file path
- `include_quality_metrics`: Whether to calculate quality metrics
- `include_motion_analysis`: Whether to analyze motion patterns
- `ctx`: Optional progress reporting context

**Returns:** Dictionary with comprehensive video statistics

---

### `extract_dominant_colors`
Color palette analysis for videos.

```python
def extract_dominant_colors(
    input_path: PathStr,
    num_colors: int = 5,
    sample_interval: float = 5.0,
    output_format: Literal["json", "image"] = "json",
    ctx: Context = None
) -> Dict[str, Any]
```

**Parameters:**
- `input_path`: Source video file path
- `num_colors`: Number of dominant colors to extract
- `sample_interval`: Sampling interval in seconds
- `output_format`: Output format for color data
- `ctx`: Optional progress reporting context

**Returns:** Dictionary with dominant colors and usage statistics

---

## 📝 Text & Graphics

### `add_text_overlay`
Add text overlays to videos.

```python
def add_text_overlay(
    input_path: PathStr,
    output_path: PathStr,
    text: str,
    font_size: int = 24,
    font_color: str = "white",
    position: str = "center",
    x_offset: int = 0,
    y_offset: int = 0,
    start_time: float = 0.0,
    duration: Optional[float] = None,
    background_color: Optional[str] = None,
    font_family: str = "Arial",
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output video with text overlay
- `text`: Text content to overlay
- `font_size`: Font size in points
- `font_color`: Text color name or hex code
- `position`: Text position ("top", "center", "bottom", "top-left", etc.)
- `x_offset`: Horizontal offset from position
- `y_offset`: Vertical offset from position
- `start_time`: When text appears in seconds
- `duration`: How long text appears (optional, full video if not specified)
- `background_color`: Background color for text (optional)
- `font_family`: Font family name
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `create_animated_text`
Create animated text effects.

```python
def create_animated_text(
    output_path: PathStr,
    text: str,
    animation_type: Literal["fade_in", "slide_in", "typewriter", "bounce"] = "fade_in",
    duration: float = 5.0,
    font_size: int = 48,
    font_color: str = "white",
    background_color: str = "black",
    width: int = 1920,
    height: int = 1080,
    ctx: Context = None
) -> str
```

**Parameters:**
- `output_path`: Output animated text video path
- `text`: Text content to animate
- `animation_type`: Type of text animation
- `duration`: Total animation duration in seconds
- `font_size`: Font size in points
- `font_color`: Text color name or hex code
- `background_color`: Background color name or hex code
- `width`: Output video width
- `height`: Output video height
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

## 🎭 Specialized Effects

### `create_green_screen_effect`
Chroma key compositing.

```python
def create_green_screen_effect(
    foreground_path: PathStr,
    background_path: PathStr,
    output_path: PathStr,
    key_color: str = "green",
    threshold: float = 0.3,
    smoothing: float = 0.1,
    spill_suppression: float = 0.1,
    ctx: Context = None
) -> str
```

**Parameters:**
- `foreground_path`: Video with green/blue screen
- `background_path`: Background video or image
- `output_path`: Output composited video
- `key_color`: Color to key out ("green", "blue", or hex code)
- `threshold`: Keying threshold (0.0 to 1.0)
- `smoothing`: Edge smoothing amount
- `spill_suppression`: Color spill suppression
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `create_particle_system`
Generate particle effects.

```python
def create_particle_system(
    output_path: PathStr,
    particle_type: Literal["snow", "rain", "sparks", "smoke"] = "snow",
    intensity: float = 1.0,
    duration: float = 10.0,
    width: int = 1920,
    height: int = 1080,
    background_color: str = "black",
    ctx: Context = None
) -> str
```

**Parameters:**
- `output_path`: Output particle effect video path
- `particle_type`: Type of particle system
- `intensity`: Particle density/intensity (0.1 to 5.0)
- `duration`: Effect duration in seconds
- `width`: Output video width
- `height`: Output video height
- `background_color`: Background color (transparent if "none")
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `apply_3d_transforms`
Apply 3D perspective transforms.

```python
def apply_3d_transforms(
    input_path: PathStr,
    output_path: PathStr,
    rotation_x: float = 0.0,
    rotation_y: float = 0.0,
    rotation_z: float = 0.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    perspective: float = 0.0,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output transformed video path
- `rotation_x`: X-axis rotation in degrees
- `rotation_y`: Y-axis rotation in degrees
- `rotation_z`: Z-axis rotation in degrees
- `scale_x`: X-axis scale factor
- `scale_y`: Y-axis scale factor
- `perspective`: Perspective distortion amount
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

### `apply_lens_effects`
Camera lens simulation effects.

```python
def apply_lens_effects(
    input_path: PathStr,
    output_path: PathStr,
    effect_type: Literal["vignette", "lens_flare", "chromatic_aberration", "barrel_distortion"] = "vignette",
    intensity: float = 0.5,
    center_x: float = 0.5,
    center_y: float = 0.5,
    ctx: Context = None
) -> str
```

**Parameters:**
- `input_path`: Source video file path
- `output_path`: Output video with lens effects
- `effect_type`: Type of lens effect to apply
- `intensity`: Effect intensity (0.0 to 1.0)
- `center_x`: Effect center X coordinate (0.0 to 1.0)
- `center_y`: Effect center Y coordinate (0.0 to 1.0)
- `ctx`: Optional progress reporting context

**Returns:** Success message with output file path

---

## 🔄 Batch Processing

### `batch_process_videos`
Automated batch processing with configurable operations.

```python
def batch_process_videos(
    input_directory: PathStr,
    output_directory: PathStr,
    operations: List[Dict[str, Any]],
    file_pattern: str = "*.mp4",
    overwrite_existing: bool = False,
    ctx: Context = None
) -> Dict[str, Any]
```

**Parameters:**
- `input_directory`: Directory containing input videos
- `output_directory`: Directory for processed videos
- `operations`: List of operations to apply to each video
- `file_pattern`: Glob pattern for input files
- `overwrite_existing`: Whether to overwrite existing output files
- `ctx`: Optional progress reporting context

**Returns:** Dictionary with processing results and statistics

---

## 📋 Usage Examples

### Basic Tool Call Pattern
```python
# Using MCP client
result = await session.call_tool("tool_name", {
    "input_path": "source.mp4",
    "output_path": "output.mp4",
    "parameter1": value1,
    "parameter2": value2
})
```

### Error Handling
```python
try:
    result = await session.call_tool("trim_video", {
        "input_path": "video.mp4",
        "output_path": "trimmed.mp4",
        "start_time": 0,
        "duration": 30
    })
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")
```

### Progress Reporting
Tools that support progress reporting will stream updates when a context is provided:

```python
# Progress updates will be automatically streamed
result = await session.call_tool("apply_color_grading", {
    "input_path": "long_video.mp4",
    "output_path": "graded.mp4",
    "contrast": 1.2,
    "saturation": 1.1
    # Progress updates sent via MCP context
})
```

---

## 🔗 Related Documentation

- **[Tools Overview](/tools/overview/)** - High-level tool categorization
- **[Resource Endpoints](/api/resources/)** - MCP resource API reference
- **[Common Workflows](/guides/common-workflows/)** - Practical usage patterns
- **[Error Handling](/api/error-handling/)** - Error types and handling

---

**Questions about specific tool signatures?** Check the individual [tool category pages](/tools/overview/) for detailed examples and usage scenarios.