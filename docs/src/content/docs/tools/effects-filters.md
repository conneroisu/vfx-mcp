---
title: Effects & Filters
description: Professional-grade video enhancement, color grading, and visual effects tools
---

# Effects & Filters

The effects and filters category provides professional-grade video enhancement tools for color correction, motion effects, stabilization, and custom filtering. These tools are essential for creating polished, professional-looking video content.

## 🎨 Available Tools

### `apply_filter`
Apply custom FFmpeg filters with complete control over video processing.

<div class="tool-signature">

```python
apply_filter(
    input_path: str,
    output_path: str,
    filter_string: str,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the filtered output video</td></tr>
<tr><td>filter_string</td><td>str</td><td>FFmpeg filter expression</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Apply black and white filter
result = await session.call_tool("apply_filter", {
    "input_path": "color_video.mp4",
    "output_path": "bw_video.mp4",
    "filter_string": "hue=s=0"
})

# Apply vintage film look
result = await session.call_tool("apply_filter", {
    "input_path": "modern_video.mp4",
    "output_path": "vintage_video.mp4", 
    "filter_string": "curves=vintage,vignette=angle=PI/4"
})

# Apply blur effect
result = await session.call_tool("apply_filter", {
    "input_path": "sharp_video.mp4",
    "output_path": "blurred_video.mp4",
    "filter_string": "boxblur=5:1"
})

# Complex filter chain
result = await session.call_tool("apply_filter", {
    "input_path": "raw_footage.mp4",
    "output_path": "stylized.mp4",
    "filter_string": "eq=contrast=1.2:brightness=0.05,unsharp=5:5:0.8"
})
```

**Common Filter Examples:**
- **Brightness/Contrast**: `eq=brightness=0.1:contrast=1.2`
- **Saturation**: `hue=s=1.5` (increase) or `hue=s=0` (grayscale)
- **Blur**: `boxblur=5:1` or `gblur=sigma=2`
- **Sharpen**: `unsharp=5:5:1.0:5:5:0.0`
- **Vignette**: `vignette=angle=PI/4`
- **Film Grain**: `noise=alls=10:allf=t`

---

### `change_speed`
Adjust video playback speed with automatic audio compensation.

<div class="tool-signature">

```python
change_speed(
    input_path: str,
    output_path: str,
    speed_factor: float,
    preserve_audio: bool = True,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the speed-adjusted output video</td></tr>
<tr><td>speed_factor</td><td>float</td><td>Speed multiplier (0.5 = half speed, 2.0 = double speed)</td></tr>
<tr><td>preserve_audio</td><td>bool</td><td>Whether to maintain audio pitch (default: True)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Create slow motion (half speed)
result = await session.call_tool("change_speed", {
    "input_path": "action_sequence.mp4",
    "output_path": "slow_motion.mp4",
    "speed_factor": 0.5,
    "preserve_audio": True
})

# Create time-lapse (4x speed)
result = await session.call_tool("change_speed", {
    "input_path": "long_process.mp4",
    "output_path": "timelapse.mp4",
    "speed_factor": 4.0,
    "preserve_audio": False  # Remove audio for time-lapse
})

# Slight speed increase for pacing
result = await session.call_tool("change_speed", {
    "input_path": "interview.mp4",
    "output_path": "tighter_pacing.mp4",
    "speed_factor": 1.15,  # 15% faster
    "preserve_audio": True
})
```

**Speed Guidelines:**
- **0.1 - 0.5**: Extreme slow motion
- **0.5 - 0.8**: Slow motion effects
- **0.8 - 1.2**: Subtle pacing adjustments
- **1.2 - 2.0**: Fast-paced content
- **2.0+**: Time-lapse effects

---

### `apply_color_grading`
Professional color correction and grading with comprehensive controls.

<div class="tool-signature">

