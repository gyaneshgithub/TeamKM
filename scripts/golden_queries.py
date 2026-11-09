#!/usr/bin/env python3
"""Run golden-query recall@k + MRR checks (REQUIREMENTS §5.5, §11)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ki.golden_eval import (
    emit_markdown_report,
    emit_text_report,
    load_golden_file,
    run_eval,
    summarize,
)
from ki.index_runner import ensure_index, load_index_optional


def main() -> int:
    p = argparse.ArgumentParser(description="Golden-query retrieval regression")
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--file", type=Path, default=None, help="Default meta/golden_queries.yaml")
    p.add_argument(
        "--report",
        choices=("text", "md", "json", "quiet"),
        default="text",
        help="Output format (default: text). quiet = CI-style PASS/FAIL only",
    )
    p.add_argument(
        "--no-index",
        action="store_true",
        help="Do not rebuild index before eval (use existing .rag)",
    )
    args = p.parse_args()
    root = args.root.resolve()
    gfile = args.file or (root / "meta" / "golden_queries.yaml")
    if not gfile.is_file():
        print("golden_queries: file not found:", gfile, file=sys.stderr)
        return 2

    data = yaml.safe_load(gfile.read_text(encoding="utf-8"))
    at_k, specs = load_golden_file(data)
    if not specs:
        print("golden_queries: no queries in file", file=sys.stderr)
        return 2

    if not args.no_index:
        ensure_index(root)

    idx = load_index_optional(root)
    if idx is None:
        print("golden_queries: index unavailable", file=sys.stderr)
        return 1

    results = run_eval(idx, specs, at_k=at_k)
    summary = summarize(results)
    failed = summary["recall_at_k_fail"]

    if args.report == "json":
        payload = {
            "recall_at_k": at_k,
            "summary": summary,
            "results": [
                {
                    "id": r.spec.id,
                    "query": r.spec.query,
                    "expected_doc_contains": r.spec.expected_doc_contains,
                    "pass": r.passed,
                    "first_hit_rank": r.first_hit_rank,
                    "mrr": r.mrr,
                    "paths_at_k": r.paths_at_k,
                }
                for r in results
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.report == "md":
        emit_markdown_report(results, summary, at_k=at_k)
    elif args.report == "text":
        emit_text_report(results, summary, at_k=at_k)
    else:
        for r in results:
            if r.passed:
                print(f"PASS {r.spec.id}")
            else:
                print(
                    f"FAIL {r.spec.id} expected doc containing {r.spec.expected_doc_contains!r}, "
                    f"got {r.paths_at_k}",
                    file=sys.stderr,
                )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
