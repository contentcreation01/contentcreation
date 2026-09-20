#!/usr/bin/env python3
"""
15-Second Teaser Clipper
========================
Automatically extracts a high-energy 15-second teaser clip from video.mp4
with a smooth audio fade-out for Instagram Stories, WhatsApp Status, or preview reels.

Usage:
  python3 Pipeline_Tools/teaser_clipper.py "<PROJECT_FOLDER_OR_VIDEO_PATH>" [--duration 15.0] [--fade 0.75]
"""

import sys
import os
import subprocess
import argparse
import json

def get_video_duration(video_path):
    """Returns video duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        return float(data.get("format", {}).get("duration", 0.0))
    except Exception as e:
        print(f"⚠️ Could not probe duration: {e}", file=sys.stderr)
        return 15.0

def clip_teaser(target_path, duration=15.0, fade_duration=0.75):
    """Extracts teaser_15s.mp4 with audio fade out."""
    if os.path.isdir(target_path):
        video_path = os.path.join(target_path, "video.mp4")
        output_path = os.path.join(target_path, "teaser_15s.mp4")
    elif os.path.isfile(target_path):
        video_path = target_path
        output_dir = os.path.dirname(target_path)
        output_path = os.path.join(output_dir, "teaser_15s.mp4")
    else:
        print(f"❌ Error: Target path not found: {target_path}", file=sys.stderr)
        return None

    if not os.path.exists(video_path):
        print(f"❌ Error: video.mp4 not found at: {video_path}", file=sys.stderr)
        return None

    total_duration = get_video_duration(video_path)
    target_duration = min(duration, total_duration)
    fade_start = max(0.0, target_duration - fade_duration)

    print(f"🎬 Clipping teaser: {target_duration:.2f}s (Audio fade from {fade_start:.2f}s to {target_duration:.2f}s)")
    print(f"   Source: {video_path}")
    print(f"   Output: {output_path}")

    # FFmpeg command: clip video, re-encode with fast preset + audio fade out
    cmd = [
        "ffmpeg", "-y",
        "-ss", "0",
        "-i", video_path,
        "-t", f"{target_duration:.3f}",
        "-af", f"afade=t=out:st={fade_start:.3f}:d={fade_duration:.3f}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Teaser successfully created: {output_path} ({size_mb:.2f} MB)")
            return output_path
        else:
            print("❌ Teaser file creation failed.", file=sys.stderr)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr.decode()}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="15-Second Teaser Clipper")
    parser.add_argument("target", help="Path to project directory or video.mp4")
    parser.add_argument("--duration", type=float, default=15.0, help="Teaser duration in seconds (default: 15.0)")
    parser.add_argument("--fade", type=float, default=0.75, help="Audio fade-out duration in seconds (default: 0.75)")
    args = parser.parse_args()

    clip_teaser(args.target, duration=args.duration, fade_duration=args.fade)

if __name__ == "__main__":
    main()
