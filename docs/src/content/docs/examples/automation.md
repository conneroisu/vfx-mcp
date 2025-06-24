---
title: Automation Scripts
description: Automated video processing workflows and batch operation examples
---


Automated video processing workflows and batch operation examples using the VFX MCP Server.

## Batch Processing Scripts

### Process Multiple Files
```python
import os
import asyncio
from pathlib import Path

async def batch_convert_format(input_dir: str, output_dir: str, target_format: str = "mp4"):
    """Convert all videos in directory to target format"""
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Find all video files
    video_extensions = ['.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(Path(input_dir).glob(f"*{ext}"))
    
    async def convert_single_file(input_file):
        output_file = Path(output_dir) / f"{input_file.stem}.{target_format}"
        
        try:
            result = await convert_format(
                str(input_file), 
                str(output_file),
                vcodec="h264",
                bitrate="2M"
            )
            return f"✓ Converted: {input_file.name}"
        except Exception as e:
            return f"✗ Failed: {input_file.name} - {str(e)}"
    
    # Process files with concurrency limit
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent conversions
    
    async def convert_with_limit(file):
        async with semaphore:
            return await convert_single_file(file)
    
    # Execute all conversions
    results = await asyncio.gather(*[convert_with_limit(f) for f in video_files])
    
    return results

# Usage
results = await batch_convert_format("input_videos/", "converted_videos/", "mp4")
for result in results:
    print(result)
```

### Batch Thumbnail Generation
```python
async def generate_video_thumbnails(video_dir: str, thumb_dir: str, timestamp: str = "00:00:05"):
    """Generate thumbnails for all videos in directory"""
    
    Path(thumb_dir).mkdir(parents=True, exist_ok=True)
    
    video_files = list(Path(video_dir).glob("*.mp4")) + list(Path(video_dir).glob("*.mov"))
    
    async def create_thumbnail(video_file):
        thumb_path = Path(thumb_dir) / f"{video_file.stem}_thumb.jpg"
        
        try:
            await generate_thumbnail(str(video_file), str(thumb_path), timestamp)
            return f"✓ Thumbnail created: {thumb_path.name}"
        except Exception as e:
            return f"✗ Failed: {video_file.name} - {str(e)}"
    
    results = await asyncio.gather(*[create_thumbnail(f) for f in video_files])
    return results

# Generate thumbnails for all videos
results = await generate_video_thumbnails("videos/", "thumbnails/", "00:00:03")
```

## Content Creation Automation

### Social Media Content Pipeline
```python
async def create_social_media_versions(source_video: str, output_dir: str):
    """Create multiple social media format versions from source"""
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Define social media formats
    formats = {
        "instagram_post": {"width": 1080, "height": 1080, "duration": 60},
        "instagram_story": {"width": 1080, "height": 1920, "duration": 15},
        "youtube_short": {"width": 1080, "height": 1920, "duration": 60},
        "tiktok": {"width": 1080, "height": 1920, "duration": 30},
        "twitter": {"width": 1280, "height": 720, "duration": 140}
    }
    
    results = []
    
    for platform, specs in formats.items():
        # Create output filename
        output_file = Path(output_dir) / f"{platform}_{Path(source_video).stem}.mp4"
        
        try:
            # Step 1: Trim to platform duration
            trimmed = await trim_video(
                source_video,
                f"temp_{platform}_trimmed.mp4",
                "00:00:00",
                f"00:00:{specs['duration']}"
            )
            
            # Step 2: Resize for platform
            resized = await resize_video(
                f"temp_{platform}_trimmed.mp4",
                f"temp_{platform}_resized.mp4",
                specs["width"],
                specs["height"]
            )
            
            # Step 3: Add platform-specific branding
            branded = await add_text_overlay(
                f"temp_{platform}_resized.mp4",
                str(output_file),
                f"Follow us on {platform.split('_')[0].title()}!",
                position="bottom",
                font_size=24,
                color="white"
            )
            
            results.append(f"✓ Created {platform} version: {output_file.name}")
            
        except Exception as e:
            results.append(f"✗ Failed {platform}: {str(e)}")
    
    # Cleanup temporary files
    temp_files = Path(".").glob("temp_*")
    for temp_file in temp_files:
        temp_file.unlink(missing_ok=True)
    
    return results

# Create all social media versions
results = await create_social_media_versions("master_video.mp4", "social_media_outputs/")
```

