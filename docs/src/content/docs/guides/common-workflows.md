---
title: Common Workflows
description: Typical video editing workflows and step-by-step guides for common tasks
---

# Common Workflows

This guide covers the most common video editing workflows using the VFX MCP Server. Each workflow includes step-by-step instructions, code examples, and best practices for achieving professional results.

## 🎬 Basic Video Editing

### Workflow: Trim, Enhance, and Export

**Use Case**: Basic video editing for social media, presentations, or personal projects.

**Steps**:
1. **Analyze the video** to understand its properties
2. **Trim** to the desired segment
3. **Enhance** with color grading and effects
4. **Resize** for target platform
5. **Export** in optimized format

**Implementation**:
```python
async def basic_editing_workflow(input_video: str, output_video: str):
    # Step 1: Get video information
    info = await session.call_tool("get_video_info", {
        "video_path": input_video
    })
    print(f"Original video: {info['duration']}s, {info['width']}x{info['height']}")
    
    # Step 2: Trim to first 60 seconds
    await session.call_tool("trim_video", {
        "input_path": input_video,
        "output_path": "temp_trimmed.mp4",
        "start_time": 0,
        "duration": 60
    })
    
    # Step 3: Apply color grading
    await session.call_tool("apply_color_grading", {
        "input_path": "temp_trimmed.mp4",
        "output_path": "temp_graded.mp4",
        "brightness": 0.05,
        "contrast": 1.1,
        "saturation": 1.2
    })
    
    # Step 4: Resize for Instagram (square format)
    await session.call_tool("resize_video", {
        "input_path": "temp_graded.mp4",
        "output_path": output_video,
        "width": 1080,
        "height": 1080,
        "quality": "high"
    })
    
    print("✅ Basic editing workflow completed!")

# Usage
await basic_editing_workflow("raw_footage.mp4", "instagram_post.mp4")
```

**Platform-specific Variations**:
```python
# Platform-specific export settings
PLATFORM_SPECS = {
    "instagram_post": {"width": 1080, "height": 1080},
    "instagram_story": {"width": 1080, "height": 1920},
    "youtube": {"width": 1920, "height": 1080},
    "tiktok": {"width": 1080, "height": 1920},
    "twitter": {"width": 1280, "height": 720}
}

async def export_for_platform(input_video: str, platform: str):
    specs = PLATFORM_SPECS[platform]
    await session.call_tool("resize_video", {
        "input_path": input_video,
        "output_path": f"{platform}_output.mp4",
        "width": specs["width"],
        "height": specs["height"],
        "quality": "high"
    })
```

---

## 🎵 Podcast Production

### Workflow: Audio-First Video Creation

**Use Case**: Convert video interviews or recordings into polished podcast episodes with professional audio.

**Steps**:
1. **Extract audio** from video source
2. **Enhance audio** quality and levels
3. **Add intro/outro music**
4. **Create audio visualization**
5. **Combine with video** for video podcast

**Implementation**:
```python
async def podcast_production_workflow(interview_video: str, intro_music: str, outro_music: str):
    # Step 1: Extract high-quality audio
    await session.call_tool("extract_audio", {
        "input_path": interview_video,
        "output_path": "raw_interview.wav",
        "format": "wav",
        "quality": "ultra"
    })
    
    # Step 2: Get video duration for music timing
    info = await session.call_tool("get_video_info", {
        "video_path": interview_video
    })
    interview_duration = info['duration']
    
    # Step 3: Create complete audio mix
    await session.call_tool("merge_audio_tracks", {
        "input_paths": [
            intro_music,
            "raw_interview.wav",
            outro_music
        ],
        "output_path": "podcast_audio.mp3",
        "volumes": [0.8, 1.0, 0.8],
        "delays": [0.0, 10.0, interview_duration + 15.0],  # 10s intro, 5s gap before outro
        "crossfade_duration": 2.0
    })
    
    # Step 4: Create audio spectrum visualization
    await session.call_tool("extract_audio_spectrum", {
        "input_path": "podcast_audio.mp3",
        "output_path": "audio_visualization.mp4",
        "visualization_type": "waveform",
        "color_scheme": "cool",
        "width": 1920,
        "height": 1080
    })
    
    # Step 5: Add final audio to original video (optional)
    await session.call_tool("add_audio", {
        "video_path": interview_video,
        "audio_path": "podcast_audio.mp3",
        "output_path": "final_podcast.mp4",
        "mode": "replace"
    })
    
    print("✅ Podcast production completed!")
    return ["podcast_audio.mp3", "audio_visualization.mp4", "final_podcast.mp4"]

# Usage
await podcast_production_workflow(
    "interview.mp4", 
    "intro_music.mp3", 
    "outro_music.mp3"
)
```

