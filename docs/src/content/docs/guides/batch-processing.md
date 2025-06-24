---
title: Batch Processing Guide
description: Efficient batch video processing workflows and automation techniques
---

# Batch Processing Guide

Learn how to efficiently process multiple videos at once using the VFX MCP Server's batch processing capabilities. This guide covers everything from simple batch operations to complex automated workflows.

## 🚀 Introduction to Batch Processing

Batch processing allows you to apply the same operations to multiple videos automatically, saving time and ensuring consistency across your video library. The VFX MCP Server provides several approaches to batch processing:

1. **Manual Iteration**: Loop through files with custom logic
2. **Built-in Batch Tool**: Use the dedicated `batch_process_videos` tool
3. **Resource-Based Discovery**: Automatically find and process videos
4. **Configuration-Driven**: Define processing pipelines with JSON/YAML

## 📁 File Discovery and Management

### Using Resource Endpoints

The server provides resource endpoints to discover videos automatically:

```python
async def discover_videos():
    """Find all videos in the working directory"""
    
    # Get list of all videos
    video_list = await session.read_resource("videos://list")
    
    print(f"Found {video_list['total_count']} videos:")
    print(f"Total size: {video_list['total_size']}")
    
    for video in video_list['videos']:
        print(f"  📹 {video['name']}: {video['duration']}s, {video['resolution']}")
    
    return video_list['videos']

# Usage
available_videos = await discover_videos()
```

### Filtering Videos by Criteria

```python
async def filter_videos_by_criteria(min_duration=None, max_duration=None, 
                                   formats=None, min_resolution=None):
    """Filter videos based on specific criteria"""
    
    video_list = await session.read_resource("videos://list")
    filtered_videos = []
    
    for video in video_list['videos']:
        # Get detailed metadata for filtering
        metadata = await session.read_resource(f"videos://{video['name']}/metadata")
        video_props = metadata['video_properties']
        
        # Apply filters
        if min_duration and video_props['duration'] < min_duration:
            continue
        if max_duration and video_props['duration'] > max_duration:
            continue
        if formats and video_props['format'] not in formats:
            continue
        if min_resolution:
            min_width, min_height = map(int, min_resolution.split('x'))
            if video_props['width'] < min_width or video_props['height'] < min_height:
                continue
        
        filtered_videos.append(video)
    
    print(f"Filtered: {len(filtered_videos)}/{len(video_list['videos'])} videos match criteria")
    return filtered_videos

# Usage examples
long_videos = await filter_videos_by_criteria(min_duration=300)  # 5+ minutes
hd_videos = await filter_videos_by_criteria(min_resolution="1280x720")
mp4_videos = await filter_videos_by_criteria(formats=["mp4"])
```

## 🔧 Basic Batch Operations

### Simple Batch Processing Loop

```python
async def simple_batch_resize():
    """Resize all videos to 720p with consistent settings"""
    
    video_list = await session.read_resource("videos://list")
    results = []
    
    for i, video in enumerate(video_list['videos'], 1):
        video_name = video['name']
        output_name = f"720p_{video_name}"
        
        print(f"Processing {i}/{len(video_list['videos'])}: {video_name}")
        
        try:
            await session.call_tool("resize_video", {
                "input_path": video_name,
                "output_path": output_name,
                "width": 1280,
                "height": 720,
                "quality": "medium"
            })
            
            results.append({
                "input": video_name,
                "output": output_name,
                "status": "success"
            })
            print(f"  ✅ Resized: {output_name}")
            
        except Exception as e:
            results.append({
                "input": video_name,
                "output": None,
                "status": "error",
                "error": str(e)
            })
            print(f"  ❌ Error: {e}")
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n📊 Batch resize complete: {successful}/{len(results)} successful")
    
    return results

# Usage
resize_results = await simple_batch_resize()
```

### Batch Processing with Progress Tracking

