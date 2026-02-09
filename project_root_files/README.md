# AgenTrx Overview

## Top-Level Structure of an AgenTrx Project
The recommended setup for an AI-assisted project using AgentRx is to have a parent directory containing 3 key subdirectories.
These can be customized via environment variables, but the default structure is:
- `<project-root>/` - The main project directory. Software project code, documentation, etc.
  - `<project-docs>/` - SW project documentation, design docs, requirements, etc.
- `<project-agentrx-root>/` - Contains all agent configurations, commands, skills, hooks, scripts, etc. Agentic coding assets from AgenTrx as well as any custom agentic assets for the project.
- <project-agentrx-dev>/ - (optional) Iterative change prompts and context documents. Defaults to an `agentrx` subdirectory of project-docs.

The `agentrx init` command sets up this structure with the default directories, but you can customize as needed. The user is given the option of copying agentrx files, linking subdirectories into the agentrx-root, or just specifying custom directories on the filesystem.

## Key Environment Variables
- `AGENTRX_DIR`: Root directory for the project. Default is the `_agents/` directory.
- `AGENTRX_PROJECT_DIR`: Directory of the main project being worked on. Default is `_project/`.
- `AGENTRX_DOCS_DIR`: Directory for project documentation. Default is `$AGENTRX_PROJECT_DIR/docs/agentrx_context`.
- `AGENTRX_PROJECT_DEV_DIR`: Directory for iterative development context documents. Default is `$AGENTRX_DOCS_DIR/agentrx`.

## 
├── _agents # Default AGENTRX_DIR
│   ├── commands
│   │   └── agentrx
│   │       ├── COMMAND_SUMMARY.md
│   │       ├── prompt-new.md
│   │       ├── trial-init.md
│   │       ├── trial-status.md
│   │       └── trial-work.md
│           └── ...
│   ├── hooks
│   │   └── agentrx
│   │       ├── ...
│   ├── scripts
│   │   └── agentrx
│   │       ├── setup-claude-links.sh
│   │       ├── trial-init.sh
│   │       ├── trial-status.sh
│   │       └── trial-work.sh
│           └── ...
│   └── skills
│       └── agentrx
│           ├── prompt-new
│           ├── trial-init
│           ├── trial-status
│           └── trial-work
│           └── ...
| # ------------------------------------------------------------------
├── _project # Default AGENTRX_PROJECT_DIR
│   ├── src
│   ├── docs # <-- This is the default AGENTRX_DOCS_DIR>
│           ├── agentrx # (default AGENTRX_DOCS_DIR)
│               └── deltas
│               └── vibes
│               └── history
│   ├── ...
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── ...
