$ErrorActionPreference = "Stop"

# Build and run both CPA and drission-scraper from workspace root.
docker compose up -d --build --remove-orphans

Write-Host "Started CPA + drission-scraper"
Write-Host "Use: docker compose logs -f"
