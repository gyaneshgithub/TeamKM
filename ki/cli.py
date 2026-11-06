"""CLI: `python -m ki` — index build, local API server."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

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
    print(f"knowledgeIntelligence listening on http://{host}:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ki", description="knowledgeIntelligence local tooling")
    p.add_argument("--root", type=Path, help="Repository root (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("index", help="Build or refresh .rag/index")
    pi.set_defaults(func=cmd_index)

    ps = sub.add_parser("serve", help="Run local HTTP API on loopback")
    ps.add_argument("--host", default="127.0.0.1")
    ps.add_argument("--port", default=8765, type=int)
    ps.set_defaults(func=cmd_serve)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
