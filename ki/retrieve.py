"""Retrieve (hybrid dense + BM25 → RRF) → mandatory rerank → context pack (REQUIREMENTS §5.5, §5.10)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ki.bm25 import bm25_score
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
    dense_score: float = 0.0
    sparse_score: float = 0.0
    fused_score: float = 0.0


def rrf_fuse(ranks_a: list[int], ranks_b: list[int], *, k_rrf: float = 60.0) -> dict[int, float]:
    """Reciprocal Rank Fusion (RRF) over two ranked lists of chunk indices."""
    scores: dict[int, float] = {}
    for r, idx in enumerate(ranks_a):
        scores[idx] = scores.get(idx, 0.0) + 1.0 / (k_rrf + r + 1)
    for r, idx in enumerate(ranks_b):
        scores[idx] = scores.get(idx, 0.0) + 1.0 / (k_rrf + r + 1)
    return scores


def pairwise_rerank_score(query: str, text: str) -> float:
    """Lightweight local reranker (mandatory second stage per §5.5)."""
    q = set(tokenize(query))
    if not q:
        return 0.0
    tl = (text or "").lower()
    hits = sum(1 for t in q if t in tl)
    base = hits / (len(q) ** 0.5)
    q_list = tokenize(query)
    if len(q_list) >= 2:
        bigrams = sum(1 for i in range(len(q_list) - 1) if f"{q_list[i]} {q_list[i + 1]}" in tl)
        base += 0.15 * bigrams
    return float(base)


def _filter_chunk(
    ch: Any,
    *,
    domain: str | None,
    area: str | None,
    include_archived: bool = False,
) -> bool:
    if domain and (ch.meta.get("domain") or "") != domain:
        return False
    if area and (ch.meta.get("area") or "") != area:
        return False
    if not include_archived and ch.meta.get("exclude_from_default_retrieval") is True:
        return False
    return True


def retrieve_candidates(
    index: CorpusIndex,
    query: str,
    *,
    top_n: int = 24,
    domain: str | None = None,
    area: str | None = None,
    include_archived: bool = False,
    rrf_k: float = 60.0,
) -> list[tuple[Any, float, float, float]]:
    """
    First stage: **hybrid** — dense tf-idf cosine + BM25, fused with RRF (§5.5 V1+ pattern).

    Returns list of (chunk, fused_score, dense_score, sparse_score).
    """
    qvec = build_query_vector(query, index.idf, total_docs=index.total_docs)
    q_terms = tokenize(query)

    dense_ranked: list[tuple[int, float]] = []
    for i, cv in enumerate(index.chunk_vectors):
        ch = index.chunks[i]
        if not _filter_chunk(ch, domain=domain, area=area, include_archived=include_archived):
            continue
        dense_ranked.append((i, cosine_sim(qvec, cv)))
    dense_ranked.sort(key=lambda x: x[1], reverse=True)

    sparse_ranked: list[tuple[int, float]] = []
    for i, tf in enumerate(index.chunk_term_freqs):
        ch = index.chunks[i]
        if not _filter_chunk(ch, domain=domain, area=area, include_archived=include_archived):
            continue
        dl = index.bm25_doc_lens[i] if i < len(index.bm25_doc_lens) else sum(tf.values())
        s = bm25_score(
            q_terms,
            tf,
            dl,
            idf=index.bm25_idf,
            avgdl=index.bm25_avgdl or 1.0,
        )
        sparse_ranked.append((i, s))
    sparse_ranked.sort(key=lambda x: x[1], reverse=True)

    dense_order = [i for i, _ in dense_ranked]
    sparse_order = [i for i, _ in sparse_ranked]
    fused = rrf_fuse(dense_order, sparse_order, k_rrf=rrf_k)

    # Rank by fused score; break ties with dense then sparse
    dense_map = {i: s for i, s in dense_ranked}
    sparse_map = {i: s for i, s in sparse_ranked}
    all_idx = sorted(
        fused.keys(),
        key=lambda i: (-fused[i], -dense_map.get(i, 0.0), -sparse_map.get(i, 0.0)),
    )[:top_n]

    out: list[tuple[Any, float, float, float]] = []
    for i in all_idx:
        ch = index.chunks[i]
        out.append(
            (
                ch,
                float(fused[i]),
                float(dense_map.get(i, 0.0)),
                float(sparse_map.get(i, 0.0)),
            )
        )
    return out


def rerank(
    query: str,
    candidates: list[tuple[Any, float, float, float]],
    *,
    take: int = 12,
) -> list[ScoredChunk]:
    """§5.5 mandatory rerank: combine fused retrieval with pairwise scorer."""
    out: list[ScoredChunk] = []
    for ch, fused, ds, ss in candidates:
        rr = pairwise_rerank_score(query, ch.text)
        combined = 0.35 * float(fused) + 0.65 * float(rr)
        out.append(
            ScoredChunk(
                chunk_id=ch.chunk_id,
                doc_path=ch.doc_path,
                heading_path=ch.heading_path,
                text=ch.text,
                line_start=ch.line_start,
                line_end=ch.line_end,
                meta=dict(ch.meta),
                retrieval_score=float(fused),
                rerank_score=float(combined),
                dense_score=float(ds),
                sparse_score=float(ss),
                fused_score=float(fused),
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
    include_archived: bool = False,
) -> list[dict[str, Any]]:
    """§5.10: retrieve → rerank → cap per doc → expand related."""
    cands = retrieve_candidates(
        index,
        query,
        top_n=candidate_k,
        domain=domain,
        area=area,
        include_archived=include_archived,
    )
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
                "dense_score": sc.dense_score,
                "sparse_score": sc.sparse_score,
                "inclusion_reason": "hit",
                "meta": {k: v for k, v in sc.meta.items() if not str(k).startswith("_")},
            }
        )
        if len(pack) >= pack_k:
            break

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
                            "dense_score": 0.0,
                            "sparse_score": 0.0,
                            "inclusion_reason": "related_doc",
                            "meta": {k: v for k, v in ch.meta.items() if not str(k).startswith("_")},
                        }
                    )
    return pack
