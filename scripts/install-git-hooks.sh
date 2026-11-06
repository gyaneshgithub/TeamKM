#!/usr/bin/env bash
# Install optional client-side hooks (REQUIREMENTS §4.6). Does not affect remote.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/.git/hooks"
cp "$ROOT/scripts/git-hooks/pre-commit-validate-knowledge.sh" "$ROOT/.git/hooks/pre-commit"
chmod +x "$ROOT/.git/hooks/pre-commit"
echo "Installed $ROOT/.git/hooks/pre-commit (validates staged knowledge/**/*.md)"
