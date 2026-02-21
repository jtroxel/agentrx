---
arx: config
name: chat-start
description: Bootstrap instructions for coding agents starting new sessions
version: 1
---

# AgentRx Bootstrap Instructions

> **For Coding Agents**: Follow these instructions precisely at session start.

## Step 1: Load Core Context

Read these files **in parallel** to establish AgentRx capabilities:

### Commands (treat as native slash commands)
```
_agents/commands/agentrx/*.md
```

### Skills
```
_agents/skills/agentrx/*.md
```

## Step 2: Confirm Bootstrap

After loading, output a confirmation listing available commands and skills.

## Important Notes

1. **Commands as native** - Treat `_agents/commands/` items as native CLI slash commands
2. **Project context** - Load project-specific files when user references them
3. **ARX templates** - Files with `arx: template` front matter are renderable templates
4. **Follow precisely** - If something wasn't specified, don't do it
