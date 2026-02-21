#!/usr/bin/env bash
# init-arx.sh — Interactive AgentRx project initializer
#
# Usage:
#   export AGENTRX_SOURCE=/path/to/agentrx-src
#   $AGENTRX_SOURCE/bin/init-arx.sh [project-dir]
#
# Activates the project's local venv, installs the arx CLI, prompts for
# directory layout (with full readline tab-completion and glob expansion),
# then calls `arx init` to do the actual file operations.

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

if [[ -z "${AGENTRX_SOURCE:-}" ]]; then
    echo "Error: AGENTRX_SOURCE is not set." >&2
    echo "  export AGENTRX_SOURCE=/path/to/agentrx-src" >&2
    exit 1
fi

PROJECT_ROOT="${1:-.}"
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
    local var="$1" label="$2" default="$3"
    local value
    # -e  : readline editing (tab-complete, history)
    # -i  : pre-fill with default so user can edit it
    read -e -r -i "$default" -p "  ${label} [${default}]: " value
    value="${value:-$default}"
    printf -v "$var" '%s' "$value"
}

prompt_choice() {
    # prompt_choice VAR_NAME "label" "default" "opt1|opt2|..."
    local var="$1" label="$2" default="$3"
    local value
    read -e -r -i "$default" -p "  ${label} [${default}]: " value
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

# Derive docs default from target
DEFAULT_DOCS="${TARGET_PROJ}/docs/agentrx"
prompt_dir  DOCS_OUT     "Docs output      (ARX_DOCS_OUT    )" "$DEFAULT_DOCS"

echo ""
echo "${CYAN}Mode${RESET}:"
prompt_choice ARX_MODE   "copy / link-arx                    " "copy"

echo ""

# ---------------------------------------------------------------------------
# Dry-run preview?
# ---------------------------------------------------------------------------

DRY_FLAG=""
read -e -r -i "n" -p "  Preview with --dry-run first? [y/N]: " dry_ans
if [[ "${dry_ans,,}" == "y" ]]; then
    DRY_FLAG="--dry-run"
fi

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
    --docs-out       "$DOCS_OUT"
)
[[ -n "$MODE_FLAG"  ]] && ARX_CMD+=("$MODE_FLAG")
[[ -n "$DRY_FLAG"   ]] && ARX_CMD+=("$DRY_FLAG")
ARX_CMD+=("$PROJECT_ROOT")

echo "Running: ${ARX_CMD[*]}"
echo ""

"${ARX_CMD[@]}"
