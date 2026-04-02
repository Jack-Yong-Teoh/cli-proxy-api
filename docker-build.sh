#!/usr/bin/env bash
set -euo pipefail

# Build and run both CPA and drission-scraper from workspace root.
docker compose up -d --build --remove-orphans

echo "Started CPA + drission-scraper"
echo "Use: docker compose logs -f"
