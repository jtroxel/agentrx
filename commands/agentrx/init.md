---
description: Initialize AgenTrx project structure
argument-hint: [--copy|--link|--custom] [target-dir]
---

# /agentrx:init - Initialize AgenTrx Project

Set up the AgenTrx directory structure for AI-assisted development.

## Usage
```
/agentrx:init [options] [target-dir]
```

## Options
- `--copy` - Copy AgenTrx files to the project (default)
- `--link` - Create symlinks to AgenTrx assets
- `--custom` - Prompt for custom directory paths
- `target-dir` - Target directory (defaults to current directory)

## What it creates

```
<target-dir>/
├── _agents/                    # AGENTRX_DIR
│   ├── commands/agentrx/       # Slash command definitions
│   ├── skills/agentrx/         # Skill definitions
│   ├── hooks/agentrx/          # Hook scripts
│   └── scripts/agentrx/        # Implementation scripts
├── _project/                   # AGENTRX_PROJECT_DIR
│   └── docs/
│       └── agentrx/            # AGENTRX_DOCS_DIR
│           ├── deltas/         # Change request documents
│           ├── vibes/          # Prompt/vibe files
│           └── history/        # Completed work history
├── AGENTS.md                   # Agent configuration
└── CLAUDE.md                   # Claude Code guidance
```

## Environment Variables (created in .env)
- `AGENTRX_DIR` - Root for agent assets (default: `_agents/`)
- `AGENTRX_PROJECT_DIR` - Main project directory (default: `_project/`)
- `AGENTRX_DOCS_DIR` - Documentation directory (default: `$AGENTRX_PROJECT_DIR/docs/agentrx`)

## Examples
```
# Initialize in current directory with default settings
/agentrx:init

# Initialize with symlinks to shared AgenTrx assets
/agentrx:init --link

# Initialize in a specific directory
/agentrx:init /path/to/my-project

# Custom directory configuration
/agentrx:init --custom
```

## Implementation

When this command is executed:

1. Parse options and target directory
2. Create directory structure based on mode:
   - `--copy`: Copy all AgenTrx template files
   - `--link`: Create symlinks to source AgenTrx assets
   - `--custom`: Prompt for custom paths
3. Create AGENTS.md and CLAUDE.md if they don't exist
4. Create .env with environment variable defaults
5. Report what was created

!bash .claude/scripts/agentrx/init.sh $ARGUMENTS
