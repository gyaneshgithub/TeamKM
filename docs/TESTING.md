# Testing and safety guardrails (knowledgeIntelligence)

This document describes **how we test** the repo today and **how we avoid corrupting** knowledge, local index state, or git history as we add the RAG stack.

**Normative requirements** remain in [REQUIREMENTS.md](REQUIREMENTS.md) (§8 CI, §7 SLOs). **Architecture** is in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. What we test today

| Layer | Purpose | Command |
|-------|---------|---------|
| **Front matter** | Schema + path/domain rules (§6.1) | `python3 scripts/validate_frontmatter.py` |
| **Index + API** | Chunk → index → hybrid retrieve (dense+BM25, RRF) → rerank → context_pack; `/v1/health` | `pytest` (includes `tests/test_index.py`, `tests/test_api.py`, `tests/test_hybrid.py`) |
| **Golden queries** | recall@k vs `meta/golden_queries.yaml` | `python3 scripts/golden_queries.py --root .` |
| **Contribute dry-run** | Merge-vs-new hints from retrieval (§5.8) | `python3 -m ki contribute --root . -f draft.md` |
| **Unit tests** | Validator, atomic writes | `pytest` (after `pip install -e ".[dev]"`) |

Optional:

- `python3 scripts/validate_frontmatter.py --inject-domain` — CI default may require explicit `domain` in files; use this where teams omit `domain` and inject at commit time.

---

## 2. Guardrails: prevent self-corruption

### 2.1 Corpus (git)

- **Source of truth** is Markdown in `knowledge/` under version control — never auto-edit without an explicit **`--fix`** ([validate_frontmatter.py](../scripts/validate_frontmatter.py)).
- **Atomic writes** — `--fix` uses a temp file in the **same directory** + `os.replace()` so a crash mid-write cannot leave a half-written `.md` ([ki/atomicio.py](../ki/atomicio.py)).
- **Validation before write** — `--fix` only rewrites after **all** other required checks pass; otherwise it prints errors and skips the file.
- **Domain lock** — `domain` must match the first folder under `knowledge/` unless `--inject-domain` / `--fix` is used (§6.1 **Domain inference**).

### 2.2 Generated index (`.rag/`)

Implemented patterns (MVP):

- **`index/` payload** — `chunks.json`, `idf.json`, `vectors.json` written as normal files (atomizing each file write is a future tighten-up).
- **`manifest.json`** — updated with **`corpus_fingerprint`**, **`index_status`**, model ids, **`chunk_count`**, built via **atomic write** ([ki/manifest.py](../ki/manifest.py)).
- **Single-flight lock** — **`.rag/build.lock`** with `fcntl` flock where available ([ki/lockfile.py](../ki/lockfile.py)).
- **Staleness** — if `corpus_fingerprint` ≠ live hash of `knowledge/**/*.md`, **`ki index`** / **`ensure_index()`** rebuilds (§12.1).

### 2.3 Git operations (future auto-sync)

- **Never** auto-merge when dirty or diverged; only **fetch + fast-forward** when safe (§12.2). Surface `sync_status` on `/health` when the API exists.

---

## 3. Recovery

| Failure | Recovery |
|---------|----------|
| Bad front matter in a PR | CI fails; fix YAML locally; re-run `validate_frontmatter.py`. |
| `--fix` interrupted | Atomic rename either completes or old file remains; no half file. Re-run `--fix`. |
| Corrupt `.rag/` (future) | Delete `.rag/` (gitignored) and **rebuild** from current `HEAD`; manifest rebuild restores consistency. |
| Wrong `domain` in file | Run `python3 scripts/validate_frontmatter.py --fix knowledge/...` to set from path. |

---

## 4. CI (GitHub Actions)

Workflow **ci.yml** runs:

1. Install Python **3.11**
2. `pip install -e ".[dev]"`
3. `pytest`
4. `python3 scripts/validate_frontmatter.py --root "$GITHUB_WORKSPACE"`
5. `python3 scripts/golden_queries.py --root "$GITHUB_WORKSPACE"`

## 5. Optional local pre-commit

```bash
./scripts/install-git-hooks.sh
```

Validates staged `knowledge/**/*.md` with [validate_frontmatter.py](../scripts/validate_frontmatter.py).

---

## 6. Future tests (RAG pipeline)

When ingest/index code lands, add:

- **Golden-query** regression (REQUIREMENTS §5.5, §11): small fixed query set → expected doc paths.
- **Indexer idempotence**: two builds from the same tree → same manifest hash.
- **Concurrent build**: second process should block or no-op (single-flight).

---

## Revision

| Version | Date | Notes |
|---------|------|-------|
| 0.1 | 2025-11-06 | Initial testing doc; ties validator + pytest + future index/sync rules. |
| 0.2 | 2025-11-06 | Golden queries in CI; contribute dry-run; optional pre-commit hook |