**Advanced Audio Processing**:
```python
async def advanced_podcast_audio(interview_video: str):
    # Extract and enhance audio
    await session.call_tool("extract_audio", {
        "input_path": interview_video,
        "output_path": "raw_audio.wav",
        "format": "wav",
        "quality": "ultra"
    })
    
    # Apply audio filters for professional sound
    await session.call_tool("apply_filter", {
        "input_path": "raw_audio.wav",
        "output_path": "enhanced_audio.wav",
        "filter_string": "highpass=f=80,lowpass=f=10000,dynaudnorm"
    })
    
    return "enhanced_audio.wav"
```

---

## 🎨 Creative Video Projects

### Workflow: Music Video Production

**Use Case**: Create engaging music videos with synchronized visuals and professional effects.

**Steps**:
1. **Prepare source materials** (video clips, images)
2. **Create slideshow** from images
3. **Add motion effects** and transitions
4. **Synchronize with audio**
5. **Apply creative grading**

**Implementation**:
```python
async def music_video_workflow(image_folder: str, music_track: str, video_clips: list):
    # Step 1: Create slideshow from images
    await session.call_tool("create_video_slideshow", {
        "image_folder": image_folder,
        "output_path": "image_slideshow.mp4",
        "duration_per_image": 3.0,
        "transition_duration": 1.0,
        "fps": 30
    })
    
    # Step 2: Concatenate with video clips
    all_clips = ["image_slideshow.mp4"] + video_clips
    await session.call_tool("concatenate_videos", {
        "input_paths": all_clips,
        "output_path": "combined_visuals.mp4",
        "transition_duration": 0.5
    })
    
    # Step 3: Add motion effects
    await session.call_tool("apply_motion_blur", {
        "input_path": "combined_visuals.mp4",
        "output_path": "motion_enhanced.mp4",
        "angle": 0.0,
        "distance": 3.0
    })
    
    # Step 4: Apply creative color grading
    await session.call_tool("apply_color_grading", {
        "input_path": "motion_enhanced.mp4",
        "output_path": "color_graded.mp4",
        "contrast": 1.3,
        "saturation": 1.5,
        "temperature": -0.2,
        "shadows": 0.1,
        "highlights": -0.05
    })
    
    # Step 5: Add synchronized music
    await session.call_tool("add_audio", {
        "video_path": "color_graded.mp4",
        "audio_path": music_track,
        "output_path": "final_music_video.mp4",
        "mode": "replace"
    })
    
    # Step 6: Create audio visualization overlay (optional)
    await session.call_tool("extract_audio_spectrum", {
        "input_path": "final_music_video.mp4",
        "output_path": "spectrum_overlay.mp4",
        "visualization_type": "bars",
        "color_scheme": "fire"
    })
    
    print("✅ Music video production completed!")
```

---

## 📺 Professional Video Production

### Workflow: Corporate Video Creation

**Use Case**: Professional corporate videos with branding, transitions, and polished presentation.

**Steps**:
1. **Organize source materials**
2. **Create branded intro/outro**
3. **Process main content** with professional grading
4. **Add professional transitions**
5. **Final assembly** and export

