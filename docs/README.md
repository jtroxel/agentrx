# AgentRx
## Elevator Pitch
AgentRx is a tool set aimed to help developers advance their agentic coding abilities.

It is a customizable template for adding slash-commands, specialized agents, and agent skills to your real work.

## Watercooler Talk
Want more? Drop it in, and AgentRx lets you incrementally Ratchet up your agentic coding process. 
1. Begin by making vibe coding less chaotic... more structured, repeatable even.
2. Advance into context engineering. Developing and maintaining structured context documentation.
3. Grow into more advanced agentic workflows: From simple "Ralph" loops; to complex, multi-agent productivity., and Parallel "Jack-Jack" splits.

## Quickstart

### Adding AgentRx
To get started with AgentRx, the developer pulls the repo into their system. That can be a central location or for every project. Fork it and you can contribute back!

### **`arx init`**
The `arx init` command sets up the initial project structure with default directories. You can customize the structure using command options or environment variables.

The `agentrx init` command sets up this structure with the default directories, but you can customize as needed. The user is given the option of copying agentrx files, linking subdirectories into the agentrx-root, or just specifying custom directories on the filesystem.

## Environment Variables
- `ARX_PROJECT_ROOT` - Root directory of the host project (default: current working directory).
- `ARX_TARGET_PROJ` - Target project directory relative to project root (default: `$ARX_PROJECT_ROOT/_project/`).
- `ARX_TOOLS` - Agent assets directory relative to the project root (default: `$ARX_PROJECT_ROOT/_agents/`).
- `ARX_DOCS_OUT` - Documentation directory (default: `$ARX_TARGET_PROJ/docs/agentrx`).
  - See [agentrx Docs Structure](_agents/agentrx/PROJECT_DOCS.md)

## Target Directory Structure

After initialization (`arx init`), your project directory will be structured as follows, with the agentrx assets and project code organized in a way that supports an agent-assisted development workflow. The CLI will create this structure with the default directories, but you can customize as needed using the command options or environment variables.

### Top Level
```
./                           # $ARX_PROJECT_ROOT set in init - Recommended setup: make this the parent of the $ARX_TOOLS and $ARX_TARGET_PROJ directories.
├── _agents/                 # If $ARX_AGENT_TOOLS is unset, defaults to ./_agents
├── _project/                # If $ARX_TARGET_PROJ is unset, defaults to ./_project - Root of the source code
│   ├── ...
│   └── docs/agentrx/        # If $ARX_DOCS_OUT is unset, defaults to ./_project/docs/agentrx 
│       └── ...
├── AGENTS.md                # Agent instructions
├── CLAUDE.md                # Claude guidance
├── CHAT_START.md            # Bootstrap instructions
└── .env                     # Configuration (contains PROJECT_ROOT_DIR and AgentRx vars)
└── .venv                    # Python virtual environment for local installation/development
```
### ARX_AGENT_TOOLS
Common Tools and Assets for Agentic Development
See [ARX_AGENT_TOOLS](../docs/README.md#arx_agent_tools)

### ARX_DOCS_OUT`
Where AgentRx-generated documentation and development artifacts are output. See [agentrx Docs](_agents/agentrx/PROJECT_DOCS.md)