```python
async def batch_with_progress(video_files, operation_name, operation_func):
    """Generic batch processor with detailed progress tracking"""
    
    total_files = len(video_files)
    results = {
        "successful": [],
        "failed": [],
        "skipped": [],
        "total_time": 0
    }
    
    print(f"🚀 Starting batch {operation_name} for {total_files} files")
    start_time = time.time()
    
    for i, video_file in enumerate(video_files, 1):
        file_start_time = time.time()
        
        print(f"\n[{i:3d}/{total_files}] Processing: {video_file}")
        print(f"Progress: {'█' * (i * 20 // total_files):<20} {i/total_files*100:.1f}%")
        
        try:
            # Check if output already exists
            output_file = operation_func['output_pattern'].format(input=video_file)
            if os.path.exists(output_file):
                print(f"  ⏭️  Skipped (already exists): {output_file}")
                results["skipped"].append(video_file)
                continue
            
            # Execute operation
            result = await session.call_tool(
                operation_func['tool_name'], 
                {**operation_func['params'], 'input_path': video_file, 'output_path': output_file}
            )
            
            file_time = time.time() - file_start_time
            print(f"  ✅ Success in {file_time:.1f}s: {output_file}")
            
            results["successful"].append({
                "input": video_file,
                "output": output_file,
                "time": file_time
            })
            
        except Exception as e:
            file_time = time.time() - file_start_time
            print(f"  ❌ Failed in {file_time:.1f}s: {e}")
            
            results["failed"].append({
                "input": video_file,
                "error": str(e),
                "time": file_time
            })
    
    total_time = time.time() - start_time
    results["total_time"] = total_time
    
    # Final summary
    print(f"\n📊 Batch {operation_name} Summary:")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Successful: {len(results['successful'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Skipped: {len(results['skipped'])}")
    print(f"  Average time per file: {total_time/total_files:.1f}s")
    
    return results

# Usage example
video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]

trim_operation = {
    "tool_name": "trim_video",
    "params": {"start_time": 0, "duration": 60},
    "output_pattern": "trimmed_{input}"
}

results = await batch_with_progress(video_files, "trimming", trim_operation)
```

## 🔄 Advanced Batch Workflows

### Configuration-Driven Batch Processing

```python
import json
from typing import Dict, List, Any

async def config_driven_batch_processing(config_file: str):
    """Process videos based on a configuration file"""
    
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"📋 Loaded batch config: {config['name']}")
    print(f"Description: {config['description']}")
    
    # Get videos to process
    if config['input']['type'] == 'directory':
        video_list = await session.read_resource("videos://list")
        videos = [v['name'] for v in video_list['videos']]
    elif config['input']['type'] == 'list':
        videos = config['input']['files']
    else:
        raise ValueError(f"Unknown input type: {config['input']['type']}")
    
    # Apply filters if specified
    if 'filters' in config:
        videos = await apply_config_filters(videos, config['filters'])
    
    print(f"🎯 Processing {len(videos)} videos")
    
    # Execute processing pipeline
    results = {}
    for step_name, step_config in config['pipeline'].items():
        print(f"\n🔧 Executing step: {step_name}")
        
        step_results = await execute_pipeline_step(
            videos, step_name, step_config, config['output']
        )
        
        results[step_name] = step_results
        
        # Update video list for next step (use outputs as inputs)
        if step_results['successful']:
            videos = [r['output'] for r in step_results['successful']]
    
    return results

async def apply_config_filters(videos: List[str], filters: Dict[str, Any]) -> List[str]:
    """Apply filters from configuration"""
    filtered_videos = []
    
    for video in videos:
        metadata = await session.read_resource(f"videos://{video}/metadata")
        video_props = metadata['video_properties']
        
        # Check each filter
        include_video = True
        
        if 'min_duration' in filters:
            if video_props['duration'] < filters['min_duration']:
                include_video = False
        
        if 'max_duration' in filters:
            if video_props['duration'] > filters['max_duration']:
                include_video = False
        
        if 'formats' in filters:
            if video_props['format'] not in filters['formats']:
                include_video = False
        
        if 'min_resolution' in filters:
            min_w, min_h = map(int, filters['min_resolution'].split('x'))
            if video_props['width'] < min_w or video_props['height'] < min_h:
                include_video = False
        
        if include_video:
            filtered_videos.append(video)
        else:
            print(f"  🚫 Filtered out: {video}")
    
    return filtered_videos

async def execute_pipeline_step(videos: List[str], step_name: str, 
                               step_config: Dict[str, Any], output_config: Dict[str, Any]):
    """Execute a single pipeline step"""
    
    tool_name = step_config['tool']
    params = step_config['params']
    output_pattern = step_config.get('output_pattern', f"{step_name}_{{}}")
    
    results = {"successful": [], "failed": []}
    
    for video in videos:
        try:
            output_file = output_pattern.format(video)
            
            # Add output directory if specified
            if 'directory' in output_config:
                output_file = f"{output_config['directory']}/{output_file}"
            
            # Execute tool
            await session.call_tool(tool_name, {
                **params,
                "input_path": video,
                "output_path": output_file
            })
            
            results["successful"].append({
                "input": video,
                "output": output_file
            })
            print(f"  ✅ {video} → {output_file}")
            
        except Exception as e:
            results["failed"].append({
                "input": video,
                "error": str(e)
            })
            print(f"  ❌ {video}: {e}")
    
    return results

# Example configuration file (batch_config.json)
example_config = {
    "name": "Social Media Batch Processing",
    "description": "Prepare videos for social media platforms",
    "input": {
        "type": "directory"
    },
    "filters": {
        "formats": ["mp4", "mov"],
        "min_duration": 10,
        "max_duration": 600
    },
    "output": {
        "directory": "processed_videos"
    },
    "pipeline": {
        "trim_intro": {
            "tool": "trim_video",
            "params": {"start_time": 5.0, "duration": 55.0},
            "output_pattern": "trimmed_{}"
        },
        "color_grade": {
            "tool": "apply_color_grading",
            "params": {
                "brightness": 0.05,
                "contrast": 1.15,
                "saturation": 1.2
            },
            "output_pattern": "graded_{}"
        },
        "resize_instagram": {
            "tool": "resize_video",
            "params": {
                "width": 1080,
                "height": 1080,
                "quality": "high"
            },
            "output_pattern": "instagram_{}"
        }
    }
}

# Save example config
with open('batch_config.json', 'w') as f:
    json.dump(example_config, f, indent=2)

# Usage
results = await config_driven_batch_processing('batch_config.json')
```

