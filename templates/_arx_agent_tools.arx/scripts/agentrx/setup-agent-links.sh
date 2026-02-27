#!/bin/bash
# setup-agent-links.sh (formerly setup-claude-links.sh)
# Creates integration files for AI coding agents
# Supports: Claude Code, Cursor, OpenCode

set -e

VERSION="2.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find project root (look for _agents or .claude directory)
find_project_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/_agents" ] || [ -d "$dir/.claude" ]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    echo ""
    return 1
}

PROJECT_ROOT="${PROJECT_ROOT:-$(find_project_root "$SCRIPT_DIR")}"
if [ -z "$PROJECT_ROOT" ]; then
    PROJECT_ROOT="$(pwd)"
fi

AGENTS_DIR="$PROJECT_ROOT/_agents"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

# Colors
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m'
else
    GREEN='' BLUE='' YELLOW='' RED='' NC=''
fi

print_success() { echo -e "${GREEN}$1${NC}"; }
print_info() { echo -e "${BLUE}$1${NC}"; }
print_warn() { echo -e "${YELLOW}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }

usage() {
    cat << EOF
AgentRx Agent Setup v$VERSION

Usage: setup-agent-links.sh [OPTIONS]

Creates integration files for AI coding agents.

Supported Providers:
  claude    Claude Code (.claude/ directory with symlinks)
  cursor    Cursor IDE (.cursorrules and .cursor/rules/)
  opencode  OpenCode (AGENTS.md wrapper file)

Options:
  --provider PROVIDER   Set provider: claude, cursor, opencode, or all (default: all)
  --project-root DIR    Set project root directory
  --clean               Remove existing links/files before creating new ones
  -v, --verbose         Show detailed output
  -h, --help            Show this help message

Environment:
  PROJECT_ROOT    Override project root detection

Examples:
  setup-agent-links.sh                    # Setup all providers
  setup-agent-links.sh --provider claude  # Setup Claude Code only
  setup-agent-links.sh --provider cursor  # Setup Cursor only
  setup-agent-links.sh --clean            # Clean and recreate all
EOF
    exit 0
}

CLEAN=false
VERBOSE=false
PROVIDER="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --provider)
            PROVIDER="$2"
            if [[ ! "$PROVIDER" =~ ^(claude|cursor|opencode|all)$ ]]; then
                print_error "Invalid provider: $PROVIDER"
                echo "Valid providers: claude, cursor, opencode, all"
                exit 1
            fi
            shift 2
            ;;
        --project-root)
            PROJECT_ROOT="$2"
            AGENTS_DIR="$PROJECT_ROOT/_agents"
            CLAUDE_DIR="$PROJECT_ROOT/.claude"
            shift 2
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
echo "AgentRx Agent Setup v$VERSION"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo "Agents dir:   $AGENTS_DIR"
echo "Provider:     $PROVIDER"
echo ""

# Verify _agents exists
if [ ! -d "$AGENTS_DIR" ]; then
    print_error "Error: _agents directory not found at $AGENTS_DIR"
    echo "Run 'arx init' or the init.sh script first."
    exit 1
fi

