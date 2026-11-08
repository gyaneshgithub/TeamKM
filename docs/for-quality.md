# For quality & QE

**You:** test engineers, QA leads, automation owners. **Success:** canonical testing knowledge under `knowledge/testing/`, CI stays green, golden queries catch retrieval regressions when the corpus changes.

---

## What you own in the corpus

| Typical content | Folder |
|-----------------|--------|
| Test strategy, environments, data rules | `knowledge/testing/` |
| Release verification themes | `knowledge/testing/` or `knowledge/delivery/` |
| Known defect classes, flaky-test runbooks | `knowledge/technical/` or `testing/` |

Same PR rules as code: [Contributing](contributing.md), [How to use](HOW_TO_USE_GROUNDLINE.md).

---

## Pre-merge gates (snippets)

From repo root with venv and `pip install -e ".[dev]"`:

```bash
pytest -q
python3 scripts/validate_frontmatter.py --root .
python3 scripts/golden_queries.py --root .
```

Optional contribute check before large new docs:

```bash
python3 -m ki --root . contribute -f path/to/draft.md
```

---

## Golden queries (regression radar)

Defined in `meta/golden_queries.yaml`. Each query asserts that recall@k returns a chunk from an expected path substring.

```bash
python3 -m ki --root . index
python3 scripts/golden_queries.py --root .
```

When CI fails:

1. Fix the **corpus** or query wording first (preferred).
2. Re-index locally, re-run script until PASS.
3. See [Testing](TESTING.md) and Cursor skill **teamkm-golden-query-tuning** in the repo.

---

## What not to commit

No credentials in test data write-ups, no ticket dumps, no production customer data—[REQUIREMENTS §3](REQUIREMENTS.md).

---

## Deep reference

| Topic | Doc |
|-------|-----|
| Test philosophy & CI | [TESTING.md](TESTING.md) |
| `include_archived`, contribute API | [REQUIREMENTS.md](REQUIREMENTS.md) |
| Local API for debugging retrieve | [For engineering](for-engineering.md), [MCP](MCP.md) |
