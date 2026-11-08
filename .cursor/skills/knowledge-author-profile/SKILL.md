---
name: knowledge-author-profile
description: >-
  Sets up or updates a **local only** author profile (name, team, topics, role)
  for Groundline so agents can pre-fill YAML front matter when
  committing knowledge docs. Use when the user asks to configure their profile,
  set up local contributor metadata, or default front matter for knowledge
  commits.
disable-model-invocation: true
---

# Groundline — local author profile

## Purpose

Each team member keeps a **local profile** (not committed—see `.gitignore`) with **name**, **team**, **topics** they work on, and related fields. The agent uses it when creating or editing `knowledge/**/*.md` to propose consistent **§6.1** front matter.

## File location (canonical)

1. **Preferred (project-local):**  
   **`meta/author-profile.local.yaml`**  
   - Lives next to `meta/` in this repo.  
   - **Must remain gitignored**; never stage or commit it.

2. **Alternative (machine-wide):**  
   **`~/.teamkm/profile.yaml`**  
   - Use if the same person works across multiple clones and wants one profile.

If **both** exist, **project-local wins** when the workspace is this repo.

## Setup steps (agent)

1. Copy the example template into the chosen path:
   - From [meta/author-profile.example.yaml](../../../meta/author-profile.example.yaml) → `meta/author-profile.local.yaml`
2. Ask the user for (or infer from context) and fill:
   - **`display_name`** — how they want to appear on docs (string).
   - **`team`** — squad or group name (string), e.g. `platform`, `billing`.
   - **`author_role`** — one of `dev` | `qe` | `pm` | `dm` | `mixed` (must align with §6.1).
   - **`topics`** — list of **areas** / themes they own or touch (string[]), e.g. `["auth", "reports"]` — maps to front matter **`area`** and **`tags`** hints.
   - **`email`** — optional; **do not** commit if policy says keep out of repo; profile file is local only.
   - **`product`** — optional default product name for functional notes.
3. Confirm `.gitignore` includes `meta/author-profile.local.yaml` and `**/.teamkm/`.
4. Tell the user: edits to the profile apply on the **next** doc the agent helps with; they can run validation after save.

## Using the profile when writing front matter

When adding or editing `knowledge/**/*.md`:

| Profile field | Front matter usage (§6.1) |
|---------------|---------------------------|
| `display_name` | optional `contributor` or `author_name` when user wants attribution on the doc |
| `team` | optional `team` |
| `topics` | suggest **`tags`** and **`area`** (user confirms—`area` is required and should match doc subject) |
| `author_role` | set **`author_role`** if not overridden |
| `product` | suggest **`product`** under `functional/**` |

**Rules:**

- **`area`** must still match the **subject** of the document, not always every profile topic—use **`tags`** to capture multiple themes.
- Never copy **secrets** into front matter.
- If the user has no profile file, offer to run this setup once before large contributions.

## Relation to other skills

- **[knowledge-contribute](../knowledge-contribute/SKILL.md):** branch/PR workflow; call **this** skill first when the user needs defaults for front matter.
- **REQUIREMENTS:** [docs/REQUIREMENTS.md](../../../docs/REQUIREMENTS.md) §6.1
