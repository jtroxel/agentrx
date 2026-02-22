#!/usr/bin/env bash
# init-arx.sh — Interactive AgentRx project initializer
#
# Usage:
#   export AGENTRX_SOURCE=/path/to/agentrx-src
#   $AGENTRX_SOURCE/bin/init-arx.sh [--dry-run|-n] [project-dir]
#
# Activates the project's local venv, installs the arx CLI, prompts for
# directory layout (with full readline tab-completion and glob expansion),
# then calls `arx init` to do the actual file operations.
#
# Flags:
#   --dry-run, -n   Pass --dry-run to `arx init` (skip the interactive prompt)

set -euo pipefail

# ---------------------------------------------------------------------------
# Parse flags
# ---------------------------------------------------------------------------

DRY_FLAG=""
POSITIONAL_ARGS=()

for arg in "$@"; do
    case "$arg" in
        --dry-run|-n)
            DRY_FLAG="--dry-run"
            ;;
        *)
            POSITIONAL_ARGS+=("$arg")
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

if [[ -z "${AGENTRX_SOURCE:-}" ]]; then
    echo "Error: AGENTRX_SOURCE is not set." >&2
    echo "  export AGENTRX_SOURCE=/path/to/agentrx-src" >&2
    exit 1
fi

PROJECT_ROOT="${POSITIONAL_ARGS[0]:-.}"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

# ---------------------------------------------------------------------------
# Activate venv
# ---------------------------------------------------------------------------

VENV_ACTIVATED=false
for venv_candidate in "$PROJECT_ROOT/.venv" "$PROJECT_ROOT/venv"; do
    if [[ -f "$venv_candidate/bin/activate" ]]; then
        # shellcheck source=/dev/null
        source "$venv_candidate/bin/activate"
        VENV_ACTIVATED=true
        break
    fi
done

if [[ "$VENV_ACTIVATED" = false ]]; then
    echo "Warning: no .venv/ or venv/ found in $PROJECT_ROOT — using current Python." >&2
fi

# ---------------------------------------------------------------------------
# Install CLI
# ---------------------------------------------------------------------------

echo "Installing arx CLI..."
pip install -e "$AGENTRX_SOURCE/cli" --quiet

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# ANSI colours (suppress when not a terminal)
if [[ -t 1 ]]; then
    CYAN=$'\033[0;36m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
    CYAN=''; BOLD=''; RESET=''
fi

prompt_dir() {
    # prompt_dir VAR_NAME "label" "default"
    # Uses `read -e` for readline editing + tab-completion.
    # `read -i` (pre-fill) requires bash 4+; fall back gracefully on macOS bash 3.2.
    local var="$1" label="$2" default="$3"
    local value
    if [[ ${BASH_VERSINFO[0]} -ge 4 ]]; then
        # -e  : readline editing (tab-complete, history)
        # -i  : pre-fill with default so user can edit it
        read -e -r -i "$default" -p "  ${label} [${default}]: " value
    else
        read -e -r -p "  ${label} [${default}]: " value
    fi
    value="${value:-$default}"
    printf -v "$var" '%s' "$value"
}

# ---------------------------------------------------------------------------
# Interactive prompts
# ---------------------------------------------------------------------------

cd "$PROJECT_ROOT"

echo ""
echo "${BOLD}AgentRx Project Initialization${RESET}"
echo "========================================"
echo "  Project root : $PROJECT_ROOT"
echo "  ARX source   : $AGENTRX_SOURCE"
echo ""
echo "${CYAN}Directory layout${RESET} (Tab to complete paths, Enter to accept default):"
echo ""

prompt_dir  AGENTS_DIR   "Agent tools dir  (ARX_AGENT_TOOLS)" "_agents"
prompt_dir  TARGET_PROJ  "Target project   (ARX_TARGET_PROJ)" "_project"