```python
apply_color_grading(
    input_path: str,
    output_path: str,
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

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the color-graded output video</td></tr>
<tr><td>brightness</td><td>float</td><td>Brightness adjustment (-1.0 to 1.0, default: 0.0)</td></tr>
<tr><td>contrast</td><td>float</td><td>Contrast multiplier (0.0 to 3.0, default: 1.0)</td></tr>
<tr><td>saturation</td><td>float</td><td>Saturation multiplier (0.0 to 3.0, default: 1.0)</td></tr>
<tr><td>gamma</td><td>float</td><td>Gamma correction (0.1 to 3.0, default: 1.0)</td></tr>
<tr><td>temperature</td><td>float</td><td>Color temperature (-1.0 warm to 1.0 cool, default: 0.0)</td></tr>
<tr><td>tint</td><td>float</td><td>Green/magenta tint (-1.0 to 1.0, default: 0.0)</td></tr>
<tr><td>shadows</td><td>float</td><td>Shadow adjustment (-1.0 to 1.0, default: 0.0)</td></tr>
<tr><td>highlights</td><td>float</td><td>Highlight adjustment (-1.0 to 1.0, default: 0.0)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Basic color correction
result = await session.call_tool("apply_color_grading", {
    "input_path": "raw_footage.mp4",
    "output_path": "corrected.mp4",
    "brightness": 0.05,
    "contrast": 1.1,
    "saturation": 1.2
})

# Warm, cinematic look
result = await session.call_tool("apply_color_grading", {
    "input_path": "scene.mp4",
    "output_path": "cinematic.mp4",
    "temperature": -0.3,    # Warmer
    "contrast": 1.15,
    "saturation": 0.9,
    "shadows": 0.1,
    "highlights": -0.05
})

# Cool, modern look
result = await session.call_tool("apply_color_grading", {
    "input_path": "tech_demo.mp4",
    "output_path": "modern_look.mp4",
    "temperature": 0.2,     # Cooler
    "contrast": 1.2,
    "saturation": 1.1,
    "gamma": 0.95
})

# Film emulation
result = await session.call_tool("apply_color_grading", {
    "input_path": "digital.mp4",
    "output_path": "film_look.mp4",
    "contrast": 0.9,
    "saturation": 0.85,
    "shadows": 0.15,
    "highlights": -0.1,
    "gamma": 1.1
})
```

**Color Grading Presets:**
```python
# Popular color grading styles
GRADING_PRESETS = {
    "cinematic": {
        "contrast": 1.15,
        "saturation": 0.9,
        "temperature": -0.2,
        "shadows": 0.1,
        "highlights": -0.05
    },
    "vibrant": {
        "contrast": 1.2,
        "saturation": 1.4,
        "brightness": 0.05,
        "gamma": 0.95
    },
    "vintage": {
        "contrast": 0.85,
        "saturation": 0.7,
        "temperature": -0.3,
        "gamma": 1.2
    },
    "modern": {
        "contrast": 1.25,
        "saturation": 1.1,
        "temperature": 0.1,
        "shadows": -0.05
    }
}
```

---

### `apply_motion_blur`
Add realistic motion blur effects with directional control.

<div class="tool-signature">

```python
apply_motion_blur(
    input_path: str,
    output_path: str,
    angle: float = 0.0,
    distance: float = 5.0,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the motion-blurred output video</td></tr>
<tr><td>angle</td><td>float</td><td>Blur direction in degrees (0-360, default: 0.0)</td></tr>
<tr><td>distance</td><td>float</td><td>Blur distance in pixels (default: 5.0)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Horizontal motion blur
result = await session.call_tool("apply_motion_blur", {
    "input_path": "car_chase.mp4",
    "output_path": "speed_blur.mp4",
    "angle": 0.0,      # Horizontal
    "distance": 8.0
})

# Vertical motion blur
result = await session.call_tool("apply_motion_blur", {
    "input_path": "falling_object.mp4",
    "output_path": "fall_blur.mp4",
    "angle": 90.0,     # Vertical
    "distance": 12.0
})

# Diagonal motion blur
result = await session.call_tool("apply_motion_blur", {
    "input_path": "diagonal_movement.mp4",
    "output_path": "diagonal_blur.mp4",
    "angle": 45.0,     # Diagonal
    "distance": 6.0
})
```

---

### `apply_video_stabilization`
Advanced optical flow-based video stabilization.

<div class="tool-signature">

```python
apply_video_stabilization(
    input_path: str,
    output_path: str,
    smoothing: float = 10.0,
    crop_black: bool = True,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source shaky video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the stabilized output video</td></tr>
<tr><td>smoothing</td><td>float</td><td>Smoothing strength (1.0 to 100.0, default: 10.0)</td></tr>
<tr><td>crop_black</td><td>bool</td><td>Whether to crop black borders (default: True)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Standard stabilization
result = await session.call_tool("apply_video_stabilization", {
    "input_path": "handheld_footage.mp4",
    "output_path": "stabilized.mp4",
    "smoothing": 15.0,
    "crop_black": True
})

# Light stabilization (preserve more original motion)
result = await session.call_tool("apply_video_stabilization", {
    "input_path": "walking_shot.mp4",
    "output_path": "lightly_stabilized.mp4",
    "smoothing": 5.0,
    "crop_black": False
})

# Heavy stabilization (very smooth)
result = await session.call_tool("apply_video_stabilization", {
    "input_path": "very_shaky.mp4",
    "output_path": "very_smooth.mp4",
    "smoothing": 25.0,
    "crop_black": True
})
```

**Smoothing Guidelines:**
- **1.0 - 5.0**: Light stabilization, preserves natural motion
- **5.0 - 15.0**: Standard stabilization for most content
- **15.0 - 30.0**: Heavy stabilization for very shaky footage
- **30.0+**: Extreme smoothing, may look artificial

