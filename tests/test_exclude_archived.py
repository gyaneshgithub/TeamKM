from __future__ import annotations

from pathlib import Path

from ki.index_model import build_index
from ki.retrieve import retrieve_candidates


def test_exclude_from_default_retrieval(tmp_path: Path):
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    (tmp_path / "knowledge" / "technical" / "hidden.md").write_text(
        "---\ntitle: H\ndomain: technical\narea: x\nauthor_role: dev\n"
        "type: adr\nstatus: draft\nexclude_from_default_retrieval: true\n---\n\n## Sec\nZZ_ARCHIVE_MARKER_99\n",
        encoding="utf-8",
    )
    (tmp_path / "knowledge" / "technical" / "visible.md").write_text(
        "---\ntitle: V\ndomain: technical\narea: x\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n## Sec\npublic notes\n",
        encoding="utf-8",
    )
    idx = build_index(tmp_path)
    q = "ZZ_ARCHIVE_MARKER_99"
    default = retrieve_candidates(idx, q, top_n=10)
    paths_def = {c[0].doc_path for c in default}
    assert not any("hidden.md" in p for p in paths_def)
    inc = retrieve_candidates(idx, q, top_n=10, include_archived=True)
    paths_inc = {c[0].doc_path for c in inc}
    assert any("hidden.md" in p for p in paths_inc)
