"""Atomic, crash-safe writes: temp file in same directory + replace."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def atomic_write_bytes(path: Path, data: bytes, *, mode: int = 0o644) -> None:
    """
    Write `data` to `path` atomically (best-effort on POSIX).

    Uses a temp file in the same directory as `path`, then os.replace so readers
    never see a partial file. Same-directory is required for atomic rename on
    most filesystems.
    """
    path = path.resolve()
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd: int | None = None
    tmp_path: str | None = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=".tmp_ki_",
            suffix=path.suffix,
            dir=str(parent),
        )
        try:
            os.write(fd, data)
        finally:
            if fd is not None:
                os.close(fd)
                fd = None
        assert tmp_path is not None
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, path)
        tmp_path = None
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8", mode: int = 0o644) -> None:
    atomic_write_bytes(path, text.encode(encoding), mode=mode)
