---
title: Basic Video Editing Examples
description: Practical code examples for fundamental video editing operations
---

# Basic Video Editing Examples

This page provides practical, copy-paste examples for common basic video editing tasks. Each example includes setup, execution, and expected results.

## 🎬 Getting Started Examples

### Example 1: Your First Video Edit

**Scenario**: You have a long presentation video and want to extract the first 5 minutes, improve the colors, and resize it for web sharing.

```python
async def first_video_edit():
    """Complete beginner workflow: analyze, trim, enhance, resize"""
    
    # Step 1: Check what we're working with
    info = await session.call_tool("get_video_info", {
        "video_path": "presentation.mp4"
    })
    
    print(f"Original video: {info['duration']}s, {info['width']}x{info['height']}")
    print(f"File size: {info['file_size']}")
    
    # Step 2: Extract first 5 minutes
    await session.call_tool("trim_video", {
        "input_path": "presentation.mp4",
        "output_path": "presentation_intro.mp4",
        "start_time": 0,
        "duration": 300  # 5 minutes = 300 seconds
    })
    
    # Step 3: Enhance colors for better visual appeal
    await session.call_tool("apply_color_grading", {
        "input_path": "presentation_intro.mp4",
        "output_path": "presentation_enhanced.mp4",
        "brightness": 0.05,    # Slightly brighter
        "contrast": 1.1,       # More contrast
        "saturation": 1.2      # More vibrant colors
    })
    
    # Step 4: Resize for web (720p)
    await session.call_tool("resize_video", {
        "input_path": "presentation_enhanced.mp4",
        "output_path": "presentation_web.mp4",
        "width": 1280,
        "height": 720,
        "quality": "medium"    # Good balance of quality and file size
    })
    
    # Check final result
    final_info = await session.call_tool("get_video_info", {
        "video_path": "presentation_web.mp4"
    })
    
    print(f"Final video: {final_info['duration']}s, {final_info['width']}x{final_info['height']}")
    print(f"Final size: {final_info['file_size']}")
    print("✅ First video edit complete!")

# Run the example
await first_video_edit()
```

**Expected Output**:
```
Original video: 1800s, 1920x1080
File size: 250.5 MB
Final video: 300s, 1280x720  
Final size: 45.2 MB
✅ First video edit complete!
```

---

## ✂️ Trimming and Segmentation

### Example 2: Extract Multiple Segments

**Scenario**: Extract specific segments from a long video for highlights.

```python
async def extract_highlights():
    """Extract multiple highlight segments from a long video"""
    
    # Define interesting segments (start_time, duration, name)
    highlights = [
        (120, 30, "opening_statement"),      # 2:00-2:30
        (450, 45, "key_demonstration"),      # 7:30-8:15  
        (1200, 60, "audience_questions"),    # 20:00-21:00
        (1800, 90, "closing_remarks")        # 30:00-31:30
    ]
    
    original_video = "full_presentation.mp4"
    
    # Extract each highlight
    extracted_files = []
    for start_time, duration, name in highlights:
        output_file = f"highlight_{name}.mp4"
        
        await session.call_tool("trim_video", {
            "input_path": original_video,
            "output_path": output_file,
            "start_time": start_time,
            "duration": duration
        })
        
        extracted_files.append(output_file)
        print(f"✅ Extracted {name}: {duration}s from {start_time}s")
    
    # Optional: Combine all highlights into one video
    await session.call_tool("concatenate_videos", {
        "input_paths": extracted_files,
        "output_path": "combined_highlights.mp4",
        "transition_duration": 0.5  # Smooth transitions
    })
    
    print("✅ All highlights extracted and combined!")
    return extracted_files

# Usage
highlight_files = await extract_highlights()
```

### Example 3: Smart Trimming Based on Video Info

**Scenario**: Automatically trim videos to remove silent parts at beginning/end.

