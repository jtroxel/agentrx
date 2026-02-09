#!/bin/bash
# AgentRx Trial Status Script
# Shows status of all trials

TRIALS_FILE="_bmad-output/trials/trials.yaml"
WORKTREE_DIR="worktrees"

echo "📊 Trial Status"
echo "========================================"
echo ""

# Check if trials directory exists
if [ ! -d "$WORKTREE_DIR" ]; then
  echo "No trials found. Run /agentrx:trial-init <approach> to create one."
  exit 0
fi

# Check if any worktrees exist
WORKTREE_COUNT=$(find "$WORKTREE_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
if [ "$WORKTREE_COUNT" -eq 0 ]; then
  echo "No trials found. Run /agentrx:trial-init <approach> to create one."
  exit 0
fi

# List all worktrees
for trial_dir in "$WORKTREE_DIR"/*/ ; do
  if [ -d "$trial_dir" ]; then
    APPROACH=$(basename "$trial_dir")

    echo "Trial: $APPROACH"
    echo "  Location: $trial_dir"

    # Get branch name
    if [ -d "$trial_dir/.git" ]; then
      BRANCH=$(cd "$trial_dir" && git branch --show-current 2>/dev/null)
      echo "  Branch: $BRANCH"
    fi

    # Get status from trials.yaml if available
    if [ -f "$TRIALS_FILE" ]; then
      STATUS=$(grep -A 5 "^  ${APPROACH}:" "$TRIALS_FILE" | grep "status:" | awk '{print $2}' || echo "unknown")
      echo "  Status: $STATUS"
    fi

    # Check if .trial-context exists
    if [ -f "$trial_dir/.trial-context" ]; then
      INITIALIZED=$(grep "initialized:" "$trial_dir/.trial-context" | cut -d' ' -f2)
      echo "  Initialized: $INITIALIZED"
    fi

    # Check for package.json (indicates setup)
    if [ -f "$trial_dir/package.json" ]; then
      echo "  Setup: ✅ Dependencies configured"
    else
      echo "  Setup: ⚠️  No package.json found"
    fi

    # Check for source files
    SRC_COUNT=$(find "$trial_dir/src" -name "*.ts" 2>/dev/null | wc -l)
    if [ "$SRC_COUNT" -gt 0 ]; then
      echo "  Files: $SRC_COUNT TypeScript files"
    fi

    echo ""
  fi
done

# Show trials.yaml summary if it exists
if [ -f "$TRIALS_FILE" ]; then
  echo "----------------------------------------"
  echo "Trials Registry: $TRIALS_FILE"
  echo ""
  cat "$TRIALS_FILE"
fi

echo ""
echo "Commands:"
echo "  /agentrx:trial-init <approach>   - Create new trial"
echo "  /agentrx:trial-work <approach>   - Work on trial"
echo "  /agentrx:trial-status            - Show this status"
