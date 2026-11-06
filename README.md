# TeamKM

**Your team’s memory, in git—searchable on your machine.**

TeamKM is a **template repo** for durable engineering knowledge: Markdown lives under `knowledge/` with validated YAML front matter, merges happen through **PRs**, and a **local** retrieval pipeline turns that corpus into **grounded context** for agents and humans (hybrid search, mandatory rerank, HTTP API on loopback). Normative behaviour: [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

---

## Why this exists

- **Chat doesn’t compound.** Decisions and gotchas that live only in threads don’t survive rotation, releases, or six months of new hires.
- **Wikis drift.** Without the same review and history model as code, “the doc” and “the system” quietly diverge.
- **Assistants need anchors.** Models answer from patterns in training data unless you **retrieve** what *your* repo already says—then answers can be **cited** and checked.

This project makes **merged markdown** the product: diffable, reviewable, and the input to a **local RAG** you control.

---

## What you get (at a glance)

| Piece | What it does |
|-------|----------------|
| **`knowledge/`** | The corpus—technical, delivery, testing, functional, meta—with §6.1 front matter. |
| **`ki`** | Validate, index, serve: chunk → hybrid retrieve → rerank → context packs. |
| **HTTP API** | `127.0.0.1` by default—any tool that speaks HTTP (or MCP downstream) can plug in. |
| **CI** | Tests, front matter checks, golden queries—see [docs/TESTING.md](docs/TESTING.md). |

After you merge to `main`, optional automation can promote **`draft` → `reviewed`** for touched docs (see [CONTRIBUTING.md](CONTRIBUTING.md)).

---

## The loop (conceptually)

```mermaid
flowchart LR
  A[Write markdown] --> B[PR + review]
  B --> C[Merge to main]
  C --> D[Index / retrieve locally]
  D --> E[Grounded answers with citations]
```

---

## Documentation map

| Doc | Read it for… |
|-----|----------------|
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Full product spec (normative). |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How indexing and retrieval fit together. |
| [docs/LEADERSHIP_PITCH.md](docs/LEADERSHIP_PITCH.md) | Short executive / leadership brief. |
| [docs/TESTING.md](docs/TESTING.md) | Tests, golden queries, safety rails. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branches, PRs, corpus rules, draft promotion. |
| [docs/GITHUB_BRANCH_PROTECTION.md](docs/GITHUB_BRANCH_PROTECTION.md) | Protecting `main` on GitHub. |

---

## Quick start (tooling)

**Python 3.10+.**

```bash
cd /path/to/TeamKM
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
python3 scripts/validate_frontmatter.py --root .
python3 -m ki index --root .
python3 -m ki serve --root . --host 127.0.0.1 --port 8765
```

**Before opening a PR**, see whether your idea overlaps existing docs (merge vs new):

```bash
python3 -m ki contribute --root . -f path/to/draft.md
```

**Another terminal**—sanity-check the API:

```bash
curl -s http://127.0.0.1:8765/v1/health | python3 -m json.tool
curl -s http://127.0.0.1:8765/v1/retrieve -H 'Content-Type: application/json' \
  -d '{"query":"your topic","candidate_k":24,"pack_k":12}' | python3 -m json.tool
```

**Validator flags:** `--inject-domain` if `domain` is omitted (canonical from path); `--fix` to write `domain` atomically after other checks pass.

**Session wrapper** (REQUIREMENTS §12.1, pattern B): [scripts/ki-session.sh](scripts/ki-session.sh) starts `ki serve` then runs your assistant.

**Retrieval stack (implemented):** tf‑idf cosine **+** BM25, **RRF** fusion, then **mandatory rerank** (`ki/retrieve.py`). **OpenAPI:** [docs/openapi.yaml](docs/openapi.yaml) (also `GET /openapi.yaml` when the server runs). **Golden queries:** [meta/golden_queries.yaml](meta/golden_queries.yaml) — run `python3 scripts/golden_queries.py --root .`

---

## Repo layout

| Path | Role |
|------|------|
| `knowledge/` | Corpus (Markdown + YAML front matter) |
| `ki/` | Python package: validators, indexer, local API |
| `scripts/` | Helpers (validate, golden queries, promote-on-merge, etc.) |
| `.rag/` | Generated index and manifest (**gitignored**) |

---

## License

Add a license file when you adopt this template for your org.
