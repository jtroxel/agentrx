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
.claude/           # Claude Code integration (symlinks)
specs/             # Project specifications
```

## How to Update
Run `_agents/scripts/agentrx/setup-claude-links.sh` to refresh links and regenerate this index.
