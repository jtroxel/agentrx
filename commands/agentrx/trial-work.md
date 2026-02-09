---
description: Spawn development agents for all trials defined in a document
argument-hint: <document-path>
---

Parse a specification document to identify trial approaches and spawn parallel development agents for each.

**Arguments:**
- `<document-path>`: Path to document defining trial approaches (e.g., iteration-0-spec.md)

**What it does:**
1. Parses document for approach definitions (searches for `## Approach N: Name` headers)
2. Identifies approach names (e.g., plaid, teller, browser)
3. Validates worktrees exist for each approach
4. Updates trial statuses to "in-progress"
5. Spawns parallel Task agents for each ready trial

**Document Format Expected:**
```markdown
## Approach 1: Plaid API
...
## Approach 2: Teller API
...
## Approach 3: Browser Automation
...
```

**Examples:**
- `/agentrx:trial-work _bmad-output/implementation-artifacts/iteration-0-spec.md`

**Prerequisites:**
- Trials must be initialized first:
  - `/agentrx:trial-init plaid`
  - `/agentrx:trial-init teller`
  - `/agentrx:trial-init browser`

**Output:**
- Lists all approaches found in document
- Shows which trials are ready vs need initialization
- Spawns agents in parallel for all ready trials

**Agent Context (each agent receives):**
- Working directory: `worktrees/<approach>/`
- Spec document: The provided document path
- Trial-specific context from `.trial-context`
- Isolated git branch: `trial/<approach>`

**Note:** Each agent works independently in its isolated worktree, implementing only the adapter for its specific approach. Agents run in parallel for faster development.

!bash .claude/scripts/agentrx/trial-work.sh $ARGUMENTS

---

**IMPORTANT - Post-Execution Instructions for Claude:**

After the bash script completes, you MUST:

1. Parse the output to extract the list of ready trials from the `READY_TRIALS=...` line
2. Spawn Task agents in parallel (one per ready trial) using a SINGLE message with multiple Task tool calls
3. Each agent should be given this context:

**Agent Prompt Template:**
```
You are implementing the {APPROACH} integration approach for Iteration 0.

Working directory: worktrees/{approach}/
Reference spec: {document-path}
Trial context: .trial-context (in your working directory)

Your goal: Implement the {APPROACH} adapter following the spec in iteration-0-spec.md.

Key tasks:
1. Read the spec document to understand requirements for your approach
2. Read .trial-context for approach-specific notes
3. Implement the integration adapter in src/server/integrations/{approach}/
4. Create CLI commands for testing (balance fetch, transaction retrieval)
5. Integrate with Google Sheets for data storage
6. Test your implementation
7. Document your findings and metrics

Work independently - other approaches are being developed in parallel by other agents.
```

**Example execution after bash script:**
If READY_TRIALS=plaid teller browser, spawn 3 Task agents in parallel:
- Agent 1: Plaid approach in worktrees/plaid/
- Agent 2: Teller approach in worktrees/teller/
- Agent 3: Browser approach in worktrees/browser/
