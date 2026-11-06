# knowledgeIntelligence — Requirements

**Project name:** **knowledgeIntelligence** (repository / product name for this RAG knowledge base).  
**Status:** Draft for review  
**Owner:** GYANESH  
**Last updated:** 2025-11-06

This document captures the planned behaviour of **knowledgeIntelligence**: a **git-hosted, RAG-based knowledge base** for agent-assisted development. **Retrieval-Augmented Generation (RAG)** is the core pattern: knowledge lives in the repo as normal files; a **local pipeline** chunks, embeds, and indexes them so agents **retrieve** grounded passages before (or instead of) answering. The **retrieval service runs locally** (e.g. `localhost`); **any agent coding assistant** that can call **HTTP** or **MCP** can integrate—**assistant-agnostic by design** (§5.12). **Cursor**, **Claude**, **Windsurf**, **GitHub Copilot**, or a **shell script** are **examples**, not hard dependencies. Revise sections as the team agrees.

**Core product idea:** **Knowledge compounds.** Every merged contribution adds to a shared corpus. Over weeks and months the index reflects **technical, delivery, testing, and product** learning—so **developers**, **QE**, **PMs**, and the **dev manager** can pull **the same grounded context** when improving **products and features** they own (new builds, refactors, quality hardening, roadmap decisions), instead of re-deriving it from memory or chat.

