#!/usr/bin/env bash
# Install the QA_ConfidenceWorkflow Cursor skill for the current user.
#
# Cursor reads personal skills from ~/.cursor/skills/<Name>/SKILL.md, which is
# outside any git repo — so a fresh machine (or a cloud agent VM) will not have
# it until this script runs.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/SKILL.md"
DEST_DIR="$HOME/.cursor/skills/QA_ConfidenceWorkflow"

mkdir -p "$DEST_DIR"
cp "$SRC" "$DEST_DIR/SKILL.md"

echo "Installed: $DEST_DIR/SKILL.md"
echo "Reload Cursor (or open a new chat) to use /QA_ConfidenceWorkflow."
