---
title: Audio Processing
description: Comprehensive audio manipulation and visualization tools
---

# Audio Processing

The audio processing tools provide comprehensive capabilities for extracting, manipulating, and visualizing audio content in videos. These tools handle everything from basic audio extraction to advanced multi-track mixing and audio spectrum visualization.

## 🎵 Available Tools

### `extract_audio` 
Extract audio tracks from video files with format and quality control.

<div class="tool-signature">

```python
extract_audio(
    input_path: str,
    output_path: str,
    format: str = "mp3",
    quality: str = "medium", 
    sample_rate: int = None,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the extracted audio file</td></tr>
<tr><td>format</td><td>str</td><td>Output format: "mp3", "wav", "aac", "flac" (default: "mp3")</td></tr>
<tr><td>quality</td><td>str</td><td>Audio quality: "low", "medium", "high", "ultra" (default: "medium")</td></tr>
<tr><td>sample_rate</td><td>int</td><td>Target sample rate in Hz (optional, keeps original if not specified)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Basic audio extraction
result = await session.call_tool("extract_audio", {
    "input_path": "interview.mp4",
    "output_path": "interview_audio.mp3"
})

# High-quality WAV extraction
result = await session.call_tool("extract_audio", {
    "input_path": "music_video.mp4", 
    "output_path": "music_track.wav",
    "format": "wav",
    "quality": "ultra"
})

# Extract with specific sample rate
result = await session.call_tool("extract_audio", {
    "input_path": "podcast.mp4",
    "output_path": "podcast.mp3",
    "sample_rate": 44100,
    "quality": "high"
})
```

**Quality Settings:**
- **ultra**: 320 kbps (MP3), 48kHz+ (WAV)
- **high**: 192 kbps (MP3), 44.1kHz (WAV)
- **medium**: 128 kbps (MP3), 22kHz (WAV) - default
- **low**: 64 kbps (MP3), 16kHz (WAV)

---

### `add_audio`
Add or replace audio tracks in video files with volume and timing control.

<div class="tool-signature">

```python
add_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    mode: str = "replace",
    volume: float = 1.0,
    audio_offset: float = 0.0,
    fade_in: float = 0.0,
    fade_out: float = 0.0,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>video_path</td><td>str</td><td>Path to the source video file</td></tr>
<tr><td>audio_path</td><td>str</td><td>Path to the audio file to add</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the output video with new audio</td></tr>
<tr><td>mode</td><td>str</td><td>"replace" or "mix" (default: "replace")</td></tr>
<tr><td>volume</td><td>float</td><td>Volume multiplier (1.0 = original, 0.5 = half volume)</td></tr>
<tr><td>audio_offset</td><td>float</td><td>Audio delay in seconds (positive = delay, negative = advance)</td></tr>
<tr><td>fade_in</td><td>float</td><td>Fade-in duration in seconds</td></tr>
<tr><td>fade_out</td><td>float</td><td>Fade-out duration in seconds</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Replace existing audio track
result = await session.call_tool("add_audio", {
    "video_path": "silent_video.mp4",
    "audio_path": "background_music.mp3",
    "output_path": "video_with_music.mp4",
    "mode": "replace"
})

# Mix background music with existing audio
result = await session.call_tool("add_audio", {
    "video_path": "interview.mp4",
    "audio_path": "ambient_music.mp3", 
    "output_path": "interview_with_music.mp4",
    "mode": "mix",
    "volume": 0.3,  # Quiet background music
    "fade_in": 2.0,
    "fade_out": 3.0
})

# Add synchronized audio with timing offset
result = await session.call_tool("add_audio", {
    "video_path": "presentation.mp4",
    "audio_path": "narration.mp3",
    "output_path": "synced_presentation.mp4",
    "audio_offset": 2.5,  # Start audio 2.5 seconds after video
    "volume": 0.8
})
```

**Modes:**
- **replace**: Completely replace the existing audio track
- **mix**: Blend new audio with existing audio

---

### `extract_audio_spectrum`
Generate visual audio spectrum and waveform videos for audio visualization.

<div class="tool-signature">

