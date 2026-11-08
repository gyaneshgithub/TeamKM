# Changelog

All notable changes to the **TeamKM engine** (this template repository) are listed here. Adopters **pin git tags** for stability; each team’s **`knowledge/` corpus** has its own history in that team’s fork.

## Unreleased

## 0.3.0 — 2026-11-08

Milestone release: TeamKM rename, local agent/MCP integration, merge automation, contribution CLI, extended front matter and retrieval API, and Cursor agent skills.

### Cursor agent skills

- Eight **`teamkm-*`** skills under `.cursor/skills/`: **retrieve-first**, **run-local**, **mcp-setup**, **pre-pr-checklist**; governance **no-secrets**, **onboard**; optional **golden-query-tuning**, **share-project** (template adoption §4.5).
- Existing corpus skills remain: **knowledge-contribute**, **knowledge-author-profile**.

### MCP and HTTP API

- **`python3 -m ki mcp`** (stdio): **`teamkm_*`** tools and **`teamkm_retrieve_first`** prompt against `TEAMKM_API_BASE` or `KI_HOST`+`KI_PORT`; optional **`pip install -e ".[mcp]"`**.
- **`GET /openapi.json`** returns the OpenAPI spec as JSON. See **[docs/MCP.md](docs/MCP.md)**.

### Knowledge workflow and front matter

- CLI: **`python3 -m ki contribute`**; **`POST /v1/contribute_dry_run`** on the HTTP API.
- Front matter: **`legacy_reviewed`**, **`applies_to`**, **`doc_version`**, **`canonical_since`**, **`exclude_from_default_retrieval`**.
- Retrieval: **`include_archived`** on HTTP API.
- Documentation: multi-team maintenance, **`legacy_reviewed`** policy, optional pre-commit hook.

### Automation

- After merge to **`main`**, GitHub Actions promotes **`status: draft` → `reviewed`** (sets **`last_reviewed`**) for touched `knowledge/**/*.md` via **`scripts/promote_draft_on_merge.py`**; follow-up commit uses **`[skip ci]`**.
- Uses push **`before`/`after`** and **`HEAD^1..HEAD`** for merge commits so path detection is not empty on merge-only pushes.

### Project identity and docs

- **Rename:** project and Python distribution **`knowledgeIntelligence` / `knowledge-intelligence` → TeamKM / `team-km`**; local profile path **`~/.teamkm/`** (was `~/.knowledgeintelligence/`).
- **[HOW_TO_USE_TEAMKM.md](docs/HOW_TO_USE_TEAMKM.md)** — plain-language guide for non-technical contributors; linked from README.
- README, CONTRIBUTING, REQUIREMENTS, ARCHITECTURE, TESTING, LEADERSHIP_PITCH, and operational docs brought in line with the above.

## 0.2.x — 2025-11-06

- Hybrid retrieval: dense tf-idf + BM25, RRF fusion; mandatory rerank.
- Local HTTP API: `/v1/health`, `/v1/retrieve`, `/v1/context_pack`; OpenAPI stub under `docs/openapi.yaml`.
- Index staging + atomic swap; golden query script and CI.
