# Groundline — Leadership brief

**Audience:** Engineering leadership, product leadership, delivery management  
**Companion:** [ARCHITECTURE.md](ARCHITECTURE.md) (how it works), [REQUIREMENTS.md](REQUIREMENTS.md) (full spec)  
**Last updated:** 2025-11-06  

---

## Elevator statement

**Groundline** is a **team-owned knowledge base** where durable know-how lives in **git** as Markdown, and a **local retrieval service** makes that corpus **queryable by any coding assistant**—with **mandatory reranking**, **structured context packs**, and **citations** so answers are **grounded in what the team actually merged**, not in model memory alone.

---

## The problem we are solving

- When people leave or rotate, **undocumented context** walks out the door; handovers and ramp-up stay expensive.
- Chat and tickets **do not compound**: they scatter and age; they are poor as a **single source of truth**.
- **AI coding tools without retrieval** reuse generic patterns and can **hallucinate** on your stack, your history, and your quality bar.

This product does **not** replace good management or mentorship. It **institutionalizes** what the team agrees to **write, review, and merge**—and makes that corpus **easy to use** during real engineering work.

---

## What we are offering (product)

| Layer | What it is |
|-------|------------|
| **Corpus** | Markdown under `knowledge/` with YAML metadata; **PR-only** merges ([REQUIREMENTS §4](REQUIREMENTS.md)). |
| **Intelligence** | Local **RAG**: chunk → embed → **retrieve → mandatory rerank** → **context packs** (not naive “top‑k cosine” only) ([§5.4–§5.6, §5.10, §5.11](REQUIREMENTS.md)). |
| **Access** | **HTTP on localhost** (canonical) plus optional **MCP** stdio server (`python3 -m ki mcp`, tools **`teamkm_*`**) so **Cursor, Claude Code, Copilot-class tools, or scripts** integrate the same way—the **host** runs the agent loop ([§5.9, §5.12](REQUIREMENTS.md)). |
| **Adoption** | Any team can treat this repo as a **template**: clone, point `origin` at **their** remote, customize layout and policy ([§4.5](REQUIREMENTS.md)). |

---

## Features leadership should care about

1. **Git as source of truth** — Diff, review, history, and compliance are the same as for code; no second silo to fund separately.
2. **Cross-role coverage** — Room for **technical, delivery, testing (QE), and functional (PM)** knowledge linked by **area** and metadata ([§2–§3, §6](REQUIREMENTS.md)).
3. **Grounded AI assistance** — Default path is **retrieve then analyze** with **citations**; unsupported claims are explicit gaps, not silent invention ([§5.7](REQUIREMENTS.md)).
4. **Quality-oriented retrieval** — **Mandatory rerank** plus **context assembly** (caps, related expansion, inclusion reasons) improves what actually reaches the model ([§5.5, §5.10](REQUIREMENTS.md)).
5. **Assistant-agnostic** — You are not betting the strategy on one IDE vendor ([§5.12](REQUIREMENTS.md)).
6. **Measurable quality over time** — **Golden query sets** and recall targets push tuning from opinion to data ([§5.5, §7, §11](REQUIREMENTS.md)).
7. **Conflict and deprecation rules** — Stale or contradictory docs are handled in the open, not blended silently at retrieval time ([§4.4, §5.10](REQUIREMENTS.md)).

---

## Outcomes (what success looks like)

| Outcome | Indicators |
|---------|------------|
| **Faster, safer delivery** | Less time re-discovering prior decisions, failure modes, and test lore; agents reference **your** corpus before changing code. |
| **Shorter ramp-up** | New hires and transfers find **reviewed** narratives by area (engineering, QE, product) instead of only tribal knowledge. |
| **Stronger handovers** | Knowledge is **in-repo and versioned**; what was merged is discoverable with provenance. |
| **Compounding returns** | Each merged PR **widens** retrieval coverage; the index at `main` reflects **cumulative** learning ([§1, §11](REQUIREMENTS.md)). |
| **Lower vendor risk** | Integration through **standard HTTP/MCP** avoids single-tool dependency for the knowledge layer ([§5.12](REQUIREMENTS.md)). |

These outcomes **scale with discipline**: teams that merge **curated** updates regularly and **use** retrieval in the loop see the largest benefit. A repo that is empty or stale behaves like one—no architecture fixes that.

---

## Success metrics (starter set)

Aligned with [REQUIREMENTS §11](REQUIREMENTS.md):

- **Corpus growth** — Steady merged contributions to `knowledge/`.
- **Retrieval quality** — Golden-set **recall@k** before changing defaults (e.g. **≥ 80% @5** as a starting bar in §7).
- **Latency / build SLOs** — Index and query times stay within agreed bounds as corpus grows ([§7](REQUIREMENTS.md)).
- **Role coverage** — At least reviewed material across domains for each major **area** / product surface ([§11](REQUIREMENTS.md)).
- **Adoption (qualitative)** — Engineers, QE, PM, DM report using context for **new** and **maintenance** work ([§11](REQUIREMENTS.md)).

---

## Investment and honesty

**Requires:** PR culture, light metadata (front matter), optional local models or approved APIs, and time to wire **session start** (MCP/API) so retrieval is **default** ([§12.1](REQUIREMENTS.md)).

**Does not replace:** Headcount judgment, architecture ownership, security review, or product prioritization.

**Does reduce:** Repeated rediscovery, contradictory one-off docs in chat, and **ungrounded** AI answers when the answer **was already in the corpus**.

---

## Ask for leadership

1. **Sponsor** “knowledge merged like code” as part of **definition of done** for meaningful features and quality milestones—not only hero documentation.
2. **Protect time** for **QE and PM** contributions where the spec calls for those domains—not only developer prose ([§3](REQUIREMENTS.md)).
3. **Approve** local tooling policy (embedding/reranker, optional CI) so teams stay **fast** without breaking **security** ([§7–§9](REQUIREMENTS.md)).

---

## Next steps

1. Pilot with **one squad** and a **small golden query set** in `meta/`.
2. Ship **MVP**: ingest → chunk → embed → retrieve → **rerank** → context pack + health ([§10](REQUIREMENTS.md)).
3. Review metrics quarterly; expand **hybrid** and contribution automation in **V1+** when baseline recall is stable ([§10](REQUIREMENTS.md)).

---

## Revision history

| Version | Date | Notes |
|---------|------|-------|
| 0.1 | 2025-11-06 | Initial leadership brief. |
| 0.2 | 2025-11-06 | Access row: MCP stdio (`ki mcp`, **`teamkm_*`**) as HTTP adapter; host holds agent loop — [MCP.md](MCP.md). |
