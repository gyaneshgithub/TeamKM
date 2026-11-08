---
name: teamkm-no-secrets
description: >-
  Block secrets, credentials, PII, and work-tracker paste in knowledge/ and
  commits. Scan drafts before staging; cite REQUIREMENTS §3. Use when editing
  knowledge markdown, opening PRs, pasting tickets into docs, or the user asks
  what must not be committed.
---

# TeamKM — no secrets in the corpus

**Normative:** [docs/REQUIREMENTS.md](../../../docs/REQUIREMENTS.md) §3.3 (out of scope v1) and §3 (no PII/secrets).

The **`knowledge/`** tree is **git history forever**. If it is sensitive, assume it will be indexed, retrieved, and shown to agents.

## Never commit

| Category | Examples (non-exhaustive) |
|----------|---------------------------|
| **Secrets** | API keys, passwords, tokens, private keys, `.env` contents, connection strings with credentials |
| **PII** | Government IDs, personal phone/email of customers, health data, unredacted HR records |
| **Work-tracker payload** | JIRA/Linear/etc. **ticket keys**, **ticket URLs**, paste of ticket **threads**, sprint exports |
| **Credentials files** | `*.pem`, `id_rsa`, kubeconfig with auth, `credentials.json`, `service-account*.json` |
| **Local-only profile** | `meta/author-profile.local.yaml`, `**/.teamkm/profile.yaml` (must stay gitignored) |

## Allowed (when self-contained)

- **Paraphrased** decisions, runbooks, and acceptance criteria written as **standalone prose**.
- **Opaque internal refs** only if the team later documents a **separate policy** (REQUIREMENTS §3 — not required for MVP).
- **Public** URLs to docs that are already public.

## Agent checklist (before `git add knowledge/`)

1. Read the **full** draft the user wants to commit.
2. **Red-flag patterns** (search mentally or with grep):
   - `AKIA`, `BEGIN PRIVATE KEY`, `Bearer ey`, `password=`, `api_key`, `sk-`, `ghp_`, `xoxb-`
   - `@` + password-like assignments in config snippets
   - `jira.`, `atlassian.net`, `linear.app/issue`, `#PROJ-1234` style ticket keys (team policy: **no** ticket URLs/keys in corpus)
3. If found: **stop**, tell the user what to remove, suggest **environment variables** or **secret store** for ops secrets, and **summarize the ticket in own words** without paste.
4. Confirm **`meta/author-profile.local.yaml`** and `.env*` are **not** staged (`.gitignore` should cover them).

## If the user pastes a ticket into chat

- Do **not** write that paste verbatim into `knowledge/**/*.md`.
- Extract **durable facts** (decision, scope, test notes) into neutral markdown.
- Optional one-line note: “Tracked externally per team policy” — **no** link to the tracker unless policy explicitly allows opaque refs.

## Related skills

- **[teamkm-pre-pr-checklist](../teamkm-pre-pr-checklist/SKILL.md)** — run before PR.
- **[knowledge-contribute](../knowledge-contribute/SKILL.md)** — contribution workflow.

## Escalation

If unsure whether content is sensitive, **default to exclude** and ask the user or a security/contact owner. Prefer a smaller, redacted doc over a full dump.
