#!/usr/bin/env bash
# Backfill historical papers (hep-lat, hep-th, hep-ex)
# Usage: ./fetch_backfill.sh [3m|6m|1y|all]
#   3m  - last 3 months
#   6m  - last 6 months
#   1y  - last 1 year
#   all - run all three periods sequentially (default)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PERIOD="${1:-all}"

run_backfill() {
    local period="$1"
    echo "=== Backfill: $period ==="
    python main.py backfill --period "$period"
}

case "$PERIOD" in
    3m|6m|1y)
        run_backfill "$PERIOD"
        ;;
    all)
        run_backfill 3m
        run_backfill 6m
        run_backfill 1y
        ;;
    *)
        echo "Error: unknown period '$PERIOD'. Choose from: 3m, 6m, 1y, all" >&2
        exit 1
        ;;
esac
