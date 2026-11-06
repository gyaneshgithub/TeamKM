from __future__ import annotations

from pathlib import Path

from ki.index_model import build_index
from ki.retrieve import retrieve_candidates


def test_hybrid_rrf_matches_bm25_for_exact_keyword(tmp_path: Path):
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    (tmp_path / "knowledge" / "technical" / "a.md").write_text(
        "---\ntitle: A\ndomain: technical\narea: x\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n## Err\nError code ERR_OAUTH_999 sometimes appears.\n",
        encoding="utf-8",
    )
    (tmp_path / "knowledge" / "technical" / "b.md").write_text(
        "---\ntitle: B\ndomain: technical\narea: x\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n## Other\nGeneral notes without the code.\n",
        encoding="utf-8",
    )
    idx = build_index(tmp_path)
    cands = retrieve_candidates(idx, "ERR_OAUTH_999", top_n=5)
    assert cands
    top = cands[0][0]
    assert "a.md" in top.doc_path
