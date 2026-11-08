---
name: teamkm-onboard
description: >-
  Onboard someone to TeamKM: non-developers to HOW_TO_USE_TEAMKM.md; developers
  to CONTRIBUTING, README quick start, and optional skills. Use when the user is
  new, asks how to start, how TeamKM works, or what to read first.
---

# TeamKM — onboard

Route the user by **role** and **goal**. Keep the first reply **short**; link deeper docs only when needed.

## 1. One-paragraph elevator

TeamKM is a **team notebook in git**: approved notes live under **`knowledge/`**, change via **Pull Requests**, and (optionally) a **local search tool** helps humans and AI assistants **find and cite** what was merged—not chat memory.

## 2. Who are they?

| If they are… | Send them to… | They usually do… |
|--------------|----------------|------------------|
| **Non-technical** (PM, DM, new hire) | [docs/HOW_TO_USE_TEAMKM.md](../../../docs/HOW_TO_USE_TEAMKM.md) | Write/review markdown via GitHub UI with a developer; no Python required |
| **Developer** contributing | [CONTRIBUTING.md](../../../CONTRIBUTING.md) + [README.md](../../../README.md) Quick start | Branch → validate → PR; optional `ki serve` / MCP |
| **Engineering lead** | [docs/LEADERSHIP_PITCH.md](../../../docs/LEADERSHIP_PITCH.md) + HOW_TO_USE § For engineering leads | Template adoption, branch protection, pilot area |
| **Implementer / architect** | [docs/REQUIREMENTS.md](../../../docs/REQUIREMENTS.md) + [docs/ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) | Full contract and data flows |

## 3. Developer first hour (ordered)

1. Read **HOW_TO_USE** skim (5 min) for vocabulary.
2. Clone the **team’s** repo (their `origin`, not only a template read-only copy).
3. [CONTRIBUTING.md](../../../CONTRIBUTING.md) — branches, draft → reviewed, CI check **`test`**.
4. Local tooling (optional same day):
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   python3 -m ki --root . index
   python3 -m ki --root . serve
   ```
5. Skills to mention: **teamkm-run-local**, **teamkm-retrieve-first**, **teamkm-pre-pr-checklist**, **knowledge-contribute**, **teamkm-no-secrets**.

## 4. Non-developer first hour

1. [docs/HOW_TO_USE_TEAMKM.md](../../../docs/HOW_TO_USE_TEAMKM.md) — sections 1–4 and glossary.
2. Ask their team for **who reviews** `knowledge/` PRs and which **folder** (`technical`, `testing`, `functional`, …) they usually use.
3. They can edit on GitHub: create branch → edit file → open PR (developer can run validators on their machine if CI fails).

## 5. What not to do on day one

- Do not require MCP or RAG to **author** a doc.
- Do not commit **secrets** or ticket paste — skill **teamkm-no-secrets**.
- Do not push directly to **`main`** if branch protection is enabled.

## 6. Adopting this repo as the team template

See **teamkm-share-project** skill or REQUIREMENTS **§4.5** (fork → own remote → customize `knowledge/`).

## Agent tone

Plain language, numbered next steps, max **three** links in the first message unless the user asks for depth.
