---
arx: config
name: chat-start
description: Bootstrap instructions for coding agents starting new sessions
version: 1
---

# AgentRx Bootstrap Instructions

> **For Coding Agents**: Follow these instructions precisely at session start.

---

## Step 1: Load Core Context

Read these files **in parallel** to establish AgentRx capabilities:

### Commands (treat as native slash commands)
```
_agents/commands/agentrx/COMMAND_INDEX.md
_agents/commands/agentrx/QUICKREF.md
_agents/commands/agentrx/init.md
_agents/commands/agentrx/prompt-new.md
_agents/commands/agentrx/trial-init.md
_agents/commands/agentrx/trial-status.md
_agents/commands/agentrx/trial-work.md
```

### Skills
```
_agents/skills/agentrx/arx_templating.md
_agents/skills/agentrx/arx_render.md
```

### Reference (read if needed)
```
_agents/commands/agentrx/README.md
_agents/commands/agentrx/GETTING-STARTED.md
_agents/commands/agentrx/TRIAL_USAGE.md
```

---

## Step 2: Load Project Context (If Present)

Check for and load project-specific extensions:

```
_agents/commands/<project>/*.md
_agents/skills/<project>/*.md
_agents/agents/<project>/*.md
_agents/hooks/<project>/*.md
```

Replace `<project>` with the project name if subdirectories exist beyond `agentrx/`.

---

## Step 3: Confirm Bootstrap

After loading, output a confirmation like:

```
**AgentRx Loaded**

Commands:
- /agentrx:init - Initialize project structure
- /agentrx:prompt-new - Create prompt files
- /agentrx:trial-init - Initialize trial worktrees
- /agentrx:trial-status - Show trial status
- /agentrx:trial-work - Spawn trial agents

Skills:
- arx-render - Render ARX templates
- arx_templating - ARX syntax reference

Ready for instructions.
```

---

## Available Commands

| Command | Description |
|---------|-------------|
| `/agentrx:init` | Initialize AgentRx project structure |
| `/agentrx:prompt-new` | Create timestamped prompt file |
| `/agentrx:trial-init` | Initialize parallel trial worktrees |
| `/agentrx:trial-status` | Show status of all trials |
| `/agentrx:trial-work` | Spawn dev agents for trials |

---

## Available Skills

| Skill | Description |
|-------|-------------|
| `arx-render` | Render ARX templates with context |
| `arx_templating` | ARX syntax reference |

---

## Important Notes

1. **Commands as native** - Treat `_agents/commands/` items as native CLI slash commands
2. **Project context** - Load project-specific files when user references them with `@`
3. **Don't over-read** - Only load files listed above at startup; read others when directed
4. **ARX templates** - Files with `arx: template` front matter are renderable templates
5. **Follow precisely** - If something wasn't specified, don't do it

---

## Detection

To detect if a project uses AgentRx, check for:

1. This file (`CHAT_START.md`) with `arx: config` front matter
2. `_agents/` directory structure
3. `AGENTS.md` or `CLAUDE.md` referencing AgentRx
