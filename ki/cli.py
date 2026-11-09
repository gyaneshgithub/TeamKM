"""CLI: `python -m ki` — index build, local API server."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ki.contribute import contribute_dry_run
from ki.golden_eval import load_golden_file, run_eval, summarize
from ki.index_runner import ensure_index, load_index_optional
from ki.index_status import index_freshness
from ki.api import run_server


def _repo_root(args: argparse.Namespace) -> Path:
    if args.root:
        return Path(args.root).resolve()
    return Path.cwd().resolve()


def cmd_index(args: argparse.Namespace) -> int:
    root = _repo_root(args)
    try:
        ensure_index(root)
        print("index:", "ready", file=sys.stderr)
    except Exception as e:
        print("index build failed:", e, file=sys.stderr)
        return 1
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    root = _repo_root(args)
    host = os.environ.get("KI_HOST", args.host)
    port = int(os.environ.get("KI_PORT", args.port))
    try:
        ensure_index(root)
    except Exception as e:
        print("warning: index build failed (server still starts):", e, file=sys.stderr)
    server = run_server(root, host=host, port=port)
    print(f"Groundline listening on http://{host}:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    try:
        from ki.mcp_server import main as mcp_main
    except ImportError as e:
        print("Install MCP support: pip install -e '.[mcp]'", file=sys.stderr)
        print(e, file=sys.stderr)
        return 1
    mcp_main()
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = _repo_root(args)
    fresh = index_freshness(root)
    sync = __import__("ki.sync_status", fromlist=["compute_sync_status"]).compute_sync_status(root)
    out = {**fresh, "sync_status": sync.sync_status}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        stale = "STALE — run: python3 -m ki --root . index" if fresh["index_stale"] else "fresh"
        print(f"index_status: {fresh['index_status']} ({stale})")
        print(f"corpus_fingerprint_current:  {fresh['corpus_fingerprint_current']}")
        idx_fp = fresh.get("corpus_fingerprint_indexed") or "(none)"
        print(f"corpus_fingerprint_indexed:  {idx_fp}")
        print(f"chunk_count: {fresh.get('chunk_count')}")
        print(f"sync_status: {sync.sync_status}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    import yaml
    from pathlib import Path as P

    root = _repo_root(args)
    gfile = P(args.file) if args.file else root / "meta" / "golden_queries.yaml"
    if not gfile.is_file():
        print("eval: golden_queries file not found:", gfile, file=sys.stderr)
        return 2
    data = yaml.safe_load(gfile.read_text(encoding="utf-8"))
    at_k, specs = load_golden_file(data)
    if not args.no_index:
        ensure_index(root)
    idx = load_index_optional(root)
    if idx is None:
        print("eval: index unavailable", file=sys.stderr)
        return 1
    results = run_eval(idx, specs, at_k=at_k)
    summary = summarize(results)
    if args.report == "json":
        print(
            json.dumps(
                {"recall_at_k": at_k, "summary": summary, "failed": summary["recall_at_k_fail"]},
                indent=2,
            )
        )
    elif args.report == "md":
        from ki.golden_eval import emit_markdown_report

        emit_markdown_report(results, summary, at_k=at_k)
    else:
        from ki.golden_eval import emit_text_report

        emit_text_report(results, summary, at_k=at_k)
    return 1 if summary["recall_at_k_fail"] else 0


def cmd_contribute(args: argparse.Namespace) -> int:
    root = _repo_root(args)
    draft = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    payload = contribute_dry_run(
        root,
        draft,
        candidate_k=args.candidate_k,
        top_k=args.top_k,
        domain=args.domain,
        area=args.area,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    err = payload.get("error")
    return 0 if err is None else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ki", description="Groundline local tooling")
    p.add_argument("--root", type=Path, help="Repository root (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("index", help="Build or refresh .rag/index")
    pi.set_defaults(func=cmd_index)

    pst = sub.add_parser("status", help="Index freshness vs corpus (no server)")
    pst.add_argument("--json", action="store_true", help="Print JSON")
    pst.set_defaults(func=cmd_status)

    pe = sub.add_parser("eval", help="Golden-query retrieval regression report")
    pe.add_argument("--file", type=Path, default=None, help="meta/golden_queries.yaml")
    pe.add_argument("--report", choices=("text", "md", "json"), default="text")
    pe.add_argument("--no-index", action="store_true", help="Skip index rebuild")
    pe.set_defaults(func=cmd_eval)

    ps = sub.add_parser("serve", help="Run local HTTP API on loopback")
    ps.add_argument("--host", default="127.0.0.1")
    ps.add_argument("--port", default=8765, type=int)
    ps.set_defaults(func=cmd_serve)

    pm = sub.add_parser(
        "mcp",
        help="Run stdio MCP server (tools wrap local HTTP API; install .[mcp])",
    )
    pm.set_defaults(func=cmd_mcp)

    pc = sub.add_parser("contribute", help="Retrieval-first contribute dry-run (§5.8)")
    pc.add_argument("--file", "-f", type=Path, help="Draft markdown file (else stdin)")
    pc.add_argument("--candidate-k", type=int, default=24)
    pc.add_argument("--top-k", type=int, default=8)
    pc.add_argument("--domain", type=str, default=None)
    pc.add_argument("--area", type=str, default=None)
    pc.set_defaults(func=cmd_contribute)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
