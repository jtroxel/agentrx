---
description: AgentRx Quick Reference
argument-hint:
---

# AgentRx Quick Reference

## Commands

```bash
# Initialize a trial
.claude/commands/agentrx/trial-init <approach>

# Work on a trial (spawns agent)
.claude/commands/agentrx/trial-work <approach>

# Check status
.claude/commands/agentrx/trial-status
```

## Typical Workflow

```bash
# 1. Initialize all three trials
.claude/commands/agentrx/trial-init plaid
.claude/commands/agentrx/trial-init teller
.claude/commands/agentrx/trial-init browser

# 2. Verify setup
.claude/commands/agentrx/trial-status

# 3. Work on each trial
.claude/commands/agentrx/trial-work plaid
# (Claude spawns agent in worktrees/plaid/)

.claude/commands/agentrx/trial-work teller
# (Claude spawns agent in worktrees/teller/)

.claude/commands/agentrx/trial-work browser
# (Claude spawns agent in worktrees/browser/)

# 4. Check final status
.claude/commands/agentrx/trial-status
```

## Directory Structure

```
worktrees/
├── plaid/          # Plaid trial (trial/plaid branch)
├── teller/         # Teller trial (trial/teller branch)
└── browser/        # Browser trial (trial/browser branch)

_bmad-output/trials/
└── trials.yaml     # Trial tracking registry
```

## Agent Context (Auto-provided)

When agent spawns via `trial-work`:
- **Working dir**: `worktrees/<approach>/`
- **Spec**: `_bmad-output/implementation-artifacts/iteration-0-spec.md`
- **Context**: `.trial-context` in worktree
- **Goal**: Implement adapter for this approach only

## Invoking in Claude Code

### Natural Language
```
"Initialize a trial for the Plaid approach"
"Work on the Plaid trial"
"Show me the trial status"
```

### Direct Command
```
"Run: .claude/commands/agentrx/trial-init plaid"
```

### Future (Skill Integration)
```
/agentrx:trial-init plaid
/agentrx:trial-work plaid
/agentrx:trial-status
```

## Tips

- Each trial is **completely isolated** - no conflicts
- Trials run on **separate branches** - easy to compare
- Agents work **independently** per trial
- **trials.yaml** tracks all progress centrally
- Use `git diff trial/plaid trial/teller` to compare