**Implementation**:
```python
async def corporate_video_workflow(intro_video: str, main_content: list, outro_video: str, logo_overlay: str):
    # Step 1: Process main content with professional grading
    processed_clips = []
    for i, clip in enumerate(main_content):
        # Standardize each clip
        await session.call_tool("resize_video", {
            "input_path": clip,
            "output_path": f"standardized_{i}.mp4",
            "width": 1920,
            "height": 1080,
            "quality": "high"
        })
        
        # Apply professional color grading
        await session.call_tool("apply_color_grading", {
            "input_path": f"standardized_{i}.mp4",
            "output_path": f"graded_{i}.mp4",
            "brightness": 0.02,
            "contrast": 1.08,
            "saturation": 0.95,
            "shadows": 0.03
        })
        
        processed_clips.append(f"graded_{i}.mp4")
    
    # Step 2: Create smooth transitions between clips
    await session.call_tool("create_video_transitions", {
        "input_paths": processed_clips,
        "output_path": "main_with_transitions.mp4",
        "transition_type": "crossfade",
        "transition_duration": 1.0
    })
    
    # Step 3: Assemble complete video
    full_sequence = [intro_video, "main_with_transitions.mp4", outro_video]
    await session.call_tool("concatenate_videos", {
        "input_paths": full_sequence,
        "output_path": "assembled_video.mp4",
        "transition_duration": 0.5
    })
    
    # Step 4: Add logo overlay (if provided)
    if logo_overlay:
        await session.call_tool("create_picture_in_picture", {
            "main_video": "assembled_video.mp4",
            "overlay_video": logo_overlay,
            "output_path": "final_corporate_video.mp4",
            "position": "top-right",
            "scale": 0.15,
            "opacity": 0.8
        })
    else:
        # Copy to final output
        await session.call_tool("trim_video", {
            "input_path": "assembled_video.mp4",
            "output_path": "final_corporate_video.mp4",
            "start_time": 0
        })
    
    print("✅ Corporate video production completed!")
```

---

## 🚀 Content Creation Workflows

### Workflow: Multi-Platform Content Creation

**Use Case**: Create content for multiple social media platforms from a single source video.

**Implementation**:
```python
async def multi_platform_content(source_video: str):
    # First, get source video info
    info = await session.call_tool("get_video_info", {
        "video_path": source_video
    })
    
    # Define platform requirements
    platforms = {
        "youtube": {
            "width": 1920, "height": 1080,
            "duration": min(info['duration'], 600),  # Max 10 minutes
            "start_time": 0
        },
        "instagram_feed": {
            "width": 1080, "height": 1080,
            "duration": min(info['duration'], 60),   # Max 1 minute
            "start_time": 0
        },
        "instagram_story": {
            "width": 1080, "height": 1920,
            "duration": min(info['duration'], 15),   # Max 15 seconds
            "start_time": 0
        },
        "tiktok": {
            "width": 1080, "height": 1920,
            "duration": min(info['duration'], 60),   # Max 1 minute
            "start_time": 0
        }
    }
    
    results = {}
    
    for platform, specs in platforms.items():
        # Trim to platform duration
        await session.call_tool("trim_video", {
            "input_path": source_video,
            "output_path": f"temp_{platform}_trimmed.mp4",
            "start_time": specs["start_time"],
            "duration": specs["duration"]
        })
        
        # Apply platform-specific color grading
        if platform in ["instagram_feed", "instagram_story"]:
            # More vibrant for Instagram
            grading_params = {
                "contrast": 1.15,
                "saturation": 1.3,
                "brightness": 0.05
            }
        else:
            # Standard grading
            grading_params = {
                "contrast": 1.1,
                "saturation": 1.1,
                "brightness": 0.02
            }
        
        await session.call_tool("apply_color_grading", {
            "input_path": f"temp_{platform}_trimmed.mp4",
            "output_path": f"temp_{platform}_graded.mp4",
            **grading_params
        })
        
        # Resize for platform
        await session.call_tool("resize_video", {
            "input_path": f"temp_{platform}_graded.mp4",
            "output_path": f"{platform}_final.mp4",
            "width": specs["width"],
            "height": specs["height"],
            "quality": "high"
        })
        
        results[platform] = f"{platform}_final.mp4"
    
    print("✅ Multi-platform content creation completed!")
    return results

# Usage
platform_videos = await multi_platform_content("master_video.mp4")
print(f"Created videos for: {', '.join(platform_videos.keys())}")
```

