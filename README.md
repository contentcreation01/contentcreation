# 🎬 AI Content Creation Studio & Strategy War Room

> **A production-grade, multi-platform AI content creation pipeline with a built-in viral strategy intelligence engine.**

Turn any Instagram Reel, YouTube Short, TikTok, or Twitter/X video into a **20-asset content production empire** — locally, privately, and without subscriptions.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%2010%2F11-lightgrey)](https://github.com)
[![Zero External Python Deps](https://img.shields.io/badge/Zero%20External%20Python%20Deps-green)](#)

---

## ⚡ 60-Second Setup

### macOS (Apple Silicon M1/M2/M3/M4 & Intel):
```bash
git clone https://github.com/YOUR_USERNAME/content-creation-ai.git
cd content-creation-ai
bash Pipeline_Tools/Setup_Dependencies/setup_mac.sh
```

### Windows 10 / 11:
```cmd
git clone https://github.com/YOUR_USERNAME/content-creation-ai.git
cd content-creation-ai
Pipeline_Tools\Setup_Dependencies\setup_windows.bat
```

### Launch the Studio Dashboard:
```bash
python3 Pipeline_Tools/studio_ui.py
```
Open **http://localhost:8080** in your browser.

---

## 🧠 What This Tool Does

### Mode A — Single Video Deep Analysis
Paste any video URL and get a full **20-asset production empire**:

| Asset | Description |
|---|---|
| `video.mp4` | Max-quality raw stream (1080p/4K @ 60fps) |
| `video_subtitled.mp4` | Ready-to-post with synchronized soft subtitles |
| `teaser_15s.mp4` | 15-second story preview with audio fade |
| `audio_studio_320k.mp3` | Studio-grade 320 kbps 48kHz master audio |
| `transcript.txt` + `.srt` | Multilingual Whisper speech-to-text |
| `teleprompter_script.txt` | 3-4 words/line with BREATHE / PAUSE cues |
| `storyboard_shotlist.md` | CapCut-native B-Roll table + editing blueprint |
| `timeline_markers.edl` | Cut markers, SFX cues, transitions for CapCut |
| `deep_analysis.md` | Hook score (1-100) + Google Flow & Higsfield AI prompts |
| `generated_scripts.md` | 5 hook archetypes + 30-day spinoff calendar |
| `comment_forensics.md` | Viral comment goldmine for Part 2 ideas |
| `seo_metadata.md` | 3 title A/B tests + tiered hashtags |
| `funnel_blueprint.md` | ManyChat DM automation copy |
| `repurposed_content.md` | Twitter thread, LinkedIn, carousel, newsletter |

---

### Mode B — Strategy Crack War Room
Paste **2-6 video links** (e.g., original creator + viral copier) + describe your goal in plain text.

The AI synthesizes a **forensic breakdown** of exactly why one went viral and delivers:
- A ready-to-film teleprompter script in **4 languages**: English, Tanglish, Mixed Tamil-English, Native Tamil
- CapCut EDL timeline markers
- Google Flow & Higsfield AI video prompts
- Caption + ManyChat funnel copy
- 3 viral hook rewrites with CapCut SFX cues
- Everything auto-saved to `Instagram/Reels/Strategy_Cracks/` in a timestamped folder

**Example use case**: Chandler re-created Luke's AI agent video. Cindy re-created Chandler's and hit a 53% comment-to-like ratio. This tool cracks the exact formula so you can do the same with your own setup.

---

## 🗂️ Directory Architecture

```
Content Creation Using Ai/
│
├── Instagram/
│   └── Reels/
│       ├── Strategy_Cracks/           # War Room session outputs (timestamped)
│       └── <Creator> - <Title> (<ID>)/
│
├── YouTube/
├── TikTok/
├── Twitter/
│
└── Pipeline_Tools/
    ├── Setup_Dependencies/
    │   ├── setup_mac.sh
    │   ├── setup_windows.bat
    │   ├── requirements.txt
    │   ├── download_models.py
    │   ├── check_environment.py
    │   └── GITHUB_SETUP_GUIDE.md
    ├── studio_ui.py                   # Local Studio Dashboard (localhost:8080)
    ├── media_pipeline.py              # Main production engine
    ├── hook_scorer.py                 # AI viral hook scorer (1-100)
    ├── vocal_dubber.py                # On-device neural voiceover
    ├── teaser_clipper.py              # 15-second teaser clipper
    ├── burn_captions.py               # Subtitle embedder
    ├── creator_playbook.py            # 30-day content matrix generator
    ├── search_content.py              # Full-text library search
    └── models/                        # AI model weights (auto-downloaded)
```

---

## 🛠️ System Requirements

| Dependency | macOS | Windows |
|---|---|---|
| **Python 3.10+** | `brew install python` | python.org/downloads |
| **FFmpeg** | `brew install ffmpeg` | `winget install Gyan.FFmpeg` |
| **yt-dlp** | `brew install yt-dlp` | `pip install yt-dlp` |
| **Whisper CLI** | `brew install whisper-cpp` | whisper.cpp/releases |

> AI model weights (~141 MB each) are excluded from Git. Run `python3 Pipeline_Tools/Setup_Dependencies/download_models.py` to auto-download them.

---

## 🌐 Multi-Language Script Output

Scripts are generated in 4 languages, switchable without re-running:

| Language | Code | Use Case |
|---|---|---|
| English | `english` | Global audience |
| Tanglish | `tanglish` | Tamil-speaking diaspora |
| Mixed Tamil-English | `mixed` | Bilingual Indian audience |
| Native Tamil | `tamil` | Tamil-only audience |

---

## 📋 Commands

```bash
# Launch Studio Dashboard:
python3 Pipeline_Tools/studio_ui.py [--port 8080]

# Process any media URL:
python3 Pipeline_Tools/media_pipeline.py "<URL>"

# Batch process:
python3 Pipeline_Tools/media_pipeline.py --batch links.txt

# Score a hook before filming:
python3 Pipeline_Tools/hook_scorer.py --hook "Your hook text here"

# Generate voiceover:
python3 Pipeline_Tools/vocal_dubber.py "<PROJECT_FOLDER>"

# Verify environment:
python3 Pipeline_Tools/Setup_Dependencies/check_environment.py
```

---

## 🔒 Privacy

All processing is **100% local** on your machine. No data is sent to external servers. No subscriptions required.

---

## 🏭 Production Stack

- **Primary Editor**: CapCut Desktop & Mobile (timeline markers in CMX 3600 EDL format)
- **AI Video**: Google Flow (cinematic B-roll) + Higsfield AI (dynamic motion)
- **Speech AI**: whisper.cpp with `ggml-base.bin` multilingual model (on-device)
- **Voiceover**: macOS `say` (neural voices) / Windows PowerShell System.Speech
