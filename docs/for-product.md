# For product

**You:** product manager, business analyst, or functional owner. **Success:** durable intent, decisions, and acceptance context in **`knowledge/functional/`** (and related areas)—reviewed like code, findable later—**without** installing Groundline locally.

---

## What you contribute

| Good fit in the corpus | Keep outside the repo |
|------------------------|------------------------|
| Problem statements, scope, decisions in plain language | Raw JIRA/Linear threads or ticket URLs |
| Acceptance themes, release notes, “why we chose X” | Secrets, customer PII, confidential contracts |
| Links to **public** specs or marketing pages | Copy-paste of internal tracker exports |

Normative rule: [REQUIREMENTS §3](REQUIREMENTS.md) — self-contained markdown only.

---

## How to participate (no Python required)

1. Read [How to use Groundline](HOW_TO_USE_GROUNDLINE.md) (sections 1–4).
2. Ask your team which **folder** to use — usually `knowledge/functional/` or `knowledge/delivery/`.
3. Edit on GitHub: **branch → edit file → Pull Request**.
4. Request a reviewer who knows the feature area.
5. After merge, the note is **official** on `main` (automation may mark `draft` → `reviewed`).

Front matter at the top of each file (`title`, `area`, `status: draft`) is filled in by you or a dev partner—see the template in any existing `knowledge/**/*.md` file in the repo.

---

## What “good” looks like

- **Short and factual** — what was decided, for whom, and what to verify in QA.
- **Stable titles** — search and retrieval use headings and metadata.
- **Version or product scope** when older decisions still matter (`applies_to`, `legacy_reviewed`—ask a dev editor if unsure).

---

## How assistants use your words

When engineers run the local index, retrieval can surface **your** merged prose during implementation and test design—**if** it is on `main` and clearly written. You do not need to use AI tools yourself for that to help.

---

## Partners

| Role | Doc |
|------|-----|
| Quality | [For quality & QE](for-quality.md) |
| Leadership | [For management](for-management.md) |
| Developers | [For engineering](for-engineering.md), [Contributing](contributing.md) |
