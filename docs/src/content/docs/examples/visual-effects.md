---
title: Visual Effects Examples
description: Practical examples for visual effects and compositing workflows
---


Practical examples for visual effects and compositing workflows using the VFX MCP Server.

## Basic Visual Effects

### Apply Color Filters
```python
# Apply vintage sepia tone effect
result = await apply_filter(
    input_path="modern_video.mp4",
    output_path="vintage_video.mp4",
    filter_name="colorchannelmixer",
    filter_params="rr=0.393:rg=0.769:rb=0.189:gr=0.349:gg=0.686:gb=0.168:br=0.272:bg=0.534:bb=0.131"
)

# Apply black and white filter
result = await apply_filter(
    input_path="color_video.mp4",
    output_path="bw_video.mp4",
    filter_name="hue",
    filter_params="s=0"
)
```

### Adjust Brightness and Contrast
```python
# Increase brightness and contrast
result = await apply_filter(
    input_path="dark_video.mp4",
    output_path="bright_video.mp4",
    filter_name="eq",
    filter_params="brightness=0.1:contrast=1.2"
)

# Apply gamma correction
result = await apply_filter(
    input_path="input.mp4",
    output_path="gamma_corrected.mp4",
    filter_name="eq",
    filter_params="gamma=1.2"
)
```

### Create Blur Effects
```python
# Apply Gaussian blur
result = await apply_filter(
    input_path="sharp_video.mp4",
    output_path="blurred_video.mp4",
    filter_name="gblur",
    filter_params="sigma=2"
)

# Apply motion blur effect
result = await apply_filter(
    input_path="static_video.mp4",
    output_path="motion_blur.mp4",
    filter_name="minterpolate",
    filter_params="fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
)
```

## Text and Graphics Overlays

### Add Title Text
```python
# Create opening title
result = await add_text_overlay(
    input_path="video.mp4",
    output_path="titled_video.mp4",
    text="MY AWESOME VIDEO",
    position="center",
    font_size=72,
    color="white"
)

# Add subtitle at bottom
result = await add_text_overlay(
    input_path="titled_video.mp4",
    output_path="subtitled_video.mp4",
    text="Subtitle text here",
    position="bottom",
    font_size=32,
    color="yellow"
)
```

### Add Logo Watermark
```python
# Add semi-transparent logo
result = await add_watermark(
    input_path="video.mp4",
    output_path="branded_video.mp4",
    watermark_path="company_logo.png",
    position="top-right",
    opacity=0.7
)

# Add bottom watermark with full opacity
result = await add_watermark(
    input_path="video.mp4",
    output_path="watermarked_video.mp4",
    watermark_path="watermark.png",
    position="bottom-left",
    opacity=1.0
)
```

## Compositing Effects

### Picture-in-Picture
```python
# Create picture-in-picture effect
result = await create_picture_in_picture(
    main_video="main_presentation.mp4",
    overlay_video="presenter_cam.mp4",
    output_path="pip_video.mp4",
    position="top-right",
    scale=0.3
)

# Multiple layer compositing
async def create_multi_layer_composite():
    # Layer 1: Main background video
    # Layer 2: Add picture-in-picture
    pip_result = await create_picture_in_picture(
        "background.mp4", "overlay1.mp4", "temp_pip.mp4",
        position="top-right", scale=0.25
    )
    
    # Layer 3: Add title overlay
    final_result = await add_text_overlay(
        "temp_pip.mp4", "final_composite.mp4",
        "Live Stream", position="top", font_size=48
    )
    
    return final_result

result = await create_multi_layer_composite()
```

### Green Screen Compositing
```python
# Remove green screen background
result = await apply_filter(
    input_path="greenscreen_footage.mp4",
    output_path="keyed_footage.mp4",
    filter_name="chromakey",
    filter_params="color=green:similarity=0.3:blend=0.1"
)

# Composite with new background
result = await create_picture_in_picture(
    main_video="new_background.mp4",
    overlay_video="keyed_footage.mp4",
    output_path="composite_final.mp4",
    position="center",
    scale=1.0
)
```