### Parallel Batch Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_batch_processing(video_files: List[str], max_workers: int = 4):
    """Process multiple videos in parallel for faster throughput"""
    
    print(f"🚀 Starting parallel processing with {max_workers} workers")
    
    # Check system capabilities
    capabilities = await session.read_resource("tools://capabilities")
    max_concurrent = capabilities['limits']['concurrent_operations']
    
    if max_workers > max_concurrent:
        print(f"⚠️  Reducing workers from {max_workers} to {max_concurrent} (server limit)")
        max_workers = max_concurrent
    
    async def process_single_video(video_file: str, worker_id: int):
        """Process a single video (worker function)"""
        print(f"[Worker {worker_id}] Processing: {video_file}")
        
        try:
            # Example: Apply color grading
            output_file = f"worker_{worker_id}_processed_{video_file}"
            
            await session.call_tool("apply_color_grading", {
                "input_path": video_file,
                "output_path": output_file,
                "brightness": 0.03,
                "contrast": 1.1,
                "saturation": 1.15
            })
            
            print(f"[Worker {worker_id}] ✅ Completed: {output_file}")
            return {"status": "success", "input": video_file, "output": output_file}
            
        except Exception as e:
            print(f"[Worker {worker_id}] ❌ Failed: {e}")
            return {"status": "error", "input": video_file, "error": str(e)}
    
    # Create semaphore to limit concurrent operations
    semaphore = asyncio.Semaphore(max_workers)
    
    async def worker_with_semaphore(video_file: str, worker_id: int):
        async with semaphore:
            return await process_single_video(video_file, worker_id)
    
    # Start all workers
    tasks = []
    for i, video_file in enumerate(video_files):
        task = asyncio.create_task(
            worker_with_semaphore(video_file, i % max_workers)
        )
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful = [r for r in results if isinstance(r, dict) and r['status'] == 'success']
    failed = [r for r in results if isinstance(r, dict) and r['status'] == 'error']
    exceptions = [r for r in results if isinstance(r, Exception)]
    
    print(f"\n📊 Parallel processing complete:")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    print(f"  Exceptions: {len(exceptions)}")
    
    return {
        "successful": successful,
        "failed": failed,
        "exceptions": exceptions
    }

