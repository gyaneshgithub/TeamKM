# Changelog

All notable changes to the **knowledgeIntelligence engine** (this template repository) are listed here. Adopters **pin git tags** for stability; each team’s **`knowledge/` corpus** has its own history in that team’s fork.

## Unreleased

- Documentation: multi-team maintenance, `legacy_reviewed`, `ki contribute`, optional pre-commit hook.
- Front matter: `legacy_reviewed`, `applies_to`, `doc_version`, `canonical_since`, `exclude_from_default_retrieval`.
- Retrieval: `include_archived` on HTTP API; `POST /v1/contribute_dry_run`.
- CLI: `python3 -m ki contribute`.

## 0.2.x — 2025-11-06

- Hybrid retrieval: dense tf-idf + BM25, RRF fusion; mandatory rerank.
- Local HTTP API: `/v1/health`, `/v1/retrieve`, `/v1/context_pack`; OpenAPI stub under `docs/openapi.yaml`.
- Index staging + atomic swap; golden query script and CI.
