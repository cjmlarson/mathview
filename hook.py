#!/usr/bin/env python3
"""Claude Code Stop hook: mirror the last math-bearing assistant message
to latest.md for the MathView browser page.

Reads the hook payload on stdin, scans the transcript backwards for the
last non-sidechain assistant message containing text blocks, and writes
its text to latest.md iff it contains $...$ / $$...$$ math. Lazily
starts the static server via serve.sh. Always exits 0 (never blocks).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

MATHVIEW = Path(__file__).resolve().parent
MATH_RE = re.compile(r"\$\$[\s\S]+?\$\$|\$[^$\n]+\$")


def last_assistant_text(transcript_path: str) -> str | None:
    try:
        lines = Path(transcript_path).read_text().splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("isSidechain"):
            continue
        msg = rec.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        texts = [b.get("text", "") for b in msg.get("content", [])
                 if isinstance(b, dict) and b.get("type") == "text"]
        if texts:
            return "\n\n".join(texts)
    return None


def main() -> None:
    payload = json.load(sys.stdin)
    text = last_assistant_text(payload.get("transcript_path", ""))
    if not text or not MATH_RE.search(text):
        return
    (MATHVIEW / "latest.md").write_text(text)
    subprocess.Popen([str(MATHVIEW / "serve.sh")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # TODO: systemMessage not appearing in the Claude Code TUI even after
    # /hooks reload (2026-08-12). Check if a full Claude Code restart fixes
    # it; if not, debug (async vs sync output handling? focus mode?) and fix.
    print(json.dumps({"systemMessage":
                      "math detected, view rendered here: "
                      "http://localhost:8321/viewer.html"}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a viewer glitch must never block the session
    sys.exit(0)
