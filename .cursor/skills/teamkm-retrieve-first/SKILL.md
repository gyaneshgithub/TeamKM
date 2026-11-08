---
name: teamkm-retrieve-first
description: >-
  Enforces retrieve-first work: query TeamKM local API (or MCP teamkm_* tools)
  before editing code, reviewing PRs, or answering "how do we…?" Always cite
  doc_path and line ranges from chunks. Use when the user changes code, asks
  about team conventions, debugs a feature, or requests implementation guidance
  in this repo.
---

# TeamKM — retrieve-first

**Policy (normative summary):** [CONTRIBUTING.md](../../../CONTRIBUTING.md) (MCP section) • [docs/MCP.md](../../../docs/MCP.md) • REQUIREMENTS §5.7–§5.9.

The **host** (this chat) runs the reasoning loop. TeamKM provides **grounded context** from merged `knowledge/**/*.md`. **Do not** rely on model memory alone for stack-specific or team-specific facts.

## When to apply

Before any of the following:

- Editing **application code** or **config** in this repo (or a service this knowledge describes).
- **Reviewing** a PR for correctness vs documented intent.
- Answering **"how do we…"**, **"what's the standard for…"**, or **"why did we…"**.
- Proposing **new** or **large edits** to files under `knowledge/`.

## Prerequisites

1. **Local API must be running** (see skill **teamkm-run-local**). Default: `http://127.0.0.1:8765`.
2. If the API is down, **say so**, run health once or ask the user to start `ki serve`; you may still read `knowledge/**/*.md` directly but **note** you did not use retrieval.

## Step 1 — Health

```bash
curl -s http://127.0.0.1:8765/v1/health | python3 -m json.tool
```

- If `index_status` is not `ready`, run `python3 -m ki --root . index` (or ask user), then retry.
- Record `corpus_fingerprint` / `local_head` in your reasoning when staleness matters.

## Step 2 — Retrieve or context pack

Choose a **short query** from the user task (feature name, error, area, component).

**Retrieve (ranked chunks):**

```bash
curl -s http://127.0.0.1:8765/v1/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"query":"<topic>","candidate_k":24,"pack_k":12}' | python3 -m json.tool
```

**Context pack (assembled bundle, preferred for multi-step work):**

```bash
curl -s http://127.0.0.1:8765/v1/context_pack \
  -H 'Content-Type: application/json' \
  -d '{"query":"<topic>","candidate_k":24,"pack_k":8,"cap_per_doc":2}' | python3 -m json.tool
```

Optional filters: `domain`, `area`, `include_archived` (see [docs/openapi.yaml](../../../docs/openapi.yaml)).

## Step 3 — MCP (if connected)

If the user has **TeamKM MCP** enabled, prefer tools (same semantics):

| Tool | Use |
|------|-----|
| `teamkm_health` | Step 1 |
| `teamkm_retrieve` | Step 2, lighter |
| `teamkm_context_pack` | Step 2, richer analysis |
| `teamkm_contribute_dry_run` | Before **new** knowledge markdown (overlap check) |

Prompt **`teamkm_retrieve_first`** can be used to restate policy to the host.

## Step 4 — Act only after grounding

1. **Summarise** what you retrieved in plain language.
2. **Cite** every factual claim from knowledge using **`doc_path`** and **`line_start`–`line_end`** (or heading_path when helpful).
3. If retrieval is **empty** or **weak**, say **"corpus gap"** explicitly; do not invent team policy.
4. Then propose code/doc changes.

## New knowledge docs

Before creating a new file under `knowledge/`, run **contribute dry-run**:

```bash
python3 -m ki --root . contribute -f path/to/draft.md
```

Or MCP `teamkm_contribute_dry_run`. Prefer **edit** or **extend** when similarity is high ([knowledge-contribute](../knowledge-contribute/SKILL.md)).

## Anti-patterns

- Skipping retrieve because the question "sounds generic."
- Quoting long chunks without path/line citation.
- Treating chat history as source of truth over merged `knowledge/`.
