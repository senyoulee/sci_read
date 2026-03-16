#!/usr/bin/env bash
# Fetch new papers, generate report, then commit and push everything to GitHub
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Fetching new papers and generating report ==="
python main.py fetch

# Commit and push any remaining project file changes (scripts, code, etc.)
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "No additional project changes to commit."
else
    git add -A
    git commit -m "Update project: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin master
    echo "Pushed project changes to GitHub."
fi
