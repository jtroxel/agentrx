#!/bin/bash
# AgentRx Trial Work Script
# Parses document to identify trials and prepares for parallel agent execution

set -e

DOC_PATH=$1

if [ -z "$DOC_PATH" ]; then
  echo "Error: Document path required"
  echo "Usage: trial-work.sh <document-path>"
  echo "Example: trial-work.sh _bmad-output/implementation-artifacts/iteration-0-spec.md"
  exit 1
fi

if [ ! -f "$DOC_PATH" ]; then
  echo "Error: Document not found at $DOC_PATH"
  exit 1
fi

TRIALS_FILE="_bmad-output/trials/trials.yaml"

echo "🔍 Parsing document for trial approaches: $DOC_PATH"
echo "========================================"
echo ""

# Parse document to extract approach names
# Look for patterns like "### Approach 1: Plaid API" or "Approach 1: Plaid API"
APPROACHES=$(grep -E "^##+ Approach [0-9]+:" "$DOC_PATH" | sed -E 's/^##+ Approach [0-9]+: ([A-Za-z ]+).*/\1/' | awk '{print tolower($1)}')

if [ -z "$APPROACHES" ]; then
  echo "❌ No approaches found in document"
  echo "Expected format: '### Approach N: Name' or '## Approach N: Name'"
  exit 1
fi

echo "📋 Found approaches:"
echo "$APPROACHES" | while read -r approach; do
  echo "  - $approach"
done
echo ""

# Check which worktrees exist and which need initialization
echo "🔧 Checking trial worktrees:"
echo ""
MISSING=()
READY=()

for approach in $APPROACHES; do
  WORKTREE_DIR="worktrees/${approach}"
  if [ ! -d "$WORKTREE_DIR" ]; then
    echo "  ❌ $approach - not initialized"
    MISSING+=("$approach")
  else
    echo "  ✅ $approach - ready"
    READY+=("$approach")

    # Update trial status to in-progress
    if [ -f "$TRIALS_FILE" ]; then
      sed -i.bak "s/${approach}:$/&\n    status: in-progress/" "$TRIALS_FILE" 2>/dev/null || true
    fi
  fi
done
echo ""

# Output results for command to process
if [ ${#MISSING[@]} -gt 0 ]; then
  echo "⚠️  Some trials need initialization:"
  for approach in "${MISSING[@]}"; do
    echo "  /agentrx:trial-init $approach"
  done
  echo ""
fi

if [ ${#READY[@]} -gt 0 ]; then
  echo "✅ Ready to spawn agents for:"
  for approach in "${READY[@]}"; do
    echo "  - $approach (worktrees/$approach/)"
  done
  echo ""
  echo "READY_TRIALS=${READY[*]}"
else
  echo "❌ No trials ready. Initialize trials first."
  exit 1
fi
