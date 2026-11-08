---
name: teamkm-share-project
description: >-
  Adopt or share TeamKM: fork template to team org remote (§4.5), GitHub
  template/fork/push, or Cursor share/new-repo skills for Cursor-hosted backup.
  Use when forking TeamKM, moving to org GitHub, or saving the project remotely.
---

# TeamKM — share / adopt the template

TeamKM is meant to be **copied per team**: your **`knowledge/`** corpus and remotes are **yours**; the engine ( `ki/`, CI, skills) travels with the clone.

**Normative:** [docs/REQUIREMENTS.md §4.5](../../../docs/REQUIREMENTS.md)

## Choose a path

| Goal | Path |
|------|------|
| **Team knowledge repo on GitHub (org)** | §4.5 below (most common) |
| **Save this workspace to Cursor-hosted repo** | Use Cursor skills **`share`** or **`new-repo`** (built-in user skills: read those SKILL.md files when the user asks to save/back up on Cursor) |
| **Keep upstream template updates** | Add `upstream` remote to template; merge selectively (optional) |

Do **not** create a second remote if `origin` already points at the team’s canonical repo—offer **push** instead.

## GitHub org adoption (§4.5)

1. **Start from template**
   - GitHub: **Use this template** → create repo under the **org**, or
   - **Fork** into the org, or
   - **Clone** this repo and change remotes.

2. **Own remote**
   ```bash
   git remote -v
   # If replacing origin:
   git remote set-url origin https://github.com/<org>/<teamkm-repo>.git
   git push -u origin main
   ```

3. **Customize** (same clone):
   - `knowledge/` — your corpus
   - `meta/golden_queries.yaml` — your regression queries
   - `.github/CODEOWNERS`, branch protection ([docs/GITHUB_BRANCH_PROTECTION.md](../../../docs/GITHUB_BRANCH_PROTECTION.md))
   - Keep **`.cursor/skills/`** or trim to team needs

4. **Do not** commit secrets — **teamkm-no-secrets** skill.

5. **Tell the team** — **teamkm-onboard** skill / [HOW_TO_USE_TEAMKM.md](../../../docs/HOW_TO_USE_TEAMKM.md).

## `gh` shortcuts (when user wants CLI)

```bash
gh repo fork <template-owner>/TeamKM --org <org> --clone=false   # org fork
gh repo create <org>/<name> --private --source=. --remote=origin --push
```

Adjust flags to match host policy. Use **`gh`** only if installed and user approves.

## Cursor-hosted backup (`share` / `new-repo`)

When the user says “save on Cursor”, “backup”, or “create repo on Cursor”:

1. **Read and follow** the **`share`** or **`new-repo`** skill from the user’s Cursor skill store (not duplicated here).
2. Before any commit: run **teamkm-no-secrets** scan; ensure `.rag/`, `.venv/`, `author-profile.local.yaml` are ignored.
3. After remote exists: link **teamkm-onboard** for teammates.

TeamKM’s **product default** for engineering teams is still **GitHub/GitLab + PRs**; Cursor repo is an optional **host**, not a replacement for §4.5 unless the team chooses it.

## Multi-team note (§4.6)

Each LoB should have **its own clone + remote**. Do not merge unrelated teams’ prose into one `knowledge/` tree without owners.

## Agent output

End with:

- **Where** the repo lives (URL).
- **Next:** branch protection, first `knowledge/` pilot doc, `pip install -e ".[dev]"`, optional MCP ([teamkm-mcp-setup](../teamkm-mcp-setup/SKILL.md)).
