#!/usr/bin/env python3
"""
Example: Create a video montage.

This example demonstrates how to use the VFX MCP server to create
a video montage by trimming clips from multiple videos and concatenating
them together with background music.
"""

import asyncio
from pathlib import Path

from fastmcp import Client


async def create_montage():
    """
    Create a video montage from multiple source videos.

    This function demonstrates:
    1. Trimming specific segments from videos
    2. Concatenating the clips together
    3. Adding background music to the final montage
    """
    # Connect to the VFX MCP server
    # Note: The server should be running with: uv run python main.py
    async with Client("python main.py") as client:
        print("Connected to VFX MCP server")

        # Define our source clips
        # In a real scenario, these would be actual video files
        clips_to_extract = [
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
        print(
            "\n1. Extracting clips from source videos..."
        )
        clips = []

        for i, (
            video,
            start,
            duration,
        ) in enumerate(clips_to_extract):
            clip_path = f"clip_{i}.mp4"

            # Check if source video exists
            if not Path(video).exists():
                print(
                    f"   ⚠️  Skipping {video} (file not found)"
                )
                continue

            print(
                f"   Trimming {video} from {start}s for {duration}s..."
            )

            try:
                await client.call_tool(
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
                print(
                    f"   ✗ Error trimming {video}: {e}"
                )

        if len(clips) < 2:
            print(
                "\n❌ Not enough clips to create montage (need at least 2)"
            )
            return

        # Step 2: Concatenate the clips
        print(
            f"\n2. Concatenating {len(clips)} clips..."
        )
        montage_path = "montage.mp4"

        try:
            await client.call_tool(
                "concatenate_videos",
                {
                    "input_paths": clips,
                    "output_path": montage_path,
                },
            )
            print(
                f"   ✓ Created montage: {montage_path}"
            )
        except Exception as e:
            print(
                f"   ✗ Error concatenating videos: {e}"
            )
            return

        # Step 3: Add background music (if available)
        music_path = "background_music.mp3"
        if Path(music_path).exists():
            print(
                "\n3. Adding background music..."
            )
            final_path = "final_montage.mp4"

            try:
                await client.call_tool(
                    "add_audio",
                    {
                        "video_path": montage_path,
                        "audio_path": music_path,
                        "output_path": final_path,
                    },
                )
                print(
                    f"   ✓ Created final montage with music: {final_path}"
                )
            except Exception as e:
                print(
                    f"   ✗ Error adding audio: {e}"
                )
        else:
            print(
                f"\n3. Skipping background music ('{music_path}' not found)"
            )
            final_path = montage_path

        # Step 4: Get information about the final video
        print("\n4. Final montage information:")
        try:
            info = await client.call_tool(
                "get_video_info",
                {"video_path": final_path},
            )

            # Parse the result
            import json

            if hasattr(info.content[0], "text"):
                info_data = json.loads(
                    info.content[0].text
                )
            else:
                info_data = info.content[0]

            print(
                f"   Duration: {info_data['duration']:.2f} seconds"
            )
            print(
                f"   Resolution: {info_data['video']['width']}x"
                f"{info_data['video']['height']}"
            )
            print(
                f"   Video codec: {info_data['video']['codec']}"
            )
            if "audio" in info_data:
                print(
                    f"   Audio codec: {info_data['audio']['codec']}"
                )
        except Exception as e:
            print(
                f"   ✗ Error getting video info: {e}"
            )

        print("\n✅ Montage creation complete!")


def main():
    """Run the montage creation example."""
    print("=== VFX MCP Video Montage Example ===")
    print("\nThis example requires:")
    print("- The VFX MCP server to be running")
    print(
        "- Video files: vacation.mp4, birthday.mp4, concert.mp4"
    )
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