### Podcast Video Generation
```python
async def create_podcast_video(audio_file: str, background_image: str, output_file: str):
    """Generate video version of podcast with static background and waveform"""
    
    # Get audio duration
    audio_info = await get_video_info(audio_file)
    import json
    duration = float(json.loads(audio_info)["format"]["duration"])
    
    # Step 1: Create video from static image
    temp_video = await apply_filter(
        background_image,
        "temp_background_video.mp4",
        "loop",
        f"loop=-1:size=1:start=0:t={duration}"
    )
    
    # Step 2: Add audio to video
    podcast_video = await add_audio(
        "temp_background_video.mp4",
        audio_file,
        "temp_with_audio.mp4",
        mode="replace"
    )
    
    # Step 3: Add podcast title overlay
    titled_video = await add_text_overlay(
        "temp_with_audio.mp4",
        "temp_titled.mp4",
        "PODCAST EPISODE",
        position="top",
        font_size=48,
        color="white"
    )
    
    # Step 4: Add waveform visualization (simplified)
    final_video = await apply_filter(
        "temp_titled.mp4",
        output_file,
        "showwaves",
        "s=1920x100:mode=line:colors=white"
    )
    
    return final_video

# Generate podcast video
result = await create_podcast_video("episode1.mp3", "podcast_bg.jpg", "episode1_video.mp4")
```

## Quality Control Automation

### Automated Quality Check
```python
async def quality_check_videos(video_dir: str):
    """Perform automated quality checks on video files"""
    
    video_files = list(Path(video_dir).glob("*.mp4"))
    quality_report = []
    
    for video_file in video_files:
        try:
            # Get video information
            info = await get_video_info(str(video_file))
            video_data = json.loads(info)
            
            # Extract key metrics
            video_stream = next(s for s in video_data["streams"] if s["codec_type"] == "video")
            audio_streams = [s for s in video_data["streams"] if s["codec_type"] == "audio"]
            
            # Quality checks
            checks = {
                "file": video_file.name,
                "resolution": f"{video_stream.get('width', 'unknown')}x{video_stream.get('height', 'unknown')}",
                "frame_rate": video_stream.get("r_frame_rate", "unknown"),
                "duration": video_data["format"].get("duration", "unknown"),
                "video_codec": video_stream.get("codec_name", "unknown"),
                "video_bitrate": video_stream.get("bit_rate", "unknown"),
                "has_audio": len(audio_streams) > 0,
                "audio_codec": audio_streams[0].get("codec_name", "none") if audio_streams else "none",
                "file_size_mb": round(int(video_data["format"].get("size", 0)) / (1024*1024), 2)
            }
            
            # Quality flags
            flags = []
            if int(video_stream.get("width", 0)) < 1280:
                flags.append("LOW_RESOLUTION")
            if not audio_streams:
                flags.append("NO_AUDIO")
            if int(video_data["format"].get("size", 0)) < 1024*1024:  # Less than 1MB
                flags.append("VERY_SMALL_FILE")
            
            checks["quality_flags"] = flags
            quality_report.append(checks)
            
        except Exception as e:
            quality_report.append({
                "file": video_file.name,
                "error": str(e),
                "quality_flags": ["ANALYSIS_FAILED"]
            })
    
    return quality_report

# Run quality check
quality_data = await quality_check_videos("output_videos/")

# Generate report
print("VIDEO QUALITY REPORT")
print("=" * 50)
for video in quality_data:
    print(f"\nFile: {video['file']}")
    if 'error' in video:
        print(f"  Error: {video['error']}")
    else:
        print(f"  Resolution: {video['resolution']}")
        print(f"  Duration: {video['duration']}s")
        print(f"  File Size: {video['file_size_mb']}MB")
        print(f"  Video Codec: {video['video_codec']}")
        print(f"  Audio Codec: {video['audio_codec']}")
        if video['quality_flags']:
            print(f"  ⚠️  Issues: {', '.join(video['quality_flags'])}")
        else:
            print(f"  ✅ Quality: OK")
```

