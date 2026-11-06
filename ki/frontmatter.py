"""Validate and optionally fix YAML front matter for knowledge/**/*.md (REQUIREMENTS §6.1)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DOMAIN_SEGMENTS = frozenset({"technical", "delivery", "testing", "functional", "meta"})
VALID_AUTHOR_ROLES = frozenset({"dev", "qe", "pm", "dm", "mixed"})
VALID_STATUS = frozenset({"draft", "reviewed", "legacy_reviewed", "deprecated"})

FRONT_MATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.DOTALL)


@dataclass
class ValidationIssue:
    path: str
    message: str
    line_hint: int | None = None

    def format(self) -> str:
        loc = f" (line ~{self.line_hint})" if self.line_hint is not None else ""
        return f"{self.path}{loc}: {self.message}"


@dataclass
class ValidationResult:
    issues: list[ValidationIssue]
    domain_injected: bool = False


def _line_number_for_key(block: str, key: str) -> int | None:
    for i, line in enumerate(block.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith(f"{key}:") or stripped.startswith(f"{key} "):
            return i
    return None


def parse_front_matter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    """
    (parsed_dict | None, body_after_front_matter, raw_yaml_block | None).

    On YAML parse failure, returns (None, full_text, raw_block_if_matched).
    """
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None, text, None
    raw = m.group(1)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, text, raw
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return None, text, raw
    return data, text[m.end() :], raw


def infer_domain_from_path(relative: Path) -> str | None:
    parts = relative.as_posix().split("/")
    if len(parts) < 2 or parts[0] != "knowledge":
        return None
    seg = parts[1]
    return seg if seg in DOMAIN_SEGMENTS else None


def validate_markdown_file(
    path: Path,
    *,
    repo_root: Path,
    inject_domain: bool,
    fix_domain: bool = False,
) -> ValidationResult:
    rel = path.resolve().relative_to(repo_root.resolve())
    text = path.read_text(encoding="utf-8")
    data, _body, raw_block = parse_front_matter(text)
    issues: list[ValidationIssue] = []
    domain_injected = False

    if data is None and raw_block is None:
        issues.append(ValidationIssue(str(rel), "missing YAML front matter (expected --- block at start)"))
        return ValidationResult(issues)

    if data is None:
        issues.append(ValidationIssue(str(rel), "front matter YAML parse error"))
        return ValidationResult(issues)

    assert isinstance(data, dict)

    def add(msg: str, key: str | None = None) -> None:
        hint = _line_number_for_key(raw_block, key) if (key and raw_block) else None
        issues.append(ValidationIssue(str(rel), msg, hint))

    canonical = infer_domain_from_path(rel)

    # --- required: title
    title = data.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        add("missing or empty required key: title", "title")

    # --- domain
    domain_val = data.get("domain")
    if canonical is None:
        issues.append(
            ValidationIssue(
                str(rel),
                "path must be under knowledge/<technical|delivery|testing|functional|meta>/...",
            )
        )
    elif domain_val is None or (isinstance(domain_val, str) and not domain_val.strip()):
        if inject_domain or fix_domain:
            domain_injected = True
        else:
            add("missing required key: domain (use --inject-domain to set from path)", "domain")
    elif not isinstance(domain_val, str):
        add("domain must be a string", "domain")
    elif domain_val.strip() != canonical:
        if fix_domain:
            domain_injected = True
        else:
            add(f"domain must match path: expected '{canonical}', got {domain_val!r}", "domain")

    # --- area
    area = data.get("area")
    if not area or not isinstance(area, str) or not area.strip():
        add("missing or empty required key: area", "area")

    # --- author_role
    author_role = data.get("author_role")
    if not isinstance(author_role, str) or author_role not in VALID_AUTHOR_ROLES:
        add(f"author_role must be one of {sorted(VALID_AUTHOR_ROLES)}", "author_role")

    # --- type
    doc_type = data.get("type")
    if not doc_type or not isinstance(doc_type, str) or not doc_type.strip():
        add("missing or empty required key: type", "type")

    # --- status / last_reviewed
    status = data.get("status")
    if not isinstance(status, str) or status not in VALID_STATUS:
        add(f"status must be one of {sorted(VALID_STATUS)}", "status")
    elif status in ("reviewed", "legacy_reviewed"):
        lr = data.get("last_reviewed")
        if not lr or not isinstance(lr, str):
            add(
                "last_reviewed (YYYY-MM-DD) required when status is reviewed or legacy_reviewed",
                "last_reviewed",
            )
        elif not re.match(r"\A\d{4}-\d{2}-\d{2}\Z", lr.strip()):
            add("last_reviewed must be ISO date YYYY-MM-DD", "last_reviewed")
        if status == "legacy_reviewed":
            csince = data.get("canonical_since")
            if csince is not None and isinstance(csince, str) and csince.strip():
                if not re.match(r"\A\d{4}-\d{2}-\d{2}\Z", csince.strip()):
                    add("canonical_since must be ISO date YYYY-MM-DD when present", "canonical_since")

    elif status == "deprecated":
        sup_a = data.get("supersedes")
        sup_b = data.get("superseded_by")
        has_sup = (isinstance(sup_a, str) and sup_a.strip()) or (isinstance(sup_b, str) and sup_b.strip())
        if not has_sup:
            add(
                "status deprecated requires at least one of supersedes, superseded_by (conflict resolution only—see §4.4)",
                "supersedes",
            )

    # --- Optional scope / version (legacy-friendly knowledge)
    applies_to = data.get("applies_to")
    if applies_to is not None:
        if not isinstance(applies_to, list):
            add("applies_to must be a list of strings when present", "applies_to")
        else:
            for x in applies_to:
                if not isinstance(x, str) or not x.strip():
                    add("applies_to entries must be non-empty strings", "applies_to")
                    break

    doc_version = data.get("doc_version")
    if doc_version is not None and (not isinstance(doc_version, str) or not doc_version.strip()):
        add("doc_version must be a non-empty string when present", "doc_version")

    exclude = data.get("exclude_from_default_retrieval")
    if exclude is not None and not isinstance(exclude, bool):
        add("exclude_from_default_retrieval must be a boolean when present", "exclude_from_default_retrieval")

    # --- tags
    tags = data.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            add("tags must be a list when present", "tags")
        else:
            for t in tags:
                if not isinstance(t, str):
                    add("tags must be a list of strings", "tags")
                    break

    # --- related
    related = data.get("related")
    if related is not None:
        if not isinstance(related, list):
            add("related must be a list when present", "related")
        else:
            for r in related:
                if not isinstance(r, str):
                    add("related must contain string paths", "related")
                    break

    # --- supersedes / superseded_by
    for pair in ("supersedes", "superseded_by"):
        v = data.get(pair)
        if v is not None and not isinstance(v, str):
            add(f"{pair} must be a string when present", pair)

    return ValidationResult(issues=issues, domain_injected=domain_injected)


def rebuild_file_with_domain(path: Path, *, repo_root: Path) -> str:
    """Return full file text with domain set from path (for --inject-domain write)."""
    text = path.read_text(encoding="utf-8")
    data, _body, raw_block = parse_front_matter(text)
    if data is None or not isinstance(data, dict) or raw_block is None:
        raise ValueError("cannot inject domain: invalid or missing front matter")
    rel = path.resolve().relative_to(repo_root.resolve())
    canonical = infer_domain_from_path(rel)
    if not canonical:
        raise ValueError("cannot inject domain: path not under knowledge/<domain>/")
    data = dict(data)
    data["domain"] = canonical
    dumped = yaml.safe_dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    new_fm = f"---\n{dumped}---\n"
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise ValueError("missing --- front matter fence")
    return new_fm + text[m.end() :]
