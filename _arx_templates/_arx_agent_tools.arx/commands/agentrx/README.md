---
description: AgentRx Trial Commands
argument-hint:
---

# AgentRx Trial Commands

Command system for managing parallel integration trials using git worktrees and sub-agents.

## Available Commands

### `/arx:trial-init <approach>`

Initialize a new trial worktree for parallel development.

**Arguments:**
- `<approach>`: Name of the integration approach (e.g., `plaid`, `teller`, `browser`)

**What it does:**
- Creates git branch `trial/<approach>`
- Adds worktree at `worktrees/<approach>/`
- Sets up baseline project structure (package.json, tsconfig.json)
- Creates `.trial-context` file with approach-specific context
- Updates `_bmad-output/trials/trials.yaml` registry

**Example:**
```
/arx:trial-init plaid
```

**Output:**
- Worktree created at `worktrees/plaid/`
- Branch `trial/plaid` ready for development

---

### `/arx:trial-work <approach>`

Spawn a development agent to work on a trial.

**Arguments:**
- `<approach>`: Name of the trial to work on

**What it does:**
- Validates worktree exists
- Updates trial status to "in-progress"
- Displays trial context
- Prepares for agent spawn in worktree directory

**Example:**
```
/arx:trial-work plaid
```

**Agent Context:**
- Working directory: `worktrees/plaid/`
- Access to: `iteration-0-spec.md`
- Trial-specific context from `.trial-context`

---

### `/arx:trial-status`

Show status of all trials.

**Arguments:** None

**What it does:**
- Lists all trial worktrees
- Shows status (initialized, in-progress, complete)
- Displays metrics if available
- Shows trials.yaml contents

**Example:**
```
/arx:trial-status
```

**Output:**
```
Trial Status:
========================================

Trial: plaid
  Location: worktrees/plaid/
  Branch: trial/plaid
  Status: in-progress
  Initialized: 2026-01-16T10:00:00Z
  Setup: ✅ Dependencies configured
  Files: 12 TypeScript files
```

---

## Implementation

Commands are backed by shell scripts in `.claude/scripts/agentrx/`:
- `trial-init.sh` - Worktree and structure setup
- `trial-work.sh` - Agent context preparation
- `trial-status.sh` - Status reporting

## Workflow

### 1. Initialize Trials

```bash
/arx:trial-init plaid
/arx:trial-init teller
/arx:trial-init browser
```

### 2. Work on Each Trial

```bash
/arx:trial-work plaid
# Agent spawns in worktrees/plaid/ to implement Plaid adapter
```

### 3. Check Status

```bash
/arx:trial-status
```

### 4. Compare and Evaluate

After trials are complete, compare implementations:
- Review `worktrees/*/` code
- Check metrics in `trials.yaml`
- Generate evaluation matrix

## Directory Structure

```
.
├── worktrees/
│   ├── plaid/          # Plaid trial worktree
│   ├── teller/         # Teller trial worktree
│   └── browser/        # Browser trial worktree
├── _bmad-output/
│   └── trials/
│       └── trials.yaml # Trial coordination registry
└── .claude/
    ├── commands/agentrx/      # Command definitions
    └── scripts/agentrx/       # Implementation scripts
```

## Git Worktree Management

Each trial runs in an isolated git worktree:
- **Main repo**: Coordination and specs (`_codebrain/`)
- **Trial worktrees**: Independent development (`worktrees/*/`)
- **Branches**: `trial/plaid`, `trial/teller`, `trial/browser`

Benefits:
- Filesystem isolation (no conflicts)
- Parallel development
- Easy comparison (`git diff trial/plaid trial/teller`)
- Selective merging of learnings

## Agent Spawning

When `/arx:trial-work <approach>` is called:

1. Script prepares context
2. Claude spawns Task agent with:
   - Working directory in trial worktree
   - Access to iteration spec
   - Trial-specific context
3. Agent works independently in isolated environment
4. Progress tracked in trials.yaml

## Future Enhancements

- [ ] `/arx:trial-evaluate` - Run evaluation framework
- [ ] `/arx:trial-merge <approach>` - Merge learnings to main
- [ ] `/arx:trial-cleanup` - Remove worktrees
- [ ] Background agent support with progress monitoring
- [ ] Automated metric collection
