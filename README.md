# mathview

Windows Terminal doesn't render math at all, and `/rc` remote control /
viewing on claude.ai is OK but not great — it shows display math
(`$$...$$`) but often not inline math (`$...$`) properly. This repo is a
solution until, hopefully, the Anthropic team solves their own web
viewer at some point :)

## How it works

A Claude Code `Stop` hook (`hook.py`, registered in
`~/.claude/settings.json`) fires after each response. If the last
assistant message contains dollar-delimited math, it writes the raw
markdown to `latest.md` and lazy-starts a static server (`serve.sh`,
port 8321). A pinned browser tab at

    http://localhost:8321/viewer.html

polls `latest.md` once a second and re-renders in place (marked +
KaTeX) only when the content changes — no reloads, no flicker.

`latest.md` is generated output, not tracked.
