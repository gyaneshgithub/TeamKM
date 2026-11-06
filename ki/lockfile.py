"""Single-flight index build lock (REQUIREMENTS §12.1)."""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

try:
    import fcntl

    _HAS_FCNTL = True
except ImportError:
    fcntl = None  # type: ignore[assignment]
    _HAS_FCNTL = False


@contextmanager
def index_build_lock(lock_path: Path) -> Generator[None, None, None]:
    """
    Exclusive lock for index builds. On platforms without fcntl, uses a best-effort
    PID file (still reduces races on macOS/Linux with fcntl).
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fp = open(lock_path, "a+", encoding="utf-8")
    try:
        if _HAS_FCNTL and fcntl is not None:
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
        else:
            # Windows: no flock; rely on atomic mkdir in future if needed
            pass
        fp.seek(0)
        fp.truncate()
        fp.write(f"{os.getpid()} {time.time()}\n")
        fp.flush()
        yield
    finally:
        if _HAS_FCNTL and fcntl is not None:
            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
