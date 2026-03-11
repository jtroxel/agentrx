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
To do so, it performs the following prompts and actions (interactive mode):
1. Prompt for ARX_AGENT_FILES:
```bash
Specify the AgentRx Agent Tools Directory (where AgentRx commands, skills, scripts, and hooks are located):
1. ./_agents
2. Copied from $ARX_SOURCE
```
  > *Source files copied from `_arx_agent_files.arx/`*

2. Prompt for local AgentRx templates:
  ```bash
  Do you want local copies of AgentRx templates?
  1. No
  2. Yes, from $ARX_SOURCE
  3. Specify a directory
  ```
  > *3: prompts `Enter Path:`*
  > *If dir specified, all templates are copied from `$AGENTRX_SOURCE/_arx_templates/` to the specified directory, see below.*

3. *Command copies/updates all root files*, from `$AGENTRX_SOURCE/_arx_templates/_arx_workspace_root.arx` to the $ARX_ROOT, see below.
   
4. **Prompt for:**
```bash
Specify the "root" directory for all target projects:
1. Let me add to the arx.config.yaml now.
2. Specify a directory
```
  > 2: prompts `Specify Path:`
  > If a directory is specified, it will be used as the root for all target projects.
  If the directory does not exist, it will be created.
  If the directory exists and is not empty, the command will consume all subdirectories as target projects, and update arx.config.yaml (and ARX_PROJ_ROOT).

1. Prompt:
```bash
Where would you likeAgentRx to update current Project Docs?
    - Default (1) = As subdirectories of each project dir (like `$ARX_PROJ_ROOT/$PROJ_ABBR_1/...`)
    - Option (2) = As subdirectories of a common  directory
  - Prompt: Specify the subdirectory for project docs:
    - (default: `..$PROJ_ABBR_1/arx_docs`)
  - Command creates the subdirectory structure.
```

**Arx Copy/Update Details:**
| Template subdir | Destination | Behaviour |
|---|---|---|
| `_arx_workspace_root.arx/` | `$ARX_WORKSPACE_ROOT` | `.ARX.` stripped; only installed if absent |
| `_arx_agent_tools.arx/` | `$ARX_AGENT_TOOLS` | Copied as-is (or symlinked with `--link-arx`) |
| `_arx_work_docs.arx/` | `$ARX_WORK_DOCS` | Always copied |
| `_arx_proj_docs.arx/` | `$ARX_PROJ_DOCS` | Optional; prompted interactively (or `--docs`/`--no-docs`) |
---

## Manual / Non-interactive Usage

If you prefer to skip the shell wizard and call `arx init` directly:
TODO



## Environment Variables

## `arx init` Behaviour

| Template subdir | Destination | Behaviour |
|---|---|---|
| `_arx_workspace_root.arx/` | `$ARX_WORKSPACE_ROOT` | `.ARX.` stripped; only installed if absent |
| `_arx_agent_tools.arx/` | `$ARX_AGENT_TOOLS` | Copied as-is (or symlinked with `--link-arx`) |
| `_arx_work_docs.arx/` | `$ARX_WORK_DOCS` | Always copied |
| `_arx_proj_docs.arx/` | `$ARX_PROJ_DOCS` | Optional; prompted interactively (or `--docs`/`--no-docs`) |

Workspace-root files (`AGENTS.md`, `CLAUDE.md`, `AGENT_TOOLS.md`, `.cursorrules`) come from `_arx_workspace_root.arx/` and are written only when absent.

### `.env`
Always written/updated with the six `ARX_*` variables.

### All options
TODO
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
