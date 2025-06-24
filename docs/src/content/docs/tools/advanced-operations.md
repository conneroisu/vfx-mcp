---
title: Advanced Operations
description: Complex video composition, effects, and advanced production tools
---

The advanced operations category provides sophisticated video production tools for complex composition, effects, and professional video creation workflows. These tools enable you to create professional-quality content with multiple video sources, advanced effects, and automated processing.

## 🎬 Available Tools

### `create_video_slideshow`
Generate dynamic slideshows from image collections with customizable transitions.

<div class="tool-signature">

```python
create_video_slideshow(
    image_folder: str,
    output_path: str,
    duration_per_image: float = 3.0,
    transition_duration: float = 1.0,
    fps: int = 30,
    resolution: str = "1920x1080",
    audio_path: str = None,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>image_folder</td><td>str</td><td>Directory containing images for slideshow</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the output slideshow video</td></tr>
<tr><td>duration_per_image</td><td>float</td><td>Display time per image in seconds (default: 3.0)</td></tr>
<tr><td>transition_duration</td><td>float</td><td>Transition duration between images (default: 1.0)</td></tr>
<tr><td>fps</td><td>int</td><td>Frame rate of output video (default: 30)</td></tr>
<tr><td>resolution</td><td>str</td><td>Output resolution (default: "1920x1080")</td></tr>
<tr><td>audio_path</td><td>str</td><td>Optional background audio file</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Basic slideshow from wedding photos
result = await session.call_tool("create_video_slideshow", {
    "image_folder": "wedding_photos/",
    "output_path": "wedding_slideshow.mp4",
    "duration_per_image": 4.0,
    "transition_duration": 1.5,
    "resolution": "1920x1080"
})

# Slideshow with background music
result = await session.call_tool("create_video_slideshow", {
    "image_folder": "vacation_pics/",
    "output_path": "vacation_memories.mp4",
    "duration_per_image": 3.5,
    "transition_duration": 1.0,
    "audio_path": "background_music.mp3",
    "fps": 30
})

# Quick preview slideshow
result = await session.call_tool("create_video_slideshow", {
    "image_folder": "product_shots/",
    "output_path": "product_preview.mp4",
    "duration_per_image": 2.0,
    "transition_duration": 0.5,
    "resolution": "1280x720"
})
```

**Supported Image Formats:**
- JPG/JPEG
- PNG
- BMP
- TIFF
- WebP

---

### `create_video_mosaic`
Create sophisticated multi-video grid layouts with customizable arrangements.

<div class="tool-signature">

```python
create_video_mosaic(
    input_paths: list[str],
    output_path: str,
    layout: str = "2x2",
    width: int = 1920,
    height: int = 1080,
    border_width: int = 2,
    border_color: str = "black",
    audio_source: str = "mix",
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_paths</td><td>list[str]</td><td>List of video file paths for mosaic</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the output mosaic video</td></tr>
<tr><td>layout</td><td>str</td><td>Grid layout format (e.g., "2x2", "3x1", "4x2")</td></tr>
<tr><td>width</td><td>int</td><td>Output video width in pixels (default: 1920)</td></tr>
<tr><td>height</td><td>int</td><td>Output video height in pixels (default: 1080)</td></tr>
<tr><td>border_width</td><td>int</td><td>Border width between videos in pixels (default: 2)</td></tr>
<tr><td>border_color</td><td>str</td><td>Border color name or hex code (default: "black")</td></tr>
<tr><td>audio_source</td><td>str</td><td>"mix", "first", "none", or index number (default: "mix")</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Security camera grid (2x2)
result = await session.call_tool("create_video_mosaic", {
    "input_paths": [
        "camera1.mp4",
        "camera2.mp4", 
        "camera3.mp4",
        "camera4.mp4"
    ],
    "output_path": "security_grid.mp4",
    "layout": "2x2",
    "border_width": 4,
    "border_color": "white",
    "audio_source": "none"
})

# Comparison layout (1x3)
result = await session.call_tool("create_video_mosaic", {
    "input_paths": [
        "original.mp4",
        "version_a.mp4",
        "version_b.mp4"
    ],
    "output_path": "comparison.mp4",
    "layout": "1x3",
    "width": 1920,
    "height": 640,
    "border_width": 2,
    "audio_source": "first"  # Use audio from first video
})

# Social media split screen (2x1)
result = await session.call_tool("create_video_mosaic", {
    "input_paths": [
        "presenter.mp4",
        "screen_share.mp4"
    ],
    "output_path": "presentation.mp4", 
    "layout": "2x1",
    "width": 1920,
    "height": 1080,
    "border_color": "#333333",
    "audio_source": "mix"
})
```

