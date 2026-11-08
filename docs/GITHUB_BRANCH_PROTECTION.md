# Protecting `main` on GitHub

GitHub shows **“Your main branch isn’t protected”** when `main` has no rule that blocks force-push/deletion or enforces checks before merge.

## Why automation may fail from the CLI

The REST API for **classic branch protection** can return **HTTP 403** for **private** repositories on a **free personal** account with a message like:

> Upgrade to GitHub Pro or make this repository public to enable this feature.

That does **not** mean branch protection is impossible—it means **API-based** configuration may be blocked until you **upgrade**, move the repo to an **organization** with the right plan, or change visibility (if policy allows).

## Fix via the UI (recommended when the banner appears)

1. Open the repo on GitHub → **Settings** → **Branches** (or use **Protect this branch** in the banner).
2. **Add branch protection rule** for `main`.
3. Enable (aligned with [Contributing](contributing.md)):
   - **Require a pull request before merging**
   - **Require approvals**: at least **1** (tune per team)
   - **Require status checks to pass** (our workflow job is named **`test`** in [`.github/workflows/ci.yml`](https://github.com/gyaneshgithub/TeamKM/blob/main/.github/workflows/ci.yml))
   - **Require conversation resolution** before merging (optional but useful)
   - **Do not allow bypassing** the above settings (admins follow rules too), if available
4. Save.

After the next push to `main` or a PR run, the check **`test`** will appear in the dropdown for required checks.

## Required check name

The CI workflow defines a single job `test` (see `ci.yml`). In branch protection, pick **test** as the required check.

## Alternatives if your plan blocks protection

- **GitHub Pro** / **Team / Enterprise** — enables full branch protection on private repos.
- **Organization repo** — often matches team policies better than a personal fork.
- **Process-only** — keep merging only via PR and never `git push --force` to `main` (weak without server-side enforcement).

## Related

- [Contributing](contributing.md) — branch workflow (`main` + feature branches)
