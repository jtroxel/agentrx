#!/bin/bash
# setup-claude-links.sh
# Creates symbolic links from .claude/ to _agents/ structure
# for Claude Code integration

set -e

VERSION="1.0.0"
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
AgentRx Claude Code Setup v$VERSION

Usage: setup-claude-links.sh [OPTIONS]

Creates symbolic links in .claude/ directory for Claude Code integration.

Options:
  --project-root DIR    Set project root directory
  --clean               Remove existing links before creating new ones
  -v, --verbose         Show detailed output
  -h, --help            Show this help message

Environment:
  PROJECT_ROOT    Override project root detection
EOF
    exit 0
}

CLEAN=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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
echo "AgentRx Claude Code Setup v$VERSION"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo "Agents dir:   $AGENTS_DIR"
echo "Claude dir:   $CLAUDE_DIR"
echo ""

# Verify _agents exists
if [ ! -d "$AGENTS_DIR" ]; then
    print_error "Error: _agents directory not found at $AGENTS_DIR"
    echo "Run 'arx init' or the init.sh script first."
    exit 1
fi

# Create .claude directory
mkdir -p "$CLAUDE_DIR/commands"
mkdir -p "$CLAUDE_DIR/skills"

# Clean existing links if requested
if [ "$CLEAN" = true ]; then
    print_info "Cleaning existing links..."
    find "$CLAUDE_DIR" -type l -delete 2>/dev/null || true
fi

# --- Link Commands ---
print_info "Setting up command links..."

COMMANDS_DIR="$AGENTS_DIR/commands"
if [ -d "$COMMANDS_DIR" ]; then
    # Find all namespace directories (e.g., agentrx, project-name)
    for namespace_dir in "$COMMANDS_DIR"/*/; do
        if [ -d "$namespace_dir" ]; then
            namespace=$(basename "$namespace_dir")
            target_link="$CLAUDE_DIR/commands/$namespace"

            # Remove existing link/dir
            rm -rf "$target_link"

            # Create relative symlink
            rel_path=$(python3 -c "import os.path; print(os.path.relpath('$namespace_dir', '$CLAUDE_DIR/commands'))" 2>/dev/null || echo "../../_agents/commands/$namespace")
            ln -sf "$rel_path" "$target_link"
            print_success "  [OK] commands/$namespace"

            if [ "$VERBOSE" = true ]; then
                # List commands in namespace
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

# --- Summary ---
echo ""
echo "========================================"
print_success "Setup complete!"
echo ""

# List available commands
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
echo "To verify: ls -la $CLAUDE_DIR/"
echo ""