**What this product is for (any team):** **Maintain** durable, reviewable knowledge in git; **share** it across roles via a single corpus; **reuse** prior decisions, analysis, and testing lore instead of rediscovering them; **support analysis** (human and agent) with retrieval that **grounds** answers in cited chunks rather than model recall alone. This repository is intended as a **reusable template**: a team **clones** it (or uses it as a **GitHub template** / fork), creates **their own remote** where they **push** markdown under `knowledge/` and evolve **meta/**, skills, and tooling to match policy—see §4.5.

**See also:** [ARCHITECTURE.md](ARCHITECTURE.md) (systems view, data flows) — [LEADERSHIP_PITCH.md](LEADERSHIP_PITCH.md) (executive brief: value, outcomes, adoption) — [TESTING.md](TESTING.md) (tests and corruption guardrails).

---

## 1. Purpose and problem

Teams doing agentic development produce many markdown (and related) documents: decisions, runbooks, API notes, domain language, and experiment logs. That knowledge is fragmented and hard to reuse as **trusted context** for tools like Cursor or Claude.

**Goal:** A single **version-controlled** project that is **easy to maintain and extend**: contributors **commit** markdown (and similar) like any other repo work; after merge, they (or CI) **rebuild the RAG index** with simple commands. The system stays **accurate** by tying assistant outputs to **retrieved chunks with citations**, not to model recall alone.

**Cumulative value:** Each PR adds or updates durable notes; the **RAG index is rebuilt from the full corpus** at a given commit. The **whole history of contributions** is what makes retrieval better over time—coverage of edge cases, test lore, product intent, and operational reality **deepens** as the team commits.

---

## 2. Stakeholders

| Role | Count | Responsibility (high level) |
|------|-------|-----------------------------|
| Developers | 8 | Commit **completed work and analysis** tied to delivery (implementation notes, trade-offs, integration points, follow-ups); review peers’ PRs; **use retrieval** when building or maintaining features |
| QE | 1 | Commit **testing knowledge**: test plans, charters, regression notes, defect patterns, environment/setup gotchas, quality risks; **use retrieval** for regression and quality planning |
| Dev Manager | 1 | Governance, access, escalation; **use retrieval** for cross-team alignment and risk on areas the team supports |
| Product Manager | 1 | Author/approve functional product knowledge; align functional docs with product themes; **use retrieval** to ground feature specs and decisions in prior engineering and QE context |

---

## 3. Scope of knowledge

### 3.1 Domains

- **Technical:** Architecture, ADRs, conventions, libraries, deployment, debugging notes, integration contracts, performance, security considerations.
- **Delivery / engineering narrative:** Summaries of **work completed**, **analysis**, and **discussion outcomes** from the team’s delivery work (feature, fix, spike, etc.). **Curated** only—no dump of raw chat or external ticket threads. **External work trackers are out of scope for this repo:** do not store keys, links, or exports from tools such as JIRA; capture only what belongs in this knowledge base as standalone prose.
- **Functional / product:** Features, user journeys, glossary, business rules, acceptance criteria summaries (not a full backlog replacement).
- **Testing / quality (QE-owned primary author):** Test strategy excerpts, coverage notes, automation hooks, known flakiness, sign-off context suitable for reuse by dev and PM readers.

### 3.2 Primary formats (initial)

- Markdown (`.md`) as the default interchange.
- Optional later: diagrams (Mermaid in-repo), structured YAML/JSON for machine-readable facts.

### 3.3 Contribution rhythm (expected behaviour)

- **Developers** add or update knowledge when a unit of work reaches a sensible checkpoint (e.g. **done**, or end of a spike): what shipped, what was decided, what to watch in maintenance.
- **QE** adds or updates knowledge when test phases complete or when durable testing assets deserve a **canonical home** in the repo (still merged via PR).
- Over time, **cumulative commits** improve the local index: newcomers and agents query **prior episodes** for the same subsystem, feature area, or defect class.
- **Cross-role context:** The same retrieval interface supports **dev** (how we built it), **QE** (how we broke it / verified it), **PM** (what we intended for the product), **DM** (themes and risks)—so feature and maintenance work stays aligned with **recorded** intent and reality.

**Out of scope (v1):** Storing secrets, credentials, or PII. Those must never be committed. **Work-tracker payloads** (e.g. ticket keys, ticket URLs, or copy-pasted threads from JIRA or similar systems) are **not** part of this knowledge base—keep that tooling outside the repo; here we keep **self-contained** knowledge only. If the team later needs traceability, decide a **separate policy** (e.g. opaque internal refs); do not block MVP on it.

### 3.4 RAG and “easy to maintain”

Maintenance should feel like **ordinary documentation practice**, not a separate product:

- **Source of truth = files in git.** No proprietary silo; diff, review, and history are standard.
- **Contributing = add or edit markdown under `knowledge/`**, open a PR, get approval, merge.
- **Indexing = automated or one command** after pull/merge (e.g. “rebuild RAG index”), with incremental rebuild where possible so daily work stays fast.
- **Chunking and embeddings** are implementation details documented in `meta/` so the team can tune them without rewriting prose.

---

## 4. Repository and governance

### 4.1 Git as source of truth

- All knowledge lives in a dedicated git repository (monorepo for knowledge only, or a clearly named subtree if nested).
- **No direct pushes to the default branch** (e.g. `main`): changes land only via **Pull Request (PR)**.
- PRs are the approval gate: at least one reviewer (policy TBD: e.g. one peer + optional domain owner).

### 4.2 What may be merged (merge criteria — draft)

Reviewers check that contributions:

1. **Belong** in the knowledge base (not transient chat dumps without curation).
2. **Are accurate** and, where possible, **cite** sources (doc link, code path, commit date, or other references that live **inside** this repo or your public/private docs—**not** external ticket IDs unless the team explicitly allows a separate policy later).
3. **Follow** the repository layout and naming (see §6).
4. **Avoid** secrets, unreleasable data, and speculative statements presented as fact (mark uncertainty explicitly, e.g. “Open question: …”).
5. **Include** front matter per **§6.1** (validated in CI).
6. **Distinguish roles:** developer commits should read as **engineering/delivery** knowledge; QE commits as **testing/quality** knowledge—cross-link when the same feature or area spans both.

### 4.3 Branch protection (recommended)

- Require PR reviews before merge.
- Optional: required status checks (e.g. lint, link check, index build in CI).
- Optional: CODEOWNERS by area (e.g. `functional/` → PM + delegate).

### 4.4 Conflicting or superseded knowledge

When retrieval surfaces **two passages that disagree**:

1. **Do not** silently merge contradictory facts in prose; reviewers resolve in a follow-up PR.
2. Prefer **one canonical** doc: add front matter `status: deprecated` and `supersedes` / `superseded_by` pointing to the replacement path, or a short **“Resolution”** subsection dated in the owning doc.
3. Optional: use **`see_also`** / **`related`** for complementary (non-conflicting) views.

### 4.5 Adopting this repository as a team template

Any team may use this project as a **starting layout and requirements spec** for their own knowledge base:

1. **Clone** (or **use “Use this template”** on the host, or **fork**) into a workspace you control.
2. **Create a new empty repository** on your git host (your org’s naming, visibility, and branch rules).
3. Point **`origin`** at that new repo and **push** your initial branch (e.g. `main`), or add it as **`origin`** and push after replacing remotes—whichever matches your host’s workflow.
4. **Customize** for your team: `knowledge/` structure, §6 front matter, `meta/` (golden queries, policies), CI, and optional Cursor skills under **`.cursor/skills/`**—the **contract** stays **git + markdown + PR merges + local RAG** (§5, §12).

Teams **do not** need to stay tied to an upstream “template” repo unless they want occasional merges from it; most adopters will treat their copy as **the** source of truth.

---

## 5. RAG architecture: ingest, index, retrieve, and (optional) generate

The **whole project** is organised around a **RAG pipeline** running **locally** (or in CI for validation). Authoring stays **file-based and git-friendly**; the RAG layer is the runtime that makes that content agent-ready.

### 5.1 Pipeline (required behaviour)

1. **Ingest:** Scan configured paths (e.g. `knowledge/**/*.md`).
2. **Normalize:** Parse front matter; strip or preserve structure consistently.
3. **Chunk:** Split into retrieval units (by heading, size, or hybrid rules), each with stable ids.
4. **Embed:** Vector embeddings per chunk (model configurable; see open decisions).
5. **Store:** **Vector store** plus optional **sparse / full-text** index for hybrid retrieval (recommended for exact terms and code-like tokens).
6. **Serve:** Local **API and/or CLI**: retrieve top‑**N** candidates (hybrid when configured), **mandatorily rerank** (§5.5), then assemble **context packs** for agents.

On **git pull** or **post-merge**, contributors should be able to **refresh the index** in one step (or watch mode in dev).

### 5.2 Run locally

After clone, a **local tool** (CLI and/or API):

1. Builds or updates the RAG index from the working tree (or pinned commit).
2. Exposes retrieval: semantic search, hybrid search, **context bundle** export, health (commit, embedding model id, index schema version).

### 5.3 Index characteristics

- **Reproducible:** Same commit SHA + same chunking/embedding config → same index (or explicitly versioned deltas).
- **Performant:** Incremental rebuild when files change; suitable for frequent use during development.
- **Portable:** Runs on macOS/Linux (Windows optional); **no mandatory cloud** for daily dev (local embeddings preferred if policy requires air‑gap).

### 5.4 Smart chunking (retrieval quality)

“Smart” RAG here means **chunks that match how people query and how prose is structured**—not arbitrary fixed windows. Requirements and recommendations:

| Concern | Approach |
|---------|----------|
| **Boundaries** | **Structure-aware splitting:** walk the Markdown AST; primary boundaries are **headings** (`##`, `###`). A section under one heading is usually one conceptual unit. |
| **Oversized sections** | If a heading block exceeds a **max token length**, sub-split by **paragraph** or **list item**, keeping **overlap only on sub-splits** so boundary sentences stay discoverable. **Default overlap (tune in `meta/`):** ~**64–128** tokens when max chunk ≈ **512** tokens (~12–25%); ~**32–64** tokens when max ≈ **256**; if chunking by **character** length, ~**10–15%** overlap of the window. **Heading-only chunks** (whole section under one heading, under max size): **0** overlap between sections. |
| **Undersized sections** | Merge **tiny** adjacent siblings (e.g. single-line `####`) up to a **min** size so the vector is not noise-dominated—unless they are **glossary** entries (keep one entry per chunk). |
| **Code and tables** | **Code blocks** and **tables** are often quoted verbatim in questions: either attach them as **separate chunks** with `type: code \| table` metadata, or keep them inside the parent section chunk but ensure the **surrounding heading** is in the same chunk for context. |
| **Front matter** | Strip from body chunks but store as **document-level metadata** replicated on every chunk from that file (filtering, faceting: `area`, `domain`, `tags`). |
| **Stable identities** | Each chunk has a deterministic **chunk id** (e.g. hash of `file_path + heading_path + chunk_index`) so incremental reindex can **replace** embeddings for changed chunks only. |

**Advanced patterns (optional, improves precision/recall):**

- **Hierarchical / parent–child:** Embed **small child chunks** for precise retrieval; at query time **expand** with the **parent section** (or preceding heading) for context in the context pack—without inflating the whole document.
- **Hypothetical questions (HyDE) or title expansion:** Optional second-stage; only if validated—**not** required for v1.

**Anti-patterns to avoid:** splitting mid-sentence arbitrarily; huge chunks that dilute the embedding; tiny chunks with no semantic mass (unless glossary).

### 5.5 Smart index construction (retrieval + maintenance)

The index is “smart” when **recall** (find the right passage) and **precision** (little junk) are both high, and when **updates** are cheap.

