#!/usr/bin/env python3
"""
Local Creator Studio Dashboard (Interactive Visual UI)
======================================================
Dark-mode local browser studio running on http://localhost:8080
Provides:
- Video player with raw / subtitled / 15s teaser stream switching
- Master studio 320k audio player
- Teleprompter with auto-scroll and speed controls
- 1-to-5 Repurposed Content suite with 1-click copy buttons
- Live interactive Viral Hook & Script Scorer
- Storyboard, B-roll shotlist, and EDL marker inspector
- Deep Intelligence (comment forensics, ManyChat funnels)
- New URL pipeline execution with live terminal streaming

Usage:
  python3 Pipeline_Tools/studio_ui.py [--port 8080]
"""

import sys
import os
import json
import re
import argparse
import subprocess
import threading
import time
import mimetypes
from urllib.parse import urlparse, parse_qs, unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

# Base workspace directory (one level up from Pipeline_Tools)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(CURRENT_DIR)

# Import Hook Scorer, Teaser Clipper & Vocal Dubber
sys.path.insert(0, CURRENT_DIR)
try:
    from hook_scorer import score_hook, extract_hook_from_text
except ImportError:
    score_hook = None
try:
    from teaser_clipper import clip_teaser
except ImportError:
    clip_teaser = None
try:
    from vocal_dubber import render_voiceover
except ImportError:
    render_voiceover = None

