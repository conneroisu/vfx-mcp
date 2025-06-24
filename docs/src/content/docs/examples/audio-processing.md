---
title: Audio Processing Examples
description: Practical examples for audio editing and processing workflows
---

# Audio Processing Examples

Practical examples for audio editing and processing workflows using the VFX MCP Server.

## Basic Audio Operations

### Extract Audio from Video
```python
# Extract audio track from video file
result = await extract_audio("presentation.mp4", "presentation_audio.wav")
print(result)
# Output: "Audio extracted successfully: presentation_audio.wav"
```

### Add Background Music
```python
# Mix background music with existing video audio
result = await add_audio(
    input_path="video.mp4",
    audio_path="background_music.mp3",
    output_path="video_with_music.mp4",
    mode="mix",
    volume=0.3  # Background music at 30% volume
)
```

### Replace Audio Track
```python
# Replace original audio with new track
result = await add_audio(
    input_path="video.mp4",
    audio_path="new_narration.wav",
    output_path="dubbed_video.mp4",
    mode="replace"
)
```

## Audio Enhancement Examples

### Normalize Audio Levels
```python
# Normalize audio to standard levels
result = await apply_filter(
    input_path="quiet_audio.wav",
    output_path="normalized_audio.wav",
    filter_name="volume",
    filter_params="normalize"
)
```

### Remove Background Noise
```python
# Apply high-pass filter to remove low-frequency noise
result = await apply_filter(
    input_path="noisy_audio.wav",
    output_path="clean_audio.wav",
    filter_name="highpass",
    filter_params="f=100"
)

# Apply low-pass filter to remove high-frequency noise
result = await apply_filter(
    input_path="clean_audio.wav",
    output_path="filtered_audio.wav",
    filter_name="lowpass",
    filter_params="f=8000"
)
```

### Boost Audio Volume
```python
# Increase volume by 6dB
result = await apply_filter(
    input_path="quiet_audio.wav",
    output_path="louder_audio.wav",
    filter_name="volume",
    filter_params="6dB"
)
```

## Advanced Audio Processing

### Audio Synchronization
```python
# Add 500ms delay to audio track
result = await apply_filter(
    input_path="out_of_sync.wav",
    output_path="synced_audio.wav",
    filter_name="adelay",
    filter_params="500"
)

# Speed up audio by 5% to match video
result = await change_speed(
    input_path="slow_audio.wav",
    output_path="synced_audio.wav",
    speed_factor=1.05
)
```

### Audio Compression
```python
# Apply dynamic range compression
result = await apply_filter(
    input_path="dynamic_audio.wav",
    output_path="compressed_audio.wav",
    filter_name="compand",
    filter_params="0.3,1:6:-70/-60,-20"
)
```

### Echo and Reverb Effects
```python
# Add echo effect
result = await apply_filter(
    input_path="dry_audio.wav",
    output_path="echo_audio.wav",
    filter_name="aecho",
    filter_params="0.8:0.9:1000:0.3"
)

# Add reverb effect
result = await apply_filter(
    input_path="dry_audio.wav",
    output_path="reverb_audio.wav",
    filter_name="afreqshift",
    filter_params="shift=0"
)
```

## Podcast Production Workflow

### Complete Podcast Processing
```python
async def process_podcast(raw_audio_path: str, output_path: str):
    """Complete podcast production pipeline"""
    
    # Step 1: Remove background noise
    step1 = await apply_filter(
        raw_audio_path, "temp_step1.wav",
        "highpass", "f=80"
    )
    
    # Step 2: Normalize audio levels
    step2 = await apply_filter(
        "temp_step1.wav", "temp_step2.wav",
        "volume", "normalize"
    )
    
    # Step 3: Apply compression for consistent levels
    step3 = await apply_filter(
        "temp_step2.wav", "temp_step3.wav",
        "compand", "0.02,0.05:-60/-60,-30/-15,-20/-10,-5/-5,0/-3:6:0:-90:0.1"
    )
    
    # Step 4: Add final limiting
    final = await apply_filter(
        "temp_step3.wav", output_path,
        "alimiter", "level_in=1:level_out=0.95"
    )
    
    # Cleanup temporary files
    import os
    for temp_file in ["temp_step1.wav", "temp_step2.wav", "temp_step3.wav"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    return final

# Process podcast episode
result = await process_podcast("raw_podcast.wav", "final_podcast.wav")
```

