from __future__ import annotations

from pathlib import Path

from ki.index_runner import ensure_index
from ki.index_status import index_freshness


def test_index_stale_after_corpus_change(tmp_path: Path):
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    doc = tmp_path / "knowledge" / "technical" / "a.md"
    doc.write_text(
        "---\ntitle: A\ndomain: technical\narea: x\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n## One\nversion one\n",
        encoding="utf-8",
    )
    ensure_index(tmp_path)
    fresh = index_freshness(tmp_path)
    assert fresh["index_stale"] is False
    assert fresh["index_status"] == "ready"

    doc.write_text(
        doc.read_text(encoding="utf-8") + "\n\n## Two\nversion two\n",
        encoding="utf-8",
    )
    fresh2 = index_freshness(tmp_path)
    assert fresh2["index_stale"] is True
    assert fresh2["index_status"] == "stale"
    assert fresh2["corpus_fingerprint_current"] != fresh2["corpus_fingerprint_indexed"]
