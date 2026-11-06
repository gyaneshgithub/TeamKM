"""Build index into .rag/index with lock + manifest (§12.1)."""

from __future__ import annotations

import time
from pathlib import Path

from ki.fingerprint import corpus_fingerprint
from ki.index_model import EMBEDDING_MODEL_ID, build_index, save_index_to_disk
from ki.lockfile import index_build_lock
from ki.manifest import read_manifest, write_manifest
from ki.sync_status import compute_sync_status


def rag_root(repo_root: Path) -> Path:
    return repo_root.resolve() / ".rag"


def index_dir(repo_root: Path) -> Path:
    return rag_root(repo_root) / "index"


def lock_path(repo_root: Path) -> Path:
    return rag_root(repo_root) / "build.lock"


def manifest_path(repo_root: Path) -> Path:
    return rag_root(repo_root) / "manifest.json"


def needs_build(repo_root: Path) -> bool:
    root = repo_root.resolve()
    idx = index_dir(root)
    if not manifest_path(root).is_file() or not (idx / "chunks.json").is_file():
        return True
    m = read_manifest(rag_root(root)) or {}
    current = corpus_fingerprint(root)
    return m.get("corpus_fingerprint") != current


def build_index_blocking(repo_root: Path) -> None:
    """Full rebuild; caller holds lock."""
    root = repo_root.resolve()
    rroot = rag_root(root)
    idir = index_dir(root)
    rroot.mkdir(parents=True, exist_ok=True)
    sync = compute_sync_status(root).sync_status
    write_manifest(
        rroot,
        corpus_fingerprint="",
        index_status="building",
        embedding_model_id=EMBEDDING_MODEL_ID,
        reranker_model_id="mvp-pairwise-tf-idf",
        sync_status=sync,
    )
    try:
        index = build_index(root)
        save_index_to_disk(index, idir)
        write_manifest(
            rroot,
            corpus_fingerprint=index.corpus_fingerprint,
            index_status="ready",
            embedding_model_id=EMBEDDING_MODEL_ID,
            reranker_model_id="mvp-pairwise-tf-idf",
            sync_status=sync,
            extra={
                "chunk_count": len(index.chunks),
                "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
    except Exception as e:
        write_manifest(
            rroot,
            corpus_fingerprint=corpus_fingerprint(root),
            index_status="missing",
            embedding_model_id=EMBEDDING_MODEL_ID,
            reranker_model_id="mvp-pairwise-tf-idf",
            sync_status=sync,
            extra={"error": str(e)},
        )
        raise


def ensure_index(repo_root: Path) -> str:
    """
    If index is stale/missing, rebuild under lock. Returns index_status string.
    """
    root = repo_root.resolve()
    if not needs_build(root):
        m = read_manifest(rag_root(root)) or {}
        return str(m.get("index_status", "ready"))

    with index_build_lock(lock_path(root)):
        if not needs_build(root):
            m = read_manifest(rag_root(root)) or {}
            return str(m.get("index_status", "ready"))
        build_index_blocking(root)
    return "ready"


def load_index_optional(repo_root: Path):
    from ki.index_model import load_index_from_disk

    root = repo_root.resolve()
    idir = index_dir(root)
    if not (idir / "chunks.json").is_file():
        return None
    return load_index_from_disk(idir)
