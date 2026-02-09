#!/bin/bash
# AgentRx Project Initialization Script
# Sets up the AgentRx directory structure for AI-assisted development

set -e

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTRX_SOURCE="${AGENTRX_SOURCE:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

# Defaults
MODE="copy"
TARGET_DIR="."
RUN_SETUP=true

# Colors (if terminal supports them)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
else
    GREEN=''
    BLUE=''
    YELLOW=''
    NC=''
fi

print_success() { echo -e "${GREEN}$1${NC}"; }
print_info() { echo -e "${BLUE}$1${NC}"; }
print_warn() { echo -e "${YELLOW}$1${NC}"; }

usage() {
    cat << EOF
AgentRx Project Initialization v$VERSION

Usage: init.sh [OPTIONS] [target-dir]

Options:
  --copy        Copy AgentRx files to project (default)
  --link        Create symlinks to AgentRx assets
  --custom      Prompt for custom directory paths
  --no-setup    Skip Claude Code setup step
  -h, --help    Show this help message

Examples:
  init.sh                       # Initialize current directory
  init.sh --link /my/project    # Initialize with symlinks
  init.sh --custom              # Interactive custom setup

Environment:
  AGENTRX_SOURCE    Source directory for AgentRx assets (default: auto-detect)
EOF
    exit 0
}

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
        --no-setup)
            RUN_SETUP=false
            shift
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            TARGET_DIR="$1"
            shift
            ;;
    esac
done

# Resolve absolute path
if [ -d "$TARGET_DIR" ]; then
    TARGET_DIR=$(cd "$TARGET_DIR" && pwd)
else
    mkdir -p "$TARGET_DIR"
    TARGET_DIR=$(cd "$TARGET_DIR" && pwd)
fi

echo ""
echo "AgentRx Project Initialization v$VERSION"
echo "========================================"
echo "Target:  $TARGET_DIR"
echo "Mode:    $MODE"
echo "Source:  $AGENTRX_SOURCE"
echo ""

cd "$TARGET_DIR"

# Define directory structure
AGENTRX_DIR="_agents"
PROJECT_DIR="_project"
DOCS_DIR="$PROJECT_DIR/docs/agentrx"

# Custom mode - prompt for directories
if [ "$MODE" = "custom" ]; then
    print_info "Custom Directory Configuration"
    echo ""
    read -p "Agent assets directory [$AGENTRX_DIR]: " input
    AGENTRX_DIR="${input:-$AGENTRX_DIR}"

    read -p "Project directory [$PROJECT_DIR]: " input
    PROJECT_DIR="${input:-$PROJECT_DIR}"

    read -p "Documentation directory [$DOCS_DIR]: " input
    DOCS_DIR="${input:-$DOCS_DIR}"
    echo ""
fi

# --- Create Directory Structure ---
print_info "Creating directory structure..."

# _agents structure
mkdir -p "$AGENTRX_DIR/commands/agentrx"
mkdir -p "$AGENTRX_DIR/skills/agentrx"
mkdir -p "$AGENTRX_DIR/hooks/agentrx"
mkdir -p "$AGENTRX_DIR/scripts/agentrx"
mkdir -p "$AGENTRX_DIR/agents/agentrx"
print_success "  [OK] $AGENTRX_DIR/"

# _project structure
mkdir -p "$PROJECT_DIR/src"
mkdir -p "$DOCS_DIR/deltas"
mkdir -p "$DOCS_DIR/vibes"
mkdir -p "$DOCS_DIR/history"
print_success "  [OK] $PROJECT_DIR/"
print_success "  [OK] $DOCS_DIR/"

# .claude directory
mkdir -p ".claude/commands"
mkdir -p ".claude/skills"
print_success "  [OK] .claude/"

# --- Handle Link Mode ---
if [ "$MODE" = "link" ] && [ -d "$AGENTRX_SOURCE/_agents" ]; then
    echo ""
    print_info "Creating symlinks to AgentRx assets..."

    for subdir in commands skills scripts hooks agents; do
        if [ -d "$AGENTRX_SOURCE/_agents/$subdir/agentrx" ]; then
            rm -rf "$AGENTRX_DIR/$subdir/agentrx"
            ln -sf "$AGENTRX_SOURCE/_agents/$subdir/agentrx" "$AGENTRX_DIR/$subdir/agentrx"
            print_success "  [OK] Linked $subdir/agentrx"
        fi
    done
fi

# --- Create Configuration Files ---
echo ""
print_info "Creating configuration files..."

# AGENTS.md
if [ ! -f "AGENTS.md" ]; then
    cat > "AGENTS.md" << 'EOF'
# AGENTS Guidance

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## IMPORTANT: Coding Agents
> Follow the instructions precisely. If it wasn't specified, don't do it.

## Startup Context
When starting a chat conversation or session for this project, read all the files indicated below. Do NOT read anything else until directed in prompts.

