# For management

**You:** engineering, product, or delivery leadership rolling out a **durable knowledge habit**. **Success:** one owned repo, PR discipline, optional local RAG—without a separate wiki budget or vendor lock-in for assistants.

---

## Elevator pitch

TeamKM keeps **agreed know-how in git** as Markdown. Anything merged to **`main`** is **official**. A **local** retrieval layer lets coding assistants **cite** that corpus instead of inventing from generic training data.

Full brief: [Leadership brief](LEADERSHIP_PITCH.md).

---

## What you are (and are not) buying

| In scope | Out of scope (v1) |
|----------|-------------------|
| Git-reviewed corpus, cross-role folders (`technical`, `testing`, `functional`, …) | Storing secrets, PII, or ticket threads in the repo |
| PR workflow, CI gates, optional draft → reviewed on merge | Replacing mentorship or management |
| Local HTTP API + optional MCP; **assistant-agnostic** | Hosted multi-tenant SaaS knowledge product |

---

## Rollout checklist (6 steps)

1. **Approve template adoption** — team owns **their** remote ([§4.5](REQUIREMENTS.md#45-adopting-this-repository-as-a-team-template)).
2. **Protect `main`** — PR required, status check **`test`** ([Branch protection](GITHUB_BRANCH_PROTECTION.md)).
3. **Name owners** — who reviews `knowledge/` by area; use `.github/CODEOWNERS` if helpful.
4. **Pilot one area** — one service or feature; avoid boiling the ocean.
5. **Tie to definition of done** — short knowledge PRs when decisions or runbooks matter.
6. **Communicate to non-devs** — [How to use TeamKM](HOW_TO_USE_TEAMKM.md); they can edit via GitHub UI.

---

## Risks leaders should monitor

- **Corpus rot** — docs without review; mitigate with PRs and `reviewed` / `legacy_reviewed` status.
- **Secret leakage** — train contributors: no credentials or ticket paste in `knowledge/`.
- **Scope creep** — REQUIREMENTS is the contract; customize policy in **your** fork, not ad hoc tool forks.
- **Measurement** — golden-query recall and corpus growth sketched in [REQUIREMENTS §11](REQUIREMENTS.md); tune when volume justifies it.

---

## Multi-team / line of business

Each LoB should have **its own clone + remote** (§4.6). Share read access via API or git; do not mix unrelated prose in one `knowledge/` tree without owners.

---

## Where engineering continues the story

[For engineering](for-engineering.md) — install, API, MCP. [For product](for-product.md) and [For quality](for-quality.md) — how other roles contribute without running Python.
