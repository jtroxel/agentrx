---
description: Initialize trial worktrees for parallel development
argument-hint: <approach|document-path>
---

Initialize trial worktrees either for a single approach or all approaches defined in a document.

**Arguments:**
- `<approach>`: Name of a single integration approach (e.g., `plaid`, `teller`, `browser`)
- `<document-path>`: Path to document defining multiple approaches (parses `## Approach N:` headers)

**What it does:**
- Creates git branch `trial/<approach>` for each trial
- Adds worktree at `worktrees/<approach>/`
- Sets up baseline project structure (package.json, tsconfig.json)
- Creates `.trial-context` file with approach-specific context
- Updates `_bmad-output/trials/trials.yaml` registry

**Single Approach Examples:**
- `/agentrx:trial-init plaid` - Initialize Plaid integration trial
- `/agentrx:trial-init teller` - Initialize Teller integration trial
- `/agentrx:trial-init browser` - Initialize Browser integration trial

**Document Mode Examples:**
- `/agentrx:trial-init _bmad-output/implementation-artifacts/iteration-0-spec.md` - Initialize all trials from spec

**Document Format Expected:**
```markdown
## Approach 1: Plaid API
...
## Approach 2: Teller API
...
## Approach 3: Browser Automation
...
```

**Output:**
- Worktree created at `worktrees/<approach>/` for each trial
- Branch `trial/<approach>` ready for development
- All trials registered in trials.yaml

!bash .claude/scripts/agentrx/trial-init.sh $ARGUMENTS
