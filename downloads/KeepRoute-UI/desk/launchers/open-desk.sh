#!/usr/bin/env bash
# Open Aria on localhost (public builds never bake in lab LAN IPs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${ARIA_PORT:-${OMNIROUTE_DESK_PORT:-20129}}"
URL="http://127.0.0.1:${PORT}/"

if ! curl -sf --max-time 2 "http://127.0.0.1:${PORT}/api/status" >/dev/null; then
  nohup python3 "$ROOT/app.py" >>"$ROOT/state/desk.log" 2>&1 &
  for _ in $(seq 1 30); do
    curl -sf --max-time 1 "http://127.0.0.1:${PORT}/api/status" >/dev/null && break
    sleep 0.4
  done
fi

if command -v xdg-open >/dev/null 2>&1; then
  exec xdg-open "$URL"
elif command -v chromium >/dev/null 2>&1; then
  exec chromium --new-window "$URL"
else
  printf 'Aria: %s\n' "$URL"
fi
