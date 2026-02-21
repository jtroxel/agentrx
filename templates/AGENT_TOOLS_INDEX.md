# Context Documents Index

This file indexes key context documents for AI coding agents.

## Agent Instructions
- [AGENTS.md](./AGENTS.md) - Primary agent instructions
- [_agents/commands/](/_agents/commands/) - Available commands

## Commands Reference
| Command | Description |
|---------|-------------|
| `/agentrx:trial-init` | argument-hint: <approach|document-path> |
| `/agentrx:prompt-new` | argument-hint: <short_name> ,out-dir |
| `/agentrx:trial-status` | argument-hint: |
| `/agentrx:trial-work` | argument-hint: <document-path> |

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
