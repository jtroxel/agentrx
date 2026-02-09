---
arx: command
name: init
description: Initialize AgentRx project structure
version: 1
argument-hint: [--copy|--link|--custom] [target-dir]
---

# /agentrx:init - Initialize AgentRx Project

Set up the AgentRx directory structure for AI-assisted development.

## Usage

```
/agentrx:init [options] [target-dir]
```

## Options

| Option | Description |
|--------|-------------|
| `--copy` | Copy AgentRx files to the project (default) |
| `--link` | Create symlinks to AgentRx assets |
| `--custom` | Prompt for custom directory paths |
| `target-dir` | Target directory (defaults to current directory) |

## What It Creates

```
<target-dir>/
├── _agents/                        # AGENTRX_DIR - Agent assets
│   ├── commands/agentrx/           # Slash command definitions
│   ├── skills/agentrx/             # Skill definitions
│   ├── hooks/agentrx/              # Hook scripts
│   └── scripts/agentrx/            # Implementation scripts
├── _project/                       # AGENTRX_PROJECT_DIR
│   ├── src/                        # Project source code
│   └── docs/
│       └── agentrx/                # AGENTRX_DOCS_DIR
│           ├── deltas/             # Change request documents
│           ├── vibes/              # Prompt/vibe files
│           └── history/            # Completed work history
├── .claude/                        # Claude Code integration
│   ├── commands/agentrx -> ...     # Symlink to commands
│   └── skills/agentrx -> ...       # Symlink to skills
├── AGENTS.md                       # Agent instructions
├── CLAUDE.md                       # Claude Code guidance
├── CHAT_START.md                   # Session bootstrap instructions
└── .env                            # Environment configuration
```

## Environment Variables

Created in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENTRX_DIR` | `_agents` | Root for agent assets |
| `AGENTRX_PROJECT_DIR` | `_project` | Main project directory |
| `AGENTRX_DOCS_DIR` | `_project/docs/agentrx` | Documentation directory |

## Examples

```bash
# Initialize in current directory with default settings
/agentrx:init

# Initialize with symlinks to shared AgentRx assets
/agentrx:init --link

# Initialize in a specific directory
/agentrx:init /path/to/my-project

# Custom directory configuration
/agentrx:init --custom
```
## ARX CLI
This command uses the ARX CLI. See [ARX CLI documentation](../../cli/README.md) for details on installation and usage.
## Modes

### Copy Mode (Default)
Copies all AgentRx template files into the project. Best for standalone projects.

### Link Mode
Creates symlinks to a shared AgentRx installation. Best for:
- Multiple projects sharing the same AgentRx version
- Development of AgentRx itself
- Keeping projects in sync with updates

### Custom Mode
Prompts for custom directory paths. Use when:
- Project has existing structure to integrate with
- Non-standard directory layout required
- Specific paths needed for organization

## Post-Init Setup

After initialization, run the Claude Code setup:

```bash
# Via Python CLI
arx setup

# Or via shell script
./_agents/scripts/agentrx/setup-claude-links.sh
```

This creates symlinks in `.claude/` for Claude Code integration.

## Implementation

When this command is executed:

1. Parse options and target directory
2. Create directory structure based on mode
3. Create configuration files (AGENTS.md, CLAUDE.md, CHAT_START.md)
4. Create .env with environment variables
5. Run Claude Code setup (symlinks)
6. Report what was created

## See Also

- [GETTING-STARTED.md](./GETTING-STARTED.md) - Quick start guide
- [QUICKREF.md](./QUICKREF.md) - Command quick reference
- [arx_templating.md](../../skills/agentrx/arx_templating.md) - ARX template syntax
