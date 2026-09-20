#!/usr/bin/env python3
"""
Fast Subtitle Embedding Engine:
Embeds timestamped subtitles directly into the MP4 container using native mov_text.
- Zero re-encoding loss
- Instant execution (<1 second)
- Toggles on/off in QuickTime, VLC, and imports automatically into video editors.

Usage:
  python3 Pipeline_Tools/burn_captions.py "<REEL_OR_VIDEO_FOLDER>"
"""

import sys
import subprocess
from pathlib import Path

def embed_subtitles(folder_path: str):
    folder = Path(folder_path).resolve()
    video_file = folder / "video.mp4"
    srt_file = folder / "transcript.srt"
    output_file = folder / "video_subtitled.mp4"

    if not video_file.exists():
        print(f"[-] video.mp4 not found in {folder}")
        return False

    if not srt_file.exists() or srt_file.stat().st_size == 0:
        print(f"[-] transcript.srt not found or empty in {folder}")
        return False

    print(f"\n[*] Embedding synchronized subtitles into MP4 container...")
    print(f"    Source: {video_file.name}")
    print(f"    Subtitles: {srt_file.name}")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_file),
        "-i", str(srt_file),
        "-c", "copy",
        "-c:s", "mov_text",
        str(output_file)
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output_file.exists():
            print(f"[✓] Created subtitled video: {output_file.name}")
            print(f"    -> {output_file.resolve()}\n")
            return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Error embedding subtitles: {e.stderr.decode()[:300]}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 Pipeline_Tools/burn_captions.py <FOLDER_PATH>")
        sys.exit(1)

    embed_subtitles(sys.argv[1])
