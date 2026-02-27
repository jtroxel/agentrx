---
description: AgentRx Command System - Summary
argument-hint:
---

# AgentRx Command System - Summary

## What Was Created

A hybrid command system for managing parallel integration trials:

### Commands (`.claude/commands/agentrx/`)
- **trial-init** - Initialize a trial worktree
- **trial-work** - Prepare to work on a trial (spawn agent)
- **trial-status** - Show status of all trials

### Implementation Scripts (`.claude/scripts/agentrx/`)
- **trial-init.sh** - Creates git worktree, sets up structure, updates registry
- **trial-work.sh** - Prepares context, updates status
- **trial-status.sh** - Reports on all trials

### Documentation
- **README.md** - Command reference
- **USAGE.md** - Workflow guide and examples
- **SUMMARY.md** - This file

## How It Works

1. **User invokes command**: `.claude/commands/agentrx/trial-init plaid`
2. **Command wrapper** calls the implementation script
3. **Script executes**: Creates worktree, sets up files, updates tracking
4. **Output**: Trial ready for development

## Key Features

✅ **Git Worktrees** - Each trial in separate filesystem location
✅ **Branch Isolation** - `trial/plaid`, `trial/teller`, `trial/browser`
✅ **Independent Agents** - Each trial can have its own spawned agent
✅ **Coordination** - Central registry in `_bmad-output/trials/trials.yaml`
✅ **Baseline Structure** - Auto-generated package.json, tsconfig, .env.example

## Next Steps

### 1. Initialize Trials

```bash
.claude/commands/agentrx/trial-init plaid
.claude/commands/agentrx/trial-init teller
.claude/commands/agentrx/trial-init browser
```

### 2. Spawn Agents to Work on Each

For each trial, run:
```bash
.claude/commands/agentrx/trial-work plaid
```

Then Claude spawns a Task agent with:
- Working directory: `worktrees/plaid/`
- Context: iteration-0-spec.md + .trial-context
- Goal: Implement Plaid adapter

### 3. Compare and Evaluate

After all trials complete:
- Check status: `.claude/commands/agentrx/trial-status`
- Review code in each worktree
- Compare metrics in trials.yaml
- Decide winning approach

## Architecture Benefits

**Filesystem Isolation**
- No merge conflicts during parallel development
- Each trial has complete independence
- Easy to compare implementations

**Agent Independence**
- Spawn multiple agents working in parallel
- Each agent has full context for their approach
- No interference between trials

**Clean Coordination**
- Main repo stays clean
- trials.yaml tracks all work
- Easy to see status at a glance

**Selective Integration**
- Cherry-pick best patterns from each trial
- Merge winning approach to main
- Extract reusable components

## File Locations

```
.claude/
├── commands/agentrx/
│   ├── trial-init*        # Command: Initialize trial
│   ├── trial-work*        # Command: Work on trial
│   ├── trial-status*      # Command: Show status
│   ├── README.md          # Command reference
│   ├── USAGE.md           # Usage guide
│   └── SUMMARY.md         # This file
└── scripts/agentrx/
    ├── trial-init.sh*     # Implementation: Init
    ├── trial-work.sh*     # Implementation: Work
    └── trial-status.sh*   # Implementation: Status

_bmad-output/
└── trials/
    └── trials.yaml        # Trial registry (created on first init)

worktrees/                 # Created when trials initialized
├── plaid/                 # Branch: trial/plaid
├── teller/                # Branch: trial/teller
└── browser/               # Branch: trial/browser
```

## Integration with Iteration 0

This command system directly supports the Iteration 0 spec:

**Iteration 0 Goal**: Validate backend integration architecture via 3 parallel trials
**AgentRx System**: Provides infrastructure to run those trials independently

**Spec Requirements**:
- ✅ 3 integration approaches (Plaid, Teller, Browser)
- ✅ Parallel development capability
- ✅ Evaluation framework (trials.yaml tracks metrics)
- ✅ CLI for testing (each trial implements CLI independently)
- ✅ Isolated environments (worktrees provide isolation)

## Future Enhancements

Possible additions to the command system:

- [ ] `/arx:trial-evaluate` - Run evaluation metrics across all trials
- [ ] `/arx:trial-merge <approach>` - Merge winning approach to main
- [ ] `/arx:trial-cleanup` - Remove all worktrees
- [ ] `/arx:trial-compare <approach1> <approach2>` - Diff two trials
- [ ] Background agent spawning with progress monitoring
- [ ] Automated metric collection from trial runs
