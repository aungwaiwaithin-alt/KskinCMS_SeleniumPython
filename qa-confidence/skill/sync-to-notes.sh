#!/usr/bin/env bash
# One-way sync: CMS git repo (canonical) → Mac notes folder (optional mirror).
#
# Use this if you still keep StepReporter HTML under
# ~/kskin-web(cms)-automation/reports/ and want the same authored YAML nearby.
# Never edit the notes copy as the source of truth — pull/edit in this repo first.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NOTES="${NOTES_ROOT:-$HOME/kskin-web(cms)-automation}"
DEST="$NOTES/qa-confidence"

if [[ ! -d "$NOTES" ]]; then
  echo "Notes folder not found: $NOTES"
  echo "Set NOTES_ROOT=... or create the folder if you want a mirror."
  exit 1
fi

mkdir -p "$DEST"
rsync -a --delete \
  --exclude 'generated/' \
  "$ROOT/qa-confidence/" "$DEST/"

# Keep generator next to notes too (handy for local one-liners)
mkdir -p "$NOTES/scripts"
cp "$ROOT/scripts/generate_qa_confidence_report.py" \
  "$NOTES/scripts/generate_qa_confidence_report.py"

echo "Mirrored authored qa-confidence → $DEST"
echo "Canonical remains: $ROOT/qa-confidence"
echo "Also ran: bash qa-confidence/skill/install.sh (recommended)"
bash "$ROOT/qa-confidence/skill/install.sh"
