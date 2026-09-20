#!/usr/bin/env python3
"""
On-Device Neural Voiceover Dubber
=================================
Synthesizes realistic human-cadence voiceover guide tracks (voiceover_guide.mp3)
from teleprompter scripts or any text using macOS native neural speech synthesis.

Features:
- Auto-translates teleprompter cues ([PAUSE], [BREATHE]) into millisecond silences ([[slnc 500]]).
- Normalizes pacing to viral retention standards (~150-165 WPM).
- Auto-discovers best installed system neural voice (Daniel, Samantha, Ava, Eddy, etc.).
- Encodes studio-grade 320 kbps 48kHz master audio track.

Usage:
  python3 Pipeline_Tools/vocal_dubber.py "<PROJECT_FOLDER_OR_SCRIPT_FILE>" [--voice Daniel] [--rate 155]
"""

import sys
import os
import re
import subprocess
import argparse
import tempfile
from pathlib import Path

PREFERRED_VOICES = ["Daniel", "Samantha", "Ava", "Eddy (English (US))", "Oliver", "Aman", "Alex"]

def get_available_voices():
    """Queries macOS say binary for installed voices."""
    try:
        res = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True)
        voices = []
        for line in res.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                name = parts[0]
                lang = parts[1]
                voices.append((name, lang))
        return voices
    except Exception:
        return [("Daniel", "en_GB"), ("Samantha", "en_US")]

def pick_best_voice(preferred=None):
    """Picks the requested voice or best available English neural voice."""
    installed = get_available_voices()
    installed_names = [v[0].lower() for v in installed]

    if preferred:
        for name, _ in installed:
            if preferred.lower() in name.lower():
                return name

    for p in PREFERRED_VOICES:
        for name, _ in installed:
            if p.lower() == name.lower():
                return name

    # Fallback to any en_ voice
    for name, lang in installed:
        if lang.startswith("en"):
            return name

    return "Daniel"

def prepare_speech_text(raw_text):
    """
    Cleans teleprompter cues and converts pauses into macOS speech silence commands.
    """
    lines = raw_text.splitlines()
    cleaned_chunks = []

    for line in lines:
        l = line.strip()
        if not l:
            continue

        # Strip structural stage cues like [HOOK - HIGH TENSION], [CTA], [BODY 1]
        if re.match(r'^\[(HOOK|CTA|SECTION|SCENE|BODY|STEP|PART|TIER|OUTRO|INTRO).*?\]$', l, re.IGNORECASE):
            continue

        # Convert pause cues
        l = re.sub(r'\[PAUSE\s*-?\s*(\d*\.?\d*)s?\]', lambda m: f"[[slnc {int(float(m.group(1))*1000)}]]" if m.group(1) else "[[slnc 600]]", l, flags=re.IGNORECASE)
        l = re.sub(r'\[PAUSE\]', "[[slnc 600]]", l, flags=re.IGNORECASE)
        l = re.sub(r'\[BREATHE\]', "[[slnc 450]]", l, flags=re.IGNORECASE)
        l = re.sub(r'\[EMPHASIZE\s*:\s*(.*?)\]', r"\1", l, flags=re.IGNORECASE)

        # Strip any other miscellaneous brackets
        l = re.sub(r'\[.*?\]', '', l).strip()

        if l:
            cleaned_chunks.append(l)

    # Combine into speech text with slight sentence spacing
    speech_text = " [[slnc 300]] ".join(cleaned_chunks)
    return speech_text

def render_voiceover(input_text_or_path, output_path=None, voice=None, rate=155):
    """
    Renders speech to 320 kbps 48kHz MP3 audio track.
    """
    # 1. Resolve text input
    text = ""
    target_dir = None
    if os.path.isdir(input_text_or_path):
        target_dir = input_text_or_path
        # Look for teleprompter_script.txt, transcript.txt, or caption.txt
        for candidate in ["teleprompter_script.txt", "transcript.txt", "caption.txt"]:
            cand_path = os.path.join(target_dir, candidate)
            if os.path.exists(cand_path):
                with open(cand_path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
                print(f"📖 Loaded text from: {candidate}")
                break
        if not output_path:
            output_path = os.path.join(target_dir, "voiceover_guide.mp3")
    elif os.path.isfile(input_text_or_path):
        with open(input_text_or_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        if not output_path:
            output_path = os.path.join(os.path.dirname(input_text_or_path), "voiceover_guide.mp3")
    else:
        # Direct string text passed
        text = input_text_or_path
        if not output_path:
            output_path = "voiceover_guide.mp3"

    if not text.strip():
        print("❌ Error: No text found to synthesize.", file=sys.stderr)
        return None

    selected_voice = pick_best_voice(voice)
    speech_text = prepare_speech_text(text)

    print(f"🎙️ Synthesizing voiceover guide...")
    print(f"   Voice: {selected_voice} | Rate: {rate} WPM")
    print(f"   Destination: {output_path}")

    # Temporary raw audio path
    suffix = ".wav" if sys.platform == "win32" else ".aiff"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_audio:
        tmp_audio_path = tmp_audio.name

    try:
        if sys.platform == "win32":
            # Windows PowerShell Native Speech Synthesis (SAPI5)
            ps_text = speech_text.replace('"', '`"').replace("'", "''")
            ps_clean = re.sub(r'\[\[slnc \d+\]\]', '... ', ps_text)
            ps_cmd = [
                "powershell", "-NoProfile", "-Command",
                f"Add-Type -AssemblyName System.Speech; "
                f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$synth.Rate = 1; "
                f"$synth.SetOutputToWaveFile('{tmp_audio_path}'); "
                f"$synth.Speak(\"{ps_clean}\"); "
                f"$synth.Dispose();"
            ]
            subprocess.run(ps_cmd, check=True)
        else:
            # macOS native say synthesis
            say_cmd = ["say", "-v", selected_voice, "-r", str(rate), "-o", tmp_audio_path, speech_text]
            subprocess.run(say_cmd, check=True)

        # 2. Master to 320 kbps 48kHz MP3 via FFmpeg
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", tmp_audio_path,
            "-ar", "48000",
            "-b:a", "320k",
            output_path
        ]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            size_kb = os.path.getsize(output_path) / 1024
            print(f"✅ Voiceover guide successfully created: {output_path} ({size_kb:.1f} KB)")
            return output_path
        else:
            print("❌ Audio encoding failed.", file=sys.stderr)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during voice synthesis: {e}", file=sys.stderr)
        return None
    finally:
        if os.path.exists(tmp_audio_path):
            os.remove(tmp_audio_path)

def main():
    parser = argparse.ArgumentParser(description="On-Device Neural Voiceover Dubber")
    parser.add_argument("target", help="Project directory, script file path, or text string")
    parser.add_argument("--voice", default=None, help="Voice name (default: auto-picks best neural voice)")
    parser.add_argument("--rate", type=int, default=155, help="Speaking rate in WPM (default: 155)")
    parser.add_argument("--output", default=None, help="Output file path (default: voiceover_guide.mp3 in target dir)")
    args = parser.parse_args()

    render_voiceover(args.target, output_path=args.output, voice=args.voice, rate=args.rate)

if __name__ == "__main__":
    main()