**Layout Options:**
- **Square**: 2x2, 3x3, 4x4
- **Horizontal**: 1x2, 1x3, 1x4
- **Vertical**: 2x1, 3x1, 4x1
- **Mixed**: 2x3, 3x2, custom arrangements

---

### `create_picture_in_picture`
Create professional picture-in-picture overlays with precise positioning and effects.

<div class="tool-signature">

```python
create_picture_in_picture(
    main_video: str,
    overlay_video: str,
    output_path: str,
    position: str = "top-right",
    scale: float = 0.25,
    opacity: float = 1.0,
    x_offset: int = 10,
    y_offset: int = 10,
    border_width: int = 0,
    border_color: str = "white",
    start_time: float = 0.0,
    duration: float = None,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>main_video</td><td>str</td><td>Main background video path</td></tr>
<tr><td>overlay_video</td><td>str</td><td>Overlay video path (picture-in-picture)</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the output composed video</td></tr>
<tr><td>position</td><td>str</td><td>Overlay position: "top-left", "top-right", "bottom-left", "bottom-right", "center"</td></tr>
<tr><td>scale</td><td>float</td><td>Overlay scale factor (0.1 to 1.0, default: 0.25)</td></tr>
<tr><td>opacity</td><td>float</td><td>Overlay opacity (0.0 to 1.0, default: 1.0)</td></tr>
<tr><td>x_offset</td><td>int</td><td>Horizontal offset from position in pixels (default: 10)</td></tr>
<tr><td>y_offset</td><td>int</td><td>Vertical offset from position in pixels (default: 10)</td></tr>
<tr><td>border_width</td><td>int</td><td>Border width around overlay in pixels (default: 0)</td></tr>
<tr><td>border_color</td><td>str</td><td>Border color name or hex code (default: "white")</td></tr>
<tr><td>start_time</td><td>float</td><td>When overlay appears in seconds (default: 0.0)</td></tr>
<tr><td>duration</td><td>float</td><td>How long overlay appears (optional, full video if not specified)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Webcam overlay for presentation
result = await session.call_tool("create_picture_in_picture", {
    "main_video": "screen_recording.mp4",
    "overlay_video": "webcam_feed.mp4",
    "output_path": "presentation_with_webcam.mp4",
    "position": "bottom-right",
    "scale": 0.2,
    "x_offset": 20,
    "y_offset": 20,
    "border_width": 3,
    "border_color": "#0066cc"
})

# Commentary overlay
result = await session.call_tool("create_picture_in_picture", {
    "main_video": "gameplay.mp4",
    "overlay_video": "commentary.mp4",
    "output_path": "gameplay_with_commentary.mp4",
    "position": "top-left",
    "scale": 0.3,
    "opacity": 0.9,
    "start_time": 5.0,
    "duration": 120.0  # 2 minutes
})

# Centered watermark overlay
result = await session.call_tool("create_picture_in_picture", {
    "main_video": "main_content.mp4",
    "overlay_video": "logo_animation.mp4",
    "output_path": "branded_content.mp4",
    "position": "center",
    "scale": 0.15,
    "opacity": 0.7,
    "start_time": 0.0,
    "duration": 10.0  # Logo appears for first 10 seconds
})
```

---

### `create_time_lapse`
Convert normal-speed footage into dynamic time-lapse videos with stabilization options.

<div class="tool-signature">

```python
create_time_lapse(
    input_path: str,
    output_path: str,
    speed_factor: float = 10.0,
    stabilize: bool = True,
    smoothing: float = 15.0,
    final_fps: int = 30,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Source video file path</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the time-lapse output video</td></tr>
<tr><td>speed_factor</td><td>float</td><td>Speed multiplier (default: 10.0 = 10x faster)</td></tr>
<tr><td>stabilize</td><td>bool</td><td>Whether to apply stabilization (default: True)</td></tr>
<tr><td>smoothing</td><td>float</td><td>Stabilization smoothing strength (default: 15.0)</td></tr>
<tr><td>final_fps</td><td>int</td><td>Output frame rate (default: 30)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Construction time-lapse
result = await session.call_tool("create_time_lapse", {
    "input_path": "construction_8hours.mp4",
    "output_path": "construction_timelapse.mp4",
    "speed_factor": 60.0,  # 60x speed = 8 hours in 8 minutes
    "stabilize": True,
    "smoothing": 20.0,
    "final_fps": 30
})

# Sunset time-lapse
result = await session.call_tool("create_time_lapse", {
    "input_path": "sunset_2hours.mp4",
    "output_path": "sunset_timelapse.mp4",
    "speed_factor": 30.0,  # 30x speed = 2 hours in 4 minutes
    "stabilize": True,
    "smoothing": 10.0
})

# Fast cooking demo
result = await session.call_tool("create_time_lapse", {
    "input_path": "cooking_1hour.mp4",
    "output_path": "cooking_fast.mp4",
    "speed_factor": 15.0,  # 15x speed = 1 hour in 4 minutes
    "stabilize": False,  # No stabilization for handheld cooking video
    "final_fps": 24
})
```

