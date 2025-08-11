#!/bin/bash

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"
MERMAIDASCII_DIR="$PROJECT_DIR/build/mermaid_ascii"

set -ex

rm -rf "$MERMAIDASCII_DIR"
git clone https://github.com/AlexanderGrooff/mermaid-ascii "$MERMAIDASCII_DIR"

# Create binary / Update if exists
cd "$MERMAIDASCII_DIR"
MERMAIDASCII_VERSION="$(git tag --sort=-v:refname|head -n 1)"

git checkout "$MERMAIDASCII_VERSION"

"${PROJECT_DIR}/scripts/versioning.sh" "$MERMAIDASCII_VERSION"

go build
cp -f "$MERMAIDASCII_DIR/mermaid-ascii" "$PROJECT_DIR/src/mermaid_ascii"
chmod +x "$PROJECT_DIR/src/mermaid_ascii"
rm -rf "$MERMAIDASCII_DIR"
set +ex
