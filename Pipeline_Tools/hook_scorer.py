#!/usr/bin/env python3
"""
Pre-Filming AI Hook & Script Scorer
===================================
Grades hook lines and video scripts from 1 to 100 on 5 algorithmic retention signals:
1. Immediate Tension & Pattern Interrupt (0-3s)
2. Brevity & Cadence (<12 words)
3. Visual & Physical Action Cues
4. Open Loop & Delayed Payoff
5. Emotional Stakes & Self-Relevance

Outputs:
- Retention Score (1-100) & Grade (S, A, B, C, F)
- Detailed diagnostic breakdown
- 3 AI-optimized high-voltage rewrite variants

Usage:
  python3 Pipeline_Tools/hook_scorer.py --hook "I turned three old Android phones into an autonomous AI robot."
  python3 Pipeline_Tools/hook_scorer.py --file "path/to/script.txt"
"""

import sys
import os
import re
import json
import argparse

# Fluff phrases that kill retention in the first 3 seconds
FLUFF_PATTERNS = [
    r"\bhey guys\b", r"\bwelcome back\b", r"\bin this video\b",
    r"\btoday i am going to\b", r"\btoday i want to\b", r"\bso basically\b",
    r"\bhi everyone\b", r"\bwhats up guys\b", r"\bmake sure to subscribe\b",
    r"\bdont forget to like\b", r"\blet me know in the comments\b"
]

# Action verbs that indicate on-screen movement/props (including inflections)
ACTION_VERBS = {
    "built", "build", "building", "turned", "turn", "turning", "plugged", "plug", "plugging",
    "tested", "test", "testing", "show", "showing", "watch", "watching", "look", "looking",
    "connected", "connect", "connecting", "coded", "code", "coding", "wired", "wire", "wiring",
    "smashed", "dropped", "hacked", "hack", "hacking", "press", "pressed", "pushed", "push",
    "installed", "install", "unboxed", "fixed", "fix", "ran", "run", "running", "created",
    "create", "creating", "transformed", "transform", "made", "make", "making",
    "replace", "replaced", "replacing", "automate", "automated", "automating", "kill", "killed"
}

NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100", "1000", "million", "billion"
}

# Tension / Pattern Interrupt triggers
TENSION_WORDS = {
    "never", "stop", "mistake", "secret", "illegal", "warning", "ruined", "ruin",
    "nobody", "truth", "exposed", "built", "tested", "hacked", "broke", "break",
    "autonomous", "insane", "impossible", "lie", "banned", "danger", "dangerous",
    "deadly", "destroy", "crazy", "flaw", "shocking", "worst", "best", "superpower",
    "ultron", "ironman", "jarvis", "drone", "army", "robot", "hacked", "hacker",
    "just", "entire", "team", "engineer", "engineering", "free", "dead", "future"
}

# Curiosity gap / Open loop markers
OPEN_LOOP_MARKERS = [
    r"\bhere is what happened\b", r"\bheres what happened\b", r"\band it actually\b",
    r"\buntil this happened\b", r"\bthe result\b", r"\bwhat happens next\b",
    r"\bno one expected\b", r"\bthe crazy part\b", r"\bthe secret\b",
    r"\bwatch what happens\b", r"\bsee what happens\b", r"\bbut then\b"
]

# High stakes / emotional impact words
STAKES_WORDS = {
    "money", "replace", "future", "free", "save", "risk", "dollar", "hours",
    "game-changer", "ai", "cost", "salary", "job", "billion", "million",
    "army", "superpower", "control", "danger"
}