## Automated Backup and Archive

### Video Archive System
```python
import shutil
from datetime import datetime

async def archive_completed_projects(source_dir: str, archive_dir: str, days_old: int = 30):
    """Archive video projects older than specified days"""
    
    archive_base = Path(archive_dir)
    archive_base.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp-based archive folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_archive = archive_base / f"archive_{timestamp}"
    current_archive.mkdir()
    
    # Find projects to archive
    source_path = Path(source_dir)
    cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
    
    archived_projects = []
    
    for project_dir in source_path.iterdir():
        if project_dir.is_dir():
            # Check if project is old enough
            mod_time = project_dir.stat().st_mtime
            
            if mod_time < cutoff_time:
                try:
                    # Archive the project
                    archive_dest = current_archive / project_dir.name
                    shutil.copytree(project_dir, archive_dest)
                    
                    # Verify archive integrity
                    if archive_dest.exists():
                        # Create project summary
                        await create_project_summary(str(archive_dest))
                        
                        # Remove original after successful archive
                        shutil.rmtree(project_dir)
                        archived_projects.append(project_dir.name)
                    
                except Exception as e:
                    print(f"Failed to archive {project_dir.name}: {e}")
    
    return archived_projects

async def create_project_summary(project_path: str):
    """Create summary of archived project"""
    
    project_dir = Path(project_path)
    summary_file = project_dir / "project_summary.txt"
    
    # Gather project statistics
    video_files = list(project_dir.glob("*.mp4")) + list(project_dir.glob("*.mov"))
    total_size = sum(f.stat().st_size for f in project_dir.rglob("*") if f.is_file())
    
    summary = f"""
PROJECT ARCHIVE SUMMARY
======================
Project: {project_dir.name}
Archived: {datetime.now().isoformat()}
Total Files: {len(list(project_dir.rglob("*")))}
Video Files: {len(video_files)}
Total Size: {total_size / (1024*1024):.2f} MB

VIDEO FILES:
"""
    
    for video_file in video_files:
        try:
            info = await get_video_info(str(video_file))
            video_data = json.loads(info)
            duration = video_data["format"].get("duration", "unknown")
            size_mb = video_file.stat().st_size / (1024*1024)
            
            summary += f"  - {video_file.name}: {duration}s, {size_mb:.2f}MB\n"
        except:
            summary += f"  - {video_file.name}: Analysis failed\n"
    
    # Write summary
    with open(summary_file, 'w') as f:
        f.write(summary)

# Archive old projects
archived = await archive_completed_projects("active_projects/", "archive/", days_old=30)
print(f"Archived {len(archived)} projects: {', '.join(archived)}")
```

## Monitoring and Reporting

