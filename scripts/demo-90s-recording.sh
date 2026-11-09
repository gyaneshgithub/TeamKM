#!/usr/bin/env bash
# Groundline — 90s screen recording driver (see docs/DEMO.md § Screen recording).
# Usage: while recording (Cmd+Shift+5), run from repo root:
#   ./scripts/demo-90s-recording.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$ROOT/.venv/bin/activate"
fi

banner() {
  printf '\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n  %s\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n' "$1"
}

wait_step() {
  local label="$1"
  local secs="${2:-5}"
  banner "$label"
  if [[ "${DEMO_FAST:-0}" == "1" ]]; then
  echo "  (DEMO_FAST — skipping ${secs}s pause)"
    return
  fi
  for ((i = secs; i >= 1; i--)); do
    printf '  (%2ds)\r' "$i"
    sleep 1
  done
  printf '\n'
}

API_BASE="${TEAMKM_API_BASE:-http://127.0.0.1:8765}"

ensure_serve() {
  if curl -sf "${API_BASE}/v1/health" >/dev/null 2>&1; then
    echo "API already up at ${API_BASE}"
    return
  fi
  echo "Starting ki serve in background…"
  python3 -m ki --root . serve --host 127.0.0.1 --port "${KI_PORT:-8765}" &
  local pid=$!
  for _ in {1..30}; do
    if curl -sf "${API_BASE}/v1/health" >/dev/null 2>&1; then
      echo "API ready (pid ${pid})"
      return
    fi
    sleep 0.5
  done
  echo "ERROR: API did not become ready" >&2
  exit 1
}

banner "Groundline — 90s demo (DEMO.md checklist)"

# 1 — Merge narrative: knowledge in git (browser)
wait_step "1/4  GitHub — team knowledge in git (PR-reviewed markdown)" 18
open "https://github.com/gyaneshgithub/TeamKM/blob/main/knowledge/technical/meta/workflow-validation.md" \
  2>/dev/null || true

# 2 — Index + serve + status
wait_step "2/4  Terminal — index, serve, freshness (ki status)" 15
python3 -m ki --root . index
ensure_serve
python3 -m ki --root . status

# 3 — Retrieve with doc_path
wait_step "3/4  curl /v1/retrieve — citations (doc_path)" 22
curl -s "${API_BASE}/v1/retrieve" \
  -H 'Content-Type: application/json' \
  -d '{"query":"How does draft promotion work on merge to main?","candidate_k":24,"pack_k":6}' \
  | python3 -m json.tool | head -55

# 4 — Docs site
wait_step "4/4  MkDocs site — role-based public docs" 18
open "https://gyaneshgithub.github.io/TeamKM/" 2>/dev/null || true

banner "Done — stop recording (Ctrl+Cmd+Esc or menu bar stop)"
