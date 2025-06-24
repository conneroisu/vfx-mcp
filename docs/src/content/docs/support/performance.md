---
title: Performance Optimization
description: Tips and techniques for optimizing video processing performance
---

Maximize the speed and efficiency of your video processing workflows with the VFX MCP Server. This guide covers performance tuning, optimization strategies, and best practices for handling large-scale video processing tasks.

## 📊 Understanding Performance Factors

### System Resources Impact

Video processing performance depends on several key factors:

1. **CPU Performance**: Single-core speed affects encoding/decoding
2. **Memory (RAM)**: Determines how much video data can be processed in memory
3. **Storage Speed**: I/O speed affects file reading/writing operations  
4. **Video Properties**: Resolution, codec, bitrate, and duration all impact processing time

### Checking System Capabilities

```python
async def check_system_performance():
    """Analyze current system performance and capabilities"""
    
    # Get server capabilities
    capabilities = await session.read_resource("tools://capabilities")
    
    system_info = capabilities['system_resources']
    limits = capabilities['limits']
    ffmpeg_info = capabilities['ffmpeg_info']
    
    print("🖥️  System Performance Analysis")
    print("=" * 50)
    
    # Current resource usage
    print(f"Current CPU Usage: {system_info['cpu_usage']:.1f}%")
    print(f"Current Memory Usage: {system_info['memory_usage']:.1f}%")
    print(f"Available Disk Space: {system_info['disk_space_free']}")
    
    # Performance limits
    print(f"\nPerformance Limits:")
    print(f"Max File Size: {limits['max_file_size']}")
    print(f"Max Resolution: {limits['max_resolution']}")
    print(f"Concurrent Operations: {limits['concurrent_operations']}")
    print(f"Temp Storage Limit: {limits['temp_storage_limit']}")
    
    # FFmpeg capabilities
    print(f"\nFFmpeg Performance:")
    print(f"Version: {ffmpeg_info['version']}")
    print(f"Hardware Encoding: {capabilities['feature_flags'].get('hardware_encoding', False)}")
    print(f"GPU Acceleration: {capabilities['feature_flags'].get('gpu_acceleration', False)}")
    
    # Performance recommendations
    recommendations = []
    
    if system_info['cpu_usage'] > 80:
        recommendations.append("High CPU usage - consider reducing concurrent operations")
    
    if system_info['memory_usage'] > 85:
        recommendations.append("High memory usage - process smaller files or restart server")
    
    if not capabilities['feature_flags'].get('hardware_encoding', False):
        recommendations.append("Hardware encoding not available - processing may be slower")
    
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
    else:
        print(f"\n✅ System performance looks good!")
    
    return capabilities

# Usage
performance_info = await check_system_performance()
```

## ⚡ Speed Optimization Strategies

### 1. Choose Optimal Quality Settings

Different quality settings dramatically affect processing speed:

```python
# Performance vs Quality trade-offs
QUALITY_PERFORMANCE_MAP = {
    "ultra": {
        "relative_speed": 0.3,    # 30% of base speed
        "use_case": "Archive, master copies",
        "file_size": "Largest"
    },
    "high": {
        "relative_speed": 0.6,    # 60% of base speed  
        "use_case": "Final output, professional delivery",
        "file_size": "Large"
    },
    "medium": {
        "relative_speed": 1.0,    # Base speed (100%)
        "use_case": "Social media, web delivery",
        "file_size": "Medium"
    },
    "low": {
        "relative_speed": 2.0,    # 200% of base speed
        "use_case": "Previews, drafts, testing",
        "file_size": "Small"
    }
}

async def optimize_quality_for_use_case(use_case: str):
    """Get optimal quality setting for specific use case"""
    
    quality_map = {
        "preview": "low",
        "draft": "low", 
        "social_media": "medium",
        "web": "medium",
        "professional": "high",
        "broadcast": "high",
        "archive": "ultra",
        "master": "ultra"
    }
    
    recommended_quality = quality_map.get(use_case, "medium")
    performance_info = QUALITY_PERFORMANCE_MAP[recommended_quality]
    
    print(f"📋 Use case: {use_case}")
    print(f"Recommended quality: {recommended_quality}")
    print(f"Expected speed: {performance_info['relative_speed']}x")
    print(f"File size: {performance_info['file_size']}")
    
    return recommended_quality

# Usage
quality = await optimize_quality_for_use_case("social_media")
```

### 2. Leverage Copy Mode Operations

When possible, use operations that don't require re-encoding:

