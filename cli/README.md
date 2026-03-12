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

The script performs the following prompts and actions (interactive mode):

1. Prompt for ARX_AGENT_FILES:
```bash
Specify the AgentRx Agent Tools Directory (where AgentRx commands, skills, scripts, and hooks are located):
1. ./_agents
2. Copied from $ARX_SOURCE
```
  > *Source files copied from `_arx_agent_tools.arx/`*

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

5. Prompt:
```bash
Where would you like AgentRx to update current Project Docs?
    - Default (1) = As subdirectories of each project dir (like `$ARX_PROJ_ROOT/$PROJ_ABBR_1/...`)
    - Option (2) = As subdirectories of a common  directory
  - Prompt: Specify the subdirectory for project docs:
    - (default: `..$PROJ_ABBR_1/arx_docs`)
  - Command creates the subdirectory structure.
```

**Arx Copy/Update Details:**
| Template subdir | Destination | Behaviour |
|---|---|---|
| `_arx_workspace_root.arx/` | `$ARX_ROOT` | Copied as-is; only installed if absent |
| `_arx_agent_tools.arx/` | `$ARX_AGENT_FILES` | Copied as-is (or symlinked with `--link-arx`) |
| `_arx_work_docs.arx/` | `$ARX_WORKING` | Always copied |
| `_arx_proj_docs.arx/` | project `docs/` dirs | Optional; prompted interactively (or `--docs`/`--no-docs`) |

> **Naming convention:** Files with normal names are copied to the workspace.
> Files/dirs with `.arx.` in the name (or ending in `.arx`) are source-only and skipped during copy.

---

## Non-interactive Usage

Skip the shell wizard and call `arx init` directly:

```bash
export AGENTRX_SOURCE=~/dev/agentrx-src
arx init ~/my-workspace \
  --agent-files _agents \
  --projects-dir _projects \
  --working-dir _projects/arx_docs \
  --docs
```

### `arx init` options

| Option | Default | Description |
|---|---|---|
| `WORKSPACE` (arg) | `.` | Target directory |
| `--agent-files` | `_agents` | Agent tools directory |
| `--templates-dir` | _(use from source)_ | Local templates copy destination |
| `--projects-dir` | `_projects` | Root directory for target projects |
| `--working-dir` | `<projects-dir>/arx_docs` | Working docs directory |
| `--link-arx` | off | Symlink agent tools instead of copying |
| `--docs / --no-docs` | `--docs` | Install project-doc templates |
| `--dry-run` | off | Preview without writing |

### `.env`
Always written/updated with the `ARX_*` variables.

---

## `arx prompt` — Prompt Primitives

Work with prompt files — create, execute, and list.

### `arx prompt new`

```bash
arx prompt new [TEMPLATE] [TEXT] [--data JSON] [--data-file FILE] [--stdin] [-o PATH]
```

| Option | Description |
|---|---|
| `TEMPLATE` (arg) | Template name resolved from `$ARX_TEMPLATES` (e.g. `arch-facet`) |
| `TEXT` (arg) | Plain text to use as the prompt body (alternative to a template) |
| `--data` | Inline JSON data context |
| `--data-file` | Path to a YAML/JSON data file |
| `--stdin` | Read additional JSON data from stdin |
| `-o, --output` | Output file path (overrides default) |

Renders the `:new` phase, writes to `$ARX_WORKING/vibes/` by default.

### `arx prompt do`

```bash
arx prompt do PROMPT_FILE [--data JSON] [--data-file FILE] [--stdin] [--dry-run] [-o PATH]
```

| Option | Description |
|---|---|
| `PROMPT_FILE` (arg) | Path to an existing prompt file |
| `--data` | Inline JSON data context |
| `--data-file` | Path to a YAML/JSON data file |
| `--stdin` | Read additional JSON data from stdin |
| `--dry-run` | Preview rendered output without side effects |
| `-o, --output` | Write output to file instead of stdout |

Renders the `:do` phase. Data sources merge in order: data-file < `--data` < stdin.

### `arx prompt list`

```bash
arx prompt list [-n LIMIT] [--dir DIR]
```

Shows recent prompt files sorted by modification time with relative age.

---

## Virtual Environment Setup

Requires Python >= 3.9.

```bash
# via pyenv
pyenv install 3.13.6
pyenv local 3.13.6

# or via Homebrew
brew install python@3.13

# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux

# Or with uv
uv venv .venv --python 3.13
source .venv/bin/activate
```

---

## Development

```bash
# Install with dev dependencies
cd $AGENTRX_SOURCE/cli
pip install -e ".[dev]"
# or with uv:
uv pip install -e ".[dev]"

# Run tests
pytest

# Run a single test
pytest tests/test_init.py::TestInitCommand::test_init_creates_config_files

# Format / lint
black agentrx/ tests/
ruff check agentrx/ tests/
```
