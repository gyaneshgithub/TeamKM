# TeamKM — MCP integration (stdio)

**Normative behaviour:** [REQUIREMENTS.md](REQUIREMENTS.md) §5.9, §5.12. **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md).

TeamKM’s **canonical** integration is the **local HTTP API** (`ki serve`). The **MCP server** is an optional **stdio adapter**: MCP tools call that same API over HTTP. The **IDE or agent host** runs the **LLM / planning loop**.

## Prerequisites

1. Python **3.10+** and repo installed with MCP extra:

   ```bash
   pip install -e ".[mcp]"
   ```

2. **API running** (default `http://127.0.0.1:8765`):

   ```bash
   python3 -m ki --root . serve
   ```

## MCP server command

Point your host’s MCP config at:

```bash
python3 -m ki mcp
```

(Run from the **repository root**, or ensure the working directory is the clone so relative paths resolve as expected.)

## Tools and prompt

| Name | Maps to |
|------|---------|
| `teamkm_health` | `GET /v1/health` |
| `teamkm_retrieve` | `POST /v1/retrieve` |
| `teamkm_context_pack` | `POST /v1/context_pack` |
| `teamkm_contribute_dry_run` | `POST /v1/contribute_dry_run` |
| Prompt `teamkm_retrieve_first` | Retrieve-before-edit policy text for the host |

## Configuration (base URL)

Override when the API is not on the default host/port:

| Variable | Effect |
|----------|--------|
| `TEAMKM_API_BASE` | Full base URL, e.g. `http://127.0.0.1:9000` (no trailing slash) |
| `KI_HOST` / `KI_PORT` | Used when `TEAMKM_API_BASE` is unset (`KI_HOST` default `127.0.0.1`, `KI_PORT` default `8765`) |

## Policy (retrieve-first)

Before changing code or adding `knowledge/**/*.md`, call **`teamkm_health`**, then **`teamkm_retrieve`** or **`teamkm_context_pack`**. Use **`teamkm_contribute_dry_run`** before proposing a brand-new doc (see §5.8).

## OpenAPI

Machine-readable contract: **`GET /openapi.yaml`** or **`GET /openapi.json`** while `ki serve` is running.
