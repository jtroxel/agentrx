#!/bin/bash
# setup-claude-links.sh
# Creates symbolic links from .claude/ to _agents/ structure
# and initializes CLAUDE.md with context document references

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
AGENTS_DIR="$PROJECT_ROOT/_agents"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

echo "=== AgentRX Claude Code Setup ==="
echo "Project root: $PROJECT_ROOT"
echo "Agents dir: $AGENTS_DIR"
echo "Claude dir: $CLAUDE_DIR"
echo ""

# Create .claude directory if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# --- 1. Link commands as skills ---
# Claude Code expects skills in .claude/skills/<name>/SKILL.md
# We link _agents/commands/<namespace>/<command>.md files

COMMANDS_DIR="$AGENTS_DIR/commands"
SKILLS_DIR="$CLAUDE_DIR/skills"

if [ -d "$COMMANDS_DIR" ]; then
    echo "Setting up skills from commands..."
    mkdir -p "$SKILLS_DIR"

    # Find all .md files in commands (excluding README, SUMMARY, etc.)
    find "$COMMANDS_DIR" -name "*.md" -type f | while read -r cmd_file; do
        filename=$(basename "$cmd_file")

        # Skip documentation files
        case "$filename" in
            README.md|SUMMARY.md|COMMAND_SUMMARY.md|GETTING-STARTED.md|QUICKREF.md|*USAGE*.md)
                echo "  Skipping doc: $filename"
                continue
                ;;
        esac

        # Extract namespace and command name
        # Handles subdirectories like commands/agentrx/prompt-new.md -> agentrx:prompt-new
        # Or nested like commands/agentrx/trial/work.md -> agentrx:trial-work
        rel_path="${cmd_file#$COMMANDS_DIR/}"
        namespace_path=$(dirname "$rel_path")
        cmd_name="${filename%.md}"

        # Create skill name with : separator for namespace
        if [ "$namespace_path" != "." ]; then
            # Get the top-level namespace (first directory)
            top_namespace=$(echo "$namespace_path" | cut -d'/' -f1)
            # Get any sub-namespace path (remaining directories)
            sub_namespace=$(echo "$namespace_path" | cut -d'/' -f2- -s)

            if [ -n "$sub_namespace" ]; then
                # Nested: agentrx/trial/work.md -> agentrx:trial-work
                # Replace / with - in sub-namespace
                sub_prefix=$(echo "$sub_namespace" | tr '/' '-')
                skill_name="${top_namespace}:${sub_prefix}-${cmd_name}"
            else
                # Simple: agentrx/prompt-new.md -> agentrx:prompt-new
                skill_name="${top_namespace}:${cmd_name}"
            fi
        else
            # No namespace, just the command name
            skill_name="$cmd_name"
        fi

        skill_dir="$SKILLS_DIR/$skill_name"
        skill_file="$skill_dir/SKILL.md"

        # Create skill directory
        mkdir -p "$skill_dir"

        # Create symlink (remove existing if present)
        if [ -L "$skill_file" ]; then
            rm "$skill_file"
        elif [ -f "$skill_file" ]; then
            echo "  Warning: $skill_file exists and is not a symlink, skipping"
            continue
        fi

        # Create relative symlink
        rel_target=$(python3 -c "import os.path; print(os.path.relpath('$cmd_file', '$skill_dir'))")
        ln -s "$rel_target" "$skill_file"
        echo "  Linked: /$skill_name -> $rel_path"
    done
fi

# --- 2. Link existing skills directory ---
# Handles both flat skills (_agents/skills/my-skill/) and
# namespaced skills (_agents/skills/agentrx/trial-work/)
if [ -d "$AGENTS_DIR/skills" ]; then
    echo ""
    echo "Linking skills directory..."

    # Find skill directories (those containing SKILL.md)
    find "$AGENTS_DIR/skills" -name "SKILL.md" -type f | while read -r skill_file; do
        skill_src=$(dirname "$skill_file")
        rel_path="${skill_src#$AGENTS_DIR/skills/}"

        # Check if this is a namespaced skill (has a parent directory)
        parent_dir=$(dirname "$rel_path")
        skill_base=$(basename "$rel_path")

        if [ "$parent_dir" != "." ]; then
            # Namespaced: skills/agentrx/trial-work -> agentrx:trial-work
            skill_name="${parent_dir}:${skill_base}"
        else
            # Flat: skills/my-skill -> my-skill
            skill_name="$skill_base"
        fi

        skill_dst="$SKILLS_DIR/$skill_name"

        if [ -L "$skill_dst" ]; then
            rm "$skill_dst"
        elif [ -d "$skill_dst" ]; then
            echo "  Warning: $skill_dst exists, skipping"
            continue
        fi

        rel_target=$(python3 -c "import os.path; print(os.path.relpath('$skill_src', '$SKILLS_DIR'))")
        ln -s "$rel_target" "$skill_dst"
        echo "  Linked skill: /$skill_name"
    done
fi

# --- 3. Link hooks directory ---
if [ -d "$AGENTS_DIR/hooks" ]; then
    echo ""
    echo "Linking hooks..."
    hooks_link="$CLAUDE_DIR/hooks"

    if [ -L "$hooks_link" ]; then
        rm "$hooks_link"
    elif [ -d "$hooks_link" ]; then
        echo "  Warning: $hooks_link exists and is not a symlink"
    else
        rel_target=$(python3 -c "import os.path; print(os.path.relpath('$AGENTS_DIR/hooks', '$CLAUDE_DIR'))")
        ln -s "$rel_target" "$hooks_link"
        echo "  Linked: .claude/hooks -> _agents/hooks"
    fi
