"""Git sync_status for /health (REQUIREMENTS §12.2) — best-effort, non-destructive."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyncSnap:
    sync_status: str
    local_head: str | None
    upstream_head: str | None


def _run(repo: Path, *args: str) -> tuple[int, str, str]:
    r = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def compute_sync_status(repo_root: Path) -> SyncSnap:
    """
    Does not modify the repo. Uses upstream tracking branch when configured.

    | sync_status | Meaning |
    |-------------|---------|
    | ok | Clean tree; HEAD equals @{upstream} (best effort after fetch is NOT run here) |
    | ok_behind | Clean; local is ancestor of upstream (fast-forward possible) |
    | blocked_diverged | Clean; non-FF relationship |
    | blocked_dirty_tree | Uncommitted changes |
    | not_configured | Not a git repo, no upstream, or detached |
    """
    root = repo_root.resolve()
    rc, _, _ = _run(root, "rev-parse", "--is-inside-work-tree")
    if rc != 0:
        return SyncSnap(sync_status="not_configured", local_head=None, upstream_head=None)

    rc, porcelain, _ = _run(root, "status", "--porcelain")
    if rc != 0:
        return SyncSnap(sync_status="not_configured", local_head=None, upstream_head=None)
    if porcelain.strip():
        return SyncSnap(sync_status="blocked_dirty_tree", local_head=_head(root), upstream_head=None)

    rc, head, _ = _run(root, "rev-parse", "HEAD")
    if rc != 0:
        return SyncSnap(sync_status="not_configured", local_head=None, upstream_head=None)

    rc, sym, _ = _run(root, "symbolic-ref", "-q", "HEAD")
    if rc != 0:
        return SyncSnap(sync_status="not_configured", local_head=head, upstream_head=None)

    rc, up_h, _ = _run(root, "rev-parse", "@{upstream}")
    if rc != 0:
        return SyncSnap(sync_status="not_configured", local_head=head, upstream_head=None)

    if head == up_h:
        return SyncSnap(sync_status="ok", local_head=head, upstream_head=up_h)

    rc, ahead_behind, _ = _run(root, "rev-list", "--left-right", "--count", f"{head}...{up_h}")
    if rc != 0:
        return SyncSnap(sync_status="not_configured", local_head=head, upstream_head=up_h)

    parts = ahead_behind.split("\t")
    if len(parts) != 2:
        return SyncSnap(sync_status="not_configured", local_head=head, upstream_head=up_h)
    # First: commits reachable from HEAD but not upstream (ahead). Second: behind.
    ahead = int(parts[0])
    behind = int(parts[1])
    if ahead == 0 and behind > 0:
        return SyncSnap(sync_status="ok_behind", local_head=head, upstream_head=up_h)
    if ahead > 0 and behind > 0:
        return SyncSnap(sync_status="blocked_diverged", local_head=head, upstream_head=up_h)
    if ahead > 0 and behind == 0:
        return SyncSnap(sync_status="ok", local_head=head, upstream_head=up_h)
    return SyncSnap(sync_status="ok", local_head=head, upstream_head=up_h)


def _head(root: Path) -> str | None:
    rc, o, _ = _run(root, "rev-parse", "HEAD")
    return o if rc == 0 else None
