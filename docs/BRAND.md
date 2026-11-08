# Brand and technical identifiers

**Product name:** **Groundline**  
**Tagline:** *Grounded context infrastructure for engineering teams.*

---

## What changed

| Layer | Name | Notes |
|-------|------|--------|
| **Product / docs / UI strings** | **Groundline** | README, MkDocs, leadership brief, HTTP `service` field, CLI banner |
| **GitHub template repo** | [`gyaneshgithub/TeamKM`](https://github.com/gyaneshgithub/TeamKM) | Repository slug unchanged; rename on GitHub when you want URL to match brand |
| **GitHub Pages URL** | `https://gyaneshgithub.github.io/TeamKM/` | Path follows **repo name**, not product name, until the repo is renamed |
| **Python distribution** | `team-km` | `pip install -e .` — package id stable for adopters |
| **CLI** | `python3 -m ki` | Unchanged |
| **MCP tools** | `teamkm_*` | Tool ids unchanged (hosts may already wire config) |
| **Cursor skills** | `.cursor/skills/teamkm-*` | Folder names unchanged; skill bodies say Groundline |
| **Env vars** | `TEAMKM_API_BASE`, `KI_HOST`, `KI_PORT` | Unchanged |

---

## Adopter fork

Teams may rename the GitHub repository (e.g. `groundline`) after “Use this template.” Update `site_url` and `repo_url` in `mkdocs.yml` to match their Pages path.

---

## Narrative (one line)

> **Groundline** turns merged, reviewed team knowledge into **retrievable context** for development and AI-assisted work—the **corpus and retrieval** side of context engineering, not a replacement for your IDE’s agent.
