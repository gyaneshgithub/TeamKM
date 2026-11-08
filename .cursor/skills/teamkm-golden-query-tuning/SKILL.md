---
name: teamkm-golden-query-tuning
description: >-
  Tune meta/golden_queries.yaml: add queries, interpret FAIL recall@k, decide
  fix corpus vs query vs re-index vs chunking. Use when golden_queries.py fails
  in CI, retrieval regression, or improving search quality.
---

# Groundline — golden query tuning

**Spec:** REQUIREMENTS §5.5, §7, §11 • **File:** [meta/golden_queries.yaml](../../../meta/golden_queries.yaml) • **Runner:** `python3 scripts/golden_queries.py --root .`

## What golden queries do

Each entry asks: “For this **natural-language query**, does the **top k** ranked chunk come from a doc whose path **contains** `expected_doc_contains`?”

```yaml
schema_version: "0.1.0"
recall_at_k: 5   # top 5 after rerank
queries:
  - id: gq-001
    query: Groundline template RAG
    expected_doc_contains: knowledge/technical
```

- Matching is **substring** on `doc_path` (not exact file path).
- Pipeline: `retrieve_candidates` → **`rerank`** → take `recall_at_k` ([scripts/golden_queries.py](../../../scripts/golden_queries.py)).

## Run locally

```bash
python3 -m ki --root . index          # if stale
python3 scripts/golden_queries.py --root .
```

Optional: `--file path/to/alternate.yaml` for experiments (do not commit ad-hoc files without team review).

## Interpreting FAIL

Example stderr:

```text
FAIL gq-001 expected doc containing 'knowledge/technical/meta', got ['knowledge/delivery/...', ...]
```

| If… | Likely cause | Try first |
|-----|----------------|-----------|
| Expected doc **missing** from top-k | Thin corpus, wrong `query` wording, or doc not indexed | Add/improve target doc; re-run index |
| **Wrong** doc ranks higher | Overlap in topics, need clearer title/headings/`area`/`tags` | Edit corpus (preferred) |
| Right doc ranks **just below** k | Raise `recall_at_k` **temporarily** to diagnose; do not raise k in CI without sign-off |
| All paths empty / index error | Index not built | `ki index`; check `.rag/manifest.json` |
| Fail after **merge** only | Fingerprint stale | `python3 -m ki --root . index` |

**Default rule:** fix **corpus** or **query text** before changing retrieval code.

## Adding a golden query

1. Pick a **real question** the team asks (on-call, feature area, regression).
2. Identify the **canonical doc path** that should win (e.g. `knowledge/testing/auth-regression.md` → needle `knowledge/testing` or full subpath if unique).
3. Add `id` with stable prefix `gq-`.
4. Run script until **PASS**; include change in PR with the **corpus** or **meta** update.

Avoid **brittle** needles (`knowledge/technical/a.md` unless that file is stable forever). Prefer folder segment + unique `area` slug in path.

## When to change chunking / hybrid (engine change)

Chunking and hybrid BM25+tf-idf live in **`ki/`** ([docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md)). Change engine defaults only when:

- Multiple golden queries fail **after** corpus fixes.
- Team agrees in PR with **before/after** `golden_queries.py` output.
- Update `schema_version` or manifest notes if index format changes (REQUIREMENTS §12).

Do **not** loosen every query to pass without improving retrieval meaning.

## CI

[.github/workflows/ci.yml](../../../.github/workflows/ci.yml) runs golden queries on every PR to `main`. Local **PASS** before push.

## Related

- **teamkm-pre-pr-checklist** — includes golden step.
- **teamkm-retrieve-first** — manual retrieve for debugging one query:

  ```bash
  curl -s http://127.0.0.1:8765/v1/retrieve \
    -H 'Content-Type: application/json' \
    -d '{"query":"<same as golden>","pack_k":12}' | python3 -m json.tool
  ```
