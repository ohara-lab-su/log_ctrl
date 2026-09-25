#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DOCS_DIR/.." && pwd)"
SRC_DIR="$ROOT_DIR/src"

export PYTHONPATH="$SRC_DIR:${PYTHONPATH:-}"

rm -rf "$DOCS_DIR/_build" "$DOCS_DIR/api"

sphinx-apidoc \
  -o "$DOCS_DIR/api" \
  "$SRC_DIR/log_server" \
  --force \
  --module-first

sphinx-build \
  -b html \
  "$DOCS_DIR" \
  "$DOCS_DIR/_build/html"

touch "$DOCS_DIR/_build/html/.nojekyll"