## Speed and Time Effects

### Speed Ramping
```python
# Create slow motion effect
result = await change_speed(
    input_path="normal_speed.mp4",
    output_path="slow_motion.mp4",
    speed_factor=0.5  # Half speed
)

# Create fast motion effect
result = await change_speed(
    input_path="normal_speed.mp4",
    output_path="fast_motion.mp4",
    speed_factor=2.0  # Double speed
)

# Complex speed ramping
async def create_speed_ramp(input_path: str, output_path: str):
    """Create dramatic speed ramp effect"""
    
    # Split video into segments
    # Segment 1: Normal speed (0-5 seconds)
    seg1 = await trim_video(input_path, "seg1.mp4", "00:00:00", "00:00:05")
    
    # Segment 2: Slow motion (5-7 seconds, slowed down)
    seg2_temp = await trim_video(input_path, "seg2_temp.mp4", "00:00:05", "00:00:07")
    seg2 = await change_speed("seg2_temp.mp4", "seg2.mp4", 0.25)  # Quarter speed
    
    # Segment 3: Back to normal (7+ seconds)
    seg3 = await trim_video(input_path, "seg3.mp4", "00:00:07", "00:00:15")
    
    # Concatenate segments
    result = await concatenate_videos(["seg1.mp4", "seg2.mp4", "seg3.mp4"], output_path)
    
    return result

result = await create_speed_ramp("action_scene.mp4", "speed_ramped.mp4")
```

### Reverse Video Effect
```python
# Create reverse playback
result = await create_reverse_video(
    input_path="forward_video.mp4",
    output_path="reverse_video.mp4"
)

# Create boomerang effect (forward + reverse)
async def create_boomerang_effect(input_path: str, output_path: str):
    """Create boomerang loop effect"""
    
    # Create reverse version
    reverse_video = await create_reverse_video(input_path, "temp_reverse.mp4")
    
    # Concatenate original with reverse
    boomerang = await concatenate_videos([input_path, "temp_reverse.mp4"], output_path)
    
    # Create seamless loop
    loop_result = await create_loop_video(output_path, "looped_" + output_path, loop_count=3)
    
    return loop_result

result = await create_boomerang_effect("short_clip.mp4", "boomerang.mp4")
```

## Color Grading Effects

### Cinematic Look
```python
# Apply cinematic color grading
result = await apply_filter(
    input_path="raw_footage.mp4",
    output_path="cinematic.mp4",
    filter_name="colorbalance",
    filter_params="rs=0.1:gs=0.05:bs=-0.1"
)

# Add film grain for vintage look
result = await apply_filter(
    input_path="cinematic.mp4",
    output_path="film_look.mp4",
    filter_name="noise",
    filter_params="alls=20:allf=t+u"
)
```

### Creative Color Effects
```python
# Duotone effect (blue and orange)
result = await apply_filter(
    input_path="input.mp4",
    output_path="duotone.mp4",
    filter_name="selectivecolor",
    filter_params="blues=c=50:m=-20:y=-50:reds=c=-30:m=20:y=50"
)

# High contrast black and white
result = await apply_filter(
    input_path="input.mp4",
    output_path="high_contrast_bw.mp4",
    filter_name="eq",
    filter_params="contrast=2.0:saturation=0"
)

# Vintage film emulation
async def apply_vintage_film_look(input_path: str, output_path: str):
    """Apply comprehensive vintage film look"""
    
    # Step 1: Adjust colors for vintage look
    step1 = await apply_filter(
        input_path, "temp_vintage1.mp4",
        "colorchannelmixer", "rr=1.0:rg=0.0:rb=0.2:gr=0.0:gg=0.8:gb=0.1:br=0.2:bg=0.1:bb=0.9"
    )
    
    # Step 2: Add slight blur for softer look
    step2 = await apply_filter(
        "temp_vintage1.mp4", "temp_vintage2.mp4",
        "gblur", "sigma=0.5"
    )
    
    # Step 3: Add film grain
    step3 = await apply_filter(
        "temp_vintage2.mp4", "temp_vintage3.mp4",
        "noise", "alls=15:allf=t"
    )
    
    # Step 4: Adjust contrast and brightness
    final = await apply_filter(
        "temp_vintage3.mp4", output_path,
        "eq", "brightness=0.05:contrast=1.1:gamma=1.2"
    )
    
    return final

result = await apply_vintage_film_look("modern_video.mp4", "vintage_film.mp4")
```

