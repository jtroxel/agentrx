---
arx: command
name: adapt-workspace
description: Add or update native coding-agent instructions so the agent discovers the AgentRx workspace
version: 2
argument-hint: <coding-agent|all>
---

# /arx:adapt-workspace — Adapt Workspace for a Coding Agent

Inject the minimum bootstrap instructions into whatever file a coding agent
reads by default, so the agent discovers `_agents/` and the rest of the ARX
structure on its very first session.

## Usage

```
/arx:adapt-workspace <coding-agent|all>
```

### Shell Script (runs outside any agent session)

```bash
_agents/scripts/agentrx/adapt-agent.sh <agent|all> [--project-root DIR]
```

> **Why both?**  The script solves the chicken-and-egg problem — it can be run
> immediately after `arx init`, before any agent has loaded the commands.
> The slash command is for refreshing the block later from inside a session.

---

## Supported Agents

| Identifier | Aliases | Instruction file(s) |
|------------|---------|---------------------|
| `claude-code` | `claude` | `CLAUDE.md` |
| `github-copilot` | `copilot` | `.github/copilot-instructions.md` |
| `cursor` | — | `.cursorrules` + `.cursor/rules/arx.mdc` |
| `all` | — | All of the above |

---

## What It Does

1. Resolves the agent's native instruction file.
2. Creates the file if it doesn't exist.
3. Writes (or replaces) a **marker-delimited block** with the minimum
   AgentRx bootstrap instructions.
4. Leaves all content outside the markers untouched.

### Markers

```
<!-- arx:begin -->
…managed content…
<!-- arx:end -->
```

**Merge rules:**

| File state | Action |
|-----------|--------|
| Does not exist | Create file with the marker block |
| Exists, contains markers | Replace only the marker block |
| Exists, no markers | Append the block at end of file |

---

## Bootstrap Content (all agents)

The injected block is intentionally **minimal** — just enough so the agent
can bootstrap the full ARX context on its own:

```markdown
## AgentRx Workspace

This workspace uses **AgentRx** for structured AI-assisted development.

### On every session start — read these files:

AGENTS.md
CHAT_START.md
_agents/commands/agentrx/QUICKREF.md

### Directory map

| Path | Purpose |
|------|---------|
| `_agents/commands/agentrx/` | Slash-command definitions |
| `_agents/skills/agentrx/`   | Skill / reference documents |
| `_agents/scripts/agentrx/`  | Implementation shell scripts |
| `_agents/hooks/agentrx/`    | Lifecycle hooks |

### Key commands

| Command | Description |
|---------|-------------|
| `/arx:init` | Initialize project structure |
| `/arx:prompt-new` | Create a prompt file |
| `/arx:adapt-workspace <agent>` | Refresh these instructions |
```

---

## Agent Details

### `claude-code`

**File:** `CLAUDE.md` (workspace root)

Claude Code reads `CLAUDE.md` automatically at session start. The injected
block tells it to also read `AGENTS.md`, `CHAT_START.md`, and the QUICKREF.

For Claude Code the commands in `_agents/commands/` are also symlinked into
`.claude/commands/` by `setup-agent-links.sh`, so they appear as native
slash commands.

---

### `github-copilot`

**File:** `.github/copilot-instructions.md`

VS Code GitHub Copilot reads this file automatically and includes it as
system-level context for every Copilot Chat conversation in the workspace.

The injected block teaches Copilot to treat `_agents/commands/agentrx/*.md`
as available commands and to read the bootstrap files at session start.

---

### `cursor`

**Files:** `.cursorrules` (legacy) + `.cursor/rules/arx.mdc` (new format)

Cursor reads `.cursorrules` in older versions and `.cursor/rules/*.mdc` in
newer versions. Both files are written to maximise compatibility.

The `.mdc` file includes front matter:

```yaml
---
description: "AgentRx workspace bootstrap"
globs: ["**/*"]
alwaysApply: true
---
```

---

## Examples

```bash
# Right after arx init — bootstrap all agents you use
_agents/scripts/agentrx/adapt-agent.sh all

# Just Copilot
_agents/scripts/agentrx/adapt-agent.sh copilot

# From inside a coding agent session (refresh after ARX upgrade)
/arx:adapt-workspace all

# Single agent
/arx:adapt-workspace github-copilot
```

## Implementation

When invoked as a slash command, the agent should:

1. Determine the target agent from the argument.
2. Run the script:
   ```bash
   _agents/scripts/agentrx/adapt-agent.sh <agent> --project-root "$PWD"
   ```
3. Report the output.

## See Also

- [QUICKREF.md](./QUICKREF.md) — command quick reference
- [GETTING-STARTED.md](./GETTING-STARTED.md) — quick-start guide
- [setup-agent-links.sh](../../scripts/agentrx/setup-agent-links.sh) — full agent link setup
