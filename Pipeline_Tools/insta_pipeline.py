#!/usr/bin/env python3
"""
Wrapper for media_pipeline.py
Maintains backwards compatibility for insta_pipeline.py calls.
"""
import sys
from media_pipeline import process_media_link

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 insta_pipeline.py <INSTAGRAM_OR_YOUTUBE_URL>")
        sys.exit(1)

    process_media_link(sys.argv[1])
