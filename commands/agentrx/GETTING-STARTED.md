---
description: Getting Started with AgentRx
argument-hint:
---

# Getting Started with AgentRx

AgentRx is now available as **native Claude Code slash commands**!

## Available Commands

Type these directly in Claude Code:

```
/agentrx:trial-init <approach>    - Initialize a new trial worktree
/agentrx:trial-work <approach>    - Spawn agent to work on a trial
/agentrx:trial-status             - Show status of all trials
```

## Documentation Commands

```
/agentrx:QUICKREF    - Quick reference guide
/agentrx:USAGE       - Detailed usage guide
/agentrx:COMMAND_SUMMARY     - System summary
/agentrx:README      - Full command reference
```

## Quick Start

### 1. Initialize trials for each approach

```
/agentrx:trial-init plaid
/agentrx:trial-init teller
/agentrx:trial-init browser
```

### 2. Check everything is set up

```
/agentrx:trial-status
```

### 3. Work on each trial

```
/agentrx:trial-work plaid
```

This spawns a specialized agent in the isolated worktree to implement the Plaid adapter.

### 4. Repeat for other approaches

```
/agentrx:trial-work teller
/agentrx:trial-work browser
```

### 5. Compare results

```
/agentrx:trial-status
```

Then review the implementations in each worktree directory.

## What Makes This "Native"?

- **Slash commands** - Type `/agentrx:` and tab-complete
- **Integrated help** - Commands appear in skill list
- **Consistent UX** - Works like built-in Claude Code commands
- **Proper argument hints** - Shows what parameters are needed
- **MCP-ready** - Can be extended via MCP server if needed

## Architecture

```
.claude/
├── commands/agentrx/          # Skill definitions (markdown)
│   ├── trial-init.md         # → /agentrx:trial-init
│   ├── trial-work.md         # → /agentrx:trial-work
│   ├── trial-status.md       # → /agentrx:trial-status
│   ├── QUICKREF.md           # → /agentrx:QUICKREF
│   ├── USAGE.md              # → /agentrx:USAGE
│   └── SUMMARY.md            # → /agentrx:SUMMARY
└── scripts/agentrx/           # Implementation (bash)
    ├── trial-init.sh
    ├── trial-work.sh
    └── trial-status.sh
```

Each markdown file defines a skill that Claude Code recognizes as a native command.

## Next Steps

1. Read the quick reference: `/agentrx:QUICKREF`
2. Initialize your first trial: `/agentrx:trial-init plaid`
3. Check it worked: `/agentrx:trial-status`
4. Start working on it: `/agentrx:trial-work plaid`

Happy trialing! 🧪
