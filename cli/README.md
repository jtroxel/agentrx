# AgentRx CLI

Command line tools for AgentRx. The CLI provides local commands (arx ...) that implement the same behaviors as the slash commands (for example `/agentrx:init` maps to `arx init`).

## Install the Source
Clone the `agentrx` repository into the target location:
```bash
git clone https://example.com/agentrx.git $HOME/.agentrx
```

### Set up the AgentRx source and initialize the project
```bash
# Point the CLI to the local source
export AGENTRX_SOURCE="$HOME/.agentrx"
```
# Install the CLI into your project (run these from the project root):

```bash
# Point the CLI to your local project, the root of the code:
export AGENTRX_PROJECT_ROOT="$HOME/my_project"
```
```bash
# Install the editable CLI from the local source
pip install -e ${AGENTRX_SOURCE}/cli
```
```bash
# (Optional) Install dev dependencies if needed
pip install -e "${AGENTRX_SOURCE}/cli[dev]"
```

```bash
# Run the CLI init command
arx init --help # get the lay of the land

# Go for it
arx init --project-root "$AGENTRX_PROJECT_ROOT" --source-dir "$AGENTRX_SOURCE"
```

### Local Development with Python Virtual Environments
For local development, we recommend using `uv` to manage a virtual environment. Suggest using the git clone method to set up the source for development.