**Speed Factor Guidelines:**
- **2-5x**: Slow activities (painting, gardening)
- **10-20x**: Medium activities (cooking, setup)
- **30-60x**: Long processes (construction, events)
- **100x+**: Very long processes (plant growth, weather)

---

### `create_video_transitions`
Add professional transitions between video clips for seamless storytelling.

<div class="tool-signature">

```python
create_video_transitions(
    input_paths: list[str],
    output_path: str,
    transition_type: str = "crossfade",
    transition_duration: float = 1.0,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_paths</td><td>list[str]</td><td>List of video file paths to connect with transitions</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the output video with transitions</td></tr>
<tr><td>transition_type</td><td>str</td><td>Type of transition: "crossfade", "fade", "slide", "wipe" (default: "crossfade")</td></tr>
<tr><td>transition_duration</td><td>float</td><td>Duration of each transition in seconds (default: 1.0)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Smooth crossfade between scenes
result = await session.call_tool("create_video_transitions", {
    "input_paths": [
        "scene1_intro.mp4",
        "scene2_action.mp4",
        "scene3_conclusion.mp4"
    ],
    "output_path": "smooth_story.mp4",
    "transition_type": "crossfade",
    "transition_duration": 2.0
})

# Quick cuts with fade transitions
result = await session.call_tool("create_video_transitions", {
    "input_paths": [
        "clip1.mp4",
        "clip2.mp4", 
        "clip3.mp4",
        "clip4.mp4"
    ],
    "output_path": "montage.mp4",
    "transition_type": "fade",
    "transition_duration": 0.5
})

# Professional slide transitions
result = await session.call_tool("create_video_transitions", {
    "input_paths": [
        "interview_part1.mp4",
        "broll_footage.mp4",
        "interview_part2.mp4"
    ],
    "output_path": "documentary_sequence.mp4",
    "transition_type": "slide",
    "transition_duration": 1.5
})
```

**Transition Types:**
- **crossfade**: Gradual blend between clips
- **fade**: Fade to black between clips
- **slide**: Sliding motion transition
- **wipe**: Directional wipe effect

---

### `create_loop_video`
Create seamlessly looping videos with automatic crossfade blending.

<div class="tool-signature">

```python
create_loop_video(
    input_path: str,
    output_path: str,
    loop_count: int = 3,
    crossfade_duration: float = 1.0,
    trim_ends: bool = True,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Source video file path</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the looped output video</td></tr>
<tr><td>loop_count</td><td>int</td><td>Number of loops (default: 3)</td></tr>
<tr><td>crossfade_duration</td><td>float</td><td>Crossfade duration between loops in seconds (default: 1.0)</td></tr>
<tr><td>trim_ends</td><td>bool</td><td>Whether to trim start/end for better looping (default: True)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Background loop for presentations
result = await session.call_tool("create_loop_video", {
    "input_path": "abstract_motion.mp4",
    "output_path": "background_loop.mp4",
    "loop_count": 5,
    "crossfade_duration": 2.0,
    "trim_ends": True
})

# Product showcase loop
result = await session.call_tool("create_loop_video", {
    "input_path": "product_rotation.mp4",
    "output_path": "product_loop.mp4",
    "loop_count": 4,
    "crossfade_duration": 0.5,
    "trim_ends": False
})

# Ambient video loop
result = await session.call_tool("create_loop_video", {
    "input_path": "nature_scene.mp4",
    "output_path": "ambient_loop.mp4",
    "loop_count": 10,
    "crossfade_duration": 3.0
})
```

---

## 🎬 Advanced Workflow Examples

### Multi-Camera Production

```python
async def multi_camera_edit():
    """Create a multi-camera production with advanced techniques"""
    
    # Step 1: Create picture-in-picture for main + reaction cam
    await session.call_tool("create_picture_in_picture", {
        "main_video": "main_camera.mp4",
        "overlay_video": "reaction_cam.mp4",
        "output_path": "main_with_reaction.mp4",
        "position": "bottom-right",
        "scale": 0.25,
        "border_width": 2,
        "border_color": "white"
    })
    
    # Step 2: Create comparison mosaic for analysis
    await session.call_tool("create_video_mosaic", {
        "input_paths": [
            "camera_angle_1.mp4",
            "camera_angle_2.mp4",
            "camera_angle_3.mp4",
            "camera_angle_4.mp4"
        ],
        "output_path": "all_angles_comparison.mp4",
        "layout": "2x2",
        "audio_source": "first"
    })
    
    # Step 3: Create smooth transitions between best angles
    await session.call_tool("create_video_transitions", {
        "input_paths": [
            "angle1_best_part.mp4",
            "angle2_best_part.mp4",
            "angle3_best_part.mp4"
        ],
        "output_path": "final_multicam_edit.mp4",
        "transition_type": "crossfade",
        "transition_duration": 1.5
    })
    
    print("✅ Multi-camera production complete!")

await multi_camera_edit()
```

