# Changelog

All notable changes to the **TeamKM engine** (this template repository) are listed here. Adopters **pin git tags** for stability; each team’s **`knowledge/` corpus** has its own history in that team’s fork.

## Unreleased

- MCP: `python3 -m ki mcp` (stdio) exposes **`teamkm_*`** tools + **`teamkm_retrieve_first`** prompt against `TEAMKM_API_BASE` / `KI_HOST`+`KI_PORT`; install optional **`pip install -e ".[mcp]"`**. `GET /openapi.json` returns the OpenAPI spec as JSON. **[docs/MCP.md](docs/MCP.md)** — integration guide.
- **Rename:** project and Python distribution **`knowledgeIntelligence` / `knowledge-intelligence` → TeamKM / `team-km`**; local profile path **`~/.teamkm/`** (was `~/.knowledgeintelligence/`).
- Automation: after merge to `main`, GitHub Actions promotes **`status: draft` → `reviewed`** (sets **`last_reviewed`**) for touched `knowledge/**/*.md` via `scripts/promote_draft_on_merge.py`; follow-up commit uses **`[skip ci]`**. Uses push **`before`/`after`** (and **`HEAD^1..HEAD`** for merge commits) so **merge commits** are not skipped with an empty path list.
- Documentation: multi-team maintenance, `legacy_reviewed`, `ki contribute`, optional pre-commit hook.
- Front matter: `legacy_reviewed`, `applies_to`, `doc_version`, `canonical_since`, `exclude_from_default_retrieval`.
- Retrieval: `include_archived` on HTTP API; `POST /v1/contribute_dry_run`.
- CLI: `python3 -m ki contribute`.

## 0.2.x — 2025-11-06

- Hybrid retrieval: dense tf-idf + BM25, RRF fusion; mandatory rerank.
- Local HTTP API: `/v1/health`, `/v1/retrieve`, `/v1/context_pack`; OpenAPI stub under `docs/openapi.yaml`.
- Index staging + atomic swap; golden query script and CI.