```python
async def fast_copy_operations_demo():
    """Demonstrate fast operations that use copy mode"""
    
    print("⚡ Fast Copy Mode Operations:")
    
    # Trimming (no re-encoding when formats match)
    start_time = time.time()
    
    await session.call_tool("trim_video", {
        "input_path": "source.mp4",
        "output_path": "trimmed_fast.mp4",
        "start_time": 10,
        "duration": 60
        # Uses copy mode - very fast!
    })
    
    trim_time = time.time() - start_time
    print(f"  ✅ Trim (copy mode): {trim_time:.1f}s")
    
    # Concatenation (when formats match)
    start_time = time.time()
    
    await session.call_tool("concatenate_videos", {
        "input_paths": ["clip1.mp4", "clip2.mp4"],
        "output_path": "combined_fast.mp4",
        "transition_duration": 0.0  # No transitions = copy mode
    })
    
    concat_time = time.time() - start_time
    print(f"  ✅ Concatenate (copy mode): {concat_time:.1f}s")
    
    print("\n💡 Copy mode is used when:")
    print("  • Input and output formats match")
    print("  • No transcoding is required")
    print("  • No effects or filters are applied")

# Usage
await fast_copy_operations_demo()
```

### 3. Optimize File I/O

Storage speed significantly impacts performance:

```python
async def optimize_file_io():
    """Optimize file I/O for better performance"""
    
    print("💾 File I/O Optimization Tips:")
    
    # Check current temp directory
    capabilities = await session.read_resource("tools://capabilities")
    temp_dir = capabilities['system_resources']['temp_directory']
    print(f"Current temp directory: {temp_dir}")
    
    # Recommendations for different storage types
    storage_recommendations = {
        "SSD": {
            "performance": "Excellent",
            "tips": [
                "Use for input, output, and temp files",
                "Enable concurrent operations",
                "Process multiple files simultaneously"
            ]
        },
        "NVMe": {
            "performance": "Outstanding", 
            "tips": [
                "Maximum concurrent operations",
                "Use for real-time processing",
                "Best for large file workflows"
            ]
        },
        "HDD": {
            "performance": "Good",
            "tips": [
                "Process files sequentially",
                "Use SSD for temp files if available",
                "Avoid too many concurrent operations"
            ]
        },
        "Network": {
            "performance": "Variable",
            "tips": [
                "Copy files locally before processing",
                "Use local temp directory",
                "Process in smaller batches"
            ]
        }
    }
    
    for storage_type, info in storage_recommendations.items():
        print(f"\n{storage_type} Storage:")
        print(f"  Performance: {info['performance']}")
        for tip in info['tips']:
            print(f"  • {tip}")

# Usage
await optimize_file_io()
```

## 🚀 Workflow Optimization

### Batch Processing Best Practices

```python
async def optimized_batch_processing(video_files: list):
    """Implement optimized batch processing strategies"""
    
    print("🔄 Optimized Batch Processing")
    
    # Strategy 1: Sort by file size (process smaller files first)
    print("\n📊 Analyzing file sizes...")
    
    file_info = []
    for video_file in video_files:
        info = await session.call_tool("get_video_info", {
            "video_path": video_file
        })
        
        # Convert file size to MB for sorting
        size_parts = info['file_size'].split()
        size_mb = float(size_parts[0])
        if size_parts[1] == 'GB':
            size_mb *= 1024
        
        file_info.append({
            "file": video_file,
            "size_mb": size_mb,
            "duration": info['duration']
        })
    
    # Sort by size (smallest first for faster feedback)
    file_info.sort(key=lambda x: x['size_mb'])
    
    print("Processing order (smallest to largest):")
    for i, info in enumerate(file_info, 1):
        print(f"  {i}. {info['file']}: {info['size_mb']:.1f}MB, {info['duration']:.1f}s")
    
    # Strategy 2: Use optimal settings for batch
    batch_settings = {
        "quality": "medium",  # Good balance for batch processing
        "concurrent_limit": 2  # Conservative for stability
    }
    
    print(f"\n⚙️  Batch settings: {batch_settings}")
    
    # Strategy 3: Process with progress tracking
    results = []
    total_time = 0
    
    for i, file_info in enumerate(file_info, 1):
        file_start = time.time()
        video_file = file_info['file']
        
        print(f"\n[{i}/{len(file_info)}] Processing: {video_file}")
        
        try:
            # Example operation: resize to 720p
            await session.call_tool("resize_video", {
                "input_path": video_file,
                "output_path": f"optimized_{video_file}",
                "width": 1280,
                "height": 720,
                "quality": batch_settings["quality"]
            })
            
            file_time = time.time() - file_start
            total_time += file_time
            
            results.append({
                "file": video_file,
                "status": "success",
                "time": file_time
            })
            
            # Estimate remaining time
            remaining_files = len(file_info) - i
            if i > 1:  # After first file
                avg_time = total_time / i
                estimated_remaining = avg_time * remaining_files
                print(f"  ✅ Completed in {file_time:.1f}s (Est. remaining: {estimated_remaining:.1f}s)")
            else:
                print(f"  ✅ Completed in {file_time:.1f}s")
            
        except Exception as e:
            file_time = time.time() - file_start
            total_time += file_time
            
            results.append({
                "file": video_file,
                "status": "error", 
                "error": str(e),
                "time": file_time
            })
            
            print(f"  ❌ Failed in {file_time:.1f}s: {e}")
    
    # Final statistics
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n📈 Batch Processing Statistics:")
    print(f"Total time: {total_time:.1f}s")
    print(f"Successful: {successful}/{len(file_info)}")
    print(f"Average time per file: {total_time/len(file_info):.1f}s")
    
    return results

# Usage
video_files = ["small.mp4", "large.mp4", "medium.mp4"]
batch_results = await optimized_batch_processing(video_files)
```

