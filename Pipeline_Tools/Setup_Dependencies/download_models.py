#!/usr/bin/env python3
"""
Whisper AI Model Downloader
===========================
Automatically downloads official GGML Whisper models from Hugging Face:
- ggml-base.bin (Multilingual, ~141 MB)
- ggml-base.en.bin (English-only, ~141 MB)

Usage:
  python3 download_models.py [--force] [--all]
"""

import sys
import os
import urllib.request
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
MODELS_DIR = BASE_DIR / "models"

MODELS = {
    "ggml-base.bin": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
        "description": "Multilingual Base Model (Auto-detects Hindi, Spanish, English, etc.)",
        "approx_size_mb": 141
    },
    "ggml-base.en.bin": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
        "description": "English-Only Optimized Base Model",
        "approx_size_mb": 141
    }
}

def format_size(bytes_val):
    return f"{bytes_val / (1024 * 1024):.1f} MB"

def download_with_progress(url, dest_path):
    """Downloads URL to dest_path with a real-time progress bar."""
    print(f"📥 Connecting to: {url}")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 64  # 64 KB
        downloaded = 0

        temp_dest = dest_path.with_suffix(".tmp")
        with open(temp_dest, 'wb') as out_file:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                out_file.write(buffer)
                
                if total_size > 0:
                    percent = downloaded * 100 / total_size
                    bar_len = 30
                    filled = int(bar_len * downloaded / total_size)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    sys.stdout.write(f"\r   [{bar}] {percent:5.1f}% ({format_size(downloaded)} / {format_size(total_size)})")
                    sys.stdout.flush()

        print()
        temp_dest.replace(dest_path)

def ensure_models(force=False, all_models=False):
    """Checks and downloads Whisper models."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 65)
    print("🤖 WHISPER AI MODEL MANAGER")
    print(f"📁 Target Folder: {MODELS_DIR}")
    print("=" * 65)

    targets = ["ggml-base.bin"]
    if all_models:
        targets.append("ggml-base.en.bin")

    for filename in targets:
        info = MODELS[filename]
        dest = MODELS_DIR / filename
        print(f"\n📦 Model: {filename} ({info['description']})")

        if dest.exists() and not force:
            size_mb = dest.stat().st_size / (1024 * 1024)
            if size_mb > 100:
                print(f"   [✓] Already installed ({size_mb:.1f} MB). Skipping download.")
                continue
            else:
                print(f"   [!] File exists but looks incomplete ({size_mb:.1f} MB). Re-downloading...")

        try:
            download_with_progress(info['url'], dest)
            print(f"   ✅ Installed successfully: {dest}")
        except Exception as e:
            print(f"   ❌ Download failed: {e}", file=sys.stderr)

    print("\n" + "=" * 65)
    print("✨ Model check completed!")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Whisper Model Downloader")
    parser.add_argument("--force", action="store_true", help="Force re-download even if file exists")
    parser.add_argument("--all", action="store_true", help="Download both multilingual and English models")
    parser.add_argument("--check", action="store_true", help="Only check models without downloading")
    args = parser.parse_args()

    if args.check:
        print("Checking installed models:")
        for name, info in MODELS.items():
            path = MODELS_DIR / name
            status = f"Installed ({format_size(path.stat().st_size)})" if path.exists() else "Not found"
            print(f" • {name}: {status}")
        return

    ensure_models(force=args.force, all_models=args.all)

if __name__ == "__main__":
    main()
