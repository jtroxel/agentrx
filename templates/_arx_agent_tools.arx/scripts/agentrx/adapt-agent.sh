#!/usr/bin/env bash
# adapt-agent.sh — Bootstrap a coding agent to recognise the AgentRx workspace
#
# After `arx init` has laid down the _agents/ directory, this script injects
# the *minimum* pointer into whatever file the target coding agent reads by
# default so the agent can discover the full ARX tools directory.
#
# Supported agents:
#   claude-code       → CLAUDE.md
#   github-copilot    → .github/copilot-instructions.md
#   cursor            → .cursorrules  +  .cursor/rules/arx.mdc
#   all               → all of the above
#
# Usage:
#   adapt-agent.sh <agent|all> [--project-root DIR]
#
# The block is idempotent — re-running replaces only the managed section.

set -euo pipefail

VERSION="1.0.0"

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
    GREEN=$'\033[0;32m'; BLUE=$'\033[0;34m'; YELLOW=$'\033[1;33m'
    RED=$'\033[0;31m'; NC=$'\033[0m'
else
    GREEN=''; BLUE=''; YELLOW=''; RED=''; NC=''
fi
ok()   { echo "${GREEN}$*${NC}"; }
info() { echo "${BLUE}$*${NC}"; }
warn() { echo "${YELLOW}$*${NC}"; }
err()  { echo "${RED}$*${NC}" >&2; }

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------
AGENT=""
PROJECT_ROOT=""

usage() {
    cat <<EOF
adapt-agent.sh v$VERSION — Bootstrap a coding agent for AgentRx

Usage: adapt-agent.sh <agent|all> [--project-root DIR]

Agents:
  claude-code       Append to CLAUDE.md
  github-copilot    Append to .github/copilot-instructions.md
  cursor            Append to .cursorrules + .cursor/rules/arx.mdc
  all               All of the above

Options:
  --project-root DIR   Workspace root (default: cwd)
  -h, --help           Show this help
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)       usage ;;
        --project-root)  PROJECT_ROOT="$2"; shift 2 ;;
        -*)              err "Unknown option: $1"; exit 1 ;;
        *)
            if [[ -z "$AGENT" ]]; then
                AGENT="$1"
            else
                err "Unexpected argument: $1"; exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$AGENT" ]]; then
    err "Missing required argument: <agent|all>"
    echo "Run with --help for usage."
    exit 1
fi

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

# Validate _agents exists
if [[ ! -d "$PROJECT_ROOT/_agents" ]]; then
    err "_agents/ directory not found in $PROJECT_ROOT"
    echo "Run 'arx init' first."
    exit 1
fi

# ---------------------------------------------------------------------------
# Marker helpers — idempotent insert / replace
# ---------------------------------------------------------------------------
ARX_BEGIN="<!-- arx:begin -->"
ARX_END="<!-- arx:end -->"

# inject_block FILE CONTENT
#   If the file doesn't exist      → create it with CONTENT wrapped in markers.
#   If it exists WITH markers      → replace the marker block.
#   If it exists WITHOUT markers   → append the block.
inject_block() {
    local file="$1" content="$2"
    local block
    block="$(printf '%s\n%s\n%s' "$ARX_BEGIN" "$content" "$ARX_END")"

    mkdir -p "$(dirname "$file")"

    if [[ ! -f "$file" ]]; then
        printf '%s\n' "$block" > "$file"
        ok "  [created] $file"
    elif grep -qF "$ARX_BEGIN" "$file"; then
        # Replace existing block — write new block to a temp file, then use
        # awk + system("cat ...") to splice it in (avoids awk -v multiline bug).
        local tmp="$file.arx_tmp"
        local blk_file="$file.arx_blk"
        printf '%s\n' "$block" > "$blk_file"
        BLK_FILE="$blk_file" awk '
            /<!-- arx:begin -->/ { system("cat " ENVIRON["BLK_FILE"]); skip=1; next }
            /<!-- arx:end -->/   { skip=0; next }
            !skip { print }
        ' "$file" > "$tmp"
        mv "$tmp" "$file"
        rm -f "$blk_file"
        ok "  [updated] $file"
    else
        printf '\n%s\n' "$block" >> "$file"
        ok "  [appended] $file"
    fi
}

# ---------------------------------------------------------------------------
# Bootstrap content — kept deliberately minimal
# ---------------------------------------------------------------------------
BOOTSTRAP_CORE='## AgentRx Workspace

This workspace uses **AgentRx** for structured AI-assisted development.

### On every session start — read these files:

```
AGENTS.md
CHAT_START.md
_agents/commands/agentrx/QUICKREF.md
```

### Directory map

| Path | Purpose |
|------|---------|
| `_agents/commands/agentrx/` | Slash-command definitions (treat as native commands prefixed `/arx:`) |
| `_agents/skills/agentrx/` | Skill / reference documents |
| `_agents/scripts/agentrx/` | Implementation shell scripts |
| `_agents/hooks/agentrx/` | Lifecycle hooks |

### Key commands

| Command | Description |
|---------|-------------|
| `/arx:init` | Initialize project structure |
| `/arx:prompt-new` | Create a prompt file |
| `/arx:adapt-workspace <agent>` | Refresh these instructions |

> Full command list: `_agents/commands/agentrx/QUICKREF.md`'

# ---------------------------------------------------------------------------
# Per-agent adapters
# ---------------------------------------------------------------------------