## Stabilization and Enhancement

### Video Stabilization
```python
# Apply basic stabilization
result = await apply_stabilization(
    input_path="shaky_footage.mp4",
    output_path="stabilized.mp4",
    strength=0.8
)

# Advanced stabilization with cropping
async def advanced_stabilization(input_path: str, output_path: str):
    """Apply stabilization with intelligent cropping"""
    
    # First pass: analyze camera movement
    stabilized = await apply_stabilization(input_path, "temp_stabilized.mp4", 0.9)
    
    # Second pass: crop to remove black borders
    cropped = await apply_filter(
        "temp_stabilized.mp4", output_path,
        "crop", "in_w-40:in_h-40:20:20"  # Crop 20px from each edge
    )
    
    return cropped

result = await advanced_stabilization("handheld_footage.mp4", "smooth_footage.mp4")
```

### Image Enhancement
```python
# Sharpen video
result = await apply_filter(
    input_path="soft_video.mp4",
    output_path="sharp_video.mp4",
    filter_name="unsharp",
    filter_params="5:5:1.0:5:5:0.0"
)

# Noise reduction
result = await apply_filter(
    input_path="noisy_video.mp4",
    output_path="clean_video.mp4",
    filter_name="nlmeans",
    filter_params="s=1.0"
)
```

## Advanced Compositing Workflow

### Multi-Layer Production
```python
async def create_professional_composite():
    """Create professional multi-layer video composite"""
    
    # Layer 1: Background plate
    background = "background_plate.mp4"
    
    # Layer 2: Remove green screen from subject
    subject_keyed = await apply_filter(
        "subject_greenscreen.mp4", "subject_keyed.mp4",
        "chromakey", "color=green:similarity=0.3:blend=0.05"
    )
    
    # Layer 3: Composite subject onto background
    composite = await create_picture_in_picture(
        background, "subject_keyed.mp4", "temp_composite.mp4",
        position="center", scale=1.0
    )
    
    # Layer 4: Add graphics overlay
    with_graphics = await add_watermark(
        "temp_composite.mp4", "temp_graphics.mp4",
        "graphics_overlay.png", position="top-left", opacity=0.8
    )
    
    # Layer 5: Add title text
    with_title = await add_text_overlay(
        "temp_graphics.mp4", "temp_title.mp4",
        "BREAKING NEWS", position="bottom", font_size=36, color="red"
    )
    
    # Layer 6: Apply final color grading
    final_result = await apply_filter(
        "temp_title.mp4", "final_composite.mp4",
        "eq", "brightness=0.02:contrast=1.05:saturation=1.1"
    )
    
    return final_result

result = await create_professional_composite()
```

## Creative Transitions

### Custom Transition Effects
```python
async def create_fade_transition(clip1: str, clip2: str, output: str, duration: float = 1.0):
    """Create custom fade transition between clips"""
    
    # Get clip durations
    info1 = await get_video_info(clip1)
    info2 = await get_video_info(clip2)
    
    # Apply fade out to end of first clip
    fade_out = await apply_filter(
        clip1, "temp_fadeout.mp4",
        "fade", f"t=out:st={float(json.loads(info1)['format']['duration']) - duration}:d={duration}"
    )
    
    # Apply fade in to start of second clip
    fade_in = await apply_filter(
        clip2, "temp_fadein.mp4",
        "fade", f"t=in:st=0:d={duration}"
    )
    
    # Concatenate with overlap
    result = await concatenate_videos(["temp_fadeout.mp4", "temp_fadein.mp4"], output)
    
    return result

# Create smooth transition
result = await create_fade_transition("scene1.mp4", "scene2.mp4", "smooth_transition.mp4")
```