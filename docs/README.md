# AgentRx

AgentRx is a toolkit that helps developers build structured, repeatable agentic coding workflows. It provides slash commands, agent skills, reusable prompt templates, and a CLI (`arx`) that brings those same workflows to the terminal.

## Elevator Pitch

Drop AgentRx into any project and incrementally ratchet up your agentic coding process:

1. Make vibe coding less chaotic — structured, repeatable prompts.
2. Advance into context engineering — maintain living documentation alongside your code.
3. Grow into multi-agent workflows: simple "Ralph" loops → complex parallel "Jack-Jack" splits.

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
│   ├── AGENTS.ARX.md             # → $ARX_PROJECT_ROOT/AGENTS.md
│   ├── AGENT_TOOLS.ARX.md        # → $ARX_PROJECT_ROOT/AGENT_TOOLS.md
│   ├── _arx_agent_tools.arx/     # → $ARX_AGENT_TOOLS/ (copy or link)
│   │   ├── commands/agentrx/
│   │   ├── skills/agentrx/
│   │   ├── scripts/agentrx/
│   │   ├── hooks/agentrx/
│   │   └── agents/
│   └── README.md                 # Templates directory documentation
└── docs/
    └── README.md                 # ← you are here
```

### Initialized project layout

After `arx init`, a target project looks like:

```
./                           # ARX_PROJECT_ROOT
├── _agents/                 # ARX_AGENT_TOOLS  — agent commands, skills, scripts, hooks
│   ├── commands/agentrx/
│   ├── skills/agentrx/
│   ├── scripts/agentrx/
│   ├── hooks/agentrx/
│   └── agents/
├── _project/                # ARX_TARGET_PROJ  — your source code lives here
│   └── docs/agentrx/        # ARX_DOCS_OUT     — generated docs and vibes
│       ├── deltas/
│       ├── vibes/
│       └── history/
├── AGENTS.md                # Agent startup instructions
├── CLAUDE.md                # Claude Code guidance
├── CHAT_START.md            # Session bootstrap
└── .env                     # ARX_* variables, sourced by shell / arx commands
```

---

## Environment Variables

| Variable | CLI flag | Default | Description |
|---|---|---|---|
| `AGENTRX_SOURCE` | `--agentrx-source` | _(none)_ | Path to the `agentrx-src` clone. Required for `--link-arx`; optional for copy. |
| `ARX_PROJECT_ROOT` | _(positional)_ | CWD | Project root. Always set to wherever `arx init` runs. |
| `ARX_AGENT_TOOLS` | `--agents-dir` | `_agents` | Agent assets directory. |
| `ARX_TARGET_PROJ` | `--target-proj` | `_project` | Target project (source code) directory. |
| `ARX_DOCS_OUT` | `--docs-out` | `_project/docs/agentrx` | Documentation output directory. |

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

Source files in `templates/` use an `.ARX.` marker in the filename to identify them as AgentRx-managed templates:

- **Pattern:** `*.ARX.*` and `*.arx.*`
- **Installed name:** the `.ARX.` segment is stripped — e.g. `AGENTS.ARX.md` → `AGENTS.md`
- **Root-level templates** (`templates/*.ARX.*`) install into `$ARX_PROJECT_ROOT`
- **Agent-tools templates** (`templates/_arx_agent_tools.arx/**`) install into `$ARX_AGENT_TOOLS`

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
| `ARX_DOCS_OUT` | no | Created (with `deltas/`, `vibes/`, `history/`) |

Root-level `*.ARX.*` templates are installed (`.ARX.` stripped) only if absent.
`.env` is always written/updated.

---

## CLI Reference

See [`cli/README.md`](../cli/README.md) for the full CLI reference including all `arx init` options, `arx prompt` usage, and virtual environment setup.

---

## Architecture Notes

- **`bin/init-arx.sh`** is the primary user-facing entry point. It is a thin shell wrapper that handles interactive prompting (where shell readline gives free tab-completion) and delegates all file operations to the Python CLI.
- **`arx init`** is the file-operations engine. It is intentionally non-interactive — all configuration comes via flags or environment variables, making it scriptable and CI-friendly.
- **`arx prompt`** works with `.md` prompt files in `ARX_DOCS_OUT/vibes/`. Prompt content can reference environment variables (`$VAR`) which are expanded on output.
- **Templates** in `templates/_arx_agent_tools.arx/` are the canonical source of all agent assets. In copy mode they are duplicated into the project; in link mode the project symlinks directly to them.


