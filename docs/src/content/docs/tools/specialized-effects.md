---
title: Specialized Effects Tools
description: Advanced and specialized video effects for unique visual transformations
---

# Specialized Effects Tools

Advanced and specialized video effects for unique visual transformations and creative video processing.

## Available Tools

### create_reverse_video
Create reverse/backwards playback of video content.

**Parameters:**
- `input_path` (str): Path to the input video file
- `output_path` (str): Path for the output video file

**Returns:** Success message with output path

**Example:**
```python
reverse = await create_reverse_video("input.mp4", "reversed.mp4")
```

### create_loop_video
Create seamlessly looping video content.

**Parameters:**
- `input_path` (str): Path to the input video file
- `output_path` (str): Path for the output video file
- `loop_count` (int, optional): Number of loops (default: 3)

**Returns:** Success message with output path

**Example:**
```python
loop = await create_loop_video("clip.mp4", "looped.mp4", loop_count=5)
```

### apply_stabilization
Apply video stabilization to reduce camera shake.

**Parameters:**
- `input_path` (str): Path to the input video file
- `output_path` (str): Path for the output video file
- `strength` (float, optional): Stabilization strength (0.0-1.0)

**Returns:** Success message with output path

**Example:**
```python
stable = await apply_stabilization("shaky.mp4", "stable.mp4", strength=0.8)
```

### create_picture_in_picture
Create picture-in-picture composite effects.

**Parameters:**
- `main_video` (str): Path to the main video file
- `overlay_video` (str): Path to the overlay video file
- `output_path` (str): Path for the output video file
- `position` (str, optional): Overlay position
- `scale` (float, optional): Overlay scale factor

**Returns:** Success message with output path

**Example:**
```python
pip = await create_picture_in_picture("main.mp4", "overlay.mp4", "pip.mp4", position="top-right")
```

## Use Cases

- **Creative Effects**: Unique visual transformations
- **Stabilization**: Fix shaky footage
- **Composite Video**: Multiple video layers
- **Animation**: Reverse and loop effects