```bash
# Install with Brew (macOS/Linux)
brew install uv
```
```bash
# Create a virtual environment
cd cli
# Create a virtual environment with Python 3.13 and pin the runtime

cd cli

# Use a specific interpreter (example: python3.13)
python3.13 -m venv .venv

# Activate the environment
source .venv/bin/activate  # On macOS/Linux

# Or, using uv to create the venv and explicitly point at the interpreter
# (uv will reuse the interpreter found on PATH)
uv venv create .venv --python "$(which python3.13)"
source .venv/bin/activate

# If Python 3.13 is not installed, install it first:
# - Homebrew (macOS/Linux)
brew install python@3.13

# - pyenv
pyenv install 3.13.0
pyenv local 3.13.0

# - (If your uv installation supports installing runtimes) example:
#   uv pkg install python@3.13   # run only if your uv supports this command

# Pin the runtime for pyenv / CI / buildpacks
echo "3.13.0" > .python-version      # pyenv
echo "python-3.13.0" > runtime.txt   # Heroku/buildpacks
```bash
# Activate the environment
source .venv/bin/activate  # On macOS/Linux
```
```bash
# Install with editable AGENTRX_SOURCE with uv
uv pip install -e "${AGENTRX_SOURCE}/cli[dev]"
```

## Command Details

### `arx init`

#### **Default Behavior:**
`arx init` will create the default directory structure as described above, using the default environment variable values. It will then save a `.env` file in the project root with the configured environment variables.

#### **How `init` uses the environment variables/flags:**
- `ARX_PROJECT_ROOT` - Determines the root directory for the project. This will always be set to the CWD where `arx init` is run. It should not Be set by the user.
- `ARX_AGENTS_SOURCE` - (`--source-dir`) Specifies the source directory of a local copy or install of AgentRx. It's 
- `ARX_TARGET_PROJ` - (`--target-proj`) Specifies the target project directory relative to the project root.
  - If not set, defaults to `$ARX_PROJECT_ROOT/_project/`.
  - If $ARX_TARGET_PROJ does not exist, it will be created.
  - If $ARX_TARGET_PROJ exists, the variable will simply be set to that directory for future CLI commands.
- `ARX_AGENT_TOOLS` - (`--agent-tools`) Specifies the agent assets directory. See [Readme ARX_AGENT_TOOLS](../docs/README.md#$ARX_AGENT_TOOLS)
  - If not set, defaults to `$ARX_PROJECT_ROOT/_agents/`.
  - If `$ARX_AGENT_TOOLS` does not exist:
    1. The `$ARX_AGENT_TOOLS` directory and all subdirectories will be created.
    2. `arx init` will then copy all contents of the `agentrx` subdirectories from `$ARX_AGENTS_SOURCE`.
  - If `$ARX_AGENT_TOOLS` doesn't exist, AND the `--link-arx` flag is used:
    1. The directory and all subdirectories will be created, minus any `agentrx` subdirs.
    2. The command then creates "deep" symlinks to the corresponding source assets (`$ARX_AGENTS_SOURCE/templates/ARX_AGENTS_DIR/**/agentrx/*.*`).
  - If set, and the directory exists, the variable will simply be set to that directory for future CLI commands.

- `ARX_DOCS_OUT` - (`--docs-out`) Specifies the documentation output directory.
  - If not set, defaults to `$ARX_TARGET_PROJ/docs/agentrx`.
  - If set, and the directory does not exist, it will be created.
  - If set, and the directory exists, the variable will simply be set to that directory for future CLI commands.

View the usage for the `arx init` command.
```bash
arx init --help
```
#### `arx init` Command Usage
```
arx init [OPTIONS] [PATH]
#Note: Always sets the $ARX_PROJECT_ROOT to the CWD.

Options:
- -l, --link
  - Create symlinks to `agentrx` subdirectories defined in the source directory (under templates/_arx_agents_source/**). All links will fail if a same-named target file already exists.
- --agents-source <PATH>
  - Source directory of a local copy or install of AgentRx. Env: ARX_AGENTS_SOURCE (default: $ARX_PROJECT_ROOT/_agents/). Files from this directory are populated in your project $ARX_AGENTS_TOOLS dir.
- --target-proj <PATH>
  - Target project directory relative to the project root. Env: ARX_TARGET_PROJ (default: $ARX_PROJECT_ROOT/_project/). If the directory does not exist it will be created.
- --agents-tools <PATH>
  - Agent assets directory. Env: ARX_AGENTS_TOOLS (default: $ARX_PROJECT_ROOT/_agents/).
- --docs-out <PATH>
  - Documentation output directory. Env: ARX_DOCS_OUT (default: $ARX_TARGET_PROJ/docs/agentrx). Will be created if it does not exist.
- -v, --verbose
  - Show detailed output.
- --dry-run
  - Perform a trial run with no changes made. Display the mkdir/copy/link actions that *would* be performed, in a concise manner.

Notes:
- Interactive default: if directory options are not provided, the command will prompt for each required path.
- Any explicit flag value overrides the corresponding environment variable.
- Use --agentrx-source or set AGENTRX_SOURCE to point link mode at the source tree.
- Example usages:
  - arx init
  - arx init --link --agentrx-source /path/to/agentrx
  - arx init /path/to/project
  - Prompt for custom directory paths (interactive).
- -v, --verbose
  - Show detailed output.

Notes:
- Any explicit flag value overrides the corresponding environment variable.
- If PATH is provided it is used as the project root (equivalent to --project-root PATH).
- Use --agentrx-source or AGENTRX_SOURCE to point link mode at the source tree.
- Example: arx init --mode link --agentrx-source /path/to/agentrx --project-root /path/to/project

Examples:

```bash
# Initialize current directory
arx init

# Initialize with symlinks to shared assets
arx init --link --agentrx-source /path/to/agentrx # <-- dir must have the `_agents` subdirectory

```
By default the command prompts for every required directory. Alternatively, you can supply each directory via its own option. The default mode is copy.

Behavior summary:
- Interactive default: if directory options are not provided, the CLI will prompt for each required path.
- When Copying: arx will create directories if they  do not exist and copy files into them. **Non-destructive** - existing files are skipped with a warning.
- Link mode: will create symlinks to the source; it will error out if a same-named directory or file already exists at the target path.
- Use `--agentrx-source` (or AGENTRX_SOURCE) to point link mode at the source tree.
- Provide explicit directory options to skip prompts and run non-interactively.

## Development

```bash
# Install with dev dependencies
pip install -e "${AGENTRX_SOURCE}/cli[dev]"

# Run tests
pytest

# Format code
black agentrx/
ruff check agentrx/
```
