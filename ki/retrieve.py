"""Retrieve → mandatory rerank → context pack (MVP — REQUIREMENTS §5.5, §5.10)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ki.index_model import CorpusIndex, build_query_vector, cosine_sim
from ki.tokenize import tokenize


@dataclass
class ScoredChunk:
    chunk_id: str
    doc_path: str
    heading_path: str
    text: str
    line_start: int
    line_end: int
    meta: dict[str, Any]
    retrieval_score: float
    rerank_score: float


def pairwise_rerank_score(query: str, text: str) -> float:
    """
    Lightweight local 'cross-encoder' surrogate: token overlap density + char trigram-ish.
    Mandatory rerank stage per §5.5 (not identity).
    """
    q = set(tokenize(query))
    if not q:
        return 0.0
    tl = (text or "").lower()
    hits = sum(1 for t in q if t in tl)
    base = hits / (len(q) ** 0.5)
    # Bonus for phrase-ish: consecutive query tokens in order
    q_list = tokenize(query)
    if len(q_list) >= 2:
        bigrams = sum(1 for i in range(len(q_list) - 1) if f"{q_list[i]} {q_list[i + 1]}" in tl)
        base += 0.15 * bigrams
    return float(base)


def retrieve_candidates(
    index: CorpusIndex,
    query: str,
    *,
    top_n: int = 24,
    domain: str | None = None,
    area: str | None = None,
) -> list[tuple[Any, float]]:
    """First stage: tf-idf cosine on chunk vectors."""
    qvec = build_query_vector(query, index.idf, total_docs=index.total_docs)
    scored: list[tuple[int, float]] = []
    for i, cv in enumerate(index.chunk_vectors):
        ch = index.chunks[i]
        if domain and (ch.meta.get("domain") or "") != domain:
            continue
        if area and (ch.meta.get("area") or "") != area:
            continue
        scored.append((i, cosine_sim(qvec, cv)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [(index.chunks[i], s) for i, s in scored[:top_n]]


def rerank(query: str, candidates: list[tuple[Any, float]], *, take: int = 12) -> list[ScoredChunk]:
    """§5.5 mandatory rerank on expanded candidate set."""
    out: list[ScoredChunk] = []
    for ch, rscore in candidates:
        rr = pairwise_rerank_score(query, ch.text)
        combined = 0.45 * float(rscore) + 0.55 * float(rr)
        out.append(
            ScoredChunk(
                chunk_id=ch.chunk_id,
                doc_path=ch.doc_path,
                heading_path=ch.heading_path,
                text=ch.text,
                line_start=ch.line_start,
                line_end=ch.line_end,
                meta=dict(ch.meta),
                retrieval_score=float(rscore),
                rerank_score=float(combined),
            )
        )
    out.sort(key=lambda x: x.rerank_score, reverse=True)
    return out[:take]


def build_context_pack(
    index: CorpusIndex,
    query: str,
    *,
    candidate_k: int = 24,
    pack_k: int = 8,
    cap_per_doc: int = 2,
    domain: str | None = None,
    area: str | None = None,
) -> list[dict[str, Any]]:
    """
    §5.10 context pack: retrieve → rerank → cap per doc → expand related (MVP).
    """
    cands = retrieve_candidates(index, query, top_n=candidate_k, domain=domain, area=area)
    ranked = rerank(query, cands, take=max(pack_k * 2, 12))
    pack: list[dict[str, Any]] = []
    per_doc: dict[str, int] = {}
    for sc in ranked:
        n = per_doc.get(sc.doc_path, 0)
        if n >= cap_per_doc:
            continue
        per_doc[sc.doc_path] = n + 1
        pack.append(
            {
                "chunk_id": sc.chunk_id,
                "doc_path": sc.doc_path,
                "heading_path": sc.heading_path,
                "text": sc.text,
                "line_start": sc.line_start,
                "line_end": sc.line_end,
                "retrieval_score": sc.retrieval_score,
                "rerank_score": sc.rerank_score,
                "inclusion_reason": "hit",
                "meta": {k: v for k, v in sc.meta.items() if not str(k).startswith("_")},
            }
        )
        if len(pack) >= pack_k:
            break

    # Related expansion from top hit
    if pack:
        top_meta = pack[0]["meta"]
        rel = top_meta.get("related")
        if isinstance(rel, list):
            by_path = {c.doc_path: c for c in index.chunks}
            for rp in rel:
                if not isinstance(rp, str) or len(pack) >= pack_k + 3:
                    break
                rp_norm = rp.replace("\\", "/")
                if rp_norm in by_path and all(p["doc_path"] != rp_norm for p in pack):
                    ch = by_path[rp_norm]
                    pack.append(
                        {
                            "chunk_id": ch.chunk_id,
                            "doc_path": ch.doc_path,
                            "heading_path": ch.heading_path,
                            "text": ch.text[:4000],
                            "line_start": ch.line_start,
                            "line_end": ch.line_end,
                            "retrieval_score": 0.0,
                            "rerank_score": 0.0,
                            "inclusion_reason": "related_doc",
                            "meta": {k: v for k, v in ch.meta.items() if not str(k).startswith("_")},
                        }
                    )
    return pack
