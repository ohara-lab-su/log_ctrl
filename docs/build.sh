#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DOCS_DIR/.." && pwd)"
SRC_DIR="$ROOT_DIR/src"
export PYTHONPATH="$SRC_DIR:${PYTHONPATH:-}"

rm -rf "$DOCS_DIR/_build"

for lang in en ja; do
  API_DIR="$DOCS_DIR/$lang/api"
  rm -f "$API_DIR"/*.rst
  sphinx-apidoc -o "$API_DIR" "$SRC_DIR/log_ctrl" \
    "$SRC_DIR/log_ctrl/server_grpc/log_grpc_server.py" \
    --force --module-first
  DOCS_LANGUAGE="$lang" sphinx-build -b html -c "$DOCS_DIR" \
    "$DOCS_DIR/$lang" "$DOCS_DIR/_build/html/$lang"
done

cp -a "$DOCS_DIR/_build/html/en/." "$DOCS_DIR/_build/html/"
touch "$DOCS_DIR/_build/html/.nojekyll"
test -f "$DOCS_DIR/_build/html/index.html"
test -f "$DOCS_DIR/_build/html/en/index.html"
test -f "$DOCS_DIR/_build/html/ja/index.html"
