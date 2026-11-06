---
title: PR workflow validation note
domain: technical
area: meta
author_role: dev
type: adr
status: draft
tags:
  - workflow
  - validation
exclude_from_default_retrieval: false
---

# Workflow validation

This note exists to validate the **feature branch → contribute checks → PR** flow for knowledgeIntelligence.

It intentionally stays small and scoped under `knowledge/technical/meta/` with valid §6.1 front matter.

## Checklist used before PR

1. `python3 scripts/validate_frontmatter.py --root .`
2. `pytest`
3. `python3 scripts/golden_queries.py --root .`
4. Optional: `python3 -m ki contribute --root . -f knowledge/technical/meta/workflow-validation.md`