### Smart Preprocessing

```python
async def smart_preprocessing_workflow(input_path: str, target_use: str):
    """Intelligently preprocess video based on intended use"""
    
    print(f"🧠 Smart preprocessing for: {target_use}")
    
    # Analyze input video
    info = await session.call_tool("get_video_info", {
        "video_path": input_path
    })
    
    print(f"Input: {info['width']}x{info['height']}, {info['duration']:.1f}s, {info['file_size']}")
    
    # Define target specifications
    target_specs = {
        "social_media": {
            "max_resolution": "1080x1080",
            "max_duration": 60,
            "target_bitrate": "2M",
            "quality": "medium"
        },
        "web": {
            "max_resolution": "1280x720", 
            "max_duration": 300,
            "target_bitrate": "1.5M",
            "quality": "medium"
        },
        "professional": {
            "max_resolution": "1920x1080",
            "max_duration": None,
            "target_bitrate": "5M", 
            "quality": "high"
        },
        "archive": {
            "max_resolution": None,
            "max_duration": None,
            "target_bitrate": None,
            "quality": "ultra"
        }
    }
    
    specs = target_specs.get(target_use, target_specs["web"])
    current_file = input_path
    
    # Step 1: Duration optimization
    if specs["max_duration"] and info["duration"] > specs["max_duration"]:
        print(f"⏱️  Trimming to {specs['max_duration']}s...")
        
        trimmed_file = f"preprocessed_trimmed_{input_path}"
        await session.call_tool("trim_video", {
            "input_path": current_file,
            "output_path": trimmed_file,
            "start_time": 0,
            "duration": specs["max_duration"]
        })
        current_file = trimmed_file
    
    # Step 2: Resolution optimization
    if specs["max_resolution"]:
        max_w, max_h = map(int, specs["max_resolution"].split('x'))
        
        if info["width"] > max_w or info["height"] > max_h:
            print(f"📐 Resizing to {specs['max_resolution']}...")
            
            resized_file = f"preprocessed_resized_{input_path}"
            await session.call_tool("resize_video", {
                "input_path": current_file,
                "output_path": resized_file,
                "width": max_w,
                "height": max_h,
                "quality": specs["quality"]
            })
            current_file = resized_file
    
    # Step 3: Quality optimization (if not already done)
    if current_file == input_path and specs["quality"] != "ultra":
        print(f"⚙️  Optimizing quality ({specs['quality']})...")
        
        optimized_file = f"preprocessed_optimized_{input_path}"
        await session.call_tool("resize_video", {
            "input_path": current_file,
            "output_path": optimized_file,
            "scale_factor": 1.0,  # Keep same size
            "quality": specs["quality"]
        })
        current_file = optimized_file
    
    # Check final result
    if current_file != input_path:
        final_info = await session.call_tool("get_video_info", {
            "video_path": current_file
        })
        
        print(f"✅ Preprocessing complete:")
        print(f"  Output: {current_file}")
        print(f"  Final: {final_info['width']}x{final_info['height']}, {final_info['duration']:.1f}s, {final_info['file_size']}")
        
        # Calculate size reduction
        original_size = float(info['file_size'].split()[0])
        final_size = float(final_info['file_size'].split()[0])
        reduction = (1 - final_size / original_size) * 100
        
        if reduction > 0:
            print(f"  Size reduction: {reduction:.1f}%")
    else:
        print("✅ No preprocessing needed - video already optimal")
    
    return current_file

# Usage
preprocessed = await smart_preprocessing_workflow("large_video.mp4", "social_media")
```

