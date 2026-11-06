# Contributing to knowledgeIntelligence

This repo is a **reusable template**: Markdown corpus under `knowledge/`, a **local** index under `.rag/` (gitignored), and **git + PRs** for governance. Normative behaviour is in [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

## Branch workflow (default)

- **`main`**: integration branch; should stay **CI-green** (pytest + golden queries + front matter).
- **`feature/<short-slug>`**: branch from `main`, open a **Pull Request**, delete after merge.
- **Releases**: tag the **engine** (e.g. `v0.6.0`) when you want downstream teams to pin a known-good template.

## Before you open a PR

1. **Validate front matter** — `python3 scripts/validate_frontmatter.py --root .` (use `--inject-domain` if your team omits `domain` in drafts).
2. **Retrieval-first contribute** (recommended) — see §5.8:
   ```bash
   python3 -m ki contribute --root . -f path/to/draft.md
   ```
   or pipe markdown on stdin. Prefer **edit** or **extend** when similarity is high.
3. **Run tests** — `pytest`.

## What to commit

- **Knowledge** under `knowledge/<technical|delivery|testing|functional|meta>/...` with §6.1 YAML front matter.
- **No** raw chat logs, ticket threads, secrets, or PII (REQUIREMENTS §3).

## Corpus maintenance (avoid unbounded growth)

- Prefer **one living doc per `area`** plus short delivery notes that **link** into it.
- For **legacy** behaviour that is still true for older lines, use **`status: legacy_reviewed`**, **`applies_to`**, and **`doc_version`** — do **not** delete working history (§4.4).
- Use **`status: deprecated`** only when two “current” answers **conflict** for the same scope; set **`supersedes` / `superseded_by`**.
- For low-signal overflow, use **`exclude_from_default_retrieval: true`**; retrieval APIs accept **`include_archived: true`** when needed.

## Optional: local pre-commit hook

```bash
./scripts/install-git-hooks.sh
```

Validates staged `knowledge/**/*.md` with `validate_frontmatter.py`.

## CODEOWNERS

Edit [.github/CODEOWNERS](.github/CODEOWNERS) so important paths always get a reviewer.