## 🎬 Professional Workflows

### Color Grade Pipeline
```python
# Professional color grading workflow
async def color_grade_workflow(input_video, output_video):
    # Step 1: Basic color correction
    await session.call_tool("apply_color_grading", {
        "input_path": input_video,
        "output_path": "temp_corrected.mp4",
        "brightness": 0.02,
        "contrast": 1.05,
        "saturation": 1.0
    })
    
    # Step 2: Creative grading
    await session.call_tool("apply_color_grading", {
        "input_path": "temp_corrected.mp4",
        "output_path": "temp_creative.mp4",
        "temperature": -0.15,
        "shadows": 0.08,
        "highlights": -0.03
    })
    
    # Step 3: Final polish with filter
    await session.call_tool("apply_filter", {
        "input_path": "temp_creative.mp4",
        "output_path": output_video,
        "filter_string": "unsharp=5:5:0.3:5:5:0.0"  # Subtle sharpening
    })
```

### Action Sequence Enhancement
```python
# Enhance action sequences
async def enhance_action_sequence(input_video, output_video):
    # Step 1: Stabilize shaky footage
    await session.call_tool("apply_video_stabilization", {
        "input_path": input_video,
        "output_path": "temp_stabilized.mp4",
        "smoothing": 12.0
    })
    
    # Step 2: Add motion blur for dynamic feel
    await session.call_tool("apply_motion_blur", {
        "input_path": "temp_stabilized.mp4",
        "output_path": "temp_blur.mp4",
        "angle": 0.0,
        "distance": 4.0
    })
    
    # Step 3: Dramatic color grading
    await session.call_tool("apply_color_grading", {
        "input_path": "temp_blur.mp4",
        "output_path": output_video,
        "contrast": 1.3,
        "saturation": 1.2,
        "shadows": 0.1,
        "highlights": -0.05
    })
```

### Documentary Style Processing
```python
# Documentary-style color grading
async def documentary_style(input_video, output_video):
    # Natural, slightly desaturated look
    await session.call_tool("apply_color_grading", {
        "input_path": input_video,
        "output_path": "temp_graded.mp4",
        "contrast": 1.08,
        "saturation": 0.85,
        "gamma": 1.05,
        "shadows": 0.03
    })
    
    # Add subtle film grain
    await session.call_tool("apply_filter", {
        "input_path": "temp_graded.mp4",
        "output_path": output_video,
        "filter_string": "noise=alls=5:allf=t"
    })
```

## 🔧 Technical Considerations

### Performance Tips

1. **Filter Complexity**: Complex filters take longer to process
2. **Preview Settings**: Use lower quality for previews, full quality for final output
3. **Batch Processing**: Apply similar effects to multiple videos together
4. **Format Considerations**: Some effects work better with specific codecs

### Quality vs. Speed Trade-offs

```python
# Fast processing (lower quality)
FAST_SETTINGS = {
    "quality": "medium",
    "smoothing": 8.0,        # Lighter stabilization
    "distance": 3.0,         # Less motion blur
    "filter_string": "eq=contrast=1.1"  # Simple filters
}

# High quality (slower processing)
QUALITY_SETTINGS = {
    "quality": "ultra",
    "smoothing": 15.0,       # More stabilization
    "distance": 6.0,         # More motion blur
    "filter_string": "eq=contrast=1.1:brightness=0.02,unsharp=5:5:0.5"
}
```

### Color Space Considerations

- **Rec.709**: Standard HD color space
- **Rec.2020**: Wide color gamut for HDR
- **sRGB**: Web-safe color space

## 🎨 Creative Applications

### Film Look Recreation
```python
# Recreate specific film looks
FILM_LOOKS = {
    "70s_film": {
        "temperature": -0.4,
        "contrast": 0.9,
        "saturation": 0.8,
        "gamma": 1.15,
        "filter_string": "curves=vintage,vignette=PI/6"
    },
    "modern_digital": {
        "temperature": 0.1,
        "contrast": 1.2,
        "saturation": 1.1,
        "shadows": -0.02,
        "highlights": -0.03
    },
    "noir": {
        "saturation": 0.0,  # Black and white
        "contrast": 1.4,
        "gamma": 1.1,
        "filter_string": "curves=strong_contrast"
    }
}
```

## 🚀 Next Steps

Ready to explore more advanced video processing?

- **[Advanced Operations](/tools/advanced-operations/)** - Complex video composition
- **[Specialized Effects](/tools/specialized-effects/)** - Professional VFX tools
- **[Color Grading Guide](/guides/color-grading/)** - Complete color grading workflows
- **[Common Workflows](/guides/common-workflows/)** - Typical video editing patterns

---

**Questions about effects and filters?** Check our [FAQ](/support/faq/) or explore the [examples section](/examples/visual-effects/).