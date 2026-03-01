# AgentRx

AgentRx is a toolkit that helps developers build structured, repeatable agentic coding workflows. It provides slash commands, agent skills, reusable prompt templates, and a CLI (`arx`) that brings those same workflows to the terminal.

## Elevator Pitch

Drop AgentRx into any project and incrementally ratchet up your agentic coding process:

1. Make vibe coding less chaotic — structured, repeatable prompts.
2. Advance into context engineering — maintain living documentation alongside your code.
3. Grow into multi-agent workflows: simple "Ralph" loops → complex parallel "Jack-Jack" splits.

---
## Environment Variables

When "installed" in a project, AgentRx sets up and uses several environment variables to locate its source, workspace root, and documentation directories.

> **Workspace vs Project**: The *workspace root* (`ARX_WORKSPACE_ROOT`) is the
> top-level directory containing AgentRx scaffolding (AGENTS.md, .env, _agents/, etc.).
> The *target project* (`ARX_TARGET_PROJ`) is where your actual source code lives.
> They are deliberately separate so that agentic-development artefacts don't pollute
> the target project, though developers may choose to combine them.

| Variable | CLI flag | Default | Description |
|---|---|---|---|
| `AGENTRX_SOURCE` | `--agentrx-source` | _(none)_ | Path to the `agentrx-src` clone. Used to copy or link templates. |
| `ARX_WORKSPACE_ROOT` | _(positional)_ | CWD | Workspace root. Always set to wherever `arx init` runs. |
| `ARX_AGENT_TOOLS` | `--agents-dir` | `$ARX_WORKSPACE_ROOT/_agents` | Agent assets directory. |
| `ARX_TARGET_PROJ` | `--target-proj` | `$ARX_WORKSPACE_ROOT/_project` | Target project (source code) directory. |
| `ARX_PROJ_DOCS` | `--proj-docs` | `$ARX_TARGET_PROJ/docs` | Up-to-date project documentation for the target project. |
| `ARX_WORK_DOCS` | `--work-docs` | `$ARX_PROJ_DOCS/agentrx` | "Working" documents from AgentRx agentic development (vibes, deltas, history). |

> **Backward compatibility**: `ARX_PROJECT_ROOT` is accepted as a fallback when
> `ARX_WORKSPACE_ROOT` is not set.

---


## Directory Structure

```
agentrx-src/                      # AGENTRX_SOURCE — clone once, point projects at it
├── bin/
│   └── init-arx.sh               # Interactive shell initializer (primary entry point)
├── cli/
│   ├── agentrx/
│   │   ├── cli.py                # arx entry point
│   │   └── commands/
│   │       ├── init.py           # arx init — file operations engine
│   │       └── prompt.py         # arx prompt do/new/list
│   └── README.md                 # CLI quickstart and full option reference
├── templates/
│   ├── _arx_workspace_root.arx/  # → $ARX_WORKSPACE_ROOT/  (.ARX. stripped)
│   │   ├── AGENTS.ARX.md         #   → AGENTS.md
│   │   ├── AGENT_TOOLS.ARX.md    #   → AGENT_TOOLS.md
│   │   ├── CLAUDE.ARX.md         #   → CLAUDE.md
│   │   └── .cursorrules.arx      #   → .cursorrules
│   ├── _arx_agent_tools.arx/     # → $ARX_AGENT_TOOLS/  (copy or link)
│   │   ├── commands/agentrx/
│   │   ├── skills/agentrx/
│   │   ├── scripts/agentrx/
│   │   ├── hooks/agentrx/
│   │   └── agents/
│   ├── _arx_proj_docs.arx/       # → $ARX_PROJ_DOCS/  (optional, prompted)
│   │   ├── Architecture.ARX.md
│   │   ├── Product.ARX.md
│   │   ├── README.ARX.md
│   │   ├── features/
│   │   └── architecture/
│   ├── _arx_work_docs.arx/       # → $ARX_WORK_DOCS/  (always copied)
│   │   ├── deltas/
│   │   ├── sessions/
│   │   ├── tasks_tracking/
│   │   └── vibes/
│   └── README.md                 # Templates directory documentation
└── docs/
    └── README.md                 # ← you are here, these are up-to-date project docs for  AgentRx.
```

### Initialized project layout

After `arx init`, a target project looks like:

```
./                           # ARX_WORKSPACE_ROOT
├── _agents/                 # ARX_AGENT_TOOLS  — agent commands, skills, scripts, hooks
│   ├── commands/agentrx/
│   ├── skills/agentrx/
│   ├── scripts/agentrx/
│   ├── hooks/agentrx/
│   └── agents/
├── _project/                # ARX_TARGET_PROJ  — your source code lives here
│   └── docs/                # ARX_PROJ_DOCS    — project documentation
│       └── agentrx/         # ARX_WORK_DOCS    — generated docs and vibes
│           ├── deltas/
│           ├── sessions/
│           ├── tasks_tracking/
│           └── vibes/
├── AGENTS.md                # Agent startup instructions
├── AGENT_TOOLS.md           # Context documents index
├── CLAUDE.md                # Claude Code guidance
├── .cursorrules             # Cursor IDE rules (delegates to AGENTS.md)
└── .env                     # ARX_* variables, sourced by shell / arx commands
```