### PARALLEL READ the following ONLY:
#### AgentRx Instructions
- README.md # to understand the basics of the project and directory structure
- _agents/commands/agentrx/*.md # agentrx commands
- _agents/skills/agentrx/*.md # agentrx skills

#### Project Context
Project-specific commands, skills, and context documents follow similar naming conventions.
Add those context documents into your context when prompted by the user.

## IMPORTANT: List What Files You've Read on Startup
At startup, after reading the files indicated above, print a list of the files read into the chat terminal.
EOF
    print_success "  [OK] AGENTS.md"
fi

# CLAUDE.md
if [ ! -f "CLAUDE.md" ]; then
    cat > "CLAUDE.md" << 'EOF'
# Claude Code Guidance

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. IMPORTANT: Start with AGENTS.md
When loading memory, prioritize reading AGENTS.md first. This file contains instructions for coding agents.

## 2. Please Summarize What You've Read
At startup, after reading the files indicated above, provide a list of the files read in the chat history.

## Context Documents
For comprehensive project context, see [CONTEXT_DOCUMENTS_INDEX.md](./CONTEXT_DOCUMENTS_INDEX.md).
EOF
    print_success "  [OK] CLAUDE.md"
fi

# CHAT_START.md
if [ ! -f "CHAT_START.md" ]; then
    cat > "CHAT_START.md" << 'EOF'
---
arx: config
name: chat-start
description: Bootstrap instructions for coding agents starting new sessions
version: 1
---

# AgentRx Bootstrap Instructions

> **For Coding Agents**: Follow these instructions precisely at session start.

## Step 1: Load Core Context

Read these files **in parallel** to establish AgentRx capabilities:

### Commands (treat as native slash commands)
```
_agents/commands/agentrx/*.md
```

### Skills
```
_agents/skills/agentrx/*.md
```

## Step 2: Confirm Bootstrap

After loading, output a confirmation listing available commands and skills.

## Important Notes

1. **Commands as native** - Treat `_agents/commands/` items as native CLI slash commands
2. **Project context** - Load project-specific files when user references them
3. **ARX templates** - Files with `arx: template` front matter are renderable templates
4. **Follow precisely** - If something wasn't specified, don't do it
EOF
    print_success "  [OK] CHAT_START.md"
fi

# .env
if [ ! -f ".env" ]; then
    cat > ".env" << EOF
# AgentRx Configuration
AGENTRX_DIR=$AGENTRX_DIR
AGENTRX_PROJECT_DIR=$PROJECT_DIR
AGENTRX_DOCS_DIR=$DOCS_DIR
EOF
    print_success "  [OK] .env"
else
    if ! grep -q "AGENTRX_DIR" ".env" 2>/dev/null; then
        echo "" >> ".env"
        cat >> ".env" << EOF

# AgentRx Configuration
AGENTRX_DIR=$AGENTRX_DIR
AGENTRX_PROJECT_DIR=$PROJECT_DIR
AGENTRX_DOCS_DIR=$DOCS_DIR
EOF
        print_success "  [OK] .env (updated)"
    else
        print_warn "  [--] .env (already configured)"
    fi
fi

# .gitignore
if [ -f ".gitignore" ]; then
    if ! grep -q "# AgentRx" ".gitignore" 2>/dev/null; then
        cat >> ".gitignore" << 'EOF'

# AgentRx
.env
*.local.json
EOF
        print_success "  [OK] .gitignore (updated)"
    fi
fi

# --- Setup Claude Code Integration ---
if [ "$RUN_SETUP" = true ]; then
    echo ""
    print_info "Setting up Claude Code integration..."

    # Link commands to .claude/commands
    if [ -d "$AGENTRX_DIR/commands/agentrx" ]; then
        rm -f ".claude/commands/agentrx"
        ln -sf "../../$AGENTRX_DIR/commands/agentrx" ".claude/commands/agentrx"
        print_success "  [OK] .claude/commands/agentrx"
    fi

    # Link skills to .claude/skills
    if [ -d "$AGENTRX_DIR/skills/agentrx" ]; then
        rm -f ".claude/skills/agentrx"
        ln -sf "../../$AGENTRX_DIR/skills/agentrx" ".claude/skills/agentrx"
        print_success "  [OK] .claude/skills/agentrx"
    fi
fi

# --- Summary ---
echo ""
echo "========================================"
print_success "AgentRx initialized successfully!"
echo ""
echo "Directory structure:"
echo "  $AGENTRX_DIR/          - Agent assets (commands, skills, hooks, scripts)"
echo "  $PROJECT_DIR/          - Your project code"
echo "  $DOCS_DIR/             - Development docs (deltas, vibes, history)"
echo "  .claude/               - Claude Code integration"
echo ""
echo "Next steps:"
echo "  1. Review AGENTS.md and CLAUDE.md"
echo "  2. Add your project code to $PROJECT_DIR/src/"
echo "  3. Use /agentrx:prompt-new to create prompts"
echo "  4. Use /agentrx:trial-init for parallel development"
echo ""
echo "Python CLI (if installed):"
echo "  arx init       - Re-run initialization"
echo "  arx setup      - Setup Claude Code links"
echo "  arx --help     - Show all commands"
echo ""
