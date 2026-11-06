"""CLI: `python -m ki` — index build, local API server."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ki.contribute import contribute_dry_run
from ki.index_runner import ensure_index
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
    print(f"TeamKM listening on http://{host}:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


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
    p = argparse.ArgumentParser(prog="ki", description="TeamKM local tooling")
    p.add_argument("--root", type=Path, help="Repository root (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("index", help="Build or refresh .rag/index")
    pi.set_defaults(func=cmd_index)

    ps = sub.add_parser("serve", help="Run local HTTP API on loopback")
    ps.add_argument("--host", default="127.0.0.1")
    ps.add_argument("--port", default=8765, type=int)
    ps.set_defaults(func=cmd_serve)

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
