# For engineering

**You:** build, operate, and review the corpus and tooling. **Success:** CI-green PRs, a local index when you need grounded retrieval, optional MCP in the IDE.

---

## Week 1

1. Skim [How to use Groundline](HOW_TO_USE_GROUNDLINE.md) and [Contributing](contributing.md).
2. Clone **your team’s** repo (after [template adoption](REQUIREMENTS.md#45-adopting-this-repository-as-a-team-template)).
3. Run the quick start below; confirm `/v1/health` reports index ready.
4. Open a small `knowledge/technical/` doc via PR; let merge automation set `reviewed` if you used `draft`.

---

## Quick start (snippets)

```bash
cd /path/to/your-teamkm
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

```bash
python3 -m ki --root . index
python3 -m ki --root . serve
```

```bash
curl -s http://127.0.0.1:8765/v1/health | python3 -m json.tool
```

Example retrieve:

```bash
curl -s http://127.0.0.1:8765/v1/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"query":"How does draft promotion work?","pack_k":5}' | python3 -m json.tool
```

---

## Optional: MCP in Cursor

```bash
pip install -e ".[mcp]"
python3 -m ki --root . serve   # in one terminal
python3 -m ki --root . mcp     # stdio — wire in Cursor MCP config
```

Details: [MCP integration](MCP.md). Policy: **retrieve first**, cite `doc_path` (Cursor skills `teamkm-retrieve-first`, `teamkm-mcp-setup` in the repo).

---

## Before you push a PR

```bash
pytest -q
python3 scripts/validate_frontmatter.py --root .
python3 scripts/golden_queries.py --root .
```

---

## Deep dives

| Topic | Doc |
|-------|-----|
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Full contract | [REQUIREMENTS.md](REQUIREMENTS.md) |
| Tests & golden queries | [TESTING.md](TESTING.md) |
| API / OpenAPI | [MCP.md](MCP.md), `docs/openapi.yaml` in repo |

---

!!! warning "Do not commit secrets or ticket paste"
    See REQUIREMENTS §3 and skill **teamkm-no-secrets** in `.cursor/skills/`.