| Layer | Role |
|-------|------|
| **Dense vectors** | Semantic similarity: “how do we handle timeouts in service X?” matches prose that never uses the exact phrase. |
| **Sparse / full-text (BM25 or equivalent)** | Exact and rare tokens: **API names, error codes, file paths, CLI flags, env vars**. **Hybrid retrieval** (merge dense + sparse scores, e.g. RRF or weighted sum) is **recommended** for a technical KB. |
| **Metadata filters** | Narrow by `domain`, `area`, `type` from front matter before or after vector search to avoid cross-domain collisions. |
| **Reranking (mandatory)** | After first-stage retrieval, **always** run a **cross-encoder** or **lightweight local reranker** on the candidate set (e.g. retrieve **20–40** → rerank → take top **8–12** for context pack assembly). This stage is **required** so **downstream coding assistants** get **optimal chunk order** for analysis—not only embedding similarity. **Run locally** (no mandatory cloud call); if policy blocks certain models, ship an **approved** small reranker documented in `meta/`. |

**Mandatory reranking (normative):**

- Default pipeline: **retrieve** `candidate_k` (config default e.g. **24**) → **rerank** with query–passage scoring → **`context_pack_k`** (e.g. **8**) before §5.10 diversification rules.
- Persist **reranker model id + version** next to embedding model in the index manifest for reproducibility.
- **API:** responses include **`rerank_score`** (or final rank position) per chunk where applicable; **`health`** may expose reranker id.

**Operational requirements:**

- **Versioning:** Persist **embedding model name + version**, **chunking config hash**, and **index schema version** with each build so behaviour is **reproducible** and debuggable.
- **Incremental rebuild:** On change, only **re-chunk and re-embed** files that differ (content hash per file); unchanged files skip embedding work.
- **Evaluation (lightweight):** Maintain a small **golden query set** in `meta/` (10–30 real questions + expected file paths or heading titles). On index or chunking changes, report **hit rate @k** in CI or a manual script—stops regressions from “tuning” blindly.

### 5.6 “Agentic” API (behavioural requirements)

The API should be **easy for agents and scripts** to use:

- Clear operations: **retrieve** (query → ranked chunks), **get chunk by id**, **context pack** (query + max tokens + min score + optional **assembly profile**—see §5.10), **neighbours** (optional graph from `related:` links), **health** (index status, corpus fingerprint—§12.1).
- **Structured responses** (JSON): chunk text, **file path**, **line range** (or offsets), **retrieval score**, **rerank score** (after §5.5 mandatory rerank), embedding / reranker / index version ids; context packs include **why included** (e.g. `hit`, `related`, `same_area`, `parent_section`) per §5.10.
- **Metadata:** repo commit, index build id, schema version; **health** returns **`index_status`** (`missing` \| `building` \| `ready` \| `stale`) and **`sync_status`** (e.g. `ok` \| `blocked_dirty_tree` \| `blocked_diverged` \| `syncing`) per §12.1–§12.2.
- Optional: **streaming** assistant answers **only** when every factual claim can be tied to retrieved chunk ids (see §5.7).

### 5.7 Minimising hallucination in a RAG-first system

RAG does **not** guarantee truth; it guarantees **grounded retrieval**. Requirements:

| Principle | Requirement |
|-----------|-------------|
| Grounding | Default path for agents: **retrieved chunks + citations** (path + lines). |
| Generation | If the tool **generates** prose (summaries, answers), output must include **chunk citations** for claims grounded in the corpus; unsupported claims must be absent or explicitly marked as **not in knowledge base**. |
| Staleness | Each chunk carries **source commit / mtime** so UIs can warn when context predates a change. |
| Gaps | Return **empty or low-confidence** results clearly; no filler from model memory. |

**Release alignment:** See **§10 Product phases**. **MVP** ships **ingest → chunk → embed → retrieve → mandatory rerank** with **mandatory citations** on any synthesized answer path; **retrieval-only** endpoints remain the safest default for strict audits. **Later** phases add hybrid retrieval hardening, contribution tooling, PR bots—see §10.

### 5.8 Agent-assisted contribution: what is new vs what already exists?

Coding assistants are **not** reliable if they guess from memory. **Duplicate or contradictory** docs hurt trust. Contribution flows must therefore be **retrieval-first** and **review-backed**.

**Principle:** “Figure out what to contribute” means **compare the draft against the indexed corpus** using the **same RAG retrieval** the team uses for reading—not an unstructured chat guess.

#### Required workflow (for tools / editor rules / CLI)

1. **Index is current.** Before a contribution, the developer runs (or the tool runs) an **index refresh** on the latest `main` merge base so retrieval targets current knowledge.
2. **Retrieve first.** From the developer’s draft (full text or a structured outline: topic, area, summary bullets), the agent **queries the RAG API** with **hybrid search** (semantic + keywords for APIs, paths, error codes).
3. **Present evidence.** The agent shows the **top‑k similar chunks** with **paths, line ranges, and similarity scores**—never a paraphrase without citations.
4. **Classify the gap (deterministic guidance).** Using retrieval scores and optional rules:
   - **Near-duplicate** (very high overlap with one doc): recommend **editing that file** (new section or revision) instead of adding a second file.
   - **Extension** (related doc exists but draft adds facts): recommend **patch to existing** doc + update front matter (`last-reviewed`, `related`).
   - **New doc** (low overlap or new `area`): recommend a **new path** under `knowledge/` per §6.
5. **Human decides.** The developer (or PR reviewers) **confirms** merge vs new file. The agent proposes a diff; **PR review** remains the quality gate—not model autonomy.

#### Optional tooling (recommended)

- **Contribution endpoint or script** (e.g. `contribute --dry-run`): accepts draft markdown, returns ranked similar chunks + suggested action (`edit` \| `merge` \| `new`) + suggested paths. Actions are **recommendations**; scores are **transparent**.
- **PR automation:** For changed files, run retrieval against the **rest of the repo** and post a comment listing **possibly related** docs (similarity above a threshold) to help reviewers spot duplication.

#### Limits (honesty)

| Limit | Implication |
|-------|-------------|
| Similarity is statistical | Borderline cases need **human** judgment; tune thresholds in `meta/` and revisit. |
| Corpus gaps | If retrieval returns nothing, “new doc” may still overlap **unindexed** text—full-text grep / list by `area` in front matter still helps. |
| Contradictions | Retrieval surfaces conflicts; **reviewers** resolve per §4.4. |

**Success:** The agent is “smart” because it **always grounds** the contribute decision in **retrieved chunks**, not because it infers from prior chat.

### 5.9 Local hosting and multi-client integration (HTTP, MCP, agnostic)

The knowledge base is **locally hosted** by default: a small **HTTP API** (and/or CLI) runs on the contributor’s machine next to the repo and index, **not** as a mandatory cloud service. Integration is **assistant-agnostic** (§5.12).

