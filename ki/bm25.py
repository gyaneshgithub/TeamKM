"""Okapi BM25 over chunk term frequencies (sparse leg of hybrid retrieval)."""

from __future__ import annotations

import math
from typing import Any


def bm25_idf(N: int, df: int) -> float:
    # Lucene-style idf (smooth)
    return math.log(1 + (N - df + 0.5) / (df + 0.5))


def build_bm25_stats(
    term_tfs: list[dict[str, int]],
) -> tuple[dict[str, float], list[int], float]:
    """
    N = len(term_tfs); df[t] = chunk count containing t; doc_len[i] = sum(tf).
    Returns (idf_per_term, doc_lens, avgdl).
    """
    N = len(term_tfs)
    df: dict[str, int] = {}
    doc_lens: list[int] = []
    for tf in term_tfs:
        dl = sum(tf.values())
        doc_lens.append(dl)
        for t in tf.keys():
            df[t] = df.get(t, 0) + 1
    avgdl = (sum(doc_lens) / N) if N else 0.0
    idf: dict[str, float] = {}
    for t, dfi in df.items():
        idf[t] = bm25_idf(N, dfi)
    return idf, doc_lens, avgdl


def bm25_score(
    query_terms: list[str],
    tf: dict[str, int],
    doc_len: int,
    *,
    idf: dict[str, float],
    avgdl: float,
    k1: float = 1.2,
    b: float = 0.75,
) -> float:
    if avgdl <= 0 or doc_len < 0:
        return 0.0
    score = 0.0
    for q in query_terms:
        if q not in tf:
            continue
        idfi = idf.get(q)
        if idfi is None:
            continue
        f = tf[q]
        denom = f + k1 * (1 - b + b * doc_len / avgdl)
        score += idfi * (f * (k1 + 1)) / denom
    return float(score)