```python
async def smart_trim_video(input_video: str):
    """Intelligently trim video based on content analysis"""
    
    # Get video information
    info = await session.call_tool("get_video_info", {
        "video_path": input_video
    })
    
    duration = info['duration']
    has_audio = info['has_audio']
    
    # Smart trimming logic
    if duration < 60:
        # Short video - minimal trim
        start_trim = 2.0
        end_trim = 2.0
    elif duration < 300:  # 5 minutes
        # Medium video - moderate trim
        start_trim = 5.0
        end_trim = 5.0
    else:
        # Long video - more aggressive trim
        start_trim = 10.0
        end_trim = 10.0
    
    # Calculate new duration
    new_duration = duration - start_trim - end_trim
    
    if new_duration > 10:  # Ensure we don't over-trim
        output_file = f"trimmed_{input_video}"
        
        await session.call_tool("trim_video", {
            "input_path": input_video,
            "output_path": output_file,
            "start_time": start_trim,
            "duration": new_duration
        })
        
        print(f"✅ Smart trimmed: {duration}s → {new_duration}s")
        return output_file
    else:
        print("⚠️ Video too short for smart trimming")
        return input_video

# Usage
trimmed_video = await smart_trim_video("raw_recording.mp4")
```

---

## 📐 Resizing and Format Optimization

### Example 4: Multi-Platform Export

**Scenario**: Create versions of a video optimized for different platforms.

```python
async def multi_platform_export(source_video: str):
    """Export video in multiple formats for different platforms"""
    
    # Platform specifications
    platforms = {
        "youtube": {
            "width": 1920, "height": 1080,
            "quality": "high",
            "description": "YouTube 1080p"
        },
        "instagram_feed": {
            "width": 1080, "height": 1080,  # Square format
            "quality": "high",
            "description": "Instagram Feed Post"
        },
        "instagram_story": {
            "width": 1080, "height": 1920,  # Vertical
            "quality": "medium",
            "description": "Instagram Story"
        },
        "twitter": {
            "width": 1280, "height": 720,
            "quality": "medium", 
            "description": "Twitter Post"
        },
        "web_thumbnail": {
            "width": 640, "height": 360,
            "quality": "low",
            "description": "Web Preview"
        }
    }
    
    results = {}
    
    for platform, specs in platforms.items():
        output_file = f"{platform}_{source_video}"
        
        await session.call_tool("resize_video", {
            "input_path": source_video,
            "output_path": output_file,
            "width": specs["width"],
            "height": specs["height"],
            "quality": specs["quality"],
            "maintain_aspect": True
        })
        
        # Get file size for comparison
        info = await session.call_tool("get_video_info", {
            "video_path": output_file
        })
        
        results[platform] = {
            "file": output_file,
            "size": info["file_size"],
            "resolution": f"{info['width']}x{info['height']}",
            "description": specs["description"]
        }
        
        print(f"✅ {specs['description']}: {info['file_size']}")
    
    return results

# Usage
platform_versions = await multi_platform_export("master_video.mp4")

# Print summary
print("\n📊 Platform Export Summary:")
for platform, details in platform_versions.items():
    print(f"{platform}: {details['resolution']} - {details['size']}")
```

### Example 5: Quality Comparison

**Scenario**: Test different quality settings to find the best balance.

```python
async def quality_comparison_test(input_video: str):
    """Test different quality settings for optimal file size/quality balance"""
    
    quality_levels = ["low", "medium", "high", "ultra"]
    results = {}
    
    # Get original file info
    original_info = await session.call_tool("get_video_info", {
        "video_path": input_video
    })
    
    print(f"Original: {original_info['file_size']} - {original_info['width']}x{original_info['height']}")
    
    for quality in quality_levels:
        output_file = f"quality_test_{quality}_{input_video}"
        
        await session.call_tool("resize_video", {
            "input_path": input_video,
            "output_path": output_file,
            "scale_factor": 1.0,  # Keep same size, change quality only
            "quality": quality
        })
        
        # Analyze result
        test_info = await session.call_tool("get_video_info", {
            "video_path": output_file
        })
        
        # Calculate compression ratio
        original_size_mb = float(original_info['file_size'].split()[0])
        test_size_mb = float(test_info['file_size'].split()[0])
        compression_ratio = test_size_mb / original_size_mb
        
        results[quality] = {
            "file": output_file,
            "size": test_info["file_size"],
            "ratio": f"{compression_ratio:.2f}x",
            "bitrate": test_info["bitrate"]
        }
        
        print(f"{quality:6}: {test_info['file_size']:>8} ({compression_ratio:.2f}x)")
    
    # Recommend best quality
    print("\n💡 Recommendations:")
    print("- Low: Good for previews and drafts")
    print("- Medium: Best for social media and web")
    print("- High: Professional output and final delivery")
    print("- Ultra: Archive and master copies")
    
    return results

# Usage
quality_results = await quality_comparison_test("sample_video.mp4")
```