| Requirement | Detail |
|-------------|--------|
| **Binding** | Default bind **`127.0.0.1`** (or `localhost`) on a **documented port**; optional config for LAN-only bind if the team explicitly allows it (document security implications). |
| **Client workflow** | **Any** coding assistant that can invoke **HTTP** or **MCP** **calls the API** (or MCP tools) in a **retrieve-first** step: *query → ranked chunks / context pack* → then **analysis, planning, or code changes** use that grounded context with **citations**. Examples: Cursor, Claude Code, Copilot—**not** a closed list. |
| **Transport** | **REST + JSON** as the canonical contract (versioned paths or `Accept-Version`); stable enough for scripts and IDE integrations. |
| **Authentication (local)** | MVP: **no auth** on loopback, or optional shared secret in config if bind is non-loopback—document in `meta/`. |
| **Multiple MCP servers** | The system SHOULD expose the same retrieval operations via an **MCP server** process so clients that speak MCP (e.g. Cursor with **multiple MCPs** enabled) can add **this** knowledge MCP **alongside** other MCPs (browser, git-host, ticketing, etc.). **No requirement** that this MCP is exclusive—teams run **several MCP servers** concurrently; each registers its own tools (e.g. `knowledge_retrieve`, `knowledge_context_pack`). |
| **Coexistence** | Namespace MCP tool names (e.g. prefix `kb_`) to avoid collisions with tools from other MCPs on the same host. |

**Implementation note:** One stack may bundle **HTTP API + MCP process** sharing the same index handle; behaviour must stay **consistent** between transports (same query → same ranked chunks for a given index version).

### 5.10 Smart context assembly and relations (better agent outcomes)

Raw “top‑k similar chunks” often **under-serve** agents: they may be **redundant**, **miss linked docs**, or **omit** the complementary view (e.g. **QE** testing notes when the query sounds **technical**). **knowledgeIntelligence** implements **context assembly** that builds **coherent bundles** with **explicit structure** so **any** integrated coding assistant performs better **after** the retrieve step. **MVP (required):** cap chunks per document, expand **explicit** `related` links, attach **`inclusion_reason`** per chunk, group output for readability. **V1+ (recommended):** MMR / diversify, cross‑domain same‑`area` expansion, optional `intent` / `profile` / `role` hints—see §10.

#### 5.10.1 Relation sources (built at index time)

The index SHOULD derive a **lightweight document graph** (no need for a heavy graph DB in MVP):

| Link type | Source | Use |
|-----------|--------|-----|
| **Explicit** | Front matter `related: [...]`, inline links to other `knowledge/**/*.md` | Always expand with **at least** the linked doc’s title + one chunk or abstract |
| **Hierarchical** | Parent heading / doc outline (`##` path) | Expand **child hit** with **parent section** for surrounding intent |
| **Same thread** | Shared `area` + `product` (and optionally `tags` overlap) | Suggest **cross-domain** neighbours: e.g. pull **testing** + **functional** when `area` matches and query is broad |
| **Supersession** | `supersedes` / `superseded_by`, `status: deprecated` | Prefer **canonical** chunk; optionally include deprecated **only** with a “superseded” warning |

#### 5.10.2 Context pack assembly (behaviour)

A **context pack** is not a flat list: it is a **budgeted** set of chunks (by max tokens / max chunks) assembled with rules:

1. **Retrieve** top‑`N` candidates (hybrid when §10 V1+ is available; else semantic-first in MVP).
2. **Rerank (mandatory, §5.5):** score candidates with query–passage reranker; order by **`rerank_score`** before diversification.
3. **Diversify (MVP: required):** **cap chunks per document** so one long note does not crowd out others. **V1+ (recommended):** add **MMR** or equivalent for extra diversity (after rerank ordering).
4. **Relational expansion:** **MVP:** always follow front matter **`related:`** (and inline `knowledge/...md` links when trivially detectable). **V1+:** optional **same-`area`, different-`domain`** peers when `profile: full` (or similar) requests a **full picture** (technical + functional + testing).
5. **Ordering:** group by **`domain`** or **relation role** in the JSON (so clients can prompt “Engineering”, “Product”, “QA”)—**recommended** in MVP, **required** in V1+ for multi-domain packs.
6. **Budget:** fill up to `max_tokens` with **declining priority**: direct hits → explicit links → optional cross-domain fillers.
7. **Transparency (MVP: required):** each chunk lists `inclusion_reason: hit \| expanded_parent \| related_doc \| same_area_peer \| deprecated_warning`.

#### 5.10.3 Optional hints (improve relevance)

- **`intent` or `profile` query params** (e.g. `coding`, `testing`, `product`, `mixed`): nudge metadata filters and relation weights—**not** required for MVP but recommended for V1+.
- **`role` hint** (`dev` \| `qe` \| `pm`): slight boost to matching `author_role` / `domain`—optional.

#### 5.10.4 Why this improves downstream agent analysis

- **Mandatory reranking (§5.5)** fixes ordering where **embedding similarity alone** is misleading—so the **best** passages lead the context pack.
- **Relations** supply **missing halves** of the story (implementation + acceptance + how we test).
- **Diversity** reduces **duplicate** context that wastes the context window.
- **Structured grouping** matches how **multi-step** analysis works in agent tools.
- **Citations + inclusion_reason** keep outputs **auditable** (§5.7).

### 5.11 Advanced RAG implementation ladder (beyond naïve embed → cosine top‑k)

**“Smart” RAG** here is **layered**: several specialised stages, each fixing a different failure mode of naïve **embed → cosine top‑k**. The normative minimum for this product is already in **§5.4–§5.7**, **§5.10**, and **§10**; this subsection ties **optional / V1+** advances into one ladder.

#### 5.11.1 Retrieval stack (precision + recall)

| Layer | What it fixes | Notes |
|-------|----------------|-------|
| **Hybrid retrieval** | Exact tokens (paths, APIs, errors) vs fuzzy meaning | Dense + **BM25 / sparse**; fuse (e.g. **RRF** or weighted sum)—**V1+** hardening (§10). |
| **Query side** | Vague or mismatched wording | **Optional (measure first):** light **query rewrite** or **HyDE** only where a **golden set** shows lift—otherwise skip (latency + risk). |
| **Mandatory rerank** | Wrong ordering in top‑k | **Normative (§5.5):** cross‑encoder or **lightweight local** reranker on **20–40 → 8–12** (typical). |
| **MMR / caps per doc** | One doc dominating the window | **After rerank:** diversify—**MVP** caps per doc; **V1+** optional **MMR** (§5.10). |

#### 5.11.2 Context assembly (what goes to the assistant)

Many simple RAG systems stop too early; **knowledgeIntelligence** does not (§5.10):

