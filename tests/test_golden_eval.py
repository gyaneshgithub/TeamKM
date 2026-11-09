from __future__ import annotations

from pathlib import Path

from ki.golden_eval import GoldenQuerySpec, eval_one, summarize
from ki.index_model import build_index


def test_golden_eval_recall_and_mrr(tmp_path: Path):
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    (tmp_path / "knowledge" / "technical" / "a.md").write_text(
        "---\ntitle: A\ndomain: technical\narea: x\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n## Auth\nOAuth ERR_OAUTH_999 flow.\n",
        encoding="utf-8",
    )
    (tmp_path / "knowledge" / "technical" / "b.md").write_text(
        "---\ntitle: B\ndomain: technical\narea: x\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n## Misc\nUnrelated notes.\n",
        encoding="utf-8",
    )
    idx = build_index(tmp_path)
    spec = GoldenQuerySpec(id="t1", query="ERR_OAUTH_999", expected_doc_contains="a.md")
    r = eval_one(idx, spec, at_k=3)
    assert r.passed
    assert r.first_hit_rank == 1
    assert r.mrr == 1.0

    bad = GoldenQuerySpec(id="t2", query="ERR_OAUTH_999", expected_doc_contains="missing")
    r2 = eval_one(idx, bad, at_k=3)
    assert not r2.passed
    assert r2.mrr == 0.0

    s = summarize([r, r2])
    assert s["recall_at_k_pass"] == 1
    assert s["mean_mrr_at_k"] == 0.5