---

## 🔗 Video Joining and Concatenation

### Example 6: Smart Video Concatenation

**Scenario**: Join multiple video clips with automatic format normalization.

```python
async def smart_concatenation(video_files: list):
    """Intelligently concatenate videos with format normalization"""
    
    print("🔍 Analyzing input videos...")
    
    # Analyze all input videos
    video_info = []
    for video_file in video_files:
        info = await session.call_tool("get_video_info", {
            "video_path": video_file
        })
        video_info.append({
            "file": video_file,
            "duration": info["duration"],
            "resolution": f"{info['width']}x{info['height']}",
            "fps": info["fps"],
            "format": info["format"]
        })
        print(f"  {video_file}: {info['duration']}s, {info['width']}x{info['height']}")
    
    # Determine target format (most common resolution and highest fps)
    resolutions = [info["resolution"] for info in video_info]
    target_resolution = max(set(resolutions), key=resolutions.count)
    target_fps = max(info["fps"] for info in video_info)
    
    print(f"\n🎯 Target format: {target_resolution} @ {target_fps}fps")
    
    # Normalize videos that don't match target format
    normalized_files = []
    for info in video_info:
        if info["resolution"] != target_resolution or info["fps"] != target_fps:
            normalized_file = f"normalized_{info['file']}"
            width, height = map(int, target_resolution.split('x'))
            
            await session.call_tool("resize_video", {
                "input_path": info["file"],
                "output_path": normalized_file,
                "width": width,
                "height": height,
                "quality": "high"
            })
            
            normalized_files.append(normalized_file)
            print(f"  📐 Normalized: {info['file']} → {normalized_file}")
        else:
            normalized_files.append(info["file"])
            print(f"  ✅ Already correct: {info['file']}")
    
    # Concatenate normalized videos
    final_output = "concatenated_final.mp4"
    await session.call_tool("concatenate_videos", {
        "input_paths": normalized_files,
        "output_path": final_output,
        "transition_duration": 1.0  # Smooth 1-second transitions
    })
    
    # Get final video info
    final_info = await session.call_tool("get_video_info", {
        "video_path": final_output
    })
    
    total_duration = sum(info["duration"] for info in video_info)
    print(f"\n✅ Concatenation complete!")
    print(f"   Total duration: {final_info['duration']}s (expected: {total_duration}s)")
    print(f"   Final size: {final_info['file_size']}")
    print(f"   Output: {final_output}")
    
    return final_output

# Usage
video_clips = ["intro.mp4", "main_content.avi", "outro.mov"]
final_video = await smart_concatenation(video_clips)
```

### Example 7: Chapter-Based Video Assembly

**Scenario**: Create a structured video with chapters and seamless transitions.