| Technique | Role |
|-----------|------|
| **Graph‑light expansion** | `related`, same `area` / `product`, parent heading—**deterministic rules + token budget**, not a giant graph DB on day one. |
| **Multi‑granularity** | **Small chunks** for retrieval; optional **parent window** for generation (retrieve child → expand to section). **V1+** recommended where measured. |
| **Structured packs** | Group by **domain** (technical / functional / testing) so downstream models attend consistently. |

#### 5.11.3 Smarter than one‑shot retrieve (optional)

| Pattern | Use |
|---------|-----|
| **Decomposed queries** | Complex question → **2–3 sub‑queries** → merge/dedup → **one rerank** pass. |
| **Iterative / agentic retrieval** | First pass narrows `area`/doc set; second drills into linked docs—**only** with **logged steps**, **capped iterations**, and **citations** per claim (§5.7). |

#### 5.11.4 Operations that improve quality over time

- **Golden query set** + **recall@k** / **nDCG** after rerank—tune chunking, hybrid weights, reranker from **data** (§5.5, §7, §11).
- **Offline reprocessing** when embedding or reranker model changes—**version** in manifest (§5.5, §12).
- **Stale / conflict handling** (`deprecated`, `supersedes`) so retrieval does not blend contradictions silently (§4.4, §5.10).

#### 5.11.5 Anti‑patterns (often look “advanced” but hurt)

| Avoid | Why |
|-------|-----|
| **Huge chunks** “for more context” | Dilutes embeddings; hurts retrieval precision. |
| **Heavy HyDE on every query** without eval | Adds latency and hallucination surface. |
| **End‑to‑end LLM chooses what to retrieve** with **no citation lock** | Hard to trust in a KB product; conflicts with §5.7. |

**Summary ladder (aligned with this spec):** **hybrid retrieve (V1+)** → **mandatory rerank (MVP)** → **graph‑light / relational context pack (MVP)** → **citation‑locked** downstream use (§5.7). Add **query rewrite**, **multi‑hop**, or **iterative retrieval** only when the **golden set** proves they help.

### 5.12 Coding-assistant agnosticism (cross–agent coding assistant)

**knowledgeIntelligence** MUST NOT depend on a **single** vendor IDE or model. The **product contract** is:

| Layer | Role | Assistant binding |
|-------|------|-------------------|
| **Canonical** | **REST + JSON** (versioned) on `localhost` | **None** — any client can `curl`, script, or use a generated SDK. |
| **Optional** | **MCP server** exposing the same operations as tools | **None** — any host that loads MCP (Cursor, Claude Desktop/Code, other MCP clients) can attach. |
| **Optional** | **CLI** (`retrieve`, `context-pack`, `health`) | **None** — terminal-only workflows. |
| **Optional UX** | `.cursor/skills/*`, editor-specific hooks | **Cursor** (or similar)—**convenience only**; not required to use the knowledge base. |

**Requirements:**

1. **No proprietary-only APIs** as the only integration path—**HTTP** remains documented and stable.
2. **Naming:** user-facing docs and examples MUST list **multiple** assistants where relevant (“Cursor, Claude Code, …”) and state that **others work** via the same REST/MCP surfaces.
3. **Session / trigger language:** §12.1 uses **“coding assistant session”** as the abstract trigger; **one team’s recipe** (e.g. Claude in terminal + MCP) is **an example**, not an exclusive platform lock.
4. **OpenAPI (V1+ recommended):** publish or generate an **OpenAPI** spec for the REST surface so new assistants can integrate without reverse-engineering.
5. **Testing:** golden queries and health checks run against **HTTP** (or CLI)—not against a single IDE plugin.

**Anti-patterns:** hard-coding only the Cursor SDK; requiring a single model provider for retrieval (embedding/rerank are **local/configurable**, not “Claude-only”).

---

## 6. Information architecture (repository layout — draft)

Suggested top-level structure (adjust in review):

```
knowledge/
  technical/
    architecture/
    runbooks/
    decisions/          # ADR-style
  delivery/             # Completed work, analysis, discussion summaries (organise by component, feature area, or time period — team picks convention)
  testing/              # QE-led: test plans, regression notes, quality findings
  functional/
    glossary/
    features/
  meta/                 # how to contribute, templates, golden queries, evaluated SLOs
.templates/             # doc templates (optional)
scripts/                # RAG indexer, embedding pipeline, local API server
```

### 6.1 Front matter schema (YAML)

Every **`knowledge/**/*.md`** file MUST include YAML front matter between `---` lines. CI validates **required keys** by path (see table).

| Key | Required when | Type | Purpose |
|-----|----------------|------|---------|
| `title` | **Always** | string | Human title for lists and UI |
| `domain` | **Always** (see **Domain inference** below) | string | `technical` \| `delivery` \| `testing` \| `functional` \| `meta` — RAG metadata filters; **canonical value is determined by file path** under `knowledge/` |
| `area` | **Always** | string | Product or system area (e.g. `billing`, `auth`, `reports`) — links dev, QE, PM, DM to the same **feature/product** surface |
| `tags` | Optional | string[] | Fine-grained labels |
| `author_role` | **Always** | string | `dev` \| `qe` \| `pm` \| `dm` \| `mixed` |
| `type` | **Always** | string | Doc kind: e.g. `adr`, `runbook`, `delivery-summary`, `test-plan`, `feature`, `glossary` |
| `status` | **Always** | string | `draft` \| `reviewed` \| `deprecated` |
| `last_reviewed` | **When `status: reviewed`** | ISO date `YYYY-MM-DD` | Freshness and staleness warnings |
| `product` | Recommended under `functional/**` | string | Product or offering the note supports (helps PM/DM queries) |
| `related` | Optional | string[] | Paths to other `.md` files in this repo |
| `supersedes` / `superseded_by` | When obsoleting | string | Canonical replacement path (see §4.4) |
| `contributor` | Optional | string | **Display name** of the person who last substantively edited the note—often pre-filled from **local author profile** (§6.2) |
| `team` | Optional | string | Squad or team name—pre-filled from profile when helpful for DM/PM filters |
| `topics_author` | Optional | string[] | **Topics** this author focuses on (may overlap `tags`)—from profile; helps retrieval when filtering “who knows what” |

**Path norms:**

- `knowledge/functional/**` → `domain: functional`; `author_role` often `pm` or `mixed`.
- `knowledge/testing/**` → `domain: testing`; `author_role` often `qe`.
- `knowledge/delivery/**` → `domain: delivery`; `author_role` often `dev`.
- `knowledge/technical/**` → `domain: technical`; `author_role` often `dev`.
- `knowledge/meta/**` (if used for indexed meta docs) → `domain: meta`.

**Domain inference (canonical):**