# ============================================================================
# CLAUDE CODE SETUP
# ============================================================================
setup_claude() {
    print_info "Setting up Claude Code integration..."
    echo ""

    # Create .claude directory
    mkdir -p "$CLAUDE_DIR/commands"
    mkdir -p "$CLAUDE_DIR/skills"

    # Clean existing links if requested
    if [ "$CLEAN" = true ]; then
        print_info "Cleaning existing Claude links..."
        find "$CLAUDE_DIR" -type l -delete 2>/dev/null || true
    fi

    # --- Link Commands ---
    print_info "Setting up command links..."

    COMMANDS_DIR="$AGENTS_DIR/commands"
    if [ -d "$COMMANDS_DIR" ]; then
        for namespace_dir in "$COMMANDS_DIR"/*/; do
            if [ -d "$namespace_dir" ]; then
                namespace=$(basename "$namespace_dir")
                target_link="$CLAUDE_DIR/commands/$namespace"
                rm -rf "$target_link"
                rel_path=$(python3 -c "import os.path; print(os.path.relpath('$namespace_dir', '$CLAUDE_DIR/commands'))" 2>/dev/null || echo "../../_agents/commands/$namespace")
                ln -sf "$rel_path" "$target_link"
                print_success "  [OK] commands/$namespace"

                if [ "$VERBOSE" = true ]; then
                    find "$namespace_dir" -name "*.md" -type f | while read -r cmd_file; do
                        filename=$(basename "$cmd_file" .md)
                        case "$filename" in
                            README|SUMMARY|COMMAND_*|GETTING-STARTED|QUICKREF|*USAGE*|*INDEX*)
                                continue
                                ;;
                        esac
                        echo "       /$namespace:$filename"
                    done
                fi
            fi
        done
    fi

    # --- Link Skills ---
    print_info "Setting up skill links..."

    SKILLS_DIR="$AGENTS_DIR/skills"
    if [ -d "$SKILLS_DIR" ]; then
        for namespace_dir in "$SKILLS_DIR"/*/; do
            if [ -d "$namespace_dir" ]; then
                namespace=$(basename "$namespace_dir")
                target_link="$CLAUDE_DIR/skills/$namespace"
                rm -rf "$target_link"
                rel_path=$(python3 -c "import os.path; print(os.path.relpath('$namespace_dir', '$CLAUDE_DIR/skills'))" 2>/dev/null || echo "../../_agents/skills/$namespace")
                ln -sf "$rel_path" "$target_link"
                print_success "  [OK] skills/$namespace"

                if [ "$VERBOSE" = true ]; then
                    find "$namespace_dir" -name "*.md" -type f | while read -r skill_file; do
                        filename=$(basename "$skill_file" .md)
                        echo "       $namespace:$filename"
                    done
                fi
            fi
        done
    fi

    # --- Link Hooks ---
    if [ -d "$AGENTS_DIR/hooks" ]; then
        print_info "Setting up hooks link..."
        hooks_link="$CLAUDE_DIR/hooks"
        rm -rf "$hooks_link"
        rel_path=$(python3 -c "import os.path; print(os.path.relpath('$AGENTS_DIR/hooks', '$CLAUDE_DIR'))" 2>/dev/null || echo "../_agents/hooks")
        ln -sf "$rel_path" "$hooks_link"
        print_success "  [OK] hooks"
    fi

    # --- Link Settings ---
    if [ -f "$AGENTS_DIR/settings.local.json" ]; then
        print_info "Setting up settings link..."
        settings_link="$CLAUDE_DIR/settings.local.json"
        rm -f "$settings_link"
        rel_path=$(python3 -c "import os.path; print(os.path.relpath('$AGENTS_DIR/settings.local.json', '$CLAUDE_DIR'))" 2>/dev/null || echo "../_agents/settings.local.json")
        ln -sf "$rel_path" "$settings_link"
        print_success "  [OK] settings.local.json"
    fi

    print_success "Claude Code setup complete!"
}