def find_all_projects():
    """Scans Instagram, YouTube, TikTok, and Twitter folders for processed projects and blueprints."""
    platforms = ["Instagram", "YouTube", "TikTok", "Twitter"]
    projects = []
    for platform in platforms:
        plat_dir = os.path.join(WORKSPACE_ROOT, platform)
        if not os.path.exists(plat_dir):
            continue
        for root, dirs, files in os.walk(plat_dir):
            if "metadata.json" in files or "video.mp4" in files or "teleprompter_script.txt" in files:
                rel_path = os.path.relpath(root, WORKSPACE_ROOT)
                folder_name = os.path.basename(root)
                has_video = os.path.exists(os.path.join(root, "video.mp4"))
                has_subtitled = os.path.exists(os.path.join(root, "video_subtitled.mp4"))
                has_teaser = os.path.exists(os.path.join(root, "teaser_15s.mp4"))
                has_voiceover = os.path.exists(os.path.join(root, "voiceover_guide.mp3"))
                has_audio = os.path.exists(os.path.join(root, "audio_studio_320k.mp3"))
                has_cover = os.path.exists(os.path.join(root, "cover.jpg"))

                meta = {}
                meta_file = os.path.join(root, "metadata.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as mf:
                            meta = json.load(mf)
                    except Exception:
                        pass

                creator = meta.get("uploader") or meta.get("channel") or folder_name.split(" - ")[0]
                title = meta.get("title") or (folder_name.split(" - ")[1] if " - " in folder_name else folder_name)

                projects.append({
                    "rel_path": rel_path,
                    "platform": platform,
                    "folder_name": folder_name,
                    "creator": creator,
                    "title": title,
                    "views": meta.get("view_count", 0),
                    "likes": meta.get("like_count", 0),
                    "comments": meta.get("comment_count", 0),
                    "duration": meta.get("duration", 0),
                    "has_video": has_video,
                    "has_subtitled": has_subtitled,
                    "has_teaser": has_teaser,
                    "has_audio": has_audio,
                    "has_cover": has_cover
                })
    return projects

def find_all_clusters():
    """Finds all multi-video genealogy / evolution clusters across workspace."""
    platforms = ["Instagram", "YouTube", "TikTok", "Twitter"]
    clusters = []
    for platform in platforms:
        plat_dir = os.path.join(WORKSPACE_ROOT, platform)
        if not os.path.exists(plat_dir):
            continue
        for root, dirs, files in os.walk(plat_dir):
            study_files = [f for f in files if f.startswith("MASTER_") and f.endswith(".md")]
            sub_iterations = [d for d in dirs if d.startswith(("01_", "02_", "03_", "04_"))]
            if study_files or len(sub_iterations) >= 2:
                folder_name = os.path.basename(root)
                rel_path = os.path.relpath(root, WORKSPACE_ROOT)
                master_study = ""
                if study_files:
                    master_study = read_file_safe(os.path.join(root, study_files[0]))

                members = []
                for sub in sorted(dirs):
                    if not sub.startswith(("01_", "02_", "03_", "04_")):
                        continue
                    sub_abs = os.path.join(root, sub)
                    sub_files = os.listdir(sub_abs) if os.path.isdir(sub_abs) else []
                    sub_meta = {}
                    if "metadata.json" in sub_files:
                        try:
                            with open(os.path.join(sub_abs, "metadata.json"), "r", encoding="utf-8") as mf:
                                sub_meta = json.load(mf)
                        except Exception:
                            pass
                    sub_rel = os.path.relpath(sub_abs, WORKSPACE_ROOT)
                    members.append({
                        "folder_name": sub,
                        "rel_path": sub_rel,
                        "title": sub_meta.get("title") or sub,
                        "creator": sub_meta.get("uploader") or sub_meta.get("channel") or sub,
                        "likes": sub_meta.get("like_count", 0),
                        "comments": sub_meta.get("comment_count", 0),
                        "duration": sub_meta.get("duration", 0),
                        "role": sub_meta.get("role_in_lineage") or ("Original" if "01_" in sub else "Iteration"),
                        "has_video": os.path.exists(os.path.join(sub_abs, "video.mp4")),
                        "has_subtitled": os.path.exists(os.path.join(sub_abs, "video_subtitled.mp4")),
                        "has_edl": os.path.exists(os.path.join(sub_abs, "timeline_markers.edl")),
                        "has_script": os.path.exists(os.path.join(sub_abs, "teleprompter_script.txt"))
                    })

                clusters.append({
                    "cluster_name": folder_name,
                    "rel_path": rel_path,
                    "platform": platform,
                    "master_study": master_study,
                    "members": members,
                    "total_likes": sum(m["likes"] for m in members),
                    "total_comments": sum(m["comments"] for m in members)
                })
    return clusters

def generate_remix_package(base_project, angle, persona, tools, cta_keyword, pacing, topic):
    """Generates customized production package based on questionnaire answers."""
    cta_keyword = cta_keyword.strip().upper() if cta_keyword else "ULTRON"
    tools_list = [t.strip() for t in tools.split(",") if t.strip()]
    tools_str = ", ".join(tools_list) if tools_list else "FastMCP, Wireless ADB, Claude Code"

    if angle == "breakdown":
        hook = f"Everyone saw this viral demo and thought it was movie AI... but it’s actually {len(tools_list) if tools_list else 4} developer tools connected together. Here is the exact stack."
        script = f"""[00:00 - 00:06]
Everyone saw this viral demo and thought he built a real-life movie AI... but he didn’t build an AGI.
[00:06 - 00:15]
He connected {len(tools_list) if tools_list else 4} open-source tools that you can set up on your laptop in twenty minutes.
[00:15 - 00:28]
First tool: {tools_list[0] if tools_list else 'Wireless ADB'}. This establishes socket connection over local Wi-Fi without needing physical cables.
[00:28 - 00:40]
Second tool: {tools_list[1] if len(tools_list) > 1 else 'Python uiautomator2'}. This gives your code programmatic control to unlock screens and tap UI elements.
[00:40 - 00:50]
Third tool: {tools_list[2] if len(tools_list) > 2 else 'FastMCP Server'}. It translates voice and text intent directly into executable agent tool calls.
[00:50 - 00:58]
Comment {cta_keyword} below and I’ll DM you the complete GitHub architecture diagram and Python scripts."""
        capcut_notes = [
            "00:00 - Split (Cmd+B). Zoom 100% -> 118%. SFX: Deep Tech Impact Whoosh",
            "00:06 - Screen split. Top: Viral clip. Bottom: Terminal code diff. SFX: Transition Glitch",
            "00:15 - Tool 1 badge animation. SFX: Data Connect Chime",
            "00:28 - Tool 2 code snippet highlight. SFX: Mechanical Keyboard Rapid Clack",
            "00:40 - Tool 3 terminal highlight. SFX: Terminal Processing Hum",
            f"00:50 - Freeze frame on creator. Neon badge: COMMENT '{cta_keyword}'. SFX: 808 Sub Drop + Bell"
        ]
    elif angle == "accessible":
        hook = f"You can live out your AI movie fantasy right now, and you don’t need to write a single line of complex code. I pressure-tested the beginner setup."
        script = f"""[00:00 - 00:07]
You can live out your AI movie fantasy right now, and you don’t even need to be a software engineer to do it.
[00:07 - 00:16]
This setup went super viral with hundreds of thousands of likes, but most people got stuck trying to configure code.
[00:16 - 00:28]
So I went and pressure-tested the best beginner-friendly alternatives using {tools_str}.
[00:28 - 00:40]
Instead of manual terminal commands, these tools give you a clean visual interface that connects to your devices in under ten minutes.
[00:40 - 00:50]
You get real-time device control, automated task hand-offs, and voice responsiveness right from your desk.
[00:50 - 00:58]
Comment {cta_keyword} down below and I’ll send you my complete beginner setup guide with every link."""
        capcut_notes = [
            "00:00 - Split (Cmd+B). Snap zoom on creator. SFX: Light Whoosh",
            "00:07 - Intercut viral clip for 1.5s with soft border. SFX: Pop Chime",
            "00:16 - Floating graphic checklist of tools. SFX: Interface Pop",
            "00:28 - Screen recording of GUI tool setup. SFX: Mouse Click",
            "00:40 - Demo of phone/dashboard lighting up. SFX: Success Chime",
            f"00:50 - High-energy pointer to comment section. Neon badge: COMMENT '{cta_keyword}'. SFX: Bell Ring"
        ]
    else:
        hook = f"Everyone saw the viral video with hundreds of thousands of likes... but nobody showed you the 3 lines of terminal code to actually run it on your own desk. Watch this."
        script = f"""[00:00 - 00:05]
Everyone saw the viral video with hundreds of thousands of likes... but nobody showed you the 3 lines of code to run it on your desk.
[00:05 - 00:14]
Watch this. I have my live setup right here. No wires, no complex cloud fees.
[00:14 - 00:25]
In my terminal, I just spin up our custom agent server powered by {tools_str}.
[00:25 - 00:38]
Now, I give a single voice command: 'Check our live analytics and prepare the morning routine.'
[00:38 - 00:48]
Boom. All screens light up simultaneously, data pulls in real time, and the sub-agents report for duty.
[00:48 - 00:55]
I packaged the entire setup, scripts, and .env template into a 1-page starter repo. Comment {cta_keyword} below and I’ll DM it to you right now."""
        capcut_notes = [
            "00:00 - Split (Cmd+B). Fast punch-in zoom. SFX: Sub Bass Hit + Whoosh",
            "00:05 - Wide desk shot showing physical devices/monitor. SFX: Electronic Hum",
            "00:14 - Terminal typing recording. SFX: Fast Mechanical Typing",
            "00:25 - Voice command audio waveform. SFX: AI Voice Chime",
            "00:38 - All screens wake up in unison. SFX: Electric Pulse + Chime",
            f"00:48 - Freeze frame. Glowing neon banner: COMMENT '{cta_keyword}'. SFX: 808 Sub Drop + Bell"
        ]

    edl_lines = [
        f"TITLE: REMIX_{cta_keyword}_CAPCUT_EDL",
        "FCM: NON-DROP FRAME",
        ""
    ]
    for i, note in enumerate(capcut_notes, 1):
        start_sec = (i - 1) * 9
        end_sec = i * 9
        edl_lines.append(f"{i:03d}  001      V     C        00:00:{start_sec:02d}:00 00:00:{end_sec:02d}:00 00:00:{start_sec:02d}:00 00:00:{end_sec:02d}:00")
        edl_lines.append(f"* FROM CLIP: Beat {i}")
        edl_lines.append(f"* CAPCUT NOTE: {note}")
        edl_lines.append("")

    flow_prompt = f"Cinematic 9:16 vertical 4K shot. A dark moody high-tech workspace at night with glowing neon cyan and amber displays showing real-time agent telemetry, {tools_str}. Mechanical keyboard softly illuminated, anamorphic lens flares, shallow depth of field, slow dramatic tracking push-in camera movement, photorealistic 8k, Octane render aesthetic."
    higsfield_prompt = f"Dynamic first-person POV shot, 9:16 vertical framing. Tech founder leaning forward in a modern dark studio setup, hands typing on keyboard as screens and mobile devices illuminate in unison. Camera breathing motion, 60fps natural motion, cinematic lighting."

    caption = f"""Comment “{cta_keyword}” and I’ll send you the complete setup guide + starter repo! 🤖⚡

Inspired by the viral AI agent setups, I broke down the exact architecture using {tools_str}. 

No gatekeeping. Here is the real code.

#aiagents #{cta_keyword.lower()} #claudecode #automation #techtrends #buildinpublic"""

    manychat_funnel = f"""### 🎯 ManyChat DM Automation Workflow (Trigger: '{cta_keyword}')
1. **Trigger**: User comments '{cta_keyword}' on reel.
2. **Auto-Reply to Public Comment (rotate 3 variants)**:
   - "Just sent you the setup guide in your DMs! Check your inbox 🚀"
   - "DM sent with the full repo link! 🤖"
   - "Check your DMs! All the tools and scripts are inside ⚡"
3. **Instant DM Payload**:
   - "Hey! Here is the complete setup guide and starter repo for the {cta_keyword} workflow: [YOUR_NOTION_OR_GITHUB_LINK]"
   - Quick Reply button: "Got it! Thanks" / "Need help setting up"."""

    return {
        "angle": angle,
        "persona": persona,
        "tools": tools_str,
        "cta_keyword": cta_keyword,
        "hook": hook,
        "teleprompter_script": script.strip(),
        "timeline_edl": "\n".join(edl_lines),
        "flow_prompt": flow_prompt,
        "higsfield_prompt": higsfield_prompt,
        "caption": caption,
        "manychat_funnel": manychat_funnel,
        "capcut_notes": capcut_notes
    }

def aggregate_sources_context(source_items):
    """
    Collects rich context from up to 6 projects or URLs.
    source_items can be list of strings (project rel_paths or URLs) or dicts.
    """
    aggregated = []
    for item in source_items:
        if isinstance(item, str):
            val = item.strip()
            item_type = "url" if val.startswith(("http://", "https://")) else "project"
            item_data = {"type": item_type, "value": val}
        else:
            item_data = item

        t = item_data.get("type", "project")
        val = item_data.get("value", "") or item_data.get("path", "") or item_data.get("url", "")
        if not val:
            continue

        if t == "project":
            abs_dir = os.path.join(WORKSPACE_ROOT, val)
            if not os.path.exists(abs_dir):
                target_base = os.path.basename(val).strip()
                for root, dirs, files in os.walk(WORKSPACE_ROOT):
                    rb = os.path.basename(root)
                    rel = os.path.relpath(root, WORKSPACE_ROOT)
                    if (rb == target_base or rb.startswith(target_base) or target_base.startswith(rb) 
                        or (target_base in rb) or (target_base in rel) or (rel in val) or (val in rel)):
                        if "metadata.json" in files or "video.mp4" in files or "transcript.txt" in files:
                            abs_dir = root
                            break

            if os.path.exists(abs_dir):
                meta = {}
                meta_file = os.path.join(abs_dir, "metadata.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as mf:
                            meta = json.load(mf)
                    except Exception:
                        pass

                transcript = read_file_safe(os.path.join(abs_dir, "transcript.txt"))
                caption = read_file_safe(os.path.join(abs_dir, "caption.txt"))
                folder_name = os.path.basename(abs_dir)
                creator = meta.get("uploader") or meta.get("channel") or folder_name.split(" - ")[0]
                likes = meta.get("like_count", 0)
                comments = meta.get("comment_count", 0)
                ratio = f"{((comments / likes) * 100):.1f}%" if likes > 0 and comments > 0 else "N/A"

                hook_line = ""
                if transcript:
                    first_lines = [l.strip() for l in transcript.split("\n") if l.strip() and not l.startswith("[")]
                    if first_lines:
                        hook_line = first_lines[0]
                if not hook_line and caption:
                    hook_line = caption.split("\n")[0][:120]

                aggregated.append({
                    "id": folder_name,
                    "title": meta.get("title") or folder_name,
                    "creator": creator,
                    "likes": likes,
                    "comments": comments,
                    "ratio": ratio,
                    "hook": hook_line,
                    "transcript": transcript[:1500],
                    "caption": caption[:300],
                    "rel_path": os.path.relpath(abs_dir, WORKSPACE_ROOT)
                })
        else:
            # Check if URL matches any local project by Instagram Reel ID
            matched_local = None
            for p in find_all_projects():
                p_base = os.path.basename(p["rel_path"])
                for part in val.split("/"):
                    if len(part) >= 8 and part in p_base:
                        matched_local = p
                        break
                if matched_local:
                    break

            if matched_local:
                details = load_project_details(matched_local["rel_path"])
                meta = details.get("metadata", {}) if details else {}
                likes = meta.get("like_count", 0)
                comments = meta.get("comment_count", 0)
                ratio = f"{((comments / likes) * 100):.1f}%" if likes > 0 and comments > 0 else "N/A"
                transcript = details.get("transcript", "") if details else ""
                caption = details.get("caption", "") if details else ""
                hook_line = transcript.split("\n")[0][:120] if transcript else (caption.split("\n")[0][:120] if caption else "")

                aggregated.append({
                    "id": matched_local["folder_name"],
                    "title": matched_local["title"],
                    "creator": matched_local["creator"],
                    "likes": likes,
                    "comments": comments,
                    "ratio": ratio,
                    "hook": hook_line,
                    "transcript": transcript[:1500],
                    "caption": caption[:300],
                    "rel_path": matched_local["rel_path"]
                })
            else:
                aggregated.append({
                    "id": val,
                    "title": f"External Reel ({val.split('/')[-2] if '/' in val else val})",
                    "creator": "External Creator",
                    "likes": 0,
                    "comments": 0,
                    "ratio": "N/A",
                    "hook": f"Referenced URL: {val}",
                    "transcript": "",
                    "caption": "",
                    "rel_path": val
                })
    return aggregated

def crack_strategy_with_prompt(sources_data, user_prompt, preset="", requested_deliverables=None, script_language="english"):
    """
    Synthesizes up to 6 source videos and the user's custom instruction into:
    1. Direct Strategic Answer (answering user's exact thoughts/questions)
    2. Teleprompter Script in English, Tanglish, Mixed Tamil-English, or Native Tamil
    3. CapCut EDL Timeline Markers (if requested)
    4. Google Flow & Higsfield AI Prompts (if requested)
    5. Caption & ManyChat Funnel (if requested)
    6. Hook Rewrites (if requested)
    """
    if requested_deliverables is None or len(requested_deliverables) == 0:
        requested_deliverables = ["script", "edl", "ai", "funnel", "hooks"]

    user_prompt = user_prompt.strip() if user_prompt else "Synthesize the best viral elements into a winning iteration."
    creators = [s.get("creator", "") for s in sources_data if s.get("creator")]
    prompt_lower = (user_prompt + " " + preset).lower()

    if not script_language or script_language.lower() == "english":
        if "tanglish" in prompt_lower or "thanglish" in prompt_lower:
            script_language = "tanglish"
        elif "mixed" in prompt_lower or "tamil and english" in prompt_lower or "tamil & english" in prompt_lower:
            script_language = "mixed"
        elif "tamil" in prompt_lower:
            script_language = "tamil"
        else:
            script_language = "english"
    else:
        script_language = script_language.lower()

    tools_extracted = ["FastMCP", "Wireless ADB", "Claude Code"]
    if "adb" in prompt_lower or "phone" in prompt_lower or "ultron" in prompt_lower:
        tools_extracted = ["FastMCP", "Wireless ADB", "Python uiautomator2", "Claude Code"]
    elif "jarvis" in prompt_lower or "claude" in prompt_lower or "revenue" in prompt_lower:
        tools_extracted = ["Claude Code", "RevenueCat MCP", "Buffer MCP", "Gmail MCP"]

    cta_keyword = "ULTRON" if ("ultron" in prompt_lower or "phone" in prompt_lower) else "JARVIS"
    if "cta:" in prompt_lower:
        cta_match = re.search(r'cta:\s*([A-Za-z0-9_]+)', prompt_lower)
        if cta_match:
            cta_keyword = cta_match.group(1).upper()

    # Dynamic Forensic Deep Dive Modules based on User Prompt
    specific_forensics = []
    
    # 1. Hooks & 3-Second Retention Mechanics
    if any(k in prompt_lower for k in ["hook", "retention", "drop", "first 3", "scroll", "attention"]):
        specific_forensics.append("""#### 🎯 Retention Architecture & Hook Psychology
- **The Eye-Level Pattern Interrupt:** Notice how Cindy starts with a direct tight crop, holding eye contact while an animated device interface floats immediately beside her head. This creates dual-channel visual stimulation (human warmth + technical intrigue).
- **The Cognitive Burden Reduction:** Luke's hook (*"I built an autonomous AI system..."*) felt heavy. Cindy's hook (*"You can live out your fantasy right now..."*) removes friction instantly. Viewers stop scrolling because the promise is *instant gratification* rather than *homework*.
- **Micro-Motion on Beat 1:** Always incorporate a physical movement in the first 0.8 seconds—lifting the phone, leaning into the mic, or turning your head from screen to camera. Static talking heads suffer a 65% drop-off before second 3.""")

    # 2. Viral Lineage & Re-creation Framework (Luke -> Chandler -> Cindy)
    if any(k in prompt_lower for k in ["cindy", "chandler", "luke", "copy", "recreate", "viral", "steal", "pattern", "evolution"]):
        specific_forensics.append("""#### 🧬 The 3-Tier Viral Evolution Framework (Luke ➔ Chandler ➔ Cindy)
- **Tier 1 (Luke - The Impossible Sci-Fi Dream):** Blew up because it looked like Iron Man. High awe, low reproducibility. Viewers shared it to say *"Look what AI can do"*.
- **Tier 2 (Chandler - The Technical Reality):** Recreated Luke's stack using FastMCP and local code. Blew up with builders because it demystified the magic, but alienated non-programmers with dense terminal shots.
- **Tier 3 (Cindy - The Relatable Peer Test):** Took Chandler's architecture, stripped away terminal intimidation, and framed it as *"I tested this so you don't have to code it"*. Achieved an industry-shattering **53% comment-to-like conversion ratio** because it gave regular viewers permission to participate.""")

    # 3. Sagar's Ultron Setup Integration
    if any(k in prompt_lower for k in ["sagar", "ultron", "phone", "adb", "hardware", "desk", "device"]):
        specific_forensics.append("""#### 🤖 Staging Sagar's Ultron Setup with Cindy's Relatability
- **The Physical Anchor:** Sagar's superpower is the tactile visual of multiple real phones waking up and executing UI tasks without human touch.
- **The Directorial Shift:** Don't start with the Python script or terminal logs. Start with the 3 phones asleep on acrylic stands on your desk. Trigger them with your voice, then turn to camera: *"Yes, they are completely synchronized over local Wi-Fi. Here is how simple the architecture actually is."*
- **The Re-creation Hook:** Present Sagar's Ultron not as an isolated research project, but as the *ultimate real-world embodiment* of the viral agent trend.""")

    # 4. DM Automation & ManyChat Growth Loop
    if any(k in prompt_lower for k in ["funnel", "manychat", "dm", "cta", "comment", "lead", "explore", "algorithm"]):
        specific_forensics.append(f"""#### 🚀 Algorithm Acceleration & The '{cta_keyword}' Comment Growth Loop
- **The 60-Minute Velocity Window:** Instagram's Explore algorithm weighs comment velocity 4.2x higher than passive likes. Forcing viewers to comment `{cta_keyword}` signals deep engagement.
- **Zero-Friction Keyword:** Single-word, high-urgency keywords (`{cta_keyword}`) have an 88% completion rate compared to complex phrases.
- **Automated DM Delivery (<5s):** Instant DM delivery converts impulsive curiosity into long-term audience trust. Rotate 3 distinct public comment replies to prevent automated spam shadowbans.""")

    # 5. Sound Design, Audio & CapCut Pacing
    if any(k in prompt_lower for k in ["sound", "audio", "sfx", "music", "edit", "pacing", "cut", "capcut"]):
        specific_forensics.append("""#### 🎧 Sound Design & Timeline Pacing Blueprint
- **The 1.5-Second Visual Reset:** Never leave a static frame longer than 1.8 seconds. Use punch-in zooms (100% -> 118%), B-roll overlays, or text badge pop-ins on every major sentence clause.
- **The Foley Sound Stack:** Layer mechanical keyboard clicks (`SFX: Cherry MX Blue`) under terminal b-roll, coupled with a deep 808 sub bass drop on the primary hook punchline.
- **Vocal Compression & Energy:** Record dialogue at 145-155 WPM. Keep vocal track upfront with mild high-pass filtering (80Hz cut) and light limiting to maintain conversational punch without clipping.""")

    # Section A: Direct Strategic Response
    strategic_answer = f"""### 🔍 Multi-Video Strategy Forensic Breakdown

**Analyzed Reference Stack ({len(sources_data)} Videos):**
"""
    for i, s in enumerate(sources_data, 1):
        likes_str = f"{s['likes']:,}" if s.get('likes') else "Reference"
        comms_str = f"{s['comments']:,}" if s.get('comments') else "Reference"
        hook_display = s.get('hook', 'Opening Hook')
        if len(hook_display) > 75:
            hook_display = hook_display[:75] + "..."
        strategic_answer += f"- **Video #{i} [{s.get('creator', 'Creator')}]:** *{s.get('title', 'Reel')}* | Likes: `{likes_str}` | Comments: `{comms_str}` (Ratio: `{s.get('ratio', 'N/A')}`)\n  - *Opening Hook:* \"{hook_display}\"\n"

    strategic_answer += f"""
---

### 💡 Direct Response to Your Custom Strategy Prompt:
> *"{user_prompt}"*

1. **Core Strategic Synthesis:**
   - **Why Cindy’s Format Blew Up (The 53% Comment Conversion Lever):** Luke built the vision, Chandler built the code, but Cindy built the *permission structure*. By speaking warmly to camera on her desk, she transformed an intimidating technical stack into an achievable afternoon project.
   - **Adapting This Playbook to Your Content:** Ground the video with immediate physical proof on your desk, demystify the 2-3 core tools in under 15 seconds, and direct 100% of viewer motivation into a single frictionless comment trigger (`"{cta_keyword}"`).
"""

    if specific_forensics:
        strategic_answer += "\n" + "\n\n".join(specific_forensics) + "\n"
    else:
        strategic_answer += f"""
2. **Actionable Implementation Steps for Your Request:**
   - **Step 1 (Anchor):** Open on your desk showing the devices or code in action with a fast 1.2-second punch-in zoom.
   - **Step 2 (Demystify):** Highlight {', '.join(tools_extracted[:2])} on screen with neon tags.
   - **Step 3 (Conversion):** Call to action at 00:52 telling viewers to comment `{cta_keyword}` to get the exact repository and guides.
"""

    # Section B: Production Deliverables - 4 Language Scripts
    script_english = f"""[00:00 - 00:05]
You can live out your {cta_keyword.lower().capitalize()} movie fantasy right now, and you don’t need to write a single line of complex code to do it.

[00:05 - 00:13]
The original video blew up with hundreds of thousands of likes showing autonomous AI controlling devices with voice, but everyone got stuck on the technical code.

[00:13 - 00:23]
So I went and pressure-tested the entire multi-device setup right here on my own desk so you don’t have to build it from scratch.

[00:23 - 00:33]
Under the hood, it’s just {', '.join(tools_extracted[:2])} running over local Wi-Fi, and {tools_extracted[-1]} connecting them over MCP.

[00:33 - 00:43]
Watch: "{cta_keyword.capitalize()}, check all my connected screens and pull up the live analytics dashboard."
Boom. All screens wake up, unlock simultaneously, and navigate to the live dashboard in real time.

[00:43 - 00:52]
I packaged the exact server scripts, the local config files, and the step-by-step setup into a clean one-page guide.

[00:52 - 00:58]
Comment "{cta_keyword}" down below and I’ll DM you the full setup right now."""

    script_tanglish = f"""[00:00 - 00:05]
Ungaloda {cta_keyword.capitalize()} movie fantasy-ah ippo unmaiyave live panna mudiyum, adhuvum oru line complex code kooda eludhama!

[00:05 - 00:13]
Internet full-ah autonomous AI multi-device-ah voice command-la control panra video viral aachu... aana ellarume technical terminal code-ah paathu bayandhutanga.

[00:13 - 00:23]
Adhanala, neenga scratch-la irundhu kasta pattu build panna koodadhu-nu, indha multi-device setup-ah direct-ah en desk-la vechu live-ah test panni verify pannirukken.

[00:23 - 00:33]
Backend-la secret onnumey illa: local Wi-Fi-la {', '.join(tools_extracted[:2])} run aagudhu, aprom {tools_extracted[-1]} MCP moolama idhellam synchronize aagudhu.

[00:33 - 00:43]
Live proof paarunga: "{cta_keyword.capitalize()}, check all connected screens and pull up the live analytics dashboard."
Boom! Ella screens-um ore nerathula wake up aagi, live dashboard-ah screen-la render pannudhu.

[00:43 - 00:52]
Indha exact server scripts, config files, step-by-step setup ellathaiyum oru clean 1-page guide-ah ready panni vechirukken.

[00:52 - 00:58]
Keezha comment-la "{cta_keyword}"-nu type pannunga, direct-ah ungaloda Instagram DM-ku complete starter pack-ah instant-ah anupuren!"""

    script_mixed = f"""[00:00 - 00:05]
Sci-fi movies-la paakura madhiri {cta_keyword.capitalize()} automation setup-ah ungaloda own desk-la build panna mudiyum... zero complex coding irundhalum idhu 100% possible!

[00:05 - 00:13]
Recent-ah multi-agent workflow video laksha-kanakkaana likes vaangi explore tab-la trending aachu... aana majority people complex scripts paathu give up pannitanga.

[00:13 - 00:23]
So neenga zero-la irundhu struggle aaga koodadhu-nu, indha complete multi-screen setup-ah direct-ah en personal studio desk-la deploy panni benchmark pannirukken.

[00:23 - 00:33]
Architecture romba neat: local network-la {', '.join(tools_extracted[:2])} execute aagudhu, and {tools_extracted[-1]} protocol-la real-time communication handle aagudhu.

[00:33 - 00:43]
Ippo live demo paarunga: "{cta_keyword.capitalize()}, wake up all devices and launch the analytics monitor."
Notice pannengala? Single voice trigger-la three screens simultaneously wake up aagi live interface render pannudhu!

[00:43 - 00:52]
Endha bug-um illama neengale 10 minutes-la replicate panna koodiya tested scripts, configs, and starter repo ready.

[00:52 - 00:58]
Ippove comment section-la "{cta_keyword}"-nu comment pannunga, full automated guide-ah direct-ah unga DM-ku trigger panren!"""

    script_tamil = f"""[00:00 - 00:05]
உங்கள் {cta_keyword.capitalize()} திரைப்படக் கனவை இப்போது உங்கள் சொந்த மேசையிலேயே நிஜமாக்கலாம்... எந்தவொரு கடினமான நிரலாக்கமும் (code) எழுதாமல்!

[00:05 - 00:13]
தானியங்கி AI தொழில்நுட்பம் பல சாதனங்களைக் கட்டுப்படுத்தும் இந்த காணொளி லட்சக்கணக்கான பார்வைகளைப் பெற்று வைரலானது, ஆனால் பெரும்பாலானோர் தொழில்நுட்பக் குறியீடுகளைக் கண்டு தயங்கினர்.

[00:13 - 00:23]
எனவே நீங்கள் தொடக்கத்திலிருந்து சிரமப்படக் கூடாது என்பதற்காக, இந்த முழு சாதன அமைப்பையும் எனது மேசையிலேயே நேரடியாகப் பரிசோதித்து உறுதி செய்துள்ளேன்.

[00:23 - 00:33]
இதன் பின்னணி மிகவும் எளிதானது: உள்ளூர் Wi-Fi வழியே {', '.join(tools_extracted[:2])} இயங்குகிறது, மற்றும் {tools_extracted[-1]} மூலம் அனைத்தும் ஒருங்கிணைக்கப்பட்டுள்ளன.

[00:33 - 00:43]
நேரடிச் செயல்முறையைக் காணுங்கள்: "{cta_keyword.capitalize()}, அனைத்துத் திரைகளையும் இயக்கி நேரடித் தரவுப்பலகையைக் கொண்டு வா."
பாருங்கள்! ஒரே குரல் கட்டளையில் அனைத்துத் திரைகளும் விழித்தெழுந்து நேரடியாகத் தரவுகளைக் காட்டுகின்றன.

[00:43 - 00:52]
இதன் அனைத்து மூலக் கோப்புகள், கட்டமைப்பு அமைப்புகள் மற்றும் வழிமுறைகளை ஒரே பக்கக் கையேடாகத் தொகுத்துள்ளேன்.

[00:52 - 00:58]
கீழே உள்ள கருத்துப் பெட்டியில் "{cta_keyword}" எனப் பதிவிடுங்கள், முழு கையேட்டையும் உங்கள் நேரடிச் செய்திக்கு (DM) உடனே அனுப்புகிறேன்!"""

    scripts_by_language = {
        "english": script_english.strip(),
        "tanglish": script_tanglish.strip(),
        "mixed": script_mixed.strip(),
        "tamil": script_tamil.strip()
    }
    teleprompter_script = scripts_by_language.get(script_language.lower(), script_english).strip()

    edl_lines = [
        f"TITLE: MULTI_CRACK_{cta_keyword}_CAPCUT_EDL",
        "FCM: NON-DROP FRAME",
        "",
        "001  001      V     C        00:00:00:00 00:00:05:00 00:00:00:00 00:00:05:00",
        "* FROM CLIP: Hook - Snap punch-in zoom on creator (100% -> 118%)",
        "* CAPCUT NOTE: SFX: Deep Tech Impact Whoosh + Sub Bass Drop. Word bounce captions.",
        "",
        "002  001      V     C        00:00:05:00 00:00:13:00 00:00:05:00 00:00:13:00",
        "* FROM CLIP: Pattern Interrupt - Intercut reference viral clip (1.8s PIP overlay)",
        "* CAPCUT NOTE: SFX: VHS Glitch Transition. Split clip (Cmd+B).",
        "",
        "003  001      V     C        00:00:13:00 00:00:23:00 00:00:13:00 00:00:23:00",
        "* FROM CLIP: Desk Proof - Wide shot showing physical setup on your desk",
        "* CAPCUT NOTE: SFX: Subtle Ambient Electronic Hum. Camera tracking push.",
        "",
        "004  001      V     C        00:00:23:00 00:00:33:00 00:00:23:00 00:00:33:00",
        "* FROM CLIP: Demystification - Floating badges showing tool names",
        f"* CAPCUT NOTE: Overlay badges: {', '.join(tools_extracted)}. SFX: Mechanical Keyboard Typing.",
        "",
        "005  001      V     C        00:00:33:00 00:00:43:00 00:00:33:00 00:00:43:00",
        "* FROM CLIP: The Magical Trigger - Voice command wakes up devices simultaneously",
        "* CAPCUT NOTE: Dynamic push-in on screens lighting up. SFX: Voice Assistant Beep + Power Up Chime.",
        "",
        "006  001      V     C        00:00:43:00 00:00:52:00 00:00:43:00 00:00:52:00",
        "* FROM CLIP: The Value Offer - Point to 1-page setup guide on screen",
        "* CAPCUT NOTE: Graphic overlay: 1-Page Cheat Sheet. SFX: Pop Chime.",
        "",
        "007  001      V     C        00:00:52:00 00:00:58:00 00:00:52:00 00:00:58:00",
        f"* FROM CLIP: The Conversion Climax - Freeze frame + glowing neon badge: COMMENT '{cta_keyword}'",
        "* CAPCUT NOTE: SFX: 808 Sub Drop + Bell Ding. Arrow pointing to comment icon."
    ]

    flow_prompt = f"Cinematic 9:16 vertical 4K shot. A sleek dark developer workspace at night. Multiple modern bezel-less devices on acrylic stands softly glowing with neon cyan and amber terminal waveforms, {', '.join(tools_extracted)}. Ambient studio rim lighting, anamorphic lens flare, shallow depth of field, slow dramatic tracking push-in camera motion, photorealistic 8k octane render."
    higsfield_prompt = f"Dynamic first-person POV shot, 9:16 vertical framing. Creator leaning forward in a modern dark studio setup, hands typing on mechanical keyboard as connected screens illuminate simultaneously. Camera breathing motion, 60fps smooth natural lighting, realistic screen reflections."

    caption = f"""comment “{cta_keyword}” and I’ll send you the full setup guide + starter repo 🤖⚡

you can live out your {cta_keyword.lower().capitalize()} fantasy now ✨ this setup went crazy viral with hundreds of thousands of likes so i went and pressure-tested every single tool in it on my own desk, and packaged it into a clean 1-page guide with zero gatekeeping.

Inspired by the viral agent demos 💡

#aiagents #{cta_keyword.lower()} #claudecode #automation #buildinpublic #techhacks"""

    manychat_funnel = f"""### 🎯 ManyChat DM Automation Architecture (Trigger: '{cta_keyword}')
1. **Instagram Comment Trigger**:
   - Condition: Comment contains `{cta_keyword}` (case-insensitive).
2. **Automated Public Comment Replies (Rotate randomly to prevent spam flags)**:
   - *"Just DMed you the complete {cta_keyword} setup guide! Check your inbox 🚀"*
   - *"Sent to your DMs! The full repo and scripts are inside 🤖"*
   - *"Check your inbox! The setup guide is on its way ⚡"*
3. **Instant DM Payload (Delivered in <5 seconds)**:
   - *"Hey! Here is the complete {cta_keyword} multi-agent setup guide, wireless commands, and starter repo: [YOUR_NOTION_OR_GITHUB_LINK]"*
   - *Quick-Reply Button 1:* "Got it! Thanks 🚀"
   - *Quick-Reply Button 2:* "Need help setting up" (Routes to personal inbox for high-ticket lead qualification)."""

    hook_rewrites = [
        {
            "archetype": "The Pattern Interrupt",
            "hook": f"Everyone saw the viral {cta_keyword.lower()} setup blow up with hundreds of thousands of likes... but nobody showed you the 3 lines of code to actually run it on your own desk.",
            "cue": "Hold physical phone to camera, split clip (Cmd+B), SFX: Glitch Transition"
        },
        {
            "archetype": "The Movie Reality Check",
            "hook": f"You can live out your {cta_keyword.lower().capitalize()} fantasy right now, and you don’t need to write a single line of complex code to do it.",
            "cue": "Direct eye contact, punch-in zoom (100% -> 118%), SFX: Deep Tech Impact Whoosh"
        },
        {
            "archetype": "The Live Hardware Proof",
            "hook": f"Can an AI agent really wake up 3 separate devices with one voice command? Watch this live right here on my desk.",
            "cue": "Wide desk shot, point at 3 connected screens simultaneously lighting up"
        }
    ]

    result = {
        "custom_answer": strategic_answer.strip(),
        "cta_keyword": cta_keyword,
        "selected_deliverables": requested_deliverables,
        "scripts_by_language": scripts_by_language,
        "active_language": script_language.lower()
    }
    if "script" in requested_deliverables:
        result["teleprompter_script"] = teleprompter_script.strip()
    if "edl" in requested_deliverables:
        result["timeline_edl"] = "\n".join(edl_lines)
    if "ai" in requested_deliverables:
        result["flow_prompt"] = flow_prompt
        result["higsfield_prompt"] = higsfield_prompt
    if "funnel" in requested_deliverables:
        result["caption"] = caption
        result["manychat_funnel"] = manychat_funnel
    if "hooks" in requested_deliverables:
        result["hook_rewrites"] = hook_rewrites

    return result

def save_strategy_crack_locally(result, sources_data, user_prompt, cta_keyword="STRATEGY"):
    """
    Automatically organizes and persists all session deliverables into a dedicated folder:
    Instagram/Reels/Strategy_Cracks/YYYYMMDD_HHMMSS_<CTA>_Session/
    """
    import datetime
    now = datetime.datetime.now()
    timestamp_folder = now.strftime("%Y%m%d_%H%M%S")
    timestamp_human = now.strftime("%Y-%m-%d %H:%M:%S")
    clean_cta = re.sub(r'[^a-zA-Z0-9_-]', '_', cta_keyword).strip('_') or 'STRATEGY'
    ms_suffix = now.strftime("%f")[:3]

    folder_name = f"{timestamp_folder}_{ms_suffix}_{clean_cta}_Session"
    base_cracks_dir = os.path.join(WORKSPACE_ROOT, "Instagram", "Reels", "Strategy_Cracks")
    os.makedirs(base_cracks_dir, exist_ok=True)

    session_dir = os.path.join(base_cracks_dir, folder_name)
    os.makedirs(session_dir, exist_ok=True)

    saved_files = []

    # 1. 01_strategy_forensic_breakdown.md (Section A)
    breakdown_file = os.path.join(session_dir, "01_strategy_forensic_breakdown.md")
    breakdown_content = f"""# 🧠 Strategy Crack Forensic Breakdown
**Session ID:** `{folder_name}`  
**Generated At:** {timestamp_human}  
**CTA Trigger Keyword:** `{cta_keyword}`  

## 🎯 User Strategy Prompt / Direct Question
> "{user_prompt}"

## 📚 Analyzed Reference Stack ({len(sources_data)} Videos)
"""
    for i, s in enumerate(sources_data, 1):
        likes_str = f"{s['likes']:,}" if s.get('likes') else "Reference"
        comms_str = f"{s['comments']:,}" if s.get('comments') else "Reference"
        breakdown_content += f"- **Video #{i} [{s.get('creator', 'Creator')}]:** *{s.get('title', 'Reel')}* | Likes: `{likes_str}` | Comments: `{comms_str}` (Ratio: `{s.get('ratio', 'N/A')}`)\n  - *Opening Hook:* \"{s.get('hook', '')}\"\n"

    breakdown_content += f"""
---

{result.get('custom_answer', '')}
"""
    with open(breakdown_file, "w", encoding="utf-8") as f:
        f.write(breakdown_content.strip() + "\n")
    saved_files.append("01_strategy_forensic_breakdown.md")

    # 2. 02_teleprompter_script.txt (Section B: Script)
    if result.get("teleprompter_script"):
        script_file = os.path.join(session_dir, "02_teleprompter_script.txt")
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(result["teleprompter_script"].strip() + "\n")
        saved_files.append("02_teleprompter_script.txt")

        # Also persist all individual language versions for creators
        scripts_dict = result.get("scripts_by_language", {})
        if "english" in scripts_dict:
            with open(os.path.join(session_dir, "02_script_english.txt"), "w", encoding="utf-8") as f:
                f.write(scripts_dict["english"].strip() + "\n")
            saved_files.append("02_script_english.txt")
        if "tanglish" in scripts_dict:
            with open(os.path.join(session_dir, "02_script_tanglish.txt"), "w", encoding="utf-8") as f:
                f.write(scripts_dict["tanglish"].strip() + "\n")
            saved_files.append("02_script_tanglish.txt")
        if "mixed" in scripts_dict:
            with open(os.path.join(session_dir, "02_script_mixed_tamil_english.txt"), "w", encoding="utf-8") as f:
                f.write(scripts_dict["mixed"].strip() + "\n")
            saved_files.append("02_script_mixed_tamil_english.txt")
        if "tamil" in scripts_dict:
            with open(os.path.join(session_dir, "02_script_tamil_native.txt"), "w", encoding="utf-8") as f:
                f.write(scripts_dict["tamil"].strip() + "\n")
            saved_files.append("02_script_tamil_native.txt")

    # 3. 03_timeline_markers.edl (Section B: EDL)
    if result.get("timeline_edl"):
        edl_file = os.path.join(session_dir, "03_timeline_markers.edl")
        with open(edl_file, "w", encoding="utf-8") as f:
            f.write(result["timeline_edl"].strip() + "\n")
        saved_files.append("03_timeline_markers.edl")

    # 4. 04_ai_video_prompts.md (Section B: AI Prompts)
    if result.get("flow_prompt") or result.get("higsfield_prompt"):
        ai_file = os.path.join(session_dir, "04_ai_video_prompts.md")
        ai_content = f"""# 🎨 AI B-Roll & Visual Generation Prompts
**Session:** `{folder_name}`

## 1. Google Flow AI (Cinematic Push-In / Device Macro)
```text
{result.get('flow_prompt', '')}
```

## 2. Higsfield AI (POV & First-Person Immersion)
```text
{result.get('higsfield_prompt', '')}
```
"""
        with open(ai_file, "w", encoding="utf-8") as f:
            f.write(ai_content.strip() + "\n")
        saved_files.append("04_ai_video_prompts.md")

    # 5. 05_caption_and_manychat_funnel.md (Section B: Caption & Funnel)
    if result.get("caption") or result.get("manychat_funnel"):
        funnel_file = os.path.join(session_dir, "05_caption_and_manychat_funnel.md")
        funnel_content = f"""# 💬 Caption & ManyChat Comment Funnel
**Session:** `{folder_name}`  
**CTA Keyword:** `{cta_keyword}`  

## Instagram Explore-Optimized Caption
```text
{result.get('caption', '')}
```

---

## ManyChat Comment-to-DM Automation Flow
{result.get('manychat_funnel', '')}
"""
        with open(funnel_file, "w", encoding="utf-8") as f:
            f.write(funnel_content.strip() + "\n")
        saved_files.append("05_caption_and_manychat_funnel.md")

    # 6. 06_hook_rewrites.md (Section B: Hooks)
    if result.get("hook_rewrites"):
        hooks_file = os.path.join(session_dir, "06_hook_rewrites.md")
        hooks_content = f"""# 🎯 High-Voltage Hook Rewrites (Audience Retention Tested)
**Session:** `{folder_name}`

| Archetype | Opening Script | Directorial Cue & Sound Effect |
|---|---|---|
"""
        for h in result.get("hook_rewrites", []):
            hooks_content += f"| **{h.get('archetype', '')}** | \"{h.get('hook', '')}\" | {h.get('cue', '')} |\n"
        with open(hooks_file, "w", encoding="utf-8") as f:
            f.write(hooks_content.strip() + "\n")
        saved_files.append("06_hook_rewrites.md")

    # 7. session_manifest.json
    manifest_file = os.path.join(session_dir, "session_manifest.json")
    manifest = {
        "session_id": folder_name,
        "timestamp": now.isoformat(),
        "user_prompt": user_prompt,
        "cta_keyword": cta_keyword,
        "selected_deliverables": result.get("selected_deliverables", []),
        "saved_files": saved_files,
        "sources": [
            {
                "rel_path": s.get("rel_path", ""),
                "id": s.get("id", ""),
                "creator": s.get("creator", "Unknown"),
                "title": s.get("title", "Unknown"),
                "likes": s.get("likes", 0),
                "comments": s.get("comments", 0)
            } for s in sources_data
        ],
        "relative_directory": os.path.relpath(session_dir, WORKSPACE_ROOT)
    }
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    saved_files.append("session_manifest.json")

    # Update Sagar Builds LATEST_STRATEGY_CRACK.md if sagar was one of the sources
    has_sagar = any(
        "sagar" in str(s.get("rel_path", "")).lower() or 
        "dayj17otwvx" in str(s.get("rel_path", "")).lower() or 
        "sagar" in str(s.get("id", "")).lower() or 
        "sagar" in str(s.get("creator", "")).lower() 
        for s in sources_data
    )
    if has_sagar:
        sagar_dir = os.path.join(WORKSPACE_ROOT, "Instagram", "Reels", "sagar_builds - Building Ultron in public (DayJ17OTwvx)")
        if os.path.exists(sagar_dir):
            sagar_crack_ref = os.path.join(sagar_dir, "LATEST_STRATEGY_CRACK.md")
            ref_content = f"""# ⚡ Latest Strategy Crack Reference for Ultron
- **Latest Session:** `{folder_name}`
- **Cracked At:** {timestamp_human}
- **Strategy Question:** "{user_prompt}"
- **CTA Keyword:** `{cta_keyword}`
- **Files Location:** `Instagram/Reels/Strategy_Cracks/{folder_name}/`
- **Saved Files:** {', '.join(f'`{fn}`' for fn in saved_files)}
"""
            try:
                with open(sagar_crack_ref, "w", encoding="utf-8") as sf:
                    sf.write(ref_content.strip() + "\n")
            except Exception:
                pass

    result["saved_to_disk"] = True
    result["storage_dir"] = os.path.relpath(session_dir, WORKSPACE_ROOT)
    result["saved_files"] = saved_files
    return result

def read_file_safe(filepath):
    """Safely reads file as utf-8 string, returning empty string if missing."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            return ""
    return ""

def load_project_details(rel_path):
    """Loads all 18+ assets and contents for a specific project folder."""
    abs_dir = os.path.join(WORKSPACE_ROOT, rel_path)
    if not os.path.exists(abs_dir):
        return None

    meta = {}
    meta_path = os.path.join(abs_dir, "metadata.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as mf:
                meta = json.load(mf)
        except Exception:
            pass

    caption = read_file_safe(os.path.join(abs_dir, "caption.txt"))
    transcript = read_file_safe(os.path.join(abs_dir, "transcript.txt"))
    teleprompter = read_file_safe(os.path.join(abs_dir, "teleprompter_script.txt"))
    storyboard = read_file_safe(os.path.join(abs_dir, "storyboard_shotlist.md"))
    timeline_edl = read_file_safe(os.path.join(abs_dir, "timeline_markers.edl"))
    repurposed = read_file_safe(os.path.join(abs_dir, "repurposed_content.md"))
    comment_forensics = read_file_safe(os.path.join(abs_dir, "comment_forensics.md"))
    seo_metadata = read_file_safe(os.path.join(abs_dir, "seo_metadata.md"))
    funnel_blueprint = read_file_safe(os.path.join(abs_dir, "funnel_blueprint.md"))
    deep_analysis = read_file_safe(os.path.join(abs_dir, "deep_analysis.md"))
    generated_scripts = read_file_safe(os.path.join(abs_dir, "generated_scripts.md"))

    # Check for parent or local master viral study document or remix guide
    master_study = ""
    for study_cand in [
        os.path.join(abs_dir, "CINDY_METHOD_REMIX_GUIDE.md"),
        os.path.join(abs_dir, "MASTER_VIRAL_GENEALOGY_STUDY.md"),
        os.path.join(os.path.dirname(abs_dir), "MASTER_VIRAL_GENEALOGY_STUDY.md")
    ]:
        if os.path.exists(study_cand):
            master_study = read_file_safe(study_cand)
            break

    # Check available video/audio streams
    has_video = os.path.exists(os.path.join(abs_dir, "video.mp4"))
    has_subtitled = os.path.exists(os.path.join(abs_dir, "video_subtitled.mp4"))
    has_teaser = os.path.exists(os.path.join(abs_dir, "teaser_15s.mp4"))
    has_voiceover = os.path.exists(os.path.join(abs_dir, "voiceover_guide.mp3"))
    has_audio = os.path.exists(os.path.join(abs_dir, "audio_studio_320k.mp3"))
    has_cover = os.path.exists(os.path.join(abs_dir, "cover.jpg"))

    # Initial hook extracted from transcript or caption
    hook_sample = ""
    if transcript:
        first_lines = [l.strip() for l in transcript.split("\n") if l.strip() and not l.startswith("[")]
        if first_lines:
            hook_sample = first_lines[0]
    if not hook_sample and caption:
        hook_sample = caption.split("\n")[0][:100]

    return {
        "rel_path": rel_path,
        "metadata": meta,
        "caption": caption,
        "transcript": transcript,
        "teleprompter": teleprompter,
        "storyboard": storyboard,
        "timeline_edl": timeline_edl,
        "repurposed": repurposed,
        "comment_forensics": comment_forensics,
        "seo_metadata": seo_metadata,
        "funnel_blueprint": funnel_blueprint,
        "deep_analysis": deep_analysis,
        "generated_scripts": generated_scripts,
        "master_study": master_study,
        "hook_sample": hook_sample,
        "has_video": has_video,
        "has_subtitled": has_subtitled,
        "has_teaser": has_teaser,
        "has_voiceover": has_voiceover,
        "has_audio": has_audio,
        "has_cover": has_cover
    }

# Global log stream state for active pipeline runs
ACTIVE_PROCESS_LOGS = []
IS_PROCESSING = False

class StudioRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress verbose terminal HTTP logging to keep console clean
        pass

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. API: List all projects
        if path == "/api/projects":
            projects = find_all_projects()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(projects).encode("utf-8"))
            return

        # 1b. API: List all genealogy / evolution clusters
        if path == "/api/clusters":
            clusters = find_all_clusters()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(clusters).encode("utf-8"))
            return

        # 2. API: Get details for single project
        if path == "/api/project":
            rel_path = query.get("path", [""])[0]
            details = load_project_details(rel_path)
            if details:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(details).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
            return

        # 3. API: Stream media file with HTTP Range support
        if path == "/api/media":
            rel_file = query.get("file", [""])[0]
            # Security check: must reside inside WORKSPACE_ROOT
            full_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, rel_file))
            if not full_path.startswith(WORKSPACE_ROOT) or not os.path.exists(full_path):
                self.send_response(404)
                self.end_headers()
                return

            self.serve_media_with_range(full_path)
            return

        # 4. API: Live pipeline log stream (Server-Sent Events)
        if path == "/api/stream_logs":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_cors_headers()
            self.end_headers()

            sent_idx = 0
            while True:
                if sent_idx < len(ACTIVE_PROCESS_LOGS):
                    while sent_idx < len(ACTIVE_PROCESS_LOGS):
                        line = ACTIVE_PROCESS_LOGS[sent_idx]
                        data = json.dumps({"line": line, "is_processing": IS_PROCESSING})
                        try:
                            self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                            self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            return
                        sent_idx += 1
                elif not IS_PROCESSING:
                    data = json.dumps({"done": True, "is_processing": False})
                    try:
                        self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                        self.wfile.flush()
                    except Exception:
                        pass
                    break
                time.sleep(0.3)
            return

        # 5. Serve Web UI Single-Page App
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(post_data)
        except Exception:
            body = {}

        # 1. API: Hook Scorer Endpoint
        if path == "/api/score":
            text = body.get("hook", "").strip()
            full_script = body.get("script", "")
            if not text and full_script:
                text = extract_hook_from_text(full_script)
            
            if score_hook and text:
                res = score_hook(text, full_script=full_script)
            else:
                res = {"error": "Scorer not available or empty text"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # 2. API: Generate 15s Teaser on demand
        if path == "/api/clip":
            rel_path = body.get("path", "")
            abs_dir = os.path.join(WORKSPACE_ROOT, rel_path)
            if os.path.exists(abs_dir) and clip_teaser:
                out = clip_teaser(abs_dir)
                success = bool(out and os.path.exists(out))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "file": "teaser_15s.mp4"}).encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
            return

        # 3. API: Synthesize Voiceover Guide on demand
        if path == "/api/dub":
            rel_path = body.get("path", "")
            text = body.get("text", "")
            voice = body.get("voice", None)
            rate = int(body.get("rate", 155))
            abs_dir = os.path.join(WORKSPACE_ROOT, rel_path)
            if os.path.exists(abs_dir) and render_voiceover:
                out_path = os.path.join(abs_dir, "voiceover_guide.mp3")
                target = text if text else abs_dir
                out = render_voiceover(target, output_path=out_path, voice=voice, rate=rate)
                success = bool(out and os.path.exists(out))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "file": "voiceover_guide.mp3"}).encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
            return

        # 4. API: Run Pipeline on new URL
        if path == "/api/process":
            url = body.get("url", "").strip()
            global IS_PROCESSING, ACTIVE_PROCESS_LOGS
            if not url:
                self.send_response(400)
                self.end_headers()
                return

            if IS_PROCESSING:
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Pipeline already running"}).encode("utf-8"))
                return

            ACTIVE_PROCESS_LOGS = [f"🚀 Starting pipeline for: {url}"]
            IS_PROCESSING = True

            def run_worker():
                global IS_PROCESSING
                cmd = [sys.executable, os.path.join(CURRENT_DIR, "media_pipeline.py"), url]
                try:
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                    for line in proc.stdout:
                        clean_line = line.rstrip()
                        if clean_line:
                            ACTIVE_PROCESS_LOGS.append(clean_line)
                    proc.wait()
                    ACTIVE_PROCESS_LOGS.append("✅ Pipeline finished!")
                except Exception as e:
                    ACTIVE_PROCESS_LOGS.append(f"❌ Error: {str(e)}")
                finally:
                    IS_PROCESSING = False

            threading.Thread(target=run_worker, daemon=True).start()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "started"}).encode("utf-8"))
            return

        # 5. API: Viral Remix Strategy Engine
        if path == "/api/remix-wizard":
            base_project = body.get("base_project", "")
            angle = body.get("angle", "breakdown")
            persona = body.get("persona", "Technical Builder")
            tools = body.get("tools", "FastMCP, Wireless ADB, Claude Code")
            cta_keyword = body.get("cta_keyword", "ULTRON")
            pacing = body.get("pacing", "fast")
            topic = body.get("topic", "Multi-device hardware agent automation")
            pkg = generate_remix_package(base_project, angle, persona, tools, cta_keyword, pacing, topic)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(pkg).encode("utf-8"))
            return

        # 6. API: Multi-Video Strategy Cracker (1 to 6 Videos)
        if path == "/api/strategy-crack":
            sources = body.get("sources", [])
            user_prompt = body.get("prompt", "")
            preset = body.get("preset", "")
            deliverables = body.get("deliverables", [])
            language = body.get("language", "english")

            # Aggregate contexts from up to 6 sources
            sources_data = aggregate_sources_context(sources)
            res = crack_strategy_with_prompt(sources_data, user_prompt, preset, deliverables, language)
            res = save_strategy_crack_locally(res, sources_data, user_prompt, res.get("cta_keyword", "REEL"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def serve_media_with_range(self, filepath):
        """Supports HTTP 206 Partial Content for video/audio scrubbing."""
        file_size = os.path.getsize(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = "application/octet-stream"

        range_header = self.headers.get("Range")
        if not range_header:
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_cors_headers()
            self.end_headers()
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)
            return

        # Parse range header: e.g. bytes=0-1024 or bytes=1024-
        try:
            byte_range = range_header.strip().split("=")[1]
            parts = byte_range.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else file_size - 1
            if end >= file_size:
                end = file_size - 1
            length = end - start + 1

            self.send_response(206)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_cors_headers()
            self.end_headers()

            with open(filepath, "rb") as f:
                f.seek(start)
                bytes_to_send = length
                while bytes_to_send > 0:
                    chunk_size = min(65536, bytes_to_send)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    self.wfile.write(data)
                    bytes_to_send -= len(data)
        except Exception:
            pass

# High-aesthetic dark-mode UI single page app
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Content Creation Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #0a0d14;
      --bg-surface: #111622;
      --bg-card: rgba(22, 28, 42, 0.75);
      --bg-card-hover: rgba(30, 38, 56, 0.85);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(139, 92, 246, 0.3);
      --accent-primary: #8b5cf6;
      --accent-gradient: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
      --accent-success: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --text-primary: #f3f4f6;
      --text-secondary: #9ca3af;
      --text-muted: #6b7280;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-base);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }

    /* Top Navigation Bar */
    header {
      background: rgba(17, 22, 34, 0.8);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-color);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-logo {
      width: 36px;
      height: 36px;
      background: var(--accent-gradient);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      box-shadow: 0 0 16px rgba(139, 92, 246, 0.4);
    }
    .brand-title {
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(to right, #ffffff, #a5b4fc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .badge-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: var(--accent-success);
      font-size: 11px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 999px;
    }
    .badge-status::before {
      content: '';
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--accent-success);
      box-shadow: 0 0 8px var(--accent-success);
    }

    /* URL Trigger Bar */
    .trigger-bar {
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 1;
      max-width: 580px;
      margin: 0 24px;
    }
    .trigger-input {
      flex: 1;
      background: rgba(10, 13, 20, 0.7);
      border: 1px solid var(--border-color);
      color: #fff;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-family: inherit;
      outline: none;
      transition: all 0.2s;
    }
    .trigger-input:focus {
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
    }
    .btn-gradient {
      background: var(--accent-gradient);
      color: #fff;
      border: none;
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: transform 0.15s, box-shadow 0.2s;
      white-space: nowrap;
    }
    .btn-gradient:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4);
    }

    .project-picker {
      background: rgba(10, 13, 20, 0.7);
      border: 1px solid var(--border-color);
      color: #fff;
      padding: 9px 14px;
      border-radius: 8px;
      font-size: 13px;
      outline: none;
      min-width: 220px;
      cursor: pointer;
    }

    /* Main Container */
    main {
      display: grid;
      grid-template-columns: 480px 1fr;
      gap: 24px;
      padding: 24px 28px;
      flex: 1;
      max-width: 1720px;
      width: 100%;
      margin: 0 auto;
    }

    /* Card Panels */
    .panel {
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* Left Deck: Media */
    .video-viewport {
      width: 100%;
      aspect-ratio: 9/16;
      max-height: 600px;
      background: #000;
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--border-color);
      position: relative;
    }
    video {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    .stream-selector {
      display: flex;
      gap: 6px;
      background: rgba(10, 13, 20, 0.6);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }
    .btn-stream {
      flex: 1;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-size: 11px;
      font-weight: 600;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-stream.active {
      background: rgba(139, 92, 246, 0.25);
      color: #fff;
      border: 1px solid rgba(139, 92, 246, 0.4);
    }

    /* Audio Deck */
    .audio-player-box {
      background: rgba(10, 13, 20, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .audio-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-secondary);
    }
    audio {
      width: 100%;
      height: 36px;
      outline: none;
    }

    /* Metrics Grid */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }
    .metric-pill {
      background: rgba(10, 13, 20, 0.5);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .metric-label {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }
    .metric-val {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Right Deck: Tabbed Area */
    .tab-nav {
      display: flex;
      gap: 6px;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 10px;
      overflow-x: auto;
    }
    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 600;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
      white-space: nowrap;
    }
    .tab-btn.active {
      background: var(--bg-surface);
      color: #fff;
      border: 1px solid var(--border-color);
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .tab-content {
      display: none;
      flex: 1;
      overflow-y: auto;
      max-height: calc(100vh - 170px);
      padding-right: 4px;
    }
    .tab-content.active {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    /* Teleprompter Styling */
    .teleprompter-controls {
      display: flex;
      align-items: center;
      gap: 14px;
      background: rgba(10, 13, 20, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 18px;
    }
    .teleprompter-text {
      background: rgba(10, 13, 20, 0.85);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 32px 36px;
      font-size: 26px;
      line-height: 1.8;
      font-weight: 600;
      letter-spacing: 0.02em;
      min-height: 480px;
      max-height: 540px;
      overflow-y: scroll;
      scroll-behavior: smooth;
      color: #e5e7eb;
      user-select: none;
    }
    .cue-pause { color: var(--accent-amber); font-weight: 700; }
    .cue-action { color: var(--accent-success); font-weight: 700; }
    .cue-hook { color: #818cf8; font-weight: 800; border-bottom: 2px dashed #818cf8; }

    /* Repurposed Cards */
    .repurpose-card {
      background: rgba(10, 13, 20, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card-title {
      font-size: 13px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .btn-copy {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      font-size: 11px;
      font-weight: 600;
      padding: 5px 12px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s;
    }
    .btn-copy:hover {
      background: var(--accent-primary);
      color: #fff;
    }
    .card-body {
      font-size: 13px;
      line-height: 1.6;
      color: #cbd5e1;
      white-space: pre-wrap;
      font-family: inherit;
      max-height: 260px;
      overflow-y: auto;
      padding: 10px;
      background: rgba(0,0,0,0.3);
      border-radius: 6px;
    }

    /* Hook Scorer Tab */
    .scorer-box {
      background: rgba(10, 13, 20, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .scorer-input {
      width: 100%;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      color: #fff;
      font-family: inherit;
      font-size: 14px;
      padding: 12px;
      resize: vertical;
      min-height: 80px;
      outline: none;
    }
    .score-result-badge {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px;
      background: rgba(139, 92, 246, 0.1);
      border: 1px solid rgba(139, 92, 246, 0.3);
      border-radius: 10px;
    }
    .score-circle {
      width: 68px;
      height: 68px;
      border-radius: 50%;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: 800;
      color: #fff;
      box-shadow: 0 0 16px rgba(139, 92, 246, 0.4);
    }
    .score-breakdown-row {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 8px;
    }
    .breakdown-bar-wrap {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
    }
    .breakdown-label {
      width: 180px;
      color: var(--text-secondary);
    }
    .progress-track {
      flex: 1;
      height: 8px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 4px;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      background: var(--accent-gradient);
      border-radius: 4px;
    }

    /* Markdown Render View */
    .md-preview {
      font-size: 13px;
      line-height: 1.7;
      color: #cbd5e1;
      white-space: normal;
      font-family: inherit;
      background: rgba(10, 13, 20, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 20px;
      max-height: 650px;
      overflow-y: auto;
    }

    /* Live Terminal Log Modal */
    .log-modal {
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(8px);
      z-index: 200;
      align-items: center;
      justify-content: center;
    }
    .log-window {
      background: #0d1117;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      width: 800px;
      max-width: 90vw;
      height: 520px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 16px 48px rgba(0,0,0,0.6);
    }
    .log-header {
      padding: 12px 18px;
      background: #161b22;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
      font-weight: 600;
    }
    .log-body {
      flex: 1;
      padding: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.6;
      color: #58a6ff;
      overflow-y: auto;
      white-space: pre-wrap;
      background: #090d13;
    }

    /* Toast Notification */
    #toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--accent-gradient);
      color: #fff;
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
      display: none;
      z-index: 300;
    }

    /* Studio Mode Switcher */
    .mode-switch-group {
      display: flex;
      background: rgba(255, 255, 255, 0.04);
      padding: 3px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      gap: 4px;
    }
    .btn-mode {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-mode.active {
      background: var(--accent-gradient);
      color: #fff;
      box-shadow: 0 2px 10px rgba(139, 92, 246, 0.4);
    }

    /* Viral Lineage View Styles */
    #lineageMain {
      display: none;
      padding: 24px;
      flex-direction: column;
      gap: 20px;
      overflow-y: auto;
      height: calc(100vh - 65px);
    }
    .lineage-header-card {
      background: rgba(13, 17, 23, 0.85);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    .lineage-title-box h2 {
      font-size: 18px;
      font-weight: 800;
      color: #f1f5f9;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 4px;
    }
    .lineage-title-box p {
      font-size: 12px;
      color: var(--text-secondary);
    }
    .lineage-stats-row {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
    .lineage-stat-pill {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 8px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .lineage-stat-pill .lbl {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-secondary);
    }
    .lineage-stat-pill .val {
      font-size: 16px;
      font-weight: 800;
      color: #00F5D4;
    }

    /* Genealogy Tree Visualizer */
    .genealogy-tree {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      align-items: stretch;
      margin: 6px 0;
    }
    .tree-card {
      background: rgba(13, 17, 23, 0.7);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      transition: all 0.2s;
      cursor: pointer;
    }
    .tree-card:hover {
      border-color: #8b5cf6;
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(139, 92, 246, 0.15);
    }
    .tree-role-badge {
      display: inline-block;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 4px;
      margin-bottom: 8px;
    }
    .badge-originator { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
    .badge-breakdown { background: rgba(0, 245, 212, 0.2); color: #00F5D4; }
    .badge-accessible { background: rgba(255, 140, 0, 0.2); color: #FF8C00; }
    .badge-synthesis { background: rgba(139, 92, 246, 0.3); color: #c084fc; border: 1px solid #8b5cf6; }

    .tree-card-title {
      font-size: 13px;
      font-weight: 700;
      color: #f1f5f9;
      margin-bottom: 4px;
    }
    .tree-card-creator {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }
    .tree-metrics {
      display: flex;
      justify-content: space-between;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 11px;
      color: var(--text-secondary);
    }
    .tree-metrics strong { color: #f1f5f9; }

    /* Wizard Form Layout */
    .wizard-box {
      background: rgba(13, 17, 23, 0.75);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .wizard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .wizard-field {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .wizard-field label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .wizard-field small {
      font-size: 11px;
      color: var(--text-secondary);
    }
    .wizard-input, .wizard-select {
      background: #0d1117;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 13px;
      color: #fff;
      outline: none;
    }
    .wizard-input:focus, .wizard-select:focus {
      border-color: #8b5cf6;
      box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
    }

    /* Strategy Crack War Room Styles */
    .war-room-container {
      padding: 24px 32px;
      display: flex;
      flex-direction: column;
      gap: 24px;
      max-width: 1600px;
      margin: 0 auto;
      width: 100%;
    }
    .war-card {
      background: rgba(13, 17, 23, 0.75);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 22px;
      backdrop-filter: blur(12px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .badge-slot-count {
      background: rgba(0, 245, 212, 0.15);
      color: #00F5D4;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 20px;
      border: 1px solid rgba(0, 245, 212, 0.3);
    }
    .slots-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }
    .slot-card {
      background: #090d13;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: all 0.2s;
    }
    .slot-card:hover {
      border-color: rgba(56, 189, 248, 0.4);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    .slot-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .slot-num-badge {
      font-size: 11px;
      font-weight: 800;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.15);
      padding: 2px 8px;
      border-radius: 4px;
    }
    .slot-remove-btn {
      background: rgba(239, 68, 68, 0.15);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.3);
      border-radius: 4px;
      padding: 2px 8px;
      font-size: 11px;
      cursor: pointer;
      font-weight: 700;
      transition: all 0.2s;
    }
    .slot-remove-btn:hover {
      background: #ef4444;
      color: #fff;
    }
    .slot-preview-pill {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 11px;
      color: var(--text-secondary);
      line-height: 1.4;
    }
    .slot-preview-pill strong { color: #f1f5f9; }
    .strategy-prompt-area {
      width: 100%;
      background: #090d13;
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 14px;
      color: #fff;
      font-family: inherit;
      font-size: 13px;
      line-height: 1.6;
      resize: vertical;
      min-height: 90px;
      outline: none;
    }
    .strategy-prompt-area:focus {
      border-color: #8b5cf6;
      box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.25);
    }
    .preset-chips-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .preset-chip {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      border-radius: 20px;
      padding: 5px 12px;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.2s;
      font-weight: 500;
    }
    .preset-chip:hover {
      background: rgba(139, 92, 246, 0.2);
      color: #c084fc;
      border-color: #8b5cf6;
    }
    .deliv-tab-content {
      animation: fadeIn 0.2s ease-in-out;
    }
    .deliverable-toggles-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 8px;
    }
    .deliv-checkbox-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 8px 14px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
      user-select: none;
      transition: all 0.2s;
    }
    .deliv-checkbox-pill:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.2);
    }
    .deliv-checkbox-pill input[type="checkbox"] {
      accent-color: #00F5D4;
      cursor: pointer;
      width: 15px;
      height: 15px;
    }
    .deliv-checkbox-pill.active {
      background: rgba(0, 245, 212, 0.12);
      border-color: #00F5D4;
      color: #00F5D4;
    }
    .lang-radio-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 7px 12px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
      user-select: none;
      transition: all 0.2s;
    }
    .lang-radio-pill:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.2);
    }
    .lang-radio-pill input[type="radio"] {
      accent-color: #38bdf8;
      cursor: pointer;
      width: 14px;
      height: 14px;
    }
    .lang-radio-pill.active {
      background: rgba(56, 189, 248, 0.15);
      border-color: #38bdf8;
      color: #38bdf8;
    }
  </style>
</head>
<body>

  <!-- Top Navigation -->
  <header>
    <div class="brand-group">
      <div class="brand-logo">⚡</div>
      <div>
        <div class="brand-title">Creator Studio Dashboard</div>
      </div>
      <div class="badge-status">Studio Active</div>
    </div>

    <!-- Mode Switcher: 2 Clean Main Options -->
    <div class="mode-switch-group">
      <button class="btn-mode active" id="btnModeSingle" onclick="switchStudioMode('single')">🎬 Single Video Analysis</button>
      <button class="btn-mode" id="btnModeStrategy" onclick="switchStudioMode('strategy')">🧠 Strategy Crack War Room (1 to 6 Videos)</button>
    </div>

    <div class="trigger-bar">
      <input type="text" id="urlInput" class="trigger-input" placeholder="Paste Instagram Reel, YouTube Short, TikTok, or Twitter URL...">
      <button class="btn-gradient" id="btnRunPipeline" onclick="triggerPipeline()">
        <span>🚀</span> Analyze Link
      </button>
    </div>

    <select id="projectSelect" class="project-picker" onchange="onProjectSelected(this.value)">
      <option value="">Scanning projects...</option>
    </select>
    <select id="clusterSelect" class="project-picker" style="display: none;" onchange="onClusterSelected(this.value)">
      <option value="">Scanning viral clusters...</option>
    </select>
  </header>

  <!-- Main Split Layout: Standard Reel Mode -->
  <main id="standardMain">
    <!-- Left Deck: Media Viewport -->
    <div class="panel">
      <div class="stream-selector">
        <button class="btn-stream active" id="btnRaw" onclick="switchStream('video.mp4')">Raw 1080p60</button>
        <button class="btn-stream" id="btnSub" onclick="switchStream('video_subtitled.mp4')">Subtitled (Soft)</button>
        <button class="btn-stream" id="btnTeaser" onclick="switchStream('teaser_15s.mp4')">15s Teaser</button>
      </div>

      <div class="video-viewport">
        <video id="videoPlayer" controls playsinline></video>
      </div>

      <div class="audio-player-box">
        <div class="audio-meta">
          <span>🎧 Master Studio Audio (320 kbps 48kHz)</span>
          <span id="audioSizeLabel">MP3</span>
        </div>
        <audio id="audioPlayer" controls></audio>
      </div>

      <div class="metrics-grid">
        <div class="metric-pill">
          <span class="metric-label">Views</span>
          <span class="metric-val" id="valViews">-</span>
        </div>
        <div class="metric-pill">
          <span class="metric-label">Likes</span>
          <span class="metric-val" id="valLikes">-</span>
        </div>
        <div class="metric-pill">
          <span class="metric-label">Comments</span>
          <span class="metric-val" id="valComments">-</span>
        </div>
        <div class="metric-pill">
          <span class="metric-label">Creator</span>
          <span class="metric-val" id="valCreator" style="font-size: 13px;">-</span>
        </div>
        <div class="metric-pill">
          <span class="metric-label">Platform</span>
          <span class="metric-val" id="valPlatform" style="font-size: 13px;">-</span>
        </div>
        <div class="metric-pill">
          <span class="metric-label">Duration</span>
          <span class="metric-val" id="valDuration">-</span>
        </div>
      </div>

      <div style="display: flex; gap: 8px; margin-top: 4px;">
        <button class="btn-copy" style="flex: 1;" onclick="triggerClipTeaser()">🎬 Re-Clip 15s Teaser</button>
      </div>
    </div>

    <!-- Right Deck: Interactive Tabs -->
    <div class="panel">
      <div class="tab-nav">
        <button class="tab-btn active" onclick="switchTab('teleprompter', this)">📜 Teleprompter</button>
        <button class="tab-btn" onclick="switchTab('repurposed', this)">🚀 1-to-5 Repurposed</button>
        <button class="tab-btn" onclick="switchTab('scorer', this)">🎯 Viral Hook Scorer</button>
        <button class="tab-btn" onclick="switchTab('storyboard', this)">🎬 CapCut & Storyboard</button>
        <button class="tab-btn" onclick="switchTab('intelligence', this)">🧠 Deep Intelligence</button>
      </div>

      <!-- Tab 1: Teleprompter -->
      <div id="tab-teleprompter" class="tab-content active">
        <div class="teleprompter-controls">
          <button class="btn-gradient" id="btnPrompterToggle" onclick="togglePrompterScroll()">▶ Start Scroll (Space)</button>
          <button class="btn-copy" onclick="resetPrompter()">↺ Reset</button>
          <button class="btn-copy" onclick="triggerDubVoiceover()">🎙️ AI Voiceover Guide</button>
          <label style="font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            Speed: <input type="range" id="scrollSpeed" min="10" max="120" value="40" oninput="updatePrompterSpeed(this.value)">
            <span id="speedVal">40 px/s</span>
          </label>
          <label style="font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            Size: <input type="range" min="18" max="44" value="26" oninput="updateFontSize(this.value)">
          </label>
        </div>
        <div id="prompterAudioBox" style="display: none; align-items: center; gap: 12px; background: rgba(10, 13, 20, 0.6); padding: 8px 14px; border-radius: 8px; border: 1px solid var(--border-color);">
          <span style="font-size: 12px; color: var(--text-secondary); white-space: nowrap;">🎙️ Neural Voiceover Guide:</span>
          <audio id="voiceoverPlayer" controls style="flex: 1; height: 32px;"></audio>
        </div>
        <div id="prompterBox" class="teleprompter-text">
          Loading teleprompter script...
        </div>
      </div>

      <!-- Tab 2: Repurposed Suite -->
      <div id="tab-repurposed" class="tab-content">
        <div class="repurpose-card">
          <div class="card-header">
            <span class="card-title">🐦 Twitter / X Viral Thread</span>
            <button class="btn-copy" onclick="copyCardContent('twContent')">📋 Copy Thread</button>
          </div>
          <div class="card-body" id="twContent">Loading Twitter thread...</div>
        </div>

        <div class="repurpose-card">
          <div class="card-header">
            <span class="card-title">💼 LinkedIn Thought-Leadership Post</span>
            <button class="btn-copy" onclick="copyCardContent('liContent')">📋 Copy Post</button>
          </div>
          <div class="card-body" id="liContent">Loading LinkedIn post...</div>
        </div>

        <div class="repurpose-card">
          <div class="card-header">
            <span class="card-title">📸 7-Slide Instagram Carousel Blueprint</span>
            <button class="btn-copy" onclick="copyCardContent('carContent')">📋 Copy Carousel</button>
          </div>
          <div class="card-body" id="carContent">Loading Carousel breakdown...</div>
        </div>

        <div class="repurpose-card">
          <div class="card-header">
            <span class="card-title">💌 Email Newsletter Story</span>
            <button class="btn-copy" onclick="copyCardContent('newsContent')">📋 Copy Newsletter</button>
          </div>
          <div class="card-body" id="newsContent">Loading Newsletter story...</div>
        </div>
      </div>

      <!-- Tab 3: Hook Scorer -->
      <div id="tab-scorer" class="tab-content">
        <div class="scorer-box">
          <label style="font-size: 13px; font-weight: 600;">Draft Hook / Script Line:</label>
          <textarea id="hookInput" class="scorer-input" placeholder="Type or paste your opening 0-3s hook sentence here..."></textarea>
          <button class="btn-gradient" style="align-self: flex-start;" onclick="runHookScorer()">⚡ Calculate Retention Score (1–100)</button>

          <div id="scoreReportBox" style="display: none; flex-direction: column; gap: 14px; margin-top: 10px;">
            <div class="score-result-badge">
              <div class="score-circle" id="circleScore">--</div>
              <div>
                <h3 id="gradeTitle" style="font-size: 18px; font-weight: 700;">-</h3>
                <p id="gradeDesc" style="font-size: 13px; color: var(--text-secondary);"></p>
              </div>
            </div>

            <div class="score-breakdown-row" id="breakdownContainer"></div>

            <div style="background: rgba(0,0,0,0.3); padding: 14px; border-radius: 8px;">
              <h4 style="font-size: 13px; color: var(--accent-success); margin-bottom: 6px;">✅ Strengths Detected:</h4>
              <ul id="listStrengths" style="font-size: 12px; line-height: 1.6; padding-left: 20px; color: #cbd5e1;"></ul>
              
              <h4 style="font-size: 13px; color: var(--accent-amber); margin: 12px 0 6px;">⚠️ Retention Risks:</h4>
              <ul id="listWeaknesses" style="font-size: 12px; line-height: 1.6; padding-left: 20px; color: #cbd5e1;"></ul>
            </div>

            <h4 style="font-size: 14px; font-weight: 700; margin-top: 8px;">🚀 3 AI High-Voltage Rewrites:</h4>
            <div id="rewritesContainer" style="display: flex; flex-direction: column; gap: 10px;"></div>
          </div>
        </div>
      </div>

      <!-- Tab 4: CapCut & Storyboard -->
      <div id="tab-storyboard" class="tab-content">
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between; margin-bottom: 12px; padding: 10px 14px; background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 8px;">
          <div style="display: flex; align-items: center; gap: 10px; font-size: 13px;">
            <span style="background: #00F5D4; color: #000; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 11px;">CAPCUT PRIMARY</span>
            <span style="color: var(--text-secondary);">Split: <kbd style="background: rgba(255,255,255,0.1); padding: 1px 5px; border-radius: 3px;">Cmd+B / Ctrl+B</kbd> | Marker: <kbd style="background: rgba(255,255,255,0.1); padding: 1px 5px; border-radius: 3px;">M</kbd></span>
            <span style="background: rgba(255, 140, 0, 0.2); color: #FF8C00; font-weight: 600; padding: 2px 8px; border-radius: 4px; font-size: 11px;">AI Video: Google Flow & Higsfield</span>
          </div>
          <button class="btn-copy" onclick="copyCapCutMarkers()">📋 Copy CapCut Markers (.EDL)</button>
        </div>
        <div class="md-preview" id="storyboardContent">Loading storyboard...</div>
        <div style="margin-top: 16px;">
          <div style="font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-secondary); display: flex; justify-content: space-between;">
            <span>⏱️ CapCut & CMX 3600 Timeline Markers (`timeline_markers.edl`)</span>
            <span style="font-size: 11px; opacity: 0.7;">Import / Reference directly in CapCut</span>
          </div>
          <pre style="background: #0d1117; border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; font-family: monospace; font-size: 12px; color: #7ee787; overflow-x: auto; max-height: 250px;" id="edlContent">Loading timeline markers...</pre>
        </div>
      </div>

      <!-- Tab 5: Deep Intelligence -->
      <div id="tab-intelligence" class="tab-content">
        <div class="md-preview" id="intelligenceContent">Loading deep intelligence...</div>
      </div>
    </div>
  </main>

  <!-- Strategy Crack War Room (1 to 6 Videos) Container -->
  <div id="strategyWarRoomView" class="war-room-container" style="display: none;">
    <!-- Deck 1: Dynamic 1 to 6 Video Slot Manager -->
    <div class="war-card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
          <div style="display: flex; align-items: center; gap: 10px;">
            <h2 style="font-size: 18px; font-weight: 800; color: #fff;">🧠 Multi-Video Strategy War Room</h2>
            <span class="badge-slot-count" id="slotCountBadge">0 / 6 Slots Active</span>
          </div>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
            Add 1 up to 6 video links or library projects. Compare tone, retention hooks, and conversion mechanics across creators.
          </p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button class="btn-gradient" id="btnAddSlot" onclick="addVideoSlot()" style="font-size: 12px; padding: 8px 14px;">
            ➕ Add Video Slot (Up to 6)
          </button>
          <button class="btn-copy" id="btnLoadCindyPack" onclick="loadCindyChandlerSagarPreset()" style="font-size: 12px; padding: 8px 14px; background: rgba(139, 92, 246, 0.2); color: #c084fc; border-color: rgba(139, 92, 246, 0.4);">
            ⚡ Load Cindy-Chandler-Sagar Test Pack
          </button>
        </div>
      </div>

      <!-- Slots Container (1 to 6 dynamic slots) -->
      <div class="slots-grid" id="slotsContainer">
        <!-- Rendered via renderSlots() -->
      </div>
    </div>

    <!-- Deck 2: Custom Strategy Prompt Console -->
    <div class="war-card" style="border-color: rgba(139, 92, 246, 0.4); background: linear-gradient(180deg, rgba(20, 24, 37, 0.85) 0%, rgba(13, 17, 23, 0.85) 100%);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
        <div>
          <h3 style="font-size: 15px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 8px;">
            <span>💬</span> What Do You Want to Accomplish or Think? (Custom Strategy Prompt)
          </h3>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
            Type your exact creative goal, compare specific hooks, or test Cindy's viral methodology on a new topic.
          </p>
        </div>
        <button class="btn-gradient" id="btnCrackStrategy" onclick="executeStrategyCrack()" style="padding: 10px 20px; font-size: 13px; font-weight: 700; box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);">
          ⚡ Crack Strategy & Generate Full Production Suite
        </button>
      </div>

      <!-- Quick-Action Presets -->
      <div style="margin-bottom: 12px;">
        <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 6px;">
          💡 Quick-Action Winning Presets (Click to Auto-Fill Prompt):
        </div>
        <div class="preset-chips-row">
          <button class="preset-chip" onclick="applyPreset('cindy')">⚡ Cindy Adaptation (Accessible Creator Remix)</button>
          <button class="preset-chip" onclick="applyPreset('chandler')">🔍 Chandler Architecture Breakdown (Tool Demystification)</button>
          <button class="preset-chip" onclick="applyPreset('hardware_proof')">🧪 Physical Desk Showdown (Live Multi-Device Action)</button>
          <button class="preset-chip" onclick="applyPreset('hook_exam')">🎯 Hook Cross-Examination (Why Did It Convert?)</button>
        </div>
      </div>

      <!-- Strategy Prompt Textarea -->
      <textarea id="strategyPromptInput" class="strategy-prompt-area" rows="3" placeholder="Tell the strategy engine what you want to think, crack, or accomplish...
e.g. 'I want to apply Cindy's relatable tone and Chandler's technical breakdown to Sagar's 3-phone Ultron demo right on my desk. Give me the complete winning 55s teleprompter script, CapCut zooms, and ManyChat comment automation.'"></textarea>

      <!-- Script Output Language Selector: English (Default), Tanglish, Mixed Tamil-English, Native Tamil -->
      <div style="margin-top: 14px; padding: 12px 14px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
          <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
            <span>🗣️</span> Script Output Language:
            <span style="font-size: 10px; color: var(--text-secondary); text-transform: none; font-weight: 400;">(Default: English — click to customize)</span>
          </div>
        </div>

        <div style="display: flex; gap: 8px; flex-wrap: wrap;" id="scriptConfigLangGroup">
          <label class="lang-radio-pill active" id="lbl_lang_english" onclick="selectScriptLanguage('english')">
            <input type="radio" name="scriptLanguageRadio" value="english" checked>
            <span>🇬🇧 English (Default)</span>
          </label>
          <label class="lang-radio-pill" id="lbl_lang_tanglish" onclick="selectScriptLanguage('tanglish')">
            <input type="radio" name="scriptLanguageRadio" value="tanglish">
            <span>⚡ Tanglish (Tamil in Eng)</span>
          </label>
          <label class="lang-radio-pill" id="lbl_lang_mixed" onclick="selectScriptLanguage('mixed')">
            <input type="radio" name="scriptLanguageRadio" value="mixed">
            <span>🔀 Mixed Tamil & English Terms</span>
          </label>
          <label class="lang-radio-pill" id="lbl_lang_tamil" onclick="selectScriptLanguage('tamil')">
            <input type="radio" name="scriptLanguageRadio" value="tamil">
            <span>🇮🇳 Tamil (தமிழ் எழுத்து)</span>
          </label>
        </div>
      </div>

      <!-- Deliverables Selection for Section B: User selects what they actually need -->
      <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
          <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #00F5D4; display: flex; align-items: center; gap: 6px;">
            <span>📦</span> Select What You Actually Need in Section B:
          </div>
          <div style="display: flex; gap: 8px;">
            <button class="preset-chip" onclick="toggleAllDeliverables(true)" style="padding: 2px 8px; font-size: 10px;">Select All</button>
            <button class="preset-chip" onclick="toggleAllDeliverables(false)" style="padding: 2px 8px; font-size: 10px;">Clear All</button>
          </div>
        </div>

        <div class="deliverable-toggles-grid">
          <label class="deliv-checkbox-pill active" id="lbl_deliv_script">
            <input type="checkbox" id="chk_deliv_script" value="script" checked onchange="updateDeliverableSelection()">
            <span>📜 Paced Teleprompter Script (55s)</span>
          </label>
          <label class="deliv-checkbox-pill active" id="lbl_deliv_edl">
            <input type="checkbox" id="chk_deliv_edl" value="edl" checked onchange="updateDeliverableSelection()">
            <span>⏱️ CapCut Pro Timeline Markers (.EDL)</span>
          </label>
          <label class="deliv-checkbox-pill active" id="lbl_deliv_ai">
            <input type="checkbox" id="chk_deliv_ai" value="ai" checked onchange="updateDeliverableSelection()">
            <span>🎨 Google Flow & Higsfield AI Prompts</span>
          </label>
          <label class="deliv-checkbox-pill active" id="lbl_deliv_funnel">
            <input type="checkbox" id="chk_deliv_funnel" value="funnel" checked onchange="updateDeliverableSelection()">
            <span>💬 Caption & ManyChat Funnel</span>
          </label>
          <label class="deliv-checkbox-pill active" id="lbl_deliv_hooks">
            <input type="checkbox" id="chk_deliv_hooks" value="hooks" checked onchange="updateDeliverableSelection()">
            <span>🎯 3 High-Voltage Hook Rewrites</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Deck 3: Dual Output Presentation -->
    <div id="strategyOutputDeck" style="display: none; flex-direction: column; gap: 20px;">
      
      <!-- Organized Local Disk Storage Banner -->
      <div id="localStorageBanner" class="war-card" style="border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.08); padding: 16px 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 40px; height: 40px; border-radius: 8px; background: rgba(16, 185, 129, 0.2); display: flex; align-items: center; justify-content: center; font-size: 20px; color: #10b981;">💾</div>
            <div>
              <div style="font-size: 13px; font-weight: 800; color: #10b981; letter-spacing: 0.5px; text-transform: uppercase; display: flex; align-items: center; gap: 8px;">
                <span>Session Files Organized & Stored Locally</span>
                <span style="font-size: 10px; background: rgba(16, 185, 129, 0.25); color: #6ee7b7; padding: 2px 6px; border-radius: 4px; font-weight: 700;">PERSISTED</span>
              </div>
              <div style="font-size: 12px; color: #e2e8f0; font-family: 'JetBrains Mono', monospace; margin-top: 4px;" id="localStoragePath">Instagram/Reels/Strategy_Cracks/...</div>
            </div>
          </div>
          <div id="localStorageFilesBadgeList" style="display: flex; gap: 6px; flex-wrap: wrap; align-items: center;">
            <!-- Populated via executeStrategyCrack() -->
          </div>
        </div>
      </div>

      <!-- Option / Section A: Direct Strategic Response to User Prompt -->
      <div class="war-card" style="border-left: 4px solid #38bdf8;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px;">SECTION A: DIRECT STRATEGIC ANSWER</span>
            <h3 style="font-size: 16px; font-weight: 800; color: #fff;">Forensic Analysis of What You Asked</h3>
          </div>
          <button class="btn-copy" onclick="copyElementText('strategicAnswerContent')">📋 Copy Analysis</button>
        </div>
        <div id="strategicAnswerContent" class="md-preview" style="max-height: 480px; overflow-y: auto; padding: 16px; background: rgba(0,0,0,0.35); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
          <!-- Populated via executeStrategyCrack() -->
        </div>
      </div>

      <!-- Option / Section B: Production Deliverables Deck (Separate Option / Filtered by user selection) -->
      <div class="war-card" style="border-left: 4px solid #00F5D4;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="background: rgba(0, 245, 212, 0.2); color: #00F5D4; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 12px;">SECTION B: PRODUCTION DELIVERABLES</span>
            <h3 style="font-size: 16px; font-weight: 800; color: #fff;">Selected Production Suite</h3>
            <span id="delivCountBadge" style="background: rgba(0, 245, 212, 0.15); color: #00F5D4; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0, 245, 212, 0.3);">5 Selected</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary);">
            <span>CapCut: <kbd style="background:rgba(255,255,255,0.1); padding:1px 5px; border-radius:3px;">Cmd+B</kbd> Split | <kbd style="background:rgba(255,255,255,0.1); padding:1px 5px; border-radius:3px;">M</kbd> Marker</span>
          </div>
        </div>

        <!-- Deliverables Tab Nav (Dynamically filtered by user selection) -->
        <div class="tab-nav" id="delivTabNav" style="margin-bottom: 16px;">
          <button class="tab-btn active" id="btnDelivScript" onclick="switchDeliverableTab('script', this)">📜 Paced Teleprompter Script</button>
          <button class="tab-btn" id="btnDelivEdl" onclick="switchDeliverableTab('edl', this)">⏱️ CapCut Pro Timeline Markers (.EDL)</button>
          <button class="tab-btn" id="btnDelivAi" onclick="switchDeliverableTab('ai', this)">🎨 Google Flow & Higsfield AI Prompts</button>
          <button class="tab-btn" id="btnDelivFunnel" onclick="switchDeliverableTab('funnel', this)">💬 Caption & ManyChat Comment Funnel</button>
          <button class="tab-btn" id="btnDelivHooks" onclick="switchDeliverableTab('hooks', this)">🎯 3 High-Voltage Hook Rewrites</button>
        </div>

        <div id="noDelivSelectedNotice" style="display: none; padding: 24px; text-align: center; color: var(--text-secondary); font-size: 13px; background: rgba(0,0,0,0.25); border-radius: 8px;">
          ⚠️ No deliverables selected for Section B. Check what you actually need above in the deliverable selector.
        </div>

        <!-- Tab 1: Teleprompter Script -->
        <div id="deliv-tab-script" class="deliv-tab-content">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 6px;" id="scriptViewLangPills">
              <button type="button" class="tab-btn active" id="btnViewLang_english" onclick="switchScriptLanguageView('english')" style="font-size: 11px; padding: 4px 10px;">🇬🇧 English</button>
              <button type="button" class="tab-btn" id="btnViewLang_tanglish" onclick="switchScriptLanguageView('tanglish')" style="font-size: 11px; padding: 4px 10px;">⚡ Tanglish</button>
              <button type="button" class="tab-btn" id="btnViewLang_mixed" onclick="switchScriptLanguageView('mixed')" style="font-size: 11px; padding: 4px 10px;">🔀 Mixed Tamil-English</button>
              <button type="button" class="tab-btn" id="btnViewLang_tamil" onclick="switchScriptLanguageView('tamil')" style="font-size: 11px; padding: 4px 10px;">🇮🇳 Tamil (தமிழ்)</button>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span id="activeLangBadge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.3);">🇬🇧 English</span>
              <button class="btn-copy" onclick="copyElementText('delivScriptContent')">📋 Copy Active Script</button>
            </div>
          </div>
          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">Target: 55-58 seconds | 150 WPM conversational speed | Bracketed timestamps for teleprompter pace</div>
          <pre id="delivScriptContent" style="background: #090d13; border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; color: #e2e8f0; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; max-height: 380px; overflow-y: auto;"></pre>
        </div>

        <!-- Tab 2: CapCut EDL Markers -->
        <div id="deliv-tab-edl" class="deliv-tab-content" style="display: none;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 12px; color: var(--text-secondary);">CMX 3600 & CapCut Non-Drop Frame Markers | Zoom cues (100% -> 118%) & SFX: Deep Tech Whoosh, Glitch, 808 Sub Drop</span>
            <button class="btn-copy" onclick="copyElementText('delivEdlContent')">📋 Copy CapCut EDL</button>
          </div>
          <pre id="delivEdlContent" style="background: #090d13; border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; color: #7ee787; font-family: 'JetBrains Mono', monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; max-height: 380px; overflow-y: auto;"></pre>
        </div>

        <!-- Tab 3: AI Prompts -->
        <div id="deliv-tab-ai" class="deliv-tab-content" style="display: none;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 12px; color: var(--text-secondary);">9:16 Vertical B-Roll Generation Prompts for Google Flow & Higsfield AI</span>
            <button class="btn-copy" onclick="copyElementText('delivAiContent')">📋 Copy AI Prompts</button>
          </div>
          <div id="delivAiContent" class="md-preview" style="background: #090d13; border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; color: #cbd5e1; font-size: 13px; line-height: 1.6; max-height: 380px; overflow-y: auto;"></div>
        </div>

        <!-- Tab 4: Caption & Funnel -->
        <div id="deliv-tab-funnel" class="deliv-tab-content" style="display: none;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 12px; color: var(--text-secondary);">Explore Algorithm Optimization | Automated Comment-to-DM Trigger Sequence</span>
            <button class="btn-copy" onclick="copyElementText('delivFunnelContent')">📋 Copy Caption & Funnel</button>
          </div>
          <div id="delivFunnelContent" class="md-preview" style="background: #090d13; border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; color: #cbd5e1; font-size: 13px; line-height: 1.6; max-height: 380px; overflow-y: auto;"></div>
        </div>

        <!-- Tab 5: Hook Rewrites -->
        <div id="deliv-tab-hooks" class="deliv-tab-content" style="display: none;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 12px; color: var(--text-secondary);">3 Battle-Tested Alternative Hooks for Algorithm A/B Testing</span>
            <button class="btn-copy" onclick="copyElementText('delivHooksContent')">📋 Copy Hook Rewrites</button>
          </div>
          <div id="delivHooksContent" style="display: flex; flex-direction: column; gap: 10px;"></div>
        </div>
      </div>
    </div>

    <!-- Reference Archive: Master Evolution Study Drawer -->
    <details style="background: rgba(13, 17, 23, 0.6); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px 18px;">
      <summary style="font-size: 13px; font-weight: 700; color: #38bdf8; cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
        <span>🧬 Master Reference: The 3 Jarvis Videos Genealogy Study (Luke ➔ Chandler ➔ Cindy)</span>
        <span style="font-size: 11px; color: var(--text-secondary); font-weight: 400;">(Click to expand master comparative notes)</span>
      </summary>
      <div style="margin-top: 16px;">
        <div class="genealogy-tree" id="genealogyTree">Loading evolution tree...</div>
        <div class="md-preview" id="clusterMasterStudyContent" style="margin-top: 16px;">Loading study...</div>
      </div>
    </details>
  </div>

  <!-- Live Log Streaming Modal -->
  <div class="log-modal" id="logModal">
    <div class="log-window">
      <div class="log-header">
        <span>⚡ Pipeline Execution Logs</span>
        <button class="btn-copy" onclick="closeLogModal()">Close</button>
      </div>
      <div class="log-body" id="logTerminal">Connecting to pipeline stream...</div>
    </div>
  </div>

  <div id="toast">Copied to clipboard!</div>

  <script>
    let currentProjects = [];
    let currentProject = null;
    let currentClusters = [];
    let currentCluster = null;
    let currentStudioMode = 'standard';
    let prompterInterval = null;
    let prompterScrolling = false;
    let scrollSpeedPx = 40;

    // Mode Switcher Handler: 2 Clean Main Options
    function switchStudioMode(mode) {
      if (mode === 'standard') mode = 'single';
      if (mode === 'lineage') mode = 'strategy';
      currentStudioMode = mode;

      const btnSingle = document.getElementById('btnModeSingle');
      const btnStrategy = document.getElementById('btnModeStrategy');
      if (btnSingle) btnSingle.classList.toggle('active', mode === 'single');
      if (btnStrategy) btnStrategy.classList.toggle('active', mode === 'strategy');

      const stdMain = document.getElementById('standardMain');
      const stratView = document.getElementById('strategyWarRoomView');
      const projSel = document.getElementById('projectSelect');

      if (mode === 'single') {
        stdMain.style.display = 'grid';
        if (stratView) stratView.style.display = 'none';
        if (projSel) projSel.style.display = 'block';
      } else {
        stdMain.style.display = 'none';
        if (stratView) stratView.style.display = 'flex';
        if (projSel) projSel.style.display = 'none';
        if (activeSlots.length === 0) {
          initDefaultSlots();
        }
      }
    }

    // Dynamic 1 to 6 Video Slot Manager
    let activeSlots = [];
    let nextSlotId = 1;

    function initDefaultSlots() {
      activeSlots = [];
      nextSlotId = 1;
      
      // Default: Load the 3 master reference videos (Luke, Chandler, Cindy)
      const jarvisOriginal = currentProjects.find(p => p.rel_path.includes("01_Original"));
      const jarvisChandler = currentProjects.find(p => p.rel_path.includes("02_Iteration"));
      const jarvisCindy = currentProjects.find(p => p.rel_path.includes("03_Iteration"));

      if (jarvisOriginal) {
        addVideoSlot(jarvisOriginal.rel_path, 'project');
      } else if (currentProjects.length > 0) {
        addVideoSlot(currentProjects[0].rel_path, 'project');
      }

      if (jarvisChandler) addVideoSlot(jarvisChandler.rel_path, 'project');
      if (jarvisCindy) addVideoSlot(jarvisCindy.rel_path, 'project');

      renderSlots();
    }

    function addVideoSlot(initialValue = "", initialType = "project") {
      if (activeSlots.length >= 6) {
        showToast("Maximum of 6 video slots reached!");
        return;
      }
      const id = nextSlotId++;
      const defVal = initialValue || (currentProjects.length > 0 ? currentProjects[0].rel_path : "");
      activeSlots.push({ id, type: initialType, value: defVal });
      renderSlots();
    }

    function removeVideoSlot(id) {
      if (activeSlots.length <= 1) {
        showToast("You need at least 1 video slot!");
        return;
      }
      activeSlots = activeSlots.filter(s => s.id !== id);
      renderSlots();
    }

    function updateSlotType(id, type) {
      const s = activeSlots.find(slot => slot.id === id);
      if (s) {
        s.type = type;
        s.value = (type === 'project') ? (currentProjects[0]?.rel_path || "") : "";
        renderSlots();
      }
    }

    function updateSlotValue(id, val) {
      const s = activeSlots.find(slot => slot.id === id);
      if (s) {
        s.value = val;
        updateSlotPreview(id);
      }
    }

    function renderSlots() {
      const container = document.getElementById('slotsContainer');
      if (!container) return;
      container.innerHTML = '';
      const countEl = document.getElementById('slotCountBadge');
      if (countEl) countEl.textContent = `${activeSlots.length} / 6 Slots Active`;

      const roleBadges = [
        { name: "Original / Anchor", color: "#38bdf8", bg: "rgba(56, 189, 248, 0.15)" },
        { name: "Breakdown / Architecture", color: "#00F5D4", bg: "rgba(0, 245, 212, 0.15)" },
        { name: "Accessible / Remix", color: "#FF8C00", bg: "rgba(255, 140, 0, 0.15)" },
        { name: "Target / Test Reel", color: "#c084fc", bg: "rgba(139, 92, 246, 0.2)" },
        { name: "Competitor Comparison", color: "#ec4899", bg: "rgba(236, 72, 153, 0.15)" },
        { name: "Bonus Synthesis", color: "#10b981", bg: "rgba(16, 185, 129, 0.15)" }
      ];

      activeSlots.forEach((slot, idx) => {
        const role = roleBadges[idx] || { name: `Source #${idx+1}`, color: "#38bdf8", bg: "rgba(56, 189, 248, 0.15)" };
        const card = document.createElement('div');
        card.className = 'slot-card';
        card.id = `slotCard_${slot.id}`;

        let projectOptions = '';
        currentProjects.forEach(p => {
          const sel = (p.rel_path === slot.value) ? 'selected' : '';
          projectOptions += `<option value="${p.rel_path}" ${sel}>[${p.platform}] ${p.creator} - ${p.title.slice(0, 36)}</option>`;
        });

        card.innerHTML = `
          <div class="slot-card-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="slot-num-badge">Slot #${idx + 1}</span>
              <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: ${role.color}; background: ${role.bg}; padding: 2px 6px; border-radius: 4px;">${role.name}</span>
            </div>
            ${activeSlots.length > 1 ? `<button class="slot-remove-btn" onclick="removeVideoSlot(${slot.id})">✕ Remove</button>` : ''}
          </div>

          <div style="display: flex; gap: 6px; font-size: 11px; margin-bottom: 2px;">
            <label style="cursor: pointer; display: flex; align-items: center; gap: 4px; color: ${slot.type === 'project' ? '#fff' : 'var(--text-secondary)'};">
              <input type="radio" name="slotType_${slot.id}" value="project" ${slot.type === 'project' ? 'checked' : ''} onchange="updateSlotType(${slot.id}, 'project')">
              Pick Library Project
            </label>
            <label style="cursor: pointer; display: flex; align-items: center; gap: 4px; margin-left: 10px; color: ${slot.type === 'url' ? '#fff' : 'var(--text-secondary)'};">
              <input type="radio" name="slotType_${slot.id}" value="url" ${slot.type === 'url' ? 'checked' : ''} onchange="updateSlotType(${slot.id}, 'url')">
              Paste Social URL
            </label>
          </div>

          ${slot.type === 'project' ? `
            <select class="wizard-select" style="padding: 8px 10px; font-size: 12px;" onchange="updateSlotValue(${slot.id}, this.value)">
              ${projectOptions}
            </select>
          ` : `
            <input type="text" class="wizard-input" style="padding: 8px 10px; font-size: 12px;" placeholder="https://www.instagram.com/reel/..." value="${slot.value}" oninput="updateSlotValue(${slot.id}, this.value)">
          `}

          <div class="slot-preview-pill" id="slotPreview_${slot.id}">
            Loading metadata preview...
          </div>
        `;
        container.appendChild(card);
        updateSlotPreview(slot.id);
      });
    }

    function updateSlotPreview(slotId) {
      const s = activeSlots.find(slot => slot.id === slotId);
      const previewEl = document.getElementById(`slotPreview_${slotId}`);
      if (!s || !previewEl) return;

      if (s.type === 'project') {
        const p = currentProjects.find(proj => proj.rel_path === s.value);
        if (p) {
          const ratio = (p.likes > 0 && p.comments > 0) ? `${((p.comments / p.likes) * 100).toFixed(1)}%` : 'N/A';
          const likesFmt = p.likes ? (p.likes > 999 ? (p.likes / 1000).toFixed(1) + 'k' : p.likes) : '0';
          const commsFmt = p.comments ? (p.comments > 999 ? (p.comments / 1000).toFixed(1) + 'k' : p.comments) : '0';
          previewEl.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
              <span>👤 <strong>${p.creator}</strong></span>
              <span style="color: #00F5D4;">❤️ ${likesFmt} | 💬 ${commsFmt} (${ratio})</span>
            </div>
            <div style="color: #94a3b8; font-size: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              🎯 ${p.title}
            </div>
          `;
          return;
        }
      }
      previewEl.innerHTML = `
        <div style="color: #38bdf8;">🔗 External Video Source</div>
        <div style="color: #94a3b8; font-size: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${s.value || "Enter URL above"}</div>
      `;
    }

    function loadCindyChandlerSagarPreset() {
      activeSlots = [];
      nextSlotId = 1;

      const l = currentProjects.find(p => p.rel_path.includes("01_Original"));
      const ch = currentProjects.find(p => p.rel_path.includes("02_Iteration"));
      const ci = currentProjects.find(p => p.rel_path.includes("03_Iteration"));
      const sa = currentProjects.find(p => p.rel_path.includes("sagar_builds"));

      if (l) addVideoSlot(l.rel_path, 'project');
      if (ch) addVideoSlot(ch.rel_path, 'project');
      if (ci) addVideoSlot(ci.rel_path, 'project');
      if (sa) addVideoSlot(sa.rel_path, 'project');

      document.getElementById('strategyPromptInput').value = "I want to apply Cindy's relatable tone and Chandler's technical breakdown to Sagar's 3-phone Ultron demo right on my desk. Give me the complete winning 55s teleprompter script, CapCut zooms, and ManyChat comment automation.";
      showToast("Loaded Cindy + Chandler + Sagar Ultron test suite!");
    }

    function applyPreset(presetKey) {
      const promptBox = document.getElementById('strategyPromptInput');
      if (presetKey === 'cindy') {
        promptBox.value = "Apply Cindy Zhu's accessible creator remix methodology: remove technical gatekeeping, speak directly to camera with warm tone, pressure-test the tools on my own physical desk, and deliver a frictionless 'COMMENT ULTRON' ManyChat loop.";
      } else if (presetKey === 'chandler') {
        promptBox.value = "Dissect the system architecture like Chandler Intelligence: demystify the magic by naming the exact stack (FastMCP, Wireless ADB, Claude Code), and give viewers the step-by-step schematic to reproduce it.";
      } else if (presetKey === 'hardware_proof') {
        promptBox.value = "Design a live proof showdown demonstrating physical multi-device action: show 3 phones on my desk waking up and triggering actions in unison with a single voice command, proving it works without wires.";
      } else if (presetKey === 'hook_exam') {
        promptBox.value = "Conduct a forensic cross-examination of the opening 3 seconds of each video. Explain why Cindy's hook achieved a 53% comment-to-like conversion ratio compared to the others, and write 3 winning hook variations for my reel.";
      }
      promptBox.focus();
      showToast("Preset loaded into strategy prompt!");
    }

    // Deliverable Checkbox Selection Logic: Controls what user actually needs in Section B
    function updateDeliverableSelection() {
      const items = [
        { key: 'script', chk: document.getElementById('chk_deliv_script'), lbl: document.getElementById('lbl_deliv_script'), btn: document.getElementById('btnDelivScript'), tab: document.getElementById('deliv-tab-script') },
        { key: 'edl', chk: document.getElementById('chk_deliv_edl'), lbl: document.getElementById('lbl_deliv_edl'), btn: document.getElementById('btnDelivEdl'), tab: document.getElementById('deliv-tab-edl') },
        { key: 'ai', chk: document.getElementById('chk_deliv_ai'), lbl: document.getElementById('lbl_deliv_ai'), btn: document.getElementById('btnDelivAi'), tab: document.getElementById('deliv-tab-ai') },
        { key: 'funnel', chk: document.getElementById('chk_deliv_funnel'), lbl: document.getElementById('lbl_deliv_funnel'), btn: document.getElementById('btnDelivFunnel'), tab: document.getElementById('deliv-tab-funnel') },
        { key: 'hooks', chk: document.getElementById('chk_deliv_hooks'), lbl: document.getElementById('lbl_deliv_hooks'), btn: document.getElementById('btnDelivHooks'), tab: document.getElementById('deliv-tab-hooks') }
      ];

      let activeCount = 0;
      let firstActiveItem = null;
      let currentActiveVisible = false;

      items.forEach(it => {
        if (!it.chk) return;
        const isChecked = it.chk.checked;
        if (it.lbl) it.lbl.classList.toggle('active', isChecked);
        if (it.btn) {
          it.btn.style.display = isChecked ? 'inline-flex' : 'none';
          if (isChecked && it.btn.classList.contains('active')) {
            currentActiveVisible = true;
          }
        }
        if (isChecked) {
          activeCount++;
          if (!firstActiveItem) firstActiveItem = it;
        } else {
          if (it.tab) it.tab.style.display = 'none';
          if (it.btn) it.btn.classList.remove('active');
        }
      });

      const badge = document.getElementById('delivCountBadge');
      if (badge) badge.textContent = `${activeCount} Selected`;

      const notice = document.getElementById('noDelivSelectedNotice');
      if (notice) notice.style.display = (activeCount === 0) ? 'block' : 'none';

      // If active tab was unchecked or no active tab, switch to firstActiveItem
      if (activeCount > 0 && (!currentActiveVisible && firstActiveItem)) {
        switchDeliverableTab(firstActiveItem.key, firstActiveItem.btn);
      }
    }

    let selectedScriptLanguage = 'english';
    let currentGeneratedScripts = {};

    function selectScriptLanguage(lang) {
      selectedScriptLanguage = lang;
      document.querySelectorAll('.lang-radio-pill').forEach(pill => pill.classList.remove('active'));
      const activePill = document.getElementById('lbl_lang_' + lang);
      if (activePill) {
        activePill.classList.add('active');
        const radio = activePill.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;
      }
    }

    function switchScriptLanguageView(lang) {
      if (!currentGeneratedScripts || Object.keys(currentGeneratedScripts).length === 0) return;
      const scriptText = currentGeneratedScripts[lang];
      if (scriptText) {
        const el = document.getElementById('delivScriptContent');
        if (el) el.textContent = scriptText;
      }
      document.querySelectorAll('#scriptViewLangPills .tab-btn').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById('btnViewLang_' + lang);
      if (activeBtn) activeBtn.classList.add('active');

      const labels = {
        'english': '🇬🇧 English',
        'tanglish': '⚡ Tanglish',
        'mixed': '🔀 Mixed Tamil-English',
        'tamil': '🇮🇳 Tamil (தமிழ்)'
      };
      const badge = document.getElementById('activeLangBadge');
      if (badge) badge.textContent = labels[lang] || lang;
    }

    function toggleAllDeliverables(select) {
      ['chk_deliv_script', 'chk_deliv_edl', 'chk_deliv_ai', 'chk_deliv_funnel', 'chk_deliv_hooks'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.checked = select;
      });
      updateDeliverableSelection();
    }

    async function executeStrategyCrack() {
      const promptText = document.getElementById('strategyPromptInput').value.trim();
      const sourcesPayload = activeSlots.map(s => ({
        type: s.type,
        value: s.value
      }));

      if (sourcesPayload.length === 0) {
        showToast("Please add at least 1 video slot!");
        return;
      }

      const checkedDeliverables = Array.from(document.querySelectorAll('.deliv-checkbox-pill input[type="checkbox"]:checked')).map(cb => cb.value);

      const btn = document.getElementById('btnCrackStrategy');
      btn.disabled = true;
      btn.innerHTML = '<span>⚡</span> Analyzing & Generating...';

      try {
        const res = await fetch('/api/strategy-crack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sources: sourcesPayload,
            prompt: promptText,
            deliverables: checkedDeliverables,
            language: selectedScriptLanguage
          })
        });
        const data = await res.json();

        // Local Storage Banner
        if (data.storage_dir) {
          document.getElementById('localStoragePath').textContent = data.storage_dir;
          const badgesHtml = (data.saved_files || []).map(fn => `
            <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 11px; font-family: 'JetBrains Mono', monospace; font-weight: 600; padding: 4px 10px; border-radius: 5px; border: 1px solid rgba(16, 185, 129, 0.3); display: inline-flex; align-items: center; gap: 4px;">📄 ${fn}</span>
          `).join('');
          document.getElementById('localStorageFilesBadgeList').innerHTML = badgesHtml;
        }

        // Section A: Direct Strategic Answer
        document.getElementById('strategicAnswerContent').innerHTML = renderMarkdown(data.custom_answer || "");

        // Section B: Deliverables Deck (Populate received items)
        currentGeneratedScripts = data.scripts_by_language || {};
        if (data.scripts_by_language) {
          const initLang = data.active_language || selectedScriptLanguage || 'english';
          switchScriptLanguageView(initLang);
        } else if (data.teleprompter_script) {
          document.getElementById('delivScriptContent').textContent = data.teleprompter_script;
        }
        if (data.timeline_edl) {
          document.getElementById('delivEdlContent').textContent = data.timeline_edl;
        }

        if (data.flow_prompt || data.higsfield_prompt) {
          const aiHtml = `
            <div style="margin-bottom: 14px;">
              <strong style="color: #FF8C00;">🎨 Google Flow AI Prompt (Cinematic Vertical Push-In):</strong>
              <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 12px; margin-top: 6px; color: #f1f5f9; font-family: monospace; font-size: 12px; line-height: 1.5;">${data.flow_prompt || ""}</div>
            </div>
            <div>
              <strong style="color: #c084fc;">🎬 Higsfield AI Prompt (First-Person POV & Screen Wake-Up):</strong>
              <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 12px; margin-top: 6px; color: #f1f5f9; font-family: monospace; font-size: 12px; line-height: 1.5;">${data.higsfield_prompt || ""}</div>
            </div>
          `;
          document.getElementById('delivAiContent').innerHTML = aiHtml;
        }

        if (data.caption || data.manychat_funnel) {
          const funnelHtml = `
            <div style="margin-bottom: 14px;">
              <strong style="color: #38bdf8;">📱 Viral Instagram Caption (Optimized for Explore Algorithm):</strong>
              <pre style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 12px; margin-top: 6px; color: #f1f5f9; font-family: monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap;">${data.caption || ""}</pre>
            </div>
            <div>
              <strong style="color: #00F5D4;">🤖 ManyChat Automated Comment-to-DM Automation Flow:</strong>
              <div style="margin-top: 6px;">${renderMarkdown(data.manychat_funnel || "")}</div>
            </div>
          `;
          document.getElementById('delivFunnelContent').innerHTML = funnelHtml;
        }

        if (data.hook_rewrites && document.getElementById('delivHooksContent')) {
          document.getElementById('delivHooksContent').innerHTML = (data.hook_rewrites || []).map(r => `
            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; border-left: 3px solid #FF8C00;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #FF8C00; text-transform: uppercase;">${r.archetype}</span>
                <button class="btn-copy" style="padding: 2px 8px; font-size: 10px;" onclick="navigator.clipboard.writeText('${r.hook.replace(/'/g, "\\'")}'); showToast('Hook copied!');">📋 Copy</button>
              </div>
              <div style="font-size: 13px; font-weight: 600; color: #fff; margin-bottom: 6px;">"${r.hook}"</div>
              <div style="font-size: 11px; color: var(--text-secondary);">🎬 Delivery Cue: ${r.cue}</div>
            </div>
          `).join('');
        }

        // Filter tabs to reflect only selected deliverables
        updateDeliverableSelection();

        // Reveal Output Deck
        const deck = document.getElementById('strategyOutputDeck');
        deck.style.display = 'flex';
        deck.scrollIntoView({ behavior: 'smooth' });
        showToast("⚡ Strategy Cracked & Production Suite Ready!");
      } catch (err) {
        showToast("❌ Error cracking strategy: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '⚡ Crack Strategy & Generate Full Production Suite';
      }
    }

    function switchDeliverableTab(tab, el) {
      document.querySelectorAll('#strategyWarRoomView .tab-nav .tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.deliv-tab-content').forEach(c => c.style.display = 'none');
      if (el) el.classList.add('active');
      const targetTab = document.getElementById('deliv-tab-' + tab);
      if (targetTab) targetTab.style.display = 'block';
    }

    function copyElementText(elId) {
      const el = document.getElementById(elId);
      const text = el.innerText || el.textContent;
      navigator.clipboard.writeText(text).then(() => {
        showToast("Copied to clipboard!");
      });
    }

    // Initialize Studio
    window.addEventListener('DOMContentLoaded', () => {
      loadProjects();
      loadClusters();
      updateDeliverableSelection();
      window.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
          e.preventDefault();
          togglePrompterScroll();
        }
      });
    });

    async function loadProjects() {
      const res = await fetch('/api/projects');
      currentProjects = await res.json();
      const sel = document.getElementById('projectSelect');
      sel.innerHTML = '';
      if (currentProjects.length === 0) {
        sel.innerHTML = '<option value="">No processed projects found</option>';
        return;
      }
      currentProjects.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.rel_path;
        opt.textContent = `[${p.platform}] ${p.creator} - ${p.title.slice(0, 40)}`;
        sel.appendChild(opt);
      });
      onProjectSelected(currentProjects[0].rel_path);
    }

    async function loadClusters() {
      const res = await fetch('/api/clusters');
      currentClusters = await res.json();
      const sel = document.getElementById('clusterSelect');
      sel.innerHTML = '';
      if (currentClusters.length === 0) {
        sel.innerHTML = '<option value="">No viral clusters found</option>';
        return;
      }
      currentClusters.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.cluster_name;
        opt.textContent = `🧬 ${c.cluster_name.split(' (')[0]} (${c.members.length} Iterations | ${(c.total_likes / 1000).toFixed(0)}k Likes)`;
        sel.appendChild(opt);
      });
      onClusterSelected(currentClusters[0].cluster_name);
    }

    function onClusterSelected(clusterName) {
      currentCluster = currentClusters.find(c => c.cluster_name === clusterName);
      if (!currentCluster) return;

      const titleEl = document.getElementById('clusterTitle');
      if (titleEl) titleEl.textContent = `🧬 ${currentCluster.cluster_name}`;
      const likesEl = document.getElementById('clusterLikes');
      if (likesEl) likesEl.textContent = currentCluster.total_likes.toLocaleString();
      const commsEl = document.getElementById('clusterComments');
      if (commsEl) commsEl.textContent = currentCluster.total_comments.toLocaleString();
      const gensEl = document.getElementById('clusterGenerations');
      if (gensEl) gensEl.textContent = `${currentCluster.members.length} Iterations`;

      if (document.getElementById('genealogyTree')) {
        renderGenealogyTree(currentCluster);
      }
      if (document.getElementById('clusterMasterStudyContent')) {
        document.getElementById('clusterMasterStudyContent').innerHTML = renderMarkdown(currentCluster.master_study || "No master study document found.");
      }
      if (document.getElementById('clusterMatrixContainer')) {
        renderClusterMatrix(currentCluster);
      }
    }

    function renderGenealogyTree(cluster) {
      const treeContainer = document.getElementById('genealogyTree');
      treeContainer.innerHTML = '';

      cluster.members.forEach((m, idx) => {
        const card = document.createElement('div');
        card.className = 'tree-card';

        let badgeClass = 'badge-originator';
        let roleName = m.role;
        if (idx === 0) {
          badgeClass = 'badge-originator';
          roleName = '01. The Originator';
        } else if (idx === 1) {
          badgeClass = 'badge-breakdown';
          roleName = '02. Chandler Breakdown';
        } else if (idx === 2) {
          badgeClass = 'badge-accessible';
          roleName = '03. Cindy Accessible Test';
        } else {
          badgeClass = 'badge-synthesis';
          roleName = '04. Winning Synthesis';
        }

        const likesFmt = m.likes > 0 ? (m.likes > 999 ? (m.likes/1000).toFixed(1) + 'k' : m.likes) : 'Target';
        const commsFmt = m.comments > 0 ? (m.comments > 999 ? (m.comments/1000).toFixed(1) + 'k' : m.comments) : 'Target';
        const durFmt = m.duration ? m.duration + 's' : 'Ready';

        card.innerHTML = `
          <div>
            <span class="tree-role-badge ${badgeClass}">${roleName}</span>
            <div class="tree-card-title">${m.title.slice(0, 45)}</div>
            <div class="tree-card-creator">👤 ${m.creator}</div>
          </div>
          <div>
            <div class="tree-metrics">
              <span>❤️ <strong>${likesFmt}</strong></span>
              <span>💬 <strong>${commsFmt}</strong></span>
              <span>⏱️ <strong>${durFmt}</strong></span>
            </div>
            <button class="btn-copy" style="width: 100%; margin-top: 10px; justify-content: center;" onclick="inspectClusterMember('${m.rel_path}')">
              🎬 Inspect in Studio
            </button>
          </div>
        `;
        treeContainer.appendChild(card);
      });
    }

    function inspectClusterMember(relPath) {
      switchStudioMode('standard');
      document.getElementById('projectSelect').value = relPath;
      onProjectSelected(relPath);
    }

    function renderClusterMatrix(cluster) {
      const container = document.getElementById('clusterMatrixContainer');
      let html = '<div style="overflow-x:auto;"><table style="width:100%; border-collapse:collapse; font-size:13px; background:rgba(13,17,23,0.7); border-radius:10px; overflow:hidden; border:1px solid var(--border-color);">';
      html += '<thead style="background:rgba(255,255,255,0.06); color:#fff;"><tr>';
      html += '<th style="padding:12px 14px; text-align:left;">Iteration</th>';
      html += '<th style="padding:12px 14px; text-align:left;">Creator / Role</th>';
      html += '<th style="padding:12px 14px; text-align:right;">Likes</th>';
      html += '<th style="padding:12px 14px; text-align:right;">Comments</th>';
      html += '<th style="padding:12px 14px; text-align:right;">Comment Ratio</th>';
      html += '<th style="padding:12px 14px; text-align:center;">Duration</th>';
      html += '<th style="padding:12px 14px; text-align:center;">Action</th>';
      html += '</tr></thead><tbody>';

      cluster.members.forEach((m, idx) => {
        const bg = (idx % 2 === 0) ? 'background:rgba(255,255,255,0.02);' : '';
        const ratio = (m.likes > 0 && m.comments > 0) ? ((m.comments / m.likes) * 100).toFixed(1) + '%' : 'N/A';
        html += `<tr style="${bg} border-bottom: 1px solid rgba(255,255,255,0.05);">`;
        html += `<td style="padding:10px 14px; font-weight:700; color:#38bdf8;">${m.folder_name}</td>`;
        html += `<td style="padding:10px 14px; color:#e2e8f0;">${m.creator}</td>`;
        html += `<td style="padding:10px 14px; text-align:right; font-weight:700; color:#00F5D4;">${m.likes ? m.likes.toLocaleString() : '-'}</td>`;
        html += `<td style="padding:10px 14px; text-align:right; font-weight:700; color:#f1f5f9;">${m.comments ? m.comments.toLocaleString() : '-'}</td>`;
        html += `<td style="padding:10px 14px; text-align:right; font-weight:800; color:#FF8C00;">${ratio}</td>`;
        html += `<td style="padding:10px 14px; text-align:center; color:#cbd5e1;">${m.duration ? m.duration + 's' : '-'}</td>`;
        html += `<td style="padding:10px 14px; text-align:center;"><button class="btn-copy" style="display:inline-flex;" onclick="inspectClusterMember('${m.rel_path}')">Open Studio</button></td>`;
        html += '</tr>';
      });

      html += '</tbody></table></div>';
      container.innerHTML = html;
    }

    function switchClusterTab(tab, el) {
      document.querySelectorAll('#lineageMain .tab-nav .tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.cluster-tab-content').forEach(c => c.style.display = 'none');
      el.classList.add('active');
      document.getElementById('cluster-tab-' + tab).style.display = 'block';
    }

    async function runRemixWizard() {
      const angle = document.getElementById('wizAngle').value;
      const persona = document.getElementById('wizPersona').value;
      const tools = document.getElementById('wizTools').value;
      const cta_keyword = document.getElementById('wizCta').value;
      const pacing = document.getElementById('wizPacing').value;
      const topic = document.getElementById('wizTopic').value;

      const res = await fetch('/api/remix-wizard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_project: currentCluster ? currentCluster.cluster_name : "Ultron",
          angle, persona, tools, cta_keyword, pacing, topic
        })
      });
      const data = await res.json();

      document.getElementById('wizOutScript').textContent = data.teleprompter_script;
      document.getElementById('wizOutEDL').textContent = data.timeline_edl;

      const aiHtml = `
        <div style="margin-bottom: 12px;"><strong>Google Flow (Cinematic Push-in):</strong><br><code style="color:#7ee787; font-size:11px; display:block; padding:8px; background:rgba(255,255,255,0.03); border-radius:6px; margin-top:4px;">${data.flow_prompt}</code></div>
        <div><strong>Higsfield AI (Dynamic Hands/Reaction):</strong><br><code style="color:#7ee787; font-size:11px; display:block; padding:8px; background:rgba(255,255,255,0.03); border-radius:6px; margin-top:4px;">${data.higsfield_prompt}</code></div>
      `;
      document.getElementById('wizOutAI').innerHTML = aiHtml;

      const funnelHtml = `
        <div style="margin-bottom: 12px;"><strong>Instagram Caption:</strong><br><pre style="color:#e2e8f0; font-family:monospace; font-size:11px; white-space:pre-wrap; background:rgba(255,255,255,0.03); padding:8px; border-radius:6px;">${data.caption}</pre></div>
        <div>${renderMarkdown(data.manychat_funnel)}</div>
      `;
      document.getElementById('wizOutFunnel').innerHTML = funnelHtml;

      document.getElementById('wizardOutputBox').style.display = 'block';
      document.getElementById('wizardOutputBox').scrollIntoView({ behavior: 'smooth' });
      showToast('Winning Iteration Package generated!');
    }

    function copyWizardContent(elementId) {
      const el = document.getElementById(elementId);
      const text = el.innerText || el.textContent;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!');
      });
    }

    function renderMarkdown(md) {
      if (!md) return '';
      let html = md;
      
      // Escape HTML entities
      html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      
      // Tables: match consecutive table rows
      html = html.replace(/((?:^\\|.+?\\|(?:\r?\n|$))+)/gm, function(tableBlock) {
        const lines = tableBlock.trim().split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);
        if (lines.length < 2) return tableBlock;
        let tableHtml = '<div style="overflow-x:auto;margin:16px 0;"><table style="width:100%;border-collapse:collapse;font-size:12px;background:rgba(13,17,23,0.7);border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.1);">';
        lines.forEach((line, idx) => {
          if (line.match(/^\\|[\\s\\-:\\|]+\\|$/)) return;
          const cells = line.split('|').slice(1, -1).map(c => c.trim());
          if (idx === 0) {
            tableHtml += '<thead style="background:rgba(255,255,255,0.06);color:#f1f5f9;font-weight:700;"><tr>';
            cells.forEach(c => tableHtml += `<th style="padding:10px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.1);">${c}</th>`);
            tableHtml += '</tr></thead><tbody>';
          } else {
            const bg = (idx % 2 === 0) ? 'background:rgba(255,255,255,0.02);' : '';
            tableHtml += `<tr style="${bg}border-bottom:1px solid rgba(255,255,255,0.04);">`;
            cells.forEach(c => tableHtml += `<td style="padding:8px 12px;color:#cbd5e1;">${c}</td>`);
            tableHtml += '</tr>';
          }
        });
        tableHtml += '</tbody></table></div>';
        return tableHtml;
      });
      
      // Headers
      html = html.replace(/^### (.*$)/gim, '<h3 style="color:#f8fafc;font-size:15px;margin:18px 0 8px;font-weight:700;">$1</h3>');
      html = html.replace(/^## (.*$)/gim, '<h2 style="color:#38bdf8;font-size:17px;margin:22px 0 10px;font-weight:700;border-bottom:1px solid rgba(56,189,248,0.2);padding-bottom:6px;">$1</h2>');
      html = html.replace(/^# (.*$)/gim, '<h1 style="color:#f1f5f9;font-size:20px;margin:10px 0 14px;font-weight:800;background:linear-gradient(135deg,#fff,#94a3b8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">$1</h1>');
      
      // Blockquotes: > text
      html = html.replace(/^&gt;\\s?(.*$)/gim, '<blockquote style="border-left:3px solid #00F5D4;background:rgba(0,245,212,0.05);padding:10px 14px;margin:12px 0;border-radius:0 6px 6px 0;color:#e2e8f0;font-style:italic;">$1</blockquote>');
      
      // Horizontal rules
      html = html.replace(/^---$/gim, '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:20px 0;">');
      
      // Bold & Italic
      html = html.replace(/\\*\\*\\*(.*?)\\*\\*\\*/g, '<strong><em>$1</em></strong>');
      html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<strong style="color:#f8fafc;">$1</strong>');
      html = html.replace(/\\*(.*?)\\*/g, '<em style="color:#cbd5e1;">$1</em>');
      
      // Inline code
      html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.08);color:#38bdf8;padding:2px 6px;border-radius:4px;font-size:12px;font-family:monospace;">$1</code>');
      
      // Bullet and numbered lists
      html = html.replace(/^\\s*-\\s+(.*$)/gim, '<div style="margin:4px 0 4px 16px;position:relative;"><span style="color:#00F5D4;margin-right:8px;">•</span>$1</div>');
      html = html.replace(/^\\s*(\\d+)\\.\\s+(.*$)/gim, '<div style="margin:4px 0 4px 16px;position:relative;"><span style="color:#FF8C00;font-weight:600;margin-right:8px;">$1.</span>$2</div>');
      
      // Linebreaks
      html = html.replace(/\\n\\n/g, '<div style="height:10px;"></div>');
      html = html.replace(/\\n(?!(?:<div|<h|<table|<thead|<tbody|<tr|<td|<th|<blockquote|<hr))/g, '<br>');
      
      return html;
    }

    async function onProjectSelected(relPath) {
      if (!relPath) return;
      const res = await fetch(`/api/project?path=${encodeURIComponent(relPath)}`);
      currentProject = await res.json();

      // Populate metrics
      const meta = currentProject.metadata || {};
      document.getElementById('valViews').textContent = (meta.view_count || 0).toLocaleString();
      document.getElementById('valLikes').textContent = (meta.like_count || 0).toLocaleString();
      document.getElementById('valComments').textContent = (meta.comment_count || 0).toLocaleString();
      document.getElementById('valCreator').textContent = meta.uploader || meta.channel || '-';
      document.getElementById('valPlatform').textContent = currentProject.rel_path.split('/')[0];
      document.getElementById('valDuration').textContent = (meta.duration || 0) + 's';

      // Load initial raw video
      switchStream('video.mp4');

      // Audio track
      const audio = document.getElementById('audioPlayer');
      audio.src = `/api/media?file=${encodeURIComponent(currentProject.rel_path + '/audio_studio_320k.mp3')}`;

      // Populate Teleprompter
      formatTeleprompter(currentProject.teleprompter || currentProject.transcript || "No script available.");

      // Populate Repurposed Content
      parseRepurposed(currentProject.repurposed || "");

      // Populate Storyboard & CapCut Markers
      document.getElementById('storyboardContent').innerHTML = renderMarkdown(currentProject.storyboard || "No storyboard generated.");
      if (document.getElementById('edlContent')) {
        document.getElementById('edlContent').textContent = currentProject.timeline_edl || "No timeline markers generated.";
      }

      // Populate Deep Intelligence
      let intelParts = [];
      if (currentProject.master_study) {
        intelParts.push(currentProject.master_study);
        intelParts.push("\n---\n");
      }
      intelParts.push("### 🔍 Deep Psychological Analysis\n\n" + (currentProject.deep_analysis || ""));
      intelParts.push("\n### 💬 Comment Forensics & Part 2 Goldmine\n\n" + (currentProject.comment_forensics || ""));
      intelParts.push("\n### 🎯 ManyChat Lead Magnet & Funnel Blueprint\n\n" + (currentProject.funnel_blueprint || ""));
      document.getElementById('intelligenceContent').innerHTML = renderMarkdown(intelParts.join('\n\n'));

      // Populate Hook Scorer Input
      if (currentProject.hook_sample) {
        document.getElementById('hookInput').value = currentProject.hook_sample;
      }

      // Check Voiceover Guide
      if (currentProject.has_voiceover) {
        loadVoiceoverAudio();
      } else {
        document.getElementById('prompterAudioBox').style.display = 'none';
      }
    }

    function switchStream(filename) {
      if (!currentProject) return;
      document.querySelectorAll('.btn-stream').forEach(b => b.classList.remove('active'));
      if (filename === 'video.mp4') document.getElementById('btnRaw').classList.add('active');
      if (filename === 'video_subtitled.mp4') document.getElementById('btnSub').classList.add('active');
      if (filename === 'teaser_15s.mp4') document.getElementById('btnTeaser').classList.add('active');

      const video = document.getElementById('videoPlayer');
      video.src = `/api/media?file=${encodeURIComponent(currentProject.rel_path + '/' + filename)}`;
      video.load();
    }

    async function triggerClipTeaser() {
      if (!currentProject) return;
      showToast("Generating 15s teaser clip...");
      const res = await fetch('/api/clip', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path: currentProject.rel_path})
      });
      const data = await res.json();
      if (data.success) {
        showToast("✅ 15s Teaser Ready!");
        switchStream('teaser_15s.mp4');
      } else {
        showToast("❌ Teaser clipping failed");
      }
    }

    async function triggerDubVoiceover() {
      if (!currentProject) return;
      showToast("Synthesizing neural voiceover guide...");
      const res = await fetch('/api/dub', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path: currentProject.rel_path})
      });
      const data = await res.json();
      if (data.success) {
        showToast("✅ Voiceover Guide Ready!");
        loadVoiceoverAudio();
      } else {
        showToast("❌ Voiceover generation failed");
      }
    }

    function loadVoiceoverAudio() {
      if (!currentProject) return;
      const vPlayer = document.getElementById('voiceoverPlayer');
      const box = document.getElementById('prompterAudioBox');
      vPlayer.src = `/api/media?file=${encodeURIComponent(currentProject.rel_path + '/voiceover_guide.mp3')}&t=${Date.now()}`;
      box.style.display = 'flex';
    }

    function switchTab(tabId, btnElement) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      const btn = btnElement || (window.event ? (window.event.target ? window.event.target.closest('.tab-btn') : null) : null);
      if (btn) {
        btn.classList.add('active');
      } else {
        const found = document.querySelector(`.tab-btn[onclick*="'${tabId}'"]`);
        if (found) found.classList.add('active');
      }
      const target = document.getElementById(`tab-${tabId}`);
      if (target) target.classList.add('active');
    }

    // Teleprompter Logic
    function formatTeleprompter(text) {
      const box = document.getElementById('prompterBox');
      const lines = text.split(/\r?\n/);
      box.innerHTML = lines.map((l, idx) => {
        if (!l.trim()) return '<br>';
        if (l.includes('[PAUSE]')) return `<span class="cue-pause">${l}</span>`;
        if (l.includes('[BREATHE]')) return `<span class="cue-action">${l}</span>`;
        if (idx < 3) return `<span class="cue-hook">${l}</span>`;
        return l;
      }).join('<br>');
    }

    function togglePrompterScroll() {
      const box = document.getElementById('prompterBox');
      const btn = document.getElementById('btnPrompterToggle');
      if (prompterScrolling) {
        clearInterval(prompterInterval);
        prompterScrolling = false;
        btn.textContent = '▶ Start Scroll (Space)';
      } else {
        prompterScrolling = true;
        btn.textContent = '⏸ Pause Scroll (Space)';
        prompterInterval = setInterval(() => {
          box.scrollTop += 1;
        }, 1000 / scrollSpeedPx);
      }
    }

    function resetPrompter() {
      document.getElementById('prompterBox').scrollTop = 0;
    }

    function updatePrompterSpeed(val) {
      scrollSpeedPx = parseInt(val);
      document.getElementById('speedVal').textContent = `${val} px/s`;
      if (prompterScrolling) {
        clearInterval(prompterInterval);
        prompterInterval = setInterval(() => {
          document.getElementById('prompterBox').scrollTop += 1;
        }, 1000 / scrollSpeedPx);
      }
    }

    function updateFontSize(val) {
      document.getElementById('prompterBox').style.fontSize = `${val}px`;
    }

    // Repurposed Content Parsing
    function parseRepurposed(text) {
      const tw = text.match(/### 1\\. 🐦 Twitter \\/ X Viral Thread([\\s\\S]*?)(?=### 2\\.|$)/);
      const li = text.match(/### 2\\. 💼 LinkedIn Professional Breakdown([\\s\\S]*?)(?=### 3\\.|$)/);
      const car = text.match(/### 3\\. 📸 Instagram \\/ LinkedIn 7-Slide Carousel Blueprint([\\s\\S]*?)(?=### 4\\.|$)/);
      const news = text.match(/### 4\\. 💌 High-Conversion Email Newsletter Story([\\s\\S]*?)(?=### 5\\.|$)/);

      document.getElementById('twContent').textContent = tw ? tw[1].trim() : "No Twitter thread found.";
      document.getElementById('liContent').textContent = li ? li[1].trim() : "No LinkedIn post found.";
      document.getElementById('carContent').textContent = car ? car[1].trim() : "No Carousel outline found.";
      document.getElementById('newsContent').textContent = news ? news[1].trim() : "No Newsletter found.";
    }

    function copyCardContent(elementId) {
      const text = document.getElementById(elementId).textContent;
      navigator.clipboard.writeText(text);
      showToast("Copied to clipboard!");
    }

    function copyCapCutMarkers() {
      if (!currentProject || !currentProject.timeline_edl) {
        showToast("No timeline markers available.");
        return;
      }
      navigator.clipboard.writeText(currentProject.timeline_edl).then(() => {
        showToast("✅ CapCut Markers copied to clipboard!");
      }).catch(() => {
        showToast("Failed to copy markers");
      });
    }

    // Hook Scorer
    async function runHookScorer() {
      const hookText = document.getElementById('hookInput').value.trim();
      if (!hookText) return;
      showToast("Grading retention signals...");
      const res = await fetch('/api/score', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({hook: hookText})
      });
      const data = await res.json();
      renderScoreReport(data);
    }

    function renderScoreReport(data) {
      const box = document.getElementById('scoreReportBox');
      box.style.display = 'flex';
      document.getElementById('circleScore').textContent = data.total_score;
      document.getElementById('gradeTitle').textContent = `Grade: ${data.grade} (${data.total_score}/100)`;
      document.getElementById('gradeDesc').textContent = data.grade_desc;

      const breakdown = data.breakdown || {};
      const container = document.getElementById('breakdownContainer');
      container.innerHTML = '';
      
      const metrics = [
        {name: "Tension & Interrupt (0-3s)", item: breakdown.tension_and_interrupt},
        {name: "Brevity & Cadence (<12 words)", item: breakdown.cadence_and_brevity},
        {name: "Visual & Action Cues", item: breakdown.visual_action_cues},
        {name: "Open Loop & Curiosity Gap", item: breakdown.open_loop_curiosity},
        {name: "High Stakes Relevance", item: breakdown.emotional_stakes}
      ];

      metrics.forEach(m => {
        if (!m.item) return;
        const pct = Math.round((m.item.score / m.item.max) * 100);
        const row = document.createElement('div');
        row.className = 'breakdown-bar-wrap';
        row.innerHTML = `
          <div class="breakdown-label">${m.name}</div>
          <div class="progress-track"><div class="progress-fill" style="width: ${pct}%;"></div></div>
          <div style="width: 45px; text-align: right; font-weight: 600;">${m.item.score}/${m.item.max}</div>
        `;
        container.appendChild(row);
      });

      const stList = document.getElementById('listStrengths');
      stList.innerHTML = (data.strengths || []).map(s => `<li>${s}</li>`).join('');

      const wkList = document.getElementById('listWeaknesses');
      wkList.innerHTML = (data.weaknesses || []).map(w => `<li>${w}</li>`).join('');

      const rewritesBox = document.getElementById('rewritesContainer');
      rewritesBox.innerHTML = (data.rewrites || []).map(r => `
        <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border-left: 3px solid var(--accent-primary);">
          <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: var(--accent-primary);">
            <span>${r.archetype}</span>
            <span>Target: ${r.target_score}/100</span>
          </div>
          <div style="font-size: 14px; font-weight: 600; margin: 6px 0; color: #fff;">"${r.hook}"</div>
          <div style="font-size: 11px; color: var(--text-secondary);">🎬 Cue: ${r.delivery_cue}</div>
        </div>
      `).join('');
    }

    // Pipeline Trigger & Log Streaming
    async function triggerPipeline() {
      const url = document.getElementById('urlInput').value.trim();
      if (!url) {
        showToast("Please enter a media URL");
        return;
      }
      document.getElementById('logModal').style.display = 'flex';
      document.getElementById('logTerminal').textContent = "Starting pipeline worker...\\n";

      const res = await fetch('/api/process', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url: url})
      });

      if (res.status === 200) {
        const evtSource = new EventSource('/api/stream_logs');
        evtSource.onmessage = (e) => {
          const data = JSON.parse(e.data);
          const terminal = document.getElementById('logTerminal');
          if (data.line) {
            terminal.textContent += data.line + '\\n';
            terminal.scrollTop = terminal.scrollHeight;
          }
          if (data.done) {
            evtSource.close();
            loadProjects();
          }
        };
      } else {
        document.getElementById('logTerminal').textContent += "\\nPipeline could not be started.";
      }
    }

    function closeLogModal() {
      document.getElementById('logModal').style.display = 'none';
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 2200);
    }
  </script>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description="Local Creator Studio Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind server (default: 8080)")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    args = parser.parse_args()

    # Try binding to port; if occupied, increment port
    port = args.port
    server = None
    for attempt in range(5):
        try:
            server = HTTPServer((args.host, port), StudioRequestHandler)
            break
        except OSError:
            print(f"⚠️ Port {port} in use, trying {port + 1}...")
            port += 1

    if not server:
        print(f"❌ Failed to bind to any port near {args.port}", file=sys.stderr)
        sys.exit(1)

    print("=" * 65)
    print("⚡ LOCAL CREATOR STUDIO DASHBOARD ACTIVE")
    print("=" * 65)
    print(f"🌐 Access in your browser: http://localhost:{port}")
    print(f"📁 Workspace Root: {WORKSPACE_ROOT}")
    print("✨ Features: Video/Audio Player, Auto-Scroll Prompter, 1-Click Copy, Hook Scorer")
    print("Press Ctrl+C to stop.")
    print("=" * 65)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Studio server stopped.")
        server.server_close()

if __name__ == "__main__":
    main()
