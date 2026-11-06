from __future__ import annotations

from pathlib import Path

from ki.fingerprint import corpus_fingerprint
from ki.index_runner import ensure_index
from ki.retrieve import retrieve_candidates, rerank


def test_fingerprint_stable(tmp_path: Path):
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    (tmp_path / "knowledge" / "technical" / "a.md").write_text(
        "---\ntitle: X\ndomain: technical\narea: t\nauthor_role: dev\ntype: adr\nstatus: draft\n---\n\n## H\nx\n",
        encoding="utf-8",
    )
    a = corpus_fingerprint(tmp_path)
    b = corpus_fingerprint(tmp_path)
    assert a == b


def test_retrieve_and_rerank(tmp_path: Path):
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    (tmp_path / "knowledge" / "technical" / "doc.md").write_text(
        "---\ntitle: Auth\n"
        "domain: technical\narea: auth\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n"
        "## Overview\nWe use OAuth2 for login.\n\n"
        "## Timeouts\nSession timeout is 900 seconds.\n",
        encoding="utf-8",
    )
    ensure_index(tmp_path)
    from ki.index_model import load_index_from_disk

    idx = load_index_from_disk(tmp_path / ".rag" / "index")
    cands = retrieve_candidates(idx, "OAuth2 login", top_n=10)
    ranked = rerank("OAuth2 login", cands, take=5)
    assert ranked
    scores = [s.rerank_score for s in ranked]
    assert scores == sorted(scores, reverse=True)