def extract_hook_from_text(text):
    """Extracts the first 1-2 sentences of the text as the hook."""
    clean = re.sub(r'[\r\n]+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    if not sentences or not sentences[0]:
        return text.strip()
    if len(sentences) >= 2 and len(sentences[0].split()) < 7:
        return f"{sentences[0]} {sentences[1]}"
    return sentences[0]

def score_hook(hook_text, full_script=None):
    """
    Analyzes hook_text and returns a comprehensive score dictionary.
    """
    hook = hook_text.strip()
    lower_hook = hook.lower()
    words = re.findall(r'\b[\w\'-]+\b', lower_hook)
    word_count = len(words)

    diagnostics = []
    strengths = []
    weaknesses = []

    # 1. Fluff Penalty Check
    fluff_found = []
    for fp in FLUFF_PATTERNS:
        if re.search(fp, lower_hook):
            fluff_found.append(fp.replace(r'\b', ''))

    # 2. Brevity & Cadence (Max 20 pts)
    cadence_score = 0
    if word_count == 0:
        cadence_score = 0
        weaknesses.append("Hook is empty.")
    elif 1 <= word_count <= 10:
        cadence_score = 20
        strengths.append(f"Ultra-punchy word count ({word_count} words). Fast retention lock.")
    elif 11 <= word_count <= 14:
        cadence_score = 16
        strengths.append(f"Good cadence ({word_count} words), under the 15-word threshold.")
    elif 15 <= word_count <= 20:
        cadence_score = 10
        weaknesses.append(f"Borderline wordy ({word_count} words). Aim for under 12 words.")
    else:
        cadence_score = 4
        weaknesses.append(f"Too long ({word_count} words). Viewers scroll away before completion.")

    # 3. Tension & Pattern Interrupt (Max 25 pts)
    tension_score = 0
    found_tension = [w for w in words if w in TENSION_WORDS]
    has_numbers = bool(re.search(r'\b\d+([kKmM%]?|\$)?\b', hook)) or any(w in NUMBER_WORDS for w in words)

    if found_tension:
        tension_score += min(15, len(found_tension) * 8)
        strengths.append(f"Pattern interrupt cues detected: {', '.join(found_tension[:3])}.")
    if has_numbers:
        tension_score += 10
        strengths.append("Contains concrete metrics/numbers (instant cognitive anchor).")

    if tension_score == 0:
        weaknesses.append("No immediate conflict, contrarian claim, or provocative anomaly.")
    tension_score = min(25, tension_score)

    # 4. Visual & Physical Action Cues (Max 20 pts)
    action_score = 0
    found_actions = [w for w in words if w in ACTION_VERBS]
    if found_actions:
        action_score = min(20, len(found_actions) * 10)
        strengths.append(f"Active physical cues: {', '.join(found_actions[:2])} (signals dynamic movement).")
    else:
        weaknesses.append("Lacks active physical verbs. Risk of static talking-head delivery.")

    # 5. Open Loop & Curiosity Gap (Max 20 pts)
    open_loop_score = 0
    for pattern in OPEN_LOOP_MARKERS:
        if re.search(pattern, lower_hook):
            open_loop_score += 15
            strengths.append("High curiosity gap phrase triggers open loop anticipation.")
            break

    # High-concept transformation or intriguing promise ("turned X into Y", "how to", "building X in public")
    if any(phrase in lower_hook for phrase in ["into an", "into a", "in public", "how to", "how i", "secret to", "why "]):
        open_loop_score += 10
        strengths.append("Transforms a common object or process into a novel curiosity loop.")

    # If full script is provided, check if open loop resolves later
    if full_script and len(full_script.split()) > word_count + 15:
        open_loop_score += 5
    elif "?" in hook:
        open_loop_score += 10
        strengths.append("Direct question stimulates cognitive response.")

    open_loop_score = min(20, open_loop_score)
    if open_loop_score < 10:
        weaknesses.append("Weak open loop; resolution may feel too immediate or unclear.")

    # 6. Emotional Stakes & Self-Relevance (Max 15 pts)
    stakes_score = 0
    found_stakes = [w for w in words if w in STAKES_WORDS]
    if found_stakes:
        stakes_score = min(15, len(found_stakes) * 8)
        strengths.append(f"High-stakes thematic anchors: {', '.join(found_stakes[:2])}.")
    else:
        stakes_score = 5

    # Fluff penalty deduction
    penalty = len(fluff_found) * 20
    if fluff_found:
        weaknesses.append(f"Deadly fluff detected ({', '.join(fluff_found)}). Causes -{penalty} pts!")

    # Calculate Total
    raw_total = cadence_score + tension_score + action_score + open_loop_score + stakes_score - penalty
    final_score = max(5, min(99, raw_total))

    # Letter Grade
    if final_score >= 90:
        grade = "S"
        grade_desc = "Viral Contender (Elite Retention)"
    elif final_score >= 80:
        grade = "A"
        grade_desc = "High Retention (Above Average)"
    elif final_score >= 70:
        grade = "B"
        grade_desc = "Good (Needs Tightening)"
    elif final_score >= 55:
        grade = "C"
        grade_desc = "Average (High Drop-off Risk)"
    else:
        grade = "F"
        grade_desc = "Fluff Alert (Imminent Swipe-Away)"

    # Generate 3 AI-Optimized High-Voltage Rewrites
    rewrites = generate_rewrites(hook, found_actions, found_tension, has_numbers)

    return {
        "hook": hook,
        "word_count": word_count,
        "total_score": final_score,
        "grade": grade,
        "grade_desc": grade_desc,
        "breakdown": {
            "cadence_and_brevity": {"score": cadence_score, "max": 20},
            "tension_and_interrupt": {"score": tension_score, "max": 25},
            "visual_action_cues": {"score": action_score, "max": 20},
            "open_loop_curiosity": {"score": open_loop_score, "max": 20},
            "emotional_stakes": {"score": stakes_score, "max": 15},
            "penalty_deductions": penalty
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "fluff_detected": fluff_found,
        "rewrites": rewrites
    }

def generate_rewrites(hook, actions, tension, has_numbers):
    """Synthesizes 3 proven retention archetypes based on the hook topic."""
    # Clean out fluff
    core = re.sub(r'^(hey guys|in this video|today i am going to|i want to show you)\s*,?\s*', '', hook, flags=re.IGNORECASE).strip()
    core = core[0].upper() + core[1:] if core else "This experiment"

    # Variant 1: The Pattern Interrupt / Shock Hook (< 10 words)
    v1 = f"Stop doing this. I turned {core.rstrip('.')} into an autonomous system." if "built" in core.lower() or "turned" in core.lower() else f"Nobody told you the truth about {core.rstrip('.')}."
    
    # Variant 2: The Proof & Anomaly Hook (Physical action + Number)
    v2 = f"Watch this: 3 lines of code just replaced an entire workflow." if "code" in core.lower() or "ai" in core.lower() else f"I tested this live: {core.rstrip('.')} in under 60 seconds."

    # Variant 3: The High-Stakes Curiosity Gap (Open Loop)
    v3 = f"Everyone said this was impossible—until this happened."

    return [
        {
            "archetype": "The Pattern Interrupt (0-3s Shock)",
            "hook": v1,
            "target_score": 94,
            "delivery_cue": "Show immediate close-up physical motion with zero verbal preamble."
        },
        {
            "archetype": "The Proof & Anomaly (Tangible Live Test)",
            "hook": v2,
            "target_score": 91,
            "delivery_cue": "Point camera directly at the screen or prop before talking."
        },
        {
            "archetype": "The High-Stakes Curiosity Gap (Unresolved Loop)",
            "hook": v3,
            "target_score": 89,
            "delivery_cue": "Fast whip-pan transition into the middle of the climax."
        }
    ]

def print_terminal_report(res):
    """Outputs an aesthetically formatted report to terminal."""
    print("=" * 65)
    print(f"🎯 VIRAL HOOK RETENTION REPORT: [{res['grade']}-TIER] ({res['total_score']}/100)")
    print(f"   Verdict: {res['grade_desc']}")
    print("=" * 65)
    print(f"📝 Analyzed Hook: \"{res['hook']}\"")
    print(f"📊 Length: {res['word_count']} words\n")

    print("--- 🔬 Retention Signals Breakdown ---")
    b = res['breakdown']
    print(f" • Immediate Tension & Interrupt:  {b['tension_and_interrupt']['score']:>2}/{b['tension_and_interrupt']['max']} pts")
    print(f" • Brevity & Cadence (<12 words):   {b['cadence_and_brevity']['score']:>2}/{b['cadence_and_brevity']['max']} pts")
    print(f" • Visual & Physical Action Cues:  {b['visual_action_cues']['score']:>2}/{b['visual_action_cues']['max']} pts")
    print(f" • Open Loop & Curiosity Gap:      {b['open_loop_curiosity']['score']:>2}/{b['open_loop_curiosity']['max']} pts")
    print(f" • Stakes & Audience Relevance:    {b['emotional_stakes']['score']:>2}/{b['emotional_stakes']['max']} pts")
    if b['penalty_deductions'] > 0:
        print(f" ⚠️ FLUFF PENALTY DEDUCTION:       -{b['penalty_deductions']} pts")

    print("\n--- ✅ Strengths ---")
    for s in res['strengths']:
        print(f"  + {s}")

    if res['weaknesses']:
        print("\n--- ⚠️ Retention Risks ---")
        for w in res['weaknesses']:
            print(f"  ! {w}")

    print("\n--- 🚀 3 High-Voltage Rewrites ---")
    for i, r in enumerate(res['rewrites'], 1):
        print(f"{i}. [{r['archetype']}] (Target: {r['target_score']}/100)")
        print(f"   \"{r['hook']}\"")
        print(f"   🎬 Director Cue: {r['delivery_cue']}\n")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Pre-Filming AI Hook & Script Scorer")
    parser.add_argument("--hook", help="Hook text to evaluate")
    parser.add_argument("--file", help="Path to text/script file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    text = None
    if args.hook:
        text = args.hook
    elif args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            print(f"❌ File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        print("🎙️ Enter your draft hook or script line below (Press Enter):")
        try:
            text = input("> ").strip()
        except EOFError:
            sys.exit(0)

    if not text:
        print("❌ No input provided.", file=sys.stderr)
        sys.exit(1)

    hook_line = extract_hook_from_text(text)
    result = score_hook(hook_line, full_script=text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_terminal_report(result)

if __name__ == "__main__":
    main()
