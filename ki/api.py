"""Minimal local HTTP API (REQUIREMENTS §5.6, §5.9) — stdlib only."""

from __future__ import annotations

import json
import os
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ki.index_model import EMBEDDING_MODEL_ID, INDEX_SCHEMA_VERSION, SPARSE_MODEL_ID
from ki.index_runner import ensure_index, index_dir, load_index_optional, rag_root
from ki.manifest import read_manifest as read_manifest_raw
from ki.manifest import write_manifest
from ki.contribute import contribute_dry_run
from ki.retrieve import build_context_pack, retrieve_candidates, rerank
from ki.index_status import index_freshness
from ki.sync_status import compute_sync_status


def _json_response(handler: BaseHTTPRequestHandler, code: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class KiHandler(BaseHTTPRequestHandler):
    repo_root: Path

    def log_message(self, fmt: str, *args: Any) -> None:
        return  # quiet default

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/v1/health":
            self._health()
            return
        if parsed.path == "/":
            _json_response(
                self,
                200,
                {
                    "service": "Groundline",
                    "health": "/v1/health",
                    "openapi_yaml": "/openapi.yaml",
                    "openapi_json": "/openapi.json",
                },
            )
            return
        if parsed.path == "/openapi.yaml":
            self._openapi_yaml(root=self.repo_root.resolve())
            return
        if parsed.path == "/openapi.json":
            self._openapi_json(root=self.repo_root.resolve())
            return
        _json_response(self, 404, {"error": "not_found", "path": parsed.path})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            _json_response(self, 400, {"error": "invalid_json"})
            return

        if parsed.path == "/v1/retrieve":
            self._retrieve(body)
            return
        if parsed.path == "/v1/context_pack":
            self._context_pack(body)
            return
        if parsed.path == "/v1/contribute_dry_run":
            self._contribute_dry_run(body)
            return
        _json_response(self, 404, {"error": "not_found", "path": parsed.path})

    def _health(self) -> None:
        root = self.repo_root.resolve()
        rr = rag_root(root)
        sync = compute_sync_status(root)
        was_stale = index_freshness(root)["index_stale"]
        try:
            ensure_index(root)
        except Exception:
            pass
        m = read_manifest_raw(rr) or {}
        fresh = index_freshness(root)
        payload = {
            "index_status": fresh["index_status"],
            "index_stale": was_stale,
            "index_stale_now": fresh["index_stale"],
            "sync_status": sync.sync_status,
            "corpus_fingerprint": fresh["corpus_fingerprint_indexed"] or m.get("corpus_fingerprint", ""),
            "corpus_fingerprint_current": fresh["corpus_fingerprint_current"],
            "corpus_fingerprint_indexed": fresh["corpus_fingerprint_indexed"],
            "local_head": sync.local_head,
            "upstream_head": sync.upstream_head,
            "embedding_model_id": m.get("embedding_model_id", EMBEDDING_MODEL_ID),
            "sparse_model_id": m.get("sparse_model_id", SPARSE_MODEL_ID),
            "reranker_model_id": m.get("reranker_model_id", "mvp-pairwise-tf-idf"),
            "schema_version": m.get("schema_version", INDEX_SCHEMA_VERSION),
            "chunk_count": fresh.get("chunk_count") or m.get("chunk_count"),
            "retrieval": m.get("retrieval", "hybrid_rrf_dense_bm25"),
            "manifest": {
                "built_at": m.get("built_at"),
                "index_dir": str(index_dir(root)),
            },
        }
        if "error" in m:
            payload["error"] = m["error"]
        _json_response(self, 200, payload)

    def _retrieve(self, body: dict[str, Any]) -> None:
        root = self.repo_root.resolve()
        q = str(body.get("query", "")).strip()
        if not q:
            _json_response(self, 400, {"error": "query_required"})
            return
        ensure_index(root)
        idx = load_index_optional(root)
        if idx is None:
            _json_response(self, 503, {"error": "index_unavailable"})
            return
        top_n = int(body.get("candidate_k", 24))
        pack_k = int(body.get("pack_k", 12))
        domain = body.get("domain")
        area = body.get("area")
        include_archived = bool(body.get("include_archived", False))
        cands = retrieve_candidates(
            idx,
            q,
            top_n=top_n,
            domain=domain,
            area=area,
            include_archived=include_archived,
        )
        ranked = rerank(q, cands, take=pack_k)
        out = [
            {
                "chunk_id": s.chunk_id,
                "doc_path": s.doc_path,
                "heading_path": s.heading_path,
                "text": s.text,
                "line_start": s.line_start,
                "line_end": s.line_end,
                "retrieval_score": s.retrieval_score,
                "rerank_score": s.rerank_score,
                "dense_score": s.dense_score,
                "sparse_score": s.sparse_score,
                "meta": s.meta,
            }
            for s in ranked
        ]
        _json_response(
            self,
            200,
            {
                "query": q,
                "chunks": out,
                "embedding_model_id": EMBEDDING_MODEL_ID,
                "sparse_model_id": SPARSE_MODEL_ID,
                "retrieval": "hybrid_rrf_dense_bm25",
            },
        )

    def _context_pack(self, body: dict[str, Any]) -> None:
        root = self.repo_root.resolve()
        q = str(body.get("query", "")).strip()
        if not q:
            _json_response(self, 400, {"error": "query_required"})
            return
        ensure_index(root)
        idx = load_index_optional(root)
        if idx is None:
            _json_response(self, 503, {"error": "index_unavailable"})
            return
        pack = build_context_pack(
            idx,
            q,
            candidate_k=int(body.get("candidate_k", 24)),
            pack_k=int(body.get("pack_k", 8)),
            cap_per_doc=int(body.get("cap_per_doc", 2)),
            domain=body.get("domain"),
            area=body.get("area"),
            include_archived=bool(body.get("include_archived", False)),
        )
        _json_response(
            self,
            200,
            {
                "query": q,
                "chunks": pack,
                "embedding_model_id": EMBEDDING_MODEL_ID,
                "sparse_model_id": SPARSE_MODEL_ID,
            },
        )

    def _contribute_dry_run(self, body: dict[str, Any]) -> None:
        root = self.repo_root.resolve()
        draft = str(body.get("draft_markdown", "") or body.get("text", "") or "")
        if not draft.strip():
            _json_response(self, 400, {"error": "draft_markdown_required"})
            return
        try:
            ensure_index(root)
        except Exception:
            pass
        payload = contribute_dry_run(
            root,
            draft,
            candidate_k=int(body.get("candidate_k", 24)),
            top_k=int(body.get("top_k", 8)),
            domain=body.get("domain"),
            area=body.get("area"),
        )
        _json_response(self, 200, payload)

    def _openapi_yaml(self, *, root: Path) -> None:
        spec_path = root / "docs" / "openapi.yaml"
        if spec_path.is_file():
            text = spec_path.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/yaml; charset=utf-8")
            b = text.encode("utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        _json_response(self, 404, {"error": "openapi_not_found"})

    def _openapi_json(self, *, root: Path) -> None:
        spec_path = root / "docs" / "openapi.yaml"
        if not spec_path.is_file():
            _json_response(self, 404, {"error": "openapi_not_found"})
            return
        try:
            import yaml
        except ImportError:
            _json_response(self, 500, {"error": "yaml_required_for_openapi_json"})
            return
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_handler_class(repo_root: Path) -> type[KiHandler]:
    resolved = repo_root.resolve()

    class H(KiHandler):
        repo_root = resolved

    return H


def run_server(repo_root: Path, *, host: str, port: int) -> ThreadingHTTPServer:
    H = make_handler_class(repo_root)
    server = ThreadingHTTPServer((host, port), H)
    return server


def serve_forever_background(repo_root: Path, *, host: str, port: int) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = run_server(repo_root, host=host, port=port)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t