1. The **first path segment** after `knowledge/` MUST be one of: `technical`, `delivery`, `testing`, `functional`, `meta`. That segment is the **canonical** `domain` for the file.
2. If front matter **includes** `domain`, it **MUST** equal the canonical value from the path; otherwise CI **fails** the PR (stops silent drift between path and metadata).
3. Authors MAY **omit** `domain` while editing; before merge, **`scripts/validate_frontmatter.py`** (or equivalent) MUST **inject** `domain` from the path **or** fail the PR if it is missing and injection is not enabled—teams choose one policy; the default SHOULD be **inject** so agents only need to place the file under the right subtree.
4. Optional later: a **`--fix`** (or **`write`**) mode on the validator **writes** the correct `domain` into the file locally so contributors run one command before `git add`.

**Validation:** PR CI runs a **schema + path/domain check**; invalid front matter **fails** the PR. Optional keys (`contributor`, `team`, `topics_author`) SHOULD be allowed by the schema when present.

### 6.2 Local author profile (optional editor skill, not committed)

So each member does not re-type **name, team, topics**, the repo MAY ship an **editor skill** for Cursor (`.cursor/skills/knowledge-author-profile/`)—**convenience only** (§5.12)—that tells the agent to read a **local YAML** profile:

- **Canonical path:** `meta/author-profile.local.yaml` (**gitignored**).
- **Example template:** `meta/author-profile.example.yaml` (committed).
- **Machine-wide optional:** `~/.knowledgeintelligence/profile.yaml` — project-local file wins when present.

The agent uses the profile to **suggest** §6.1 fields when committing knowledge (`author_role`, `tags`, `area`, optional `contributor`, `team`, `topics_author`). **Humans still approve** PR content; profile data **never** forces incorrect `area` on a doc.

---

## 7. Non-functional requirements

**Corpus assumptions (adjust in `meta/`):** on the order of **10²–10³** files and **~10–50 MB** raw markdown—large enough that **incremental** index updates matter.

| Area | Requirement (draft SLOs — tighten as the corpus grows) |
|------|-------------|
| **Full index build** | On a typical developer laptop, full rebuild stays **under ~15 minutes** at MVP; stretch **under ~5 minutes** with a mature incremental pipeline. |
| **Incremental build** | After a small change, **p95** rebuild dominated by **re-embed of touched files**, target **under ~2 minutes** (document actuals in `meta/`). |
| **Retrieve / context pack API** | **p95** latency **under ~500 ms** per query locally, excluding **cold start** (cold start allowed if documented once). |
| **Retrieval quality** | Golden query set (§5.5): **recall@5** (correct doc in top 5) **≥ 80%** before changing default chunking without sign-off (threshold evolves with the eval set). |
| **Scale** | Document behaviour at **2× and 5×** reference corpus size (capacity planning). |
| Security | No secrets in repo; pre-merge secret-pattern checks; **air‑gap**: no calls to unapproved embedding endpoints. |
| Observability | Log index duration, files changed, chunk/embed counts, errors; optional **p95** API latency. |
| Licensing | Document embedding model + vector store **license** in `meta/`. |

---

## 8. CI/CD (recommended)

- On **PR:** markdown lint, broken-link check, **front matter schema (§6.1)**, optional **golden-query regression** on dry-run index.
- **Dry-run RAG index build** in CI (or validate chunk counts + schema) so broken content fails before merge.
- On **merge** to default branch: optional **versioned index artefact** (§12)—not required if all consumers build locally.

---

## 9. Open decisions (to fill in as you progress)

- [ ] **PR policy:** minimum reviewers, CODEOWNERS per path.
- [ ] **RAG tooling stack:** vector store (e.g. Chroma, LanceDB, Qdrant local); optional hybrid sparse index (SQLite FTS, Tantivy, etc.).
- [ ] **Embedding model:** local vs API; dimension; offline / air-gap requirement; same model pinned in CI for reproducibility.
- [ ] **Reranker model:** cross-encoder vs lightweight ranker; **approved** local model list; `candidate_k` / `context_pack_k` defaults.
- [ ] **Chunking strategy:** max tokens per chunk; sub-split defaults; overlap values (starting defaults in §5.4).
- [ ] **API surface:** default port, loopback-only defaults; **REST** contract versioning; MCP package layout and **tool naming** (`kb_*` vs other prefix).
- [ ] **Multiple MCPs:** document how many concurrent MCP connections the team uses and **example configs** for major hosts (Cursor, Claude Code, …) plus generic JSON—**no single-vendor lock-in**.
- [ ] **Retention:** how to deprecate or archive stale docs.
- [ ] **Naming/versioning** of the repo and index schema.
- [ ] **Delivery doc granularity:** one doc per small change vs one living doc per feature area; filename and folder convention.
- [ ] **Contribution thresholds:** similarity cutoffs for "edit existing" vs "new doc"; whether PR bot posts related-doc hints.
- [ ] **External refs:** keep zero ticket linkage vs optional opaque internal ids (see §3—do not block MVP).
- [ ] **Numeric SLOs:** replace §7 placeholders with measured p95 after first production-sized corpus.
- [ ] **Auto-index:** `core.hooksPath` vs per-repo `.git/hooks`; fingerprint strategy (`git HEAD` vs content hash); lockfile location.
- [ ] **Auto-sync:** poll interval; ff-only vs merge strategy; behaviour when dirty/diverged; opt-out for active contributors.
- [ ] **Terminal session hook:** MCP loaded by the assistant vs `scripts/ki-session.sh` wrapper vs shell `cd` hook; which one the team standardizes on.

---

## 10. Product phases (MVP and later)

| Phase | Goal | In scope |
|-------|------|----------|
| **MVP** | Compound knowledge from PRs and make it **retrievable** | Markdown under `knowledge/`; ingest → **structure-aware** chunk → embed → **vector** store; **mandatory local rerank** after first-stage retrieve (§5.5); **locally hosted** **HTTP API** on loopback (§5.9) so **any** assistant can call **retrieve/context_pack**; **assistant-agnostic** integration (§5.12); **primary trigger:** **coding-assistant session** starts MCP/API (§12.1) → **auto-sync** + **auto-index** when safe/stale; **health** with `index_status` and `sync_status`; **context packs** with per-doc caps, **`related:`** expansion, **`inclusion_reason`** (§5.10); optional **MCP server** exposing the same ops; **citations** on all passages; front matter **§6.1** + CI validation; **author profile** skill + local yaml (§6.2, optional); golden query file in `meta/` (manual or CI). |
| **V1+** | Better **recall/precision** and **smarter context** | **Hybrid** retrieval (dense + sparse/BM25); **MMR** / richer diversification; optional **cross-domain same-`area` expansion** and **`intent`/`profile` hints** (§5.10); incremental pipeline hardened; optional **contribute --dry-run** (§5.8); MCP tool set hardened for **multi-MCP** Cursor setups. |
| **V2** | Operational excellence | Optional **PR bot** (related docs); optional **published index artefacts** for shared consumers (§12). |

