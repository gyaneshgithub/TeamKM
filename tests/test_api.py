from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from ki.api import run_server


def test_health_endpoint(tmp_path: Path):
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
        assert body.get("index_status") in {"ready", "building", "missing"}
        assert "corpus_fingerprint" in body
    finally:
        srv.shutdown()
        srv.server_close()