fi

# --- 4. Link settings.local.json ---
if [ -f "$AGENTS_DIR/settings.local.json" ]; then
    echo ""
    echo "Linking settings..."
    settings_link="$CLAUDE_DIR/settings.local.json"

    if [ -L "$settings_link" ]; then
        rm "$settings_link"
    elif [ -f "$settings_link" ]; then
        echo "  Warning: $settings_link exists and is not a symlink"
    else
        rel_target=$(python3 -c "import os.path; print(os.path.relpath('$AGENTS_DIR/settings.local.json', '$CLAUDE_DIR'))")
        ln -s "$rel_target" "$settings_link"
        echo "  Linked: .claude/settings.local.json -> _agents/settings.local.json"
    fi
fi

# --- 5. Create/Update CLAUDE.md with context reference ---
echo ""
echo "Updating CLAUDE.md..."

CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"
AGENT_TOOLS_INDEX="$PROJECT_ROOT/AGENT_TOOLS_INDEX.md"
CONTEXT_INDEX="$PROJECT_ROOT/CONTEXT_DOCUMENTS_INDEX.md"
CONTEXT_SECTION="## Context Documents"

# Create AGENT_TOOLS_INDEX.md if it doesn't exist
if [ ! -f "$AGENT_TOOLS_INDEX" ]; then  
    echo "Creating AGENT_TOOLS_INDEX.md..."
    cat > "$AGENT_TOOLS_INDEX" << 'INDEXEOF'
# Agent Tools Index     

This file indexes key context documents for AI coding agents.

## Agent Instructions
- [AGENTS.md](./AGENTS.md) - Primary agent instructions
- [_agents/commands/](/_agents/commands/) - Available commands

## Commands Reference
| Command | Description |
|---------|-------------|
INDEXEOF

    # Add commands to the index
    if [ -d "$COMMANDS_DIR" ]; then
        find "$COMMANDS_DIR" -name "*.md" -type f | while read -r cmd_file; do
            filename=$(basename "$cmd_file")
            case "$filename" in
                README.md|SUMMARY.md|COMMAND_SUMMARY.md|GETTING-STARTED.md|QUICKREF.md|*USAGE*.md)
                    continue
                    ;;
            esac

            rel_path="${cmd_file#$PROJECT_ROOT/}"
            namespace=$(basename "$(dirname "$cmd_file")")
            cmd_name="${filename%.md}"

            # Extract description from frontmatter if present
            desc=$(grep -A1 "^description:" "$cmd_file" 2>/dev/null | tail -1 | sed 's/^description: *//' || echo "")
            if [ -z "$desc" ]; then
                desc="See file for details"
            fi

            echo "| \`/${namespace}:${cmd_name}\` | $desc |" >> "$CONTEXT_INDEX"
        done
    fi

    cat >> "$CONTEXT_INDEX" << 'INDEXEOF'

## Project Structure
```
_agents/           # Agent configurations
  commands/        # Slash command definitions
  skills/          # Skill definitions
  hooks/           # Event hooks
  scripts/         # Utility scripts
.claude/           # Claude Code integration (symlinks)
specs/             # Project specifications
```

## How to Update
Run `_agents/scripts/agentrx/setup-claude-links.sh` to refresh links and regenerate this index.
INDEXEOF
    echo "  Created: CONTEXT_DOCUMENTS_INDEX.md"
fi

# Check if CLAUDE.md needs the context section
if [ -f "$CLAUDE_MD" ]; then
    if ! grep -q "CONTEXT_DOCUMENTS_INDEX" "$CLAUDE_MD"; then
        echo "" >> "$CLAUDE_MD"
        echo "$CONTEXT_SECTION" >> "$CLAUDE_MD"
        echo "  Appended context section to CLAUDE.md"
    else
        echo "  CLAUDE.md already references CONTEXT_DOCUMENTS_INDEX.md"
    fi
else
    # Create minimal CLAUDE.md
    cat > "$CLAUDE_MD" << 'CLAUDEEOF'
# Claude Code Guidance

This file provides guidance to Claude Code when working with this repository.

## Primary Instructions
See [AGENTS.md](./AGENTS.md) for detailed agent instructions.

CLAUDEEOF
    echo "$CONTEXT_SECTION" >> "$CLAUDE_MD"
    echo "  Created: CLAUDE.md"
fi

# Create CONTEXT_DOCUMENTS_INDEX.md if it doesn't exist
if [ ! -f "$CONTEXT_INDEX" ]; then  
    echo "Creating CONTEXT_DOCUMENTS_INDEX.md..."
    cat > "$CONTEXT_INDEX" << 'INDEXEOF'
# Context Documents Index

This file indexes key context documents for the project.

## Project Specifications
- [specs/](/specs/) - Project specifications and requirements

## Architecture Decisions
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Architectural decisions and rationale

## Current Project Documentation
- docs, notes, and references relevant to the project

INDEXEOF
    echo "  Created: CONTEXT_DOCUMENTS_INDEX.md"
fi

# --- Summary ---
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Skills available (type / to see them):"
ls -1 "$SKILLS_DIR" 2>/dev/null | sed 's/^/  \//'
echo ""
echo "To verify: ls -la .claude/"
