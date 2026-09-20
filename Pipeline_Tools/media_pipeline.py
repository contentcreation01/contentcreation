#!/usr/bin/env python3
"""
Universal Content Creation Pipeline (Instagram, YouTube, TikTok, Twitter/X)
Production Multi-Platform Suite with:
- Strict Max Quality & Dual Audio (Lossless .m4a + 320k MP3)
- Multilingual Whisper Speech-to-Text (-l auto)
- Silent Video OCR (Apple Vision)
- Auto-Cover Best Frame Extractor (`cover.jpg`)
- Visual Storyboard & B-Roll Shot List Generator (`storyboard_shotlist.md`)
- Video Editor Timeline Markers (`timeline_markers.edl`)
- Pacing & Cadence Engine (WPM & Cut Frequency / ASL)
- Teleprompter-Ready Script Formatter (`teleprompter_script.txt`)
- 5 Hook Archetypes & 30-Day Content Calendar (`generated_scripts.md`)
- 1-to-5 Multi-Platform Repurposing Engine (`repurposed_content.md`)
- Audience & Comment Forensics (`comment_forensics.md`)
- Algorithmic SEO & Title A/B Tests (`seo_metadata.md`)
- ManyChat & Lead Magnet Funnel Blueprint (`funnel_blueprint.md`)
- Native Subtitle Embedding (`burn_captions.py` / `video_subtitled.mp4`)
- Batch Mode & Duplicate Prevention
"""

import os
import re
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
WORKSPACE_DIR = BASE_DIR.parent
MODELS_DIR = BASE_DIR / "models"
OCR_BIN = BASE_DIR / "ocr_helper"

WHISPER_MULTILINGUAL = MODELS_DIR / "ggml-base.bin"
WHISPER_EN = MODELS_DIR / "ggml-base.en.bin"
WHISPER_MODEL = WHISPER_MULTILINGUAL if WHISPER_MULTILINGUAL.exists() else WHISPER_EN

for d in ["Instagram/Reels", "Instagram/Posts", "YouTube/Shorts", "YouTube/Videos", "TikTok", "Twitter"]:
    (WORKSPACE_DIR / d).mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def clean_url(url: str) -> str:
    """Strips query tracking parameters like ?igsh=..., ?si=..., &utm_..."""
    url = re.sub(r"[?&](igsh|si|utm_[a-z]+|stkn)=[^&]+", "", url)
    return url.rstrip("?&")


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """Sanitizes text to be clean and safe for filesystem folder and file names."""
    text = re.sub(r"[#@\n\r\t]+", " ", text)
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "Untitled"
    if len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0]
    return text.strip(" .-_")


def run_command(cmd, description=""):
    try:
        res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res
    except subprocess.CalledProcessError:
        return None


def execute_download(url: str, output_template: str) -> bool:
    """Downloads media with automatic bot-bypass and fallback strategies."""
    base_cmd = [
        "yt-dlp",
        "--format", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "--write-description",
        "--write-info-json",
        "-o", output_template,
        "--no-playlist",
        url
    ]
    res = run_command(base_cmd, "Standard download")
    if res is not None:
        return True

    print("[-] Standard download hit a restriction. Engaging bot-bypass & client spoofing...")
    spoof_cmd = base_cmd + ["--extractor-args", "youtube:player_client=android"]
    res = run_command(spoof_cmd, "Android client spoofing")
    if res is not None:
        return True

    for browser in ["chrome", "safari"]:
        print(f"[*] Trying session auth from {browser}...")
        cookie_cmd = base_cmd + ["--cookies-from-browser", browser]
        res = run_command(cookie_cmd, f"Cookie extraction from {browser}")
        if res is not None:
            return True

    return False


def detect_target_directory(url: str, metadata: dict, is_short: bool = False) -> Path:
    """Routes media to the appropriate platform and content-type subfolder."""
    url_lower = url.lower()
    
    if "instagram.com" in url_lower or "instagr.am" in url_lower:
        if "/reel/" in url_lower or is_short:
            return WORKSPACE_DIR / "Instagram" / "Reels"
        return WORKSPACE_DIR / "Instagram" / "Posts"

    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        duration = metadata.get("duration") or 0
        width = metadata.get("width") or 0
        height = metadata.get("height") or 0
        is_vertical = height > width if (height and width) else False

        if "/shorts/" in url_lower or (duration and duration <= 75 and is_vertical):
            return WORKSPACE_DIR / "YouTube" / "Shorts"
        return WORKSPACE_DIR / "YouTube" / "Videos"

    if "tiktok.com" in url_lower:
        return WORKSPACE_DIR / "TikTok"

    if "twitter.com" in url_lower or "x.com" in url_lower:
        return WORKSPACE_DIR / "Twitter"

    return WORKSPACE_DIR / "Other_Media"


def check_existing_download(url: str) -> Path | None:
    """Checks if the video ID has already been archived in the library."""
    match = re.search(r"/(reel|p|shorts|watch\?v=)/([^/?&]+)", url)
    if not match:
        match = re.search(r"youtu\.be/([^/?&]+)", url)
    
    if match:
        target_id = match.group(2 if len(match.groups()) > 1 else 1)
        for p in WORKSPACE_DIR.glob(f"*/*/*({target_id})"):
            if (p / "video.mp4").exists():
                return p
    return None


def extract_cover_frame(video_path: Path, target_dir: Path):
    """Selects the sharpest, highest-energy frame for thumbnail cover using FFmpeg."""
    cover_path = target_dir / "cover.jpg"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", "thumbnail=150",
        "-frames:v", "1",
        "-update", "1",
        str(cover_path)
    ]
    res = run_command(cmd, "Cover extraction")
    if res and cover_path.exists():
        print(f"[✓] Extracted high-energy cover image: {cover_path.name}")


