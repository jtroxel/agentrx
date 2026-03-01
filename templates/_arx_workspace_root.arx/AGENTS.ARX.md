# AGENTS.md

Guidance for AI coding agents working in this repository.

## On Startup — Read These Files

Read the following in parallel at the start of every session.
Do **not** read anything else until directed by the user.

### Always read
- `README.md`
- `docs/README.md` — project overview, architecture, directory structure, env vars
- `cli/README.md` — CLI quickstart, `arx init` usage, `init-arx.sh` workflow
- `cli/agentrx/commands/init.py` — canonical source of truth for init behaviour
- `cli/agentrx/commands/prompt.py` — prompt command implementation

### Read when working on templates
- `templates/` — top-level listing only (do not recurse unless directed)

## After Reading

Print a list of every file read into the chat.

## Key Principles

1. Follow instructions precisely — if it wasn't specified, don't do it.
2. `docs/README.md` is the authoritative reference for project architecture and env vars.
3. `cli/README.md` is the authoritative reference for CLI usage and the shell init workflow.
4. Build/test/lint commands are in `CLAUDE.md`.