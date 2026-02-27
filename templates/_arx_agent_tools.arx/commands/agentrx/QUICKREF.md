---
arx: context
name: quickref
description: AgentRx Quick Reference
version: 1
---

# AgentRx Quick Reference

## Slash Commands

| Command | Description |
|---------|-------------|
| `/arx:init` | Initialize project structure |
| `/arx:prompt-new "text"` | Create timestamped prompt file |
| `/arx:trial-init <name>` | Initialize trial worktree |
| `/arx:trial-work <name>` | Spawn agent for trial |
| `/arx:trial-status` | Show all trial status |
| `/arx:adapt-workspace <coding-agent>` | Add/update native agent instructions for ARX |

## Python CLI

```bash
arx init [dir]              # Initialize project
arx setup                   # Setup Claude Code links
arx --help                  # Show help
```

## Typical Workflow

```bash
# 1. Initialize project
arx init my-project && cd my-project

# 2. Create a prompt
/arx:prompt-new "Implement feature X" feature_x

# 3. Initialize trials for different approaches
/arx:trial-init approach-a
/arx:trial-init approach-b

# 4. Check setup
/arx:trial-status

# 5. Work on each trial
/arx:trial-work approach-a
/arx:trial-work approach-b

# 6. Compare results
/arx:trial-status
git diff trial/approach-a trial/approach-b
```

## Directory Structure

```
project/
├── _agents/                    # Agent assets
│   ├── commands/agentrx/       # Commands
│   ├── skills/agentrx/         # Skills
│   ├── hooks/agentrx/          # Hooks
│   └── scripts/agentrx/        # Scripts
├── _project/                   # Project code
│   └── docs/agentrx/
│       ├── deltas/             # Change requests
│       ├── vibes/              # Prompts
│       └── history/            # History
├── .claude/                    # Claude Code links
├── worktrees/                  # Trial worktrees
│   ├── approach-a/
│   └── approach-b/
├── AGENTS.md
├── CLAUDE.md
└── CHAT_START.md
```

## Skills

| Skill | Description |
|-------|-------------|
| `arx-render` | Render ARX templates |
| `arx_templating` | ARX syntax reference |

## ARX Template Syntax

```html
<ARX [[variable]] />              <!-- Variable -->
<ARX [[var | "default"]] />       <!-- With default -->
<ARX [[#condition]]: />...<ARX /: />  <!-- If block -->
<ARX [[*list as item]]: />...<ARX /: />  <!-- Loop -->
<ARX @"file.md" />                <!-- Include -->
```

## Environment Variables

```bash
AGENTRX_DIR=_agents
AGENTRX_PROJECT_DIR=_project
AGENTRX_DOCS_DIR=_project/docs/agentrx
```

## Documentation

| Command | Content |
|---------|---------|
| `/arx:GETTING-STARTED` | Quick start guide |
| `/arx:README` | Full reference |
| `/arx:TRIAL_USAGE` | Trial system guide |
| `/arx:COMMAND_INDEX` | Command index |

## Tips

- Each trial is **completely isolated** - no conflicts
- Trials run on **separate branches** - easy to compare
- Use `git diff trial/a trial/b` to compare implementations
- ARX templates use `[[...]]` to avoid mustache conflicts
- All AgentRx docs use YAML front matter with `arx:` field
