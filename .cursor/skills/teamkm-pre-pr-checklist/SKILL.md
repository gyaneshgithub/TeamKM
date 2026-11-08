---
name: teamkm-pre-pr-checklist
description: >-
  Pre-PR gate for Groundline: pytest, validate_frontmatter.py, golden_queries.py,
  optional ki contribute dry-run on changed knowledge files. Use when opening a
  PR, before push, or when the user asks if the branch is ready to merge.
---

# Groundline — pre-PR checklist

Run from **repository root** with venv active (`pip install -e ".[dev]"` minimum).

**Related:** [CONTRIBUTING.md](../../../CONTRIBUTING.md) • [docs/TESTING.md](../../../docs/TESTING.md) • skill [knowledge-contribute](../knowledge-contribute/SKILL.md).

## Agent workflow

Execute steps in order. **Stop and report** on first failure unless the user asks to continue. Do **not** open a PR while checks are red unless the user explicitly overrides.

### 0. Scope

- If **`knowledge/`** changed: run **[teamkm-no-secrets](../teamkm-no-secrets/SKILL.md)** scan before staging (no secrets, PII, or ticket paste — REQUIREMENTS §3).
- Identify changed files (`git status` / `git diff main...HEAD`).
- If only docs outside `knowledge/`, still run **pytest** when code paths exist; skip golden queries only if **no** retrieval/index assumptions changed (when in doubt, run golden queries).

### 1. Unit tests

```bash
pytest -q
```

All tests must pass (includes API smoke, index, hybrid retrieval, front matter).

### 2. Front matter (all knowledge touched)

```bash
python3 scripts/validate_frontmatter.py --root .
```

For a **single file** in the PR:

```bash
python3 scripts/validate_frontmatter.py --root . path/to/file.md
```

If team policy omits `domain` in drafts:

```bash
python3 scripts/validate_frontmatter.py --root . --inject-domain
```

Use `--fix` only when the user asked to write corrected `domain` from path.

**Dates:** `last_reviewed` must be a **quoted string** in YAML (e.g. `"2026-11-08"`) so validation does not treat it as a date object.

### 3. Golden queries (retrieval regression)

```bash
python3 scripts/golden_queries.py --root .
```

Requires a built index; script calls `ensure_index`. Failures mean top-k retrieval no longer hits expected docs—fix corpus, query file, or index before merge.

### 4. Optional — contribute dry-run (knowledge PRs)

For **each new or heavily rewritten** `knowledge/**/*.md`:

```bash
python3 -m ki --root . contribute -f path/to/draft.md
```

Review `suggested_action` (`edit` | `extend` | `new_doc`) and `similar` paths. Prefer merging into existing docs when scores are high (§5.8).

Requires local API/index only indirectly (contribute uses index); run **teamkm-run-local** if contribute errors on missing index.

### 5. Git hygiene (remind user)

- Branch name: `feature/<slug>` or `kb/<slug>` per CONTRIBUTING.
- **No** secrets, ticket dumps, or PII in `knowledge/`.
- **No commit** unless the user explicitly asked (team rule).

### 6. CI parity

GitHub Actions **ci.yml** runs the same core checks:

1. `pip install -e ".[dev,mcp]"`
2. `pytest -q`
3. `python3 scripts/validate_frontmatter.py --root "$GITHUB_WORKSPACE"`
4. `python3 scripts/golden_queries.py --root "$GITHUB_WORKSPACE"`

Local green ≈ required check **`test`** on PR.

## Output template (agent)

Report to the user:

```markdown
## Pre-PR checklist
- [ ] pytest — PASS/FAIL
- [ ] validate_frontmatter — PASS/FAIL
- [ ] golden_queries — PASS/FAIL
- [ ] contribute dry-run — PASS/SKIP/FAIL (per file list)

**Blockers:** …
**Suggested next:** …
```

## When checks fail

| Check | Common fix |
|-------|------------|
| Front matter | Missing `area`, bad `status`/`last_reviewed`, `domain` ≠ path |
| Golden queries | Re-index; add corpus; tune `meta/golden_queries.yaml` with team sign-off |
| pytest | Fix regressions in `ki/` or tests |
| contribute | Overlap → edit existing doc; or justify `new_doc` in PR description |
