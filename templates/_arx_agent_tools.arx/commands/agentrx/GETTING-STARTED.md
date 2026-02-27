---
arx: context
name: getting-started
description: Quick start guide for AgentRx
version: 1
---

# Getting Started with AgentRx

AgentRx provides AI-assisted development tools through native Claude Code slash commands and a Python CLI.

## Quick Start

### Option 1: Python CLI (Recommended)

```bash
# Install the CLI
cd cli && pip install -e .

# Initialize a new project
arx init /path/to/my-project

# Or initialize current directory
arx init
```

### Option 2: Shell Script

```bash
# Run the init script directly
./_agents/scripts/agentrx/init.sh /path/to/my-project
```

### Option 3: Slash Commands (In Claude Code)

```
/arx:init
```

## What Gets Created

```
my-project/
├── _agents/                    # Agent assets
│   ├── commands/agentrx/       # Slash command definitions
│   ├── skills/agentrx/         # Skill definitions
│   ├── hooks/agentrx/          # Event hooks
│   └── scripts/agentrx/        # Implementation scripts
├── _project/                   # Your project code
│   ├── src/
│   └── docs/agentrx/
│       ├── deltas/             # Change request documents
│       ├── vibes/              # Prompt/vibe files
│       └── history/            # Completed work history
├── .claude/                    # Claude Code integration (symlinks)
├── AGENTS.md                   # Agent instructions
├── CLAUDE.md                   # Claude Code guidance
├── CHAT_START.md               # Session bootstrap
└── .env                        # Configuration
```

## Available Commands

Type these in Claude Code:

| Command | Description |
|---------|-------------|
| `/arx:init` | Initialize project structure |
| `/arx:prompt-new` | Create timestamped prompt file |
| `/arx:trial-init` | Initialize trial worktree |
| `/arx:trial-work` | Spawn agent for trial |
| `/arx:trial-status` | Show trial status |
| `/arx:adapt-workspace` | Add/update native agent instructions for ARX |

## Available Skills

| Skill | Description |
|-------|-------------|
| `arx-render` | Render ARX templates with context |
| `arx_templating` | ARX syntax reference |

## Documentation Commands

```
/arx:QUICKREF          - Quick reference guide
/arx:TRIAL_USAGE       - Detailed usage guide
/arx:COMMAND_INDEX     - System summary
/arx:README            - Full command reference
```

## Python CLI Commands

```bash
arx init [OPTIONS] [TARGET_DIR]    # Initialize project
arx setup [OPTIONS]                # Setup Claude Code links
arx --help                         # Show all commands
arx --version                      # Show version
```

## Workflow Example

### 1. Initialize Your Project

```bash
arx init my-project
cd my-project
```

### 2. Bootstrap Your Coding Agent(s)

```bash
# All agents at once
_agents/scripts/agentrx/adapt-agent.sh all

# Or just one
_agents/scripts/agentrx/adapt-agent.sh github-copilot
_agents/scripts/agentrx/adapt-agent.sh claude-code
_agents/scripts/agentrx/adapt-agent.sh cursor
```

This injects a minimal pointer into the agent's native instruction file so it
discovers `_agents/` on its very first session.

### 3. Create a Prompt

```
/arx:prompt-new "Implement user authentication" auth
```

Creates: `_project/docs/agentrx/vibes/auth_26-02-09-10.md`

### 4. Start Parallel Trials

```
/arx:trial-init jwt
/arx:trial-init session
/arx:trial-init oauth
```

### 5. Work on Each Trial

```
/arx:trial-work jwt
/arx:trial-work session
/arx:trial-work oauth
```

### 6. Compare Results

```
/arx:trial-status
```

Review implementations in each worktree.

## ARX Templates

AgentRx uses ARX templating syntax for dynamic content:

```markdown
---
arx: template
version: 1
---
# Report: <ARX [[title]] />

<ARX [[#sections]]: />
## <ARX [[.heading]] />
<ARX [[.content]] />
<ARX /: />
```

See [arx_templating.md](../../skills/agentrx/arx_templating.md) for full syntax reference.

## Configuration

Environment variables in `.env`:

```bash
AGENTRX_DIR=_agents
AGENTRX_PROJECT_DIR=_project
AGENTRX_DOCS_DIR=_project/docs/agentrx
```

## Next Steps

1. **Read the quick reference**: `/arx:QUICKREF`
2. **Create your first prompt**: `/arx:prompt-new "your task here"`
3. **Initialize trials**: `/arx:trial-init approach1`
4. **Start working**: `/arx:trial-work approach1`

## Getting Help

- Quick reference: `/arx:QUICKREF`
- Full documentation: `/arx:README`
- CLI help: `arx --help`