# Usage
video_files = ["video1.mp4", "video2.mp4", "video3.mp4", "video4.mp4"]
parallel_results = await parallel_batch_processing(video_files, max_workers=2)
```

## 📊 Monitoring and Reporting

### Comprehensive Batch Reporting

```python
import time
import json
from datetime import datetime

class BatchProcessor:
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.start_time = None
        self.results = {
            "job_name": job_name,
            "start_time": None,
            "end_time": None,
            "total_time": 0,
            "files_processed": 0,
            "successful": [],
            "failed": [],
            "skipped": [],
            "performance_metrics": {}
        }
    
    async def start_job(self):
        """Initialize batch job"""
        self.start_time = time.time()
        self.results["start_time"] = datetime.now().isoformat()
        print(f"🚀 Starting batch job: {self.job_name}")
    
    async def process_file(self, input_file: str, operation: str, params: dict):
        """Process a single file with error handling and timing"""
        file_start = time.time()
        
        try:
            result = await session.call_tool(operation, {
                "input_path": input_file,
                **params
            })
            
            file_time = time.time() - file_start
            
            self.results["successful"].append({
                "input": input_file,
                "output": params.get("output_path", "unknown"),
                "processing_time": file_time,
                "operation": operation
            })
            
            print(f"  ✅ {input_file} processed in {file_time:.1f}s")
            return True
            
        except Exception as e:
            file_time = time.time() - file_start
            
            self.results["failed"].append({
                "input": input_file,
                "error": str(e),
                "processing_time": file_time,
                "operation": operation
            })
            
            print(f"  ❌ {input_file} failed in {file_time:.1f}s: {e}")
            return False
    
    async def finish_job(self):
        """Finalize batch job and generate report"""
        end_time = time.time()
        total_time = end_time - self.start_time
        
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_time"] = total_time
        self.results["files_processed"] = (
            len(self.results["successful"]) + 
            len(self.results["failed"]) + 
            len(self.results["skipped"])
        )
        
        # Calculate performance metrics
        if self.results["successful"]:
            processing_times = [f["processing_time"] for f in self.results["successful"]]
            self.results["performance_metrics"] = {
                "avg_processing_time": sum(processing_times) / len(processing_times),
                "min_processing_time": min(processing_times),
                "max_processing_time": max(processing_times),
                "throughput_files_per_minute": len(processing_times) / (total_time / 60)
            }
        
        # Generate report
        self.generate_report()
        
    def generate_report(self):
        """Generate detailed batch processing report"""
        results = self.results
        
        print(f"\n📊 Batch Processing Report: {self.job_name}")
        print(f"{'='*60}")
        print(f"Start Time: {results['start_time']}")
        print(f"End Time: {results['end_time']}")
        print(f"Total Duration: {results['total_time']:.1f}s")
        print(f"\nFiles Processed: {results['files_processed']}")
        print(f"  ✅ Successful: {len(results['successful'])}")
        print(f"  ❌ Failed: {len(results['failed'])}")
        print(f"  ⏭️  Skipped: {len(results['skipped'])}")
        
        if results["performance_metrics"]:
            metrics = results["performance_metrics"]
            print(f"\nPerformance Metrics:")
            print(f"  Average processing time: {metrics['avg_processing_time']:.1f}s")
            print(f"  Fastest file: {metrics['min_processing_time']:.1f}s")
            print(f"  Slowest file: {metrics['max_processing_time']:.1f}s")
            print(f"  Throughput: {metrics['throughput_files_per_minute']:.1f} files/minute")
        
        # Save detailed report
        report_file = f"batch_report_{self.job_name}_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        return results

