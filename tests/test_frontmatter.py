from __future__ import annotations

from pathlib import Path

from ki.frontmatter import (
    infer_domain_from_path,
    rebuild_file_with_domain,
    validate_markdown_file,
)


def _write(root: Path, rel: str, content: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_infer_domain_from_path():
    assert infer_domain_from_path(Path("knowledge/technical/foo.md")) == "technical"
    assert infer_domain_from_path(Path("knowledge/wrong/x.md")) is None


def test_validate_ok_with_domain(tmp_path: Path):
    root = tmp_path
    md = _write(
        root,
        "knowledge/delivery/sample.md",
        """---
title: Hello
domain: delivery
area: billing
author_role: dev
type: delivery-summary
status: draft
---

Body.
""",
    )
    r = validate_markdown_file(md, repo_root=root, inject_domain=False)
    assert r.issues == []


def test_validate_missing_domain_strict(tmp_path: Path):
    root = tmp_path
    md = _write(
        root,
        "knowledge/testing/x.md",
        """---
title: T
area: auth
author_role: qe
type: test-plan
status: draft
---

x
""",
    )
    r = validate_markdown_file(md, repo_root=root, inject_domain=False)
    assert any("domain" in i.message.lower() for i in r.issues)


def test_validate_inject_domain_passes(tmp_path: Path):
    root = tmp_path
    md = _write(
        root,
        "knowledge/functional/x.md",
        """---
title: F
area: reports
author_role: pm
type: feature
status: draft
---

x
""",
    )
    r = validate_markdown_file(md, repo_root=root, inject_domain=True)
    assert r.issues == []
    assert r.domain_injected is True


def test_wrong_domain_fails(tmp_path: Path):
    root = tmp_path
    md = _write(
        root,
        "knowledge/technical/a.md",
        """---
title: A
domain: functional
area: x
author_role: dev
type: adr
status: draft
---

z
""",
    )
    r = validate_markdown_file(md, repo_root=root, inject_domain=False)
    assert any("must match path" in i.message for i in r.issues)


def test_wrong_domain_with_fix_flag(tmp_path: Path):
    root = tmp_path
    md = _write(
        root,
        "knowledge/technical/a.md",
        """---
title: A
domain: functional
area: x
author_role: dev
type: adr
status: draft
---

z
""",
    )
    r = validate_markdown_file(md, repo_root=root, inject_domain=True, fix_domain=True)
    assert r.issues == []
    assert r.domain_injected is True


def test_rebuild_file_with_domain(tmp_path: Path):
    root = tmp_path
    md = _write(
        root,
        "knowledge/meta/n.md",
        """---
title: N
area: core
author_role: dev
type: adr
status: draft
---

Hi
""",
    )
    out = rebuild_file_with_domain(md, repo_root=root)
    assert "domain: meta\n" in out


def test_reviewed_requires_last_reviewed(tmp_path: Path):
    root = tmp_path
    md = _write(
        root,
        "knowledge/delivery/a.md",
        """---
title: A
domain: delivery
area: x
author_role: dev
type: delivery-summary
status: reviewed
---

x
""",
    )
    r = validate_markdown_file(md, repo_root=root, inject_domain=False)
    assert any("last_reviewed" in i.message for i in r.issues)