adapt_claude_code() {
    info "Adapting for Claude Code → CLAUDE.md"
    local file="$PROJECT_ROOT/CLAUDE.md"

    # Claude-specific preamble wraps the shared core
    local content
    content="$(cat <<'BLOCK'
## AgentRx Workspace

This workspace uses **AgentRx** for structured AI-assisted development.

### On every session start — read these files:

```
AGENTS.md
CHAT_START.md
_agents/commands/agentrx/QUICKREF.md
```

### Directory map

| Path | Purpose |
|------|---------|
| `_agents/commands/agentrx/` | Slash-command definitions (also linked to `.claude/commands/`) |
| `_agents/skills/agentrx/` | Skill / reference documents |
| `_agents/scripts/agentrx/` | Implementation shell scripts |
| `_agents/hooks/agentrx/` | Lifecycle hooks |

### Key commands

| Command | Description |
|---------|-------------|
| `/arx:init` | Initialize project structure |
| `/arx:prompt-new` | Create a prompt file |
| `/arx:adapt-workspace <agent>` | Refresh these instructions |

> Full command list: `_agents/commands/agentrx/QUICKREF.md`
BLOCK
)"

    inject_block "$file" "$content"
}

adapt_github_copilot() {
    info "Adapting for GitHub Copilot → .github/copilot-instructions.md"
    local file="$PROJECT_ROOT/.github/copilot-instructions.md"

    local content
    content="$(cat <<'BLOCK'
## AgentRx Workspace

This workspace uses **AgentRx** for structured AI-assisted development.

### On every session start — read these files:

```
AGENTS.md
CHAT_START.md
_agents/commands/agentrx/QUICKREF.md
```

### Directory map

| Path | Purpose |
|------|---------|
| `_agents/commands/agentrx/` | Slash-command definitions (treat as native commands prefixed `/arx:`) |
| `_agents/skills/agentrx/` | Skill / reference documents |
| `_agents/scripts/agentrx/` | Implementation shell scripts |
| `_agents/hooks/agentrx/` | Lifecycle hooks |

### Key commands

| Command | Description |
|---------|-------------|
| `/arx:init` | Initialize project structure |
| `/arx:prompt-new` | Create a prompt file |
| `/arx:adapt-workspace <agent>` | Refresh these instructions |

> Full command list: `_agents/commands/agentrx/QUICKREF.md`
BLOCK
)"

    inject_block "$file" "$content"
}

adapt_cursor() {
    info "Adapting for Cursor → .cursorrules + .cursor/rules/arx.mdc"

    # --- Legacy .cursorrules ---
    local file="$PROJECT_ROOT/.cursorrules"
    local content
    content="$(cat <<'BLOCK'
# AgentRx Workspace

This workspace uses AgentRx for structured AI-assisted development.

## On every session start — read these files:

1. `AGENTS.md`
2. `CHAT_START.md`
3. `_agents/commands/agentrx/QUICKREF.md`

## Directory map

- `_agents/commands/agentrx/` — Slash-command definitions (treat as native `/arx:` commands)
- `_agents/skills/agentrx/` — Skill / reference documents
- `_agents/scripts/agentrx/` — Implementation shell scripts
- `_agents/hooks/agentrx/` — Lifecycle hooks

## Key commands

- `/arx:init` — Initialize project structure
- `/arx:prompt-new` — Create a prompt file
- `/arx:adapt-workspace <agent>` — Refresh these instructions

Full command list: `_agents/commands/agentrx/QUICKREF.md`
BLOCK
)"
    inject_block "$file" "$content"

    # --- New-format .cursor/rules/arx.mdc ---
    local mdc_file="$PROJECT_ROOT/.cursor/rules/arx.mdc"
    mkdir -p "$PROJECT_ROOT/.cursor/rules"

    local mdc_content
    mdc_content="$(cat <<'BLOCK'
---
description: "AgentRx workspace bootstrap"
globs: ["**/*"]
alwaysApply: true
---

# AgentRx Workspace

This workspace uses AgentRx for structured AI-assisted development.

## On every session start — read these files:

1. `AGENTS.md`
2. `CHAT_START.md`
3. `_agents/commands/agentrx/QUICKREF.md`

## Directory map

- `_agents/commands/agentrx/` — Slash-command definitions (treat as native `/arx:` commands)
- `_agents/skills/agentrx/` — Skill / reference documents
- `_agents/scripts/agentrx/` — Implementation shell scripts
- `_agents/hooks/agentrx/` — Lifecycle hooks

## Key commands

- `/arx:init` — Initialize project structure
- `/arx:prompt-new` — Create a prompt file
- `/arx:adapt-workspace <agent>` — Refresh these instructions

Full command list: `_agents/commands/agentrx/QUICKREF.md`
BLOCK
)"
    inject_block "$mdc_file" "$mdc_content"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo ""
echo "adapt-agent.sh v$VERSION"
echo "========================================"
echo "  Project root: $PROJECT_ROOT"
echo "  Agent:        $AGENT"
echo ""

case "$AGENT" in
    claude-code|claude)
        adapt_claude_code
        ;;
    github-copilot|copilot)
        adapt_github_copilot
        ;;
    cursor)
        adapt_cursor
        ;;
    all)
        adapt_claude_code
        echo ""
        adapt_github_copilot
        echo ""
        adapt_cursor
        ;;
    *)
        err "Unknown agent: $AGENT"
        echo "Supported: claude-code, github-copilot, cursor, all"
        exit 1
        ;;
esac

echo ""
ok "Done. The agent will now discover _agents/ on next session start."
echo ""
