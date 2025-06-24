---
title: Audio Editing Guide
description: Comprehensive guide to audio processing and editing workflows
---

Complete guide to audio processing, editing, and enhancement workflows using the VFX MCP Server.

## Audio Processing Workflow

### 1. Audio Extraction
First, extract audio from video files for independent processing:

```python
# Extract audio from video
await extract_audio("input_video.mp4", "extracted_audio.wav")
```

### 2. Audio Enhancement
Apply filters and effects to improve audio quality:

```python
# Normalize audio levels
await apply_filter("audio.wav", "normalized.wav", "volume", "normalize")

# Remove noise
await apply_filter("audio.wav", "clean.wav", "highpass", "f=80")
```

### 3. Audio Mixing
Combine multiple audio sources:

```python
# Add background music
await add_audio("video.mp4", "music.mp3", "final.mp4", mode="mix", volume=0.3)

# Replace original audio
await add_audio("video.mp4", "new_audio.wav", "final.mp4", mode="replace")
```

## Common Audio Tasks

### Noise Reduction
Remove unwanted background noise:

```python
# High-pass filter to remove low-frequency noise
await apply_filter("input.wav", "clean.wav", "highpass", "f=100")

# Low-pass filter to remove high-frequency noise
await apply_filter("input.wav", "clean.wav", "lowpass", "f=8000")
```

### Volume Control
Adjust audio levels and dynamics:

```python
# Increase volume by 10dB
await apply_filter("audio.wav", "louder.wav", "volume", "10dB")

# Normalize audio to standard levels
await apply_filter("audio.wav", "normalized.wav", "volume", "normalize")
```

### Audio Synchronization
Sync audio with video content:

```python
# Add delay to audio track
await apply_filter("audio.wav", "delayed.wav", "adelay", "1000")

# Speed up audio to match video
await change_speed("audio.wav", "synced.wav", 1.05)
```

## Professional Audio Workflows

### Podcast Production
Complete podcast processing pipeline:

1. **Extract and clean audio**
2. **Normalize levels**
3. **Remove gaps and silences**
4. **Add intro/outro music**
5. **Final mix and export**

### Music Video Creation
Sync video content with music tracks:

1. **Extract video timing**
2. **Analyze audio beats**
3. **Cut video to music rhythm**
4. **Mix original and new audio**

### Voice-over Integration
Add narration to video content:

1. **Record clean voice-over**
2. **Match audio levels**
3. **Reduce background video audio**
4. **Mix voice with background**

## Audio Format Considerations

### Recommended Formats
- **WAV**: Uncompressed, best quality for editing
- **MP3**: Compressed, good for final distribution
- **AAC**: Modern compression, mobile-friendly

### Quality Settings
- **Sample Rate**: 44.1kHz for music, 48kHz for video
- **Bit Depth**: 16-bit minimum, 24-bit preferred
- **Bitrate**: 128kbps minimum for MP3, 320kbps preferred

## Troubleshooting Audio Issues

### Common Problems
- **Audio sync drift**: Use speed adjustment tools
- **Volume inconsistencies**: Apply normalization
- **Background noise**: Use filtering techniques
- **Clipping**: Reduce gain and apply limiting

### Best Practices
- Always work with high-quality source audio
- Make incremental adjustments
- Test on multiple playback devices
- Keep backup copies of original files