```python
async def create_chaptered_video():
    """Create a professional video with chapters and transitions"""
    
    # Define video structure
    chapters = [
        {
            "name": "Introduction",
            "file": "intro.mp4",
            "transition": "fade",
            "duration": 30
        },
        {
            "name": "Overview", 
            "file": "overview.mp4",
            "transition": "crossfade",
            "duration": 120
        },
        {
            "name": "Demonstration",
            "file": "demo.mp4", 
            "transition": "crossfade",
            "duration": 300
        },
        {
            "name": "Conclusion",
            "file": "conclusion.mp4",
            "transition": "fade",
            "duration": 45
        }
    ]
    
    print("🎬 Creating chaptered video...")
    
    # Process each chapter
    processed_chapters = []
    for i, chapter in enumerate(chapters):
        chapter_file = f"chapter_{i:02d}_{chapter['name'].lower()}.mp4"
        
        # Trim to exact duration if needed
        await session.call_tool("trim_video", {
            "input_path": chapter["file"],
            "output_path": chapter_file,
            "start_time": 0,
            "duration": chapter["duration"]
        })
        
        processed_chapters.append(chapter_file)
        print(f"  ✅ Chapter {i+1}: {chapter['name']} ({chapter['duration']}s)")
    
    # Assemble with transitions
    await session.call_tool("concatenate_videos", {
        "input_paths": processed_chapters,
        "output_path": "final_chaptered_video.mp4",
        "transition_duration": 2.0  # 2-second transitions between chapters
    })
    
    # Create chapter markers file
    chapter_markers = []
    current_time = 0
    for i, chapter in enumerate(chapters):
        chapter_markers.append(f"{current_time:02d}:{(current_time % 60):02d} - {chapter['name']}")
        current_time += chapter["duration"] + 2  # Add transition time
    
    # Save chapter info
    with open("chapters.txt", "w") as f:
        f.write("Video Chapters:\n")
        f.write("\n".join(chapter_markers))
    
    print(f"\n✅ Chaptered video created: final_chaptered_video.mp4")
    print("📑 Chapter markers saved to: chapters.txt")
    
    return "final_chaptered_video.mp4"

# Usage
chaptered_video = await create_chaptered_video()
```

---

## 🎯 Practical Automation Examples

### Example 8: Batch Processing Workflow

**Scenario**: Process multiple videos with consistent settings.

```python
async def batch_process_folder():
    """Process all videos in a folder with consistent settings"""
    
    # Get list of videos to process
    video_list = await session.read_resource("videos://list")
    
    # Define processing pipeline
    processing_steps = [
        {
            "operation": "trim_start_end",
            "start_trim": 3.0,    # Remove first 3 seconds
            "end_trim": 2.0       # Remove last 2 seconds
        },
        {
            "operation": "color_enhancement",
            "brightness": 0.03,
            "contrast": 1.08,
            "saturation": 1.15
        },
        {
            "operation": "resize_720p",
            "width": 1280,
            "height": 720,
            "quality": "medium"
        }
    ]
    
    processed_videos = []
    total_videos = len(video_list["videos"])
    
    print(f"🔄 Processing {total_videos} videos...")
    
    for i, video in enumerate(video_list["videos"], 1):
        video_name = video["name"]
        print(f"\n📹 Processing {i}/{total_videos}: {video_name}")
        
        current_file = video_name
        
        # Step 1: Smart trimming
        if video["duration"] > 10:  # Only trim if video is long enough
            trimmed_file = f"01_trimmed_{video_name}"
            trim_duration = video["duration"] - 3.0 - 2.0  # Remove start and end
            
            await session.call_tool("trim_video", {
                "input_path": current_file,
                "output_path": trimmed_file,
                "start_time": 3.0,
                "duration": trim_duration
            })
            current_file = trimmed_file
            print(f"  ✅ Trimmed: {trim_duration:.1f}s")
        
        # Step 2: Color enhancement
        enhanced_file = f"02_enhanced_{video_name}"
        await session.call_tool("apply_color_grading", {
            "input_path": current_file,
            "output_path": enhanced_file,
            "brightness": 0.03,
            "contrast": 1.08,
            "saturation": 1.15
        })
        current_file = enhanced_file
        print("  ✅ Color enhanced")
        
        # Step 3: Resize to 720p
        final_file = f"final_{video_name}"
        await session.call_tool("resize_video", {
            "input_path": current_file,
            "output_path": final_file,
            "width": 1280,
            "height": 720,
            "quality": "medium"
        })
        
        processed_videos.append(final_file)
        print(f"  ✅ Resized to 720p: {final_file}")
    
    print(f"\n🎉 Batch processing complete!")
    print(f"   Processed: {len(processed_videos)} videos")
    print(f"   Output files: final_*.mp4")
    
    return processed_videos

# Usage
processed_files = await batch_process_folder()
```

