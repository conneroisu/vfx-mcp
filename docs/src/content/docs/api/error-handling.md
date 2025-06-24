---
title: Error Handling
description: Comprehensive error handling and debugging guide for the VFX MCP Server
---

# Error Handling

Comprehensive error handling and debugging guide for the VFX MCP Server.

## Error Types

### FFmpeg Errors
Most common errors originate from FFmpeg processing:

```python
try:
    await trim_video("input.mp4", "output.mp4", "00:01:00", "00:02:00")
except RuntimeError as e:
    print(f"FFmpeg error: {e}")
```

### File System Errors
File access and path-related issues:

```python
# Check file existence before processing
import os
if not os.path.exists("input.mp4"):
    raise FileNotFoundError("Input file not found")
```

### Parameter Validation Errors
Invalid parameter values or types:

```python
# Validate parameter ranges
if speed_factor <= 0:
    raise ValueError("Speed factor must be positive")
```

## Common Error Scenarios

### Input File Issues
**Problem**: "No such file or directory"
- **Cause**: Incorrect file path or missing file
- **Solution**: Verify file exists and path is correct

**Problem**: "Invalid data found when processing input"
- **Cause**: Corrupted or unsupported video file
- **Solution**: Try different input file or convert format

### Output File Issues
**Problem**: "Permission denied"
- **Cause**: Insufficient write permissions
- **Solution**: Check output directory permissions

**Problem**: "File already exists"
- **Cause**: Output file exists and overwrite not enabled
- **Solution**: Delete existing file or use different name

### Processing Parameter Errors
**Problem**: "Invalid argument"
- **Cause**: Unsupported parameter values
- **Solution**: Check parameter documentation and ranges

**Problem**: "Codec not found"
- **Cause**: Requested codec not available
- **Solution**: Use supported codec or install codec

## Error Response Format

### Standard Error Structure
All tools return consistent error information:

```json
{
  "error": true,
  "message": "FFmpeg error: Invalid input format",
  "stderr": "detailed ffmpeg error output",
  "tool": "trim_video",
  "parameters": {
    "input_path": "input.mp4",
    "output_path": "output.mp4"
  }
}
```

### Context Information
Error responses include operational context:

- **Tool name**: Which tool generated the error
- **Parameters**: Input parameters that caused the error
- **Stderr**: Detailed FFmpeg error output
- **Suggestions**: Recommended fixes when available

## Debugging Strategies

### Enable Verbose Logging
Use MCP context for detailed progress information:

```python
async def process_with_logging(ctx: Context):
    if ctx:
        await ctx.info("Starting video processing...")
        await ctx.info("Applying filters...")
        await ctx.error("Processing failed: invalid codec")
```

### Parameter Validation
Validate inputs before processing:

```python
def validate_time_format(time_str: str) -> bool:
    """Validate HH:MM:SS time format"""
    import re
    pattern = r'^(\d{2}):(\d{2}):(\d{2})$'
    return bool(re.match(pattern, time_str))
```

### Step-by-Step Debugging
Break complex operations into smaller steps:

```python
# Instead of complex single operation
await complex_video_edit("input.mp4", "output.mp4")

# Break into steps for easier debugging
temp1 = await trim_video("input.mp4", "temp1.mp4", "00:01:00", "00:02:00")
temp2 = await apply_filter("temp1.mp4", "temp2.mp4", "brightness", "0.1")
final = await resize_video("temp2.mp4", "output.mp4", 1920, 1080)
```

## Error Prevention

### Input Validation
Always validate inputs before processing:

```python
# Check file format
def is_video_file(path: str) -> bool:
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    return any(path.lower().endswith(ext) for ext in video_extensions)

# Validate time ranges
def validate_time_range(start: str, end: str) -> bool:
    start_seconds = time_to_seconds(start)
    end_seconds = time_to_seconds(end)
    return start_seconds < end_seconds
```

### Resource Management
Monitor system resources:

```python
import shutil

# Check available disk space
def check_disk_space(path: str, required_gb: float) -> bool:
    free_bytes = shutil.disk_usage(path).free
    required_bytes = required_gb * 1024**3
    return free_bytes > required_bytes
```

### Graceful Degradation
Implement fallback strategies:

```python
async def process_with_fallback(input_path: str, output_path: str):
    try:
        # Try high-quality processing
        await convert_format(input_path, output_path, vcodec="h264", quality="high")
    except RuntimeError:
        # Fallback to standard quality
        await convert_format(input_path, output_path, vcodec="h264", quality="medium")
```

## Recovery Procedures

### Temporary File Cleanup
Clean up failed operations:

```python
import os
import glob

def cleanup_temp_files(pattern: str = "temp_*.mp4"):
    """Remove temporary files from failed operations"""
    for file in glob.glob(pattern):
        try:
            os.remove(file)
        except OSError:
            pass  # File already removed
```

### Operation Retry
Implement retry logic for transient failures:

```python
import asyncio

async def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    """Retry operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(delay * (2 ** attempt))
```

## Performance Optimization

### Memory Management
Monitor memory usage for large files:

```python
import psutil

def check_memory_usage():
    """Check available system memory"""
    memory = psutil.virtual_memory()
    return memory.available > 1024**3  # 1GB minimum
```

### Concurrent Processing
Limit concurrent operations to prevent resource exhaustion:

```python
import asyncio

semaphore = asyncio.Semaphore(2)  # Max 2 concurrent operations

async def process_with_limit(input_path: str, output_path: str):
    async with semaphore:
        await process_video(input_path, output_path)
```

## Support and Troubleshooting

### Log Collection
Gather diagnostic information:

1. **System Information**: OS, FFmpeg version, available codecs
2. **File Information**: Input file properties and format
3. **Error Messages**: Complete error output and context
4. **Operation Parameters**: All input parameters and settings

### Community Resources
- Check FAQ for common solutions
- Search existing issues and discussions
- Provide detailed error reports for support