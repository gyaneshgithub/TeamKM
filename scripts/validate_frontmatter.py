#!/usr/bin/env python3
"""
Validate YAML front matter for knowledge/**/*.md per docs/REQUIREMENTS.md §6.1.

Usage:
  python3 scripts/validate_frontmatter.py [--inject-domain] [--fix] [paths...]

Default paths: knowledge/**/*.md under repo root (cwd or --root).

Exit codes:
  0 — all files valid (after --fix writes if requested)
  1 — validation errors
  2 — usage / IO error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running without pip install -e .
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ki.atomicio import atomic_write_text
from ki.frontmatter import rebuild_file_with_domain, validate_markdown_file


def discover_files(root: Path, explicit: list[Path] | None) -> list[Path]:
    if explicit:
        out: list[Path] = []
        for p in explicit:
            pr = (root / p).resolve() if not p.is_absolute() else p.resolve()
            if pr.is_dir():
                out.extend(sorted(pr.rglob("*.md")))
            elif pr.suffix == ".md":
                out.append(pr)
        return sorted(set(out))
    knowledge = root / "knowledge"
    if not knowledge.is_dir():
        return []
    return sorted(knowledge.rglob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate knowledge front matter (§6.1).")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Specific files or dirs (relative to root); default: all knowledge/**/*.md",
    )
    parser.add_argument(
        "--inject-domain",
        action="store_true",
        help="Treat missing domain as valid (canonical value from path); required for strict check without --fix",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Write domain into front matter from path (atomic rename); implies --inject-domain for checks",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    inject = args.inject_domain or args.fix

    files = discover_files(root, args.paths or None)
    if not files:
        print("validate_frontmatter: no markdown files found under knowledge/", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in files:
        try:
            path = path.resolve()
            rel = path.relative_to(root)
        except ValueError:
            errors.append(f"{path}: not under --root {root}")
            continue

        if args.fix:
            res = validate_markdown_file(path, repo_root=root, inject_domain=True, fix_domain=True)
            if res.issues:
                for i in res.issues:
                    errors.append(i.format())
                continue
            try:
                new_text = rebuild_file_with_domain(path, repo_root=root)
            except ValueError as e:
                errors.append(f"{rel}: {e}")
                continue
            old = path.read_text(encoding="utf-8")
            if new_text != old:
                atomic_write_text(path, new_text)
                print(f"fixed (domain): {rel}")
            else:
                print(f"unchanged: {rel}")
        else:
            res = validate_markdown_file(path, repo_root=root, inject_domain=inject, fix_domain=False)
            for i in res.issues:
                errors.append(i.format())
            if inject and res.domain_injected and not res.issues:
                print(f"ok (would inject domain): {rel}")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"OK: {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
