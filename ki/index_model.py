"""In-memory index (MVP dense surrogate: tf-idf cosine). REQUIRED §5.5 rerank applied in ki/retrieve.py."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ki.chunking import Chunk, chunk_markdown_file
from ki.fingerprint import corpus_fingerprint
from ki.tokenize import term_freq

INDEX_SCHEMA_VERSION = "0.1.0"
EMBEDDING_MODEL_ID = "mvp-tfidf"


@dataclass
class CorpusIndex:
    chunks: list[Chunk] = field(default_factory=list)
    corpus_fingerprint: str = ""
    idf: dict[str, float] = field(default_factory=dict)
    chunk_vectors: list[dict[str, float]] = field(default_factory=list)
    total_docs: int = 0


def _build_idf(chunks: list[Chunk]) -> dict[str, float]:
    df: dict[str, int] = {}
    n = len(chunks)
    for ch in chunks:
        tf = ch.meta.get("_tf") or {}
        terms = set(tf.keys())
        for t in terms:
            df[t] = df.get(t, 0) + 1
    idf: dict[str, float] = {}
    for t, dfi in df.items():
        idf[t] = math.log((n + 1) / (dfi + 1.0)) + 1.0
    return idf


def _tfidf_vec(tf: dict[str, int], idf: dict[str, float]) -> dict[str, float]:
    vec: dict[str, float] = {}
    for t, f in tf.items():
        if t not in idf or f <= 0:
            continue
        vec[t] = (1.0 + math.log(f)) * idf[t]
    return vec


def _norm(vec: dict[str, float]) -> float:
    return math.sqrt(sum(v * v for v in vec.values())) or 1.0


def cosine_sim(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = 0.0
    for t, av in a.items():
        if t in b:
            dot += av * b[t]
    return dot / (_norm(a) * _norm(b))


def build_index(repo_root: Path) -> CorpusIndex:
    root = repo_root.resolve()
    fp = corpus_fingerprint(root)
    files = sorted((root / "knowledge").rglob("*.md")) if (root / "knowledge").is_dir() else []
    chunks: list[Chunk] = []
    for f in files:
        chunks.extend(chunk_markdown_file(f, repo_root=root))
    idf = _build_idf(chunks)
    vectors: list[dict[str, float]] = []
    for ch in chunks:
        tf = ch.meta.get("_tf") or {}
        assert isinstance(tf, dict)
        itf = {k: int(v) for k, v in tf.items()}
        vectors.append(_tfidf_vec(itf, idf))
    return CorpusIndex(chunks=chunks, corpus_fingerprint=fp, idf=idf, chunk_vectors=vectors, total_docs=len(chunks))


def build_query_vector(query: str, idf: dict[str, float], *, total_docs: int) -> dict[str, float]:
    qtf = term_freq(query)
    return _tfidf_vec(dict(qtf), idf)


def _serialize_chunk(ch: Chunk) -> dict[str, Any]:
    meta = {k: v for k, v in ch.meta.items() if not str(k).startswith("_")}
    return {
        "chunk_id": ch.chunk_id,
        "doc_path": ch.doc_path,
        "heading_path": ch.heading_path,
        "text": ch.text,
        "line_start": ch.line_start,
        "line_end": ch.line_end,
        "meta": meta,
    }


def save_index_to_disk(index: CorpusIndex, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "embedding_model_id": EMBEDDING_MODEL_ID,
        "reranker_model_id": "mvp-pairwise-tf-idf",
        "corpus_fingerprint": index.corpus_fingerprint,
        "chunk_count": len(index.chunks),
        "chunks": [_serialize_chunk(c) for c in index.chunks],
    }
    (dest_dir / "chunks.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dest_dir / "idf.json").write_text(json.dumps(index.idf, indent=2) + "\n", encoding="utf-8")
    (dest_dir / "vectors.json").write_text(json.dumps(index.chunk_vectors) + "\n", encoding="utf-8")


def load_index_from_disk(src_dir: Path) -> CorpusIndex:
    payload = json.loads((src_dir / "chunks.json").read_text(encoding="utf-8"))
    idf = json.loads((src_dir / "idf.json").read_text(encoding="utf-8"))
    vectors = json.loads((src_dir / "vectors.json").read_text(encoding="utf-8"))
    chunks: list[Chunk] = []
    for ent in payload["chunks"]:
        chunks.append(
            Chunk(
                chunk_id=ent["chunk_id"],
                doc_path=ent["doc_path"],
                heading_path=ent["heading_path"],
                text=ent["text"],
                line_start=int(ent["line_start"]),
                line_end=int(ent["line_end"]),
                meta=dict(ent.get("meta", {})),
            )
        )
    return CorpusIndex(
        chunks=chunks,
        corpus_fingerprint=payload.get("corpus_fingerprint", ""),
        idf={k: float(v) for k, v in idf.items()},
        chunk_vectors=[{k: float(v) for k, v in vec.items()} for vec in vectors],
        total_docs=len(chunks),
    )
