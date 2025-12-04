# agentrx

A minimal, modern Python project to generate Markdown files from templates using a Typer CLI and configurable AI agents (LangChain).

## Quick start

### 1. Create a virtual environment and install dependencies:
**with `uv`**
```bash
# install uv (optional)
pipx install uv

# create and activate a virtual environment named .venv
uv venv create .venv
source .venv/bin/activate

# install project in editable mode with dev dependencies
pip install -e '.[dev]'
```

**with python/venv**

```bash
# Install pyenv (if not already installed; e.g., macOS: `brew install pyenv`)
pyenv install 3.13.0
pyenv local 3.13.0
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### 2. Run the CLI (once installed):

```bash
agentrx generate --title "My Note" --output note.md
```

See `README.md` for configuration notes on LangChain/OpenAI keys.
