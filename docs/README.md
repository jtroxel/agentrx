# AgentRx

AgentRx is a toolkit that helps developers build structured, repeatable agentic coding workflows. It provides composable commands (/slash and CLI), agent skills, and reusable prompt templates — designed to bring order to AI-assisted development without locking you into a single agent or framework.

## Elevator Pitch

Drop AgentRx into any project and incrementally ratchet up your agentic coding process:

1. **Make vibe coding less chaotic** — structured, repeatable prompts replace ad-hoc conversations that evaporate when the context window rolls over.
2. **Prompt-Engineering primitives** — create, render, execute, and version prompts as first-class development artifacts, not throwaway chat messages.
3. **Multi-agent adaptable** — Claude Code, Cursor, Copilot, Codex, OpenCode can all work on the same projects with shared context and commands.
4. **Unix philosophy** — AgentRx (or `arx`) commands are designed in the spirit of old-skool "Unix programming": small, composable, and chainable. The /slash commands also reflect this philosophy.

---
## Quick Look

**Set up a workspace**
```bash
export AGENTRX_SOURCE=$(pwd)
# Initialize a new AgentRx workspace in the current directory.
$AGENTRX_SOURCE/bin/init-arx.sh . # interactive script
# ... Sets up the initial workspace:
#     - Setup python env and install CLI
#     - links, environment variables, and arx.config.yaml file

# Initial set up for your coding agent
arx adapt pi --with-agent # or claude, copilot, codex, opencode
# Sets up basic "bootstrap" configuration for the selected coding agent.
```
**In your Coding Agent, work with prompts**
```bash
> Help me design feature X, to help users A, B, and C
# ... back and forth
# ... if available, hooks detect compaction or refresh 
# ... or proactively capture the context:
> /arx:prompt-new --session "initial design feature X" # Creates a summary and a repeatable prompt based on the context of this session. Defaults to $ARX_WORKING/$ARX_MYPROJ/vibes/, see below.
# User can edit, refine. Then:
> /arx:prompt-run @260309_init-design-feat-x # Loads and runs previously saved prompt
```
**From the CLI (outside an agent session)**
```bash
# Run a finished prompt
arx prompt do $ARX_WORKING/$ARX_MYPROJ/vibes/another_prompt.yaml pi
# ... $ARX_MYPROJ (set in .env) is the project abbreviation, `pi` is the agent

# Create a prompt from a template
arx prompt new arch-facet --data '{"component": "auth-service"}'
# ... resolves a template from $ARX_TEMPLATES by name
# ... renders with provided data context, writes to vibes/

# Create from a mustache template programmatically
arx tmpl --mustache-only $ARX_TMPL/$ARX_MYPROJ/my_mustache_templ.yaml > $ARX_WORKING/$ARX_MYPROJ/vibes/another_prompt.yaml
# ... --mustache-only evaluates mustache templates only
# ... use --conf <yaml_file> to supply custom template variables

# List recent prompts
arx prompt list -n 10
```
## AgentRx Workspace and Source Structure
The "AgentRx workflow" structure is designed to have minimal, optional impact on the source and repo structure of the target projects. You can adopt as much or as little as you want — a single prompt template directory, or the full workspace with multi-project support.

### AGENTRX_SOURCE
An environment variable pointing to the AgentRx source directory, from a clone or download. AgentRx is "installed" from the source into the current directory. That directory becomes the AgentRx "workspace".

### Initialized AgentRx "Workspace" - Env
The shell that the init-arx was run in will have the following variables. These are also captured in a .env file.

| Variable | Description |
|---|---|
| `AGENTRX_SOURCE` | Path to the AgentRx source directory (clone or download) |
| `ARX_ROOT` | Workspace root directory; auto-detected or set by `init-arx` |
| `ARX_<PROJ_ABBR>` | Set for each project abbreviation in a multi-project workspace, the location of the project directory |
| `ARX_AGENT_FILES` | Agent assets directory (commands, skills, scripts, hooks) |
| `ARX_TEMPLATES` | Templates directory for this Workspace (_arx_templates) |
| `ARX_WORKING` | Working documents directory for this Workspace (vibes, deltas, sessions, tasks) |

### Initialized AgentRx Workspace

**The AgentRx Workspace Structure** will look like the following, after `init-arx`.