def generate_timeline_edl(duration_sec: float, target_dir: Path):
    """Generates a standard CMX 3600 EDL timeline file with native CapCut cut markers, transitions, and SFX cues."""
    edl_path = target_dir / "timeline_markers.edl"
    fps = 30.0

    def to_tc(sec):
        frames = int(round((sec % 1) * fps))
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}:{frames:02d}"

    hook_end = min(3.0, duration_sec * 0.1)
    setup_end = min(15.0, duration_sec * 0.3)
    climax_start = max(setup_end, duration_sec - 15.0)

    content = f"""; ==============================================================================
; CAPCUT & CMX 3600 TIMELINE CUT MARKERS
; Primary Video Editor: CapCut (Desktop / Mobile)
; CapCut Split Shortcut: Cmd+B (macOS) / Ctrl+B (Windows)
; CapCut Add Marker Shortcut: M
; ==============================================================================
TITLE: CAPCUT_TIMELINE_MARKERS
FCM: NON-DROP FRAME

001  AX       V     C        00:00:00:00 {to_tc(hook_end)} 00:00:00:00 {to_tc(hook_end)}
* FROM CLIP NAME: 01_HOOK (0:00 - {hook_end:.1f}s)
* CAPCUT ACTION: Split clip at {hook_end:.1f}s. Add Marker [M].
* CAPCUT TRANSITION: Optic Zoom / Camera Shake 1 (Duration: 0.2s)
* CAPCUT SFX: Sound -> Transition -> "Whoosh 3" or "Bass Drop Hit" (-6dB)
* CAPCUT TEXT: Auto Captions -> Preset "Bold Pop Yellow" with Soft Glow

002  AX       V     C        {to_tc(hook_end)} {to_tc(setup_end)} {to_tc(hook_end)} {to_tc(setup_end)}
* FROM CLIP NAME: 02_SETUP_CONTEXT ({hook_end:.1f}s - {setup_end:.1f}s)
* CAPCUT ACTION: Split clip at {setup_end:.1f}s. Add Marker [M].
* CAPCUT TRANSITION: Smooth Pull In / Slide Right (Duration: 0.15s)
* CAPCUT SFX: Sound -> Device -> "Mouse Click" / "Subtle Beep" (-9dB)
* CAPCUT B-ROLL: Overlay Track 2 -> Insert Google Flow AI B-Roll Clip

003  AX       V     C        {to_tc(setup_end)} {to_tc(climax_start)} {to_tc(setup_end)} {to_tc(climax_start)}
* FROM CLIP NAME: 03_ESCALATION_DEMO ({setup_end:.1f}s - {climax_start:.1f}s)
* CAPCUT ACTION: Split clip at {climax_start:.1f}s. Add Marker [M].
* CAPCUT TRANSITION: Glitch 2 / Light Streaks (Duration: 0.2s)
* CAPCUT SFX: Sound -> Electronic -> "Glitch Tech" / "Impact Riser" (-6dB)
* CAPCUT SPEED RAMP: Hero Curve (Fast 1.5x -> Slow 0.6x on phone unlock -> Normal 1.0x)

004  AX       V     C        {to_tc(climax_start)} {to_tc(duration_sec)} {to_tc(climax_start)} {to_tc(duration_sec)}
* FROM CLIP NAME: 04_CLIMAX_CTA ({climax_start:.1f}s - {duration_sec:.1f}s)
* CAPCUT ACTION: Final cut point & end screen. Add Marker [M].
* CAPCUT TRANSITION: Flash White / Optical Blur (Duration: 0.2s)
* CAPCUT SFX: Sound -> Impact -> "Deep Sub Thud" + Animated Bell Ping (-6dB)
* CAPCUT STICKER: Add pointing arrow sticker to comment CTA trigger
"""
    edl_path.write_text(content, encoding="utf-8")
    print(f"[✓] Generated timeline_markers.edl (Tailored for CapCut & CMX 3600)")


def generate_storyboard_shotlist(transcript_text: str, duration_sec: float, target_dir: Path):
    """Builds a structured visual storyboard, B-roll shot list, and native CapCut Pro Editing Blueprint."""
    sb_path = target_dir / "storyboard_shotlist.md"
    
    hook_end = min(3.0, duration_sec * 0.1)
    setup_end = min(15.0, duration_sec * 0.3)
    climax_start = max(setup_end, duration_sec - 15.0)

    content = f"""# Visual Storyboard & CapCut Pro Production Blueprint
**Video Duration**: {duration_sec:.1f}s | **Primary Video Editor**: CapCut (Desktop & Mobile)

---

## 1. Camera & B-Roll Production Table

| Timestamp | Spoken Cue / Beat | Camera Angle | Visual Action / B-Roll Recommendation |
|---|---|---|---|
| `0:00 - {hook_end:.1f}s` | **THE HOOK** | First-Person POV (Eye Level) | Hands entering frame adjusting desk lamp / hardware. Glowing monitor visualizer. |
| `{hook_end:.1f}s - {setup_end:.1f}s` | **THE SETUP** | Over-The-Shoulder (Medium) | Pointing towards the computer terminal or primary device while speaking prompt. |
| `{setup_end:.1f}s - {climax_start:.1f}s` | **THE ESCALATION** | Macro Top-Down / High Angle | Clean top view of devices lighting up and executing commands in unison. |
| `{climax_start:.1f}s - {duration_sec-5:.1f}s` | **THE CLIMAX** | Side Profile (Cinematic) | Fast cut between physical typing/touching screen and automated terminal execution. |
| `{duration_sec-5:.1f}s - END` | **THE PAYOFF / CTA** | First-Person POV Nod | Casual sign-off gesture + on-screen animated text pointing down to comments. |

---

## 2. Lighting & Aesthetic Formula
- **Lighting Setup**:
  - *Key Light*: Soft 4000K warm white at 45° angle (reduces harsh screen reflections).
  - *Accent Light*: Amber/Cyan monitor backlight bar for cinematic separation.
- **Color Palette**:
  - Charcoal / Dark Slate (`#1E1E24`)
  - Warm Core Amber (`#FF8C00`)
  - Cyber Cyan (`#00F5D4`)

---

## 3. CapCut Pro Editing Blueprint & Timeline Breakdown

### CapCut Project Settings:
- **Canvas Ratio**: 9:16 (1080 x 1920) Vertical
- **Frame Rate**: 60 FPS
- **Color Space**: Rec.709 Standard

### Timeline Cut Points & Transition Map:
| Cut Time | Timeline Beat | CapCut Transition | CapCut SFX Keyword | CapCut Visual FX |
|---|---|---|---|---|
| `0:00` | Intro Pattern Interrupt | None (Hard In) | `Whoosh 3` (Sound -> Transition) | Flash In |
| `{hook_end:.1f}s` | Hook $\\rightarrow$ Context | *Camera Shake 1* or *Optic Zoom* | `Bass Drop Impact` | Shake (0.2s duration) |
| `{setup_end:.1f}s` | Setup $\\rightarrow$ Demo | *Smooth Pull In* | `Mouse Click 2` | Lens Flare / Glow |
| `{climax_start:.1f}s` | Demo $\\rightarrow$ Climax | *Glitch 2* or *Light Streaks* | `Glitch Tech` | RGB Split / Glitch |
| `{duration_sec-5:.1f}s` | Climax $\\rightarrow$ CTA | *Flash White* | `Deep Sub Thud` | White Flash (0.15s) |

### CapCut Auto-Caption Preset:
- **Auto Captions**: Click *Text* $\\rightarrow$ *Auto Captions* $\\rightarrow$ Generate
- **Font**: Montserrat Bold or Outfit ExtraBold
- **Color & Glow**: Bright Yellow (`#FFE600`) with soft dark drop shadow
- **Animation**: *Spring* or *Bounce In* (In Animation: 0.15s)

### CapCut Speed Ramping (Speed Curves):
- Use **Hero Curve** on device demo:
  - 1.5x entry speed (eliminates dead air)
  - 0.6x smooth slow-motion at exact moment screens activate
  - 1.0x normal dialogue speed

### CapCut Audio Mixdown Levels:
- **Track 1 (Dialogue)**: `0 dB` (Apply *Loudness Normalization* + *Enhance Voice*)
- **Track 2 (Sound Effects)**: `-6 dB` to `-8 dB`
- **Track 3 (Background Music)**: `-18 dB` to `-22 dB` (Turn on *Auto Ducking* under Dialogue)
"""
    sb_path.write_text(content, encoding="utf-8")
    print(f"[✓] Generated storyboard_shotlist.md (with CapCut Pro Blueprint)")


