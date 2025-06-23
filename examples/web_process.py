#!/usr/bin/env python3
"""
Example: Process video for web deployment.

This example demonstrates how to prepare a video for web deployment by:
1. Converting to web-friendly format
2. Creating multiple resolution versions
3. Generating thumbnails
"""

import asyncio
from pathlib import Path

from fastmcp import Client


async def process_for_web(input_video: str):
    """
    Process a video for web deployment.

    Args:
        input_video: Path to the input video file

    This function demonstrates:
    1. Converting to H.264/AAC MP4 format
    2. Creating multiple resolutions for adaptive streaming
    3. Generating thumbnail images
    """
    async with Client("python main.py") as client:
        print(
            f"Processing '{input_video}' for web deployment..."
        )

        # Check if input exists
        if not Path(input_video).exists():
            print(
                f"❌ Error: '{input_video}' not found"
            )
            return

        # Get original video info
        print("\n1. Analyzing source video...")
        try:
            info_result = await client.call_tool(
                "get_video_info",
                {"video_path": input_video},
            )

            # Parse the result
            import json

            if hasattr(
                info_result.content[0], "text"
            ):
                info = json.loads(
                    info_result.content[0].text
                )
            else:
                info = info_result.content[0]

            print(
                f"   Original resolution: {info['video']['width']}x"
                f"{info['video']['height']}"
            )
            print(
                f"   Duration: {info['duration']:.2f} seconds"
            )
            print(f"   Format: {info['format']}")
            original_width = info["video"][
                "width"
            ]
        except Exception as e:
            print(
                f"   ✗ Error getting video info: {e}"
            )
            return

        # Step 1: Convert to web-friendly format
        print(
            "\n2. Converting to web-optimized format..."
        )
        web_video = "web_optimized.mp4"

        # Note: In the current implementation, convert_format is not available
        # This is a placeholder for when the tool is implemented
        print(
            "   ⚠️  Format conversion not yet implemented"
        )
        print(
            "   Using resize as a workaround to re-encode..."
        )

        try:
            # Use resize with same dimensions to trigger re-encoding
            await client.call_tool(
                "resize_video",
                {
                    "input_path": input_video,
                    "output_path": web_video,
                    "width": original_width,
                },
            )
            print(
                f"   ✓ Created web-optimized video: {web_video}"
            )
        except Exception as e:
            print(
                f"   ✗ Error optimizing video: {e}"
            )
            web_video = input_video  # Fall back to original

        # Step 2: Create multiple resolutions
        print(
            "\n3. Creating multiple resolutions..."
        )

        # Define target resolutions (width, name)
        # Only create resolutions smaller than the original
        all_resolutions = [
            (1920, "1080p"),
            (1280, "720p"),
            (854, "480p"),
            (640, "360p"),
        ]

        resolutions = [
            (w, n)
            for w, n in all_resolutions
            if w <= original_width
        ]

        created_versions = []
        for width, name in resolutions:
            output_path = f"web_video_{name}.mp4"
            print(
                f"   Creating {name} version ({width}px wide)..."
            )

            try:
                await client.call_tool(
                    "resize_video",
                    {
                        "input_path": web_video,
                        "output_path": output_path,
                        "width": width,
                    },
                )
                created_versions.append(
                    (output_path, width, name)
                )
                print(
                    f"   ✓ Created {output_path}"
                )
            except Exception as e:
                print(
                    f"   ✗ Error creating {name} version: {e}"
                )

        # Step 3: Generate thumbnails
        print("\n4. Generating thumbnails...")

        # Note: In the current implementation, generate_thumbnail is not available
        # This is a placeholder for when the tool is implemented
        print(
            "   ⚠️  Thumbnail generation not yet implemented"
        )
        print(
            "   Placeholder for future implementation:"
        )

        thumbnail_times = [
            0,
            info["duration"] / 4,
            info["duration"] / 2,
        ]
        for i, timestamp in enumerate(
            thumbnail_times
        ):
            print(
                f"   Would generate thumbnail_{i}.jpg at {timestamp:.1f}s"
            )

        # Step 4: Create adaptive streaming manifest (placeholder)
        print(
            "\n5. Adaptive streaming preparation:"
        )
        print(
            "   For HLS or DASH streaming, you would:"
        )
        print(
            "   - Segment each resolution version"
        )
        print(
            "   - Create manifest files (.m3u8 or .mpd)"
        )
        print(
            "   - Set up proper CORS headers on your web server"
        )

        # Summary
        print("\n✅ Web processing complete!")
        print(
            f"\nCreated {len(created_versions)} resolution versions:"
        )
        for (
            path,
            _width,
            name,
        ) in created_versions:
            print(f"   - {name}: {path}")

        # Sample HTML5 video player code
        print("\nSample HTML5 video element:")
        print("```html")
        print(
            '<video controls width="100%" poster="thumbnail_1.jpg">'
        )
        for path, width, _name in reversed(
            created_versions
        ):
            print(
                f'  <source src="{path}" type="video/mp4" '
                f'media="(min-width: {width}px)">'
            )
        print(
            "  Your browser does not support the video tag."
        )
        print("</video>")
        print("```")


async def batch_process_directory(
    directory: str = ".",
):
    """
    Process all videos in a directory for web deployment.

    Args:
        directory: Directory containing video files
    """
    video_extensions = [
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".webm",
    ]
    videos = []

    # Find all video files
    for file in Path(directory).iterdir():
        if (
            file.is_file()
            and file.suffix.lower()
            in video_extensions
        ):
            videos.append(file)

    if not videos:
        print(
            f"No video files found in '{directory}'"
        )
        return

    print(
        f"Found {len(videos)} video(s) to process:"
    )
    for video in videos:
        print(f"  - {video.name}")

    # Process each video
    for i, video in enumerate(videos, 1):
        print(f"\n{'='*50}")
        print(
            f"Processing video {i}/{len(videos)}: {video.name}"
        )
        print("=" * 50)

        await process_for_web(str(video))


def main():
    """Run the web processing example."""
    import sys

    print(
        "=== VFX MCP Web Video Processing Example ==="
    )
    print("\nUsage:")
    print("  python web_process.py [video_file]")
    print(
        "  python web_process.py  # Process all videos in current directory"
    )
    print("\nPress Ctrl+C to cancel\n")

    try:
        if len(sys.argv) > 1:
            # Process specific video
            asyncio.run(
                process_for_web(sys.argv[1])
            )
        else:
            # Process all videos in current directory
            asyncio.run(batch_process_directory())
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
