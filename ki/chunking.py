"""Structure-aware Markdown chunking (MVP — REQUIREMENTS §5.4)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ki.frontmatter import FRONT_MATTER_RE, parse_front_matter
from ki.tokenize import term_freq


@dataclass
class Chunk:
    chunk_id: str
    doc_path: str
    heading_path: str
    text: str
    line_start: int
    line_end: int
    meta: dict[str, Any]


def _stable_chunk_id(doc_rel: str, heading_path: str, chunk_index: int) -> str:
    raw = f"{doc_rel}\n{heading_path}\n{chunk_index}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _split_file_lines(text: str) -> tuple[list[str], int]:
    """(all_lines, body_start_line_index_0based_into_all_lines)."""
    m = FRONT_MATTER_RE.match(text)
    lines = text.splitlines()
    if not m or not lines or lines[0].strip() != "---":
        return lines, 0
    for i in range(1, min(len(lines), 500)):
        if lines[i].strip() == "---":
            return lines, i + 1
    return lines, 0


_H2 = re.compile(r"^##\s+(.+?)\s*$")
_H3 = re.compile(r"^###\s+(.+?)\s*$")


def chunk_markdown_file(path: Path, *, repo_root: Path) -> list[Chunk]:
    rel = path.relative_to(repo_root.resolve()).as_posix()
    raw = path.read_text(encoding="utf-8")
    fm_data, _, _ = parse_front_matter(raw)
    meta_base: dict[str, Any] = dict(fm_data or {})

    all_lines, body_start = _split_file_lines(raw)
    body_lines = all_lines[body_start:] if body_start < len(all_lines) else []

    if not body_lines:
        start = 1
        end = max(1, len(all_lines))
        return [
            Chunk(
                chunk_id=_stable_chunk_id(rel, "(document)", 0),
                doc_path=rel,
                heading_path="(document)",
                text="",
                line_start=start,
                line_end=end,
                meta=_chunk_meta(meta_base, ""),
            )
        ]

    # Section starts: any line that is ## or ### (not # or ####+)
    sections: list[tuple[str, list[str], int, int]] = []
    current_heading = "(preamble)"
    buf: list[str] = []
    sec_start_file = body_start + 1

    def flush() -> None:
        nonlocal buf, sec_start_file, current_heading
        if not buf:
            return
        text = "\n".join(buf).strip()
        if not text:
            buf = []
            return
        end_line = sec_start_file + len(buf) - 1
        sections.append((current_heading, list(buf), sec_start_file, end_line))
        buf = []

    for i, line in enumerate(body_lines):
        file_line = body_start + 1 + i
        if _H2.match(line) or _H3.match(line):
            flush()
            m2 = _H2.match(line)
            m3 = _H3.match(line)
            current_heading = (m2 or m3).group(1).strip()  # type: ignore[union-attr]
            buf = [line]
            sec_start_file = file_line
        else:
            if not buf:
                sec_start_file = file_line
                current_heading = "(preamble)" if i == 0 else current_heading
                buf = [line]
            else:
                buf.append(line)

    flush()

    if not sections:
        text = "\n".join(body_lines).strip()
        return [
            Chunk(
                chunk_id=_stable_chunk_id(rel, "(document)", 0),
                doc_path=rel,
                heading_path="(document)",
                text=text,
                line_start=body_start + 1,
                line_end=body_start + len(body_lines),
                meta=_chunk_meta(meta_base, text),
            )
        ]

    chunks: list[Chunk] = []
    for idx, (heading, lines, ls, le) in enumerate(sections):
        text = "\n".join(lines).strip()
        chunks.append(
            Chunk(
                chunk_id=_stable_chunk_id(rel, heading, idx),
                doc_path=rel,
                heading_path=heading,
                text=text,
                line_start=ls,
                line_end=le,
                meta=_chunk_meta(meta_base, text),
            )
        )
    return chunks


def _chunk_meta(meta_base: dict[str, Any], text: str) -> dict[str, Any]:
    title = str(meta_base.get("title", ""))
    return {
        "domain": meta_base.get("domain"),
        "area": meta_base.get("area"),
        "type": meta_base.get("type"),
        "title": meta_base.get("title"),
        "status": meta_base.get("status"),
        "related": meta_base.get("related"),
        "applies_to": meta_base.get("applies_to"),
        "doc_version": meta_base.get("doc_version"),
        "canonical_since": meta_base.get("canonical_since"),
        "supersedes": meta_base.get("supersedes"),
        "superseded_by": meta_base.get("superseded_by"),
        "exclude_from_default_retrieval": meta_base.get("exclude_from_default_retrieval"),
        "_tf": dict(term_freq(text + " " + title)),
    }
