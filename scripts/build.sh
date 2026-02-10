#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

# Clean AppleDouble files to avoid Docker xattr issues on macOS
find "$ROOT_DIR" -name '._*' -delete

# Build image
if [[ "${1-}" == "--rebuild" ]]; then
  docker compose build --no-cache
else
  docker compose build
fi

# Optionally restart compose stack
if [[ "${1-}" == "--up" || "${2-}" == "--up" ]]; then
  docker compose up -d
fi

# Optionally run migrations
if [[ "${1-}" == "--migrate" || "${2-}" == "--migrate" || "${3-}" == "--migrate" ]]; then
  docker compose exec api alembic upgrade head
fi

# Optionally run tests
if [[ "${1-}" == "--test" || "${2-}" == "--test" || "${3-}" == "--test" || "${4-}" == "--test" ]]; then
  docker compose run --rm test
fi
