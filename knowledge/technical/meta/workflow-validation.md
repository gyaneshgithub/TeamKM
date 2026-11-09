---
title: PR workflow validation note
domain: technical
area: meta
author_role: dev
type: adr
status: reviewed
last_reviewed: "2026-11-06"
tags:
  - workflow
  - validation
exclude_from_default_retrieval: false
---

# Workflow validation

This note exists to validate the **feature branch → contribute checks → PR** flow for Groundline.

It intentionally stays small and scoped under `knowledge/technical/meta/` with valid §6.1 front matter.

## Checklist used before PR

1. `python3 scripts/validate_frontmatter.py --root .`
2. `pytest`
3. `python3 -m ki --root . status` (re-index if stale)
4. `python3 scripts/golden_queries.py --root .` or `python3 -m ki --root . eval --report md`
5. Optional: `python3 -m ki --root . contribute -f knowledge/technical/meta/workflow-validation.md`
