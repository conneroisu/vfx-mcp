#!/usr/bin/env python3
"""Example: Create a video montage.

This example demonstrates how to use the VFX MCP server to create
a video montage by trimming clips from multiple videos and concatenating
them together with background music.

Typical usage example:
    $ python examples/montage.py
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TypedDict

from fastmcp import Client


class VideoInfo(TypedDict, total=False):
    """Type definition for video stream information."""
    width: int
    height: int
    codec: str


class AudioInfo(TypedDict, total=False):
    """Type definition for audio stream information."""
    codec: str


class VideoMetadata(TypedDict, total=False):
    """Type definition for video metadata returned by get_video_info."""
    duration: float
    video: VideoInfo
    audio: AudioInfo


def parse_video_metadata(text: str) -> VideoMetadata | None:
    """Parse JSON text into VideoMetadata, returning None on error."""
    try:
        # Parse JSON - we accept the Any type here as it's unavoidable
        json_data: object = json.loads(text)
        
        # Type guard to ensure we have a dict
        if not isinstance(json_data, dict):
            return None
            
        # Now build the typed result with explicit checking
        result: VideoMetadata = {}
        
        # Check duration with explicit type narrowing
        duration_raw = json_data.get("duration")
        if isinstance(duration_raw, (int, float)):
            result["duration"] = float(duration_raw)
            
        # Check video with explicit type narrowing
        video_raw = json_data.get("video")
        if isinstance(video_raw, dict):
            video_info: VideoInfo = {}
            # Type narrow each field individually
            width_raw = video_raw.get("width")
            height_raw = video_raw.get("height")
            codec_raw = video_raw.get("codec")
            
            if isinstance(width_raw, int):
                video_info["width"] = width_raw
            if isinstance(height_raw, int):
                video_info["height"] = height_raw
            if isinstance(codec_raw, str):
                video_info["codec"] = codec_raw
                
            if video_info:  # Only add if we found valid data
                result["video"] = video_info
                
        # Check audio with explicit type narrowing
        audio_raw = json_data.get("audio")
        if isinstance(audio_raw, dict):
            audio_info: AudioInfo = {}
            codec_raw = audio_raw.get("codec")
            
            if isinstance(codec_raw, str):
                audio_info["codec"] = codec_raw
                
            if audio_info:  # Only add if we found valid data
                result["audio"] = audio_info
                
        return result if result else None
        
    except (json.JSONDecodeError, ValueError):
        return None


async def create_montage() -> None:
    """Create a video montage from multiple source videos.

    Demonstrates a complete workflow for creating a video montage:
    1. Trimming specific segments from source videos
    2. Concatenating the clips together
    3. Adding background music to the final montage
    4. Extracting final video information

    Requires source videos (vacation.mp4, birthday.mp4, concert.mp4)
    and optionally background_music.mp3 in the current directory.
    """
    # Connect to the VFX MCP server
    # Note: The server should be running with: uv run python main.py
    async with Client("python main.py") as client:
        print("Connected to VFX MCP server")

        # Define source clips with (filename, start_time, duration) tuples
        # In a real scenario, these would be actual video files
        clips_to_extract: list[tuple[str, int, int]] = [
            (
                "vacation.mp4",
                30,
                5,
            ),  # 5 seconds starting at 30s
            (
                "birthday.mp4",
                120,
                8,
            ),  # 8 seconds starting at 120s
            (
                "concert.mp4",
                45,
                6,
            ),  # 6 seconds starting at 45s
        ]

        # Step 1: Trim clips from source videos
        print("\n1. Extracting clips from source videos...")
        clips: list[str] = []

        for i, (
            video,
            start,
            duration,
        ) in enumerate(clips_to_extract):
            clip_path: str = f"clip_{i}.mp4"

            # Check if source video exists
            if not Path(video).exists():
                print(f"   ⚠️  Skipping {video} (file not found)")
                continue

            print(f"   Trimming {video} from {start}s for {duration}s...")

            try:
                _ = await client.call_tool(
                    "trim_video",
                    {
                        "input_path": video,
                        "output_path": clip_path,
                        "start_time": start,
                        "duration": duration,
                    },
                )
                clips.append(clip_path)
                print(f"   ✓ Created {clip_path}")
            except Exception as e:
                print(f"   ✗ Error trimming {video}: {e}")

        if len(clips) < 2:
            print("\n❌ Not enough clips to create montage (need at least 2)")
            return

        # Step 2: Concatenate the clips
        print(f"\n2. Concatenating {len(clips)} clips...")
        montage_path: str = "montage.mp4"

        try:
            _ = await client.call_tool(
                "concatenate_videos",
                {
                    "input_paths": clips,
                    "output_path": montage_path,
                },
            )
            print(f"   ✓ Created montage: {montage_path}")
        except Exception as e:
            print(f"   ✗ Error concatenating videos: {e}")
            return

        # Step 3: Add background music (if available)
        music_path: str = "background_music.mp3"
        final_path: str
        if Path(music_path).exists():
            print("\n3. Adding background music...")
            final_path = "final_montage.mp4"

            try:
                _ = await client.call_tool(
                    "add_audio",
                    {
                        "video_path": montage_path,
                        "audio_path": music_path,
                        "output_path": final_path,
                    },
                )
                print(f"   ✓ Created final montage with music: {final_path}")
            except Exception as e:
                print(f"   ✗ Error adding audio: {e}")
        else:
            print(f"\n3. Skipping background music ('{music_path}' not found)")
            final_path = montage_path

        # Step 4: Get information about the final video
        print("\n4. Final montage information:")
        try:
            info = await client.call_tool(
                "get_video_info",
                {"video_path": final_path},
            )

            # Parse the result from MCP response
            # info is a list[MCPContent] - we need the first element
            metadata: VideoMetadata | None = None
            if info and len(info) > 0:
                content = info[0]
                # MCPContent types have a 'type' attribute we can check
                if hasattr(content, "type") and hasattr(content, "text"):
                    content_type = getattr(content, "type", None)
                    if content_type == "text":
                        # Now we know it's a TextContent, so text attribute exists
                        text_value = getattr(content, "text", None)
                        if isinstance(text_value, str):
                            # Parse JSON using our type-safe helper
                            metadata = parse_video_metadata(text_value)

            # Access the parsed data with proper type handling
            if metadata:
                duration = metadata.get("duration")
                if duration is not None:
                    print(f"   Duration: {duration:.2f} seconds")
                
                video_info = metadata.get("video")
                if video_info:
                    width = video_info.get("width")
                    height = video_info.get("height")
                    codec = video_info.get("codec")
                    if width is not None and height is not None:
                        print(f"   Resolution: {width}x{height}")
                    if codec is not None:
                        print(f"   Video codec: {codec}")
                
                audio_info = metadata.get("audio")
                if audio_info:
                    audio_codec = audio_info.get("codec")
                    if audio_codec is not None:
                        print(f"   Audio codec: {audio_codec}")
        except Exception as e:
            print(f"   ✗ Error getting video info: {e}")

        print("\n✅ Montage creation complete!")


def main() -> None:
    """Run the montage creation example.

    Displays usage information and executes the montage creation workflow.
    Handles keyboard interrupts gracefully and reports any errors.
    """
    print("=== VFX MCP Video Montage Example ===")
    print("\nThis example requires:")
    print("- The VFX MCP server to be running")
    print("- Video files: vacation.mp4, birthday.mp4, concert.mp4")
    print("- Optional: background_music.mp3")
    print("\nPress Ctrl+C to cancel\n")

    try:
        asyncio.run(create_montage())
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