# ============================================================================
# CURSOR SETUP
# ============================================================================
setup_cursor() {
    print_info "Setting up Cursor IDE integration..."
    echo ""

    CURSOR_DIR="$PROJECT_ROOT/.cursor"
    CURSOR_RULES_DIR="$CURSOR_DIR/rules"

    # Clean existing files if requested
    if [ "$CLEAN" = true ]; then
        print_info "Cleaning existing Cursor files..."
        rm -f "$PROJECT_ROOT/.cursorrules" 2>/dev/null || true
        rm -rf "$CURSOR_RULES_DIR" 2>/dev/null || true
    fi

    # Create .cursor/rules directory
    mkdir -p "$CURSOR_RULES_DIR"

    # --- Create .cursorrules wrapper file (legacy support) ---
    print_info "Creating .cursorrules wrapper file..."
    cat > "$PROJECT_ROOT/.cursorrules" << 'CURSORRULES_EOF'
# Cursor Rules - AgentRx Integration
# This file wraps the AgentRx agent configuration.
# For full agent instructions, see: _agents/AGENTS.md

## Important Files
Read the following files at the start of each session:
1. `_agents/AGENTS.md` - Main agent instructions
2. `_agents/CLAUDE.md` - Additional guidance (if exists)

## Quick Reference
- Commands are in `_agents/commands/`
- Skills are in `_agents/skills/`
- Hooks are in `_agents/hooks/`

## Instructions
Follow all guidance in `_agents/AGENTS.md`. That file contains the primary
instructions for AI agents working with this codebase.
CURSORRULES_EOF
    print_success "  [OK] .cursorrules"

    # --- Create .cursor/rules/agents.mdc (new format) ---
    print_info "Creating .cursor/rules/agents.mdc..."
    cat > "$CURSOR_RULES_DIR/agents.mdc" << 'MDC_EOF'
---
description: "AgentRx Agent Configuration"
globs: ["**/*"]
alwaysApply: true
---

# AgentRx Agent Configuration

This project uses AgentRx for AI agent configuration.

## Required Reading

At the start of each session, read:
1. `_agents/AGENTS.md` - Primary agent instructions
2. `_agents/CLAUDE.md` - Additional Claude-specific guidance

## Project Structure

- `_agents/commands/` - Slash commands (e.g., /arx:init)
- `_agents/skills/` - Reusable skills and templates
- `_agents/hooks/` - Event hooks for agent actions
- `_agents/scripts/` - Shell scripts for automation

## Key Principles

Follow all guidance in `_agents/AGENTS.md`. The instructions there take
precedence for this project.
MDC_EOF
    print_success "  [OK] .cursor/rules/agents.mdc"

    print_success "Cursor setup complete!"
}

# ============================================================================
# OPENCODE SETUP
# ============================================================================
setup_opencode() {
    print_info "Setting up OpenCode integration..."
    echo ""

    # Clean existing files if requested
    if [ "$CLEAN" = true ]; then
        print_info "Cleaning existing OpenCode files..."
        # Don't delete AGENTS.md if it's the main file in _agents
        if [ -f "$PROJECT_ROOT/AGENTS.md" ] && [ ! "$PROJECT_ROOT/AGENTS.md" -ef "$AGENTS_DIR/AGENTS.md" ]; then
            rm -f "$PROJECT_ROOT/AGENTS.md" 2>/dev/null || true
        fi
    fi

    # --- Create AGENTS.md wrapper in project root ---
    # OpenCode reads AGENTS.md from project root by default
    # Create a wrapper that references _agents/AGENTS.md

    if [ -f "$PROJECT_ROOT/AGENTS.md" ]; then
        # Check if it's already a wrapper or the actual file
        if grep -q "AgentRx Wrapper" "$PROJECT_ROOT/AGENTS.md" 2>/dev/null; then
            print_info "AGENTS.md wrapper already exists, updating..."
        else
            print_warn "AGENTS.md already exists. Creating AGENTS.md.agentrx instead."
            print_warn "You may want to manually merge or replace."
            PROJECT_AGENTS_FILE="$PROJECT_ROOT/AGENTS.md.agentrx"
        fi
    fi

    PROJECT_AGENTS_FILE="${PROJECT_AGENTS_FILE:-$PROJECT_ROOT/AGENTS.md}"

    print_info "Creating AGENTS.md wrapper file..."
    cat > "$PROJECT_AGENTS_FILE" << 'AGENTS_EOF'
<!-- AgentRx Wrapper - Auto-generated by setup-agent-links.sh -->
# Agent Instructions

This project uses AgentRx for AI agent configuration.

## Required Reading

**IMPORTANT**: Read the full agent instructions from the following file:

→ **`_agents/AGENTS.md`** - Primary agent instructions and project context

Additional context files:
- `_agents/CLAUDE.md` - Claude-specific guidance
- `_agents/project_root_files/CONTEXT_DOCUMENTS_INDEX.md` - Context document index

## Quick Reference

| Resource | Location |
|----------|----------|
| Commands | `_agents/commands/` |
| Skills | `_agents/skills/` |
| Hooks | `_agents/hooks/` |
| Scripts | `_agents/scripts/` |

## Instructions

All agent behavior should follow the guidance in `_agents/AGENTS.md`.
That file contains the authoritative instructions for this project.
AGENTS_EOF
    print_success "  [OK] $(basename "$PROJECT_AGENTS_FILE")"

    # --- Create opencode.json if it doesn't exist ---
    OPENCODE_CONFIG="$PROJECT_ROOT/opencode.json"
    if [ ! -f "$OPENCODE_CONFIG" ]; then
        print_info "Creating opencode.json configuration..."
        cat > "$OPENCODE_CONFIG" << 'OPENCODE_EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "_agents/AGENTS.md",
    "_agents/CLAUDE.md"
  ]
}
OPENCODE_EOF
        print_success "  [OK] opencode.json"
    else
        print_info "opencode.json already exists, skipping..."
    fi

    print_success "OpenCode setup complete!"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Run setup based on provider
