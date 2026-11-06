"""TeamKM MCP server (stdio): exposes local HTTP API as MCP tools.

Run `ki serve` in another terminal (or rely on a host that starts it). This
process is intentionally thin: the **host** runs the LLM agent loop; TeamKM
remains retrieval + corpus ops (see docs/ARCHITECTURE.md).

Requires: pip install -e ".[mcp]"
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

INSTRUCTIONS = """TeamKM MCP — tools call the local TeamKM HTTP API on loopback.

**Retrieve-first policy (recommended):** Before changing code or writing new knowledge,
call `teamkm_health`, then `teamkm_retrieve` or `teamkm_context_pack` for the task topic.
Use `teamkm_contribute_dry_run` before adding a doc to avoid duplicates.

**Prerequisite:** start the API in the repo root, e.g. `python3 -m ki serve --root . --host 127.0.0.1 --port 8765`
(or set TEAMKM_API_BASE to match your URL).

OpenAPI: GET {base}/openapi.json
"""


def _api_base() -> str:
    base = (os.environ.get("TEAMKM_API_BASE") or os.environ.get("KI_API_BASE") or "").strip().rstrip("/")
    if base:
        return base
    host = os.environ.get("KI_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = (os.environ.get("KI_PORT") or "8765").strip() or "8765"
    return f"http://{host}:{port}"


def _post_json(path: str, payload: dict[str, Any], timeout: float = 120.0) -> dict[str, Any]:
    base = _api_base()
    url = f"{base}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"error": "http_error", "status": e.code, "body": raw[:2000]}
    return json.loads(raw)


def _get_json(path: str, timeout: float = 30.0) -> dict[str, Any]:
    base = _api_base()
    url = f"{base}{path}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"error": "http_error", "status": e.code, "body": raw[:2000]}
    return json.loads(raw)


def _tool_result(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP(
        name="teamkm",
        instructions=INSTRUCTIONS.format(base=_api_base()),
    )

    @mcp.tool()
    def teamkm_health() -> str:
        """Index/sync health from GET /v1/health (start `ki serve` first)."""
        return _tool_result(_get_json("/v1/health"))

    @mcp.tool()
    def teamkm_retrieve(
        query: str,
        candidate_k: int = 24,
        pack_k: int = 12,
        domain: str | None = None,
        area: str | None = None,
        include_archived: bool = False,
    ) -> str:
        """Hybrid retrieve + mandatory rerank (POST /v1/retrieve). Call before code/analysis work."""
        payload: dict[str, Any] = {
            "query": query,
            "candidate_k": candidate_k,
            "pack_k": pack_k,
            "include_archived": include_archived,
        }
        if domain is not None and domain.strip():
            payload["domain"] = domain.strip()
        if area is not None and area.strip():
            payload["area"] = area.strip()
        return _tool_result(_post_json("/v1/retrieve", payload))

    @mcp.tool()
    def teamkm_context_pack(
        query: str,
        candidate_k: int = 24,
        pack_k: int = 8,
        cap_per_doc: int = 2,
        domain: str | None = None,
        area: str | None = None,
        include_archived: bool = False,
    ) -> str:
        """Assembled context pack with inclusion_reason (POST /v1/context_pack)."""
        payload: dict[str, Any] = {
            "query": query,
            "candidate_k": candidate_k,
            "pack_k": pack_k,
            "cap_per_doc": cap_per_doc,
            "include_archived": include_archived,
        }
        if domain is not None and domain.strip():
            payload["domain"] = domain.strip()
        if area is not None and area.strip():
            payload["area"] = area.strip()
        return _tool_result(_post_json("/v1/context_pack", payload))

    @mcp.tool()
    def teamkm_contribute_dry_run(
        draft_markdown: str,
        candidate_k: int = 24,
        top_k: int = 8,
        domain: str | None = None,
        area: str | None = None,
    ) -> str:
        """Retrieval-first duplicate check before adding knowledge (POST /v1/contribute_dry_run)."""
        payload: dict[str, Any] = {
            "draft_markdown": draft_markdown,
            "candidate_k": candidate_k,
            "top_k": top_k,
        }
        if domain is not None and domain.strip():
            payload["domain"] = domain.strip()
        if area is not None and area.strip():
            payload["area"] = area.strip()
        return _tool_result(_post_json("/v1/contribute_dry_run", payload))

    @mcp.prompt(
        name="teamkm_retrieve_first",
        description="Instruct the assistant to call TeamKM tools before changing code or writing docs.",
    )
    def teamkm_retrieve_first(task_description: str) -> str:
        return f"""You are helping with this task:

{task_description}

**TeamKM policy:** Before editing code or authoring new markdown under `knowledge/`, call `teamkm_health`
then `teamkm_retrieve` or `teamkm_context_pack` with a query summarizing the task. Cite retrieved
`doc_path` and line ranges when you use them. If the user wants a new knowledge doc, run
`teamkm_contribute_dry_run` on a draft outline first."""

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
