---
name: teamkm-mcp-setup
description: >-
  Wire Cursor or another MCP host to TeamKM: pip install ".[mcp]", run ki serve
  plus ki mcp (stdio), TEAMKM_API_BASE / KI_HOST / KI_PORT, example MCP config.
  Use when configuring MCP, TeamKM tools in the IDE, or teamkm_* not working.
---

# TeamKM — MCP setup

**Read first:** [docs/MCP.md](../../../docs/MCP.md) • [CONTRIBUTING.md](../../../CONTRIBUTING.md) (Optional: MCP).

## Architecture (one sentence)

**`ki serve`** owns the index and HTTP API. **`ki mcp`** is a **stdio** process whose tools **HTTP-call** that API. The **IDE** runs the agent loop.

## 1. Install

From repo root (venv recommended):

```bash
pip install -e ".[mcp]"
```

## 2. Two processes

**Terminal A — API (must be running):**

```bash
python3 -m ki --root . index    # if stale or first run
python3 -m ki --root . serve --host 127.0.0.1 --port 8765
```

**Terminal B — MCP (stdio; host usually launches this):**

```bash
cd /path/to/TeamKM
python3 -m ki mcp
```

`ki mcp` blocks on **stdin**; do not run it in a terminal you need for typing. Cursor starts it as a **child process**.

## 3. Environment

| Variable | Purpose |
|----------|---------|
| `TEAMKM_API_BASE` | Full URL, e.g. `http://127.0.0.1:8765` (no trailing `/`) |
| `KI_HOST` / `KI_PORT` | Used when `TEAMKM_API_BASE` unset (defaults `127.0.0.1` / `8765`) |

MCP subprocess **cwd** should be the **repo root** so relative paths behave consistently.

## 4. Cursor MCP config (example)

Add a server entry (location depends on Cursor version: **Settings → MCP** or project MCP config). Adapt paths to the user machine:

```json
{
  "mcpServers": {
    "teamkm": {
      "command": "/path/to/TeamKM/.venv/bin/python3",
      "args": ["-m", "ki", "mcp"],
      "cwd": "/path/to/TeamKM",
      "env": {
        "TEAMKM_API_BASE": "http://127.0.0.1:8765"
      }
    }
  }
}
```

If `ki` is on PATH from `pip install -e ".[mcp]"`:

```json
{
  "mcpServers": {
    "teamkm": {
      "command": "python3",
      "args": ["-m", "ki", "mcp"],
      "cwd": "/absolute/path/to/TeamKM"
    }
  }
}
```

Restart MCP / reload window after changes.

## 5. Tools exposed

| MCP tool | HTTP |
|----------|------|
| `teamkm_health` | `GET /v1/health` |
| `teamkm_retrieve` | `POST /v1/retrieve` |
| `teamkm_context_pack` | `POST /v1/context_pack` |
| `teamkm_contribute_dry_run` | `POST /v1/contribute_dry_run` |

Prompt: **`teamkm_retrieve_first`**.

## 6. Stdio rules

- MCP uses **stdin/stdout** for JSON-RPC. **Do not** `print()` debug to stdout on the MCP process (breaks the wire). Use **logging to stderr** if needed.
- **`ki serve`** is separate; it **does** log to stderr (`TeamKM listening on http://...`).

## 7. Verify

1. `curl -s http://127.0.0.1:8765/v1/health` → 200, `index_status` ready.
2. In Cursor MCP panel, confirm **teamkm** server connected and list tools.
3. Call `teamkm_health` from the host; should mirror curl JSON.

## 8. Policy for agents

After MCP works, use skill **teamkm-retrieve-first**: health → retrieve/context_pack → cite `doc_path` → then edit code or knowledge.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| MCP tools fail with connection error | Start **`ki serve`** first; check `TEAMKM_API_BASE` |
| Wrong cwd | Set `"cwd"` to repo root in MCP config |
| `Install MCP support` from CLI | `pip install -e ".[mcp]"` |
| Inspector / `mcp dev` | `uv run mcp dev path/to/ki/mcp_server.py` (advanced; module entry is `ki.mcp_server`) |
