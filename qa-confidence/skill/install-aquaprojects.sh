#!/usr/bin/env bash
# Install QA_ConfidenceWorkflow for all AquaProjects work (CMS + mobile + …).
#
# Places:
#   1) ~/AquaProjects/QA_ConfidenceWorkflow/SKILL.md     (shared source)
#   2) ~/AquaProjects/.cursor/skills/.../SKILL.md       (when AquaProjects is open)
#   3) ~/.cursor/skills/QA_ConfidenceWorkflow/SKILL.md  (global — all Cursor chats)
#
# Run on your Mac from any clone that contains this script, e.g.:
#   bash ~/AquaProjects/KskinCMS/qa-confidence/skill/install-aquaprojects.sh
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/SKILL.md"
AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"

if [[ ! -f "$SRC" ]]; then
  echo "Missing SKILL.md next to this script: $SRC" >&2
  exit 1
fi

if [[ ! -d "$AQUA" ]]; then
  echo "AquaProjects not found: $AQUA" >&2
  echo "Set AQUA_ROOT=/path/to/AquaProjects if needed." >&2
  exit 1
fi

SHARED="$AQUA/QA_ConfidenceWorkflow"
PROJECT_SKILL="$AQUA/.cursor/skills/QA_ConfidenceWorkflow"
GLOBAL_SKILL="$HOME/.cursor/skills/QA_ConfidenceWorkflow"

mkdir -p "$SHARED" "$PROJECT_SKILL" "$GLOBAL_SKILL"
cp "$SRC" "$SHARED/SKILL.md"
cp "$SRC" "$PROJECT_SKILL/SKILL.md"
cp "$SRC" "$GLOBAL_SKILL/SKILL.md"

# Tiny pointer README at AquaProjects root of the skill folder
cat > "$SHARED/README.md" <<EOF
# QA_ConfidenceWorkflow (shared)

Canonical shared Cursor skill for AquaProjects (CMS web + mobile).

- Edit/source: \`SKILL.md\` in this folder (updated via install script from KskinCMS)
- Global Cursor copy: \`~/.cursor/skills/QA_ConfidenceWorkflow/SKILL.md\`
- Per-product mappings stay in each project’s \`qa-confidence/\` (e.g. \`KskinCMS/qa-confidence/\`)

Reinstall after skill updates:

\`\`\`bash
bash $AQUA/KskinCMS/qa-confidence/skill/install-aquaprojects.sh
\`\`\`

Then start a **new** Agent chat and type \`/QA_ConfidenceWorkflow\`.
EOF

echo "Installed shared source: $SHARED/SKILL.md"
echo "Installed AquaProjects project skill: $PROJECT_SKILL/SKILL.md"
echo "Installed global Cursor skill: $GLOBAL_SKILL/SKILL.md"
echo
echo "Next: start a NEW Agent chat in Cursor and type /QA_ConfidenceWorkflow"