# Usage example
async def enhanced_batch_workflow():
    """Complete batch workflow with monitoring and reporting"""
    
    processor = BatchProcessor("social_media_prep")
    await processor.start_job()
    
    # Get videos to process
    video_list = await session.read_resource("videos://list")
    
    for video in video_list['videos']:
        video_name = video['name']
        
        # Step 1: Trim to 60 seconds
        await processor.process_file(
            video_name, 
            "trim_video",
            {
                "output_path": f"trimmed_{video_name}",
                "start_time": 0,
                "duration": 60
            }
        )
        
        # Step 2: Apply social media color grading
        await processor.process_file(
            f"trimmed_{video_name}",
            "apply_color_grading", 
            {
                "output_path": f"graded_{video_name}",
                "brightness": 0.08,
                "contrast": 1.2,
                "saturation": 1.3
            }
        )
        
        # Step 3: Resize for Instagram
        await processor.process_file(
            f"graded_{video_name}",
            "resize_video",
            {
                "output_path": f"instagram_{video_name}",
                "width": 1080,
                "height": 1080,
                "quality": "high"
            }
        )
    
    # Generate final report
    await processor.finish_job()

# Run enhanced workflow
await enhanced_batch_workflow()
```

## ⚡ Performance Optimization

### Batch Processing Best Practices

1. **File Size Optimization**:
   ```python
   # Process smaller files first for faster feedback
   async def size_optimized_batch():
       video_list = await session.read_resource("videos://list")
       
       # Sort by file size (smallest first)
       videos_by_size = sorted(video_list['videos'], 
                              key=lambda v: float(v['size'].split()[0]))
       
       for video in videos_by_size:
           # Process video...
           pass
   ```

2. **Quality vs Speed Trade-offs**:
   ```python
   # Use appropriate quality settings for batch operations
   BATCH_QUALITY_SETTINGS = {
       "preview": "low",      # Fast processing for previews
       "social": "medium",    # Balanced for social media
       "final": "high",       # High quality for final output
       "archive": "ultra"     # Maximum quality for archival
   }
   ```

3. **Memory Management**:
   ```python
   # Monitor system resources during batch processing
   async def monitor_resources():
       capabilities = await session.read_resource("tools://capabilities")
       resources = capabilities['system_resources']
       
       if resources['memory_usage'] > 85:
           print("⚠️ High memory usage - consider reducing concurrent operations")
       
       if resources['cpu_usage'] > 90:
           print("⚠️ High CPU usage - processing may be slow")
   ```

### Error Recovery Strategies

```python
async def resilient_batch_processing(video_files: List[str], max_retries: int = 3):
    """Batch processing with automatic retry and error recovery"""
    
    failed_files = []
    retry_queue = video_files.copy()
    attempt = 1
    
    while retry_queue and attempt <= max_retries:
        print(f"\n🔄 Attempt {attempt}/{max_retries}: {len(retry_queue)} files")
        
        current_batch = retry_queue.copy()
        retry_queue = []
        
        for video_file in current_batch:
            try:
                # Process video
                await session.call_tool("resize_video", {
                    "input_path": video_file,
                    "output_path": f"processed_{video_file}",
                    "width": 1280,
                    "height": 720,
                    "quality": "medium"
                })
                
                print(f"  ✅ Success: {video_file}")
                
            except Exception as e:
                print(f"  ❌ Failed: {video_file} - {e}")
                
                # Add to retry queue unless it's a permanent error
                if "file not found" not in str(e).lower():
                    retry_queue.append(video_file)
                else:
                    failed_files.append(video_file)
        
        attempt += 1
        
        # Wait between retries
        if retry_queue and attempt <= max_retries:
            await asyncio.sleep(5)  # 5-second delay between retries
    
    # Report final results
    total_files = len(video_files)
    successful = total_files - len(retry_queue) - len(failed_files)
    
    print(f"\n📊 Final Results:")
    print(f"  Successful: {successful}/{total_files}")
    print(f"  Failed (permanent): {len(failed_files)}")
    print(f"  Failed (retry exhausted): {len(retry_queue)}")
    
    return {
        "successful": successful,
        "permanent_failures": failed_files,
        "retry_exhausted": retry_queue
    }
```

## 🎯 Next Steps

You're now equipped with powerful batch processing capabilities! Explore related guides:

- **[Color Grading Guide](/guides/color-grading/)** - Apply consistent color grading in batches
- **[Common Workflows](/guides/common-workflows/)** - Complete production workflows
- **[Performance Tips](/support/performance/)** - Optimize processing speed
- **[Automation Examples](/examples/automation/)** - Advanced automation patterns

**Questions about batch processing?** Check our [FAQ](/support/faq/) or explore the [troubleshooting guide](/support/troubleshooting/).