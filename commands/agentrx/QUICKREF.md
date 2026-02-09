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
| `/agentrx:init` | Initialize project structure |
| `/agentrx:prompt-new "text"` | Create timestamped prompt file |
| `/agentrx:trial-init <name>` | Initialize trial worktree |
| `/agentrx:trial-work <name>` | Spawn agent for trial |
| `/agentrx:trial-status` | Show all trial status |

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
/agentrx:prompt-new "Implement feature X" feature_x

# 3. Initialize trials for different approaches
/agentrx:trial-init approach-a
/agentrx:trial-init approach-b

# 4. Check setup
/agentrx:trial-status

# 5. Work on each trial
/agentrx:trial-work approach-a
/agentrx:trial-work approach-b

# 6. Compare results
/agentrx:trial-status
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
| `/agentrx:GETTING-STARTED` | Quick start guide |
| `/agentrx:README` | Full reference |
| `/agentrx:TRIAL_USAGE` | Trial system guide |
| `/agentrx:COMMAND_INDEX` | Command index |

## Tips

- Each trial is **completely isolated** - no conflicts
- Trials run on **separate branches** - easy to compare
- Use `git diff trial/a trial/b` to compare implementations
- ARX templates use `[[...]]` to avoid mustache conflicts
- All AgentRx docs use YAML front matter with `arx:` field
