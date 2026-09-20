# Content Creation AI Workspace Rules & Master Agent Memory (A to Z)

This workspace is a production-grade, multi-platform AI content creation studio designed to analyze, reverse-engineer, and recreate high-performing video content from Instagram, YouTube, TikTok, and Twitter/X.

Every AI agent, pair programmer, automated subagent, or developer working in this workspace MUST adhere to these architectural standards, operational workflows, and file conventions without exception.

---

## 1. Zero Root Clutter Architecture

The root workspace must remain 100% clean. No loose `.md`, `.txt`, `.py`, `.sh`, or media files are ever permitted in the root directory.

### Allowed Root Entities Only:
1. `Instagram/` — Platform content root (`Reels/` and `Posts/`)
2. `YouTube/` — Platform content root (`Shorts/` and `Videos/`)
3. `TikTok/` — Platform content root
4. `Twitter/` — Platform content root
5. `Pipeline_Tools/` — The centralized toolkit (all scripts, binaries, models, docs, rules, setup installers)
6. `.agents/` — Antigravity agent configuration and workspace rules
7. `.gitignore` — Standard git ignore file protecting GitHub file limits

---

## 2. Directory & Link Routing Standards

Every downloaded link is automatically assigned to its dedicated platform category and sanitized folder:

- **Instagram Reels**: `Instagram/Reels/<Creator_Handle> - <Hook_or_Title> (<Shortcode_or_ID>)/`
- **Instagram Posts**: `Instagram/Posts/<Creator_Handle> - <Hook_or_Title> (<Shortcode_or_ID>)/`
- **YouTube Shorts**: `YouTube/Shorts/<Channel_Name> - <Title> (<Video_ID>)/`
- **YouTube Videos**: `YouTube/Videos/<Channel_Name> - <Title> (<Video_ID>)/`
- **TikTok Videos**: `TikTok/<Creator_Handle> - <Title> (<Video_ID>)/`
- **Twitter / X Videos**: `Twitter/<Creator_Handle> - <Title> (<Tweet_ID>)/`

---

## 3. The 20-Asset Production & Repurposing Suite (All Applied in Code)

Every processed link folder contains a complete 20-asset production empire:

| # | Asset Filename | Category | Description |
|---|---|---|---|
| 1 | `video.mp4` | Raw Media | Strict maximum quality uncompressed stream (up to 4K/1080p60). |
| 2 | `video_subtitled.mp4` | Finished Video | Ready-to-post MP4 with native synchronized soft subtitles (`mov_text`). |
| 3 | `teaser_15s.mp4` | Promo Video | 15.00s high-energy story/status preview clip with smooth 0.75s audio fade-out. |
| 4 | `voiceover_guide.mp3` | Master Audio | Studio neural voiceover rehearsal guide (320 kbps 48kHz) with human pause timing. |
| 5 | `cover.jpg` | Visuals | Auto-extracted sharpest high-energy frame via FFmpeg `thumbnail=150` filter. |
| 6 | `audio_lossless.m4a` | Audio Track | Untouched original source bitstream copy. |
| 7 | `audio_studio_320k.mp3` | Audio Track | Studio-grade 320 kbps 48kHz master audio track. |
| 8 | `caption.txt` | Text Metadata | Original creator post caption, hashtags, and mentions. |
| 9 | `metadata.json` | Analytics | Likes, comments, views, uploader ID, duration, upload date. |
| 10 | `transcript.txt` | Speech | Clean spoken text from on-device multilingual Whisper model (`-l auto`). |
| 11 | `transcript.srt` | Subtitles | Millisecond-timestamped subtitle captions file. |
| 12 | `teleprompter_script.txt` | Filming | 3–4 words per line formatted with breathing cues (`[BREATHE]`, `[PAUSE]`). |
| 13 | `storyboard_shotlist.md` | Filming & Editing | B-Roll shot list table + **CapCut Pro Editing Blueprint** (cut points, transitions, SFX). |
| 14 | `timeline_markers.edl` | Video Editing | **CapCut timeline cut markers**, transitions, SFX cues & standard CMX 3600 entries. |
| 15 | `repurposed_content.md` | Omni-Channel | 1-to-5 Suite: Twitter thread, LinkedIn post, 7-slide carousel, newsletter, poll. |
| 16 | `comment_forensics.md` | Audience Intel | Top viewer questions, objections, skepticism, and memes (Goldmine for Part 2). |
| 17 | `seo_metadata.md` | Algorithm SEO | 3 Title A/B tests (Curiosity, Search, Contrarian) + tiered hashtags. |
| 18 | `funnel_blueprint.md` | Conversion | Automated ManyChat DM lead magnet copy to turn comments into email leads. |
| 19 | `deep_analysis.md` | Strategy & AI Video | Pacing, hook score, and **Google Flow & Higsfield AI video generation prompt recipes**. |
| 20 | `generated_scripts.md` | Scriptwriting | 5 hook archetypes + full reenactment script + 30-day spinoff calendar. |

