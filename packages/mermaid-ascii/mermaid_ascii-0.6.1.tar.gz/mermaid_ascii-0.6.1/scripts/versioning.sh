#!/usr/bin/env bash

echo "[II] Versioning pyproject.toml ..."

set -euo pipefail

if [ "$1" == "" ]; then
  echo "Version parameter is required."
  exit 1
fi

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"
PYPROJECT_PATH="${PROJECT_DIR}/pyproject.toml"

SEARCH_BY="version\s*=\s*\"[0-9]*\.[0-9]*\.[0-9]*\"\s*#\s*mermaid-ascii\sversion"
REPLACE_BY="version = \"$1\"  # mermaid-ascii version"

# match the line that has the comment marker too
SEARCH_RE='^version[[:space:]]*=[[:space:]]*"([0-9]+\.[0-9]+\.[0-9]+)"[[:space:]]*#.*mermaid-ascii[[:space:]]*version'

line="$(grep -E "$SEARCH_RE" "$PYPROJECT_PATH" || true)"
if [ -z "${line}" ]; then
  echo "No version found in the pyproject.toml." >&2
  exit 1
fi

CURRENT_VERSION="$(printf '%s\n' "$line" | sed -E 's/.*"([0-9]+\.[0-9]+\.[0-9]+)".*/\1/')"

ORIGINAL_CONTENT=$(cat "${PYPROJECT_PATH}")
sed -i "s/$SEARCH_BY/$REPLACE_BY/" "$PYPROJECT_PATH"
NEW_CONTENT=$(cat "${PYPROJECT_PATH}")

echo "[II] pyproject.toml directory: ${PYPROJECT_PATH}"
echo "[II] Current version: ${CURRENT_VERSION}"
echo "[II] New version: $1"

if [ "${ORIGINAL_CONTENT}" == "${NEW_CONTENT}" ]; then
  echo "[EE] The project uses already the latest version."
  exit 0
fi
