#!/usr/bin/env python3
"""
After a merge to `main`, promote `status: draft` → `reviewed` for touched
`knowledge/**/*.md` files and set `last_reviewed` to UTC today.

Designed for GitHub Actions: commit with `[skip ci]` to avoid re-running CI.

Usage (from repo root):
  python3 scripts/promote_draft_on_merge.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ki.atomicio import atomic_write_text
from ki.frontmatter import FRONT_MATTER_RE, parse_front_matter
import yaml


_ZEROS = "0" * 40
# Git's fixed SHA-1 for the empty tree (used when `before` is all zeros — first push).
_EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def _git_diff_name_only(repo: Path, *args: str) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def _changed_knowledge_files(repo: Path) -> list[Path]:
    """
    Markdown under knowledge/ changed in this push.

    Merge commits (GitHub "Create a merge commit") have an empty `git diff-tree HEAD`
    list; use the push range when provided (Actions: before..after), or
    `HEAD^1..HEAD` so merges include all files touched vs first parent.
    """
    before = os.environ.get("PROMOTE_GIT_BEFORE", "").strip()
    after = os.environ.get("PROMOTE_GIT_AFTER", "").strip()

    names: list[str] = []
    if before and after:
        if before == _ZEROS:
            # New branch / initial push: everything introduced in `after`
            names = _git_diff_name_only(repo, _EMPTY_TREE, after)
        else:
            names = _git_diff_name_only(repo, before, after)
    if not names:
        # First parent vs merge/single-child result (correct for merge commits).
        chk = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "HEAD^1"],
            capture_output=True,
            text=True,
        )
        if chk.returncode == 0:
            p1 = chk.stdout.strip()
            names = _git_diff_name_only(repo, p1, "HEAD")
    if not names:
        out = subprocess.run(
            ["git", "-C", str(repo), "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        names = [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]

    paths: list[Path] = []
    seen: set[str] = set()
    for p in names:
        if not p.startswith("knowledge/") or not p.endswith(".md"):
            continue
        if p in seen:
            continue
        seen.add(p)
        paths.append(repo / p)
    return paths


def promote_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    data, body, _raw = parse_front_matter(text)
    if data is None or not isinstance(data, dict):
        return False
    if data.get("status") != "draft":
        return False
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return False

    data = dict(data)
    data["status"] = "reviewed"
    data["last_reviewed"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dumped = yaml.safe_dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    new_text = f"---\n{dumped}---\n" + text[m.end() :]
    if new_text == text:
        return False
    atomic_write_text(path, new_text)
    return True


def main() -> int:
    repo = Path(os.environ.get("GITHUB_WORKSPACE", _ROOT)).resolve()
    if not (repo / "knowledge").is_dir():
        print("promote_draft_on_merge: no knowledge/", file=sys.stderr)
        return 0

    changed = _changed_knowledge_files(repo)
    if not changed:
        print("promote_draft_on_merge: no knowledge/**/*.md in latest commit", file=sys.stderr)
        return 0

    n = 0
    for p in changed:
        if not p.is_file():
            continue
        try:
            if promote_file(p):
                print(f"promoted: {p.relative_to(repo)}")
                n += 1
        except OSError as e:
            print(f"error: {p}: {e}", file=sys.stderr)
            return 1

    if n == 0:
        print("promote_draft_on_merge: no draft files to promote")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
