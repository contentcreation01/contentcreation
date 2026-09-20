# GitHub Quickstart & Cross-Platform Installation Guide

Welcome to the **AI Content Creation Studio & Production Pipeline**.
This guide helps you clone and run this repository on **macOS**, **Windows**, or **Linux** in under 60 seconds.

---

## ⚡ 1-Click Automated Setup

### On macOS (Apple Silicon M1/M2/M3/M4 & Intel):
Open Terminal in the project root and run:
```bash
bash Pipeline_Tools/Setup_Dependencies/setup_mac.sh
```
*Automatically installs Homebrew dependencies (`ffmpeg`, `yt-dlp`, `whisper-cpp`), downloads the multilingual Whisper AI model weights, and validates your environment.*

### On Windows (10 / 11):
Double-click or run in Command Prompt:
```cmd
Pipeline_Tools\Setup_Dependencies\setup_windows.bat
```
*Installs `yt-dlp`, checks `ffmpeg` (or installs via `winget`), downloads the Whisper AI model weights, and verifies your system.*

---

## 🛠️ Manual Step-by-Step Installation

If you prefer to install dependencies manually:

### Step 1: System Binaries
* **FFmpeg**:
  * macOS: `brew install ffmpeg`
  * Windows: `winget install Gyan.FFmpeg` (or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/))
  * Linux: `sudo apt install ffmpeg`
* **yt-dlp**:
  * macOS: `brew install yt-dlp`
  * Windows / Linux: `pip install yt-dlp`
* **Whisper CLI** (Optional for speech-to-text):
  * macOS: `brew install whisper-cpp`
  * Windows: Download release from [whisper.cpp releases](https://github.com/ggerganov/whisper.cpp/releases)

### Step 2: Download AI Model Weights
Because GitHub has a strict 100MB file limit, model weights are excluded from Git and downloaded locally:
```bash
python3 Pipeline_Tools/Setup_Dependencies/download_models.py
```
*(Downloads `ggml-base.bin` ~141 MB directly from Hugging Face into `Pipeline_Tools/models/`).*

### Step 3: Verify Environment
Run the diagnostic scanner:
```bash
python3 Pipeline_Tools/Setup_Dependencies/check_environment.py
```

---

## 🚀 Running the Studio

### 1. Launch the Local Creator Studio Dashboard (Visual Browser UI):
```bash
python3 Pipeline_Tools/studio_ui.py
```
Open `http://localhost:8080` in your browser.

### 2. Process Any Media Link via CLI:
```bash
python3 Pipeline_Tools/media_pipeline.py "<INSTAGRAM_YOUTUBE_TIKTOK_OR_TWITTER_URL>"
```

### 3. Evaluate Viral Hooks:
```bash
python3 Pipeline_Tools/hook_scorer.py --hook "Your opening hook line here"
```
