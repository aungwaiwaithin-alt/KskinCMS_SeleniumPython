#!/usr/bin/env bash
# Diagnose / recover mobile one-click originals on the Mac Desktop pack.
set -euo pipefail
DEST="${1:-$HOME/Desktop/One click bash files}"
echo "Pack: $DEST"
echo ""
echo "=== Visible *.legacy ==="
ls -la "$DEST"/*.legacy 2>/dev/null || echo "(none)"
echo ""
echo "=== Hidden .legacy/ ==="
ls -la "$DEST/.legacy" 2>/dev/null || echo "(none)"
echo ""
echo "=== Which look like OUR wrappers (bad as backup)? ==="
for f in "$DEST"/*.legacy "$DEST/.legacy"/*; do
  [[ -f "$f" ]] || continue
  if grep -q 'thin wrapper\|suppressed legacy open\|FRESH RUN' "$f" 2>/dev/null; then
    echo "WRAPPER (bad backup): $f"
  else
    echo "ORIGINAL? (good):     $f  ($(wc -c < "$f") bytes)"
  fi
done
echo ""
echo "Good originals are usually 4KB–6KB. Wrappers are ~2–3KB and contain 'thin wrapper'."
echo "If all say WRAPPER, restore the old .command from Time Machine into:"
echo "  $DEST/.legacy/run-android-signup-login.command"
echo "  $DEST/.legacy/run-ios-signup-login.command"
