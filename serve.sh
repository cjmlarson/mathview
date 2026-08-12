#!/usr/bin/env bash
# Serve the mathview dir on localhost:8321 if not already running.
# Safe to call repeatedly (e.g. from a Claude Code Stop hook).
PORT=8321
DIR="$(cd "$(dirname "$0")" && pwd)"
if ! curl -sf -o /dev/null "http://localhost:$PORT/viewer.html"; then
  nohup python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$DIR" \
    >/dev/null 2>&1 &
fi
