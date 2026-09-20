#!/usr/bin/env bash
# ==============================================================================
# 1-Click Setup Script for macOS (Apple Silicon M1/M2/M3/M4 & Intel)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=================================================================="
echo "⚡ AI Content Creation Pipeline - macOS Setup"
echo "📂 Workspace: $WORKSPACE_ROOT"
echo "=================================================================="

# 1. Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "⚠️ Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "📦 Installing system tools via Homebrew (ffmpeg, yt-dlp, whisper-cpp)..."
brew install ffmpeg yt-dlp whisper-cpp || true

# 2. Check Python
if ! command -v python3 &> /dev/null; then
    echo "⚠️ Python 3 not found. Installing python3 via Homebrew..."
    brew install python
fi

# 3. Install Python requirements
echo "🐍 Installing Python packages..."
python3 -m pip install -q -r "$SCRIPT_DIR/requirements.txt" || true

# 4. Download Whisper AI Models
echo "🤖 Downloading on-device Whisper speech model..."
python3 "$SCRIPT_DIR/download_models.py"

# 5. Run Environment Diagnostic
echo ""
python3 "$SCRIPT_DIR/check_environment.py"
