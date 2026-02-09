#!/bin/bash
# AgenTrx Project Initialization Script
# Sets up the AgenTrx directory structure for AI-assisted development

set -e

# Defaults
MODE="copy"
TARGET_DIR="."
AGENTRX_SOURCE="${AGENTRX_SOURCE:-$(dirname "$0")/../../..}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --copy)
      MODE="copy"
      shift
      ;;
    --link)
      MODE="link"
      shift
      ;;
    --custom)
      MODE="custom"
      shift
      ;;
    -h|--help)
      echo "Usage: init.sh [--copy|--link|--custom] [target-dir]"
      echo ""
      echo "Options:"
      echo "  --copy    Copy AgenTrx files to project (default)"
      echo "  --link    Create symlinks to AgenTrx assets"
      echo "  --custom  Prompt for custom directory paths"
      echo ""
      echo "Examples:"
      echo "  init.sh                    # Initialize current directory"
      echo "  init.sh --link /my/project # Initialize with symlinks"
      exit 0
      ;;
    *)
      TARGET_DIR="$1"
      shift
      ;;
  esac
done

# Resolve absolute path
TARGET_DIR=$(cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")

echo "🚀 Initializing AgenTrx Project"
echo "========================================"
echo "Target: $TARGET_DIR"
echo "Mode: $MODE"
echo ""

# Create target directory if needed
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# Define directory structure
AGENTRX_DIR="_agents"
PROJECT_DIR="_project"
DOCS_DIR="$PROJECT_DIR/docs/agentrx"

# Custom mode - prompt for directories
if [ "$MODE" = "custom" ]; then
  echo "📁 Custom Directory Configuration"
  echo ""
  read -p "Agent assets directory [$AGENTRX_DIR]: " input
  AGENTRX_DIR="${input:-$AGENTRX_DIR}"

  read -p "Project directory [$PROJECT_DIR]: " input
  PROJECT_DIR="${input:-$PROJECT_DIR}"

  read -p "Documentation directory [$DOCS_DIR]: " input
  DOCS_DIR="${input:-$DOCS_DIR}"
  echo ""
fi

echo "📂 Creating directory structure..."

# Create _agents structure
mkdir -p "$AGENTRX_DIR/commands/agentrx"
mkdir -p "$AGENTRX_DIR/skills/agentrx"
mkdir -p "$AGENTRX_DIR/hooks/agentrx"
mkdir -p "$AGENTRX_DIR/scripts/agentrx"
echo "  ✅ $AGENTRX_DIR/"

# Create _project structure
mkdir -p "$PROJECT_DIR/src"
mkdir -p "$DOCS_DIR/deltas"
mkdir -p "$DOCS_DIR/vibes"
mkdir -p "$DOCS_DIR/history"
echo "  ✅ $PROJECT_DIR/"
echo "  ✅ $DOCS_DIR/"

# Create .claude directory for Claude Code integration
mkdir -p ".claude/commands"
mkdir -p ".claude/skills"
echo "  ✅ .claude/"

# Handle copy vs link mode for AgenTrx assets
if [ "$MODE" = "link" ] && [ -d "$AGENTRX_SOURCE/_agents" ]; then
  echo ""
  echo "🔗 Creating symlinks to AgenTrx assets..."

  # Link command files
  if [ -d "$AGENTRX_SOURCE/_agents/commands/agentrx" ]; then
    ln -sf "$AGENTRX_SOURCE/_agents/commands/agentrx" "$AGENTRX_DIR/commands/" 2>/dev/null || true
    echo "  ✅ Linked commands/agentrx"
  fi

  # Link skill directories
  if [ -d "$AGENTRX_SOURCE/_agents/skills/agentrx" ]; then
    ln -sf "$AGENTRX_SOURCE/_agents/skills/agentrx" "$AGENTRX_DIR/skills/" 2>/dev/null || true
    echo "  ✅ Linked skills/agentrx"
  fi

  # Link scripts
  if [ -d "$AGENTRX_SOURCE/_agents/scripts/agentrx" ]; then
    ln -sf "$AGENTRX_SOURCE/_agents/scripts/agentrx" "$AGENTRX_DIR/scripts/" 2>/dev/null || true
    echo "  ✅ Linked scripts/agentrx"
  fi
fi

# Create AGENTS.md if it doesn't exist
if [ ! -f "AGENTS.md" ]; then
  echo ""
  echo "📄 Creating AGENTS.md..."
  cat > "AGENTS.md" <<'EOF'
# AGENTS Guidance

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## IMPORTANT: Coding Agents
> Follow the instructions precisely. If it wasn't specified, don't do it.

## Startup Context
When starting a chat conversation or session for this project, read all the files indicated below. Do NOT read anything else until directed in prompts.

### PARALLEL READ the following ONLY:
- README.md # to understand the basics of the project and directory structure
- _agents/commands/agentrx/*.md # agentrx commands
- _agents/skills/agentrx/** # agentrx skills

### IMPORTANT: Show What You've Read
At startup, after reading the files indicated above, print a list of the files read into the chat terminal.
EOF
  echo "  ✅ AGENTS.md"
fi

# Create CLAUDE.md if it doesn't exist
if [ ! -f "CLAUDE.md" ]; then
  echo "📄 Creating CLAUDE.md..."
  cat > "CLAUDE.md" <<'EOF'
# Claude Code Guidance

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. IMPORTANT: Start with AGENTS.md
When loading memory, prioritize reading AGENTS.md first. This file contains instructions for coding agents. Treat AGENTS.md as your effective `CLAUDE.md` file.

## 2. Please Summarize What You've Read
At startup, after reading the files indicated above, provide a list of the files read in the chat history.
EOF
  echo "  ✅ CLAUDE.md"
fi

# Create .env with AgenTrx environment variables
if [ ! -f ".env" ]; then
  echo "📄 Creating .env..."
  cat > ".env" <<EOF
# AgenTrx Configuration
AGENTRX_DIR=$AGENTRX_DIR
AGENTRX_PROJECT_DIR=$PROJECT_DIR
AGENTRX_DOCS_DIR=$DOCS_DIR
EOF
  echo "  ✅ .env"
else
  echo ""
  echo "📄 Appending to existing .env..."
  cat >> ".env" <<EOF

# AgenTrx Configuration
AGENTRX_DIR=$AGENTRX_DIR
AGENTRX_PROJECT_DIR=$PROJECT_DIR
AGENTRX_DOCS_DIR=$DOCS_DIR
EOF
  echo "  ✅ .env (updated)"
fi

# Create .gitignore entries if .gitignore exists
if [ -f ".gitignore" ]; then
  if ! grep -q "# AgenTrx" ".gitignore" 2>/dev/null; then
    echo "" >> ".gitignore"
    echo "# AgenTrx" >> ".gitignore"
    echo ".env" >> ".gitignore"
    echo "  ✅ .gitignore (updated)"
  fi
fi

# Setup Claude Code integration (symlinks in .claude/)
echo ""
echo "🔗 Setting up Claude Code integration..."

# Link commands to .claude/commands
if [ -d "$AGENTRX_DIR/commands/agentrx" ]; then
  ln -sf "../../$AGENTRX_DIR/commands/agentrx" ".claude/commands/agentrx" 2>/dev/null || true
  echo "  ✅ .claude/commands/agentrx -> $AGENTRX_DIR/commands/agentrx"
fi

# Link skills to .claude/skills
if [ -d "$AGENTRX_DIR/skills/agentrx" ]; then
  ln -sf "../../$AGENTRX_DIR/skills/agentrx" ".claude/skills/agentrx" 2>/dev/null || true
  echo "  ✅ .claude/skills/agentrx -> $AGENTRX_DIR/skills/agentrx"
fi

echo ""
echo "========================================"
echo "✅ AgenTrx initialized successfully!"
echo ""
echo "Directory structure:"
echo "  $AGENTRX_DIR/          - Agent assets (commands, skills, hooks, scripts)"
echo "  $PROJECT_DIR/          - Your project code"
echo "  $DOCS_DIR/   - Development docs (deltas, vibes, history)"
echo ""
echo "Next steps:"
echo "  1. Review AGENTS.md and CLAUDE.md"
echo "  2. Add your project code to $PROJECT_DIR/"
echo "  3. Use /agentrx:prompt-new to create prompts"
echo "  4. Use /agentrx:trial-init for parallel development"
echo ""