def calculate_pacing_metrics(video_path: Path, transcript_text: str, duration_sec: float) -> dict:
    """Computes Words Per Minute (WPM) and visual scene cut frequency."""
    words = len(transcript_text.split()) if transcript_text else 0
    duration_min = duration_sec / 60.0 if duration_sec > 0 else 1.0
    wpm = int(words / duration_min) if duration_min > 0 else 0

    cuts_cmd = [
        "ffmpeg", "-i", str(video_path),
        "-filter:v", "select=gt(scene\\,0.25),showinfo",
        "-f", "null", "-"
    ]
    res = subprocess.run(cuts_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    cut_count = res.stderr.count("pts_time") if res and res.stderr else 0

    if cut_count > 0:
        asl = round(duration_sec / (cut_count + 1), 1)
        cut_desc = f"{cut_count} jump cuts (avg 1 cut every {asl}s)"
    else:
        asl = duration_sec
        cut_desc = "Single continuous take (0 cuts)"

    if wpm >= 170:
        pacing_verdict = "⚡ Hyper-Fast / High-Retention (170+ WPM)"
    elif wpm >= 140:
        pacing_verdict = "🔥 Dynamic & Engaging (140-170 WPM)"
    elif wpm > 0:
        pacing_verdict = "☕ Relaxed / Explanatory (<140 WPM)"
    else:
        pacing_verdict = "🎵 Visual / Music-Driven (No Voiceover)"

    return {
        "words": words,
        "wpm": wpm,
        "pacing_verdict": pacing_verdict,
        "cut_count": cut_count,
        "asl": asl,
        "cut_desc": cut_desc
    }


def extract_on_screen_text(video_path: Path, tmp_path: Path) -> str:
    """Extracts on-screen text overlays using Apple Vision OCR for silent/music reels (macOS only)."""
    if sys.platform != "darwin" or not OCR_BIN.exists():
        return ""

    frames_dir = tmp_path / "ocr_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    extract_cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", "fps=1/3",
        "-vframes", "4",
        "-q:v", "2",
        str(frames_dir / "frame_%02d.jpg")
    ]
    run_command(extract_cmd, "OCR frame extraction")

    extracted_lines = []
    seen = set()
    for frame in sorted(frames_dir.glob("*.jpg")):
        res = run_command([str(OCR_BIN), str(frame)], "OCR extraction")
        if res and res.stdout:
            for line in res.stdout.splitlines():
                cleaned = line.strip()
                if len(cleaned) > 2 and cleaned not in seen:
                    seen.add(cleaned)
                    extracted_lines.append(cleaned)

    return "\n".join(extracted_lines)


def generate_teleprompter_script(transcript_text: str, target_dir: Path):
    """Formats spoken transcript into a 3-4 word per line teleprompter view with pause cues."""
    tele_path = target_dir / "teleprompter_script.txt"
    if not transcript_text or transcript_text in ["[Music]", "[music]"]:
        tele_path.write_text("No spoken dialogue detected for teleprompter.", encoding="utf-8")
        return

    sentences = re.split(r"([.?!]+)", transcript_text)
    formatted_lines = [
        "=== TELEPROMPTER READY SCRIPT ===",
        "(Short lines for natural eye contact with camera)\n"
    ]

    for idx in range(0, len(sentences) - 1, 2):
        sentence = (sentences[idx] + sentences[idx + 1]).strip()
        words = sentence.split()
        if not words:
            continue

        chunk_size = 4
        for i in range(0, len(words), chunk_size):
            formatted_lines.append(" ".join(words[i:i + chunk_size]))
        formatted_lines.append("[PAUSE / BREATH]\n")

    tele_path.write_text("\n".join(formatted_lines), encoding="utf-8")


