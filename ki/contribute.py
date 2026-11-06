"""Retrieval-first contribution suggestions (REQUIREMENTS §5.8)."""

from __future__ import annotations

import re
from typing import Any

from ki.index_runner import ensure_index, load_index_optional
from ki.retrieve import retrieve_candidates, rerank

# Tunable; teams may override in meta/contribute_policy.yaml later.
THRESHOLD_NEAR_DUPLICATE = 0.55
THRESHOLD_EXTENSION = 0.22


def _draft_query(draft_markdown: str) -> str:
    text = draft_markdown.strip()
    if text.startswith("---"):
        m = re.search(r"^---\s*\r?\n.*?\r?\n---\s*\r?\n", text, re.DOTALL)
        if m:
            text = text[m.end() :]
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    head = "\n".join(lines[:24])
    return head[:8000] if head else text[:8000]


def contribute_dry_run(
    repo_root: Any,
    draft_markdown: str,
    *,
    candidate_k: int = 24,
    top_k: int = 8,
    domain: str | None = None,
    area: str | None = None,
) -> dict[str, Any]:
    """
    Returns similar chunks + suggested action: edit | extend | new_doc.
    """
    from pathlib import Path

    root = Path(repo_root).resolve()
    ensure_index(root)
    idx = load_index_optional(root)
    if idx is None:
        return {"error": "index_unavailable", "suggested_action": "unknown", "similar": []}

    q = _draft_query(draft_markdown)
    if not q.strip():
        return {"error": "empty_draft", "suggested_action": "new_doc", "similar": []}

    cands = retrieve_candidates(idx, q, top_n=candidate_k, domain=domain, area=area)
    ranked = rerank(q, cands, take=top_k)
    similar = [
        {
            "chunk_id": s.chunk_id,
            "doc_path": s.doc_path,
            "heading_path": s.heading_path,
            "snippet": (s.text[:500] + "…") if len(s.text) > 500 else s.text,
            "retrieval_score": s.retrieval_score,
            "rerank_score": s.rerank_score,
        }
        for s in ranked
    ]

    best = ranked[0].rerank_score if ranked else 0.0
    top_paths = [s.doc_path for s in ranked[:3]]

    if best >= THRESHOLD_NEAR_DUPLICATE:
        action = "edit"
        reason = "high similarity to existing chunk(s)—prefer revising an existing doc/section"
    elif best >= THRESHOLD_EXTENSION:
        action = "extend"
        reason = "related content exists—consider adding a section or patching linked docs"
    else:
        action = "new_doc"
        reason = "low overlap with corpus—new file may be appropriate"

    return {
        "suggested_action": action,
        "reason": reason,
        "best_rerank_score": best,
        "thresholds": {
            "near_duplicate": THRESHOLD_NEAR_DUPLICATE,
            "extension": THRESHOLD_EXTENSION,
        },
        "top_doc_paths": top_paths,
        "similar": similar,
    }
