#!/usr/bin/env python3
"""Run golden-query recall@k checks (REQUIREMENTS §5.5, §11)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ki.index_runner import ensure_index
from ki.retrieve import retrieve_candidates, rerank


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--file", type=Path, default=None, help="Default meta/golden_queries.yaml")
    args = p.parse_args()
    root = args.root.resolve()
    gfile = args.file or (root / "meta" / "golden_queries.yaml")
    if not gfile.is_file():
        print("golden_queries: file not found:", gfile, file=sys.stderr)
        return 2

    data = yaml.safe_load(gfile.read_text(encoding="utf-8"))
    at_k = int(data.get("recall_at_k", 5))
    queries = data.get("queries") or []

    ensure_index(root)
    from ki.index_runner import load_index_optional

    idx = load_index_optional(root)
    if idx is None:
        print("golden_queries: index unavailable", file=sys.stderr)
        return 1

    failed = 0
    for q in queries:
        qid = q.get("id", "?")
        query = q.get("query", "")
        needle = q.get("expected_doc_contains", "")
        cands = retrieve_candidates(idx, query, top_n=at_k * 2)
        ranked = rerank(query, cands, take=at_k)
        paths = [s.doc_path for s in ranked]
        ok = any(needle in p for p in paths)
        if ok:
            print(f"PASS {qid}")
        else:
            print(f"FAIL {qid} expected doc containing {needle!r}, got {paths}", file=sys.stderr)
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