---

## 11. Success metrics and adoption

| Metric | Meaning | Starting target |
|--------|---------|-----------------|
| **Corpus growth** | Markdown files + merged PRs to `knowledge/` per month | Non-zero steady growth; **DM/PM** review trends in standups |
| **Golden-set recall@k** | Correct relevant doc in top *k* | **≥ 80% @5** before changing defaults (§7) |
| **Index build SLO** | Full + incremental times | Meet §7 until corpus outgrows—then re-benchmark |
| **Role coverage** | At least one **reviewed** doc per domain (`technical`, `delivery`, `testing`, `functional`) per major **area** / product | Expands as products/features evolve |
| **Adoption (qualitative)** | Dev/QE/PM/DM report using context packs for **new** and **existing** feature work | Periodic survey or retro note |

---

## 12. Operations: who builds the index and where it lives

- **Source of truth** is always **git**: every merged PR **adds** to the corpus; **knowledge compounds** with each merge.
- **Default (MVP):** each contributor (or local automation) runs **index build** after **pull** or **merge**; generated index files live under a **gitignored** path (e.g. `.rag/index/`) documented in the repo README—not committed unless the team explicitly chooses artefact storage.
- **Serving:** Start the **local API** (and optionally **MCP**) after the index is built; **coding assistants** connect to **`localhost`** (§5.9) to **retrieve before analyze**—no separate cloud dependency for that path.
- **CI:** validates corpus + schema + optional dry-run build; may emit **non-committed** logs or metrics.
- **Optional (V2):** publish a **versioned index tarball** per `main` SHA for teams that want identical local behaviour without rebuilding (still derived from the same commit).

### 12.1 Automatic indexing on checkout and on coding-assistant session start

Goal: when a team member **checks out** this repo (clone, checkout, pull) or **starts a coding-assistant session** (terminal or IDE) with this project, **indexing begins without a manual step** so retrieval is warm or warming. Details are **assistant-agnostic** (§5.12).

**Primary hook (MVP): assistant session starts MCP or local API.** The team picks one **documented** entrypoint. **knowledgeIntelligence** MUST tie indexing (and optional upstream sync—§12.2) to that moment:

| Trigger | Required behaviour (MVP) |
|---------|--------------------------|
| **Coding-assistant session (primary)** | At least one pattern MUST be documented and supported: **(A)** **MCP**: the host assistant loads **knowledgeIntelligence** MCP so **`initialize`** runs the local API or attached service → background **sync** (§12.2, if enabled) → background **index** if missing/stale (**works for any MCP-capable assistant**). **(B)** **Shell wrapper** (e.g. `scripts/ki-session.sh`) that the team aliases to their assistant CLI (**claude**, **cursor**, **etc.**), which spawns API/MCP then **`exec`s** the real binary (non-blocking fork where possible). **(C)** **`direnv` / `.envrc` or shell function** that runs **`ki ensure-index &`** when `cwd` is this repo (weaker: per-shell, not per assistant invocation). **(A) or (B) is preferred.** |
| **Fresh clone / checkout / pull** | **Optional (supplementary):** **git hooks** (e.g. `post-checkout`, `post-merge`) or **`./scripts/install-hooks.sh`**. On trigger, run **`index build` in the background** if **missing or stale**. **Opt-in** install—see caveat below. Hooks **do not** replace the **session** path. |
| **MCP / local API initialize** | Whenever the **MCP server** or **local API** starts: (1) **`/health`** with `index_status`, `sync_status` (§12.2), `corpus_fingerprint`, optional `progress`; (2) **enqueue** background **sync** (if enabled) then **index** if missing/stale; (3) **do not block** handshake on full completion—degraded retrieval until `ready` (§5.9). |
| **IDE workspace open** | **Recommended (V1+):** editor “on folder open” or hooks—same non-blocking rules; secondary to **MCP** for portability across assistants. |

**Staleness / fingerprint:** persist a small file under `.rag/` (gitignored), e.g. `.rag/manifest.json`: `corpus_fingerprint` (hash of sorted `(relpath, sha256 content)` for `knowledge/**` or **git tree `HEAD`** + chunking config hash + embedding model id). If fingerprint mismatch → **stale** → rebuild (incremental when implemented).

**Concurrency:** use a **single-flight lock** (e.g. `.rag/build.lock` or OS lock) so overlapping triggers (pull + MCP start) **do not** run parallel full embeds.

**User experience:** README states: “First use may **build the index in the background**; wait until `GET /health` shows `ready` or watch logs.” Optionally a **desktop notice** is out of scope for MVP.

**Important caveat (Git hooks):** Git **does not** run **server-side** hooks on **`git clone`**. Client hooks run only after **local** git actions **and only if** installed. **“Index on clone, zero steps”** is **not** guaranteed by hooks alone. **Primary path for teams:** an **assistant session** starts **MCP/API** (§12.1 first row)—runs **without** git hook install. **True “on clone with zero install”** still needs the user to **open a session** (or configure MCP) at least once—document in README.

### 12.2 Automatic sync with upstream (no manual `git pull` for consumers)

Goal: when **new commits** land on the tracked **upstream** branch (e.g. `origin/main`), local clones **update automatically** so the **knowledge corpus and index** track the latest merged PRs without the user running **`git pull` manually**.

**Safety (non-negotiable):** automation must **not** clobber work. Default rules:

| Condition | Behaviour |
|-----------|------------|
| **Clean** working tree and index; local branch can **fast-forward** | Run **`git fetch`** then **`git merge --ff-only`** (or equivalent `git pull --ff-only`) to the configured upstream. **No rebase**, **no force**. |
| **Dirty** working tree (uncommitted changes) | **Do not** pull. Surface **`sync_status: blocked_dirty_tree`** via **health** (§5.6) and logs; optionally notify once. User resolves or commits. |
| **Diverged** (local commits not on upstream, non-FF) | **Do not** auto-merge. Surface **`sync_status: blocked_diverged`**; user must integrate manually (branch, rebase, or merge as per team policy). |
| **Detached HEAD** or **no upstream** | **Do not** pull unless `knowledgeIntelligence.sync.upstream` is explicitly set; surface **`sync_status: not_configured`**. |

**Triggers (MVP—at least one must be implemented; all may coexist):**

