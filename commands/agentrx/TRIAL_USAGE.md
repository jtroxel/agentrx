---
description: AgentRx Parallel Trials - Usage Guide
argument-hint:
---

# Parallel Tial Usage Guide

## Quick Start

### 1. Initialize a Trial

When you're ready to start working on one of the integration approaches:

```
When the user types: "/agentrx:trial-init plaid"
Claude will execute: .claude/commands/agentrx/trial-init plaid
```

**For now, manually invoke via:**
```bash
.claude/commands/agentrx/trial-init plaid
```

Or tell Claude to run it:
```
Please run: .claude/commands/agentrx/trial-init plaid
```

### 2. Work on the Trial

After initialization, spawn an agent to work on it:

```bash
.claude/commands/agentrx/trial-work plaid
```

Then, Claude will spawn a Task agent with:
- Working directory: `worktrees/plaid/`
- Context from iteration spec
- Isolated filesystem for parallel work

### 3. Check Status

At any time, check trial progress:

```bash
.claude/commands/agentrx/trial-status
```

## Full Workflow Example

```bash
# 1. Initialize all three trials
.claude/commands/agentrx/trial-init plaid
.claude/commands/agentrx/trial-init teller
.claude/commands/agentrx/trial-init browser

# 2. Check that all were created
.claude/commands/agentrx/trial-status

# 3. Work on first trial
.claude/commands/agentrx/trial-work plaid
# (Agent spawns and implements Plaid adapter)

# 4. Work on second trial
.claude/commands/agentrx/trial-work teller
# (Agent spawns and implements Teller adapter)

# 5. Work on third trial
.claude/commands/agentrx/trial-work browser
# (Agent spawns and implements browser automation)

# 6. Check final status
.claude/commands/agentrx/trial-status

# 7. Compare implementations
cd worktrees/plaid && git log
cd ../teller && git log
cd ../browser && git log
```

## Integration with Claude Code

### Option A: Manual Invocation (Current)

User tells Claude:
```
"Run the trial-init command for plaid"
```

Claude executes:
```bash
.claude/commands/agentrx/trial-init plaid
```

### Option B: Slash Command (Future)

Once registered as a skill, user can type:
```
/agentrx:trial-init plaid
```

### Option C: Natural Language

User says:
```
"Initialize a trial for the Plaid integration approach"
```

Claude recognizes intent and runs:
```bash
.claude/commands/agentrx/trial-init plaid
```

## Agent Spawning Pattern

When working on a trial, Claude should:

1. Run trial-work script to prepare context
2. Spawn Task agent with prompt like:

```
You are implementing the Plaid integration approach for Iteration 0
of the Family CFO account sync spike.

Working directory: worktrees/plaid/
Reference spec: _bmad-output/implementation-artifacts/iteration-0-spec.md
Trial context: .trial-context

Your goal: Implement the Plaid adapter following the spec's acceptance criteria.
Focus only on the Plaid approach - other approaches are being developed
in parallel in separate worktrees.

Key deliverables:
1. PlaidAdapter.ts implementing the AccountAdapter interface
2. CLI commands for testing (update-accounts)
3. Google Sheets integration via abstraction layer
4. Test data demonstrating the adapter works

You have full autonomy within this worktree. Work iteratively and
test frequently.
```

3. Agent works in isolation
4. Updates committed to `trial/plaid` branch
5. Metrics recorded in trials.yaml

## Directory Structure After Initialization

```
_codebrain/                    # Main repo (you are here)
├── _bmad-output/
│   ├── implementation-artifacts/
│   │   └── iteration-0-spec.md
│   └── trials/
│       └── trials.yaml        # Trial tracking
├── worktrees/
│   ├── plaid/                 # Plaid trial (branch: trial/plaid)
│   │   ├── .trial-context
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── src/
│   │       ├── server/
│   │       └── shared/
│   ├── teller/                # Teller trial (branch: trial/teller)
│   │   └── ...
│   └── browser/               # Browser trial (branch: trial/browser)
│       └── ...
└── .claude/
    ├── commands/agentrx/
    │   ├── README.md
    │   ├── trial-init*
    │   ├── trial-work*
    │   └── trial-status*
    └── scripts/agentrx/
        ├── trial-init.sh*
        ├── trial-work.sh*
        └── trial-status.sh*
```

## Tips

1. **Parallel Development**: Each trial is isolated, so you can work on multiple approaches simultaneously without conflicts.

2. **Branch Management**: Each trial has its own branch (`trial/plaid`, etc.), making it easy to compare approaches with `git diff`.

3. **Selective Merging**: After evaluation, you can cherry-pick the best patterns from each approach into main.

4. **Clean Separation**: Worktrees keep your main repo clean - no switching branches, no stashing changes.

5. **Agent Independence**: Each agent spawned for a trial works independently without interfering with other trials.

## Troubleshooting

**Problem**: Command not found
**Solution**: Ensure scripts are executable: `chmod +x .claude/commands/agentrx/*`

**Problem**: Worktree already exists
**Solution**: Remove it first: `git worktree remove worktrees/plaid`

**Problem**: Can't spawn agent in worktree
**Solution**: Ensure trial is initialized first with `trial-init`