---

## 4. Production Stack & Tooling Standards

Every agent and tool in this workspace must adhere to the user's defined production stack:

### A. Primary Video Editing Application: **CapCut** (Desktop & Mobile)
- **Primary Workflow**: All cut points, transitions, and timeline markers are optimized for CapCut.
- **Timeline Shortcuts**: Split Clip (`Cmd+B` on macOS / `Ctrl+B` on Windows) | Add Marker (`M`).
- **Transitions**: Native CapCut transitions (*Camera Shake*, *Optic Zoom*, *Pull In*, *Flash White*, *Glitch*).
- **Auto-Captions**: CapCut Auto Captions formatted in *Bold Pop Yellow* (`#FFE600`) with soft dark glow and *Spring* or *Bounce In* animations.
- **Speed Ramping**: CapCut *Hero Curve* (1.5x fast entry $\rightarrow$ 0.6x slow-mo on key action $\rightarrow$ 1.0x normal dialogue).
- **Audio Mix**: Track 1 Dialogue (0 dB + voice enhancement), Track 2 SFX (-6 dB), Track 3 Music (-18 dB with auto-ducking).

### B. Primary AI Video Generation: **Google Flow** & **Higsfield AI**
- **Google Flow (Primary AI Video Model)**:
  - Used for photorealistic cinematography, dynamic camera movement, and atmospheric studio lighting.
  - Prompts must include camera motion tags (`[Camera: Slow Push-in]`, `[Camera: Orbit]`), 9:16 vertical ratio, 60fps, photorealistic reflections.
- **Higsfield AI (Secondary Motion / Character Dynamic Model)**:
  - Used when high-energy motion, realistic hand physics, zero finger deformation, or complex character gestures are required.
  - Prompts must include motion intensity parameters (`[Motion: Medium-High (0.70)]`, `[Physics: Zero morphing]`, `[Camera: Handheld dynamic tracking]`).
- **CapCut B-Roll Integration**: Generated MP4 clips are dragged into CapCut Overlay Track 2 at the cut markers specified in `timeline_markers.edl`.

---

## 5. Centralized Toolkit Reference (`Pipeline_Tools/`)

All code, models, and dependencies reside strictly inside `Pipeline_Tools/`:

### Core Execution Engines:
- **`studio_ui.py`**:
  - Local dark-mode Creator Studio Web Dashboard (`http://localhost:8080`).
  - Zero external dependencies (Python standard library HTTP server + REST API).
  - Video stream switcher (Raw, Subtitled, 15s Teaser) with HTTP 206 Partial Content range scrubbing.
  - Interactive teleprompter with auto-scroll speed controls (px/s), font resizing, and spacebar toggle.
  - In-dashboard neural voiceover player & synthesis trigger (`/api/dub`).
  - 1-click clipboard copy for Twitter threads, LinkedIn posts, carousels, and newsletters.
  - Interactive live Hook Scorer (`/api/score`).
  - Live pipeline runner with Server-Sent Events terminal log streaming (`/api/stream_logs`).
- **`media_pipeline.py`**:
  - Main automated pipeline engine. Accepts single URLs, multiple URLs, or `--batch links.txt`.
  - Downloads max-quality video + dual audio streams.
  - Runs local Whisper speech transcription with auto-language detection.
  - Runs native Apple Vision OCR for silent/music reels (on macOS).
  - Generates the full 20-asset production suite in one command.
- **`hook_scorer.py`**:
  - Pre-filming AI retention scorer (1–100 & S/A/B/C/F grade).
  - Evaluates 5 retention vectors: 0–3s tension (25 pts), brevity <12 words (20 pts), physical action cues (20 pts), curiosity gap (20 pts), emotional stakes (15 pts).
  - Deducts -20 pts per fluff phrase (`"hey guys"`, `"in this video"`).
  - Generates 3 AI high-voltage rewrite variants.
  - Supports CLI, JSON output (`--json`), and Python module import.
- **`teaser_clipper.py`**:
  - Extracts 15.00s high-energy story/status preview clip from `video.mp4`.
  - Applies subtle 0.75s audio fade-out (`afade=t=out:st=14.25:d=0.75`).
