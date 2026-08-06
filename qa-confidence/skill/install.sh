#!/usr/bin/env bash
# Keep install.sh as a thin wrapper → AquaProjects-wide install when possible,
# else fall back to global ~/.cursor/skills only.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"

if [[ -d "$AQUA" ]]; then
  exec bash "$DIR/install-aquaprojects.sh"
fi

SRC="$DIR/SKILL.md"
DEST_DIR="$HOME/.cursor/skills/QA_ConfidenceWorkflow"
mkdir -p "$DEST_DIR"
cp "$SRC" "$DEST_DIR/SKILL.md"
echo "Installed (global only): $DEST_DIR/SKILL.md"
echo "AquaProjects not found — re-run install-aquaprojects.sh later for shared copy."
echo "Reload Cursor (or open a new chat) to use /QA_ConfidenceWorkflow."
