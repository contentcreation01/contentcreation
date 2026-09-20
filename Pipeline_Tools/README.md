# Multi-Platform Content Pipeline & Production Suite

All utilities, local AI speech models, OCR engines, creator playbook generators, subtitle embedders, and automated pipelines are centralized inside `Pipeline_Tools`.

---

## Directory Architecture

```
Content Creation Using Ai/
│
├── Instagram/                         # Instagram Reels & Posts
│   └── Reels/
│       └── <Creator> - <Title> (<ID>)/
│           ├── video.mp4              # Strict max quality raw stream (1080p/4K @ 60fps)
│           ├── video_subtitled.mp4    # MP4 with native synchronized soft subtitles
│           ├── teaser_15s.mp4         # 15-second high-energy story preview with audio fade
│           ├── voiceover_guide.mp3    # Neural voiceover rehearsal & guide track (320 kbps)
│           ├── cover.jpg              # Auto-extracted sharpest high-energy frame
│           ├── audio_lossless.m4a     # Lossless direct bitstream copy
│           ├── audio_studio_320k.mp3  # Studio-grade 320 kbps 48kHz MP3
│           ├── caption.txt            # Original post caption & hashtags
│           ├── metadata.json          # Likes, comments, views, uploader ID, date
│           ├── transcript.txt         # Transcribed spoken text
│           ├── transcript.srt         # Timed subtitle captions file
│           ├── teleprompter_script.txt# Teleprompter format (3-4 words/line + pauses)
│           ├── storyboard_shotlist.md # Visual B-roll table & lighting guide
│           ├── timeline_markers.edl   # Timeline markers for Premiere/DaVinci/CapCut
│           ├── repurposed_content.md  # 1-to-5 Suite (Twitter, LinkedIn, Carousel, Newsletter)
│           ├── comment_forensics.md   # Part 2 goldmine (Questions, Objections, Memes)
│           ├── seo_metadata.md        # 3 Title A/B tests & tiered hashtags
│           ├── funnel_blueprint.md    # ManyChat lead capture & DM conversion copy
│           ├── deep_analysis.md       # Hook score, pacing, psychology & AI thumbnail prompts
│           └── generated_scripts.md   # 5 hook archetypes + 30-day calendar
│
├── YouTube/                           # YouTube Shorts & Videos
├── TikTok/                            # TikTok Videos
├── Twitter/                           # Twitter / X Videos
│
└── Pipeline_Tools/                    # Centralized toolkit
    ├── Setup_Dependencies/            # Cross-platform GitHub installers & model downloaders
    │   ├── setup_mac.sh               # 1-click macOS Homebrew + model installer
    │   ├── setup_windows.bat          # 1-click Windows winget + model installer
    │   ├── download_models.py         # Automated Whisper model weight downloader
    │   ├── check_environment.py       # Cross-platform diagnostic scanner
    │   ├── requirements.txt           # Python dependency specification
    │   └── GITHUB_SETUP_GUIDE.md      # Onboarding guide for GitHub users
    ├── studio_ui.py                   # Local Dark-Mode Creator Studio Web Dashboard (localhost:8080)
    ├── vocal_dubber.py                # On-Device Neural Voiceover Dubber (macOS & Windows)
    ├── hook_scorer.py                 # Pre-Filming AI Hook & Script Scorer (1–100 & S/A/B/C/F)
    ├── teaser_clipper.py              # 15-second teaser & story preview clipper
    ├── media_pipeline.py              # Main automated production & repurposing engine
    ├── insta_pipeline.py              # Compatibility wrapper
    ├── creator_playbook.py            # Reverse-engineers creators into 30-day calendars
    ├── burn_captions.py               # 1-click subtitle embedder
    ├── search_content.py              # 1-command library search engine
    ├── ocr_helper                     # Apple Vision native on-screen text OCR binary (macOS)
    ├── README.md                      # Complete system guide
    ├── AGENTS.md                      # Multi-agent memory
    ├── GEMINI.md                      # Instructions reference
    └── models/
        ├── ggml-base.bin              # Multilingual Whisper speech model (-l auto)
        └── ggml-base.en.bin           # English Whisper model
```

---

## ⚡ GitHub Quickstart (Mac & Windows)

Anyone cloning this repository can get completely set up in under 60 seconds:

### On macOS (Apple Silicon & Intel):
```bash
bash Pipeline_Tools/Setup_Dependencies/setup_mac.sh
```

### On Windows (10 / 11):
```cmd
Pipeline_Tools\Setup_Dependencies\setup_windows.bat
```

### Diagnostic Check:
```bash
python3 Pipeline_Tools/Setup_Dependencies/check_environment.py
```

---

## The 20-Asset Production Suite (Per Link)

Every single downloaded link is automatically transformed into an entire content production empire:

