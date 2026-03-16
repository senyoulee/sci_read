#!/usr/bin/env bash
# Fetch new papers from the last 7 days (hep-lat, hep-th, hep-ex)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Weekly fetch: last 7 days ==="
cd "$SCRIPT_DIR"
python main.py fetch
