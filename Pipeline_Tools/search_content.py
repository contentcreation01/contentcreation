#!/usr/bin/env python3
"""
Content Search Engine:
Quickly search across all downloaded transcripts, captions, and deep analysis files.
Usage: python3 Pipeline_Tools/search_content.py "keyword"
"""
import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
WORKSPACE_DIR = BASE_DIR.parent

def search_library(query: str):
    print(f"\n[*] Searching library for: '{query}'...\n")
    matches = 0
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for platform_dir in ["Instagram", "YouTube"]:
        plat_path = WORKSPACE_DIR / platform_dir
        if not plat_path.exists():
            continue

        for file_path in sorted(plat_path.glob("**/*.txt")) + sorted(plat_path.glob("**/*.md")):
            if "deep_analysis" in file_path.name or "caption" in file_path.name or "transcript" in file_path.name:
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                    lines = text.splitlines()
                    matching_lines = [line.strip() for line in lines if pattern.search(line)]
                    if matching_lines:
                        matches += 1
                        rel_path = file_path.relative_to(WORKSPACE_DIR)
                        print(f"📁 Match in: {rel_path}")
                        for line in matching_lines[:3]: # preview up to 3 lines
                            print(f"   ↳ {line}")
                        print()
                except Exception:
                    pass

    if matches == 0:
        print(f"[-] No results found for '{query}'.")
    else:
        print(f"[✓] Found matches in {matches} file(s).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 Pipeline_Tools/search_content.py <KEYWORD>")
        sys.exit(1)
    search_library(sys.argv[1])
