# AgentRx

AgentRx is a toolkit that helps developers build structured, repeatable agentic coding workflows. It provides composable commands (/slash and CLI), agent skills, reusable prompt templates.

## Elevator Pitch

Drop AgentRx into any project and incrementally ratchet up your agentic coding process:

1. Make vibe coding less chaotic — structured, repeatable prompts.
2. Provides Prompt-Engineering primitives for managing repeatable prompts and content.
3. Adaptable to multiple coding agents, working on the same projects.
4. AgentRx (or `arx`) commands are designed in the spirit of old-skool "Unix programming": small, composable, and chainable. The /slash commands also reflect this philosophy.

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
****
```bash
# Run a finished prompt
arx prompt run $ARX_WORKING/$ARX_MYPROJ/vibes/another_prompt.yaml pi
# ... $ARX_MYPROJ (set in .env) is the project abbreviation, `pi` is the agent

# Create a prompt from a template.
arx tmpl --mustache-only $ARX_TMPL/$ARX_MYPROJ/my_mustache_templ.yaml > $ARX_WORKING/$ARX_MYPROJ/vibes/another_prompt.yaml # generating a new prompt 
# ... --mustache-only, eval mustache templates only, programatically
# ... using --conf <yaml_file> with custom template variables

```
## AgentRx Workspace and Source Structure
The "AgentRx workflow" structure is designed to have minimal, optional impact of source and repo structure of the target projects.

### AGENTRX_SOURCE
An environment variable pointing to the AgentRx source directory, from a clone or download. AgentRx is "installed" from the source into the current directory. That directory becomes the AgentRx "workspace".

### Initialized AgentRx "Workspace" - Env
The shell that the ARX init was run in will have the following variables. These are also captured in a .env file.

| Variable | Description |
|---|---|
| `AGENTRX_SOURCE` | Path to the AgentRx source directory (clone or download) |
| `ARX_ROOT` | Workspace root directory; auto-detected or set by `arx init` |
| `ARX_<PROJ_ABBR>` | Set for each project abbreviation in a multi-project workspace, the location of the project directory |
| `ARX_AGENT_FILES` | Agent assets directory (commands, skills, scripts, hooks) |
| `ARX_TEMPLATES` | Templates directory for this Workspace (_arx_templates) |
| `ARX_WORKING` | Working documents directory for this Workspace (vibes, deltas, sessions, tasks) |


### Initialized AgentRx Workspace

**The AgentRx Workspace Structure** will look like the following, after `arx init`.

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
**The `arx init` command initializes the workspace structure.** To do so, it performs the following prompts and actions(interactive mode):
1. Prompt: Specify the AgentRx Agent Tools Directory (where the agent commands, skills, scripts, and hooks are located).
   - Default is an empty _agents dir.
   - Source files copied from `_arx_agent_files.arx/`, see below
2. Prompt: Do you want local copies of AgentRx templates? 
   - Default (empty) is "Use from $ARX_SOURCE"
   - If dir specified, all templates are copied from `$AGENTRX_SOURCE/_arx_templates/` to the specified directory, see below.
3. Command copies/updates all templates in `_arx_workspace_root.arx/` from the template location from (2), to the $ARX_ROOT, see below.
4. Prompt: Specify the "root" directory for all target projects.
  - Default (empty) = Let me add to the arx.config.yaml now. Command prompts for any key to continue.
  - If a directory is specified, it will be used as the root for all target projects.
    - If the directory does not exist, it will be created.
    - If the directory exists and is not empty, the command will consume all subdirectories as target projects, and update arx.config.yaml (and ARX_PROJ_ROOT).
5. Prompt: Where would you like AgentRx to update current Project Docs?
    - Default (1) = As subdirectories of each project dir (like $ARX_PROJ_ROOT/$PROJ_ABBR_1/...)
    - Option (2) = As subdirectories of a common  directory
  - Prompt: Specify the subdirectory for project docs:
    - (default: `..$PROJ_ABBR_1/arx_docs`)
  - Command creates the subdirectory structrure.

** Arx Copy/Update Details:**
| Template subdir | Destination | Behaviour |
|---|---|---|
| `_arx_workspace_root.arx/` | `$ARX_WORKSPACE_ROOT` | `.ARX.` stripped; only installed if absent |
| `_arx_agent_tools.arx/` | `$ARX_AGENT_TOOLS` | Copied as-is (or symlinked with `--link-arx`) |
| `_arx_work_docs.arx/` | `$ARX_WORK_DOCS` | Always copied |
| `_arx_proj_docs.arx/` | `$ARX_PROJ_DOCS` | Optional; prompted interactively (or `--docs`/`--no-docs`) |

## CLI Commands - Examples
Note: After initializing the workspace.
**In your Coding Agent**
Get the agent oriented... 
```bash
> /arx:... # Check if the agent has loaded AgentRx commands.
# If the agent hasn't, try rereading AGENTS.MD
# Additional agent customization
> @AGENTS.MD # Try reading in the base cross-agent documentation
# ...
# If still not working, try the /slash-command and restart
> run the @arx:adapt command to customize for your (Pi Coding Agent) needs.
# Augments and/or reworks the agentrx 
```

## arx prompt "primitives"
### CLI

Work with prompt files — create, execute, and list.

```bash
arx prompt new TODO
# - option to use a template from $ARX_TEMPLATES by subdir, e.g.: arch-facet or readme-0 ...
# - templates are evaluated programmatically (mustache), and with the arx_templating skill
arx prompt do ... TODO
arx prompt list [-n LIMIT] [--dir DIR]
```

**`prompt new`** creates a prompt file from a template or plain text. Templates are resolved from TODO

**`prompt do`** executes a prompt file with optional context TODO

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
TODO