| Category | Asset | Description |
|---|---|---|
| **Media** | `video.mp4` | Strict max quality uncompressed stream (1080p/4K @ 60fps) |
| **Media** | `video_subtitled.mp4` | Ready-to-post MP4 with native synchronized soft subtitles |
| **Media** | `teaser_15s.mp4` | 15-second high-energy story preview with 0.75s audio fade |
| **Voiceover** | `voiceover_guide.mp3` | Master neural voiceover guide track with human pause timing |
| **Media** | `cover.jpg` | Auto-extracted sharpest high-energy frame for thumbnail cover |
| **Audio** | `audio_lossless.m4a` | Lossless source bitstream copy |
| **Audio** | `audio_studio_320k.mp3` | Studio-grade 320 kbps 48kHz master audio |
| **Text** | `caption.txt` | Complete post copy & hashtags |
| **Text** | `metadata.json` | Full platform metrics, likes, comments, views, upload date |
| **Speech** | `transcript.txt` | Clean spoken text from multilingual Whisper |
| **Speech** | `transcript.srt` | Timed subtitle captions file |
| **Filming** | `teleprompter_script.txt` | 3–4 words per line with breathing & pause markers |
| **Filming & Editing** | `storyboard_shotlist.md` | B-Roll shot list table + **CapCut Pro Editing Blueprint** (cut points, transitions, SFX) |
| **Editing** | `timeline_markers.edl` | **CapCut timeline cut markers**, transitions, SFX cues & CMX 3600 entries |
| **Omni-Channel** | `repurposed_content.md` | Twitter thread (7 tweets), LinkedIn post, 7-slide carousel, newsletter, poll |
| **Audience** | `comment_forensics.md` | Top viewer questions & objections (Goldmine for Part 2) |
| **Algorithm** | `seo_metadata.md` | 3 Title A/B tests (Curiosity, SEO, Contrarian) + hashtag tiers |
| **Growth** | `funnel_blueprint.md` | Automated ManyChat DM copy to turn comments into leads |
| **Strategy & AI Video** | `deep_analysis.md` | Hook score (1-100), pacing metrics, sound design, **Google Flow & Higsfield AI video prompts** |
| **Scripts** | `generated_scripts.md` | 5 hook archetypes + full script + 30-day spinoff calendar |

---

## 🎬 Production Stack & Tooling

- **Primary Video Editor**: **CapCut** (Desktop & Mobile)
  - Full timeline cut markers and transitions (*Camera Shake*, *Optic Zoom*, *Pull In*, *Glitch*, *Flash White*).
  - CapCut Auto-Caption preset styling: *Bold Pop Yellow* (`#FFE600`) with soft dark glow and *Spring* or *Bounce In* animations.
  - CapCut Speed Ramping: *Hero Curve* (1.5x fast entry $\rightarrow$ 0.6x slow-mo on key action $\rightarrow$ 1.0x normal dialogue).
  - CapCut Timeline Shortcuts: Split Clip (`Cmd+B` / `Ctrl+B`) and Add Marker (`M`).
- **Primary AI Video Generation**:
  - **Google Flow (Primary)**: Generates 9:16 vertical 4K/60fps photorealistic cinematic video B-roll with camera motion tags (`[Camera: Slow Push-in]`, `[Camera: Orbit]`).
  - **Higsfield AI (Secondary / Dynamic Motion)**: Generates dynamic character hand physics, zero finger deformation, and fluid camera tilt motions (`Motion Intensity: 0.70`).


---

## Execution Commands

### 1. Launch Local Creator Studio Dashboard (Interactive Visual UI):
```bash
python3 Pipeline_Tools/studio_ui.py [--port 8080]
```
*Opens `http://localhost:8080` in your browser. Features live video/audio players, auto-scrolling teleprompter with speed controls, in-app neural voiceover generator, 1-click clipboard copy for Twitter/LinkedIn posts, interactive hook scoring, and new URL pipeline runner with live log streaming.*

### 2. On-Device Neural Voiceover Dubber:
```bash
# Render voiceover for project directory:
python3 Pipeline_Tools/vocal_dubber.py "<PROJECT_FOLDER_OR_SCRIPT_PATH>" [--voice Daniel] [--rate 155]

# Render voiceover from direct text:
python3 Pipeline_Tools/vocal_dubber.py "Stop doing this. I turned three phones into an AI drone army." --output voice.mp3
```

### 3. Pre-Filming AI Hook & Script Scorer:
```bash
# Evaluate a hook string:
python3 Pipeline_Tools/hook_scorer.py --hook "I turned three old phones into an autonomous AI drone army."

# Evaluate a full script file:
python3 Pipeline_Tools/hook_scorer.py --file "path/to/script.txt"

# JSON output mode:
python3 Pipeline_Tools/hook_scorer.py --hook "Stop doing this." --json
```

### 4. Generate 15-Second Teaser Clip:
```bash
python3 Pipeline_Tools/teaser_clipper.py "<PROJECT_FOLDER_OR_VIDEO_PATH>" [--duration 15.0] [--fade 0.75]
```

### 5. Process Any Media Link:
```bash
python3 Pipeline_Tools/media_pipeline.py "<URL>"
```

### 6. Process Multiple Links or Batch File:
```bash
python3 Pipeline_Tools/media_pipeline.py "<URL_1>" "<URL_2>"
python3 Pipeline_Tools/media_pipeline.py --batch links.txt
```

### 7. Embed Subtitles:
```bash
python3 Pipeline_Tools/burn_captions.py "<FOLDER_PATH>"
```

### 8. Generate Creator Playbook & 30-Day Matrix:
```bash
python3 Pipeline_Tools/creator_playbook.py
```

### 9. Search Entire Library:
```bash
python3 Pipeline_Tools/search_content.py "<KEYWORD>"
```

### 10. Run Diagnostic Environment Scan:
```bash
python3 Pipeline_Tools/Setup_Dependencies/check_environment.py
```
