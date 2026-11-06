"""Corpus fingerprint: sorted (relpath, sha256) over knowledge/**/*.md (REQUIREMENTS §12.1)."""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_file_content(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def corpus_fingerprint(repo_root: Path, *, knowledge_glob: str = "knowledge/**/*.md") -> str:
    """
    Deterministic fingerprint of all tracked knowledge markdown files.
    Uses content hashes only (not git metadata) so uncommitted edits count.
    """
    root = repo_root.resolve()
    files = sorted(root.glob(knowledge_glob), key=lambda p: p.as_posix())
    h = hashlib.sha256()
    for path in files:
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix().encode()
        h.update(rel)
        h.update(b"\0")
        h.update(hash_file_content(path).encode())
        h.update(b"\n")
    return h.hexdigest()
