# Groundline — portfolio summary

**Author:** [Gyanesh Maurya](https://github.com/gyaneshgithub)  
**Repository:** [gyaneshgithub/TeamKM](https://github.com/gyaneshgithub/TeamKM)  
**License:** [MIT](../LICENSE)  
**Docs site:** [gyaneshgithub.github.io/TeamKM](https://gyaneshgithub.github.io/TeamKM/)

---

## One-line pitch (for résumé / LinkedIn)

**Groundline** — open-source **git-native RAG** for engineering teams: PR-governed Markdown corpus, hybrid retrieval + mandatory rerank, local HTTP API, optional **MCP** for IDE agents, CI golden-query regression, and merge automation for knowledge lifecycle.

---

## Problem

Teams lose context in chat and wikis; coding assistants guess without **cited, merged** team knowledge. Groundline treats **reviewed markdown in git** as the source of truth and adds a **local** retrieval layer so humans and agents can **retrieve first, then answer**.

---

## What I built

| Area | Highlights |
|------|------------|
| **RAG engine** | Chunking, tf-idf + BM25, RRF fusion, mandatory rerank, context packs (`ki/`) |
| **API** | Fast loopback HTTP: health, retrieve, context_pack, contribute dry-run, OpenAPI JSON |
| **MCP** | Stdio server; `teamkm_*` tools call the same API (assistant-agnostic) |
| **Governance** | YAML front matter validator, golden queries in CI, draft→reviewed on merge to `main` |
| **Agent UX** | 10 Cursor skills (retrieve-first, MCP setup, pre-PR, onboarding, etc.) |
| **Docs** | MkDocs Material site, role-based guides (eng / mgmt / product / QE) |
| **Spec** | Normative REQUIREMENTS + architecture docs suitable for template adoption |

---

## Tech stack

Python 3.10+, PyYAML, pytest, GitHub Actions, MkDocs Material, optional MCP SDK, no mandatory cloud.

---

## Demonstrations (for interviews)

1. **Self-serve path** — [HOW_TO_USE_GROUNDLINE](HOW_TO_USE_GROUNDLINE.md) (non-dev writers) + [Quick start](../README.md#quick-start-tooling).
2. **Retrieval** — `ki serve` → `curl /v1/retrieve` with citations in `doc_path`.
3. **Quality** — `pytest`, `golden_queries.py`, front matter validation on PRs.
4. **Agents** — `ki mcp` + retrieve-first policy ([MCP.md](MCP.md)).
5. **Docs** — stakeholder site on GitHub Pages.

---

## Design choices worth discussing

- **Local-first** — index under `.rag/`, bind `127.0.0.1`; data stays on the machine.
- **Git = product** — knowledge merges like code; no separate wiki silo.
- **Thin MCP** — host runs the LLM loop; Groundline exposes tools + policy prompt.
- **Template / §4.5** — teams fork to their own remote; engine vs corpus separation.

---

## Links

| Resource | URL |
|----------|-----|
| Source | https://github.com/gyaneshgithub/TeamKM |
| Live docs | https://gyaneshgithub.github.io/TeamKM/ |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## Suggested résumé bullets (copy, then tailor)

- Built **Groundline**, an open-source template for **git-hosted team knowledge** with **hybrid RAG**, local REST API, and **MCP** integration for IDE coding assistants.
- Implemented **CI retrieval regression** (golden queries), YAML corpus validation, and **GitHub Actions** automation for knowledge review state on merge.
- Shipped **MkDocs** stakeholder documentation and **Cursor agent skills** for retrieve-first development workflows.