## 🔧 Hardware Optimization

### Multi-Core Processing

```python
async def optimize_for_multicore():
    """Optimize processing for multi-core systems"""
    
    # Check available cores/threads
    capabilities = await session.read_resource("tools://capabilities")
    concurrent_ops = capabilities['limits']['concurrent_operations']
    
    print(f"💻 Multi-Core Optimization")
    print(f"Max concurrent operations: {concurrent_ops}")
    
    # Strategies for different core counts
    if concurrent_ops >= 8:
        strategy = "aggressive_parallel"
        recommendation = "Use maximum parallelization"
    elif concurrent_ops >= 4:
        strategy = "moderate_parallel"
        recommendation = "Use moderate parallelization"
    else:
        strategy = "sequential"
        recommendation = "Process sequentially to avoid overload"
    
    strategies = {
        "aggressive_parallel": {
            "batch_size": 8,
            "worker_count": concurrent_ops,
            "memory_buffer": "large"
        },
        "moderate_parallel": {
            "batch_size": 4,
            "worker_count": concurrent_ops // 2,
            "memory_buffer": "medium"
        },
        "sequential": {
            "batch_size": 1,
            "worker_count": 1,
            "memory_buffer": "small"
        }
    }
    
    config = strategies[strategy]
    
    print(f"\n⚙️  Recommended strategy: {strategy}")
    print(f"Recommendation: {recommendation}")
    print(f"Configuration: {config}")
    
    return config

# Usage
optimization_config = await optimize_for_multicore()
```

### Memory Management

```python
async def optimize_memory_usage():
    """Optimize memory usage for large video processing"""
    
    capabilities = await session.read_resource("tools://capabilities")
    memory_usage = capabilities['system_resources']['memory_usage']
    
    print(f"🧠 Memory Optimization")
    print(f"Current memory usage: {memory_usage:.1f}%")
    
    # Memory optimization strategies
    if memory_usage > 80:
        print("🔴 High memory usage - implementing conservative strategies")
        
        strategies = [
            "Process one video at a time",
            "Use 'low' or 'medium' quality settings",
            "Clear temp files frequently",
            "Consider restarting server if needed"
        ]
        
    elif memory_usage > 60:
        print("🟡 Moderate memory usage - balanced approach")
        
        strategies = [
            "Limit concurrent operations to 2-3",
            "Use 'medium' quality for batch processing",
            "Monitor memory during long operations"
        ]
        
    else:
        print("🟢 Good memory availability - can use full capabilities")
        
        strategies = [
            "Full concurrent processing available",
            "Can use 'high' or 'ultra' quality",
            "Batch processing recommended"
        ]
    
    print("\n💡 Memory optimization strategies:")
    for strategy in strategies:
        print(f"  • {strategy}")
    
    # Memory-efficient processing example
    print(f"\n📋 Memory-efficient batch processing:")
    
    if memory_usage > 80:
        batch_config = {
            "max_concurrent": 1,
            "quality": "low",
            "chunk_size": 1
        }
    elif memory_usage > 60:
        batch_config = {
            "max_concurrent": 2, 
            "quality": "medium",
            "chunk_size": 3
        }
    else:
        batch_config = {
            "max_concurrent": 4,
            "quality": "high",
            "chunk_size": 5
        }
    
    print(f"  Recommended config: {batch_config}")
    
    return batch_config

# Usage
memory_config = await optimize_memory_usage()
```

## 📈 Performance Monitoring

### Real-Time Performance Tracking