---

## 🔧 Automation and Batch Processing

### Workflow: Batch Video Processing

**Use Case**: Process multiple videos with consistent settings for efficiency.

**Implementation**:
```python
async def batch_processing_workflow(input_directory: str, processing_config: dict):
    # Get list of all videos
    video_list = await session.read_resource("videos://list")
    
    results = []
    
    for video in video_list['videos']:
        video_name = video['name']
        print(f"Processing {video_name}...")
        
        try:
            # Apply standard processing pipeline
            if processing_config.get('trim'):
                trim_config = processing_config['trim']
                await session.call_tool("trim_video", {
                    "input_path": video_name,
                    "output_path": f"trimmed_{video_name}",
                    **trim_config
                })
                current_file = f"trimmed_{video_name}"
            else:
                current_file = video_name
            
            if processing_config.get('color_grade'):
                grade_config = processing_config['color_grade']
                await session.call_tool("apply_color_grading", {
                    "input_path": current_file,
                    "output_path": f"graded_{video_name}",
                    **grade_config
                })
                current_file = f"graded_{video_name}"
            
            if processing_config.get('resize'):
                resize_config = processing_config['resize']
                await session.call_tool("resize_video", {
                    "input_path": current_file,
                    "output_path": f"final_{video_name}",
                    **resize_config
                })
                current_file = f"final_{video_name}"
            
            results.append({
                "original": video_name,
                "processed": current_file,
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "original": video_name,
                "processed": None,
                "status": "error",
                "error": str(e)
            })
            print(f"❌ Error processing {video_name}: {e}")
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    total = len(results)
    print(f"✅ Batch processing completed: {successful}/{total} videos processed successfully")
    
    return results

# Usage example
batch_config = {
    "trim": {"start_time": 0, "duration": 60},
    "color_grade": {"contrast": 1.1, "saturation": 1.1},
    "resize": {"width": 1920, "height": 1080, "quality": "medium"}
}

results = await batch_processing_workflow("./videos", batch_config)
```

## 📊 Performance Optimization Tips

### Efficient Workflow Patterns

1. **Minimize Re-encoding**:
   ```python
   # Good: Use copy mode when possible
   await session.call_tool("trim_video", {
       "input_path": "source.mp4",
       "output_path": "trimmed.mp4",
       "start_time": 10,
       "duration": 30
       # Uses copy mode - very fast
   })
   ```

2. **Batch Similar Operations**:
   ```python
   # Process all videos with same settings together
   for video in video_list:
       await session.call_tool("apply_color_grading", {
           "input_path": video,
           "output_path": f"graded_{video}",
           "contrast": 1.1,
           "saturation": 1.1
       })
   ```

3. **Use Appropriate Quality Settings**:
   ```python
   QUALITY_MAP = {
       "preview": "low",
       "social_media": "medium", 
       "professional": "high",
       "archive": "ultra"
   }
   ```

## 🎯 Next Steps

Explore more specific techniques:

- **[Audio Editing Guide](/guides/audio-editing/)** - Advanced audio workflows
- **[Color Grading Guide](/guides/color-grading/)** - Professional color techniques
- **[Batch Processing Guide](/guides/batch-processing/)** - Efficient automation
- **[VFX and Compositing](/guides/vfx-compositing/)** - Advanced visual effects

---

**Need help with a specific workflow?** Check our [examples section](/examples/basic-editing/) or [FAQ](/support/faq/) for more guidance.