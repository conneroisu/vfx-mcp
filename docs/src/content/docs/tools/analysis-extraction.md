---
title: Analysis & Extraction Tools
description: Video analysis and content extraction tools for metadata, thumbnails, and information gathering
---

# Analysis & Extraction Tools

Video analysis and content extraction tools for metadata, thumbnails, and information gathering.

## Available Tools

### get_video_info
Extract comprehensive metadata from video files.

**Parameters:**
- `input_path` (str): Path to the input video file

**Returns:** JSON string with video metadata including:
- Duration, resolution, frame rate
- Codec information, bitrate
- Audio stream details
- Format information

**Example:**
```python
info = await get_video_info("input.mp4")
```

### generate_thumbnail
Create thumbnail images from video frames.

**Parameters:**
- `input_path` (str): Path to the input video file
- `output_path` (str): Path for the output thumbnail image
- `time` (str, optional): Timestamp for thumbnail (default: "00:00:01")

**Returns:** Success message with output path

**Example:**
```python
thumbnail = await generate_thumbnail("video.mp4", "thumb.jpg", "00:02:30")
```

### extract_audio
Extract audio tracks from video files.

**Parameters:**
- `input_path` (str): Path to the input video file
- `output_path` (str): Path for the output audio file

**Returns:** Success message with output path

**Example:**
```python
audio = await extract_audio("video.mp4", "audio.mp3")
```

## Use Cases

- **Metadata Analysis**: Extract technical information for processing decisions
- **Content Preview**: Generate thumbnails for video catalogs
- **Audio Extraction**: Separate audio for independent processing
- **Quality Assessment**: Analyze video properties for optimization