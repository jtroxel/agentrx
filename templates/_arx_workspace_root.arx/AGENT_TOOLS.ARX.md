# Context Documents Index

This file indexes key context documents for AI coding agents.

## Agent Instructions
- [AGENTS.md](./AGENTS.md) - Primary agent instructions
- [_agents/commands/](/_agents/commands/) - Available commands

## Commands Reference
| Command | Description |
|---------|-------------|
| `/arx:trial-init` | argument-hint: <approach|document-path> |
| `/arx:prompt-new` | argument-hint: <short_name> ,out-dir |
| `/arx:trial-status` | argument-hint: |
| `/arx:trial-work` | argument-hint: <document-path> |
| `/arx:adapt-workspace` | argument-hint: <coding-agent> |

## Project Structure
```
_agents/           # Agent configurations
  commands/        # Slash command definitions
  skills/          # Skill definitions
  hooks/           # Event hooks
  scripts/         # Utility scripts
_project/          # Project code and documentation
specs/             # Project specifications
```

## How to Update
Re-run `arx init` to refresh AgentRx assets (non-destructive).