### Processing Statistics
```python
import time
import psutil
from dataclasses import dataclass
from typing import List

@dataclass
class ProcessingStats:
    start_time: float
    end_time: float
    input_file: str
    output_file: str
    operation: str
    success: bool
    error_message: str = ""
    input_size_mb: float = 0
    output_size_mb: float = 0
    processing_time_seconds: float = 0

class VideoProcessingMonitor:
    def __init__(self):
        self.stats: List[ProcessingStats] = []
    
    async def monitored_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Wrapper to monitor video processing operations"""
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        try:
            # Extract input/output paths from args if available
            input_path = args[0] if args else "unknown"
            output_path = args[1] if len(args) > 1 else "unknown"
            
            # Get input file size
            input_size = 0
            if Path(input_path).exists():
                input_size = Path(input_path).stat().st_size / (1024*1024)
            
            # Execute operation
            result = await operation_func(*args, **kwargs)
            
            # Get output file size
            output_size = 0
            if Path(output_path).exists():
                output_size = Path(output_path).stat().st_size / (1024*1024)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Record successful operation
            stat = ProcessingStats(
                start_time=start_time,
                end_time=end_time,
                input_file=input_path,
                output_file=output_path,
                operation=operation_name,
                success=True,
                input_size_mb=input_size,
                output_size_mb=output_size,
                processing_time_seconds=processing_time
            )
            
            self.stats.append(stat)
            return result
            
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Record failed operation
            stat = ProcessingStats(
                start_time=start_time,
                end_time=end_time,
                input_file=input_path,
                output_file=output_path,
                operation=operation_name,
                success=False,
                error_message=str(e),
                processing_time_seconds=processing_time
            )
            
            self.stats.append(stat)
            raise e
    
    def generate_report(self) -> str:
        """Generate processing statistics report"""
        
        if not self.stats:
            return "No processing operations recorded."
        
        successful_ops = [s for s in self.stats if s.success]
        failed_ops = [s for s in self.stats if not s.success]
        
        total_processing_time = sum(s.processing_time_seconds for s in self.stats)
        total_input_size = sum(s.input_size_mb for s in successful_ops)
        total_output_size = sum(s.output_size_mb for s in successful_ops)
        
        report = f"""
VIDEO PROCESSING REPORT
======================
Total Operations: {len(self.stats)}
Successful: {len(successful_ops)}
Failed: {len(failed_ops)}
Success Rate: {len(successful_ops)/len(self.stats)*100:.1f}%

PERFORMANCE METRICS:
Total Processing Time: {total_processing_time:.2f}s
Average Time per Operation: {total_processing_time/len(self.stats):.2f}s
Total Input Size: {total_input_size:.2f}MB
Total Output Size: {total_output_size:.2f}MB
Compression Ratio: {total_input_size/total_output_size if total_output_size > 0 else 0:.2f}:1

OPERATIONS BY TYPE:
"""
        
        # Group by operation type
        operation_counts = {}
        for stat in self.stats:
            op_type = stat.operation
            if op_type not in operation_counts:
                operation_counts[op_type] = {"count": 0, "success": 0, "total_time": 0}
            
            operation_counts[op_type]["count"] += 1
            if stat.success:
                operation_counts[op_type]["success"] += 1
            operation_counts[op_type]["total_time"] += stat.processing_time_seconds
        
        for op_type, data in operation_counts.items():
            success_rate = data["success"] / data["count"] * 100
            avg_time = data["total_time"] / data["count"]
            report += f"  {op_type}: {data['count']} ops, {success_rate:.1f}% success, {avg_time:.2f}s avg\n"
        
        if failed_ops:
            report += "\nFAILED OPERATIONS:\n"
            for failed_op in failed_ops[-5:]:  # Show last 5 failures
                report += f"  - {failed_op.operation}: {failed_op.input_file} -> {failed_op.error_message}\n"
        
        return report

# Usage example
monitor = VideoProcessingMonitor()

# Monitored batch processing
async def monitored_batch_process(file_list: List[str]):
    """Process files with monitoring"""
    
    for input_file in file_list:
        output_file = f"processed_{Path(input_file).name}"
        
        try:
            # Monitor video conversion
            await monitor.monitored_operation(
                "convert_format",
                convert_format,
                input_file,
                output_file,
                vcodec="h264",
                bitrate="2M"
            )
            
            # Monitor thumbnail generation
            thumb_file = f"thumb_{Path(input_file).stem}.jpg"
            await monitor.monitored_operation(
                "generate_thumbnail",
                generate_thumbnail,
                output_file,
                thumb_file
            )
            
        except Exception as e:
            print(f"Failed to process {input_file}: {e}")
    
    # Generate final report
    print(monitor.generate_report())

# Process files with monitoring
files_to_process = ["video1.mp4", "video2.mp4", "video3.mp4"]
await monitored_batch_process(files_to_process)
```