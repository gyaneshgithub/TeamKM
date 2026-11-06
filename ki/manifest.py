"""Index manifest under .rag/ (REQUIREMENTS §12.1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ki.atomicio import atomic_write_text
from ki.index_model import INDEX_SCHEMA_VERSION


def manifest_path(rag_root: Path) -> Path:
    return rag_root / "manifest.json"


def write_manifest(
    rag_root: Path,
    *,
    corpus_fingerprint: str,
    index_status: str,
    embedding_model_id: str,
    reranker_model_id: str,
    sync_status: str,
    extra: dict[str, Any] | None = None,
) -> None:
    rag_root.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "corpus_fingerprint": corpus_fingerprint,
        "index_status": index_status,
        "embedding_model_id": embedding_model_id,
        "reranker_model_id": reranker_model_id,
        "sync_status": sync_status,
    }
    if extra:
        data.update(extra)
    atomic_write_text(manifest_path(rag_root), json.dumps(data, indent=2) + "\n")


def read_manifest(rag_root: Path) -> dict[str, Any] | None:
    p = manifest_path(rag_root)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
