#!/usr/bin/env bash
# Session wrapper (REQUIREMENTS §12.1 pattern B): start local API then exec assistant.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export KI_HOST="${KI_HOST:-127.0.0.1}"
export KI_PORT="${KI_PORT:-8765}"
python3 -m ki index --root "$ROOT" >/dev/null 2>&1 || true
python3 -m ki serve --root "$ROOT" --host "$KI_HOST" --port "$KI_PORT" &
KI_PID=$!
cleanup() { kill "$KI_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
sleep 0.3
exec "$@"