1. **Same as indexing—assistant session:** on **MCP initialize** (when the coding assistant loads MCP), run **fetch + ff-only** (§12.2 rules) then **reindex** if `HEAD` changed—**primary** alignment with “start session = up to date when safe.”
2. **Periodic timer inside MCP/API:** e.g. every **5–30 min** (default **15 min**) for clones where the session stays open—catches upstream pushes **without** restarting the assistant.
3. **Optional daemon:** documented **`knowledgeintelligence sync`** long-running command that **only** fetch/ff-only + reindex.
4. **Git hooks** supplement only; **not** sufficient when others push upstream unless combined with (1) or (2).

**Configuration (documented env or config file):**

- `upstream_remote` (default `origin`), `upstream_branch` (default `main` or tracked branch).
- `sync_interval_seconds` (0 = only on MCP start, no periodic poll).
- `sync_enabled` (default **true** for “read-only” clones; **false** for contributors actively committing—recommended default **true** with dirty-tree blocking).

**Transparency:** **`/health`** (or MCP tool) SHOULD include `sync_status`, `last_sync_at`, `local_head`, `upstream_head` (after fetch) so **any** integrated assistant can report “knowledge is current as of …” or “sync blocked—uncommitted changes”.

**Relationship to indexing:** after a **successful** ff-only merge, **corpus fingerprint** changes → §12.1 marks index **stale** and **background rebuild** runs (same lock as index build).

---

## 13. Success criteria (first milestone)

1. Repository exists with governance (PR-only to `main`) and documented contribution rules.
2. Developers can **clone** the repo; **starting a coding-assistant session** (per §12.1 **primary** path) triggers **background** upstream sync (if enabled, §12.2) and **index** build when missing/stale; optional git hooks remain supplementary. A manual one-command full build remains available.
3. **Locally hosted** API (or CLI) on **loopback** supports **retrieval** with **mandatory reranking** (§5.5) and **cited chunks** (path + line range + text, **retrieval + rerank scores**); any **generated** answer path attaches citations per §5.7. Documented integration for **HTTP and MCP** so **any** supported assistant can call **before** analysis (§5.9, §5.12). **`/health`** exposes **`sync_status`** and **`index_status`** (§12.1, §12.2).
4. At least one **technical**, one **delivery**, one **testing (QE)**, and one **functional** example—each with valid **§6.1** front matter—so **dev, QE, PM, and DM** can retrieve cross-role context for a shared **area** / product.
5. A **second** merged PR in the same **area** proves **compounding**: retrieval returns both older and newer chunks so **feature work and maintenance** benefit from prior contributions.
6. A **contribute** path (rule, script, or API) demonstrates **retrieve → compare → suggest edit vs new file** with **cited** similar chunks.

---

## 14. Revision history

| Version | Date | Notes |
|---------|------|-------|
| 0.1 | 2025-11-06 | Initial draft |
| 0.2 | 2025-11-06 | Delivery + QE testing docs, cumulative-knowledge outcomes |
| 0.3 | 2025-11-06 | Explicit exclusion of JIRA/work-tracker content from the knowledge base |
| 0.4 | 2025-11-06 | Whole project framed as RAG-based; maintainability via git + simple index rebuild; pipeline and grounding rules updated |
| 0.5 | 2025-11-06 | Agent-assisted contribution: retrieval-first dedup, merge vs new doc, optional contrib endpoint and PR hints |
| 0.6 | 2025-11-06 | Smart chunking (structure-aware) and smart index (hybrid, metadata, incremental, light evaluation) |
| 0.7 | 2025-11-06 | Cumulative knowledge + cross-role (dev/QE/PM/DM); TPM fixes: §6.1 schema, phases, SLOs, metrics, operations, overlap defaults |
| 0.8 | 2025-11-06 | Local hosting (localhost), Cursor/Claude retrieve-then-analyse; multi-MCP coexistence + §5.9 |
| 0.9 | 2025-11-06 | Project name **knowledgeIntelligence** in title and intro |
| 0.10 | 2025-11-06 | §5.10 smart context assembly and relations (Cursor/Claude); §5.6 context pack fields; §10 phase alignment |
| 0.11 | 2025-11-06 | §12.1 auto-index on checkout/pull + Claude/MCP start; health `index_status`; open decision on hooks/fingerprint |
| 0.12 | 2025-11-06 | §12.2 auto **fetch + ff-only** upstream sync; dirty/diverged safety; health `sync_status`; MVP table + success criteria |
| 0.13 | 2025-11-06 | §12.1 caveat: hooks not on clone without install; MCP/API as primary no-hook path |
| 0.14 | 2025-11-06 | §12.1–§12.2: **terminal assistant session** as primary hook (MCP init or wrapper); git hooks supplementary |
| 0.15 | 2025-11-06 | **Mandatory reranking** (§5.5): local cross-encoder/light ranker; API `rerank_score`; MVP/V2 table and §5.10 step order |
| 0.16 | 2025-11-06 | §6.2 local author profile skill + optional front matter `contributor`/`team`/`topics_author`; `meta/author-profile.example.yaml`; `.gitignore` for local profile |
| 0.17 | 2025-11-06 | §5.12 coding-assistant agnosticism; §12.1 generic session hook; wording aligned HTTP/MCP-first |
| 0.18 | 2025-11-06 | §5.11 Advanced RAG implementation ladder (layered stack; subsections 5.11.1–5.11.5); agnosticism renumbered §5.12 |
| 0.19 | 2025-11-06 | Intro: maintain/share/reuse/analysis + template adoption; §4.5 adopt-as-template (clone → new remote → push) |
| 0.20 | 2025-11-06 | §6.1 **Domain inference:** path-canonical `domain`; omit-allowed + validator inject; mismatch fails; `knowledge/meta/**` path norm |
| 0.21 | 2025-11-06 | **docs:** [ARCHITECTURE.md](ARCHITECTURE.md) (C4-style context, components, sequence flows); [LEADERSHIP_PITCH.md](LEADERSHIP_PITCH.md); intro links |
| 0.22 | 2025-11-06 | **Build slice:** `ki/` package, `scripts/validate_frontmatter.py`, `knowledge/` sample, `pytest`, [TESTING.md](TESTING.md), GitHub Actions CI |
| 0.23 | 2025-11-06 | **MVP implementation:** `ki index` / `ki serve` (HTTP `/v1/health`, `/v1/retrieve`, `/v1/context_pack`); tf-idf + mandatory rerank; `.rag/` manifest + lock; `meta/golden_queries.yaml`; [scripts/ki-session.sh](scripts/ki-session.sh) |
| 0.24 | 2025-11-06 | **Hybrid retrieval:** BM25 + dense tf‑idf → RRF; index staging dir + atomic rename; manifest only after successful swap; [docs/openapi.yaml](openapi.yaml); [scripts/golden_queries.py](../scripts/golden_queries.py); CI golden run |
