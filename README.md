# knowledgeIntelligence

**Git-hosted, local-first** team knowledge base: Markdown under `knowledge/`, validated metadata, and a **local RAG** slice (MVP: **tf‑idf** vectors + **mandatory rerank** stage + **context packs**) exposed over **HTTP** on loopback. Full behaviour is defined in [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

| Doc | Purpose |
|-----|---------|
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Product requirements (normative) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [docs/LEADERSHIP_PITCH.md](docs/LEADERSHIP_PITCH.md) | Leadership brief |
| [docs/TESTING.md](docs/TESTING.md) | How we test and stay safe |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branches, PRs, corpus maintenance |

## Quick start (tooling)

Requires **Python 3.10+**.

```bash
cd /path/to/Cuursorproject
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
python3 scripts/validate_frontmatter.py
python3 -m ki index --root .
python3 -m ki serve --root . --host 127.0.0.1 --port 8765
```

Before adding a doc, run **contribute dry-run** (merge vs new):

```bash
python3 -m ki contribute --root . -f path/to/draft.md
```

In another terminal:

```bash
curl -s http://127.0.0.1:8765/v1/health | python3 -m json.tool
curl -s http://127.0.0.1:8765/v1/retrieve -H 'Content-Type: application/json' \
  -d '{"query":"your topic","candidate_k":24,"pack_k":12}' | python3 -m json.tool
```

- **`--inject-domain`** — validate when `domain` is omitted (canonical value from path).
- **`--fix`** — atomically write correct `domain` from path (after other checks pass).

**Session wrapper** (per §12.1, pattern B): [scripts/ki-session.sh](scripts/ki-session.sh) — starts `ki serve` then `exec`s your assistant binary.

**Retrieval (V1+ hybrid, implemented in Python):** first stage = **tf‑idf cosine** (dense surrogate) **+ BM25** fused with **RRF**; second stage = **mandatory rerank** (see `ki/retrieve.py`). **OpenAPI:** [docs/openapi.yaml](docs/openapi.yaml) (also `GET /openapi.yaml` when the server runs). **Golden queries:** [meta/golden_queries.yaml](meta/golden_queries.yaml) — run `python3 scripts/golden_queries.py --root .`

## Layout

- `knowledge/` — corpus (Markdown + YAML front matter per §6.1)
- `ki/` — Python package (validators, indexer, local API)
- `scripts/` — CLI entrypoints
- `.rag/` — generated index and manifest (gitignored)

## License

Add a license file when you adopt this template for your org.
