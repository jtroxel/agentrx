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
/agentrx:init
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
| `/agentrx:init` | Initialize project structure |
| `/agentrx:prompt-new` | Create timestamped prompt file |
| `/agentrx:trial-init` | Initialize trial worktree |
| `/agentrx:trial-work` | Spawn agent for trial |
| `/agentrx:trial-status` | Show trial status |

## Available Skills

| Skill | Description |
|-------|-------------|
| `arx-render` | Render ARX templates with context |
| `arx_templating` | ARX syntax reference |

## Documentation Commands

```
/agentrx:QUICKREF          - Quick reference guide
/agentrx:TRIAL_USAGE       - Detailed usage guide
/agentrx:COMMAND_INDEX     - System summary
/agentrx:README            - Full command reference
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

### 2. Create a Prompt

```
/agentrx:prompt-new "Implement user authentication" auth
```

Creates: `_project/docs/agentrx/vibes/auth_26-02-09-10.md`

### 3. Start Parallel Trials

```
/agentrx:trial-init jwt
/agentrx:trial-init session
/agentrx:trial-init oauth
```

### 4. Work on Each Trial

```
/agentrx:trial-work jwt
/agentrx:trial-work session
/agentrx:trial-work oauth
```

### 5. Compare Results

```
/agentrx:trial-status
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

1. **Read the quick reference**: `/agentrx:QUICKREF`
2. **Create your first prompt**: `/agentrx:prompt-new "your task here"`
3. **Initialize trials**: `/agentrx:trial-init approach1`
4. **Start working**: `/agentrx:trial-work approach1`

## Getting Help

- Quick reference: `/agentrx:QUICKREF`
- Full documentation: `/agentrx:README`
- CLI help: `arx --help`
