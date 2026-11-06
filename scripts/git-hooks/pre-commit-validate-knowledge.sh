#!/usr/bin/env bash
# Optional pre-commit hook: validate staged knowledge/**/*.md front matter.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
export PATH="$ROOT/.venv/bin:$PATH"
PYTHON="${PYTHON:-python3}"
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^knowledge/.*\.md$' || true)
if [[ -z "$STAGED" ]]; then
  exit 0
fi
echo "$STAGED" | xargs "$PYTHON" "$ROOT/scripts/validate_frontmatter.py" --root "$ROOT"
exit 0
