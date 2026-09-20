#!/usr/bin/env python3
"""
Cross-Platform Environment Diagnostic Scanner
=============================================
Scans system dependencies across macOS and Windows:
- Python 3.10+
- FFmpeg & FFprobe
- yt-dlp
- Whisper CLI binary & models
- Speech synthesis engine (macOS say / Windows PowerShell System.Speech)

Usage:
  python3 check_environment.py
"""

import sys
import os
import shutil
import subprocess
import platform
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
MODELS_DIR = BASE_DIR / "models"
OCR_BIN = BASE_DIR / "ocr_helper"

def print_header():
    print("=" * 68)
    print("🔍 AI CONTENT CREATION PIPELINE - ENVIRONMENT DIAGNOSTIC")
    print(f"🖥️  OS: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"🐍 Python: {sys.version.split()[0]} ({sys.executable})")
    print("=" * 68)

def check_binary(name, common_paths=None):
    """Locates a binary in PATH or common directories."""
    path = shutil.which(name)
    if path:
        return path
    if common_paths:
        for cp in common_paths:
            p = Path(cp)
            if p.exists() and os.access(p, os.X_OK):
                return str(p)
    return None

def check_speech_engine():
    """Checks speech synthesis availability."""
    if sys.platform == "darwin":
        if shutil.which("say"):
            return True, "macOS native 'say' engine available"
        return False, "macOS 'say' not found"
    elif sys.platform == "win32":
        try:
            cmd = ["powershell", "-NoProfile", "-Command", "Add-Type -AssemblyName System.Speech; [System.Speech.Synthesis.SpeechSynthesizer]"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return True, "Windows PowerShell System.Speech available"
            return False, "PowerShell System.Speech failed"
        except Exception as e:
            return False, f"PowerShell check failed: {e}"
    else:
        if shutil.which("espeak") or shutil.which("espeak-ng"):
            return True, "Linux espeak available"
        return False, "No speech synthesis binary found (install espeak)"

def run_diagnostics():
    print_header()
    all_ok = True
    missing_fix = []

    # 1. Python Version
    py_ver = sys.version_info
    if py_ver >= (3, 10):
        print(f" [✓] Python {py_ver.major}.{py_ver.minor}.{py_ver.micro} (Supported)")
    else:
        print(f" [✗] Python {py_ver.major}.{py_ver.minor} is outdated. Python 3.10+ required.")
        missing_fix.append("Update Python to 3.10 or newer (https://www.python.org/downloads/)")
        all_ok = False

    # 2. FFmpeg & FFprobe
    ffmpeg = check_binary("ffmpeg", ["/opt/homebrew/bin/ffmpeg", "C:\\ffmpeg\\bin\\ffmpeg.exe"])
    ffprobe = check_binary("ffprobe", ["/opt/homebrew/bin/ffprobe", "C:\\ffmpeg\\bin\\ffprobe.exe"])
    if ffmpeg and ffprobe:
        print(f" [✓] FFmpeg: {ffmpeg}")
        print(f" [✓] FFprobe: {ffprobe}")
    else:
        print(f" [✗] FFmpeg/FFprobe missing.")
        if sys.platform == "darwin":
            missing_fix.append("brew install ffmpeg")
        else:
            missing_fix.append("winget install Gyan.FFmpeg   (or download from https://ffmpeg.org)")
        all_ok = False

    # 3. yt-dlp
    ytdlp = check_binary("yt-dlp", ["/opt/homebrew/bin/yt-dlp", "C:\\Program Files\\yt-dlp\\yt-dlp.exe"])
    if ytdlp:
        print(f" [✓] yt-dlp: {ytdlp}")
    else:
        print(f" [✗] yt-dlp missing.")
        if sys.platform == "darwin":
            missing_fix.append("brew install yt-dlp  (or: pip install yt-dlp)")
        else:
            missing_fix.append("pip install yt-dlp  (or: winget install yt-dlp)")
        all_ok = False

    # 4. Whisper CLI
    whisper = check_binary("whisper-cli", ["/opt/homebrew/bin/whisper-cli", "C:\\whisper\\whisper-cli.exe"])
    if not whisper:
        whisper = check_binary("whisper", ["/opt/homebrew/bin/whisper"])
    
    if whisper:
        print(f" [✓] Whisper CLI: {whisper}")
    else:
        print(f" [!] Whisper CLI not found in PATH.")
        if sys.platform == "darwin":
            missing_fix.append("brew install whisper-cpp")
        else:
            missing_fix.append("Download whisper.cpp Windows release (https://github.com/ggerganov/whisper.cpp/releases)")

    # 5. Whisper AI Model
    model_multilingual = MODELS_DIR / "ggml-base.bin"
    model_en = MODELS_DIR / "ggml-base.en.bin"
    if model_multilingual.exists() and model_multilingual.stat().st_size > 100 * 1024 * 1024:
        print(f" [✓] Whisper Model: {model_multilingual.name} ({model_multilingual.stat().st_size / (1024*1024):.1f} MB)")
    elif model_en.exists() and model_en.stat().st_size > 100 * 1024 * 1024:
        print(f" [✓] Whisper Model: {model_en.name} ({model_en.stat().st_size / (1024*1024):.1f} MB)")
    else:
        print(f" [✗] Whisper AI Model missing in: {MODELS_DIR}")
        missing_fix.append(f"python3 \"{Path(__file__).parent / 'download_models.py'}\"")
        all_ok = False

    # 6. Speech Engine
    has_speech, speech_desc = check_speech_engine()
    if has_speech:
        print(f" [✓] Voiceover Synthesis: {speech_desc}")
    else:
        print(f" [!] Voiceover Synthesis: {speech_desc}")

    # 7. OCR Capability
    if sys.platform == "darwin":
        if OCR_BIN.exists() and os.access(OCR_BIN, os.X_OK):
            print(f" [✓] Apple Vision OCR Helper: {OCR_BIN}")
        else:
            print(f" [!] Apple Vision OCR Helper not compiled.")
    else:
        print(" [i] Native Apple Vision OCR skipped (macOS only). Fallback to caption/transcript active.")

    print("=" * 68)
    if all_ok:
        print("🎉 ALL CRITICAL DEPENDENCIES INSTALLED AND READY!")
        print("   You can start the studio right now:")
        print("   ▶ python3 Pipeline_Tools/studio_ui.py")
        print("   ▶ python3 Pipeline_Tools/media_pipeline.py <URL>")
    else:
        print("⚠️  MISSING DEPENDENCIES DETECTED. Run these commands to fix:")
        for idx, cmd in enumerate(missing_fix, 1):
            print(f"   {idx}. {cmd}")
    print("=" * 68)
    return all_ok

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
