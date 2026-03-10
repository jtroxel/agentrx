---
title: "AgentRx Templates"
description: "Template files for AgentRx projects. Each subdirectory maps to one ARX_* destination variable."
arx: template
---

# AgentRx Templates

This directory contains all template files installed by `arx init`. Each `_arx_<name>.arx/` subdirectory maps **1-to-1** to an `ARX_*` environment variable (destination path).

## Subdirectory → Destination Mapping

| Subdirectory | Destination | Behaviour |
|---|---|---|
| `_arx_workspace_root.arx/` | `$ARX_WORKSPACE_ROOT` | `.ARX.` marker stripped from filenames; bare files (no `.ARX.`) are not installed |
| `_arx_agent_tools.arx/` | `$ARX_AGENT_TOOLS` | All files copied as-is (or each `agentrx/` leaf symlinked with `--link-arx`) |
| `_arx_work_docs.arx/` | `$ARX_WORK_DOCS` | Always copied |
| `_arx_proj_docs.arx/` | `$ARX_PROJ_DOCS` | Optional; user is prompted interactively (or `--docs`/`--no-docs`) |

## `.ARX.` Naming Convention

Files whose names contain `.ARX.` (or `.arx.`) have the marker stripped on installation:
- `AGENTS.ARX.md` → `AGENTS.md`
- `CLAUDE.ARX.md` → `CLAUDE.md`
- `.cursorrules.arx` → `.cursorrules`

Files **without** the marker inside `_arx_workspace_root.arx/` are treated as documentation for the templates directory itself and are **not** installed. All other subdirs copy all files without filtering.

## `_arx_workspace_root.arx/`

Templates for the workspace root (`$ARX_WORKSPACE_ROOT`). Installed with `.ARX.` stripped:
- `AGENTS.ARX.md` → startup instructions for coding agents
- `AGENT_TOOLS.ARX.md` → context documents index
- `CLAUDE.ARX.md` → Claude Code guidance
- `.cursorrules.arx` → Cursor IDE rules (delegates to AGENTS.md)

## `_arx_agent_tools.arx/`

Agent assets installed into `$ARX_AGENT_TOOLS` (default: `_agents/`):
- `commands/agentrx/` — slash command definitions
- `skills/agentrx/` — agent skill documents
- `scripts/agentrx/` — utility shell scripts
- `hooks/agentrx/` — event hooks
- `agents/` — agent configurations

In `--link-arx` mode each `agentrx/` leaf is symlinked back to this source tree instead of copied.

## `_arx_proj_docs.arx/`

Optional project documentation skeleton installed into `$ARX_PROJ_DOCS` (default: `_project/docs/`). Prompted interactively unless `--docs` or `--no-docs` is passed:
- `README.ARX.md` → `README.md` — docs index
- `Architecture.ARX.md` → `Architecture.md`
- `Product.ARX.md` → `Product.md`
- `features/feature.ARX.md` → per-feature design template
- `architecture/` — deep-dive architecture templates

## `_arx_work_docs.arx/`

Working docs scaffolding installed into `$ARX_WORK_DOCS` (default: `_project/docs/agentrx/`). Always copied. Subdirs contain `.gitkeep` files so git tracks the empty directories:
- `deltas/` — change specs and delta documents
- `sessions/` — session context and notes
- `tasks_tracking/` — active task lists
- `vibes/` — prompt files (`arx prompt new` output)