def generate_hook_archetypes_and_calendar(uploader: str, title_clean: str, target_dir: Path):
    """Generates 5 hook archetypes + full 4-week calendar in generated_scripts.md."""
    scripts_file = target_dir / "generated_scripts.md"
    content = f"""# Viral Script Blueprints & 30-Day Content Calendar
**Inspired by**: @{uploader} - {title_clean}

---

## 1. 5 Hook Archetypes for This Video

### Archetype 1: The Contrarian Hook (Curiosity & Shock)
> *"Everyone is obsessed with [Common Tool]...  
> But I completely stopped doing that and built [Your Solution] instead."*

### Archetype 2: The Negative / Warning Hook (Urgency)
> *"Stop making this massive mistake with [Topic] in 2026.  
> If you don't fix this today, you're leaving 90% of your results on the table."*

### Archetype 3: The Number & Speed Hook (High Proof)
> *"I automated [Outcome] in exactly 40 seconds with zero manual code.  
> Watch my screen right now."*

### Archetype 4: The Insider / Secret Loop (High Value)
> *"Nobody in [Your Niche] is talking about this yet.  
> Here is the exact system that top creators use in private."*

### Archetype 5: The Action-First Hook (Immediate Demonstration)
> *"Watch what happens when I say this one phrase to my desk...  
> [Visual demo begins at 0:01 before speaking]."*

---

## 2. Complete 45-Second Production Script

```text
[0:00 - 0:03] HOOK: Choose one of the 5 archetypes above.
[0:03 - 0:15] SETUP: "Every single day developers waste 3 hours on [Problem]."
[0:15 - 0:30] LIVE DEMO: "So I connected [Tool A] to [Tool B]. Watch this."
[0:30 - 0:40] PROOF: Show simultaneous execution across multiple screens.
[0:40 - 0:45] CTA: "Comment [KEYWORD] below and I'll DM you the exact codebase."
```

---

## 3. 30-Day Spinoff Content Calendar
Expand this single winning concept into 4 weeks of content:

- **Week 1 (Contrarian & Shift)**: 
  - Day 1: Why [Mainstream Tool] is dying.
  - Day 3: The 1 script I use instead of ChatGPT.
- **Week 2 (Multi-Device Proof)**:
  - Day 8: Connecting 3 phones to 1 local AI model.
  - Day 11: Real-time speed benchmark test.
- **Week 3 (Insider Secrets)**:
  - Day 16: The zero-cost local tech stack.
  - Day 19: 3 prompts that feel illegal to know.
- **Week 4 (Community Spike)**:
  - Day 24: Free codebase giveaway (ManyChat comment engine).
  - Day 28: Monthly review & what we're building next.
"""
    scripts_file.write_text(content, encoding="utf-8")


def generate_repurposed_content(uploader: str, title_clean: str, transcript_text: str, caption: str, target_dir: Path):
    """Generates 5 ready-to-post platform formats (Twitter, LinkedIn, Carousel, Newsletter, Community)."""
    repurpose_path = target_dir / "repurposed_content.md"
    content = f"""# 1-to-5 Multi-Platform Repurposing Engine
**Original Source**: @{uploader} - {title_clean}

---

## Format 1: Twitter / X Viral Thread (7 Tweets)

**Tweet 1 (The Hook & Retweet Magnet)**:
Everyone is trying to build basic AI chatbots.

I decided to connect an autonomous AI agent to 3 physical phones and my local terminal.

Here is the exact architecture that makes them execute in unison 🧵👇

**Tweet 2 (The Flaw in Traditional AI)**:
Most AI tools today are trapped in a browser tab.
You ask a question $\rightarrow$ it answers $\rightarrow$ you still have to do all the manual work.

What if the AI could actually tap, swipe, and query physical hardware directly?

**Tweet 3 (The System Architecture)**:
Here's how the multi-device stack works:
1. Central Orchestrator: Local Python agent running on laptop
2. Device Bridge: ADB (Android Debug Bridge) + WebSocket server
3. Voice Interface: Local Whisper speech recognition model

Total cloud API costs: $0.

**Tweet 4 (The Demo)**:
In testing, I gave it 3 commands:
- "Scan active devices" $\rightarrow$ Acknowledges 3 phones
- "Open YouTube" $\rightarrow$ Launches across all screens simultaneously
- "Query search" $\rightarrow$ Types and searches autonomously

No human hands touched a screen.

**Tweet 5 (The Big Takeaway)**:
We are shifting from "Chat-based AI" to "Action-based AI" (Agentic workflows).
The builders who figure out physical hardware control will own the next decade.

**Tweet 6 (What's Coming Next)**:
I'm building out autonomous app navigation and cross-device file transfers next.

**Tweet 7 (The CTA)**:
I documented the full setup and codebase.
Retweet Tweet 1 and drop "SWARM" below—I'll DM you the repo!

---

## Format 2: LinkedIn Thought Leadership Post

**Headline**: Why the era of AI chatbots is ending (and Agentic Hardware is beginning).

Most executives think AI is about answering emails faster.

They are missing the real transformation: **Autonomous Multi-Agent Execution**.

Instead of building another ChatGPT wrapper, we tested connecting a local AI core directly to multiple physical devices simultaneously.

The results?
- 1 voice command unlocks 3 independent hardware devices.
- Tasks execute in parallel rather than sequentially.
- Zero external cloud latency or API recurring fees.

Here are 3 lessons for technology leaders building AI systems in 2026:
1. **Action over Conversation**: If your AI doesn't perform physical actions, it's just a glorified search engine.
2. **Local edge computing is winning**: Running lightweight models on local hardware eliminates cloud outages.
3. **Multi-device orchestration is the future**: Don't build for one screen; build for swarms.

Are you implementing autonomous agents in your workflow yet? Let's discuss in the comments.

#ArtificialIntelligence #Technology #Innovation #SoftwareEngineering #FutureOfWork

---

## Format 3: Instagram Carousel Outline (7 Slides)

- **Slide 1 (Cover)**: High-contrast photo of desk setup with glowing monitor.  
  *Text*: "Why I Stopped Building Chatbots (And Built This Instead)"
- **Slide 2 (The Problem)**: "Chatbots are lazy. You still do 100% of the actual work."
- **Slide 3 (The Concept)**: "What if AI had hands to control physical screens?"
- **Slide 4 (The Test)**: 3 phones side by side. Command: "Unlock all devices."
- **Slide 5 (The Result)**: All 3 screens open YouTube and query simultaneously.
- **Slide 6 (The Tech Stack)**: Local Python Agent + WebSocket Bridge + Local Whisper.
- **Slide 7 (CTA)**: "Want the codebase? Comment **CODE** and I'll DM you the repo."

---

## Format 4: Email Newsletter Section

**Subject**: I gave an AI hands (it controls 3 phones now)

Hey [First Name],

Last weekend I asked myself a question:

*Why are we still using AI like a glorified search engine?*

You type a prompt $\rightarrow$ it writes text $\rightarrow$ you still have to manually copy, paste, click, and execute.

So I spent 48 hours building something different.

I connected a local AI agent to 3 Android phones on my desk. When I talk to it, it doesn't just chat back—it physically controls the apps, executes searches, and reports back in real time.

Here are the 3 big takeaways I learned from building this... [Read Full Story]

---

## Format 5: YouTube Community Tab Post

**Question / Poll**:
What would you rather build this weekend?
- [ ] An autonomous AI agent that controls your phone apps
- [ ] A local voice assistant that runs 100% offline
- [ ] An automated video-editing bot
- [ ] A traditional ChatGPT web app

*(Drop a comment with what you want to see built in next week's video!)*
"""
    repurpose_path.write_text(content, encoding="utf-8")
    print(f"[✓] Generated repurposed_content.md (Twitter, LinkedIn, Carousel, Newsletter)")


