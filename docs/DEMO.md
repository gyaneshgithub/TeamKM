# Groundline — interview demo script (~10 minutes)

Use this page for **live demos**, screen recordings, or pair-programming interviews. All commands assume **repository root** with Python **3.10+**.

**Prep (before the call):**

```bash
git clone https://github.com/gyaneshgithub/TeamKM.git
cd TeamKM
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,mcp]"
python3 -m ki --root . index
```

---

## 1. Story (30 seconds)

Groundline keeps **team knowledge in git** with PR review, builds a **local index**, and answers via **hybrid retrieval + rerank** with **`doc_path` citations**. Optional **MCP** wires the same API into Cursor or other agent hosts.

---

## 2. CI / quality gates (1 min)

```bash
pytest -q
python3 scripts/validate_frontmatter.py --root .
python3 -m ki --root . status
python3 scripts/golden_queries.py --root .
python3 -m ki --root . eval --report md
```

**Say:** front matter is schema-validated; golden queries are **retrieval regression** (recall@k + MRR); `status` shows if the index lags the corpus.

---

## 3. Start API (1 min)

Terminal A:

```bash
python3 -m ki --root . serve --host 127.0.0.1 --port 8765
```

Terminal B:

```bash
curl -s http://127.0.0.1:8765/v1/health | python3 -m json.tool
```

Point at `index_status: "ready"`, `index_stale: false`, and matching `corpus_fingerprint_current` / `corpus_fingerprint_indexed`.

---

## 4. Retrieve with citations (2 min)

```bash
curl -s http://127.0.0.1:8765/v1/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"query":"How does draft promotion work on merge to main?","candidate_k":24,"pack_k":8}' \
  | python3 -m json.tool
```

**Say:** each chunk includes **`doc_path`** and text — assistants should **cite** these, not invent.

**Context pack** (richer bundle):

```bash
curl -s http://127.0.0.1:8765/v1/context_pack \
  -H 'Content-Type: application/json' \
  -d '{"query":"Groundline MCP integration","pack_k":6}' \
  | python3 -m json.tool
```

---

## 5. OpenAPI (30 s)

```bash
curl -s http://127.0.0.1:8765/openapi.json | python3 -m json.tool | head -30
```

**Say:** agent hosts can codegen clients; MCP tools are thin wrappers over the same routes ([MCP.md](MCP.md)).

---

## 6. Contribute dry-run (1 min)

```bash
python3 -m ki --root . contribute -f knowledge/technical/meta/workflow-validation.md
```

**Say:** before adding a doc, check **overlap** with existing corpus (REQUIREMENTS §5.8).

---

## 7. MCP (optional, 2 min)

With API still running, show config concept ([MCP.md](MCP.md)):

```bash
python3 -m ki --root . mcp
```

(stdio — wire in Cursor MCP settings; tools `teamkm_health`, `teamkm_retrieve`, `teamkm_context_pack`.)

**Say:** host runs the LLM; Groundline runs **retrieve-first** policy via prompt `teamkm_retrieve_first`.

---

## 8. Docs site (30 s)

Open: [https://gyaneshgithub.github.io/TeamKM/](https://gyaneshgithub.github.io/TeamKM/)

**Say:** role-based MkDocs for eng / management / product / QE; [PORTFOLIO.md](PORTFOLIO.md) for hiring narrative.

---

## 9. Architecture one-liner (30 s)

Chunk → hybrid BM25 + tf-idf → RRF → **mandatory rerank** → pack. Details: [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 10. Q&A prompts interviewers like

| Question | Point to |
|----------|----------|
| Why local-first? | REQUIREMENTS §5.2, `.rag/` gitignored |
| How prevent secret leak? | REQUIREMENTS §3, skill `teamkm-no-secrets` |
| Multi-team? | REQUIREMENTS §4.6, one corpus per remote |
| Why not only embeddings API? | Hybrid + rerank in `ki/retrieve.py`; golden queries in CI |

---

## Screen recording (90 s)

**Record:** macOS **Cmd+Shift+5** → **Record Selected Portion** (terminal + browser) or full screen.

**Run** (repo root, venv active):

```bash
chmod +x scripts/demo-90s-recording.sh
./scripts/demo-90s-recording.sh
```

The script pauses ~90s total and walks the checklist:

| Step | What viewers see |
|------|------------------|
| 1 | GitHub — [workflow-validation.md](https://github.com/gyaneshgithub/TeamKM/blob/main/knowledge/technical/meta/workflow-validation.md) (knowledge in git) |
| 2 | `ki --root . index`, `status` (and starts `serve` if API is down) |
| 3 | `curl /v1/retrieve` — highlight **`doc_path`** in JSON |
| 4 | [Docs home](https://gyaneshgithub.github.io/TeamKM/) |

**One-liner while recording:** *Groundline keeps reviewed markdown in git, builds a local hybrid index, and returns cited chunks — same API behind MCP and HTTP.*

**Export:** trim to **≤90s**, **1080p** if possible, upload to LinkedIn **Featured** with repo link.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `index unavailable` | `python3 -m ki --root . index` |
| Port in use | `KI_PORT=8766 python3 -m ki --root . serve` |
| Golden FAIL after edit | `ki index` then re-run `golden_queries.py` |