# Derive docs defaults from target — strip any trailing slash first
DEFAULT_PROJ_DOCS="${TARGET_PROJ%/}/docs"
prompt_dir  PROJ_DOCS    "Project docs     (ARX_PROJ_DOCS   )" "$DEFAULT_PROJ_DOCS"

DEFAULT_WORK_DOCS="${PROJ_DOCS%/}/agentrx"
prompt_dir  WORK_DOCS    "Working docs     (ARX_WORK_DOCS   )" "$DEFAULT_WORK_DOCS"

echo ""
echo "${CYAN}How would you like to populate the 'agentrx' subdirectories under ./${BOLD}${AGENTS_DIR}${RESET}${CYAN}/?${RESET}"
read -r -n1 -p "  copy / link [C/l]: " mode_char
echo ""
# Lowercase without ${,,} (bash 3.2 compat)
case "$(echo "$mode_char" | tr '[:upper:]' '[:lower:]')" in
    l) ARX_MODE="link-arx" ;;
    *) ARX_MODE="copy" ;;
esac
echo "  → $ARX_MODE"

echo ""

# ---------------------------------------------------------------------------
# Dry-run preview?
# ---------------------------------------------------------------------------

if [[ -z "$DRY_FLAG" ]]; then
    if [[ ${BASH_VERSINFO[0]} -ge 4 ]]; then
        read -e -r -i "n" -p "  Preview with --dry-run first? [y/N]: " dry_ans
    else
        read -e -r -p "  Preview with --dry-run first? [y/N]: " dry_ans
    fi
    if [[ "$(echo "$dry_ans" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
        DRY_FLAG="--dry-run"
    fi
else
    echo "  --dry-run flag set — skipping live run."
fi

echo ""

# ---------------------------------------------------------------------------
# .gitignore
# ---------------------------------------------------------------------------

GITIGNORE="$PROJECT_ROOT/.gitignore"

add_to_gitignore() {
    local entry="$1"
    # Normalise: strip leading ./ for comparison
    local clean="${entry#./}"
    if [[ -f "$GITIGNORE" ]] && grep -qxF "$clean" "$GITIGNORE" 2>/dev/null; then
        return  # already present
    fi
    if [[ "$DRY_FLAG" == "--dry-run" ]]; then
        echo "  [gitignore] would add: $clean"
    else
        echo "$clean" >> "$GITIGNORE"
        echo "  [gitignore] added: $clean"
    fi
}

echo "${CYAN}Git ignore${RESET} — should any project-root directories be added to .gitignore?"
echo ""
for dir_entry in "$AGENTS_DIR" "$TARGET_PROJ" "$PROJ_DOCS" "$WORK_DOCS"; do
    # Only ask about dirs that sit directly under the project root
    clean="${dir_entry#./}"
    # Skip if the path goes outside the project root (absolute or contains ..)
    [[ "$clean" == /* || "$clean" == ..* ]] && continue
    read -r -n1 -p "  Ignore '${clean}'? [y/N]: " ig_char
    echo ""
    if [[ "$(echo "$ig_char" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
        add_to_gitignore "$clean"
    fi
done

echo ""

# ---------------------------------------------------------------------------
# Build arx init command
# ---------------------------------------------------------------------------

MODE_FLAG=""
if [[ "$ARX_MODE" == "link-arx" || "$ARX_MODE" == "link" ]]; then
    MODE_FLAG="--link-arx"
fi

ARX_CMD=(
    arx init
    --agentrx-source "$AGENTRX_SOURCE"
    --agents-dir     "$AGENTS_DIR"
    --target-proj    "$TARGET_PROJ"
    --proj-docs      "$PROJ_DOCS"
    --work-docs      "$WORK_DOCS"
)
[[ -n "$MODE_FLAG"  ]] && ARX_CMD+=("$MODE_FLAG")
[[ -n "$DRY_FLAG"   ]] && ARX_CMD+=("$DRY_FLAG")
ARX_CMD+=("$PROJECT_ROOT")

echo "Running: ${ARX_CMD[*]}"
echo ""

"${ARX_CMD[@]}"
