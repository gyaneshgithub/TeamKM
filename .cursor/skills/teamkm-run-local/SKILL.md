---
name: teamkm-run-local
description: >-
  Run Groundline locally: venv, pip install -e ".[dev]" or ".[mcp]", build index
  (ki --root . index), start HTTP API (ki serve), verify /v1/health. Use when
  the user says run Groundline, start the API, rebuild index, or local RAG is not
  working.
---

# Groundline — run locally

Workspace root = this repository (contains `knowledge/`, `pyproject.toml`, `ki/`).

## Python

Requires **Python 3.10+**. Prefer a venv:

```bash
cd /path/to/Groundline
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

## Install

**Core + tests:**

```bash
pip install -e ".[dev]"
```

**Optional MCP adapter** (for `python3 -m ki mcp`):

```bash
pip install -e ".[dev,mcp]"
```

## CLI argument order (important)

`--root` is a **global** flag on `ki`. It must come **before** the subcommand:

| Correct | Wrong |
|---------|--------|
| `python3 -m ki --root . index` | `python3 -m ki index --root .` |
| `python3 -m ki --root . serve` | `python3 -m ki serve --root .` |

From repo root you may omit `--root .` if cwd is the repo.

## Build or refresh index

```bash
python3 -m ki --root . index
```

- Writes under **`.rag/`** (gitignored).
- Re-run after pulling `main` when `knowledge/` changed materially.

## Start HTTP API (foreground)

```bash
python3 -m ki --root . serve --host 127.0.0.1 --port 8765
```

Overrides: `KI_HOST`, `KI_PORT`.

## Verify

```bash
curl -s http://127.0.0.1:8765/v1/health | python3 -m json.tool
```

Expect `index_status` in `ready` | `building` | `missing` (usually `ready` after index).

**Smoke retrieve:**

```bash
curl -s http://127.0.0.1:8765/v1/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"query":"Groundline","pack_k":5}' | python3 -m json.tool
```

## Two terminals (typical dev day)

| Terminal | Command |
|----------|---------|
| 1 | `python3 -m ki --root . serve` |
| 2 | Editor chat + optional `python3 -m ki mcp` (see **teamkm-mcp-setup**) |

## Session wrapper (optional)

[scripts/ki-session.sh](../../../scripts/ki-session.sh) starts `ki serve` in the background then `exec`s another command (e.g. your assistant CLI).

## Troubleshooting

| Symptom | Try |
|---------|-----|
| `index_unavailable` / 503 on retrieve | `python3 -m ki --root . index` |
| Port in use | Change `--port` or `KI_PORT` |
| Empty retrieval | Confirm `knowledge/` has `.md`; check health `chunk_count` |
| Stale answers | Re-index after merge; compare `corpus_fingerprint` in health |

## References

- [README.md](../../../README.md) — quick start
- [docs/HOW_TO_USE_GROUNDLINE.md](../../../docs/HOW_TO_USE_GROUNDLINE.md) — non-technical overview
- [docs/openapi.yaml](../../../docs/openapi.yaml) — API contract