```python
extract_audio_spectrum(
    input_path: str,
    output_path: str,
    visualization_type: str = "spectrum",
    width: int = 1920,
    height: int = 1080,
    color_scheme: str = "rainbow",
    sensitivity: float = 1.0,
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_path</td><td>str</td><td>Path to the source video or audio file</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the output visualization video</td></tr>
<tr><td>visualization_type</td><td>str</td><td>"spectrum", "waveform", "bars", "circle" (default: "spectrum")</td></tr>
<tr><td>width</td><td>int</td><td>Output video width in pixels (default: 1920)</td></tr>
<tr><td>height</td><td>int</td><td>Output video height in pixels (default: 1080)</td></tr>
<tr><td>color_scheme</td><td>str</td><td>"rainbow", "fire", "cool", "mono" (default: "rainbow")</td></tr>
<tr><td>sensitivity</td><td>float</td><td>Audio sensitivity multiplier (default: 1.0)</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Create spectrum visualization
result = await session.call_tool("extract_audio_spectrum", {
    "input_path": "music.mp4",
    "output_path": "music_spectrum.mp4",
    "visualization_type": "spectrum",
    "color_scheme": "rainbow"
})

# Create waveform visualization
result = await session.call_tool("extract_audio_spectrum", {
    "input_path": "podcast.mp3",
    "output_path": "podcast_waveform.mp4",
    "visualization_type": "waveform",
    "color_scheme": "cool",
    "width": 1280,
    "height": 720
})

# Create frequency bars visualization
result = await session.call_tool("extract_audio_spectrum", {
    "input_path": "concert.mp4",
    "output_path": "concert_bars.mp4", 
    "visualization_type": "bars",
    "color_scheme": "fire",
    "sensitivity": 1.5  # More sensitive to audio
})
```

**Visualization Types:**
- **spectrum**: Frequency spectrum display
- **waveform**: Traditional waveform visualization
- **bars**: Frequency bars (equalizer style)
- **circle**: Circular audio visualizer

**Color Schemes:**
- **rainbow**: Multi-color spectrum
- **fire**: Red/orange/yellow gradient
- **cool**: Blue/cyan/green gradient  
- **mono**: Single color (white/gray)

---

### `merge_audio_tracks`
Merge multiple audio tracks with individual volume control and timing.

<div class="tool-signature">

```python
merge_audio_tracks(
    input_paths: list[str],
    output_path: str,
    volumes: list[float] = None,
    delays: list[float] = None,
    crossfade_duration: float = 0.0,
    output_format: str = "mp3",
    ctx: Context = None
) -> str
```

</div>

**Parameters:**
<table class="params-table">
<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
<tr><td>input_paths</td><td>list[str]</td><td>List of audio file paths to merge</td></tr>
<tr><td>output_path</td><td>str</td><td>Path for the merged audio output</td></tr>
<tr><td>volumes</td><td>list[float]</td><td>Volume levels for each track (optional, defaults to 1.0)</td></tr>
<tr><td>delays</td><td>list[float]</td><td>Delay in seconds for each track (optional, defaults to 0.0)</td></tr>
<tr><td>crossfade_duration</td><td>float</td><td>Crossfade duration between tracks in seconds</td></tr>
<tr><td>output_format</td><td>str</td><td>Output format: "mp3", "wav", "aac" (default: "mp3")</td></tr>
<tr><td>ctx</td><td>Context</td><td>Optional context for progress reporting</td></tr>
</table>

**Example Usage:**
```python
# Simple merge with equal volumes
result = await session.call_tool("merge_audio_tracks", {
    "input_paths": [
        "voice_over.mp3",
        "background_music.mp3",
        "sound_effects.mp3"
    ],
    "output_path": "final_audio.mp3"
})

# Merge with custom volumes and delays
result = await session.call_tool("merge_audio_tracks", {
    "input_paths": [
        "narrator.wav",
        "music.wav", 
        "ambience.wav"
    ],
    "output_path": "podcast_mix.wav",
    "volumes": [1.0, 0.3, 0.2],    # Narrator full, music/ambience quiet
    "delays": [0.0, 5.0, 10.0],    # Music starts at 5s, ambience at 10s
    "output_format": "wav"
})

# Merge with crossfade transitions
result = await session.call_tool("merge_audio_tracks", {
    "input_paths": [
        "intro_music.mp3",
        "main_track.mp3",
        "outro_music.mp3" 
    ],
    "output_path": "seamless_mix.mp3",
    "crossfade_duration": 2.0,  # 2-second crossfade between tracks
    "volumes": [0.8, 1.0, 0.8]
})
```

## 🎧 Advanced Audio Workflows

### Podcast Production
```python
# 1. Extract audio from video interview
await session.call_tool("extract_audio", {
    "input_path": "interview_video.mp4",
    "output_path": "raw_interview.wav",
    "format": "wav",
    "quality": "ultra"
})

# 2. Create background music mix
await session.call_tool("merge_audio_tracks", {
    "input_paths": [
        "raw_interview.wav",
        "intro_music.mp3",
        "outro_music.mp3"
    ],
    "output_path": "podcast_with_music.mp3",
    "volumes": [1.0, 0.4, 0.4],
    "delays": [10.0, 0.0, 1800.0],  # Interview starts 10s in
    "crossfade_duration": 3.0
})

# 3. Add final audio to video
await session.call_tool("add_audio", {
    "video_path": "interview_video.mp4",
    "audio_path": "podcast_with_music.mp3",
    "output_path": "final_podcast.mp4",
    "mode": "replace"
})
```

