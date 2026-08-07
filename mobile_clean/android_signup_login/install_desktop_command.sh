#!/usr/bin/env bash
# Install the CLEAN Android signup .command onto the Desktop one-click folder.
# Does NOT touch old run-android-signup-login.command wrappers.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/run_android_signup_login.command"
DEST=""
for d in \
  "$HOME/Desktop/One click bash files" \
  "$HOME/One click bash files" \
  "$HOME/Documents/One click bash files"
do
  [[ -d "$d" ]] && DEST="$d" && break
done
DEST="${1:-${DEST:-$HOME/Desktop/One click bash files}}"
mkdir -p "$DEST"

chmod +x "$SRC"
cp -f "$SRC" "$DEST/run-android-signup-login-CLEAN.command"
chmod +x "$DEST/run-android-signup-login-CLEAN.command"

echo "Installed:"
echo "  $DEST/run-android-signup-login-CLEAN.command"
echo ""
echo "Double-click that file (Appium + emulator must be running)."
echo "Old run-android-signup-login.command files are left alone on purpose."
