from __future__ import annotations

from pathlib import Path

from ki.contribute import contribute_dry_run


def test_contribute_dry_run_suggests_extend_when_similar(tmp_path: Path):
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    (tmp_path / "knowledge" / "technical" / "auth.md").write_text(
        "---\ntitle: Auth\n"
        "domain: technical\narea: auth\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n"
        "## OAuth2\nWe use OAuth2 for the public API.\n",
        encoding="utf-8",
    )
    draft = (
        "---\ntitle: Auth note\ndomain: technical\narea: auth\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n"
        "## OAuth2\nWe use OAuth2 for the public API. Refresh tokens live in Redis.\n"
    )
    out = contribute_dry_run(tmp_path, draft, candidate_k=12, top_k=5)
    assert out.get("suggested_action") in ("edit", "extend", "new_doc")
    assert out.get("similar")
