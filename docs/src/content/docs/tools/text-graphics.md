---
title: Text & Graphics Tools
description: Video text overlay, graphics, and visual element manipulation tools
---

Video text overlay, graphics, and visual element manipulation tools for adding textual and graphic content.

## Available Tools

### add_text_overlay
Add text overlays to video with customizable styling.

**Parameters:**
- `input_path` (str): Path to the input video file
- `output_path` (str): Path for the output video file
- `text` (str): Text content to overlay
- `position` (str, optional): Text position ("top", "center", "bottom")
- `font_size` (int, optional): Font size for text
- `color` (str, optional): Text color (default: "white")

**Returns:** Success message with output path

**Example:**
```python
overlay = await add_text_overlay("input.mp4", "output.mp4", "My Title", position="top", font_size=48)
```

### add_watermark
Add image watermarks to videos.

**Parameters:**
- `input_path` (str): Path to the input video file
- `output_path` (str): Path for the output video file
- `watermark_path` (str): Path to the watermark image
- `position` (str, optional): Watermark position
- `opacity` (float, optional): Watermark opacity (0.0-1.0)

**Returns:** Success message with output path

**Example:**
```python
watermark = await add_watermark("video.mp4", "watermarked.mp4", "logo.png", opacity=0.7)
```

## Use Cases

- **Branding**: Add logos and watermarks to videos
- **Titles**: Create professional title sequences
- **Subtitles**: Add text overlays for accessibility
- **Graphics**: Overlay graphical elements and animations