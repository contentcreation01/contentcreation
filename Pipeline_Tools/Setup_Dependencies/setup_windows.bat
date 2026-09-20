@echo off
REM ==============================================================================
REM 1-Click Setup Script for Windows 10 / 11
REM ==============================================================================
setlocal EnableDelayedExpansion

echo ==================================================================
echo   AI Content Creation Pipeline - Windows Setup
echo ==================================================================

REM 1. Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python not detected. Please install Python 3.10+ from https://www.python.org/downloads/
    echo     Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo [✓] Python detected.

REM 2. Install Python requirements
echo [*] Installing Python requirements...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"

REM 3. Check FFmpeg
ffmpeg -version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] FFmpeg not found in PATH.
    echo [*] Attempting automated installation via winget...
    winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Winget install skipped. Please download FFmpeg manually from:
        echo     https://www.gyan.dev/ffmpeg/builds/
        echo     and add its bin folder to your Windows System PATH.
    )
) else (
    echo [✓] FFmpeg detected.
)

REM 4. Download Whisper AI Models
echo [*] Checking / Downloading Whisper AI speech models...
python "%~dp0download_models.py"

REM 5. Run Environment Diagnostic
echo.
python "%~dp0check_environment.py"

echo.
echo Setup finished! You can now start the studio with:
echo python Pipeline_Tools\studio_ui.py
pause