```python
import time
import asyncio

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.operations = []
        self.current_operation = None
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        print("📊 Performance monitoring started")
    
    async def log_operation_start(self, operation: str, details: dict = None):
        """Log the start of an operation"""
        self.current_operation = {
            "operation": operation,
            "start_time": time.time(),
            "details": details or {}
        }
        print(f"⏱️  Started: {operation}")
    
    async def log_operation_end(self, success: bool = True, error: str = None):
        """Log the end of an operation"""
        if not self.current_operation:
            return
        
        end_time = time.time()
        operation_time = end_time - self.current_operation["start_time"]
        
        operation_log = {
            **self.current_operation,
            "end_time": end_time,
            "duration": operation_time,
            "success": success,
            "error": error
        }
        
        self.operations.append(operation_log)
        
        status = "✅" if success else "❌"
        print(f"{status} Completed: {self.current_operation['operation']} ({operation_time:.1f}s)")
        
        self.current_operation = None
    
    async def get_performance_report(self):
        """Generate comprehensive performance report"""
        if not self.operations:
            print("No operations recorded")
            return
        
        total_time = time.time() - self.start_time
        successful_ops = [op for op in self.operations if op['success']]
        failed_ops = [op for op in self.operations if not op['success']]
        
        print(f"\n📊 Performance Report")
        print(f"{'='*50}")
        print(f"Total monitoring time: {total_time:.1f}s")
        print(f"Total operations: {len(self.operations)}")
        print(f"Successful: {len(successful_ops)}")
        print(f"Failed: {len(failed_ops)}")
        
        if successful_ops:
            durations = [op['duration'] for op in successful_ops]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            print(f"\nOperation Performance:")
            print(f"  Average duration: {avg_duration:.1f}s")
            print(f"  Fastest operation: {min_duration:.1f}s")
            print(f"  Slowest operation: {max_duration:.1f}s")
            print(f"  Throughput: {len(successful_ops) / total_time * 60:.1f} ops/minute")
        
        # Operation breakdown
        operation_types = {}
        for op in successful_ops:
            op_type = op['operation']
            if op_type not in operation_types:
                operation_types[op_type] = []
            operation_types[op_type].append(op['duration'])
        
        if operation_types:
            print(f"\nOperation Type Breakdown:")
            for op_type, durations in operation_types.items():
                avg_time = sum(durations) / len(durations)
                print(f"  {op_type}: {len(durations)} ops, avg {avg_time:.1f}s")
        
        # Failed operations
        if failed_ops:
            print(f"\nFailed Operations:")
            for op in failed_ops:
                print(f"  ❌ {op['operation']}: {op.get('error', 'Unknown error')}")
        
        return {
            "total_time": total_time,
            "total_operations": len(self.operations),
            "successful": len(successful_ops),
            "failed": len(failed_ops),
            "operation_types": operation_types
        }

# Usage example
async def monitored_batch_processing():
    """Example of batch processing with performance monitoring"""
    
    monitor = PerformanceMonitor()
    await monitor.start_monitoring()
    
    video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]
    
    for video_file in video_files:
        await monitor.log_operation_start("resize_video", {"file": video_file})
        
        try:
            await session.call_tool("resize_video", {
                "input_path": video_file,
                "output_path": f"resized_{video_file}",
                "width": 1280,
                "height": 720,
                "quality": "medium"
            })
            
            await monitor.log_operation_end(success=True)
            
        except Exception as e:
            await monitor.log_operation_end(success=False, error=str(e))
    
    # Generate final report
    report = await monitor.get_performance_report()
    return report

# Run monitored processing
performance_report = await monitored_batch_processing()
```

## 💡 Performance Tips Summary

### Quick Optimization Checklist

```python
def performance_optimization_checklist():
    """Quick checklist for optimizing video processing performance"""
    
    checklist = {
        "File Management": [
            "✅ Use SSD storage for temp files",
            "✅ Clean up temp files regularly", 
            "✅ Use absolute file paths",
            "✅ Keep input/output on same drive when possible"
        ],
        "Quality Settings": [
            "✅ Use 'low' for previews and testing",
            "✅ Use 'medium' for social media and web",
            "✅ Use 'high' for professional output",
            "✅ Use 'ultra' only for archival/master copies"
        ],
        "Processing Strategy": [
            "✅ Process smaller files first in batches",
            "✅ Use copy mode when possible (no re-encoding)",
            "✅ Limit concurrent operations based on system resources",
            "✅ Monitor memory and CPU usage during processing"
        ],
        "Workflow Optimization": [
            "✅ Combine multiple operations when possible",
            "✅ Use preprocessing for consistent input formats",
            "✅ Implement error recovery in batch processing",
            "✅ Cache analysis results to avoid recomputation"
        ]
    }
    
    print("⚡ Performance Optimization Checklist")
    print("=" * 50)
    
    for category, items in checklist.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  {item}")
    
    return checklist

# Display checklist
checklist = performance_optimization_checklist()
```

## 🎯 Next Steps

Now you have the knowledge to optimize your video processing workflows! Continue with:

- **[Batch Processing Guide](/guides/batch-processing/)** - Apply these optimizations to batch workflows
- **[Common Workflows](/guides/common-workflows/)** - Optimize complete production pipelines
- **[Troubleshooting Guide](/support/troubleshooting/)** - Debug performance issues
- **[FAQ](/support/faq/)** - Common performance questions

**Questions about performance?** Check our [troubleshooting guide](/support/troubleshooting/) or explore the [system capabilities documentation](/api/resources/).