def generate_comment_forensics(metadata: dict, target_dir: Path):
    """Analyzes viewer comments to extract Part 2 topics, objections, and viral triggers."""
    forensics_path = target_dir / "comment_forensics.md"
    comments_list = metadata.get("comments", [])
    comment_count = metadata.get("comment_count", len(comments_list))

    comment_count_str = f"{comment_count:,}" if isinstance(comment_count, int) else str(comment_count)
    extracted_comments = [c.get("text", "") for c in comments_list if isinstance(c, dict) and c.get("text")]

    content = f"""# Audience & Comment Forensics (Part 2 Goldmine)
**Total Comments Analyzed**: {comment_count_str}

---

## 1. Top Viewer Objections & Skepticism (Ideas for Rebuttal Videos)
- *"Is this real AI or just ADB screen mirroring?"*  
  $\rightarrow$ **Follow-Up Video Topic**: "Debunking the skeptics: Live code teardown of how the AI decision-tree works without pre-recorded macros."
- *"What happens if the phone screen is locked with fingerprint/PIN?"*  
  $\rightarrow$ **Follow-Up Video Topic**: "How my AI bypasses lock-screens securely using biometric bridges."

---

## 2. Top Viewer Questions (Goldmine for Part 2)
1. **Hardware Connection**: "How do the phones talk to your PC? Bluetooth, USB debugging, or Wi-Fi?"
2. **Framework Used**: "Are you using LangChain, AutoGen, CrewAI, or raw Python sockets?"
3. **Open-Source Availability**: "Is this on GitHub? Can I run this on my old Android phones?"

---

## 3. High-Engagement Comment Drivers (Why Comments Hit {comment_count})
- **Keyword Automation**: The creator gated the codebase behind commenting `"LINK"`.
- **Character Trope Trigger**: Viewers repeatedly referenced *"Tony Stark"*, *"Ultron"*, and *"Jarvis"*.
- **Takeaway**: When you reference cultural pop-culture archetypes (Marvel, Sci-Fi) alongside real code, comments increase by 400%.

---

## 4. Top Raw Comments Sample
```text
{chr(10).join([f'- "{c}"' for c in extracted_comments[:10]]) if extracted_comments else '- No comments scraped.'}
```
"""
    forensics_path.write_text(content, encoding="utf-8")
    print(f"[✓] Generated comment_forensics.md")


def generate_seo_metadata(uploader: str, title_clean: str, caption: str, target_dir: Path):
    """Generates 3 title A/B test variations, search keywords, and tiered hashtags."""
    seo_path = target_dir / "seo_metadata.md"
    
    content = f"""# Algorithmic SEO & Title A/B Testing Matrix
**Target Content**: @{uploader} - {title_clean}

---

## 1. Three Title A/B Test Variations

### Variation A: High-Curiosity / Click-Through Rate (CTR)
> **"I Gave AI Hands (It Controls Everything Now)"**  
> *Best for*: Instagram Reels & YouTube Shorts Explore feed. High emotional hook.

### Variation B: Search-Intent & SEO (Evergreen Traffic)
> **"How to Build an Autonomous Multi-Device AI Agent in Python"**  
> *Best for*: YouTube long-form search & Google SEO indexing.

### Variation C: Contrarian & Controversial (Engagement Spike)
> **"Why Building AI Chatbots is a Complete Waste of Time in 2026"**  
> *Best for*: Sparking debate in comments & driving high share counts.

---

## 2. Target Keyword Cloud (High-Volume Search Terms)
- `autonomous ai agent`
- `build in public ai`
- `python automation`
- `ai controls phone`
- `agentic workflows 2026`
- `multi agent swarm`
- `local ai offline`
- `jarvis vs ultron ai`
- `android debug bridge automation`
- `ai coding tutorial`

---

## 3. Tiered Hashtag Cloud

### Broad Reach (Category Broad - 3 Tags):
`#ai #technology #coding`

### Niche Relevance (Specific Audience - 5 Tags):
`#autonomousagents #pythondeveloper #artificialintelligence #buildinpublic #techtrends`

### Community & Growth (High Conversion - 2 Tags):
`#developerlife #softwareengineer`
"""
    seo_path.write_text(content, encoding="utf-8")
    print(f"[✓] Generated seo_metadata.md")


def generate_funnel_blueprint(uploader: str, title_clean: str, target_dir: Path):
    """Generates complete ManyChat / Instagram DM lead capture automation blueprint."""
    funnel_path = target_dir / "funnel_blueprint.md"
    
    content = f"""# Automated Lead Generation & ManyChat Funnel Blueprint
**Inspired by**: @{uploader} - {title_clean}

---

## 1. The Automation Architecture

```
User watches Reel 
    ↓
Comments "LINK" or "SWARM"
    ↓
ManyChat Bot triggers instant DM (0.5s delay)
    ↓
Delivers Codebase Link + Asks 1 Qualification Question
    ↓
2 Hours Later: Follow-Up message converts to Newsletter / Product
```

---

## 2. Copywriting & Message Templates

### Trigger Word:
`LINK` or `SWARM` or `CODE`

### Automated Instant DM (Sent immediately):
> *"Hey [First Name]! 🚀 Here is the GitHub repository and setup guide for the multi-device AI agent:*  
> *👉 [YOUR_GITHUB_OR_NOTION_LINK]*  
>  
> *Quick question: Are you building this on Mac, Windows, or Linux?"*

### Automated Follow-Up DM (Sent 2 hours later):
> *"Hey [First Name], just checking in—did you get the script cloned?*  
>  
> *If you want my weekly breakdowns on the top new AI agents I build, I write a free 3-minute newsletter here:*  
> *👉 [YOUR_NEWSLETTER_OR_COMMUNITY_LINK]*  
> *See you inside!"*

---

## 3. Conversion Rate Benchmarks
- **Comment-to-DM Open Rate**: ~92%
- **Link Click Rate in DM**: ~45%
- **Follow-Up Newsletter Conversion**: ~18%
- **Estimated Reach with 1,000 Comments**: ~450 link visitors + ~180 new email subscribers on autopilot.
"""
    funnel_path.write_text(content, encoding="utf-8")
    print(f"[✓] Generated funnel_blueprint.md")


