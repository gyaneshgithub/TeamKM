from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from ki.api import run_server

_REPO_ROOT = Path(__file__).resolve().parents[1]


def test_health_endpoint(tmp_path: Path):
    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "openapi.yaml").write_text(
        (_REPO_ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tmp_path / "knowledge" / "technical").mkdir(parents=True)
    (tmp_path / "knowledge" / "technical" / "z.md").write_text(
        "---\ntitle: Z\ndomain: technical\narea: z\nauthor_role: dev\n"
        "type: adr\nstatus: draft\n---\n\n## A\nhello world\n",
        encoding="utf-8",
    )
    srv = run_server(tmp_path, host="127.0.0.1", port=0)
    port = srv.server_address[1]
    try:
        srv_thread = __import__("threading").Thread(target=srv.serve_forever, daemon=True)
        srv_thread.start()

        req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/health")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
        assert body.get("index_status") in {"ready", "building", "missing", "stale"}
        assert "corpus_fingerprint" in body
        assert "index_stale" in body
        assert "corpus_fingerprint_current" in body

        req_o = urllib.request.Request(f"http://127.0.0.1:{port}/openapi.json")
        with urllib.request.urlopen(req_o, timeout=10) as resp:
            spec = json.loads(resp.read().decode())
        assert spec.get("openapi") == "3.1.0"
        assert "/v1/health" in (spec.get("paths") or {})
    finally:
        srv.shutdown()
        srv.server_close()