```
./                           # ARX_ROOT root of AgentRx Workspace
├── _agents/                 # ARX_AGENT_FILES (default ARX_ROOT/_agents) — agent commands, skills, scripts, hooks
│   ├── commands/agentrx/
│   ├── skills/agentrx/
│   ├── ...
├── _projects/               # ARX_PROJ_ROOT - From user input, _projects is default
│   └── proj-abbr-1/         # Project Source Dir for PROJ_ABBR_1
│   |   └── docs/            # Project documentation, At ARX_PROJ_ROOT/ARX_<PROJ_ABBR>/docs
│   ├── arx_docs/            # ARX_WORKING (default ARX_PROJ_ROOT/arx_docs) — From user input, generated docs and vibes
│       ├── deltas/
│       ├── sessions/
│       ├── tasks/
│       └── vibes/
│   └── proj-abbr-2/         # Project Source Dir for PROJ_ABBR_2
├── AGENTS.md                # Agent startup instructions
├── AGENT_TOOLS.md           # Context documents index
├── CLAUDE.md                # Ex: Claude Code file, init creates or appends to refer to AGENTS.md
└── .env                     # ARX_* variables, sourced by shell / arx commands
└── arx.config.yaml          # Detailed Workspace configuration
└── _arx_templates/          # $ARX_TEMPLATES, default to _arx_templates - prompt and context markdown templates

```
**The `init-arx` command initializes the workspace structure.** 

## CLI Commands - Examples
Note: After initializing the workspace.

**In your Coding Agent — getting oriented**

Once the workspace is initialized, your coding agent needs to discover the AgentRx commands and context. Here's the typical flow:
```bash
> /arx:... # Check if the agent has loaded AgentRx commands.
# If the agent hasn't, try rereading AGENTS.MD
> @AGENTS.MD # Read in the base cross-agent documentation

# Additional agent customization — adapts commands/skills to your agent's conventions
> run the @arx:adapt command to customize for your (Pi Coding Agent) needs.
# Augments and/or reworks the agentrx slash commands and skills
# for the specific agent's capabilities and idioms.
```

## arx prompt "primitives"
### CLI

Work with prompt files — create, execute, and list.

```bash
arx prompt new [TEMPLATE] [TEXT] [--data JSON] [--data-file FILE]
# - option to use a template from $ARX_TEMPLATES by subdir, e.g.: arch-facet or readme-0
# - templates are evaluated programmatically (ARX tags + env vars)
# - mustache {{...}} blocks are passed through for agent-side evaluation

arx prompt do [PROMPT_FILE] [--data JSON] [--data-file FILE] [--dry-run]
# - renders the prompt with data context and outputs to stdout or file
# - data sources merge in order: data-file < --data JSON < stdin

arx prompt list [-n LIMIT] [--dir DIR]
# - shows recent prompt files with relative age (e.g., "2h ago", "3d ago")
```

**`prompt new`** creates a prompt file from a template or plain text.

  Templates are resolved from `$ARX_TEMPLATES` by subdirectory name (e.g., `arch-facet`, `readme-0`). The `:new` render phase runs at creation time — resolving environment variables, project metadata, and any context-enrichment scripts declared in the template's front matter. Output lands in `$ARX_WORKING/vibes/` by default.

**`prompt do`** executes a prompt file with optional data context.
  The `:do` render phase runs at execution time — resolving runtime variables (file contents, API data, user input). Supports `--dry-run` to preview the rendered output without side effects.

**`prompt list`** shows recent prompt files sorted by modification time with relative age.

## Core Modules

### render.py — ARX Template Engine

Three-step processing pipeline:
1. **Strip YAML front matter** (`---` blocks) — returned separately
2. **Expand env vars**: `$VAR` and `${VAR}` from `os.environ`
3. **Resolve ARX tags**:
   - `<ARX:IF [[expr]]>`... `</ARX:IF>`
   - `<ARX:REPLACE agent: agent-name, "prompt text">`... `</ARX:REPLACE>`

Tag expression types:
- Dot notation: `[[user.profile.name]]`
- Default values: `[[key | "default"]]`
- Environment: `[[env.VAR_NAME]]`

Mustache `{{...}}` block directives are passed through unchanged — structural evaluation is handled agent-side.

Public API:
- `render(text, data, phase)` → rendered string
- `render_file(path, data, phase)` → (front_matter, rendered_body)
- `build_context(data_json, data_file, stdin_json)` → merged dict
- `strip_front_matter(text)` → (fm_dict, body)

## Environment Variables & config yaml

### arx.config.yaml

The workspace configuration file, created by `init-arx`. Stores project paths, project abbreviations, agent preferences, and template settings. All `arx` commands read from this file to resolve workspace layout.

Example:
```yaml
TODO
```

### .env file

Shell-sourceable file with all `ARX_*` variables (see the table above under "Initialized AgentRx Workspace - Env"). Auto-generated by `init-arx`. Consumed by the CLI, agent hooks, and context-enrichment scripts.

### Prompt/Template Front Matter

Prompt and template files use YAML front matter to declare metadata and inputs:

```yaml
---
arx: template              # Type: template | context | prompt | skill | config
description: Brief description of this template
inputs:
  - name: component
    type: string
    required: true
    default: "my-service"
subdir: vibes               # Output subdirectory under ARX_WORKING
short_name: arch-design     # Output filename base
script: ./scripts/enrich.sh # Context enrichment script (run before rendering)
---
```