## Music Video Audio Processing

### Sync Video to Music Beat
```python
async def sync_video_to_music(video_path: str, music_path: str, output_path: str):
    """Sync video content to music rhythm"""
    
    # Extract original video audio for reference
    await extract_audio(video_path, "original_audio.wav")
    
    # Replace video audio with music track
    synced_video = await add_audio(
        video_path, music_path, "temp_synced.mp4", mode="replace"
    )
    
    # Fine-tune timing if needed
    final_video = await apply_filter(
        "temp_synced.mp4", output_path,
        "atempo", "1.02"  # Slight speed adjustment
    )
    
    return final_video

# Create music video
result = await sync_video_to_music("dance_video.mp4", "beat_track.mp3", "music_video.mp4")
```

## Voice-over Integration

### Add Narration to Video
```python
async def add_narration(video_path: str, voiceover_path: str, output_path: str):
    """Add voice-over narration with background audio ducking"""
    
    # Extract original video audio
    await extract_audio(video_path, "background_audio.wav")
    
    # Reduce background audio volume
    reduced_bg = await apply_filter(
        "background_audio.wav", "ducked_background.wav",
        "volume", "0.3"  # Reduce to 30% volume
    )
    
    # Mix voice-over with reduced background
    mixed_audio = await add_audio(
        "ducked_background.wav", voiceover_path,
        "mixed_narration.wav", mode="mix"
    )
    
    # Replace video audio with mixed track
    final_video = await add_audio(
        video_path, "mixed_narration.wav", output_path, mode="replace"
    )
    
    return final_video

# Add narration to educational video
result = await add_narration("lesson.mp4", "narration.wav", "narrated_lesson.mp4")
```

## Audio Quality Assessment

### Check Audio Properties
```python
async def analyze_audio_quality(audio_path: str):
    """Analyze audio file properties"""
    
    # Get detailed audio information
    info = await get_video_info(audio_path)
    
    # Parse audio properties from info
    import json
    audio_data = json.loads(info)
    
    audio_streams = [stream for stream in audio_data.get('streams', []) 
                    if stream.get('codec_type') == 'audio']
    
    if audio_streams:
        audio_info = audio_streams[0]
        return {
            'codec': audio_info.get('codec_name'),
            'sample_rate': audio_info.get('sample_rate'),
            'channels': audio_info.get('channels'),
            'bit_rate': audio_info.get('bit_rate'),
            'duration': audio_info.get('duration')
        }
    
    return None

# Analyze audio file
quality_info = await analyze_audio_quality("audio_file.wav")
print(f"Audio quality: {quality_info}")
```

## Batch Audio Processing

### Process Multiple Audio Files
```python
import os
import asyncio

async def batch_audio_processing(input_directory: str, output_directory: str):
    """Process multiple audio files with consistent settings"""
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all audio files
    audio_files = [f for f in os.listdir(input_directory) 
                  if f.lower().endswith(('.wav', '.mp3', '.aac', '.flac'))]
    
    async def process_single_file(filename):
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, f"processed_{filename}")
        
        # Apply consistent processing
        await apply_filter(input_path, output_path, "volume", "normalize")
        return f"Processed: {filename}"
    
    # Process files concurrently (limit to 3 at a time)
    semaphore = asyncio.Semaphore(3)
    
    async def process_with_limit(filename):
        async with semaphore:
            return await process_single_file(filename)
    
    # Process all files
    results = await asyncio.gather(*[process_with_limit(f) for f in audio_files])
    return results

# Process all audio files in directory
results = await batch_audio_processing("raw_audio/", "processed_audio/")
for result in results:
    print(result)
```