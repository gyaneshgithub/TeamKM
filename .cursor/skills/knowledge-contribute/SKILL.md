---
name: knowledge-contribute
description: >-
  Guides git-based contribution for the RAG knowledge repo: sync main, create a
  feature branch (and fork workflow when contributing upstream), validate
  Markdown front matter, run similarity checks via the local RAG API when
  available, stage files, and prepare commits only when the user explicitly
  asks to commit. Use when the user wants to add or edit knowledge markdown,
  contribute a doc, open a PR branch, or follow the team’s knowledge
  contribution workflow.
---

# Knowledge base contribution

Use this skill when contributing `.md` knowledge files under `knowledge/`. It combines **git workflow**, **front matter validation**, and **retrieval-first** checks so merges stay consistent with [docs/REQUIREMENTS.md](../../../docs/REQUIREMENTS.md).

## Principles

- **PR-only to `main`.** Work happens on a **feature branch**, never direct push to `main`.
- **Commits only when asked.** Do **not** run `git commit` unless the user **explicitly** requests a commit (team rule: avoid unsolicited commits).
- **Fork vs branch:** Inside the team repo, use **branch** from `main`. Use **fork + branch** only when contributing to a repo where the developer lacks write access (open-source style). Do not conflate “fork” with “feature branch”; ask which applies if unclear.
- **Grounding:** Before suggesting a new file, use the local **RAG retrieve** or `contribute --dry-run` flow from §5.9 of REQUIREMENTS when that tooling exists.

## Author profile (before front matter)

If the user has not set up a local profile, offer **[knowledge-author-profile](../knowledge-author-profile/SKILL.md)** once: copy `meta/author-profile.example.yaml` → `meta/author-profile.local.yaml`, fill **name, team, author_role, topics**. Use it to pre-fill optional §6.1 fields (`contributor`, `team`, `topics_author`) and to suggest `tags` / `area`.

## Required steps (agent)

### 1. Sync and branch

1. Ensure working tree is clean or stash with user consent.
2. `git fetch origin` (and `upstream` if using a fork).
3. `git checkout main` then `git pull` (from `origin` or `upstream` as appropriate).
4. Create branch: `kb/<short-slug>-<topic>` (e.g. `kb/add-auth-timeout-notes`). Use ASCII, lowercase, hyphens.

**Fork workflow (external contributor):**

1. Fork on the git host (user action or `gh repo fork` if user requests and `gh` is available).
2. `git remote add fork <fork-url>` (if not cloned from fork).
3. Branch from updated `main`, push to **fork**: `git push -u fork HEAD`.

### 2. Front matter and template

1. New docs should follow **§6.1** in [docs/REQUIREMENTS.md](../../../docs/REQUIREMENTS.md). Use **author profile** (`meta/author-profile.local.yaml`) when present for `contributor`, `team`, `topics_author`, `author_role`, `tags` hints.
2. **`domain` and path:** The **canonical** `domain` is the first folder under `knowledge/` (`technical`, `delivery`, `testing`, `functional`, or `meta`). Either set `domain` in YAML to **match** that path, or **omit** `domain` and pass **`--inject-domain`** to validation, or use **`--fix`** to inject atomically. Never set `domain` to a value that disagrees with the path—CI will fail.
3. Run validation before PR:

   ```bash
   python3 scripts/validate_frontmatter.py path/to/file.md
   ```

   If the script supports in-place fixes (e.g. `--fix`), use it so omitted `domain` is written before staging.

4. Fix all errors before staging.

### 3. Content and placement

- Put files under `knowledge/<domain>/...` per [docs/REQUIREMENTS.md §6](../../../docs/REQUIREMENTS.md)—**choosing the folder is the primary way to choose `domain`** (see **Domain inference** in §6.1).
- If overlap with existing knowledge is possible, run retrieval / similarity first (§5.9).

### 4. Stage and commit (commit only if user asked)

1. `git add` only the intended paths.
2. If the user asked to commit: use a clear message, e.g. `knowledge(delivery): add timeout handling notes for auth service`.
3. If the user did **not** ask to commit: stop after staging or leave changes unstaged—summarise `git status` and next steps (push, open PR).

### 5. Push and PR

1. `git push -u origin kb/<short-slug>-<topic>` (or `fork` remote for fork workflow).
2. Open a PR toward `main` (`gh pr create` if user wants GitHub and `gh` is available).

## Front matter quick reference

Required fields are in [docs/REQUIREMENTS.md §6.1](../../../docs/REQUIREMENTS.md): `title`, `area`, `author_role`, `type`, `status`, plus `last_reviewed` when `status: reviewed`. **`domain`:** required in the **effective** file (match path or omit for validator inject—see §6.1 **Domain inference**). Optional: `contributor`, `team`, `topics_author`, `tags`, `product`, `related`.

## Scripts in this repo

| Script | Purpose |
|--------|---------|
| `scripts/validate_frontmatter.py` | Validates YAML front matter and domain/path rules for `knowledge/**/*.md` |

When RAG CLI/API exists, add a step to run contribute dry-run or hybrid search here.