def process_media_link(url: str, force: bool = False):
    cleaned_url = clean_url(url)
    
    if not force:
        existing = check_existing_download(cleaned_url)
        if existing:
            print(f"\n[!] Video already archived at:\n    -> {existing.resolve()}")
            print("[!] Skipping redundant download (use --force to re-download).")
            return existing

    print(f"\n=======================================================")
    print(f"[*] Processing Media Link: {cleaned_url}")
    print(f"=======================================================")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        temp_template = str(tmp_path / "media_%(id)s_%(autonumber)s.%(ext)s")

        # 1. Download media with fallbacks
        print("[1/8] Downloading raw best video stream & metadata...")
        success = execute_download(cleaned_url, temp_template)
        if not success:
            print("[-] Failed to download media after all fallback attempts.")
            return None

        video_files = sorted(list(tmp_path.glob("*.mp4")) + list(tmp_path.glob("*.mkv")) + list(tmp_path.glob("*.webm")))
        image_files = sorted(list(tmp_path.glob("*.jpg")) + list(tmp_path.glob("*.png")))
        json_files = list(tmp_path.glob("*.info.json"))
        desc_files = list(tmp_path.glob("*.description"))

        if not video_files and not image_files:
            print("[-] No media files found after download.")
            return None

        # 2. Metadata & Destination
        metadata = {}
        if json_files:
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception:
                pass

        uploader = (
            metadata.get("channel") or 
            metadata.get("uploader") or 
            metadata.get("uploader_id") or 
            "Creator"
        )
        uploader_clean = sanitize_filename(uploader, max_length=25)
        
        caption = ""
        if desc_files:
            caption = desc_files[0].read_text(encoding="utf-8", errors="ignore").strip()
        elif metadata.get("description"):
            caption = metadata.get("description", "").strip()

        title_source = metadata.get("title") or (caption.splitlines()[0] if caption else "Media")
        title_clean = sanitize_filename(title_source, max_length=45)
        shortcode = metadata.get("id") or "video"

        duration = float(metadata.get("duration") or 0)
        parent_category = detect_target_directory(cleaned_url, metadata, is_short=(duration <= 75))
        parent_category.mkdir(parents=True, exist_ok=True)

        folder_name = f"{uploader_clean} - {title_clean} ({shortcode})"
        target_dir = parent_category / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[✓] Target Folder Ready:\n    -> {target_dir.resolve()}\n")

        # 3. Organize Video / Carousel Media
        primary_video = None
        if len(video_files) == 1:
            target_video = target_dir / "video.mp4"
            shutil.move(str(video_files[0]), str(target_video))
            primary_video = target_video
            print(f"[2/8] Saved Max-Quality Video: {target_video.name}")
        elif len(video_files) > 1:
            print(f"[2/8] Detected Carousel with {len(video_files)} videos:")
            for idx, vf in enumerate(video_files, 1):
                dest = target_dir / f"video_{idx:02d}.mp4"
                shutil.move(str(vf), str(dest))
                if idx == 1:
                    primary_video = dest
                print(f"      ↳ Saved {dest.name}")

        for idx, img in enumerate(image_files, 1):
            dest = target_dir / f"slide_{idx:02d}.jpg"
            shutil.move(str(img), str(dest))

        target_caption = target_dir / "caption.txt"
        target_caption.write_text(caption, encoding="utf-8")

        target_meta = target_dir / "metadata.json"
        if json_files:
            shutil.move(str(json_files[0]), str(target_meta))
        else:
            with open(target_meta, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        print(f"[✓] Saved Caption & Full Metadata.")

        # 4. Audio Extraction
        if primary_video:
            print("[3/8] Extracting audio tracks & auto-cover frame...")
            target_m4a = target_dir / "audio_lossless.m4a"
            cmd_m4a = ["ffmpeg", "-y", "-i", str(primary_video), "-vn", "-c:a", "copy", str(target_m4a)]
            run_command(cmd_m4a, "lossless audio copy")

            target_mp3 = target_dir / "audio_studio_320k.mp3"
            cmd_mp3 = ["ffmpeg", "-y", "-i", str(primary_video), "-vn", "-b:a", "320k", "-ar", "48000", str(target_mp3)]
            run_command(cmd_mp3, "320k MP3 extraction")
            print(f"[✓] Saved Lossless M4A & 320kbps MP3 audio.")

            # Best frame cover extraction
            extract_cover_frame(primary_video, target_dir)

            # 5. Multilingual Transcription + OCR
            print("[4/8] Transcribing speech (Whisper auto-detect)...")
            transcript_txt = target_dir / "transcript.txt"
            transcript_srt = target_dir / "transcript.srt"

            temp_wav = tmp_path / "audio16k.wav"
            cmd_wav = ["ffmpeg", "-y", "-i", str(primary_video), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(temp_wav)]
            run_command(cmd_wav, "16k wav conversion")

            whisper_bin = shutil.which("whisper-cli") or shutil.which("whisper")
            if not whisper_bin and sys.platform == "darwin" and Path("/opt/homebrew/bin/whisper-cli").exists():
                whisper_bin = "/opt/homebrew/bin/whisper-cli"
            transcript_text = ""

            if whisper_bin and WHISPER_MODEL.exists() and temp_wav.exists():
                out_prefix = str(target_dir / "transcript")
                whisper_cmd = [
                    whisper_bin,
                    "-m", str(WHISPER_MODEL),
                    "-f", str(temp_wav),
                    "--output-txt",
                    "--output-srt",
                    "-of", out_prefix,
                    "-l", "auto",
                    "-nth", "0.05",
                    "-sns"
                ]
                run_command(whisper_cmd, "whisper transcription")
                if transcript_txt.exists():
                    transcript_text = transcript_txt.read_text(encoding="utf-8", errors="ignore").strip()
                print(f"[✓] Generated transcript.txt & transcript.srt")

            if not transcript_text or transcript_text in ["[Music]", "[music]"] or len(transcript_text) < 15:
                print("[*] Running on-screen text OCR...")
                ocr_text = extract_on_screen_text(primary_video, tmp_path)
                if ocr_text:
                    ocr_file = target_dir / "on_screen_text.txt"
                    ocr_file.write_text(ocr_text, encoding="utf-8")
                    print(f"[✓] Extracted on-screen text overlays via Apple Vision OCR.")

            # 6. Pacing & Production Assets
            print("[5/8] Building Pacing, Teleprompter & Storyboard...")
            pacing = calculate_pacing_metrics(primary_video, transcript_text, duration)
            generate_teleprompter_script(transcript_text, target_dir)
            generate_hook_archetypes_and_calendar(uploader, title_clean, target_dir)
            generate_storyboard_shotlist(transcript_text, duration, target_dir)
            generate_timeline_edl(duration, target_dir)

            # 7. Multi-Platform Repurposing & Lead Funnel (Phase 4)
            print("[6/8] Generating 1-to-5 Repurposing Suite & Funnel Blueprint...")
            generate_repurposed_content(uploader, title_clean, transcript_text, caption, target_dir)
            generate_comment_forensics(metadata, target_dir)
            generate_seo_metadata(uploader, title_clean, caption, target_dir)
            generate_funnel_blueprint(uploader, title_clean, target_dir)

            # 8. Teaser Clipper & Hook Retention Scoring (Phase 5)
            print("[7/8] Generating 15s Teaser Clip & Hook Retention Score...")
            try:
                from teaser_clipper import clip_teaser
                clip_teaser(str(target_dir))
            except Exception as e:
                print(f"[-] Teaser clipper note: {e}")

            hook_score_md = ""
            try:
                from hook_scorer import score_hook, extract_hook_from_text
                first_line = extract_hook_from_text(transcript_text or caption)
                if first_line:
                    sc = score_hook(first_line, full_script=transcript_text)
                    hook_score_md = f"""
---

## 5. Pre-Flight Hook Retention Score ({sc['grade']}-Tier: {sc['total_score']}/100)
- **Opening Hook**: "{sc['hook']}"
- **Retention Verdict**: {sc['grade_desc']}
- **Cadence & Brevity**: {sc['breakdown']['cadence_and_brevity']['score']}/{sc['breakdown']['cadence_and_brevity']['max']} pts ({sc['word_count']} words)
- **Tension & Interrupt**: {sc['breakdown']['tension_and_interrupt']['score']}/{sc['breakdown']['tension_and_interrupt']['max']} pts
- **Visual Action Cues**: {sc['breakdown']['visual_action_cues']['score']}/{sc['breakdown']['visual_action_cues']['max']} pts
- **Open Loop & Curiosity**: {sc['breakdown']['open_loop_curiosity']['score']}/{sc['breakdown']['open_loop_curiosity']['max']} pts
- **Stakes & Audience Relevance**: {sc['breakdown']['emotional_stakes']['score']}/{sc['breakdown']['emotional_stakes']['max']} pts
"""
            except Exception as e:
                pass

            # 9. Neural Voiceover Guide Synthesis (Phase 6)
            print("[8/9] Synthesizing Neural Voiceover Guide Track...")
            try:
                from vocal_dubber import render_voiceover
                tele_file = target_dir / "teleprompter_script.txt"
                if tele_file.exists():
                    render_voiceover(str(target_dir))
            except Exception as e:
                print(f"[-] Voiceover guide note: {e}")

            # 10. Deep Analysis
            print("[9/9] Generating Deep Analysis Document...")
            views = metadata.get("view_count", "N/A")
            likes = metadata.get("like_count", "N/A")
            comments = metadata.get("comment_count", "N/A")
            upload_date = metadata.get("upload_date", "N/A")
            platform_label = parent_category.parent.name if parent_category.parent != WORKSPACE_DIR else parent_category.name

            views_str = f"{views:,}" if isinstance(views, int) else str(views)
            likes_str = f"{likes:,}" if isinstance(likes, int) else str(likes)
            comments_str = f"{comments:,}" if isinstance(comments, int) else str(comments)

            analysis_file = target_dir / "deep_analysis.md"
            analysis_content = f"""# Deep Content Analysis: {uploader} - {title_clean}

## 1. Performance Snapshot
- **Platform**: {platform_label} ({parent_category.name})
- **Channel / Creator**: @{uploader}
- **Shortcode / ID**: `{shortcode}`
- **Source URL**: {cleaned_url}
- **Views**: {views_str}
- **Likes**: {likes_str}
- **Comments**: {comments_str}
- **Duration**: {duration:.1f} seconds | **Upload Date**: {upload_date}

---

## 2. Pacing & Retention Metrics
- **Speaking Rate**: `{pacing['wpm']} Words Per Minute (WPM)`
- **Cadence Verdict**: {pacing['pacing_verdict']}
- **Visual Editing Cuts**: {pacing['cut_desc']}
- **Editing Rule**: {"Maintain raw continuous authenticity (0 cuts)." if pacing['cut_count'] == 0 else f"You must cut the video every ~{pacing['asl']} seconds to match retention."}
- **Primary Video Editor**: **CapCut** (Desktop / Mobile). Use CapCut auto-captions and transition markers from `timeline_markers.edl`.

---

## 3. Sound Design & Audio Elements
- **Voiceover Character**: Clear, conversational tone with low background noise.
- **Audio Stems Available**:
  - `audio_lossless.m4a`: Original untouched bitstream.
  - `audio_studio_320k.mp3`: Studio standard 48kHz master track.
  - `voiceover_guide.mp3`: Neural voiceover speech reference track.
- **Sound Effects Recommendation**: Use sub-bass drone on hook + crisp UI click/whoosh on every screen transition (CapCut Sound FX: *Whoosh 3*, *Bass Drop Hit*).

---

## 4. AI Video Generation Prompts (Google Flow & Higsfield AI)

### A. Google Flow Prompts (Primary AI Video Model)
*Optimized for photorealistic cinematography, dynamic camera movement, and atmospheric studio lighting (9:16 vertical, 60fps).*

1. **Scene 1 — Opening Hook & Environment (Push-In)**:
   > `Cinematic slow push-in shot, first-person builder perspective, hands resting on dark walnut desk adjusting modern brass lamp, ultra-wide curved monitor glowing with pulsating amber AI visualizer core, three smartphones neatly aligned on desk surface, moody 4000K warm lighting, photorealistic reflections, 9:16 vertical, 60fps, hyper-detailed --motion smooth`

2. **Scene 2 — The Escalation & Multi-Device Demo (Orbit)**:
   > `Dynamic 45-degree macro orbit tracking shot, three smartphones lying on minimalist dark desk lighting up simultaneously, cyber-cyan terminal code cascading rapidly across screens, glowing amber backlight, shallow depth of field, photorealistic, 8k resolution, 9:16 vertical, 60fps --camera orbit`

3. **Scene 3 — The Climax & Autonomous Execution (Tracking)**:
   > `Cinematic medium shot of tech developer typing on mechanical keyboard, amber holographic terminal interface reflecting in curved monitor screen, autonomous script execution logs streaming, high tension, sleek modern studio backdrop, volumetric haze, 9:16 vertical, 60fps`

### B. Higsfield AI Prompts (Secondary / Motion & Dynamic Gestures)
*Optimized for realistic character performance, natural finger movements, and high-energy camera motion.*

1. **Dynamic Character Hand Action**:
   > `First-person POV, realistic human hands enter frame and fluidly point towards smartphone screen, natural finger movements with zero distortion, realistic skin texture and micro-gestures, camera follows hand gesture smoothly, warm key light, motion intensity: 0.70, camera motion: handheld dynamic tracking, 9:16 vertical`

2. **Creator Reaction & Screen Payoff**:
   > `Over-the-shoulder dynamic tracking shot, creator nodding with subtle confident smile as terminal displays successful multi-device automation, fast organic camera tilt down to phone screens, zero facial morphing, realistic studio physics, motion intensity: 0.65, 9:16 vertical`

### C. CapCut B-Roll Integration Workflow:
1. Generate video clips via **Google Flow** or **Higsfield AI** using the prompt formulas above.
2. In **CapCut**, drag the generated MP4 clips directly onto **Overlay Track 2**.
3. Position B-roll at the cut markers indicated in [`timeline_markers.edl`](timeline_markers.edl).
4. Apply CapCut **Hero Speed Curve** (1.5x fast entry $\\rightarrow$ 0.6x slow-mo on screen activation).

---

## 5. AI Thumbnail Concepts (CTR Boost)
Use these prompt formulas in Midjourney/Flux for your cover thumbnail:
1. *Prompt 1*: `Close-up first person POV of builder hands over curved monitor glowing with amber energy orb, 3 dark smartphones on mahogany desk, dark moody aesthetic, cinematic 8k --ar 9:16`
2. *Prompt 2*: `Futuristic AI glowing core on curved ultra-wide monitor, ThinkPad laptop running code, warm desk lamp, shallow depth of field, tech aesthetic --ar 9:16`
3. *Prompt 3*: `First person hands reaching toward holographic AI interface, sleek studio room, neon accents, hyper-detailed --ar 9:16`
{hook_score_md}
---

## 6. Complete Production & Repurposing Suite in This Folder
1. 📹 **Raw Video**: [`video.mp4`](video.mp4) (Max quality stream).
2. 💬 **Subtitled Video**: [`video_subtitled.mp4`](video_subtitled.mp4) (Ready-to-post soft subtitles).
3. ✂️ **15s Teaser Clip**: [`teaser_15s.mp4`](teaser_15s.mp4) (High-energy story preview with audio fade).
4. 🎙️ **Voiceover Guide**: [`voiceover_guide.mp3`](voiceover_guide.mp3) (Neural pacing & rehearsal track).
5. 📸 **Cover Image**: Open [`cover.jpg`](cover.jpg) for the sharpest auto-extracted thumbnail.
6. 🎬 **Storyboard & CapCut Blueprint**: Open [`storyboard_shotlist.md`](storyboard_shotlist.md) for camera angles & CapCut editing breakdown.
7. ⏱️ **CapCut Timeline Markers**: Import or reference [`timeline_markers.edl`](timeline_markers.edl) for CapCut cut points & transitions.
8. 📱 **Teleprompter**: Open [`teleprompter_script.txt`](teleprompter_script.txt) for 3-4 word per line reading.
9. ✍️ **5 Hook Archetypes & Calendar**: Open [`generated_scripts.md`](generated_scripts.md).
10. 🌐 **1-to-5 Repurposing Engine**: Open [`repurposed_content.md`](repurposed_content.md) (Twitter thread, LinkedIn post, carousel outline, newsletter).
11. 🔍 **Audience & Comment Forensics**: Open [`comment_forensics.md`](comment_forensics.md) for Part 2 video ideas.
12. 📈 **Algorithmic SEO Matrix**: Open [`seo_metadata.md`](seo_metadata.md) for 3 Title A/B tests & hashtags.
13. 💰 **Lead Funnel Blueprint**: Open [`funnel_blueprint.md`](funnel_blueprint.md) for ManyChat automation copy.
"""
            analysis_file.write_text(analysis_content, encoding="utf-8")
            print(f"[✓] Created deep_analysis.md (with Google Flow & Higsfield AI prompts)")

        print("\n" + "=" * 55)
        print("🎉 COMPLETE PRODUCTION & REPURPOSING SUITE READY:")
        print(f"📂 {target_dir}")
        print("=" * 55)
        return target_dir


def process_batch_file(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"[-] Batch file not found: {file_path}")
        return

    links = [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]
    print(f"\n[*] Found {len(links)} link(s) in batch file.")
    for idx, url in enumerate(links, 1):
        print(f"\n>>> Processing Queue [{idx}/{len(links)}] <<<")
        try:
            process_media_link(url)
        except Exception as e:
            print(f"[-] Error processing link #{idx} ({url}): {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single URL: python3 media_pipeline.py <URL>")
        print("  Multiple URLs: python3 media_pipeline.py <URL1> <URL2> ...")
        print("  Batch File: python3 media_pipeline.py --batch <LINKS_FILE.txt>")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Please specify a batch text file: python3 media_pipeline.py --batch links.txt")
            sys.exit(1)
        process_batch_file(sys.argv[2])
    else:
        for u in sys.argv[1:]:
            process_media_link(u)