### Music Video Production
```python
# 1. Extract original audio for reference
await session.call_tool("extract_audio", {
    "input_path": "raw_performance.mp4",
    "output_path": "reference_audio.wav",
    "format": "wav"
})

# 2. Replace with studio track
await session.call_tool("add_audio", {
    "video_path": "raw_performance.mp4",
    "audio_path": "studio_track.mp3",
    "output_path": "synced_performance.mp4",
    "mode": "replace",
    "volume": 0.95
})

# 3. Create audio visualization
await session.call_tool("extract_audio_spectrum", {
    "input_path": "synced_performance.mp4",
    "output_path": "spectrum_overlay.mp4",
    "visualization_type": "spectrum",
    "color_scheme": "fire",
    "sensitivity": 1.2
})
```

### Multi-language Content
```python
# Create multiple language versions
languages = {
    "english": "narration_en.mp3",
    "spanish": "narration_es.mp3", 
    "french": "narration_fr.mp3"
}

for lang, audio_file in languages.items():
    # Merge narration with background music
    await session.call_tool("merge_audio_tracks", {
        "input_paths": [audio_file, "background_music.mp3"],
        "output_path": f"mixed_audio_{lang}.mp3",
        "volumes": [1.0, 0.25],
        "delays": [0.0, 0.0]
    })
    
    # Add to video
    await session.call_tool("add_audio", {
        "video_path": "base_video.mp4",
        "audio_path": f"mixed_audio_{lang}.mp3",
        "output_path": f"video_{lang}.mp4",
        "mode": "replace"
    })
```

## 🔧 Technical Considerations

### Audio Quality Settings

**For Speech/Dialogue:**
- Format: MP3 or AAC
- Quality: Medium (128 kbps) or High (192 kbps)
- Sample Rate: 22kHz or 44.1kHz

**For Music:**
- Format: WAV (uncompressed) or MP3 (320 kbps)
- Quality: Ultra or High
- Sample Rate: 44.1kHz or 48kHz

**For Sound Effects:**
- Format: WAV for editing, MP3 for final output
- Quality: High or Ultra
- Sample Rate: 44.1kHz

### Volume Level Guidelines

```python
# Recommended volume levels for mixing
VOLUME_LEVELS = {
    "primary_dialogue": 1.0,      # Full volume
    "background_music": 0.2-0.4,  # Quiet background
    "sound_effects": 0.6-0.8,     # Noticeable but not overpowering
    "ambient_sounds": 0.1-0.3,    # Subtle atmosphere
    "intro_music": 0.7-0.9,       # Prominent but not overwhelming
}
```

### Synchronization Tips

1. **Audio Offset Calculation:**
   - Positive values delay audio
   - Negative values advance audio
   - Use video editor to find exact sync points

2. **Crossfade Duration:**
   - 0.5-1.0s for quick transitions
   - 2.0-3.0s for smooth blending
   - 5.0s+ for long, cinematic fades

3. **File Format Compatibility:**
   - MP3: Universal compatibility, good compression
   - WAV: Uncompressed, best quality for editing
   - AAC: Modern format, good quality/size ratio

## 📊 Performance Optimization

### Batch Audio Processing
```python
# Process multiple audio files efficiently
audio_files = ["track1.mp3", "track2.mp3", "track3.mp3"]

# Extract all audio tracks
for i, video_file in enumerate(["video1.mp4", "video2.mp4", "video3.mp4"]):
    await session.call_tool("extract_audio", {
        "input_path": video_file,
        "output_path": f"extracted_{i}.mp3",
        "quality": "medium"
    })

# Batch merge operations
await session.call_tool("merge_audio_tracks", {
    "input_paths": [f"extracted_{i}.mp3" for i in range(3)],
    "output_path": "combined_audio.mp3",
    "volumes": [1.0, 0.8, 0.6]
})
```

## 🎯 Next Steps

Ready to explore more audio capabilities?

- **[Effects & Filters](/tools/effects-filters/)** - Apply audio effects and enhancements
- **[Text & Graphics](/tools/text-graphics/)** - Add text overlays to your audio content
- **[Common Workflows](/guides/common-workflows/)** - Complete audio editing workflows
- **[Audio Editing Guide](/guides/audio-editing/)** - Advanced audio production techniques

---

**Questions about audio processing?** Check our [FAQ](/support/faq/) or explore the [examples section](/examples/audio-processing/).