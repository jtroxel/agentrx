---
description: Show status of all trials
argument-hint:
---

Display the current status of all trial worktrees.

**Arguments:** None

**What it shows:**
- List of all trial worktrees
- Status for each trial (initialized, in-progress, complete)
- Metrics if available
- Contents of trials.yaml registry

**Example:**
- `/agentrx:trial-status` - Show all trial statuses

**Output includes:**
- Trial name and location
- Git branch information
- Current status
- Initialization timestamp
- Setup status (dependencies, files, etc.)
- Progress metrics

**Use this to:**
- Check which trials are initialized
- Monitor trial progress
- See which trial to work on next
- Verify trial setup

!bash .claude/scripts/agentrx/trial-status.sh $ARGUMENTS
