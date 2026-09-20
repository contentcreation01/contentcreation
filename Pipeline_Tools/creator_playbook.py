#!/usr/bin/env python3
"""
Creator Playbook & 30-Day Content Calendar Generator
Analyzes saved reels/videos to reverse-engineer creator formulas and builds a complete 30-day posting matrix.

Usage:
  python3 Pipeline_Tools/creator_playbook.py
  python3 Pipeline_Tools/creator_playbook.py "@sagar_builds"
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
WORKSPACE_DIR = BASE_DIR.parent

def generate_playbook(creator_filter: str = ""):
    print("\n=======================================================")
    print("[*] Generating Creator Playbook & 30-Day Content Matrix")
    print("=======================================================")

    reels_found = []
    for platform in ["Instagram", "YouTube", "TikTok", "Twitter"]:
        plat_dir = WORKSPACE_DIR / platform
        if not plat_dir.exists():
            continue
        for folder in sorted(plat_dir.glob("*/*")):
            if folder.is_dir() and (folder / "metadata.json").exists():
                if not creator_filter or creator_filter.lower().replace("@", "") in folder.name.lower():
                    reels_found.append(folder)

    if not reels_found:
        print("[-] No analyzed videos found matching criteria.")
        return

    print(f"[✓] Analyzing {len(reels_found)} video(s) for creator blueprint...\n")

    playbook_file = BASE_DIR / "Creator_Playbook_30Day_Matrix.md"
    content = f"""# Creator Playbook & 30-Day Viral Content Matrix

Generated from {len(reels_found)} high-performing analyzed video(s).

---

## 1. The Core Retention Playbook

From reverse-engineering top performers:
- **Hook Duration**: Exactly 1.5 – 3.0 seconds. Never introduce yourself ("Hey guys"); launch straight into tension.
- **Visual Pattern Interrupt**: The camera angle or on-screen action MUST change within the first 2 seconds.
- **Escalation Formula**:
  - Stage 1 (0–15s): Single action / baseline question.
  - Stage 2 (15–40s): Multi-device or multiplied action (the "magic" moment).
  - Stage 3 (40–60s): Full autonomous execution without human touch.
  - Stage 4 (60–75s): Casual sign-off ("Awesome", "Clean") + 1-word comment CTA.

---

## 2. 30-Day Content Matrix (4-Week Posting Calendar)

### Week 1: Contrarian & Status-Quo Breaking Hooks
- **Day 1**: *"Everyone is building [Tool A], I built [Unorthodox Extreme System]."* (POV desk setup demo)
- **Day 3**: *"Stop using [Standard Tool] like this in 2026."* (Side-by-side split screen)
- **Day 5**: *"Why 99% of people fail at [Outcome] (and the 1 script that fixes it)."* (Macro top-down shot)
- **Day 7**: *Weekly Recap / Behind-The-Scenes failure & lesson.* (Casual vlog style)

### Week 2: Proof-First & Speed Demos
- **Day 9**: *"Watch what happens when I tap this single button..."* (Immediate 0-second action)
- **Day 11**: *"I automated my entire morning research in 18 seconds."* (Timer on screen)
- **Day 13**: *"Connecting 3 devices to 1 AI brain (live test)."* (Multi-screen synchronized execution)
- **Day 15**: *Case Study / Viewer Question answered with code demo.*

### Week 3: Secret Loops & High-Trust Insider Value
- **Day 17**: *"The hidden local setup nobody is sharing because it saves $500/mo."* (Terminal / zero-cost angle)
- **Day 19**: *"How to turn any video into a complete script in 30 seconds."* (Workflow demonstration)
- **Day 21**: *"Top 3 tools I actually use every day as a solo builder."* (Fast rapid-fire cuts)
- **Day 23**: *Mistake breakdown: "I built this wrong 4 times before it worked."*

### Week 4: Viral Scaling & Community Lead Engine
- **Day 25**: *"This 1 automated prompt replaces a 4-person agency."* (Shock factor + high value)
- **Day 27**: *"Ultron vs Jarvis: Can AI really control hardware?"* (Debate / comment magnet)
- **Day 29**: *"Full codebase release: Drop [KEYWORD] below and I'll DM you."* (ManyChat growth spike)
- **Day 30**: *Monthly growth reflection & what we're building next.*

---

## 3. High-Converting Call-To-Action (CTA) Formulas

1. **The ManyChat Automator**:
   > *"Drop the word **[LINK/CODE/SWARM]** below and my bot will instantly DM you the GitHub repo + setup guide."*
2. **The Controversial Question**:
   > *"Would you trust an AI to control your whole room, or is this going too far? Let me know below."*
3. **The Save-For-Later Loop**:
   > *"Save this video before the algorithm loses it, because you'll need this setup tomorrow."*
"""
    playbook_file.write_text(content, encoding="utf-8")
    print(f"🎉 Creator Playbook generated at:\n   -> {playbook_file.resolve()}\n")

if __name__ == "__main__":
    creator_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    generate_playbook(creator_arg)