case "$PROVIDER" in
    claude)
        setup_claude
        ;;
    cursor)
        setup_cursor
        ;;
    opencode)
        setup_opencode
        ;;
    all)
        setup_claude
        echo ""
        setup_cursor
        echo ""
        setup_opencode
        ;;
esac

# --- Summary ---
echo ""
echo "========================================"
print_success "Setup complete for: $PROVIDER"
echo ""

# List available commands (only if Claude was set up)
if [ "$PROVIDER" = "claude" ] || [ "$PROVIDER" = "all" ]; then
    echo "Available commands:"
    if [ -d "$CLAUDE_DIR/commands" ]; then
        for namespace_dir in "$CLAUDE_DIR/commands"/*/; do
            if [ -d "$namespace_dir" ]; then
                namespace=$(basename "$namespace_dir")
                find "$namespace_dir" -name "*.md" -type f 2>/dev/null | while read -r cmd_file; do
                    filename=$(basename "$cmd_file" .md)
                    case "$filename" in
                        README|SUMMARY|COMMAND_*|GETTING-STARTED|QUICKREF|*USAGE*|*INDEX*)
                            continue
                            ;;
                    esac
                    echo "  /$namespace:$filename"
                done
            fi
        done
    fi

    echo ""
    echo "Available skills:"
    if [ -d "$CLAUDE_DIR/skills" ]; then
        for namespace_dir in "$CLAUDE_DIR/skills"/*/; do
            if [ -d "$namespace_dir" ]; then
                namespace=$(basename "$namespace_dir")
                find "$namespace_dir" -name "*.md" -type f 2>/dev/null | while read -r skill_file; do
                    filename=$(basename "$skill_file" .md)
                    echo "  $namespace:$filename"
                done
            fi
        done
    fi
    echo ""
fi

echo "Provider-specific files created:"
case "$PROVIDER" in
    claude)
        echo "  - .claude/ directory with symlinks"
        ;;
    cursor)
        echo "  - .cursorrules (legacy format)"
        echo "  - .cursor/rules/agents.mdc (new format)"
        ;;
    opencode)
        echo "  - AGENTS.md wrapper file"
        echo "  - opencode.json configuration"
        ;;
    all)
        echo "  - .claude/ directory with symlinks"
        echo "  - .cursorrules (legacy format)"
        echo "  - .cursor/rules/agents.mdc (new format)"
        echo "  - AGENTS.md wrapper file"
        echo "  - opencode.json configuration"
        ;;
esac

echo ""
echo "To verify:"
case "$PROVIDER" in
    claude)
        echo "  ls -la $CLAUDE_DIR/"
        ;;
    cursor)
        echo "  cat $PROJECT_ROOT/.cursorrules"
        echo "  cat $PROJECT_ROOT/.cursor/rules/agents.mdc"
        ;;
    opencode)
        echo "  cat $PROJECT_ROOT/AGENTS.md"
        echo "  cat $PROJECT_ROOT/opencode.json"
        ;;
    all)
        echo "  ls -la $CLAUDE_DIR/"
        echo "  cat $PROJECT_ROOT/.cursorrules"
        echo "  cat $PROJECT_ROOT/AGENTS.md"
        ;;
esac
echo ""