### Example 9: Quality Control Automation

**Scenario**: Automatically check and fix common video issues.

```python
async def quality_control_check(video_file: str):
    """Automatically detect and fix common video quality issues"""
    
    print(f"🔍 Quality control check: {video_file}")
    
    # Get video information
    info = await session.call_tool("get_video_info", {
        "video_path": video_file
    })
    
    issues_found = []
    fixes_applied = []
    current_file = video_file
    
    # Check 1: Resolution too high for typical use
    if info["width"] > 1920:
        issues_found.append(f"High resolution: {info['width']}x{info['height']}")
        
        # Fix: Downscale to 1080p
        downscaled_file = f"qc_downscaled_{video_file}"
        await session.call_tool("resize_video", {
            "input_path": current_file,
            "output_path": downscaled_file,
            "width": 1920,
            "height": 1080,
            "quality": "high"
        })
        current_file = downscaled_file
        fixes_applied.append("Downscaled to 1080p")
    
    # Check 2: Very long duration (might need trimming suggestion)
    if info["duration"] > 1800:  # 30 minutes
        issues_found.append(f"Very long video: {info['duration']/60:.1f} minutes")
        print(f"  💡 Suggestion: Consider splitting into shorter segments")
    
    # Check 3: Low bitrate (might indicate quality issues)
    if info["bitrate"] < 1000000:  # Less than 1 Mbps
        issues_found.append(f"Low bitrate: {info['bitrate']/1000:.0f} kbps")
        
        # Fix: Re-encode with better quality
        reencoded_file = f"qc_reencoded_{video_file}"
        await session.call_tool("resize_video", {
            "input_path": current_file,
            "output_path": reencoded_file,
            "scale_factor": 1.0,  # Keep same size
            "quality": "high"     # But improve quality
        })
        current_file = reencoded_file
        fixes_applied.append("Re-encoded with higher quality")
    
    # Check 4: Missing audio
    if not info["has_audio"]:
        issues_found.append("No audio track detected")
        print(f"  💡 Suggestion: Consider adding background music or narration")
    
    # Apply automatic color correction if no major issues
    if len(issues_found) <= 1:
        corrected_file = f"qc_corrected_{video_file}"
        await session.call_tool("apply_color_grading", {
            "input_path": current_file,
            "output_path": corrected_file,
            "brightness": 0.02,
            "contrast": 1.05,
            "saturation": 1.1
        })
        current_file = corrected_file
        fixes_applied.append("Applied automatic color correction")
    
    # Generate report
    print(f"\n📊 Quality Control Report:")
    if issues_found:
        print(f"  Issues found: {len(issues_found)}")
        for issue in issues_found:
            print(f"    ⚠️  {issue}")
    else:
        print("  ✅ No issues detected")
    
    if fixes_applied:
        print(f"  Fixes applied: {len(fixes_applied)}")
        for fix in fixes_applied:
            print(f"    🔧 {fix}")
        print(f"  Output file: {current_file}")
    else:
        print("  No fixes needed")
    
    return {
        "issues": issues_found,
        "fixes": fixes_applied,
        "output_file": current_file if fixes_applied else video_file
    }

# Usage  
qc_result = await quality_control_check("raw_video.mp4")
```

---

## 🎯 Next Steps

These examples demonstrate fundamental video editing patterns. Ready to explore more advanced techniques?

- **[Audio Processing Examples](/examples/audio-processing/)** - Audio extraction, mixing, and enhancement
- **[Visual Effects Examples](/examples/visual-effects/)** - Color grading, effects, and compositing
- **[Automation Examples](/examples/automation/)** - Batch processing and workflow automation
- **[Common Workflows](/guides/common-workflows/)** - Complete production workflows

**Questions about these examples?** Check the [FAQ](/support/faq/) or explore individual [tool documentation](/tools/overview/).