---

## Init Workflow

### Standard setup (shell entry point)

```bash
# 1. Clone AgentRx source once
git clone https://github.com/your-org/agentrx.git ~/dev/agentrx-src
export AGENTRX_SOURCE=~/dev/agentrx-src

# 2. Create and enter your project
mkdir ~/my-project && cd ~/my-project
python3.13 -m venv .venv && source .venv/bin/activate

# 3. Run the interactive initializer
$AGENTRX_SOURCE/bin/init-arx.sh .
```

`init-arx.sh` will:
- Activate `.venv` / `venv` in the project root
- `pip install` the `arx` CLI from `$AGENTRX_SOURCE/cli`
- Prompt for directory layout using **readline tab-completion** (Tab to complete paths)
- Optionally show a `--dry-run` preview before making changes
- Call `arx init` with the resolved values

### Copy mode vs link mode

| Mode | How it works | When to use |
|---|---|---|
| `copy` (default) | Files copied from `templates/`; `*.ARX.*` names stripped to plain names | Most projects; files travel with the project |
| `--link-arx` | Skeleton dirs created; each `agentrx/` leaf is a symlink back to source | Active AgentRx development; always see latest commands |

### Template naming convention

Each `templates/_arx_<name>.arx/` subdirectory maps 1-to-1 to an `ARX_*` destination variable:

| Template subdir | Destination | Notes |
|---|---|---|
| `_arx_workspace_root.arx/` | `$ARX_WORKSPACE_ROOT` | `.ARX.` stripped; bare files skipped |
| `_arx_agent_tools.arx/` | `$ARX_AGENT_TOOLS` | All files copied as-is (or symlinked with `--link-arx`) |
| `_arx_work_docs.arx/` | `$ARX_WORK_DOCS` | Always copied |
| `_arx_proj_docs.arx/` | `$ARX_PROJ_DOCS` | Optional; prompted interactively |

**`.ARX.` marker**: files whose names contain `.ARX.` (or `.arx.`) have the marker stripped on installation — e.g. `AGENTS.ARX.md` → `AGENTS.md`. Files with the `.arx` suffix have the suffix dropped (e.g. `.cursorrules.arx` → `.cursorrules`). Bare files (no marker) inside `_arx_workspace_root.arx/` are treated as templates-dir documentation and are **not** installed.

#### Conflict handling

| Mode | Target exists | Action |
|---|---|---|
| copy | file exists | Merge contents into existing file |
| link | path exists | Create symlink named `<base>.ARX.<ext>` (append numeric suffix if still conflicts) |

### `arx init` directory rules

| Directory | Exists | Result |
|---|---|---|
| `ARX_AGENT_TOOLS` | yes | Left untouched |
| `ARX_AGENT_TOOLS` | no (copy) | Created; populated from `templates/_arx_agent_tools.arx/`. |
| `ARX_AGENT_TOOLS` | no (`--link-arx`) | Skeleton created; `agentrx/` leaves symlinked to source |
| `ARX_TARGET_PROJ` | no | Created (with `src/` inside) |
| `ARX_PROJ_DOCS` | no | Created |
| `ARX_WORK_DOCS` | no | Created (with `deltas/`, `sessions/`, `tasks_tracking/`, `vibes/`) |

Root-level workspace files (`AGENTS.md`, `CLAUDE.md`, `AGENT_TOOLS.md`, `.cursorrules`) come from `_arx_workspace_root.arx/` and are installed only if absent.
`.env` is always written/updated with all six `ARX_*` variables.

---

## CLI Reference

See [`cli/README.md`](../cli/README.md) for the full CLI reference including all `arx init` options, `arx prompt` usage, and virtual environment setup.

---

## Architecture Notes

- **`bin/init-arx.sh`** is the primary user-facing entry point. It is a thin shell wrapper that handles interactive prompting (where shell readline gives free tab-completion) and delegates all file operations to the Python CLI.
- **`arx init`** is the file-operations engine. It is intentionally non-interactive — all configuration comes via flags or environment variables, making it scriptable and CI-friendly.
- **`arx prompt`** works with `.md` prompt files in `ARX_WORK_DOCS/vibes/`. Prompt content can reference environment variables (`$VAR`) which are expanded on output.
- **Templates** in `templates/_arx_agent_tools.arx/` are the canonical source of all agent assets. In copy mode they are duplicated into the project; in link mode the project symlinks directly to them.