- **`vocal_dubber.py`**:
  - Cross-platform on-device neural voiceover generator.
  - On macOS: uses native `say` with neural voices (`Daniel`, `Samantha`, etc.).
  - On Windows: uses built-in PowerShell `System.Speech.Synthesis.SpeechSynthesizer` (SAPI5).
  - Encodes studio-grade 320 kbps 48kHz MP3 (`voiceover_guide.mp3`).
- **`burn_captions.py`**:
  - Embeds native soft subtitles into MP4 container via `mov_text` with 0 re-encoding loss.
- **`creator_playbook.py`**:
  - Scans analyzed library and outputs a consolidated 30-day posting matrix.
- **`search_content.py`**:
  - Instant full-text search across all captions, transcripts, and analysis files.
- **`ocr_helper`**:
  - Native compiled Swift binary using Apple Vision (`VNRecognizeTextRequest`) on macOS.

---

## 6. Cross-Platform GitHub Distribution & Dependency Rules (`Setup_Dependencies/`)

When deploying, cloning, or distributing this repository via GitHub:

### GitHub 100MB File Limit Protection:
- The Whisper AI models (`ggml-base.bin`, `ggml-base.en.bin`) are **141 MB each**, which exceeds GitHub's 100MB file limit.
- [`.gitignore`](.gitignore) strictly ignores `Pipeline_Tools/models/*.bin` and large video binaries (`*.mp4`, `*.m4a`).
- Model weights are downloaded automatically on the user's machine on first run via `download_models.py`.
- Empty platform directories contain `.gitkeep` files so the full folder structure is preserved when cloned.

### 1-Click Setup Scripts:
- **macOS (Apple Silicon & Intel)**:
  ```bash
  bash Pipeline_Tools/Setup_Dependencies/setup_mac.sh
  ```
  *(Installs Homebrew packages `ffmpeg`, `yt-dlp`, `whisper-cpp` + downloads models).*
- **Windows (10 / 11)**:
  ```cmd
  Pipeline_Tools\Setup_Dependencies\setup_windows.bat
  ```
  *(Checks Python, installs pip requirements, installs `ffmpeg` via winget, downloads models).*
- **Diagnostic Environment Scanner**:
  ```bash
  python3 Pipeline_Tools/Setup_Dependencies/check_environment.py
  ```

---

## 7. Execution Command Reference

```bash
# 1. Launch Local Creator Studio Web Dashboard:
python3 Pipeline_Tools/studio_ui.py [--port 8080]

# 2. Process Any Media Link (Single or Batch):
python3 Pipeline_Tools/media_pipeline.py "<URL>"
python3 Pipeline_Tools/media_pipeline.py --batch links.txt

# 3. Pre-Filming Hook Retention Scorer:
python3 Pipeline_Tools/hook_scorer.py --hook "Your hook text here" [--json]

# 4. Generate 15s Story Teaser Clip:
python3 Pipeline_Tools/teaser_clipper.py "<PROJECT_FOLDER_OR_VIDEO_PATH>"

# 5. Synthesize Neural Voiceover Guide Track:
python3 Pipeline_Tools/vocal_dubber.py "<PROJECT_FOLDER_OR_SCRIPT_PATH>" [--rate 155]

# 6. Embed Subtitles into MP4:
python3 Pipeline_Tools/burn_captions.py "<FOLDER_PATH>"

# 7. Reverse-Engineer 30-Day Matrix:
python3 Pipeline_Tools/creator_playbook.py

# 8. Search Content Library:
python3 Pipeline_Tools/search_content.py "<KEYWORD>"

# 9. Diagnostic Environment Scan:
python3 Pipeline_Tools/Setup_Dependencies/check_environment.py

# 10. Download AI Models:
python3 Pipeline_Tools/Setup_Dependencies/download_models.py
```

---

## 8. Operational Commitments for AI Agents

1. **Zero Root Clutter**: Never create loose `.md`, `.txt`, `.py`, or `.sh` files in the workspace root.
2. **Standardized Folders**: Always route downloaded links to their dedicated `<Creator> - <Title> (<ID>)` folder inside the appropriate platform directory.
3. **Primary Editor (CapCut)**: Always generate timeline markers, cut points, transition cues, and editing shot lists tailored natively for CapCut (Desktop & Mobile).
4. **Primary AI Video (Google Flow & Higsfield AI)**: Always provide production-ready prompt recipes for Google Flow (primary cinematography) and Higsfield AI (dynamic motion/gestures).
5. **No Placeholders**: Every file generated must contain real, extracted, or calculated production data.
6. **Cross-Platform Compatibility**: Always write code that checks `sys.platform` and runs seamlessly on both macOS and Windows.
7. **Preserve Audio Quality**: Always generate dual audio tracks (`.m4a` lossless stream copy + 320 kbps 48kHz studio MP3).