### Automated Content Creation

```python
async def automated_social_content():
    """Automatically create social media content from source material"""
    
    # Step 1: Create slideshow from product images
    await session.call_tool("create_video_slideshow", {
        "image_folder": "product_photos/",
        "output_path": "product_slideshow.mp4",
        "duration_per_image": 2.5,
        "transition_duration": 0.8,
        "resolution": "1080x1080",  # Square for Instagram
        "audio_path": "upbeat_music.mp3"
    })
    
    # Step 2: Create time-lapse of behind-the-scenes
    await session.call_tool("create_time_lapse", {
        "input_path": "behind_scenes_2hours.mp4",
        "output_path": "bts_timelapse.mp4",
        "speed_factor": 30.0,
        "stabilize": True
    })
    
    # Step 3: Combine with picture-in-picture
    await session.call_tool("create_picture_in_picture", {
        "main_video": "product_slideshow.mp4",
        "overlay_video": "bts_timelapse.mp4",
        "output_path": "social_content_final.mp4",
        "position": "top-left",
        "scale": 0.3,
        "opacity": 0.8,
        "start_time": 5.0,
        "duration": 15.0
    })
    
    print("✅ Social media content generated!")

await automated_social_content()
```

### Professional Video Mosaic Dashboard

```python
async def create_video_dashboard():
    """Create a professional video monitoring dashboard"""
    
    # Security camera layout
    security_feeds = [
        "camera_entrance.mp4",
        "camera_parking.mp4", 
        "camera_warehouse.mp4",
        "camera_office.mp4"
    ]
    
    await session.call_tool("create_video_mosaic", {
        "input_paths": security_feeds,
        "output_path": "security_dashboard.mp4",
        "layout": "2x2",
        "width": 1920,
        "height": 1080,
        "border_width": 4,
        "border_color": "#00ff00",  # Green borders
        "audio_source": "none"  # No audio for security feed
    })
    
    # Performance monitoring layout
    performance_videos = [
        "cpu_usage_graph.mp4",
        "memory_usage_graph.mp4",
        "network_traffic.mp4"
    ]
    
    await session.call_tool("create_video_mosaic", {
        "input_paths": performance_videos,
        "output_path": "performance_dashboard.mp4",
        "layout": "1x3",
        "width": 1920,
        "height": 640,
        "border_width": 2,
        "border_color": "#333333",
        "audio_source": "none"
    })
    
    print("✅ Video dashboards created!")

await create_video_dashboard()
```

## 🔧 Advanced Tips and Techniques

### Optimizing for Different Platforms

```python
# Platform-specific mosaic configurations
PLATFORM_CONFIGS = {
    "youtube": {
        "resolution": (1920, 1080),
        "layout": "2x2",
        "border_width": 2
    },
    "instagram": {
        "resolution": (1080, 1080),
        "layout": "2x2", 
        "border_width": 4
    },
    "tiktok": {
        "resolution": (1080, 1920),
        "layout": "2x1",  # Vertical stack
        "border_width": 6
    },
    "dashboard": {
        "resolution": (3840, 2160),  # 4K for large displays
        "layout": "3x3",
        "border_width": 1
    }
}
```

### Performance Considerations

1. **Memory Usage**: Complex compositions use more memory
2. **Processing Time**: Multiple video streams take longer to process
3. **File Size**: Output files can be large - consider compression
4. **Audio Handling**: Be mindful of audio mixing in multi-video compositions

### Creative Applications

- **Educational Content**: Multi-angle demonstrations
- **Security Systems**: Real-time monitoring layouts
- **Sports Analysis**: Multiple camera angle comparisons
- **Live Streaming**: Picture-in-picture for commentary
- **Marketing**: Product showcase combinations
- **Training Materials**: Step-by-step process documentation

## 🎯 Next Steps

Ready to explore more advanced video production techniques?

- **[Specialized Effects](/tools/specialized-effects/)** - Professional VFX and cinematic effects
- **[Text & Graphics](/tools/text-graphics/)** - Add text overlays and animations
- **[Analysis & Extraction](/tools/analysis-extraction/)** - Video content analysis
- **[VFX Compositing Guide](/guides/vfx-compositing/)** - Advanced compositing workflows

**Questions about advanced operations?** Check our [FAQ](/support/faq/) or explore the [examples section](/examples/visual-effects/) for more creative ideas.