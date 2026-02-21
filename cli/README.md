# AgentRx CLI

Command-line tools for AgentRx. The `arx` CLI implements the same workflows as the
slash commands (e.g. `/agentrx:init` → `arx init`).

---

## Quickstart

### 1. Clone AgentRx source

```bash
git clone https://github.com/your-org/agentrx.git ~/dev/agentrx-src
export AGENTRX_SOURCE=~/dev/agentrx-src
```

### 2. Set up your project

```bash
mkdir ~/my-project && cd ~/my-project
python3.13 -m venv .venv
source .venv/bin/activate
```

### 3. Run the interactive initializer

```bash
$AGENTRX_SOURCE/bin/init-arx.sh .
```

The script will:
1. Activate `.venv` (or `venv`) found in the project root
2. `pip install` the `arx` CLI from `$AGENTRX_SOURCE/cli`
3. Prompt for directory layout with **readline tab-completion** and glob expansion:
   - `ARX_AGENT_TOOLS` — agent assets dir (default: `_agents`)
   - `ARX_TARGET_PROJ` — target project dir (default: `_project`)
   - `ARX_DOCS_OUT`    — docs output dir (default: `_project/docs/agentrx`)
   - Mode: `copy` (default) or `link-arx`
4. Optionally run a `--dry-run` preview first
5. Call `arx init` with the resolved values to do the actual work

---

## Manual / Non-interactive Usage

If you prefer to skip the shell wizard and call `arx init` directly:

```bash
# Install CLI first
pip install -e $AGENTRX_SOURCE/cli

# Copy mode (default)
arx init --agentrx-source $AGENTRX_SOURCE

# Link mode — symlinks agentrx/ leaf dirs instead of copying
arx init --link-arx --agentrx-source $AGENTRX_SOURCE

# Dry-run preview
arx init --agentrx-source $AGENTRX_SOURCE --dry-run

# Fully explicit
arx init \
  --agentrx-source $AGENTRX_SOURCE \
  --agents-dir _agents \
  --target-proj _project \
  --docs-out _project/docs/agentrx \
  /path/to/project
```

---

## Environment Variables

| Variable | Flag | Default | Description |
|---|---|---|---|
| `ARX_PROJECT_ROOT` | _(positional)_ | CWD | Project root; always set to where `arx init` runs. |
| `AGENTRX_SOURCE` | `--agentrx-source` | _(none)_ | AgentRx source directory. Required for `--link-arx`; optional for copy. |
| `ARX_AGENT_TOOLS` | `--agents-dir` | `_agents` | Agent assets directory. |
| `ARX_TARGET_PROJ` | `--target-proj` | `_project` | Target project directory. |
| `ARX_DOCS_OUT` | `--docs-out` | `_project/docs/agentrx` | Docs output directory. |

---

## `arx init` Behaviour

### Directory rules

| State | Mode | Result |
|---|---|---|
| `ARX_AGENT_TOOLS` exists | any | Left untouched. |
| `ARX_AGENT_TOOLS` missing | copy | Created; files copied from `AGENTRX_SOURCE/templates/_arx_agent_tools/`. |
| `ARX_AGENT_TOOLS` missing | `--link-arx` | Skeleton dirs created; each `agentrx/` leaf symlinked to source. |
| `ARX_TARGET_PROJ` missing | any | Created (with `src/` inside). |
| `ARX_DOCS_OUT` missing | any | Created (with `deltas/`, `vibes/`, `history/`). |

### Root files written
`AGENTS.md`, `CLAUDE.md`, `CHAT_START.md` — written only if absent.

### `.env`
Always written/updated with the four `ARX_*` variables.

### All options

```
arx init [OPTIONS] [TARGET_DIR]

  -l, --link-arx         Symlink agentrx/ assets instead of copying.
      --agentrx-source   AgentRx source dir (env: AGENTRX_SOURCE).
      --agents-dir       Agent tools dir    (env: ARX_AGENT_TOOLS, default: _agents).
      --target-proj      Target project dir (env: ARX_TARGET_PROJ, default: _project).
      --docs-out         Docs output dir    (env: ARX_DOCS_OUT).
      --data             YAML file with extra template variables, or '-' for stdin.
  -v, --verbose          Show detailed output.
      --dry-run          Preview actions without making changes.
  -h, --help             Show this message and exit.
```

---

## Virtual Environment Setup

```bash
# Python 3.13 via pyenv
pyenv install 3.13.6
pyenv local 3.13.6

# or via Homebrew
brew install python@3.13

# Create and activate venv
python3.13 -m venv .venv
source .venv/bin/activate        # macOS / Linux

# Or with uv
uv venv .venv --python python3.13
source .venv/bin/activate
```

---

## Development

```bash
# Install with dev dependencies (from AGENTRX_SOURCE)
pip install -e "${AGENTRX_SOURCE}/cli[dev]"

# Run tests
cd $AGENTRX_SOURCE/cli
pytest

# Run a single test
pytest tests/test_init.py::TestInitCommand::test_init_creates_config_files

# Format / lint
black agentrx/ tests/
ruff check agentrx/ tests/
```
