#!/bin/bash
# AgentRx Trial Initialization Script
# Creates git worktrees for parallel trial development

set -e

INPUT=$1

if [ -z "$INPUT" ]; then
  echo "Error: Approach name or document path required"
  echo "Usage: trial-init.sh <approach-name|document-path>"
  echo "Examples:"
  echo "  trial-init.sh plaid"
  echo "  trial-init.sh _bmad-output/implementation-artifacts/iteration-0-spec.md"
  exit 1
fi

TRIALS_FILE="_bmad-output/trials/trials.yaml"

# Function to initialize a single trial
init_trial() {
  local APPROACH=$1
  local WORKTREE_DIR="worktrees/${APPROACH}"
  local BRANCH_NAME="trial/${APPROACH}"

  # Check if already exists
  if [ -d "$WORKTREE_DIR" ]; then
    echo "  ⚠️  Worktree for '$APPROACH' already exists at $WORKTREE_DIR"
    return 0
  fi

  echo "  🚀 Initializing: $APPROACH"

  # Create worktree with new branch
  git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" 2>/dev/null || {
    git worktree add "$WORKTREE_DIR" "$BRANCH_NAME" 2>/dev/null || {
      echo "  ❌ Failed to create worktree for $APPROACH"
      return 1
    }
  }

  # Create baseline structure in worktree
  mkdir -p "$WORKTREE_DIR/src/server/integrations/${APPROACH}"
  mkdir -p "$WORKTREE_DIR/src/server/services"
  mkdir -p "$WORKTREE_DIR/src/shared"

  # Create trial context file
  cat > "$WORKTREE_DIR/.trial-context" <<EOF
# Trial Context: $APPROACH
approach: $APPROACH
branch: $BRANCH_NAME
worktree: $WORKTREE_DIR
initialized: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
spec: _bmad-output/implementation-artifacts/iteration-0-spec.md

# Approach-specific notes
# Add credentials, API docs, integration notes here
EOF

  # Copy package.json template if it exists, otherwise create minimal one
  if [ -f "templates/package.json" ]; then
    cp templates/package.json "$WORKTREE_DIR/"
  else
    cat > "$WORKTREE_DIR/package.json" <<EOF
{
  "name": "family-cfo-${APPROACH}-trial",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server/cli.ts",
    "build": "tsc",
    "test": "vitest",
    "cli": "tsx src/server/cli.ts"
  },
  "dependencies": {
    "commander": "^12.0.0",
    "chalk": "^5.3.0",
    "dotenv": "^16.4.1",
    "googleapis": "^132.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0",
    "vitest": "^1.2.0"
  }
}
EOF
  fi

  # Create minimal tsconfig.json
  cat > "$WORKTREE_DIR/tsconfig.json" <<EOF
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF

  # Create .env.example
  cat > "$WORKTREE_DIR/.env.example" <<EOF
# Google Sheets
GOOGLE_SHEETS_ID=your-sheet-id
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service-account.json

# ${APPROACH} specific credentials
# Add your credentials here
EOF

  # Update trials.yaml
  if [ ! -f "$TRIALS_FILE" ]; then
    mkdir -p "$(dirname "$TRIALS_FILE")"
    cat > "$TRIALS_FILE" <<EOF
trials: {}
EOF
  fi

  # Add trial entry to trials.yaml (simple append for now)
  cat >> "$TRIALS_FILE" <<EOF
  ${APPROACH}:
    branch: ${BRANCH_NAME}
    worktree: ${WORKTREE_DIR}
    status: initialized
    started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
    metrics: {}
EOF

  echo "  ✅ $APPROACH initialized"
}

# Determine if input is a file or approach name
if [ -f "$INPUT" ]; then
  # Document mode - parse and initialize all approaches
  echo "📄 Document mode: Parsing $INPUT"
  echo "========================================"
  echo ""

  # Parse document to extract approach names
  APPROACHES=$(grep -E "^##+ Approach [0-9]+:" "$INPUT" | sed -E 's/^##+ Approach [0-9]+: ([A-Za-z ]+).*/\1/' | awk '{print tolower($1)}')

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

  echo "🚀 Initializing trials:"
  echo ""

  # Initialize each approach
  for approach in $APPROACHES; do
    init_trial "$approach"
  done

  echo ""
  echo "✅ All trials initialized!"
  echo ""
  echo "Next step: /agentrx:trial-work $INPUT"

else
  # Single approach mode
  APPROACH=$INPUT
  echo "🚀 Initializing trial worktree: $APPROACH"
  echo "========================================"
  echo ""

  mkdir -p _bmad-output/trials
  init_trial "$APPROACH"

  echo ""
  echo "✅ Trial initialized successfully!"
  echo ""
  echo "Next steps:"
  echo "  1. cd worktrees/$APPROACH"
  echo "  2. Edit .trial-context with approach-specific info"
  echo "  3. Add credentials to .env (copy from .env.example)"
  echo "  4. Run: /agentrx:trial-work <document-path>"
fi

echo ""
