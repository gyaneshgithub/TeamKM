from __future__ import annotations

from pathlib import Path

from ki.atomicio import atomic_write_text


def test_atomic_write_replaces(tmp_path: Path):
    p = tmp_path / "a" / "b.txt"
    atomic_write_text(p, "one")
    assert p.read_text() == "one"
    atomic_write_text(p, "two")
    assert p.read_text() == "two"
