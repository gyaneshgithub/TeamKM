"""Index freshness vs corpus fingerprint (operator / health)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ki.fingerprint import corpus_fingerprint
from ki.index_runner import index_dir, manifest_path, rag_root
from ki.manifest import read_manifest


def index_freshness(repo_root: Path) -> dict[str, Any]:
    """
    Compare live corpus fingerprint to manifest.

    ``index_stale`` is true when the indexed fingerprint lags the corpus or
    index files are missing / not ready.
    """
    root = repo_root.resolve()
    fp_current = corpus_fingerprint(root)
    rr = rag_root(root)
    m = read_manifest(rr) or {}
    fp_indexed = str(m.get("corpus_fingerprint", "") or "")
    status = str(m.get("index_status", "missing"))
    chunks = index_dir(root) / "chunks.json"
    index_ok = chunks.is_file() and status == "ready"

    stale = not index_ok
    if index_ok and fp_indexed and fp_indexed != fp_current:
        stale = True
        status = "stale"

    return {
        "index_status": status,
        "index_stale": stale,
        "corpus_fingerprint_current": fp_current,
        "corpus_fingerprint_indexed": fp_indexed or None,
        "chunk_count": m.get("chunk_count"),
        "manifest_present": manifest_path(root).is_file(),
    }
