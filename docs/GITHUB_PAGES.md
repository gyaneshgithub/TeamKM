# Publishing this documentation site

TeamKM uses **[MkDocs](https://www.mkdocs.org/)** with **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)**. The site is built from this `docs/` folder.

---

## Live site URL

After setup: **`https://<github-org-or-user>.github.io/TeamKM/`**  
(for this template: [gyaneshgithub.github.io/TeamKM](https://gyaneshgithub.github.io/TeamKM))

---

## Automatic deploy

Workflow [`.github/workflows/docs.yml`](https://github.com/gyaneshgithub/TeamKM/blob/main/.github/workflows/docs.yml) on push to **`main`**:

1. `pip install -e ".[docs]"`
2. `mkdocs gh-deploy --force` → **`gh-pages`** branch

---

## One-time GitHub settings

1. Repo **Settings → Pages**.
2. **Build and deployment** → Source: **Deploy from a branch**.
3. Branch: **`gh-pages`** / **`/(root)`**.
4. Save; first deploy may take 1–2 minutes after the workflow runs.

---

## Build locally

```bash
pip install -e ".[docs]"
mkdocs serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Production build:

```bash
mkdocs build -d site
```

(`site/` is gitignored.)

---

## Editing navigation

Add or move pages in [`mkdocs.yml`](https://github.com/gyaneshgithub/TeamKM/blob/main/mkdocs.yml) under `nav:`.
